"""
Whisper-based Speech Recognition for Jarvis Voice Assistant.

This module provides local speech recognition using OpenAI's Whisper model
via the faster-whisper implementation for optimal performance on Apple Silicon.
"""

import logging
import tempfile
import wave
import numpy as np
from typing import Optional, Dict, Any
from pathlib import Path
import threading
from faster_whisper import WhisperModel

from ..config import AudioConfig
from ..exceptions import SpeechRecognitionError

logger = logging.getLogger(__name__)


class WhisperSpeechRecognizer:
    """
    Local speech recognition using Faster-Whisper for 100% offline operation.
    
    This provides high-quality speech recognition without requiring internet
    connectivity, ensuring privacy and reliability.
    """
    
    def __init__(self, config: AudioConfig):
        """
        Initialize the Whisper speech recognizer.
        
        Args:
            config: Audio configuration settings
        """
        self.config = config
        self.model: Optional[WhisperModel] = None
        self._is_initialized = False
        self._lock = threading.Lock()
        
        # Whisper configuration
        self.model_size = getattr(config, 'whisper_model_size', 'base')
        self.device = getattr(config, 'whisper_device', 'cpu')
        self.language = getattr(config, 'whisper_language', 'en')
        self.compute_type = getattr(config, 'whisper_compute_type', 'float32')
        
        logger.info(f"WhisperSpeechRecognizer initialized with model: {self.model_size}")
    
    def initialize(self) -> None:
        """
        Initialize the Whisper model.
        
        Raises:
            SpeechRecognitionError: If model initialization fails
        """
        try:
            logger.info(f"Loading Whisper model: {self.model_size}")
            
            with self._lock:
                # Load the Whisper model
                self.model = WhisperModel(
                    self.model_size,
                    device=self.device,
                    compute_type=self.compute_type
                )
                
                self._is_initialized = True
                logger.info(f"Whisper model '{self.model_size}' loaded successfully")
                
        except Exception as e:
            error_msg = f"Failed to initialize Whisper model: {str(e)}"
            logger.error(error_msg)
            raise SpeechRecognitionError(error_msg) from e
    
    def is_initialized(self) -> bool:
        """
        Check if the Whisper model is properly initialized.
        
        Returns:
            True if model is initialized, False otherwise
        """
        return self._is_initialized and self.model is not None
    
    def recognize_speech_from_audio_data(self, audio_data) -> str:
        """
        Recognize speech from speech_recognition AudioData object.
        
        Args:
            audio_data: AudioData object from speech_recognition library
            
        Returns:
            Recognized text as a string
            
        Raises:
            SpeechRecognitionError: If speech recognition fails
        """
        if not self.is_initialized():
            raise SpeechRecognitionError("Whisper model not initialized. Call initialize() first.")
        
        try:
            # Convert AudioData to temporary WAV file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                # Get raw audio data
                raw_data = audio_data.get_raw_data()
                
                # Create WAV file
                with wave.open(temp_file.name, 'wb') as wav_file:
                    wav_file.setnchannels(1)  # Mono
                    wav_file.setsampwidth(audio_data.sample_width)
                    wav_file.setframerate(audio_data.sample_rate)
                    wav_file.writeframes(raw_data)
                
                # Transcribe using Whisper
                text = self._transcribe_file(temp_file.name)
                
                # Clean up temporary file
                Path(temp_file.name).unlink(missing_ok=True)
                
                return text
                
        except Exception as e:
            error_msg = f"Failed to recognize speech with Whisper: {str(e)}"
            logger.error(error_msg)
            raise SpeechRecognitionError(error_msg, recognition_service="whisper") from e
    
    def recognize_speech_from_file(self, audio_file_path: str) -> str:
        """
        Recognize speech from an audio file.
        
        Args:
            audio_file_path: Path to the audio file
            
        Returns:
            Recognized text as a string
            
        Raises:
            SpeechRecognitionError: If speech recognition fails
        """
        if not self.is_initialized():
            raise SpeechRecognitionError("Whisper model not initialized. Call initialize() first.")
        
        try:
            return self._transcribe_file(audio_file_path)
        except Exception as e:
            error_msg = f"Failed to recognize speech from file: {str(e)}"
            logger.error(error_msg)
            raise SpeechRecognitionError(error_msg, recognition_service="whisper") from e
    
    def _transcribe_file(self, audio_file_path: str) -> str:
        """
        Internal method to transcribe an audio file using Whisper.
        
        Args:
            audio_file_path: Path to the audio file
            
        Returns:
            Transcribed text
        """
        logger.debug(f"Transcribing audio file: {audio_file_path}")
        
        with self._lock:
            # Transcribe with speed-optimized parameters
            # Research shows these settings provide best speed/accuracy balance
            segments, info = self.model.transcribe(
                audio_file_path,
                language=self.language if self.language != 'auto' else None,
                beam_size=1,  # Reduced from 5 for speed (greedy decoding)
                best_of=1,    # Reduced from 5 for speed
                temperature=0.0,
                condition_on_previous_text=False,
                vad_filter=False,  # DISABLED: VAD was removing valid speech
                # Speed optimizations: lower beam_size and best_of for faster inference
            )
            
            # Combine all segments into a single text
            text_segments = []
            for segment in segments:
                text_segments.append(segment.text.strip())
            
            full_text = " ".join(text_segments).strip()
            
            logger.debug(f"Whisper transcription: '{full_text}'")
            logger.debug(f"Detected language: {info.language} (probability: {info.language_probability:.2f})")
            
            if not full_text:
                raise SpeechRecognitionError("No speech detected in audio", recognition_service="whisper")
            
            return full_text
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the loaded Whisper model.
        
        Returns:
            Dictionary containing model information
        """
        if not self.is_initialized():
            return {"status": "not_initialized"}
        
        return {
            "status": "initialized",
            "model_size": self.model_size,
            "device": self.device,
            "language": self.language,
            "compute_type": self.compute_type
        }
    
    def set_language(self, language: str) -> None:
        """
        Set the language for speech recognition.
        
        Args:
            language: Language code (e.g., 'en', 'es', 'fr') or 'auto' for auto-detection
        """
        self.language = language
        logger.info(f"Whisper language set to: {language}")
    
    def cleanup(self) -> None:
        """
        Clean up Whisper model resources.
        """
        if self.model is not None:
            try:
                with self._lock:
                    del self.model
                    self.model = None
            except Exception as e:
                logger.warning(f"Error during Whisper cleanup: {e}")
            
            self._is_initialized = False
            logger.info("Whisper model resources cleaned up")


# Convenience function for backward compatibility
def create_whisper_recognizer(config: AudioConfig) -> WhisperSpeechRecognizer:
    """
    Create and initialize a Whisper speech recognizer.
    
    Args:
        config: Audio configuration settings
        
    Returns:
        Initialized WhisperSpeechRecognizer instance
    """
    recognizer = WhisperSpeechRecognizer(config)
    recognizer.initialize()
    return recognizer
