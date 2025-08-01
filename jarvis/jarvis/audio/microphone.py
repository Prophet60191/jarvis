"""
Microphone management for Jarvis Voice Assistant.

This module handles microphone initialization, configuration, and audio capture
with proper error handling and device management.
"""

import logging
import speech_recognition as sr
from typing import Optional, List, Dict, Any
from contextlib import contextmanager

from ..config import AudioConfig
from ..exceptions import MicrophoneError, SpeechRecognitionError, AudioError
from .whisper_speech import WhisperSpeechRecognizer


logger = logging.getLogger(__name__)


class MicrophoneManager:
    """
    Manages microphone operations for the Jarvis voice assistant.

    This class handles microphone initialization, device selection,
    audio capture, and speech recognition with proper error handling.
    """

    def __init__(self, config: AudioConfig):
        """
        Initialize the microphone manager.

        Args:
            config: Audio configuration settings
        """
        self.config = config
        self.recognizer = sr.Recognizer()
        self.microphone: Optional[sr.Microphone] = None
        self.whisper_recognizer: Optional[WhisperSpeechRecognizer] = None
        self._is_initialized = False

        # Configure recognizer settings
        self._update_recognizer_settings()

        logger.info(f"MicrophoneManager initialized with config: {config}")

    def _update_recognizer_settings(self) -> None:
        """Update recognizer settings from current configuration."""
        self.recognizer.energy_threshold = self.config.energy_threshold
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8
        self.recognizer.operation_timeout = None
        logger.debug("Updated recognizer settings from configuration")

    def update_config(self, new_config: AudioConfig) -> None:
        """
        Update the microphone configuration.

        Args:
            new_config: New audio configuration
        """
        logger.info("Updating microphone configuration")

        old_config = self.config
        self.config = new_config

        # Update recognizer settings
        self._update_recognizer_settings()

        # Update Whisper recognizer if it exists and supports config updates
        if self.whisper_recognizer:
            if hasattr(self.whisper_recognizer, 'update_config'):
                self.whisper_recognizer.update_config(new_config)
            else:
                # Reinitialize Whisper recognizer
                self.whisper_recognizer = WhisperSpeechRecognizer(new_config)

        # If microphone index changed, reinitialize microphone
        if old_config.mic_index != new_config.mic_index or old_config.mic_name != new_config.mic_name:
            if self._is_initialized:
                logger.info("Microphone device changed, reinitializing...")
                try:
                    self.initialize()
                except Exception as e:
                    logger.error(f"Error reinitializing microphone: {e}")

        logger.info("Microphone configuration updated successfully")
    
    def initialize(self) -> None:
        """
        Initialize the microphone with the configured settings.

        Raises:
            MicrophoneError: If microphone initialization fails
        """
        try:
            logger.info(f"Initializing microphone with index {self.config.mic_index}")

            # List available microphones for debugging
            available_mics = self.list_microphones()
            logger.debug(f"Available microphones: {available_mics}")

            # Try to initialize microphone with specified index
            success = self._try_initialize_microphone(self.config.mic_index)

            if not success:
                # Try fallback microphones
                logger.warning(f"Failed to initialize microphone {self.config.mic_index}, trying fallbacks...")
                success = self._try_fallback_microphones()

            if not success:
                raise MicrophoneError(
                    f"Failed to initialize any microphone. Available devices: {available_mics}",
                    mic_index=self.config.mic_index,
                    mic_name=self.config.mic_name
                )

            # Initialize Whisper speech recognizer
            logger.info("Initializing Whisper speech recognition...")
            self.whisper_recognizer = WhisperSpeechRecognizer(self.config)
            self.whisper_recognizer.initialize()

            self._is_initialized = True
            logger.info(f"Microphone and Whisper initialized successfully: {self.config.mic_name}")

        except Exception as e:
            if isinstance(e, MicrophoneError):
                raise
            error_msg = f"Unexpected error during microphone initialization: {str(e)}"
            logger.error(error_msg)
            raise MicrophoneError(error_msg) from e

    def _try_initialize_microphone(self, mic_index: int) -> bool:
        """
        Try to initialize a specific microphone.

        Args:
            mic_index: Microphone device index to try

        Returns:
            True if successful, False otherwise
        """
        try:
            # Initialize microphone with specified index
            test_microphone = sr.Microphone(device_index=mic_index)

            # Test microphone by adjusting for ambient noise
            with test_microphone as source:
                logger.info(f"Testing microphone {mic_index}, adjusting for ambient noise...")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)

            # If we get here, the microphone works
            self.microphone = test_microphone
            logger.info(f"Successfully initialized microphone {mic_index}")
            return True

        except Exception as e:
            logger.warning(f"Failed to initialize microphone {mic_index}: {e}")
            return False

    def _try_fallback_microphones(self) -> bool:
        """
        Try to initialize fallback microphones.

        Returns:
            True if any microphone was successfully initialized
        """
        available_mics = self.list_microphones()

        # Try each available input device
        for mic_info in available_mics:
            mic_index = mic_info['index']

            # Skip the one we already tried
            if mic_index == self.config.mic_index:
                continue

            # Only try input devices (devices with input channels)
            try:
                import pyaudio
                p = pyaudio.PyAudio()
                device_info = p.get_device_info_by_index(mic_index)
                p.terminate()

                if device_info['maxInputChannels'] > 0:
                    logger.info(f"Trying fallback microphone: {mic_info['name']}")
                    if self._try_initialize_microphone(mic_index):
                        logger.info(f"Successfully initialized fallback microphone: {mic_info['name']}")
                        return True

            except Exception as e:
                logger.debug(f"Error checking device {mic_index}: {e}")
                continue

        return False
    
    def is_initialized(self) -> bool:
        """
        Check if the microphone is properly initialized.
        
        Returns:
            True if microphone is initialized, False otherwise
        """
        return self._is_initialized and self.microphone is not None
    
    @contextmanager
    def capture_audio(self, timeout: Optional[float] = None, phrase_time_limit: Optional[float] = None):
        """
        Context manager for capturing audio from the microphone.
        
        Args:
            timeout: Maximum time to wait for audio (uses config default if None)
            phrase_time_limit: Maximum time for a single phrase (uses config default if None)
            
        Yields:
            AudioData object containing the captured audio
            
        Raises:
            MicrophoneError: If microphone is not initialized or capture fails
            AudioError: If audio capture times out or fails
        """
        if not self.is_initialized():
            raise MicrophoneError("Microphone not initialized. Call initialize() first.")
        
        timeout = timeout or self.config.timeout
        phrase_time_limit = phrase_time_limit or self.config.phrase_time_limit
        
        try:
            with self.microphone as source:
                logger.debug(f"Listening for audio (timeout={timeout}, phrase_limit={phrase_time_limit})")
                audio = self.recognizer.listen(
                    source,
                    timeout=timeout,
                    phrase_time_limit=phrase_time_limit
                )
                yield audio
                
        except sr.WaitTimeoutError:
            logger.debug("Audio capture timed out")
            raise AudioError("Audio capture timed out")
        except sr.UnknownValueError:
            # This is normal - no speech detected
            logger.debug("No speech detected during audio capture")
            raise AudioError("Could not understand audio")
        except Exception as e:
            error_msg = f"Failed to capture audio: {str(e)}"
            logger.error(error_msg)
            raise AudioError(error_msg) from e
    
    def recognize_speech(self, audio_data, service: str = "whisper") -> str:
        """
        Recognize speech from audio data using the specified service.
        
        Args:
            audio_data: AudioData object containing the audio to recognize
            service: Speech recognition service to use ("whisper", "google", "sphinx")
            
        Returns:
            Recognized text as a string
            
        Raises:
            SpeechRecognitionError: If speech recognition fails
        """
        try:
            logger.debug(f"Recognizing speech using {service} service")
            
            if service.lower() == "whisper":
                if not self.whisper_recognizer or not self.whisper_recognizer.is_initialized():
                    raise SpeechRecognitionError("Whisper recognizer not initialized")
                text = self.whisper_recognizer.recognize_speech_from_audio_data(audio_data)
            elif service.lower() == "google":
                text = self.recognizer.recognize_google(audio_data)
            elif service.lower() == "sphinx":
                text = self.recognizer.recognize_sphinx(audio_data)
            else:
                raise SpeechRecognitionError(f"Unsupported recognition service: {service}")
            
            logger.debug(f"Speech recognized: '{text}'")
            return text
            
        except sr.UnknownValueError:
            logger.debug("No speech detected or could not understand audio")
            raise SpeechRecognitionError("Could not understand audio", recognition_service=service)
        except sr.RequestError as e:
            error_msg = f"Speech recognition service error: {str(e)}"
            logger.error(error_msg)
            raise SpeechRecognitionError(error_msg, recognition_service=service) from e
        except SpeechRecognitionError:
            # Re-raise SpeechRecognitionError as-is to preserve original message
            raise
        except Exception as e:
            error_msg = f"Unexpected error during speech recognition: {str(e)}"
            logger.error(error_msg)
            raise SpeechRecognitionError(error_msg, recognition_service=service) from e
    
    def listen_for_speech(self, timeout: Optional[float] = None,
                         phrase_time_limit: Optional[float] = None,
                         service: str = "whisper") -> Optional[str]:
        """
        Listen for speech and return the recognized text.

        Args:
            timeout: Maximum time to wait for audio
            phrase_time_limit: Maximum time for a single phrase
            service: Speech recognition service to use

        Returns:
            Recognized text or None if no speech was detected

        Raises:
            MicrophoneError: If microphone operations fail
            SpeechRecognitionError: If speech recognition fails
        """
        try:
            with self.capture_audio(timeout, phrase_time_limit) as audio:
                # Try primary service first
                try:
                    return self.recognize_speech(audio, service)
                except SpeechRecognitionError as e:
                    # If Whisper fails with "No speech detected", try Google as fallback
                    if service.lower() == "whisper" and "No speech detected" in str(e):
                        logger.debug("Whisper failed to detect speech, trying Google fallback...")
                        try:
                            result = self.recognize_speech(audio, "google")
                            logger.info(f"Google fallback successful: '{result}'")
                            return result
                        except Exception as fallback_error:
                            logger.debug(f"Google fallback also failed: {fallback_error}")
                    # Re-raise original error if fallback fails or not applicable
                    raise e
        except AudioError as e:
            # Check if this is a wrapped SpeechRecognitionError from capture_audio
            if "No speech detected" in str(e) and service.lower() == "whisper":
                logger.debug("Audio capture failed due to Whisper speech detection, trying Google fallback...")
                try:
                    # Try to capture audio again and use Google
                    with self.capture_audio(timeout, phrase_time_limit) as audio:
                        result = self.recognize_speech(audio, "google")
                        logger.info(f"Google fallback successful after audio error: '{result}'")
                        return result
                except Exception as fallback_error:
                    logger.debug(f"Google fallback after audio error also failed: {fallback_error}")
            # Return None for normal timeout/no speech cases
            return None
        except SpeechRecognitionError:
            # Recognition issues - return None (normal)
            return None
    
    @staticmethod
    def list_microphones() -> List[Dict[str, Any]]:
        """
        List all available microphones on the system with detailed information.

        Returns:
            List of dictionaries containing microphone information
        """
        microphones = []

        try:
            import pyaudio
            p = pyaudio.PyAudio()

            for mic_index in range(p.get_device_count()):
                try:
                    device_info = p.get_device_info_by_index(mic_index)

                    # Only include devices with input channels
                    if device_info['maxInputChannels'] > 0:
                        microphones.append({
                            'index': mic_index,
                            'name': device_info['name'],
                            'max_input_channels': device_info['maxInputChannels'],
                            'default_sample_rate': device_info['defaultSampleRate'],
                            'is_default': mic_index == p.get_default_input_device_info()['index']
                        })
                except Exception as e:
                    logger.debug(f"Error getting microphone {mic_index}: {e}")

            p.terminate()

        except Exception as e:
            logger.error(f"Error listing microphones with PyAudio: {e}")
            # Fallback to speech_recognition method
            try:
                mic_names = sr.Microphone.list_microphone_names()
                for mic_index, mic_name in enumerate(mic_names):
                    microphones.append({
                        'index': mic_index,
                        'name': mic_name,
                        'max_input_channels': 1,  # Assume 1 channel
                        'default_sample_rate': 44100,  # Assume standard rate
                        'is_default': mic_index == 0
                    })
            except Exception as fallback_e:
                logger.error(f"Fallback microphone listing also failed: {fallback_e}")

        return microphones

    @staticmethod
    def get_recommended_microphone() -> Optional[Dict[str, Any]]:
        """
        Get the recommended microphone for the current system.

        Returns:
            Dictionary with recommended microphone info, or None if none found
        """
        available_mics = MicrophoneManager.list_microphones()

        if not available_mics:
            return None

        # Prefer default input device
        for mic in available_mics:
            if mic.get('is_default', False):
                logger.info(f"Recommended microphone (default): {mic['name']}")
                return mic

        # Prefer built-in microphones (usually have "MacBook" or "Built-in" in name)
        for mic in available_mics:
            name_lower = mic['name'].lower()
            if any(keyword in name_lower for keyword in ['macbook', 'built-in', 'internal']):
                logger.info(f"Recommended microphone (built-in): {mic['name']}")
                return mic

        # Return first available microphone
        logger.info(f"Recommended microphone (first available): {available_mics[0]['name']}")
        return available_mics[0]

    @staticmethod
    def check_microphone_permissions() -> bool:
        """
        Check if the application has microphone permissions.

        Returns:
            True if permissions are granted, False otherwise
        """
        try:
            import pyaudio
            p = pyaudio.PyAudio()

            # Try to get default input device
            default_device = p.get_default_input_device_info()

            # Try to create a test stream
            test_stream = p.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=44100,
                input=True,
                input_device_index=default_device['index'],
                frames_per_buffer=1024
            )

            # If we get here, permissions are OK
            test_stream.close()
            p.terminate()

            logger.info("✅ Microphone permissions verified")
            return True

        except Exception as e:
            logger.warning(f"⚠️ Microphone permission check failed: {e}")
            return False

    def test_microphone(self, duration: float = 3.0) -> bool:
        """
        Test the microphone by capturing audio for a specified duration.
        
        Args:
            duration: Duration in seconds to test the microphone
            
        Returns:
            True if test successful, False otherwise
        """
        if not self.is_initialized():
            logger.error("Cannot test microphone: not initialized")
            return False
        
        try:
            logger.info(f"Testing microphone for {duration} seconds...")
            with self.capture_audio(timeout=duration + 1, phrase_time_limit=duration):
                logger.info("Microphone test successful")
                return True
        except Exception as e:
            logger.error(f"Microphone test failed: {str(e)}")
            return False
    
    def cleanup(self) -> None:
        """Clean up microphone resources."""
        logger.info("Cleaning up microphone resources")

        # Clean up Whisper recognizer
        if hasattr(self, 'whisper_recognizer') and self.whisper_recognizer:
            try:
                self.whisper_recognizer.cleanup()
                logger.debug("Whisper recognizer cleaned up")
            except Exception as e:
                logger.error(f"Error cleaning up Whisper recognizer: {e}")

        # Clean up microphone
        if self.microphone:
            self.microphone = None

        self._is_initialized = False
