"""
Interruption Handling System for Jarvis Voice Assistant.

Provides intelligent interruption detection and handling during speech output.
"""

import logging
import threading
import time
from typing import Optional, Callable
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class InterruptionType(Enum):
    """Types of interruptions."""
    VOICE_DETECTED = "voice_detected"
    WAKE_WORD_DETECTED = "wake_word_detected"
    MANUAL_STOP = "manual_stop"
    TIMEOUT = "timeout"


@dataclass
class InterruptionEvent:
    """Interruption event data."""
    type: InterruptionType
    timestamp: float
    confidence: float = 1.0
    data: Optional[dict] = None


class InterruptionManager:
    """
    Manages interruption detection and handling during speech output.
    
    Allows users to interrupt Jarvis while it's speaking by detecting
    voice activity or wake words.
    """
    
    def __init__(self):
        """Initialize the interruption manager."""
        self.is_speaking = False
        self.interruption_enabled = True
        self.interruption_callback: Optional[Callable] = None
        
        # Interruption thresholds
        self.voice_threshold = 0.3  # Minimum voice activity level
        self.wake_word_threshold = 0.7  # Minimum wake word confidence
        self.interruption_delay = 0.5  # Seconds of voice activity before interrupting
        
        # State tracking
        self._monitoring_thread: Optional[threading.Thread] = None
        self._stop_monitoring = threading.Event()
        self._voice_start_time: Optional[float] = None
        self._last_interruption_time = 0.0
        self._interruption_cooldown = 1.0  # Prevent rapid interruptions
        
        # Audio monitoring (placeholder for actual audio input)
        self._audio_level = 0.0
        self._wake_word_detected = False
    
    def start_speaking(self, interruption_callback: Optional[Callable] = None):
        """
        Start speaking mode with interruption monitoring.
        
        Args:
            interruption_callback: Function to call when interruption is detected
        """
        if self.is_speaking:
            logger.warning("Already in speaking mode")
            return
        
        self.is_speaking = True
        self.interruption_callback = interruption_callback
        self._stop_monitoring.clear()
        
        if self.interruption_enabled:
            self._start_monitoring()
        
        logger.debug("Started speaking mode with interruption monitoring")
    
    def stop_speaking(self):
        """Stop speaking mode and interruption monitoring."""
        if not self.is_speaking:
            return
        
        self.is_speaking = False
        self.interruption_callback = None
        self._stop_monitoring.set()
        
        # Wait for monitoring thread to finish
        if self._monitoring_thread and self._monitoring_thread.is_alive():
            self._monitoring_thread.join(timeout=1.0)
        
        logger.debug("Stopped speaking mode")
    
    def _start_monitoring(self):
        """Start the interruption monitoring thread."""
        self._monitoring_thread = threading.Thread(
            target=self._monitor_interruptions,
            daemon=True
        )
        self._monitoring_thread.start()
    
    def _monitor_interruptions(self):
        """Monitor for interruptions while speaking."""
        logger.debug("Started interruption monitoring")
        
        while not self._stop_monitoring.is_set() and self.is_speaking:
            try:
                # Check for voice activity
                if self._check_voice_interruption():
                    self._handle_interruption(InterruptionType.VOICE_DETECTED)
                    break
                
                # Check for wake word
                if self._check_wake_word_interruption():
                    self._handle_interruption(InterruptionType.WAKE_WORD_DETECTED)
                    break
                
                # Small delay to prevent excessive CPU usage
                time.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Error in interruption monitoring: {e}")
                break
        
        logger.debug("Stopped interruption monitoring")
    
    def _check_voice_interruption(self) -> bool:
        """
        Check if voice activity indicates an interruption.
        
        Returns:
            True if voice interruption detected
        """
        current_time = time.time()
        
        # Simulate voice activity detection (replace with actual audio input)
        voice_detected = self._audio_level > self.voice_threshold
        
        if voice_detected:
            if self._voice_start_time is None:
                self._voice_start_time = current_time
            
            # Check if voice has been active long enough
            voice_duration = current_time - self._voice_start_time
            if voice_duration >= self.interruption_delay:
                # Check cooldown period
                if current_time - self._last_interruption_time > self._interruption_cooldown:
                    return True
        else:
            # Reset voice start time when no voice detected
            self._voice_start_time = None
        
        return False
    
    def _check_wake_word_interruption(self) -> bool:
        """
        Check if wake word was detected during speaking.
        
        Returns:
            True if wake word interruption detected
        """
        # Simulate wake word detection (replace with actual wake word detector)
        if self._wake_word_detected:
            current_time = time.time()
            if current_time - self._last_interruption_time > self._interruption_cooldown:
                self._wake_word_detected = False  # Reset flag
                return True
        
        return False
    
    def _handle_interruption(self, interruption_type: InterruptionType):
        """
        Handle detected interruption.
        
        Args:
            interruption_type: Type of interruption detected
        """
        current_time = time.time()
        self._last_interruption_time = current_time
        
        interruption_event = InterruptionEvent(
            type=interruption_type,
            timestamp=current_time,
            confidence=0.8,  # Placeholder confidence
            data={"audio_level": self._audio_level}
        )
        
        logger.info(f"Interruption detected: {interruption_type.value}")
        
        # Call the interruption callback if provided
        if self.interruption_callback:
            try:
                self.interruption_callback(interruption_event)
            except Exception as e:
                logger.error(f"Error in interruption callback: {e}")
        
        # Stop speaking
        self.stop_speaking()
    
    def manual_interrupt(self):
        """Manually trigger an interruption."""
        if self.is_speaking:
            self._handle_interruption(InterruptionType.MANUAL_STOP)
    
    def set_voice_threshold(self, threshold: float):
        """
        Set the voice activity threshold for interruption detection.
        
        Args:
            threshold: Voice activity threshold (0.0 to 1.0)
        """
        self.voice_threshold = max(0.0, min(threshold, 1.0))
        logger.debug(f"Voice threshold set to {self.voice_threshold}")
    
    def set_interruption_delay(self, delay: float):
        """
        Set the delay before voice activity triggers interruption.
        
        Args:
            delay: Delay in seconds
        """
        self.interruption_delay = max(0.1, delay)
        logger.debug(f"Interruption delay set to {self.interruption_delay}s")
    
    def enable_interruption(self, enabled: bool = True):
        """
        Enable or disable interruption detection.
        
        Args:
            enabled: Whether to enable interruption detection
        """
        self.interruption_enabled = enabled
        logger.debug(f"Interruption detection {'enabled' if enabled else 'disabled'}")
    
    def update_audio_level(self, level: float):
        """
        Update current audio level for voice activity detection.
        
        Args:
            level: Audio level (0.0 to 1.0)
        """
        self._audio_level = max(0.0, min(level, 1.0))
    
    def trigger_wake_word_detection(self):
        """Trigger wake word detection (for testing/simulation)."""
        self._wake_word_detected = True
    
    def get_status(self) -> dict:
        """
        Get current interruption manager status.
        
        Returns:
            Status dictionary
        """
        return {
            "is_speaking": self.is_speaking,
            "interruption_enabled": self.interruption_enabled,
            "voice_threshold": self.voice_threshold,
            "interruption_delay": self.interruption_delay,
            "current_audio_level": self._audio_level,
            "monitoring_active": (
                self._monitoring_thread is not None and 
                self._monitoring_thread.is_alive()
            )
        }


# Context manager for easy use
class SpeakingContext:
    """Context manager for speaking with interruption handling."""
    
    def __init__(self, interruption_manager: InterruptionManager, 
                 interruption_callback: Optional[Callable] = None):
        self.interruption_manager = interruption_manager
        self.interruption_callback = interruption_callback
    
    def __enter__(self):
        self.interruption_manager.start_speaking(self.interruption_callback)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.interruption_manager.stop_speaking()


# Global instance for easy access
interruption_manager = InterruptionManager()
