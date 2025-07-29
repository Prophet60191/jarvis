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
from .voice_presets import get_voice_config


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
                # Configure device based on settings and suppress warnings
                import os
                import warnings

                # Suppress PyTorch MPS warnings
                os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = '0'
                warnings.filterwarnings("ignore", category=UserWarning, module="torch")

                self.device = self._detect_device()
                logger.info(f"Using device: {self.device} (from config: {self.config.coqui_device})")

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

                # Get voice configuration from preset
                voice_config = get_voice_config(self.config.coqui_voice_preset)
                target_model = voice_config["model"]
                target_speaker = voice_config["speaker_id"]
                voice_info = voice_config["voice_info"]

                logger.info(f"Loading voice preset: {self.config.coqui_voice_preset}")
                logger.info(f"Voice: {voice_info.get('name', 'Unknown')}")
                logger.info(f"Model: {target_model}")
                if target_speaker:
                    logger.info(f"Speaker: {target_speaker}")

                # Clear any cached model references
                if hasattr(TTS, '_models'):
                    TTS._models.clear()

                # Initialize TTS model with voice preset configuration (suppress verbose output)
                import sys
                import io
                from contextlib import redirect_stdout, redirect_stderr

                # Capture and suppress TTS initialization output
                with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                    self.tts = TTS(model_name=target_model, progress_bar=False).to(self.device)

                # Store speaker ID for multi-speaker models
                self.current_speaker_id = target_speaker
                self.current_voice_info = voice_info

                logger.info(f"Successfully loaded voice: {voice_info.get('name', 'Unknown')}")

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

                # Skip performance optimization to avoid MPS conflicts
                logger.info("Skipping performance optimization to avoid MPS tensor issues")

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

    def update_config(self, new_config: AudioConfig) -> None:
        """
        Update the TTS configuration and reinitialize if voice preset changed.

        Args:
            new_config: New audio configuration
        """
        # Store old values BEFORE updating config
        old_voice_preset = getattr(self.config, 'coqui_voice_preset', None)
        old_model = getattr(self.config, 'coqui_model', None)

        # Update configuration AFTER storing old values
        self.config = new_config

        # Update TTS parameters
        self.model_name = new_config.coqui_model
        self.language = new_config.coqui_language
        self.temperature = new_config.coqui_temperature
        self.length_penalty = new_config.coqui_length_penalty
        self.repetition_penalty = new_config.coqui_repetition_penalty
        self.top_k = new_config.coqui_top_k
        self.top_p = new_config.coqui_top_p

        # Check if voice preset or model changed
        new_voice_preset = new_config.coqui_voice_preset

        # Get voice configurations to compare actual models
        from .voice_presets import get_voice_config
        old_voice_config = get_voice_config(old_voice_preset) if old_voice_preset else {}
        new_voice_config = get_voice_config(new_voice_preset)

        old_actual_model = old_voice_config.get("model", old_model)
        new_actual_model = new_voice_config.get("model", new_config.coqui_model)

        voice_changed = (old_voice_preset != new_voice_preset) or (old_actual_model != new_actual_model)

        logger.info(f"Voice change check: '{old_voice_preset}' -> '{new_voice_preset}'")
        logger.info(f"Model change check: '{old_actual_model}' -> '{new_actual_model}'")
        logger.info(f"Voice changed: {voice_changed}")

        if voice_changed and self.is_initialized():
            logger.info(f"🔄 Voice preset changed from '{old_voice_preset}' to '{new_voice_preset}' - reinitializing TTS")

            # Clean up current TTS
            self.cleanup()

            # Reinitialize with new voice
            self.initialize()

            logger.info(f"✅ Voice successfully changed to: {new_voice_config.get('voice_info', {}).get('name', 'Unknown')}")
        else:
            logger.debug("Configuration updated without voice change")
    
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
            logger.debug(f"🔊 SPEAK: Starting TTS for text: '{text[:50]}{'...' if len(text) > 50 else ''}'")
            logger.debug(f"🔊 SPEAK: Text length: {len(text)} characters")

            # Check cache first
            voice_profile_id = self.current_voice_profile.id if self.current_voice_profile else "default"
            logger.debug(f"🔊 SPEAK: Using voice profile: {voice_profile_id}")
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
                logger.debug("🔊 SPEAK: Using cached audio for TTS")
                logger.debug(f"🔊 SPEAK: Cached audio shape: {wav.shape if hasattr(wav, 'shape') else 'unknown'}")
            else:
                # Generate new audio
                logger.debug("🔊 SPEAK: No cached audio found, generating new audio")
                start_time = time.time()

                with self._lock:
                    # Use voice preset configuration
                    voice_name = getattr(self, 'current_voice_info', {}).get('name', 'Current Voice')
                    logger.debug(f"🔊 SPEAK: Using voice: {voice_name}")

                    try:
                        # Prepare TTS parameters
                        tts_params = {"text": text}

                        # Add speaker for multi-speaker models
                        if hasattr(self, 'current_speaker_id') and self.current_speaker_id:
                            logger.debug(f"🔊 SPEAK: Multi-speaker model with speaker {self.current_speaker_id}")
                            tts_params["speaker"] = self.current_speaker_id
                        else:
                            logger.debug(f"🔊 SPEAK: Single-speaker model")

                        # Add advanced parameters if supported by the model
                        if hasattr(self.tts, 'synthesizer') and self.tts.synthesizer:
                            # Advanced model - can use additional parameters
                            if self.config.coqui_enable_text_splitting:
                                tts_params["split_sentences"] = True

                        # Generate speech (suppress verbose TTS output)
                        import sys
                        import io
                        from contextlib import redirect_stdout, redirect_stderr

                        # Capture and suppress TTS synthesis output
                        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                            wav = self.tts.tts(**tts_params)

                        # Convert to numpy array if it's a list
                        if isinstance(wav, list):
                            import numpy as np
                            wav = np.array(wav)

                        # Apply voice speed and speed factor
                        wav = self._apply_speed_adjustments(wav)

                        # Apply silence trimming if enabled
                        if self.config.coqui_do_trim_silence:
                            wav = self._trim_silence(wav)

                        logger.debug(f"🔊 SPEAK: Generated audio with shape: {wav.shape}")

                    except Exception as e:
                        logger.error(f"Voice synthesis failed: {e}")
                        # No fallback - raise the error
                        logger.error("Voice synthesis failed, no fallback available")
                        raise


                generation_time = time.time() - start_time
                self.performance_optimizer.record_generation_time(generation_time)

                # Cache the generated audio
                self.performance_optimizer.cache_audio(
                    text=text,
                    voice_profile_id=voice_profile_id,
                    language=self.language,
                    audio_data=wav,
                    sample_rate=self.config.coqui_sample_rate,
                    temperature=self.temperature,
                    length_penalty=self.length_penalty,
                    repetition_penalty=self.repetition_penalty,
                    top_k=self.top_k,
                    top_p=self.top_p
                )

                logger.debug(f"Generated audio in {generation_time:.2f}s")

            # Play the audio
            logger.debug(f"🔊 SPEAK: About to play audio with shape: {wav.shape if hasattr(wav, 'shape') else 'unknown'}")
            audio_start_time = time.time()

            self._play_audio(wav)

            audio_end_time = time.time()
            audio_duration = audio_end_time - audio_start_time
            logger.debug(f"🔊 SPEAK: Audio playback completed in {audio_duration:.2f} seconds")

            # Run memory optimization if needed
            if self.performance_optimizer.should_run_gc():
                self.performance_optimizer.optimize_memory()

            logger.debug("🔊 SPEAK: Coqui TTS operation completed successfully")

        except Exception as e:
            error_msg = f"Failed to speak text with Coqui TTS: {str(e)}"
            logger.error(error_msg)
            raise TextToSpeechError(error_msg, text=text) from e




    
    def _play_audio(self, wav_data) -> None:
        """
        Play audio data using system audio.

        Args:
            wav_data: Audio waveform data from TTS
        """
        logger.debug(f"🔊 _play_audio called with wav_data shape: {wav_data.shape if hasattr(wav_data, 'shape') else 'unknown'}")

        try:
            import soundfile as sf
            import sounddevice as sd

            logger.debug("🔊 Importing soundfile and sounddevice - SUCCESS")

            # Create temporary file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
                logger.debug(f"🔊 Created temporary file: {tmp_file.name}")

                # Write audio data to temporary file
                sample_rate = self.config.coqui_sample_rate
                sf.write(tmp_file.name, wav_data, sample_rate)
                logger.debug(f"🔊 Wrote audio data to file ({sample_rate} Hz)")

                # Read and play audio
                data, fs = sf.read(tmp_file.name)
                logger.debug(f"🔊 Read audio data: shape={data.shape}, sample_rate={fs}")

                # Check audio duration
                duration = len(data) / fs
                logger.debug(f"🔊 Audio duration: {duration:.2f} seconds")

                logger.debug("🔊 Starting sounddevice playback...")
                sd.play(data, fs)
                logger.debug("🔊 sounddevice.play() called - audio should be playing now")

                logger.debug("🔊 Waiting for playback to complete...")
                sd.wait()  # Wait for playback to complete
                logger.debug("🔊 sounddevice.wait() completed - playback finished")

                # Clean up temporary file
                os.unlink(tmp_file.name)
                logger.debug(f"🔊 Cleaned up temporary file: {tmp_file.name}")

        except ImportError as e:
            # Fallback: save to file and use system command
            logger.warning(f"🔊 soundfile/sounddevice not available: {e}, using system audio fallback")
            self._play_audio_fallback(wav_data)
        except Exception as e:
            logger.error(f"🔊 Failed to play audio: {e}")
            logger.error(f"🔊 Exception type: {type(e).__name__}")
            import traceback
            logger.error(f"🔊 Traceback: {traceback.format_exc()}")
            raise TextToSpeechError(f"Audio playback failed: {e}")


    
    def _play_audio_fallback(self, wav_data) -> None:
        """
        Fallback audio playback using system commands.

        Args:
            wav_data: Audio waveform data from TTS
        """
        logger.debug(f"🔊 _play_audio_fallback called with wav_data shape: {wav_data.shape if hasattr(wav_data, 'shape') else 'unknown'}")

        try:
            import soundfile as sf
            import subprocess

            logger.debug("🔊 Fallback: Importing soundfile and subprocess - SUCCESS")

            # Create temporary file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
                logger.debug(f"🔊 Fallback: Created temporary file: {tmp_file.name}")

                sample_rate = self.config.coqui_sample_rate
                sf.write(tmp_file.name, wav_data, sample_rate)
                logger.debug(f"🔊 Fallback: Wrote audio data to file ({sample_rate} Hz)")

                # Check audio duration
                data, fs = sf.read(tmp_file.name)
                duration = len(data) / fs
                logger.debug(f"🔊 Fallback: Audio duration: {duration:.2f} seconds")

                # Use system audio player
                if os.name == 'posix':  # macOS/Linux
                    if os.system('which afplay > /dev/null 2>&1') == 0:  # macOS
                        logger.debug("🔊 Fallback: Using afplay on macOS")
                        result = subprocess.run(['afplay', tmp_file.name], check=True, capture_output=True, text=True)
                        logger.debug(f"🔊 Fallback: afplay completed with return code: {result.returncode}")
                    elif os.system('which aplay > /dev/null 2>&1') == 0:  # Linux
                        logger.debug("🔊 Fallback: Using aplay on Linux")
                        result = subprocess.run(['aplay', tmp_file.name], check=True, capture_output=True, text=True)
                        logger.debug(f"🔊 Fallback: aplay completed with return code: {result.returncode}")
                    else:
                        logger.error("🔊 Fallback: No suitable audio player found")
                        raise TextToSpeechError("No audio player available")
                else:  # Windows
                    logger.debug("🔊 Fallback: Using winsound on Windows")
                    import winsound
                    winsound.PlaySound(tmp_file.name, winsound.SND_FILENAME)
                    logger.debug("🔊 Fallback: winsound playback completed")

                # Clean up
                os.unlink(tmp_file.name)
                logger.debug(f"🔊 Fallback: Cleaned up temporary file: {tmp_file.name}")

        except Exception as e:
            logger.error(f"🔊 Fallback audio playback failed: {e}")
            logger.error(f"🔊 Fallback exception type: {type(e).__name__}")
            import traceback
            logger.error(f"🔊 Fallback traceback: {traceback.format_exc()}")
            raise TextToSpeechError(f"Audio playback failed: {e}")
                
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

    def _apply_speed_adjustments(self, wav_data):
        """
        Apply voice speed and speed factor adjustments to audio.

        Args:
            wav_data: Audio waveform data

        Returns:
            Modified audio data
        """
        try:
            import numpy as np
            from scipy import signal

            # Calculate combined speed factor
            combined_speed = self.config.coqui_voice_speed * self.config.coqui_speed_factor

            if combined_speed == 1.0:
                return wav_data  # No change needed

            # Apply speed change using resampling
            if combined_speed > 1.0:
                # Speed up - reduce sample count
                new_length = int(len(wav_data) / combined_speed)
                wav_data = signal.resample(wav_data, new_length)
            elif combined_speed < 1.0:
                # Slow down - increase sample count
                new_length = int(len(wav_data) / combined_speed)
                wav_data = signal.resample(wav_data, new_length)

            logger.debug(f"🔊 Applied speed factor: {combined_speed}x")
            return wav_data

        except ImportError:
            logger.warning("scipy not available for speed adjustment, using original audio")
            return wav_data
        except Exception as e:
            logger.warning(f"Speed adjustment failed: {e}, using original audio")
            return wav_data

    def _trim_silence(self, wav_data):
        """
        Trim silence from the beginning and end of audio.

        Args:
            wav_data: Audio waveform data

        Returns:
            Trimmed audio data
        """
        try:
            import numpy as np

            # Simple silence detection based on amplitude threshold
            threshold = 0.01 * np.max(np.abs(wav_data))

            # Find first and last non-silent samples
            non_silent = np.where(np.abs(wav_data) > threshold)[0]

            if len(non_silent) == 0:
                return wav_data  # All silence, return as-is

            start_idx = max(0, non_silent[0] - int(0.1 * self.config.coqui_sample_rate))  # Keep 0.1s padding
            end_idx = min(len(wav_data), non_silent[-1] + int(0.1 * self.config.coqui_sample_rate))

            trimmed = wav_data[start_idx:end_idx]
            logger.debug(f"🔊 Trimmed silence: {len(wav_data)} -> {len(trimmed)} samples")
            return trimmed

        except Exception as e:
            logger.warning(f"Silence trimming failed: {e}, using original audio")
            return wav_data

    def cleanup(self) -> None:
        """Clean up TTS resources and reset initialization state."""
        try:
            with self._lock:
                if hasattr(self, 'tts') and self.tts is not None:
                    logger.info("Cleaning up Coqui TTS resources...")
                    del self.tts
                    self.tts = None

                # Reset initialization state
                self._is_initialized = False

                # Clear speaker info
                if hasattr(self, 'current_speaker_id'):
                    self.current_speaker_id = None
                if hasattr(self, 'current_voice_info'):
                    self.current_voice_info = None

                logger.info("Coqui TTS cleanup completed")

        except Exception as e:
            logger.warning(f"Error during TTS cleanup: {e}")

    def stop_speaking(self) -> None:
        """Stop any ongoing speech synthesis."""
        # Note: Coqui TTS doesn't have a built-in stop mechanism
        # This is handled at the audio playback level
        logger.debug("Stop speaking requested (handled by audio playback)")
