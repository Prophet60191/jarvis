"""
Coqui TTS implementation for Jarvis Voice Assistant.

This module provides high-quality neural text-to-speech using Coqui TTS
with support for voice cloning, multiple languages, and streaming.
"""

import logging
import torch
import tempfile
import os
import time
from typing import Optional, List, Dict, Any
from threading import Lock
from pathlib import Path

try:
    from TTS.api import TTS
except ImportError:
    TTS = None

from ..config import AudioConfig
from ..exceptions import TextToSpeechError
from .voice_profiles import VoiceProfileManager, VoiceProfile
from .performance_optimizer import PerformanceOptimizer


logger = logging.getLogger(__name__)


class CoquiTTSManager:
    """
    Manages Coqui TTS operations for the Jarvis voice assistant.
    
    This class provides high-quality neural text-to-speech with support for
    voice cloning, multiple languages, and streaming capabilities.
    """
    
    def __init__(self, config: AudioConfig):
        """
        Initialize the Coqui TTS manager.
        
        Args:
            config: Audio configuration settings
        """
        self.config = config
        self.tts: Optional[TTS] = None
        self.device: Optional[str] = None
        self._is_initialized = False
        self._lock = Lock()  # Thread safety for TTS operations

        # Voice profile management
        self.voice_manager = VoiceProfileManager()
        self.current_voice_profile: Optional[VoiceProfile] = None

        # Performance optimization
        self.performance_optimizer = PerformanceOptimizer()
        
        # Coqui TTS specific settings from config
        self.model_name = config.coqui_model
        self.language = config.coqui_language
        self.speaker_wav: Optional[str] = config.coqui_speaker_wav
        self.temperature = config.coqui_temperature
        self.length_penalty = config.coqui_length_penalty
        self.repetition_penalty = config.coqui_repetition_penalty
        self.top_k = config.coqui_top_k
        self.top_p = config.coqui_top_p
        
        logger.info(f"CoquiTTSManager initialized with config: {config}")
    
    def _detect_device(self) -> str:
        """
        Detect the best available device for TTS processing.

        Returns:
            Device string: 'cuda', 'mps', or 'cpu'
        """
        # If device is explicitly set in config, use it
        if self.config.coqui_device != "auto":
            return self.config.coqui_device

        # Auto-detect best device
        if self.config.coqui_use_gpu:
            if torch.cuda.is_available():
                return "cuda"
            elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                return "mps"  # Apple Silicon

        return "cpu"
    
    def initialize(self) -> None:
        """
        Initialize the Coqui TTS engine with the configured settings.
        
        Raises:
            TextToSpeechError: If TTS engine initialization fails
        """
        if TTS is None:
            raise TextToSpeechError("Coqui TTS not installed. Please install with: pip install TTS")
        
        try:
            logger.info("Initializing Coqui TTS engine...")

            with self._lock:
                # Detect optimal device
                self.device = self._detect_device()
                logger.info(f"Using device: {self.device}")

                # Fix PyTorch 2.6+ weights_only issue for Coqui TTS
                # We trust Coqui TTS models, so disable weights_only for compatibility
                import torch
                original_load = torch.load
                def patched_load(*args, **kwargs):
                    if 'weights_only' not in kwargs:
                        kwargs['weights_only'] = False
                    return original_load(*args, **kwargs)
                torch.load = patched_load
                logger.debug("Patched torch.load to use weights_only=False for Coqui TTS compatibility")

                # Initialize TTS model
                self.tts = TTS(self.model_name).to(self.device)

                # Ensure all model parameters are in float32 to avoid mixed precision issues
                if hasattr(self.tts, 'synthesizer') and hasattr(self.tts.synthesizer, 'tts_model'):
                    # Convert the entire TTS model to float32
                    self.tts.synthesizer.tts_model.float()

                    # Also convert any sub-components that might be in half precision
                    if hasattr(self.tts.synthesizer.tts_model, 'hifigan_decoder'):
                        self.tts.synthesizer.tts_model.hifigan_decoder.float()

                    # Convert any other model components
                    for module in self.tts.synthesizer.tts_model.modules():
                        if hasattr(module, 'float'):
                            module.float()

                # Optimize model for performance
                self.tts = self.performance_optimizer.optimize_model(self.tts)

                self._is_initialized = True
                logger.info(f"Coqui TTS engine initialized successfully on {self.device}")

        except Exception as e:
            error_msg = f"Failed to initialize Coqui TTS engine: {str(e)}"
            logger.error(error_msg)
            raise TextToSpeechError(error_msg) from e
    
    def is_initialized(self) -> bool:
        """
        Check if the TTS engine is properly initialized.
        
        Returns:
            True if TTS engine is initialized, False otherwise
        """
        return self._is_initialized and self.tts is not None
    
    def speak(self, text: str, wait: bool = True) -> None:
        """
        Convert text to speech and play it.
        
        Args:
            text: Text to convert to speech
            wait: Whether to wait for speech to complete (compatibility parameter)
            
        Raises:
            TextToSpeechError: If TTS operation fails
        """
        if not text or not text.strip():
            logger.warning("Empty text provided for TTS")
            return
        
        if not self.is_initialized():
            raise TextToSpeechError("Coqui TTS engine not initialized. Call initialize() first.")
        
        try:
            logger.debug(f"Speaking text: '{text[:50]}{'...' if len(text) > 50 else ''}'")

            # Check cache first
            voice_profile_id = self.current_voice_profile.id if self.current_voice_profile else "default"
            cached_audio = self.performance_optimizer.get_cached_audio(
                text=text,
                voice_profile_id=voice_profile_id,
                language=self.language,
                temperature=self.temperature,
                length_penalty=self.length_penalty,
                repetition_penalty=self.repetition_penalty,
                top_k=self.top_k,
                top_p=self.top_p
            )

            if cached_audio is not None:
                wav, sample_rate = cached_audio
                logger.debug("Using cached audio for TTS")
            else:
                # Generate new audio
                start_time = time.time()

                with self._lock:
                    # Use XTTS_v2 model - EXACT working configuration from git commit 5bb003c
                    logger.info(f"🎤 Using XTTS_v2 multilingual model (working configuration)")
                    logger.info(f"🎤 Model: {self.config.coqui_model}")

                    # Generate speech using configured model
                    try:
                        # Check if model is multi-speaker and add speaker parameter if needed
                        tts_kwargs = {
                            'text': text,
                            'temperature': self.temperature,
                            'length_penalty': self.length_penalty,
                            'repetition_penalty': self.repetition_penalty,
                            'top_k': self.top_k,
                            'top_p': self.top_p
                        }

                        # Add speaker parameter for multi-speaker models like VCTK
                        if hasattr(self.tts, 'speakers') and self.tts.speakers and self.config.coqui_speaker_id:
                            tts_kwargs['speaker'] = self.config.coqui_speaker_id
                            logger.info(f"🎤 Using speaker: {self.config.coqui_speaker_id}")

                        wav = self.tts.tts(**tts_kwargs)
                    except RuntimeError as e:
                        if "expected scalar type Float but found Half" in str(e) or "MPSFloatType" in str(e):
                            logger.warning(f"Voice cloning failed due to tensor precision issues: {e}")
                            logger.warning("Falling back to basic TTS")
                            self._fallback_speak(text)
                            return
                        else:
                            raise

                generation_time = time.time() - start_time
                self.performance_optimizer.record_generation_time(generation_time)

                # Cache the generated audio
                self.performance_optimizer.cache_audio(
                    text=text,
                    voice_profile_id=voice_profile_id,
                    language=self.language,
                    audio_data=wav,
                    sample_rate=22050,  # XTTS-v2 sample rate
                    temperature=self.temperature,
                    length_penalty=self.length_penalty,
                    repetition_penalty=self.repetition_penalty,
                    top_k=self.top_k,
                    top_p=self.top_p
                )

                logger.debug(f"Generated audio in {generation_time:.2f}s")

            # Play the audio
            self._play_audio(wav)

            # Run memory optimization if needed
            if self.performance_optimizer.should_run_gc():
                self.performance_optimizer.optimize_memory()
                
            logger.debug("Coqui TTS operation completed")

        except Exception as e:
            error_msg = f"Failed to speak text with Coqui TTS: {str(e)}"
            logger.error(error_msg)
            raise TextToSpeechError(error_msg, text=text) from e

    def _fallback_speak(self, text: str) -> None:
        """
        Fallback TTS method when voice cloning is not available.
        Uses system TTS as a temporary solution.
        """
        try:
            import pyttsx3

            logger.info("Using fallback pyttsx3 TTS")
            engine = pyttsx3.init()

            # Configure voice settings
            voices = engine.getProperty('voices')
            if voices:
                # Try to find a good voice
                for voice in voices:
                    if 'daniel' in voice.name.lower() or 'alex' in voice.name.lower():
                        engine.setProperty('voice', voice.id)
                        break

            # Set rate and volume
            engine.setProperty('rate', self.config.tts_rate)
            engine.setProperty('volume', self.config.tts_volume)

            # Speak the text
            engine.say(text)
            engine.runAndWait()
            engine.stop()

            logger.debug("Fallback TTS completed")

        except ImportError:
            logger.error("Fallback TTS not available - pyttsx3 not installed")
            logger.error("Please set up a voice profile or install pyttsx3: pip install pyttsx3")
        except Exception as e:
            logger.error(f"Fallback TTS failed: {e}")
            logger.error("Please set up a voice profile using: python setup_default_voice.py")
    
    def _play_audio(self, wav_data) -> None:
        """
        Play audio data using system audio.
        
        Args:
            wav_data: Audio waveform data from TTS
        """
        try:
            import soundfile as sf
            import sounddevice as sd
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
                # Write audio data to temporary file
                sf.write(tmp_file.name, wav_data, 22050)  # XTTS-v2 uses 22050 Hz
                
                # Read and play audio
                data, fs = sf.read(tmp_file.name)
                sd.play(data, fs)
                sd.wait()  # Wait for playback to complete
                
                # Clean up temporary file
                os.unlink(tmp_file.name)
                
        except ImportError:
            # Fallback: save to file and use system command
            logger.warning("soundfile/sounddevice not available, using system audio fallback")
            self._play_audio_fallback(wav_data)
        except Exception as e:
            logger.error(f"Failed to play audio: {e}")
            raise TextToSpeechError(f"Audio playback failed: {e}")
    
    def _play_audio_fallback(self, wav_data) -> None:
        """
        Fallback audio playback using system commands.
        
        Args:
            wav_data: Audio waveform data from TTS
        """
        try:
            import soundfile as sf
            import subprocess
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
                sf.write(tmp_file.name, wav_data, 22050)
                
                # Use system audio player
                if os.name == 'posix':  # macOS/Linux
                    if os.system('which afplay > /dev/null 2>&1') == 0:  # macOS
                        subprocess.run(['afplay', tmp_file.name], check=True)
                    elif os.system('which aplay > /dev/null 2>&1') == 0:  # Linux
                        subprocess.run(['aplay', tmp_file.name], check=True)
                    else:
                        logger.error("No suitable audio player found")
                        raise TextToSpeechError("No audio player available")
                else:  # Windows
                    import winsound
                    winsound.PlaySound(tmp_file.name, winsound.SND_FILENAME)
                
                # Clean up
                os.unlink(tmp_file.name)
                
        except Exception as e:
            logger.error(f"Fallback audio playback failed: {e}")
            raise TextToSpeechError(f"Audio playback failed: {e}")
    
    def speak_async(self, text: str) -> None:
        """
        Convert text to speech asynchronously (non-blocking).
        
        Args:
            text: Text to convert to speech
            
        Raises:
            TextToSpeechError: If TTS operation fails
        """
        # For now, Coqui TTS speak is already relatively fast
        # In future phases, we can implement true async with threading
        self.speak(text, wait=True)
    
    def stop_speaking(self) -> None:
        """
        Stop any current speech output.
        
        Note: This is a compatibility method. Coqui TTS doesn't support
        stopping mid-speech in the same way as pyttsx3.
        """
        logger.debug("Stop speaking requested (Coqui TTS doesn't support mid-speech stopping)")
    
    def get_available_voices(self) -> List[Dict[str, Any]]:
        """
        Get list of available TTS voices.
        
        Returns:
            List of dictionaries containing voice information
            
        Raises:
            TextToSpeechError: If unable to retrieve voices
        """
        if not self.is_initialized():
            raise TextToSpeechError("Coqui TTS engine not initialized. Call initialize() first.")
        
        # Coqui TTS XTTS-v2 supports voice cloning, so voices are dynamic
        voices = [
            {
                "index": 0,
                "id": "xtts_v2_default",
                "name": "XTTS-v2 Default Voice",
                "languages": ["en", "es", "fr", "de", "it", "pt", "pl", "tr", "ru", "nl", "cs", "ar", "zh-cn", "ja", "hu", "ko"],
                "gender": "configurable",
                "age": "configurable",
                "cloneable": True
            }
        ]
        
        if self.speaker_wav:
            voices.append({
                "index": 1,
                "id": "xtts_v2_cloned",
                "name": "XTTS-v2 Cloned Voice",
                "languages": ["en", "es", "fr", "de", "it", "pt", "pl", "tr", "ru", "nl", "cs", "ar", "zh-cn", "ja", "hu", "ko"],
                "gender": "cloned",
                "age": "cloned",
                "cloneable": True,
                "source": self.speaker_wav
            })
        
        return voices
    
    def set_voice(self, voice_id: str) -> None:
        """
        Set the TTS voice (compatibility method).
        
        Args:
            voice_id: Voice identifier
        """
        logger.debug(f"Voice setting requested: {voice_id} (Coqui TTS uses voice cloning)")
    
    def set_rate(self, rate: int) -> None:
        """
        Set the TTS speech rate (compatibility method).
        
        Args:
            rate: Speech rate (not directly applicable to Coqui TTS)
        """
        logger.debug(f"Rate setting requested: {rate} (Coqui TTS uses different parameters)")
    
    def set_volume(self, volume: float) -> None:
        """
        Set the TTS volume (compatibility method).
        
        Args:
            volume: Volume level (handled at system level for Coqui TTS)
        """
        logger.debug(f"Volume setting requested: {volume} (handled at system audio level)")
    
    def set_speaker_wav(self, speaker_wav_path: str) -> None:
        """
        Set the speaker WAV file for voice cloning.
        
        Args:
            speaker_wav_path: Path to the speaker WAV file for voice cloning
        """
        if not os.path.exists(speaker_wav_path):
            raise TextToSpeechError(f"Speaker WAV file not found: {speaker_wav_path}")
        
        self.speaker_wav = speaker_wav_path
        logger.info(f"Speaker WAV set for voice cloning: {speaker_wav_path}")
    
    def set_language(self, language: str) -> None:
        """
        Set the TTS language.
        
        Args:
            language: Language code (e.g., 'en', 'es', 'fr')
        """
        supported_languages = ["en", "es", "fr", "de", "it", "pt", "pl", "tr", "ru", "nl", "cs", "ar", "zh-cn", "ja", "hu", "ko"]
        
        if language not in supported_languages:
            raise TextToSpeechError(f"Unsupported language: {language}. Supported: {supported_languages}")
        
        self.language = language
        logger.info(f"Language set to: {language}")
    
    def cleanup(self) -> None:
        """Clean up TTS resources."""
        with self._lock:
            # Clean up performance optimizer
            if hasattr(self, 'performance_optimizer'):
                self.performance_optimizer.cleanup()

            if self.tts is not None:
                # Coqui TTS cleanup
                del self.tts
                self.tts = None

            self._is_initialized = False
            logger.info("Coqui TTS resources cleaned up")

    def _get_speaker_wav_path(self) -> Optional[str]:
        """
        Get the speaker WAV path from current voice profile or direct setting.

        Returns:
            Path to speaker WAV file, None if not available
        """
        # Priority 1: Current voice profile
        if self.current_voice_profile:
            return self.current_voice_profile.audio_path

        # Priority 2: Direct speaker_wav setting
        if self.speaker_wav:
            return self.speaker_wav

        # Priority 3: Best quality profile from voice manager
        best_profile = self.voice_manager.get_best_quality_profile()
        if best_profile:
            return best_profile.audio_path

        return None

    def set_voice_profile(self, profile_id: str) -> bool:
        """
        Set the current voice profile for TTS.

        Args:
            profile_id: ID of the voice profile to use

        Returns:
            True if profile set successfully, False if not found
        """
        profile = self.voice_manager.get_profile(profile_id)
        if not profile:
            logger.warning(f"Voice profile not found: {profile_id}")
            return False

        if not profile.is_active:
            logger.warning(f"Voice profile is inactive: {profile_id}")
            return False

        self.current_voice_profile = profile
        self.language = profile.language  # Update language to match profile

        logger.info(f"Voice profile set: {profile.name} (ID: {profile_id})")
        return True

    def set_voice_profile_by_name(self, name: str) -> bool:
        """
        Set the current voice profile by name.

        Args:
            name: Name of the voice profile to use

        Returns:
            True if profile set successfully, False if not found
        """
        profile = self.voice_manager.get_profile_by_name(name)
        if not profile:
            logger.warning(f"Voice profile not found: {name}")
            return False

        return self.set_voice_profile(profile.id)

    def get_current_voice_profile(self) -> Optional[VoiceProfile]:
        """
        Get the currently active voice profile.

        Returns:
            Current voice profile, None if not set
        """
        return self.current_voice_profile

    def create_voice_profile(
        self,
        name: str,
        audio_path: str,
        description: str = "",
        language: str = "en",
        gender: str = "unknown",
        age_group: str = "unknown"
    ) -> Optional[str]:
        """
        Create a new voice profile.

        Args:
            name: Name for the voice profile
            audio_path: Path to the audio file
            description: Description of the voice
            language: Language of the voice
            gender: Gender of the voice
            age_group: Age group of the voice

        Returns:
            Profile ID if created successfully, None otherwise
        """
        try:
            profile_id = self.voice_manager.create_profile(
                name=name,
                audio_path=audio_path,
                description=description,
                language=language,
                gender=gender,
                age_group=age_group
            )

            logger.info(f"Voice profile created: {name} (ID: {profile_id})")
            return profile_id

        except Exception as e:
            logger.error(f"Failed to create voice profile: {e}")
            return None

    def list_voice_profiles(self) -> List[VoiceProfile]:
        """
        Get all available voice profiles.

        Returns:
            List of voice profiles
        """
        return self.voice_manager.list_profiles()

    def delete_voice_profile(self, profile_id: str) -> bool:
        """
        Delete a voice profile.

        Args:
            profile_id: ID of the profile to delete

        Returns:
            True if deleted successfully, False otherwise
        """
        # Don't delete if it's the current profile
        if self.current_voice_profile and self.current_voice_profile.id == profile_id:
            self.current_voice_profile = None
            logger.info("Cleared current voice profile")

        return self.voice_manager.delete_profile(profile_id)

    def get_voice_profile_stats(self) -> Dict[str, Any]:
        """
        Get statistics about voice profiles.

        Returns:
            Dictionary with profile statistics
        """
        return self.voice_manager.get_profile_stats()

    def get_performance_metrics(self):
        """
        Get performance metrics for TTS operations.

        Returns:
            PerformanceMetrics with current statistics
        """
        return self.performance_optimizer.get_performance_metrics()

    def clear_audio_cache(self) -> None:
        """Clear the audio cache."""
        self.performance_optimizer.clear_cache()
        logger.info("Audio cache cleared")

    def log_performance_metrics(self) -> None:
        """Log current performance metrics."""
        self.performance_optimizer.log_performance_metrics()
