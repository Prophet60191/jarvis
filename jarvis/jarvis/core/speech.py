"""
Speech management for Jarvis Voice Assistant.

This module coordinates speech recognition and text-to-speech operations,
providing a unified interface for all speech-related functionality.
"""

import logging
import time
from typing import Optional, Dict, Any
from contextlib import contextmanager

from ..config import AudioConfig
from ..audio import MicrophoneManager, TextToSpeechManager, AudioProcessor
from ..exceptions import AudioError, SpeechRecognitionError, TextToSpeechError


logger = logging.getLogger(__name__)


class SpeechManager:
    """
    Manages speech operations for the Jarvis voice assistant.

    This class coordinates microphone input, speech recognition,
    and text-to-speech output with proper error handling and configuration.
    """

    def __init__(self, config: AudioConfig):
        """
        Initialize the speech manager.

        Args:
            config: Audio configuration settings
        """
        self.config = config
        self.microphone_manager = MicrophoneManager(config)
        self.tts_manager = TextToSpeechManager(config)
        self.audio_processor = AudioProcessor()
        self._is_initialized = False

        logger.info(f"SpeechManager initialized with config: {config}")

    def update_config(self, new_config: AudioConfig) -> None:
        """
        Update the speech manager configuration.

        Args:
            new_config: New audio configuration
        """
        logger.info("Updating speech manager configuration")

        # Update internal config reference
        self.config = new_config

        # Update child components
        if hasattr(self.microphone_manager, 'update_config'):
            self.microphone_manager.update_config(new_config)

        if hasattr(self.tts_manager, 'update_config'):
            self.tts_manager.update_config(new_config)

        logger.info("Speech manager configuration updated successfully")
    
    def initialize(self) -> None:
        """
        Initialize all speech components.
        
        Raises:
            AudioError: If initialization fails
        """
        try:
            logger.info("Initializing speech components...")
            
            # Initialize microphone
            self.microphone_manager.initialize()
            logger.info("Microphone manager initialized")
            
            # Initialize TTS
            self.tts_manager.initialize()
            logger.info("TTS manager initialized")
            
            self._is_initialized = True
            logger.info("SpeechManager initialization completed")
            
        except Exception as e:
            error_msg = f"Failed to initialize speech components: {str(e)}"
            logger.error(error_msg)
            raise AudioError(error_msg) from e
    
    def is_initialized(self) -> bool:
        """
        Check if all speech components are initialized.
        
        Returns:
            True if all components are initialized, False otherwise
        """
        return (self._is_initialized and 
                self.microphone_manager.is_initialized() and 
                self.tts_manager.is_initialized())
    
    def listen_for_speech(self, timeout: Optional[float] = None,
                         phrase_time_limit: Optional[float] = None,
                         enhance_audio: bool = True,
                         recognition_service: str = "whisper") -> Optional[str]:
        """
        Listen for speech and return the recognized text.
        
        Args:
            timeout: Maximum time to wait for audio
            phrase_time_limit: Maximum time for a single phrase
            enhance_audio: Whether to enhance audio before recognition
            recognition_service: Speech recognition service to use
            
        Returns:
            Recognized text or None if no speech detected
            
        Raises:
            AudioError: If speech listening fails
            SpeechRecognitionError: If speech recognition fails
        """
        if not self.is_initialized():
            raise AudioError("SpeechManager not initialized. Call initialize() first.")
        
        try:
            logger.debug("Listening for speech...")

            # Use the microphone manager's listen method which handles errors gracefully
            text = self.microphone_manager.listen_for_speech(
                timeout=timeout,
                phrase_time_limit=phrase_time_limit,
                service=recognition_service
            )

            # If we got text and enhancement is requested, we could enhance here
            # For now, just return the text as-is since the microphone manager
            # already handles the audio processing
            return text

        except Exception as e:
            # Log but don't raise - return None for graceful handling
            logger.debug(f"Speech listening failed: {str(e)}")
            return None
    
    def speak_text(self, text: str, wait: bool = True) -> None:
        """
        Convert text to speech and play it.

        Args:
            text: Text to speak
            wait: Whether to wait for speech to complete

        Raises:
            TextToSpeechError: If TTS fails
        """
        if not self.is_initialized():
            raise AudioError("SpeechManager not initialized. Call initialize() first.")

        try:
            logger.debug(f"🔊 SPEECH_MANAGER: speak_text called with wait={wait}")
            logger.debug(f"🔊 SPEECH_MANAGER: Original text: '{text[:50]}{'...' if len(text) > 50 else ''}'")

            # Format text for natural speech (remove markdown, fix special characters)
            from ..audio.tts_formatter import format_text_for_speech
            formatted_text = format_text_for_speech(text)

            if formatted_text != text:
                logger.debug(f"🔊 SPEECH_MANAGER: Formatted text: '{formatted_text[:50]}{'...' if len(formatted_text) > 50 else ''}'")

            speech_start_time = time.time()
            self.tts_manager.speak(formatted_text, wait)
            speech_end_time = time.time()
            speech_duration = speech_end_time - speech_start_time

            logger.debug(f"🔊 SPEECH_MANAGER: TTS manager completed in {speech_duration:.2f} seconds")

            # Add small delay after speech for better user experience
            if wait:
                logger.debug(f"🔊 SPEECH_MANAGER: Adding response delay of {self.config.response_delay}s")
                time.sleep(self.config.response_delay)
                logger.debug(f"🔊 SPEECH_MANAGER: Response delay completed")

        except Exception as e:
            speech_end_time = time.time()
            speech_duration = speech_end_time - speech_start_time if 'speech_start_time' in locals() else 0
            error_msg = f"Failed to speak text after {speech_duration:.2f}s: {str(e)}"
            logger.error(f"🔊 SPEECH_MANAGER: {error_msg}")
            raise TextToSpeechError(error_msg, text=text) from e
    
    def speak_async(self, text: str) -> None:
        """
        Convert text to speech asynchronously (non-blocking).
        
        Args:
            text: Text to speak
            
        Raises:
            TextToSpeechError: If TTS fails
        """
        self.speak_text(text, wait=False)
    
    def stop_speaking(self) -> None:
        """
        Stop any current speech output.
        
        Raises:
            TextToSpeechError: If stop operation fails
        """
        if not self.is_initialized():
            return
        
        try:
            self.tts_manager.stop_speaking()
        except Exception as e:
            error_msg = f"Failed to stop speaking: {str(e)}"
            logger.error(error_msg)
            raise TextToSpeechError(error_msg) from e
    
    @contextmanager
    def conversation_mode(self):
        """
        Context manager for conversation mode with optimized settings.
        
        This adjusts audio settings for better conversation flow.
        """
        # Store original settings
        original_timeout = self.config.timeout
        original_phrase_limit = self.config.phrase_time_limit
        
        try:
            # Optimize settings for conversation
            self.config.timeout = 5.0  # Longer timeout for conversation
            self.config.phrase_time_limit = 8.0  # Allow longer phrases
            
            logger.debug("Entered conversation mode")
            yield
            
        finally:
            # Restore original settings
            self.config.timeout = original_timeout
            self.config.phrase_time_limit = original_phrase_limit
            logger.debug("Exited conversation mode")
    
    def analyze_audio_quality(self, timeout: Optional[float] = None) -> Dict[str, Any]:
        """
        Capture and analyze audio quality.
        
        Args:
            timeout: Maximum time to wait for audio
            
        Returns:
            Dictionary containing audio quality metrics
            
        Raises:
            AudioError: If audio capture fails
        """
        if not self.is_initialized():
            raise AudioError("SpeechManager not initialized. Call initialize() first.")
        
        try:
            with self.microphone_manager.capture_audio(timeout or 3.0) as audio:
                return self.audio_processor.analyze_audio_quality(audio)
        except Exception as e:
            error_msg = f"Failed to analyze audio quality: {str(e)}"
            logger.error(error_msg)
            raise AudioError(error_msg) from e
    
    def test_speech_recognition(self, test_duration: float = 5.0) -> bool:
        """
        Test speech recognition functionality.
        
        Args:
            test_duration: Duration to listen for test speech
            
        Returns:
            True if test successful, False otherwise
        """
        if not self.is_initialized():
            logger.error("Cannot test speech recognition: not initialized")
            return False
        
        try:
            logger.info(f"Testing speech recognition for {test_duration} seconds...")
            self.speak_text("Please say something for the speech recognition test.")
            
            text = self.listen_for_speech(timeout=test_duration)
            if text:
                logger.info(f"Speech recognition test successful. Heard: '{text}'")
                self.speak_text(f"I heard you say: {text}")
                return True
            else:
                logger.warning("Speech recognition test failed: no speech detected")
                self.speak_text("I didn't hear anything during the test.")
                return False
                
        except Exception as e:
            logger.error(f"Speech recognition test failed: {str(e)}")
            self.speak_text("Speech recognition test failed.")
            return False
    
    def test_text_to_speech(self, test_text: str = "This is a test of the text to speech system.") -> bool:
        """
        Test text-to-speech functionality.
        
        Args:
            test_text: Text to use for testing
            
        Returns:
            True if test successful, False otherwise
        """
        return self.tts_manager.test_speech(test_text)
    
    def get_available_voices(self) -> list:
        """
        Get list of available TTS voices.
        
        Returns:
            List of available voices
        """
        if not self.is_initialized():
            return []
        
        try:
            return self.tts_manager.get_available_voices()
        except Exception as e:
            logger.error(f"Failed to get available voices: {str(e)}")
            return []
    
    def set_voice(self, voice_id: str) -> None:
        """
        Set the TTS voice.
        
        Args:
            voice_id: ID of the voice to use
            
        Raises:
            TextToSpeechError: If voice setting fails
        """
        if not self.is_initialized():
            raise AudioError("SpeechManager not initialized. Call initialize() first.")
        
        self.tts_manager.set_voice(voice_id)
    
    def adjust_speech_rate(self, rate: int) -> None:
        """
        Adjust the TTS speech rate.
        
        Args:
            rate: Speech rate (words per minute)
            
        Raises:
            TextToSpeechError: If rate adjustment fails
        """
        if not self.is_initialized():
            raise AudioError("SpeechManager not initialized. Call initialize() first.")
        
        self.tts_manager.set_rate(rate)
    
    def adjust_volume(self, volume: float) -> None:
        """
        Adjust the TTS volume.
        
        Args:
            volume: Volume level (0.0 to 1.0)
            
        Raises:
            TextToSpeechError: If volume adjustment fails
        """
        if not self.is_initialized():
            raise AudioError("SpeechManager not initialized. Call initialize() first.")
        
        self.tts_manager.set_volume(volume)
    
    def get_system_info(self) -> Dict[str, Any]:
        """
        Get information about the speech system.
        
        Returns:
            Dictionary containing system information
        """
        return {
            "is_initialized": self.is_initialized(),
            "microphone_initialized": self.microphone_manager.is_initialized(),
            "tts_initialized": self.tts_manager.is_initialized(),
            "available_microphones": self.microphone_manager.list_microphones(),
            "available_voices": self.get_available_voices(),
            "config": {
                "mic_index": self.config.mic_index,
                "mic_name": self.config.mic_name,
                "energy_threshold": self.config.energy_threshold,
                "tts_rate": self.config.tts_rate,
                "tts_volume": self.config.tts_volume,
                "tts_voice_preference": self.config.tts_voice_preference
            }
        }
    
    def cleanup(self) -> None:
        """Clean up all speech resources."""
        logger.info("Cleaning up speech resources")
        
        try:
            self.microphone_manager.cleanup()
        except Exception as e:
            logger.error(f"Error cleaning up microphone: {str(e)}")
        
        try:
            self.tts_manager.cleanup()
        except Exception as e:
            logger.error(f"Error cleaning up TTS: {str(e)}")
        
        self._is_initialized = False
