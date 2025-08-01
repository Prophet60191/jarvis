"""
Smart Query Classifier for Jarvis Voice Assistant

This module provides intelligent query classification with 4-level complexity analysis
and confidence scoring for optimal routing and performance optimization.
"""

import re
import time
import logging
from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Set
from collections import defaultdict

logger = logging.getLogger(__name__)


class QueryComplexity(Enum):
    """Query complexity levels for intelligent routing."""
    INSTANT = "instant"           # 0.05s target - Simple greetings, acknowledgments
    EXPLICIT_FACT = "explicit_fact"  # 0.3s target - Direct factual queries
    SIMPLE_REASONING = "simple_reasoning"  # 1s target - Basic analysis, explanations
    COMPLEX_MULTI_STEP = "complex_multi_step"  # 5s target - Multi-tool workflows


@dataclass
class ClassificationResult:
    """Result of query classification."""
    complexity: QueryComplexity
    confidence: float
    suggested_tools: List[str]
    reasoning: str
    cache_key: Optional[str] = None
    estimated_response_time: float = 0.0


class SmartQueryClassifier:
    """
    Intelligent query classifier with pattern matching and confidence scoring.
    
    Provides 4-level classification system optimized for voice assistant performance:
    - Instant: Pattern-based responses (greetings, simple acknowledgments)
    - Explicit Fact: Direct factual queries (time, weather, definitions)
    - Simple Reasoning: Basic analysis requiring single tool or knowledge
    - Complex Multi-Step: Workflows requiring multiple tools and coordination
    """
    
    def __init__(self):
        """Initialize the smart query classifier."""
        self.classification_stats = defaultdict(int)
        self.pattern_cache = {}
        self._initialize_patterns()
        logger.info("SmartQueryClassifier initialized")
    
    def _initialize_patterns(self) -> None:
        """Initialize classification patterns and keywords."""
        
        # INSTANT responses - Pattern-based, no LLM needed
        self.instant_patterns = {
            # Greetings and acknowledgments
            r'\b(hi|hello|hey|good morning|good afternoon|good evening)\b': 0.95,
            r'\b(thanks?|thank you|thx)\b': 0.95,
            r'\b(yes|yeah|yep|ok|okay|sure|alright)\b': 0.90,
            r'\b(no|nope|nah)\b': 0.90,
            r'\b(bye|goodbye|see you|talk later)\b': 0.95,

            # Simple confirmations
            r'^(got it|understood|makes sense)$': 0.95,
            r'^(cool|nice|great|awesome|perfect)$': 0.85,

            # Tool listing queries
            r'(what tools|all tools|available tools|tools you have)': 0.95,
            r'(what can you do|your capabilities|list tools)': 0.95,
            r'(show tools|show all tools|tools available)': 0.90,
        }
        
        # EXPLICIT FACT queries - Direct factual information
        self.explicit_fact_patterns = {
            # Time and date queries
            r'\b(what time|current time|time is it)\b': 0.95,
            r'\b(what date|today\'s date|current date)\b': 0.95,
            r'\b(what day|day of the week)\b': 0.90,
            
            # Direct factual queries
            r'\b(what is|define|definition of)\b': 0.85,
            r'\b(how many|how much|how long|how far)\b': 0.80,
            r'\b(when did|when was|when will)\b': 0.80,
            r'\b(where is|where are|where can)\b': 0.75,
        }
        
        # SIMPLE REASONING - Single tool or basic analysis
        self.simple_reasoning_patterns = {
            # Explanatory requests
            r'\b(explain|tell me about|describe)\b': 0.85,
            r'\b(how does|how do|why does|why do)\b': 0.80,
            r'\b(what are the|list the|show me)\b': 0.75,
            
            # Memory operations
            r'\b(remember that|save this|store)\b': 0.90,
            r'\b(what do you remember|recall|search memory)\b': 0.90,
            
            # Simple calculations
            r'\b(calculate|compute|math|add|subtract|multiply|divide)\b': 0.85,
        }
        
        # COMPLEX MULTI-STEP - Multiple tools and coordination
        self.complex_patterns = {
            # Creation and development
            r'\b(create|build|develop|make|generate)\b.*\b(script|program|tool|system)\b': 0.90,
            r'\b(analyze|process|extract).*\b(data|file|website)\b': 0.85,
            
            # Multi-step workflows
            r'\b(research|investigate|study)\b.*\b(and|then)\b': 0.80,
            r'\b(download|scrape|get).*\b(and|then)\b.*\b(analyze|process)\b': 0.85,
            
            # Automation requests
            r'\b(automate|schedule|monitor|track)\b': 0.80,
            r'\b(test|validate|check).*\b(and|then)\b': 0.75,
        }
        
        # Tool suggestion mappings
        self.tool_suggestions = {
            # Time-related
            r'\b(time|date|day)\b': ['get_current_time'],
            
            # Memory operations
            r'\b(remember|save|store)\b': ['remember_fact'],
            r'\b(recall|search memory|what do you remember)\b': ['search_long_term_memory'],
            
            # Code execution
            r'\b(calculate|compute|run|execute)\b': ['execute_code'],
            r'\b(analyze.*file|process.*data)\b': ['analyze_file'],
            
            # Web operations
            r'\b(website|web|scrape|download)\b': ['web_automation_task'],
            
            # File operations
            r'\b(file|folder|directory)\b': ['filesystem'],
        }
    
    def classify_query(self, query: str) -> ClassificationResult:
        """
        Classify a query and return classification result with confidence.
        
        Args:
            query: User query to classify
            
        Returns:
            ClassificationResult with complexity, confidence, and suggestions
        """
        start_time = time.time()
        
        if not query or not query.strip():
            return ClassificationResult(
                complexity=QueryComplexity.INSTANT,
                confidence=0.0,
                suggested_tools=[],
                reasoning="Empty query",
                estimated_response_time=0.01
            )
        
        query_lower = query.lower().strip()
        
        # Check cache first
        cache_key = f"classify_{hash(query_lower)}"
        if cache_key in self.pattern_cache:
            cached_result = self.pattern_cache[cache_key]
            cached_result.estimated_response_time = time.time() - start_time
            return cached_result
        
        # Classify using pattern matching
        result = self._classify_with_patterns(query_lower)
        
        # Add suggested tools
        result.suggested_tools = self._suggest_tools(query_lower)
        
        # Set cache key and timing
        result.cache_key = cache_key
        result.estimated_response_time = time.time() - start_time
        
        # Cache result
        self.pattern_cache[cache_key] = result
        
        # Update stats
        self.classification_stats[result.complexity.value] += 1
        
        logger.debug(f"Classified query '{query[:50]}...' as {result.complexity.value} "
                    f"(confidence: {result.confidence:.2f})")
        
        return result
    
    def _classify_with_patterns(self, query: str) -> ClassificationResult:
        """Classify query using pattern matching."""
        
        # Check INSTANT patterns first (highest priority)
        for pattern, confidence in self.instant_patterns.items():
            if re.search(pattern, query, re.IGNORECASE):
                return ClassificationResult(
                    complexity=QueryComplexity.INSTANT,
                    confidence=confidence,
                    suggested_tools=[],
                    reasoning=f"Matched instant pattern: {pattern}"
                )
        
        # Check COMPLEX patterns (before simple ones to catch multi-step)
        max_complex_confidence = 0.0
        complex_pattern = None
        for pattern, confidence in self.complex_patterns.items():
            if re.search(pattern, query, re.IGNORECASE):
                if confidence > max_complex_confidence:
                    max_complex_confidence = confidence
                    complex_pattern = pattern
        
        if max_complex_confidence > 0.7:  # High confidence threshold for complex
            return ClassificationResult(
                complexity=QueryComplexity.COMPLEX_MULTI_STEP,
                confidence=max_complex_confidence,
                suggested_tools=[],
                reasoning=f"Matched complex pattern: {complex_pattern}"
            )
        
        # Check EXPLICIT FACT patterns
        max_fact_confidence = 0.0
        fact_pattern = None
        for pattern, confidence in self.explicit_fact_patterns.items():
            if re.search(pattern, query, re.IGNORECASE):
                if confidence > max_fact_confidence:
                    max_fact_confidence = confidence
                    fact_pattern = pattern
        
        # Check SIMPLE REASONING patterns
        max_reasoning_confidence = 0.0
        reasoning_pattern = None
        for pattern, confidence in self.simple_reasoning_patterns.items():
            if re.search(pattern, query, re.IGNORECASE):
                if confidence > max_reasoning_confidence:
                    max_reasoning_confidence = confidence
                    reasoning_pattern = pattern
        
        # Determine best classification
        if max_fact_confidence > max_reasoning_confidence and max_fact_confidence > 0.6:
            return ClassificationResult(
                complexity=QueryComplexity.EXPLICIT_FACT,
                confidence=max_fact_confidence,
                suggested_tools=[],
                reasoning=f"Matched explicit fact pattern: {fact_pattern}"
            )
        elif max_reasoning_confidence > 0.6:
            return ClassificationResult(
                complexity=QueryComplexity.SIMPLE_REASONING,
                confidence=max_reasoning_confidence,
                suggested_tools=[],
                reasoning=f"Matched simple reasoning pattern: {reasoning_pattern}"
            )
        elif max_complex_confidence > 0.5:  # Lower threshold as fallback
            return ClassificationResult(
                complexity=QueryComplexity.COMPLEX_MULTI_STEP,
                confidence=max_complex_confidence,
                suggested_tools=[],
                reasoning=f"Matched complex pattern (lower confidence): {complex_pattern}"
            )
        else:
            # Default to simple reasoning for unmatched queries
            return ClassificationResult(
                complexity=QueryComplexity.SIMPLE_REASONING,
                confidence=0.5,
                suggested_tools=[],
                reasoning="Default classification - no strong pattern match"
            )
    
    def _suggest_tools(self, query: str) -> List[str]:
        """Suggest relevant tools based on query content."""
        suggested = set()
        
        for pattern, tools in self.tool_suggestions.items():
            if re.search(pattern, query, re.IGNORECASE):
                suggested.update(tools)
        
        return list(suggested)
    
    def get_performance_targets(self, complexity: QueryComplexity) -> Dict[str, float]:
        """Get performance targets for a complexity level."""
        targets = {
            QueryComplexity.INSTANT: {"response_time": 0.05, "api_calls": 0},
            QueryComplexity.EXPLICIT_FACT: {"response_time": 0.3, "api_calls": 0.5},
            QueryComplexity.SIMPLE_REASONING: {"response_time": 1.0, "api_calls": 1},
            QueryComplexity.COMPLEX_MULTI_STEP: {"response_time": 5.0, "api_calls": 3}
        }
        return targets.get(complexity, targets[QueryComplexity.SIMPLE_REASONING])
    
    def get_classification_stats(self) -> Dict[str, int]:
        """Get classification statistics."""
        return dict(self.classification_stats)
    
    def clear_cache(self) -> None:
        """Clear the pattern cache."""
        self.pattern_cache.clear()
        logger.info("Classification cache cleared")


# Global classifier instance
_classifier_instance = None


def get_smart_classifier() -> SmartQueryClassifier:
    """Get the global smart classifier instance."""
    global _classifier_instance
    if _classifier_instance is None:
        _classifier_instance = SmartQueryClassifier()
    return _classifier_instance
