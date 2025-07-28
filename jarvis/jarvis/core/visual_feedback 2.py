"""
Visual Feedback System for Jarvis Voice Assistant.

Provides real-time visual indicators for system status and user interaction.
"""

import logging
import sys
import time
from typing import Dict, Optional
from enum import Enum
from threading import Lock

logger = logging.getLogger(__name__)


class FeedbackStatus(Enum):
    """Visual feedback status types."""
    IDLE = "idle"
    LISTENING_WAKE_WORD = "listening_wake_word"
    WAKE_WORD_DETECTED = "wake_word_detected"
    LISTENING_COMMAND = "listening_command"
    PROCESSING = "processing"
    SPEAKING = "speaking"
    ERROR = "error"
    THINKING = "thinking"


class VisualFeedbackManager:
    """
    Manages visual feedback for the Jarvis voice assistant.
    
    Provides real-time status indicators and user interaction feedback
    without cluttering the console output.
    """
    
    def __init__(self, enable_colors: bool = True, enable_animations: bool = True):
        """
        Initialize the visual feedback manager.
        
        Args:
            enable_colors: Whether to use colored output
            enable_animations: Whether to show animated indicators
        """
        self.enable_colors = enable_colors
        self.enable_animations = enable_animations
        self._current_status = FeedbackStatus.IDLE
        self._lock = Lock()
        self._animation_frame = 0
        
        # Status indicators with colors and animations
        self.status_indicators = {
            FeedbackStatus.IDLE: {
                "icon": "💤",
                "text": "Idle",
                "color": "\033[90m",  # Gray
                "animation": ["💤", "😴"]
            },
            FeedbackStatus.LISTENING_WAKE_WORD: {
                "icon": "👂",
                "text": "Listening for wake word",
                "color": "\033[94m",  # Blue
                "animation": ["👂", "🎧", "👂", "🔊"]
            },
            FeedbackStatus.WAKE_WORD_DETECTED: {
                "icon": "✨",
                "text": "Wake word detected!",
                "color": "\033[92m",  # Green
                "animation": ["✨", "⭐", "🌟", "✨"]
            },
            FeedbackStatus.LISTENING_COMMAND: {
                "icon": "🎤",
                "text": "Listening for command",
                "color": "\033[93m",  # Yellow
                "animation": ["🎤", "🎙️", "🎤", "📢"]
            },
            FeedbackStatus.PROCESSING: {
                "icon": "🧠",
                "text": "Processing",
                "color": "\033[95m",  # Magenta
                "animation": ["🧠", "💭", "🤔", "💡"]
            },
            FeedbackStatus.THINKING: {
                "icon": "🤔",
                "text": "Thinking",
                "color": "\033[96m",  # Cyan
                "animation": ["🤔", "💭", "🧠", "💡"]
            },
            FeedbackStatus.SPEAKING: {
                "icon": "🗣️",
                "text": "Speaking",
                "color": "\033[91m",  # Red
                "animation": ["🗣️", "💬", "🗨️", "💭"]
            },
            FeedbackStatus.ERROR: {
                "icon": "❌",
                "text": "Error occurred",
                "color": "\033[91m",  # Red
                "animation": ["❌", "⚠️", "🚫", "❗"]
            }
        }
        
        # Color codes
        self.colors = {
            "reset": "\033[0m",
            "bold": "\033[1m",
            "dim": "\033[2m"
        }
    
    def show_status(self, status: FeedbackStatus, message: Optional[str] = None) -> None:
        """
        Show a status indicator.
        
        Args:
            status: The status to display
            message: Optional custom message
        """
        with self._lock:
            self._current_status = status
            indicator = self.status_indicators[status]
            
            # Get animated icon if animations are enabled
            if self.enable_animations:
                icon = indicator["animation"][self._animation_frame % len(indicator["animation"])]
                self._animation_frame += 1
            else:
                icon = indicator["icon"]
            
            # Build status line
            text = message or indicator["text"]
            
            if self.enable_colors:
                color = indicator["color"]
                reset = self.colors["reset"]
                status_line = f"\r{color}{icon} {text}{reset}"
            else:
                status_line = f"\r{icon} {text}"
            
            # Print without newline and flush immediately
            print(status_line, end="", flush=True)
    
    def show_progress(self, status: FeedbackStatus, progress: float, message: Optional[str] = None) -> None:
        """
        Show a status with progress bar.
        
        Args:
            status: The status to display
            progress: Progress value between 0.0 and 1.0
            message: Optional custom message
        """
        with self._lock:
            indicator = self.status_indicators[status]
            icon = indicator["icon"]
            text = message or indicator["text"]
            
            # Create progress bar
            bar_length = 20
            filled_length = int(bar_length * progress)
            bar = "█" * filled_length + "░" * (bar_length - filled_length)
            
            if self.enable_colors:
                color = indicator["color"]
                reset = self.colors["reset"]
                status_line = f"\r{color}{icon} {text} [{bar}] {progress:.0%}{reset}"
            else:
                status_line = f"\r{icon} {text} [{bar}] {progress:.0%}"
            
            print(status_line, end="", flush=True)
    
    def show_confidence(self, status: FeedbackStatus, confidence: float, message: Optional[str] = None) -> None:
        """
        Show a status with confidence indicator.
        
        Args:
            status: The status to display
            confidence: Confidence value between 0.0 and 1.0
            message: Optional custom message
        """
        with self._lock:
            indicator = self.status_indicators[status]
            icon = indicator["icon"]
            text = message or indicator["text"]
            
            # Confidence indicator
            if confidence >= 0.8:
                conf_icon = "🟢"
            elif confidence >= 0.6:
                conf_icon = "🟡"
            else:
                conf_icon = "🔴"
            
            if self.enable_colors:
                color = indicator["color"]
                reset = self.colors["reset"]
                status_line = f"\r{color}{icon} {text} {conf_icon} {confidence:.0%}{reset}"
            else:
                status_line = f"\r{icon} {text} {conf_icon} {confidence:.0%}"
            
            print(status_line, end="", flush=True)
    
    def clear_status(self) -> None:
        """Clear the current status line."""
        with self._lock:
            print("\r" + " " * 80 + "\r", end="", flush=True)
    
    def newline(self) -> None:
        """Print a newline to move to the next line."""
        print()
    
    def show_message(self, message: str, status: Optional[FeedbackStatus] = None) -> None:
        """
        Show a message with optional status.
        
        Args:
            message: Message to display
            status: Optional status for styling
        """
        with self._lock:
            if status and self.enable_colors:
                color = self.status_indicators[status]["color"]
                reset = self.colors["reset"]
                print(f"{color}{message}{reset}")
            else:
                print(message)
    
    def get_current_status(self) -> FeedbackStatus:
        """Get the current status."""
        return self._current_status


# Global instance for easy access
feedback_manager = VisualFeedbackManager()
