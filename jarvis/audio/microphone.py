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
        self._is_initialized = False
        
        # Configure recognizer settings
        self.recognizer.energy_threshold = config.energy_threshold
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8
        self.recognizer.operation_timeout = None
        
        logger.info(f"MicrophoneManager initialized with config: {config}")
    
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
            
            # Initialize microphone with specified index
            self.microphone = sr.Microphone(device_index=self.config.mic_index)
            
            # Test microphone by adjusting for ambient noise
            with self.microphone as source:
                logger.info("Adjusting for ambient noise...")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
            
            self._is_initialized = True
            logger.info(f"Microphone initialized successfully: {self.config.mic_name}")
            
        except OSError as e:
            error_msg = f"Failed to initialize microphone with index {self.config.mic_index}: {str(e)}"
            logger.error(error_msg)
            raise MicrophoneError(
                error_msg,
                mic_index=self.config.mic_index,
                mic_name=self.config.mic_name
            ) from e
        except Exception as e:
            error_msg = f"Unexpected error during microphone initialization: {str(e)}"
            logger.error(error_msg)
            raise MicrophoneError(error_msg) from e
    
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
    
    def recognize_speech(self, audio_data, service: str = "google") -> str:
        """
        Recognize speech from audio data using the specified service.
        
        Args:
            audio_data: AudioData object containing the audio to recognize
            service: Speech recognition service to use ("google", "sphinx", etc.)
            
        Returns:
            Recognized text as a string
            
        Raises:
            SpeechRecognitionError: If speech recognition fails
        """
        try:
            logger.debug(f"Recognizing speech using {service} service")
            
            if service.lower() == "google":
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
        except Exception as e:
            error_msg = f"Unexpected error during speech recognition: {str(e)}"
            logger.error(error_msg)
            raise SpeechRecognitionError(error_msg, recognition_service=service) from e
    
    def listen_for_speech(self, timeout: Optional[float] = None, 
                         phrase_time_limit: Optional[float] = None,
                         service: str = "google") -> Optional[str]:
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
                return self.recognize_speech(audio, service)
        except (AudioError, SpeechRecognitionError):
            # Timeout, no speech, or recognition issues - return None (normal)
            return None
    
    @staticmethod
    def list_microphones() -> List[Dict[str, Any]]:
        """
        List all available microphones on the system.
        
        Returns:
            List of dictionaries containing microphone information
        """
        microphones = []
        try:
            for index, name in enumerate(sr.Microphone.list_microphone_names()):
                microphones.append({
                    "index": index,
                    "name": name
                })
        except Exception as e:
            logger.error(f"Failed to list microphones: {str(e)}")
        
        return microphones
    
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
        if self.microphone:
            logger.info("Cleaning up microphone resources")
            self.microphone = None
            self._is_initialized = False
