"""
Learning Engine for Tool Orchestration

Implements machine learning capabilities for improving tool selection
and orchestration over time based on usage patterns and success rates.
"""

import time
import logging
import statistics
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque
import threading
import json

logger = logging.getLogger(__name__)

class LearningStrategy(Enum):
    """Learning strategies for the engine."""
    REINFORCEMENT = "reinforcement"
    PATTERN_BASED = "pattern_based"
    COLLABORATIVE = "collaborative"
    HYBRID = "hybrid"

@dataclass
class LearningPattern:
    """Represents a learned pattern."""
    pattern_id: str
    pattern_type: str
    confidence: float = 0.0
    usage_count: int = 0
    success_rate: float = 0.0
    last_updated: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)

class LearningEngine:
    """
    Machine learning engine for tool orchestration optimization.
    
    This component learns from tool usage patterns and outcomes to
    improve future tool selection and orchestration decisions.
    """
    
    def __init__(self, strategy: LearningStrategy = LearningStrategy.HYBRID):
        """
        Initialize the learning engine.
        
        Args:
            strategy: Learning strategy to use
        """
        self.strategy = strategy
        
        # Learning data
        self._patterns: Dict[str, LearningPattern] = {}
        self._experience_buffer: deque = deque(maxlen=10000)
        self._success_history: Dict[str, List[bool]] = defaultdict(list)
        
        # Configuration
        self.learning_rate = 0.1
        self.confidence_threshold = 0.7
        self.pattern_decay_rate = 0.95
        self.min_pattern_occurrences = 5
        
        # Thread safety
        self._lock = threading.RLock()
        
        logger.info(f"LearningEngine initialized with {strategy.value} strategy")
    
    def learn_from_experience(self, experience: Dict[str, Any]) -> None:
        """
        Learn from a tool orchestration experience.
        
        Args:
            experience: Experience data including tools, context, and outcome
        """
        with self._lock:
            # Add to experience buffer
            experience["timestamp"] = time.time()
            self._experience_buffer.append(experience)
            
            # Extract learning signals
            self._extract_patterns(experience)
            self._update_success_rates(experience)
            
            logger.debug(f"Learned from experience: {experience.get('outcome', 'unknown')}")
    
    def get_recommendations(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Get tool recommendations based on learned patterns.
        
        Args:
            context: Current context
            
        Returns:
            List[Dict[str, Any]]: Recommendations with confidence scores
        """
        with self._lock:
            recommendations = []
            
            # Find relevant patterns
            relevant_patterns = self._find_relevant_patterns(context)
            
            for pattern in relevant_patterns:
                if pattern.confidence >= self.confidence_threshold:
                    recommendation = {
                        "pattern_id": pattern.pattern_id,
                        "pattern_type": pattern.pattern_type,
                        "confidence": pattern.confidence,
                        "success_rate": pattern.success_rate,
                        "metadata": pattern.metadata
                    }
                    recommendations.append(recommendation)
            
            # Sort by confidence
            recommendations.sort(key=lambda r: r["confidence"], reverse=True)
            
            return recommendations
    
    def update_pattern_confidence(self, pattern_id: str, success: bool) -> None:
        """
        Update pattern confidence based on outcome.
        
        Args:
            pattern_id: Pattern identifier
            success: Whether the pattern led to success
        """
        with self._lock:
            if pattern_id in self._patterns:
                pattern = self._patterns[pattern_id]
                
                # Update success rate
                pattern.usage_count += 1
                if pattern.usage_count == 1:
                    pattern.success_rate = 1.0 if success else 0.0
                else:
                    total_successes = pattern.success_rate * (pattern.usage_count - 1)
                    total_successes += 1.0 if success else 0.0
                    pattern.success_rate = total_successes / pattern.usage_count
                
                # Update confidence
                usage_factor = min(pattern.usage_count / 10.0, 1.0)
                pattern.confidence = usage_factor * pattern.success_rate
                pattern.last_updated = time.time()
    
    def get_learning_statistics(self) -> Dict[str, Any]:
        """
        Get learning engine statistics.
        
        Returns:
            Dict[str, Any]: Learning statistics
        """
        with self._lock:
            total_patterns = len(self._patterns)
            high_confidence_patterns = sum(
                1 for p in self._patterns.values() if p.confidence > 0.7
            )
            
            avg_confidence = 0.0
            avg_success_rate = 0.0
            
            if self._patterns:
                avg_confidence = statistics.mean(p.confidence for p in self._patterns.values())
                avg_success_rate = statistics.mean(p.success_rate for p in self._patterns.values())
            
            return {
                "strategy": self.strategy.value,
                "total_patterns": total_patterns,
                "high_confidence_patterns": high_confidence_patterns,
                "experience_buffer_size": len(self._experience_buffer),
                "average_confidence": avg_confidence,
                "average_success_rate": avg_success_rate,
                "learning_rate": self.learning_rate
            }
    
    def _extract_patterns(self, experience: Dict[str, Any]) -> None:
        """Extract patterns from experience."""
        tools_used = experience.get("tools_used", [])
        context = experience.get("context", {})
        success = experience.get("success", False)
        
        if len(tools_used) < 2:
            return
        
        # Create pattern for tool sequence
        pattern_id = "->".join(tools_used)
        
        if pattern_id not in self._patterns:
            self._patterns[pattern_id] = LearningPattern(
                pattern_id=pattern_id,
                pattern_type="tool_sequence",
                metadata={
                    "tools": tools_used,
                    "context_type": context.get("type", "unknown")
                }
            )
        
        # Update pattern
        self.update_pattern_confidence(pattern_id, success)
    
    def _update_success_rates(self, experience: Dict[str, Any]) -> None:
        """Update success rates for tools."""
        tools_used = experience.get("tools_used", [])
        success = experience.get("success", False)
        
        for tool in tools_used:
            self._success_history[tool].append(success)
            
            # Keep only recent history
            if len(self._success_history[tool]) > 100:
                self._success_history[tool] = self._success_history[tool][-100:]
    
    def _find_relevant_patterns(self, context: Dict[str, Any]) -> List[LearningPattern]:
        """Find patterns relevant to the current context."""
        relevant_patterns = []
        
        context_type = context.get("type", "unknown")
        
        for pattern in self._patterns.values():
            # Check if pattern is relevant to context
            if pattern.metadata.get("context_type") == context_type:
                relevant_patterns.append(pattern)
        
        return relevant_patterns
