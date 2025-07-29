"""
Text-to-Speech management for Jarvis Voice Assistant.

This module handles text-to-speech operations using Coqui TTS for
high-quality neural speech synthesis.
"""

import logging
from typing import List, Dict, Any

from ..config import AudioConfig
from ..exceptions import TextToSpeechError
from .coqui_tts import CoquiTTSManager


logger = logging.getLogger(__name__)


class TextToSpeechManager:
    """
    Manages text-to-speech operations for the Jarvis voice assistant.

    This class uses Coqui TTS for high-quality neural speech synthesis.
    """

    def __init__(self, config: AudioConfig):
        """
        Initialize the text-to-speech manager with Coqui TTS only.

        Args:
            config: Audio configuration settings
        """
        self.config = config

        # Use Coqui TTS as the only TTS backend
        self.coqui_tts = CoquiTTSManager(config)

        logger.info(f"TextToSpeechManager initialized with Coqui TTS only")

    def update_config(self, new_config: AudioConfig) -> None:
        """
        Update the TTS configuration.

        Args:
            new_config: New audio configuration
        """
        logger.info("Updating TTS configuration")

        # Update internal config reference
        self.config = new_config

        # Update all TTS backends with new configuration
        try:
            # Update Coqui TTS settings (primary)
            if hasattr(self.coqui_tts, 'update_config'):
                self.coqui_tts.update_config(new_config)
            else:
                # Reinitialize if no update method available
                self.coqui_tts = CoquiTTSManager(new_config)
                if self.is_initialized():
                    self.coqui_tts.initialize()

            # Only Coqui TTS is used now

            logger.info("TTS configuration updated successfully")

        except Exception as e:
            logger.error(f"Error updating TTS configuration: {e}")

    def initialize(self) -> None:
        """
        Initialize the TTS engine with the configured settings.

        Raises:
            TextToSpeechError: If TTS engine initialization fails
        """
        try:
            # Initialize Coqui TTS as the only TTS backend
            logger.info("Initializing Coqui TTS engine...")
            self.coqui_tts.initialize()
            logger.info("Coqui TTS engine initialized successfully")

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
        return self.coqui_tts.is_initialized()

    def speak(self, text: str, wait: bool = True) -> None:
        """
        Convert text to speech and play it using Coqui TTS.

        Args:
            text: Text to convert to speech
            wait: Whether to wait for speech to complete

        Raises:
            TextToSpeechError: If TTS engine fails
        """
        try:
            # Use Coqui TTS only
            self.coqui_tts.speak(text, wait)
        except Exception as e:
            logger.error(f"Coqui TTS failed: {e}")
            raise TextToSpeechError(f"TTS failed: {e}") from e

    def speak_async(self, text: str) -> None:
        """
        Convert text to speech asynchronously (non-blocking).

        Args:
            text: Text to convert to speech

        Raises:
            TextToSpeechError: If TTS operation fails
        """
        self.coqui_tts.speak_async(text)

    def stop_speaking(self) -> None:
        """
        Stop any current speech output.

        Raises:
            TextToSpeechError: If stop operation fails
        """
        self.coqui_tts.stop_speaking()

    def get_available_voices(self) -> List[Dict[str, Any]]:
        """
        Get list of available TTS voices.

        Returns:
            List of dictionaries containing voice information

        Raises:
            TextToSpeechError: If unable to retrieve voices
        """
        return self.coqui_tts.get_available_voices()
    
    def set_voice(self, voice_id: str) -> None:
        """
        Set the TTS voice by ID.

        Args:
            voice_id: ID of the voice to use

        Raises:
            TextToSpeechError: If voice setting fails
        """
        self.coqui_tts.set_voice(voice_id)

    def set_rate(self, rate: int) -> None:
        """
        Set the TTS speech rate.

        Args:
            rate: Speech rate (words per minute)

        Raises:
            TextToSpeechError: If rate setting fails
        """
        self.coqui_tts.set_rate(rate)

    def set_volume(self, volume: float) -> None:
        """
        Set the TTS volume.

        Args:
            volume: Volume level (0.0 to 1.0)

        Raises:
            TextToSpeechError: If volume setting fails
        """
        self.coqui_tts.set_volume(volume)

    def test_speech(self, test_text: str = "Hello, this is a test of the Coqui TTS system.") -> bool:
        """
        Test the TTS system with sample text.

        Args:
            test_text: Text to use for testing

        Returns:
            True if test successful, False otherwise
        """
        if not self.is_initialized():
            logger.error("Cannot test TTS: not initialized")
            return False

        try:
            logger.info("Testing Coqui TTS system...")
            self.speak(test_text)
            logger.info("Coqui TTS test successful")
            return True
        except Exception as e:
            logger.error(f"Coqui TTS test failed: {str(e)}")
            return False

    def cleanup(self) -> None:
        """Clean up TTS engine resources."""
        try:
            logger.info("Cleaning up Coqui TTS engine resources")
            self.coqui_tts.cleanup()
        except Exception as e:
            logger.error(f"Error during Coqui TTS cleanup: {str(e)}")

    # Coqui TTS specific methods
    def set_speaker_wav(self, speaker_wav_path: str) -> None:
        """
        Set the speaker WAV file for voice cloning.

        Args:
            speaker_wav_path: Path to the speaker WAV file for voice cloning
        """
        self.coqui_tts.set_speaker_wav(speaker_wav_path)

    def set_language(self, language: str) -> None:
        """
        Set the TTS language.

        Args:
            language: Language code (e.g., 'en', 'es', 'fr')
        """
        self.coqui_tts.set_language(language)

    # Streaming TTS methods
    def speak_streaming(self, text: str, callback=None) -> None:
        """
        Convert text to speech using streaming for faster response.

        Args:
            text: Text to convert to speech
            callback: Optional callback function called for each chunk

        Raises:
            TextToSpeechError: If streaming TTS fails
        """
        self.streaming_tts.speak_streaming(text, callback)

    def stop_streaming(self) -> None:
        """Stop any current streaming TTS."""
        self.streaming_tts.stop_streaming()

    def is_streaming(self) -> bool:
        """Check if streaming TTS is currently active."""
        return self.streaming_tts.is_streaming()

    def wait_for_streaming_completion(self, timeout=None) -> bool:
        """
        Wait for streaming TTS to complete.

        Args:
            timeout: Maximum time to wait in seconds

        Returns:
            True if completed, False if timed out
        """
        return self.streaming_tts.wait_for_completion(timeout)

    # Voice profile methods for streaming
    def set_streaming_voice_profile(self, profile_id: str) -> bool:
        """Set voice profile for streaming TTS."""
        return self.streaming_tts.set_voice_profile(profile_id)

    def set_streaming_voice_profile_by_name(self, name: str) -> bool:
        """Set voice profile by name for streaming TTS."""
        return self.streaming_tts.set_voice_profile_by_name(name)

    # Multi-language TTS methods
    def speak_multilingual(self, text: str, language=None, auto_detect=None) -> None:
        """
        Convert text to speech with multi-language support.

        Args:
            text: Text to convert to speech
            language: Specific language to use (optional)
            auto_detect: Whether to auto-detect language (optional)

        Raises:
            TextToSpeechError: If TTS operation fails
        """
        self.multilang_tts.speak_multilingual(text, language, auto_detect)

    def detect_language(self, text: str):
        """
        Detect the language of the given text.

        Args:
            text: Text to analyze

        Returns:
            LanguageDetectionResult if detection successful, None otherwise
        """
        return self.multilang_tts.detect_language(text)

    def get_supported_languages(self) -> List[str]:
        """Get list of supported language codes."""
        return self.multilang_tts.get_supported_languages()

    def get_language_name(self, language_code: str) -> str:
        """Get human-readable language name."""
        return self.multilang_tts.get_language_name(language_code)

    def set_language_voice_profile(self, language: str, profile_id: str) -> bool:
        """Set the voice profile to use for a specific language."""
        return self.multilang_tts.set_language_voice_profile(language, profile_id)

    def get_voice_profiles_for_language(self, language: str):
        """Get voice profiles available for a specific language."""
        return self.multilang_tts.get_voice_profiles_for_language(language)

    def get_language_statistics(self):
        """Get statistics about language support and voice profiles."""
        return self.multilang_tts.get_language_statistics()

    def cleanup(self) -> None:
        """Clean up TTS resources."""
        logger.info("Cleaning up TTS resources")

        # Clean up Apple TTS (primary backend)
        if hasattr(self, 'apple_tts') and self.apple_tts:
            try:
                self.apple_tts.cleanup()
                logger.debug("Apple TTS cleaned up")
            except Exception as e:
                logger.error(f"Error cleaning up Apple TTS: {e}")

        # Clean up other TTS systems
        if hasattr(self, 'streaming_tts') and self.streaming_tts:
            try:
                self.streaming_tts.cleanup()
            except Exception as e:
                logger.error(f"Error cleaning up streaming TTS: {e}")

        if hasattr(self, 'multilang_tts') and self.multilang_tts:
            try:
                self.multilang_tts.cleanup()
            except Exception as e:
                logger.error(f"Error cleaning up multilang TTS: {e}")

        if hasattr(self, 'coqui_tts') and self.coqui_tts:
            try:
                self.coqui_tts.cleanup()
            except Exception as e:
                logger.error(f"Error cleaning up Coqui TTS: {e}")
