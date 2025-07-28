"""
Confidence Scoring System for Jarvis Voice Assistant.

Provides confidence scoring for speech recognition and response generation.
"""

import logging
import re
from typing import Dict, Optional, Tuple, List
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class ConfidenceLevel(Enum):
    """Confidence level categories."""
    HIGH = "high"        # >= 0.8
    MEDIUM = "medium"    # >= 0.6
    LOW = "low"          # >= 0.4
    VERY_LOW = "very_low"  # < 0.4


@dataclass
class ConfidenceResult:
    """Result of confidence analysis."""
    text: str
    confidence: float
    level: ConfidenceLevel
    factors: Dict[str, float]
    suggestions: List[str]


class ConfidenceManager:
    """
    Manages confidence scoring for speech recognition and responses.
    
    Analyzes various factors to determine confidence in recognition accuracy
    and provides appropriate handling for low-confidence scenarios.
    """
    
    def __init__(self):
        """Initialize the confidence manager."""
        self.confidence_threshold = 0.6
        self.high_confidence_threshold = 0.8
        self.very_low_threshold = 0.4
        
        # Common words that indicate uncertainty
        self.uncertainty_words = {
            "um", "uh", "er", "ah", "hmm", "well", "like", "you know",
            "i think", "maybe", "perhaps", "possibly", "probably"
        }
        
        # Words that indicate clear intent
        self.clarity_words = {
            "please", "can you", "i want", "i need", "show me", "tell me",
            "what is", "how do", "when is", "where is", "why is"
        }
        
        # Common command patterns
        self.command_patterns = [
            r"what.*time",
            r"tell me.*about",
            r"show me",
            r"play.*video",
            r"set.*timer",
            r"remind me",
            r"search for",
            r"open.*app"
        ]
    
    def analyze_confidence(self, text: str, whisper_confidence: Optional[float] = None) -> ConfidenceResult:
        """
        Analyze confidence in recognized text.
        
        Args:
            text: The recognized text
            whisper_confidence: Optional confidence from Whisper model
            
        Returns:
            ConfidenceResult with analysis
        """
        if not text or not text.strip():
            return ConfidenceResult(
                text="",
                confidence=0.0,
                level=ConfidenceLevel.VERY_LOW,
                factors={"empty_text": 0.0},
                suggestions=["Please speak clearly and try again"]
            )
        
        factors = {}
        
        # Factor 1: Whisper model confidence (if available)
        if whisper_confidence is not None:
            factors["whisper_model"] = whisper_confidence
        
        # Factor 2: Text length and completeness
        factors["text_length"] = self._analyze_text_length(text)
        
        # Factor 3: Word clarity and uncertainty
        factors["word_clarity"] = self._analyze_word_clarity(text)
        
        # Factor 4: Command pattern recognition
        factors["command_pattern"] = self._analyze_command_patterns(text)
        
        # Factor 5: Grammar and structure
        factors["grammar_structure"] = self._analyze_grammar(text)
        
        # Factor 6: Repetition and stuttering
        factors["repetition"] = self._analyze_repetition(text)
        
        # Calculate overall confidence
        overall_confidence = self._calculate_overall_confidence(factors)
        
        # Determine confidence level
        level = self._get_confidence_level(overall_confidence)
        
        # Generate suggestions for low confidence
        suggestions = self._generate_suggestions(factors, level)
        
        return ConfidenceResult(
            text=text,
            confidence=overall_confidence,
            level=level,
            factors=factors,
            suggestions=suggestions
        )
    
    def _analyze_text_length(self, text: str) -> float:
        """Analyze text length appropriateness."""
        words = text.split()
        word_count = len(words)
        
        if word_count == 0:
            return 0.0
        elif word_count == 1:
            return 0.3  # Single words are often incomplete
        elif 2 <= word_count <= 20:
            return 0.9  # Good length for commands
        elif 21 <= word_count <= 50:
            return 0.7  # Longer but still reasonable
        else:
            return 0.4  # Very long, possibly garbled
    
    def _analyze_word_clarity(self, text: str) -> float:
        """Analyze word clarity and uncertainty markers."""
        text_lower = text.lower()
        words = text_lower.split()
        
        if not words:
            return 0.0
        
        # Count uncertainty words
        uncertainty_count = sum(1 for word in words if word in self.uncertainty_words)
        uncertainty_ratio = uncertainty_count / len(words)
        
        # Count clarity indicators
        clarity_count = sum(1 for phrase in self.clarity_words if phrase in text_lower)
        clarity_bonus = min(clarity_count * 0.2, 0.4)
        
        # Base score reduced by uncertainty, increased by clarity
        base_score = 0.8
        uncertainty_penalty = uncertainty_ratio * 0.5
        
        return max(0.0, min(1.0, base_score - uncertainty_penalty + clarity_bonus))
    
    def _analyze_command_patterns(self, text: str) -> float:
        """Analyze if text matches common command patterns."""
        text_lower = text.lower()
        
        # Check for command patterns
        pattern_matches = sum(1 for pattern in self.command_patterns 
                            if re.search(pattern, text_lower))
        
        if pattern_matches > 0:
            return 0.9  # High confidence for recognized patterns
        
        # Check for question words
        question_words = ["what", "when", "where", "why", "how", "who"]
        if any(word in text_lower for word in question_words):
            return 0.7
        
        # Check for action words
        action_words = ["play", "show", "tell", "open", "close", "start", "stop"]
        if any(word in text_lower for word in action_words):
            return 0.6
        
        return 0.4  # Lower confidence for unrecognized patterns
    
    def _analyze_grammar(self, text: str) -> float:
        """Analyze basic grammar and sentence structure."""
        # Simple heuristics for grammar analysis
        
        # Check for proper capitalization
        has_capital = any(c.isupper() for c in text)
        
        # Check for reasonable punctuation
        has_punctuation = any(c in text for c in ".!?")
        
        # Check for reasonable word patterns
        words = text.split()
        if not words:
            return 0.0
        
        # Very basic grammar scoring
        score = 0.5  # Base score
        
        if has_capital:
            score += 0.1
        if has_punctuation:
            score += 0.1
        
        # Penalize very short or very fragmented text
        if len(words) < 2:
            score -= 0.2
        
        # Check for repeated characters (often indicates poor recognition)
        repeated_chars = sum(1 for i in range(len(text) - 1) 
                           if text[i] == text[i + 1] and text[i].isalpha())
        if repeated_chars > len(text) * 0.1:  # More than 10% repeated chars
            score -= 0.3
        
        return max(0.0, min(1.0, score))
    
    def _analyze_repetition(self, text: str) -> float:
        """Analyze repetition and stuttering patterns."""
        words = text.lower().split()
        if len(words) < 2:
            return 0.8
        
        # Count repeated words
        repeated_words = 0
        for i in range(len(words) - 1):
            if words[i] == words[i + 1]:
                repeated_words += 1
        
        repetition_ratio = repeated_words / len(words)
        
        # High repetition indicates poor recognition
        if repetition_ratio > 0.3:
            return 0.2
        elif repetition_ratio > 0.1:
            return 0.6
        else:
            return 0.9
    
    def _calculate_overall_confidence(self, factors: Dict[str, float]) -> float:
        """Calculate overall confidence from individual factors."""
        # Weighted average of factors
        weights = {
            "whisper_model": 0.3,
            "text_length": 0.15,
            "word_clarity": 0.25,
            "command_pattern": 0.15,
            "grammar_structure": 0.1,
            "repetition": 0.05
        }
        
        weighted_sum = 0.0
        total_weight = 0.0
        
        for factor, value in factors.items():
            if factor in weights:
                weight = weights[factor]
                weighted_sum += value * weight
                total_weight += weight
        
        if total_weight == 0:
            return 0.0
        
        return weighted_sum / total_weight
    
    def _get_confidence_level(self, confidence: float) -> ConfidenceLevel:
        """Convert confidence score to level."""
        if confidence >= self.high_confidence_threshold:
            return ConfidenceLevel.HIGH
        elif confidence >= self.confidence_threshold:
            return ConfidenceLevel.MEDIUM
        elif confidence >= self.very_low_threshold:
            return ConfidenceLevel.LOW
        else:
            return ConfidenceLevel.VERY_LOW
    
    def _generate_suggestions(self, factors: Dict[str, float], level: ConfidenceLevel) -> List[str]:
        """Generate suggestions for improving recognition."""
        suggestions = []
        
        if level in [ConfidenceLevel.LOW, ConfidenceLevel.VERY_LOW]:
            if factors.get("text_length", 1.0) < 0.5:
                suggestions.append("Try speaking in complete sentences")
            
            if factors.get("word_clarity", 1.0) < 0.5:
                suggestions.append("Speak more clearly and avoid filler words")
            
            if factors.get("command_pattern", 1.0) < 0.5:
                suggestions.append("Try using clear commands like 'What time is it?' or 'Show me...'")
            
            if factors.get("repetition", 1.0) < 0.5:
                suggestions.append("Avoid repeating words")
            
            # General suggestions
            suggestions.extend([
                "Speak closer to the microphone",
                "Reduce background noise",
                "Speak at a normal pace"
            ])
        
        return suggestions[:3]  # Limit to top 3 suggestions
    
    def should_ask_for_clarification(self, confidence_result: ConfidenceResult) -> bool:
        """Determine if we should ask for clarification."""
        return confidence_result.level in [ConfidenceLevel.LOW, ConfidenceLevel.VERY_LOW]
    
    def format_clarification_request(self, confidence_result: ConfidenceResult) -> str:
        """Format a clarification request message."""
        if confidence_result.level == ConfidenceLevel.VERY_LOW:
            return "I didn't catch that. Could you please repeat your request?"
        
        elif confidence_result.level == ConfidenceLevel.LOW:
            return f"I heard '{confidence_result.text}' but I'm not sure. Could you clarify what you meant?"
        
        else:
            return f"Did you say '{confidence_result.text}'?"


# Global instance for easy access
confidence_manager = ConfidenceManager()
