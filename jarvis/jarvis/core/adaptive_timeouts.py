"""
Adaptive Timeout System for Jarvis Voice Assistant.

Provides intelligent timeout management based on user behavior patterns
and conversation context.
"""

import logging
import time
from typing import Dict, Optional, List
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class ConversationContext(Enum):
    """Types of conversation contexts that affect timeout behavior."""
    SIMPLE_QUERY = "simple_query"
    COMPLEX_QUERY = "complex_query"
    FOLLOW_UP = "follow_up"
    FIRST_INTERACTION = "first_interaction"
    REPEATED_FAILURE = "repeated_failure"


@dataclass
class UserSpeechPattern:
    """User's speech pattern data."""
    user_id: str
    average_speech_duration: float = 3.0
    average_pause_duration: float = 1.5
    speech_speed_factor: float = 1.0  # 1.0 = normal, >1.0 = fast, <1.0 = slow
    interaction_count: int = 0
    last_updated: float = field(default_factory=time.time)
    
    def update_pattern(self, speech_duration: float, pause_duration: float):
        """Update speech pattern with new data."""
        # Weighted average to adapt gradually
        weight = 0.2  # How much new data influences the pattern
        
        self.average_speech_duration = (
            (1 - weight) * self.average_speech_duration + 
            weight * speech_duration
        )
        
        self.average_pause_duration = (
            (1 - weight) * self.average_pause_duration + 
            weight * pause_duration
        )
        
        # Update speech speed factor based on duration vs expected
        expected_duration = 3.0  # Baseline expectation
        self.speech_speed_factor = expected_duration / max(self.average_speech_duration, 0.5)
        
        self.interaction_count += 1
        self.last_updated = time.time()


class AdaptiveTimeoutManager:
    """
    Manages adaptive timeouts based on user patterns and context.
    
    Learns from user behavior to provide optimal timeout values for
    different conversation scenarios.
    """
    
    def __init__(self):
        """Initialize the adaptive timeout manager."""
        self.user_patterns: Dict[str, UserSpeechPattern] = {}
        self.default_user_id = "default"
        
        # Base timeout values (in seconds)
        self.base_timeouts = {
            "wake_word": 2.0,
            "command_listening": 5.0,
            "phrase_timeout": 1.5,
            "conversation_timeout": 30.0
        }
        
        # Context multipliers
        self.context_multipliers = {
            ConversationContext.SIMPLE_QUERY: 1.0,
            ConversationContext.COMPLEX_QUERY: 1.5,
            ConversationContext.FOLLOW_UP: 0.8,
            ConversationContext.FIRST_INTERACTION: 1.3,
            ConversationContext.REPEATED_FAILURE: 2.0
        }
        
        # Environment factors
        self.noise_level_factor = 1.0  # Adjusted based on background noise
        self.time_of_day_factor = 1.0  # Adjusted based on time of day
    
    def get_user_pattern(self, user_id: Optional[str] = None) -> UserSpeechPattern:
        """Get or create user speech pattern."""
        user_id = user_id or self.default_user_id
        
        if user_id not in self.user_patterns:
            self.user_patterns[user_id] = UserSpeechPattern(user_id=user_id)
        
        return self.user_patterns[user_id]
    
    def get_adaptive_timeout(
        self, 
        timeout_type: str, 
        context: ConversationContext = ConversationContext.SIMPLE_QUERY,
        user_id: Optional[str] = None
    ) -> float:
        """
        Get adaptive timeout value.
        
        Args:
            timeout_type: Type of timeout ('wake_word', 'command_listening', etc.)
            context: Conversation context
            user_id: User identifier for personalization
            
        Returns:
            Adaptive timeout value in seconds
        """
        if timeout_type not in self.base_timeouts:
            logger.warning(f"Unknown timeout type: {timeout_type}")
            return 5.0  # Default fallback
        
        base_timeout = self.base_timeouts[timeout_type]
        user_pattern = self.get_user_pattern(user_id)
        
        # Apply user speech speed factor
        user_factor = 1.0 / max(user_pattern.speech_speed_factor, 0.3)  # Prevent extreme values
        
        # Apply context multiplier
        context_factor = self.context_multipliers.get(context, 1.0)
        
        # Apply environment factors
        environment_factor = self.noise_level_factor * self.time_of_day_factor
        
        # Calculate adaptive timeout
        adaptive_timeout = base_timeout * user_factor * context_factor * environment_factor
        
        # Apply reasonable bounds
        min_timeout = base_timeout * 0.5
        max_timeout = base_timeout * 3.0
        adaptive_timeout = max(min_timeout, min(adaptive_timeout, max_timeout))
        
        logger.debug(
            f"Adaptive timeout for {timeout_type}: {adaptive_timeout:.2f}s "
            f"(base: {base_timeout}, user: {user_factor:.2f}, "
            f"context: {context_factor:.2f}, env: {environment_factor:.2f})"
        )
        
        return adaptive_timeout
    
    def update_user_pattern(
        self, 
        speech_duration: float, 
        pause_duration: float,
        user_id: Optional[str] = None
    ):
        """
        Update user speech pattern with new interaction data.
        
        Args:
            speech_duration: Duration of user's speech in seconds
            pause_duration: Duration of pause before speech in seconds
            user_id: User identifier
        """
        user_pattern = self.get_user_pattern(user_id)
        user_pattern.update_pattern(speech_duration, pause_duration)
        
        logger.debug(
            f"Updated user pattern for {user_pattern.user_id}: "
            f"avg_speech={user_pattern.average_speech_duration:.2f}s, "
            f"avg_pause={user_pattern.average_pause_duration:.2f}s, "
            f"speed_factor={user_pattern.speech_speed_factor:.2f}"
        )
    
    def set_environment_factors(self, noise_level: float = 1.0, time_factor: float = 1.0):
        """
        Set environment factors that affect timeouts.
        
        Args:
            noise_level: Noise level factor (1.0 = normal, >1.0 = noisy)
            time_factor: Time of day factor (1.0 = normal, >1.0 = tired/slow)
        """
        self.noise_level_factor = max(0.5, min(noise_level, 2.0))
        self.time_of_day_factor = max(0.5, min(time_factor, 2.0))
        
        logger.debug(f"Environment factors updated: noise={self.noise_level_factor:.2f}, time={self.time_of_day_factor:.2f}")
    
    def get_conversation_context(
        self, 
        command: str, 
        is_follow_up: bool = False,
        retry_count: int = 0
    ) -> ConversationContext:
        """
        Determine conversation context from command.
        
        Args:
            command: User command text
            is_follow_up: Whether this is a follow-up to previous command
            retry_count: Number of retries for this interaction
            
        Returns:
            Appropriate conversation context
        """
        if retry_count > 0:
            return ConversationContext.REPEATED_FAILURE
        
        if is_follow_up:
            return ConversationContext.FOLLOW_UP
        
        # Check for complex query indicators
        complex_indicators = [
            "explain", "describe", "tell me about", "how does", "why does",
            "what happens when", "compare", "difference between", "analyze"
        ]
        
        if any(indicator in command.lower() for indicator in complex_indicators):
            return ConversationContext.COMPLEX_QUERY
        
        # Check for simple query indicators
        simple_indicators = [
            "what time", "what's the time", "current time", "time is it",
            "play", "show", "open", "close", "start", "stop"
        ]
        
        if any(indicator in command.lower() for indicator in simple_indicators):
            return ConversationContext.SIMPLE_QUERY
        
        # Default to simple query
        return ConversationContext.SIMPLE_QUERY
    
    def get_timeout_recommendations(self, user_id: Optional[str] = None) -> Dict[str, float]:
        """
        Get all timeout recommendations for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            Dictionary of timeout recommendations
        """
        recommendations = {}
        
        for timeout_type in self.base_timeouts.keys():
            recommendations[timeout_type] = self.get_adaptive_timeout(
                timeout_type, 
                ConversationContext.SIMPLE_QUERY, 
                user_id
            )
        
        return recommendations
    
    def reset_user_pattern(self, user_id: Optional[str] = None):
        """Reset user pattern to defaults."""
        user_id = user_id or self.default_user_id
        if user_id in self.user_patterns:
            del self.user_patterns[user_id]
        logger.info(f"Reset user pattern for {user_id}")


# Global instance for easy access
adaptive_timeout_manager = AdaptiveTimeoutManager()
