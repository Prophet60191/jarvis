"""
Wake word detection for Jarvis Voice Assistant.

This module handles wake word detection with configurable sensitivity,
false positive reduction, and multiple detection strategies.
"""

import logging
import time
from typing import Optional, List, Dict, Any, Callable
from dataclasses import dataclass
from threading import Event, Thread

from ..config import ConversationConfig
from ..exceptions import WakeWordError, AudioError
from .speech import SpeechManager


logger = logging.getLogger(__name__)


@dataclass
class WakeWordDetection:
    """Data class for wake word detection results."""
    detected: bool
    confidence: float
    text: str
    timestamp: float
    detection_method: str


class WakeWordDetector:
    """
    Handles wake word detection for the Jarvis voice assistant.
    
    This class provides configurable wake word detection with multiple
    strategies and false positive reduction.
    """
    
    def __init__(self, config: ConversationConfig, speech_manager: SpeechManager):
        """
        Initialize the wake word detector.
        
        Args:
            config: Conversation configuration settings
            speech_manager: Speech management instance
        """
        self.config = config
        self.speech_manager = speech_manager
        
        # Detection settings
        self.wake_words = [config.wake_word.lower()]
        self.sensitivity = 0.8  # Confidence threshold (0-1)
        self.min_confidence = 0.6
        
        # State management
        self.is_listening = False
        self.detection_thread: Optional[Thread] = None
        self.stop_event = Event()
        
        # Callbacks
        self.detection_callback: Optional[Callable[[WakeWordDetection], None]] = None
        
        # Statistics
        self.detection_stats = {
            "total_detections": 0,
            "false_positives": 0,
            "true_positives": 0,
            "last_detection_time": None
        }
        
        logger.info(f"WakeWordDetector initialized with wake words: {self.wake_words}")
    
    def add_wake_word(self, wake_word: str) -> None:
        """
        Add an additional wake word.
        
        Args:
            wake_word: Wake word to add
        """
        wake_word_lower = wake_word.lower().strip()
        if wake_word_lower not in self.wake_words:
            self.wake_words.append(wake_word_lower)
            logger.info(f"Added wake word: '{wake_word}'")
    
    def remove_wake_word(self, wake_word: str) -> bool:
        """
        Remove a wake word.
        
        Args:
            wake_word: Wake word to remove
            
        Returns:
            True if wake word was removed, False if not found
        """
        wake_word_lower = wake_word.lower().strip()
        if wake_word_lower in self.wake_words:
            self.wake_words.remove(wake_word_lower)
            logger.info(f"Removed wake word: '{wake_word}'")
            return True
        return False
    
    def set_sensitivity(self, sensitivity: float) -> None:
        """
        Set wake word detection sensitivity.
        
        Args:
            sensitivity: Sensitivity level (0.0 to 1.0)
                        Higher values = more sensitive but more false positives
        """
        if not 0.0 <= sensitivity <= 1.0:
            raise ValueError("Sensitivity must be between 0.0 and 1.0")
        
        self.sensitivity = sensitivity
        logger.info(f"Wake word sensitivity set to: {sensitivity}")
    
    def set_detection_callback(self, callback: Callable[[WakeWordDetection], None]) -> None:
        """
        Set callback function for wake word detections.
        
        Args:
            callback: Function to call when wake word is detected
        """
        self.detection_callback = callback
        logger.debug("Wake word detection callback set")
    
    def detect_in_text(self, text: str) -> WakeWordDetection:
        """
        Detect wake word in given text.
        
        Args:
            text: Text to analyze for wake words
            
        Returns:
            WakeWordDetection result
        """
        if not text:
            return WakeWordDetection(
                detected=False,
                confidence=0.0,
                text="",
                timestamp=time.time(),
                detection_method="text_analysis"
            )
        
        text_lower = text.lower().strip()
        best_match = None
        best_confidence = 0.0
        
        for wake_word in self.wake_words:
            confidence = self._calculate_text_confidence(wake_word, text_lower)
            
            if confidence > best_confidence:
                best_confidence = confidence
                best_match = wake_word
        
        detected = best_confidence >= self.sensitivity
        
        if detected:
            logger.debug(f"Wake word detected: '{best_match}' in '{text}' (confidence: {best_confidence:.2f})")
            self.detection_stats["total_detections"] += 1
            self.detection_stats["last_detection_time"] = time.time()
        
        return WakeWordDetection(
            detected=detected,
            confidence=best_confidence,
            text=text,
            timestamp=time.time(),
            detection_method="text_analysis"
        )
    
    def _calculate_text_confidence(self, wake_word: str, text: str) -> float:
        """
        Calculate confidence score for wake word detection in text.
        
        Args:
            wake_word: Wake word to search for
            text: Text to search in
            
        Returns:
            Confidence score (0.0 to 1.0)
        """
        # Exact match
        if wake_word in text:
            # Check if it's a word boundary match
            words = text.split()
            if wake_word in words:
                return 1.0
            else:
                # Partial match within a word
                return 0.8
        
        # Fuzzy matching for similar sounding words
        # This is a simple implementation - could be enhanced with phonetic matching
        wake_word_parts = wake_word.split()
        text_words = text.split()
        
        matches = 0
        for wake_part in wake_word_parts:
            for text_word in text_words:
                if self._words_similar(wake_part, text_word):
                    matches += 1
                    break
        
        if matches > 0:
            return min(0.7, matches / len(wake_word_parts))
        
        return 0.0
    
    def _words_similar(self, word1: str, word2: str, threshold: float = 0.7) -> bool:
        """
        Check if two words are similar using simple string similarity.
        
        Args:
            word1: First word
            word2: Second word
            threshold: Similarity threshold
            
        Returns:
            True if words are similar enough
        """
        if not word1 or not word2:
            return False
        
        # Simple Levenshtein-like similarity
        max_len = max(len(word1), len(word2))
        if max_len == 0:
            return True
        
        # Count matching characters
        matches = sum(1 for a, b in zip(word1, word2) if a == b)
        similarity = matches / max_len
        
        return similarity >= threshold
    
    def listen_once(self, timeout: Optional[float] = None) -> WakeWordDetection:
        """
        Listen for wake word once.

        Args:
            timeout: Maximum time to listen (uses default if None)

        Returns:
            WakeWordDetection result

        Raises:
            WakeWordError: If listening fails
        """
        try:
            # Listen for speech
            text = self.speech_manager.listen_for_speech(
                timeout=timeout or 2.0,
                phrase_time_limit=4.0,
                enhance_audio=True
            )

            if text:
                return self.detect_in_text(text)
            else:
                return WakeWordDetection(
                    detected=False,
                    confidence=0.0,
                    text="",
                    timestamp=time.time(),
                    detection_method="speech_recognition"
                )

        except Exception as e:
            # Don't raise exception for common audio issues, just return no detection
            logger.debug(f"Wake word listening failed (this is normal): {str(e)}")
            return WakeWordDetection(
                detected=False,
                confidence=0.0,
                text="",
                timestamp=time.time(),
                detection_method="speech_recognition_failed"
            )
    
    def start_continuous_listening(self) -> None:
        """
        Start continuous wake word detection in background thread.
        
        Raises:
            WakeWordError: If continuous listening fails to start
        """
        if self.is_listening:
            logger.warning("Wake word detection already running")
            return
        
        try:
            logger.info("Starting continuous wake word detection")
            self.is_listening = True
            self.stop_event.clear()
            
            self.detection_thread = Thread(
                target=self._continuous_detection_loop,
                daemon=True,
                name="WakeWordDetection"
            )
            self.detection_thread.start()
            
        except Exception as e:
            error_msg = f"Failed to start continuous wake word detection: {str(e)}"
            logger.error(error_msg)
            self.is_listening = False
            raise WakeWordError(error_msg) from e
    
    def stop_continuous_listening(self) -> None:
        """Stop continuous wake word detection."""
        if not self.is_listening:
            return
        
        logger.info("Stopping continuous wake word detection")
        self.is_listening = False
        self.stop_event.set()
        
        if self.detection_thread and self.detection_thread.is_alive():
            self.detection_thread.join(timeout=2.0)
            if self.detection_thread.is_alive():
                logger.warning("Wake word detection thread did not stop gracefully")
        
        self.detection_thread = None
    
    def _continuous_detection_loop(self) -> None:
        """Main loop for continuous wake word detection."""
        logger.debug("Wake word detection loop started")
        
        while self.is_listening and not self.stop_event.is_set():
            try:
                # Listen for wake word
                detection = self.listen_once(timeout=1.0)
                
                if detection.detected:
                    logger.info(f"Wake word detected: {detection}")
                    
                    # Call callback if set
                    if self.detection_callback:
                        try:
                            self.detection_callback(detection)
                        except Exception as e:
                            logger.error(f"Error in wake word callback: {str(e)}")
                
                # Small delay to prevent excessive CPU usage
                time.sleep(0.1)
                
            except AudioError:
                # Audio timeout or similar - continue listening
                continue
            except Exception as e:
                logger.error(f"Error in wake word detection loop: {str(e)}")
                time.sleep(1.0)  # Longer delay on error
        
        logger.debug("Wake word detection loop ended")
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get wake word detection statistics.
        
        Returns:
            Dictionary containing detection statistics
        """
        return {
            "wake_words": self.wake_words,
            "sensitivity": self.sensitivity,
            "min_confidence": self.min_confidence,
            "is_listening": self.is_listening,
            "stats": self.detection_stats.copy()
        }
    
    def reset_statistics(self) -> None:
        """Reset detection statistics."""
        self.detection_stats = {
            "total_detections": 0,
            "false_positives": 0,
            "true_positives": 0,
            "last_detection_time": None
        }
        logger.info("Wake word detection statistics reset")
    
    def test_detection(self, test_phrases: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Test wake word detection with sample phrases.
        
        Args:
            test_phrases: List of phrases to test (uses defaults if None)
            
        Returns:
            Dictionary containing test results
        """
        if test_phrases is None:
            test_phrases = [
                f"Hey {self.config.wake_word}",
                f"{self.config.wake_word} are you there",
                f"Hello {self.config.wake_word}",
                "This should not trigger",
                "Random speech without wake word"
            ]
        
        results = []
        for phrase in test_phrases:
            detection = self.detect_in_text(phrase)
            results.append({
                "phrase": phrase,
                "detected": detection.detected,
                "confidence": detection.confidence
            })
        
        logger.info(f"Wake word detection test completed: {len(results)} phrases tested")
        return {
            "test_phrases": len(test_phrases),
            "results": results,
            "wake_words": self.wake_words,
            "sensitivity": self.sensitivity
        }
    
    def cleanup(self) -> None:
        """Clean up wake word detector resources."""
        logger.info("Cleaning up wake word detector")
        self.stop_continuous_listening()
        self.detection_callback = None
