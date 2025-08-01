"""
Apple System TTS Manager for Jarvis Voice Assistant.

This module provides a reliable, high-quality TTS system using Apple's built-in
system voices, optimized for Apple Silicon Macs.
"""

import logging
import pyttsx3
from typing import Optional, List, Dict, Any
from threading import Lock
from ..config import AudioConfig
from ..exceptions import TextToSpeechError

logger = logging.getLogger(__name__)


class AppleTTSManager:
    """
    Apple System TTS Manager using pyttsx3 with Apple's high-quality voices.
    
    This provides a reliable, fast, and high-quality TTS solution that's
    perfectly compatible with Apple Silicon Macs.
    """
    
    def __init__(self, config: AudioConfig):
        """
        Initialize the Apple TTS manager.
        
        Args:
            config: Audio configuration settings
        """
        self.config = config
        self.engine: Optional[pyttsx3.Engine] = None
        self._is_initialized = False
        self._lock = Lock()  # Thread safety for TTS operations
        
        # TTS settings from config
        self.voice_name = getattr(config, 'tts_voice_preference', 'Daniel')
        self.rate = getattr(config, 'tts_rate', 180)
        self.volume = getattr(config, 'tts_volume', 0.9)
        
        logger.info(f"AppleTTSManager initialized with voice: {self.voice_name}")
    
    def initialize(self) -> None:
        """
        Initialize the Apple TTS engine with the configured settings.
        
        Raises:
            TextToSpeechError: If TTS engine initialization fails
        """
        try:
            logger.info("Initializing Apple TTS engine...")
            
            with self._lock:
                # Initialize pyttsx3 engine
                self.engine = pyttsx3.init()
                
                # Configure voice
                self._set_voice(self.voice_name)
                
                # Configure speech rate
                self.engine.setProperty('rate', self.rate)
                
                # Configure volume
                self.engine.setProperty('volume', self.volume)
                
                self._is_initialized = True
                logger.info(f"Apple TTS engine initialized successfully with voice: {self.voice_name}")
                
        except Exception as e:
            error_msg = f"Failed to initialize Apple TTS engine: {str(e)}"
            logger.error(error_msg)
            raise TextToSpeechError(error_msg) from e
    
    def _set_voice(self, voice_name: str) -> None:
        """
        Set the TTS voice by name.
        
        Args:
            voice_name: Name of the voice to use
        """
        voices = self.engine.getProperty('voices')
        
        # Try to find the exact voice name
        for voice in voices:
            if voice.name == voice_name:
                self.engine.setProperty('voice', voice.id)
                logger.info(f"Voice set to: {voice_name}")
                return
        
        # If exact match not found, try partial match
        for voice in voices:
            if voice_name.lower() in voice.name.lower():
                self.engine.setProperty('voice', voice.id)
                logger.info(f"Voice set to: {voice.name} (partial match for {voice_name})")
                return
        
        # If no match found, use default and log warning
        logger.warning(f"Voice '{voice_name}' not found, using default voice")
    
    def is_initialized(self) -> bool:
        """
        Check if the TTS engine is properly initialized.
        
        Returns:
            True if TTS engine is initialized, False otherwise
        """
        return self._is_initialized and self.engine is not None
    
    def speak(self, text: str, wait: bool = True) -> None:
        """
        Convert text to speech and play it.
        
        Args:
            text: Text to convert to speech
            wait: Whether to wait for speech to complete (default: True)
        
        Raises:
            TextToSpeechError: If TTS fails
        """
        if not text or not text.strip():
            logger.warning("Empty text provided for TTS")
            return
        
        if not self.is_initialized():
            raise TextToSpeechError("Apple TTS engine not initialized. Call initialize() first.")
        
        try:
            logger.debug(f"Speaking text: '{text[:50]}{'...' if len(text) > 50 else ''}'")
            
            with self._lock:
                self.engine.say(text)
                if wait:
                    self.engine.runAndWait()
                
            logger.debug("Apple TTS speech completed")
            
        except Exception as e:
            error_msg = f"Failed to speak text with Apple TTS: {str(e)}"
            logger.error(error_msg)
            raise TextToSpeechError(error_msg, text=text) from e
    
    def speak_async(self, text: str) -> None:
        """
        Convert text to speech asynchronously (non-blocking).
        
        Args:
            text: Text to convert to speech
        """
        self.speak(text, wait=False)
    
    def stop_speaking(self) -> None:
        """
        Stop any current speech output.
        """
        if self.is_initialized():
            try:
                with self._lock:
                    self.engine.stop()
                logger.debug("Apple TTS speech stopped")
            except Exception as e:
                logger.warning(f"Failed to stop Apple TTS: {e}")
    
    def get_available_voices(self) -> List[Dict[str, Any]]:
        """
        Get list of available system voices.
        
        Returns:
            List of dictionaries containing voice information
        """
        if not self.is_initialized():
            raise TextToSpeechError("Apple TTS engine not initialized. Call initialize() first.")
        
        voices = []
        system_voices = self.engine.getProperty('voices')
        
        for i, voice in enumerate(system_voices):
            voices.append({
                "index": i,
                "name": voice.name,
                "id": voice.id,
                "language": getattr(voice, 'languages', ['en']),
                "gender": "unknown"  # pyttsx3 doesn't provide gender info
            })
        
        return voices
    
    def set_voice(self, voice_name: str) -> bool:
        """
        Change the current voice.
        
        Args:
            voice_name: Name of the voice to use
            
        Returns:
            True if voice was set successfully, False otherwise
        """
        if not self.is_initialized():
            return False
        
        try:
            with self._lock:
                self._set_voice(voice_name)
                self.voice_name = voice_name
            return True
        except Exception as e:
            logger.error(f"Failed to set voice to {voice_name}: {e}")
            return False
    
    def set_rate(self, rate: int) -> None:
        """
        Set the speech rate.
        
        Args:
            rate: Speech rate (words per minute)
        """
        if self.is_initialized():
            with self._lock:
                self.engine.setProperty('rate', rate)
                self.rate = rate
            logger.debug(f"Speech rate set to: {rate}")
    
    def set_volume(self, volume: float) -> None:
        """
        Set the speech volume.
        
        Args:
            volume: Volume level (0.0 to 1.0)
        """
        if self.is_initialized():
            volume = max(0.0, min(1.0, volume))  # Clamp to valid range
            with self._lock:
                self.engine.setProperty('volume', volume)
                self.volume = volume
            logger.debug(f"Speech volume set to: {volume}")
    
    def cleanup(self) -> None:
        """
        Clean up TTS resources properly to avoid pyttsx3 warnings.
        """
        if self.engine is not None:
            try:
                with self._lock:
                    # Stop any current speech
                    self.engine.stop()

                    # Properly cleanup pyttsx3 engine
                    try:
                        # Try to access the driver and cleanup properly
                        if hasattr(self.engine, '_driver') and self.engine._driver:
                            if hasattr(self.engine._driver, 'destroy'):
                                self.engine._driver.destroy()
                    except Exception:
                        pass  # Ignore driver cleanup errors

                    # Delete the engine reference
                    del self.engine
                    self.engine = None

            except Exception as e:
                logger.warning(f"Error during Apple TTS cleanup: {e}")

            self._is_initialized = False
            logger.info("Apple TTS resources cleaned up")
