"""
Intent Router for Fast/Slow Path Optimization

Implements industry-standard fast/slow path routing pattern used by
Alexa, Google Assistant, and other high-performance AI systems.
"""

import time
import logging
from typing import Dict, List, Optional, Callable, Any
from enum import Enum
from dataclasses import dataclass

logger = logging.getLogger(__name__)

class ExecutionPath(Enum):
    """Execution path types based on query complexity."""
    INSTANT = "instant"      # <200ms, direct function calls, no LLM
    ADAPTIVE = "adaptive"    # 200ms-2s, lightweight processing
    COMPLEX = "complex"      # 2s+, full orchestration and LLM processing

@dataclass
class RouteResult:
    """Result of intent routing."""
    path: ExecutionPath
    intent: str
    confidence: float
    handler: Optional[Callable] = None
    metadata: Dict[str, Any] = None

class IntentRouter:
    """
    Fast intent classification and routing system.
    
    Uses simple pattern matching (not LLM) for speed, following
    the approach used by major voice assistants.
    """
    
    def __init__(self):
        """Initialize the intent router."""
        
        # Fast path patterns - VERY specific keyword matching to avoid false positives
        self.instant_patterns = {
            "time_query": {
                "patterns": ["what time is it", "what's the time", "current time", "tell me the time"],
                "handler": self._handle_time_query,
                "description": "Get current time"
            },
            "greeting": {
                "patterns": ["hello", "hi", "hey jarvis", "good morning", "good afternoon"],
                "handler": self._handle_greeting,
                "description": "Respond to greetings"
            },
            "simple_status": {
                "patterns": ["how are you", "are you working", "are you ok"],
                "handler": self._handle_status_check,
                "description": "Simple status check"
            }
        }
        
        # Adaptive path patterns - specific tool-related queries that need LLM processing
        self.adaptive_patterns = {
            "profile_operations": {
                "patterns": ["my name is", "set my name", "what is my name", "show my profile", "my pronouns"],
                "description": "User profile operations"
            },
            "memory_operations": {
                "patterns": ["remember that", "search my", "what do you remember", "find in my"],
                "description": "Memory and search operations"
            },
            "system_operations": {
                "patterns": ["open logs", "show logs", "open vault", "show vault", "system status", "show status"],
                "description": "System control operations"
            },
            "tool_status": {
                "patterns": ["is aider", "is web automation", "is the test", "check status"],
                "description": "Tool status checks"
            },
            "simple_question": {
                "patterns": ["what is", "who is", "where is", "when is", "how do"],
                "description": "Simple factual questions"
            }
        }
        
        # Complex path indicators - require full orchestration
        self.complex_patterns = {
            "analysis": ["analyze", "compare", "evaluate", "assess"],
            "creation": ["create", "generate", "build", "make", "write"],
            "automation": ["automate", "script", "batch", "process multiple"],
            "integration": ["integrate", "connect", "sync", "combine"],
            "explanation": ["explain how", "describe the process", "walk me through"]
        }
        
        # Performance tracking
        self.route_stats = {
            ExecutionPath.INSTANT: {"count": 0, "total_time": 0.0},
            ExecutionPath.ADAPTIVE: {"count": 0, "total_time": 0.0},
            ExecutionPath.COMPLEX: {"count": 0, "total_time": 0.0}
        }
        
        logger.info("IntentRouter initialized with fast/slow path optimization")
    
    def route_query(self, query: str) -> RouteResult:
        """
        Route query to appropriate execution path.

        Args:
            query: User query string

        Returns:
            RouteResult: Routing decision with path and handler
        """
        start_time = time.time()
        query_lower = query.lower().strip()

        # Step 0: Check for complex query indicators that should NEVER use fast path
        if self._is_complex_query(query_lower):
            route_time = time.time() - start_time
            self._update_stats(ExecutionPath.COMPLEX, route_time)
            result = RouteResult(
                path=ExecutionPath.COMPLEX,
                intent="complex_workflow",
                confidence=0.9,
                metadata={"forced_complex": True}
            )
            logger.info(f"🔄 COMPLEX query detected, forcing FULL path: '{query}'")
            return result

        # Step 1: Check for instant patterns (fast path) - only for simple queries
        instant_result = self._check_instant_patterns(query_lower)
        if instant_result:
            route_time = time.time() - start_time
            self._update_stats(ExecutionPath.INSTANT, route_time)
            logger.debug(f"Routed to INSTANT path: {instant_result.intent} ({route_time*1000:.1f}ms)")
            return instant_result
        
        # Step 2: Check for adaptive patterns
        adaptive_result = self._check_adaptive_patterns(query_lower)
        if adaptive_result:
            route_time = time.time() - start_time
            self._update_stats(ExecutionPath.ADAPTIVE, route_time)
            logger.debug(f"Routed to ADAPTIVE path: {adaptive_result.intent} ({route_time*1000:.1f}ms)")
            return adaptive_result
        
        # Step 3: Check for complex patterns
        complex_result = self._check_complex_patterns(query_lower)
        if complex_result:
            route_time = time.time() - start_time
            self._update_stats(ExecutionPath.COMPLEX, route_time)
            logger.debug(f"Routed to COMPLEX path: {complex_result.intent} ({route_time*1000:.1f}ms)")
            return complex_result
        
        # Step 4: Default to adaptive path for unknown queries
        route_time = time.time() - start_time
        self._update_stats(ExecutionPath.ADAPTIVE, route_time)
        result = RouteResult(
            path=ExecutionPath.ADAPTIVE,
            intent="unknown_query",
            confidence=0.5,
            metadata={"fallback": True}
        )
        logger.debug(f"Routed to ADAPTIVE path (default): unknown_query ({route_time*1000:.1f}ms)")
        return result
    
    def _is_complex_query(self, query: str) -> bool:
        """Check if query contains complex indicators that require full processing."""
        import re

        complex_indicators = [
            r'\b(?:and|then|after|also|plus|additionally)\b',  # Multiple actions
            r'\b(?:create|build|make|generate)\s+(?:tool|function|script|calculator)\b',  # Tool creation
            r'\b(?:remember|store|save)\s+.*\s+(?:and|then)\b',  # Memory + action
            r'\b(?:search|find|look)\s+.*\s+(?:and|then)\b',  # Search + action
            r'\b(?:if|when|unless|provided)\b',  # Conditional logic
            r'\b(?:workflow|process|sequence|steps)\b',  # Multi-step processes
            r'\b(?:first|second|third|finally|lastly)\b',  # Sequential steps
            r'\b(?:calculate|compute|add|subtract|multiply|divide)\s+\d+',  # Math operations
        ]

        for pattern in complex_indicators:
            if re.search(pattern, query):
                return True
        return False

    def _check_instant_patterns(self, query: str) -> Optional[RouteResult]:
        """Check for instant execution patterns - only exact matches for simple queries."""
        for intent, config in self.instant_patterns.items():
            for pattern in config["patterns"]:
                # Only match if the query is EXACTLY the pattern (with minor variations)
                if (pattern == query or
                    f"{pattern}?" == query or
                    f"{pattern}." == query):
                    return RouteResult(
                        path=ExecutionPath.INSTANT,
                        intent=intent,
                        confidence=0.9,
                        handler=config.get("handler"),
                        metadata={"pattern_matched": pattern}
                    )
        return None
    
    def _check_adaptive_patterns(self, query: str) -> Optional[RouteResult]:
        """Check for adaptive execution patterns."""
        for intent, config in self.adaptive_patterns.items():
            for pattern in config["patterns"]:
                if pattern in query:
                    return RouteResult(
                        path=ExecutionPath.ADAPTIVE,
                        intent=intent,
                        confidence=0.7,
                        metadata={"pattern_matched": pattern}
                    )
        return None
    
    def _check_complex_patterns(self, query: str) -> Optional[RouteResult]:
        """Check for complex execution patterns."""
        for category, patterns in self.complex_patterns.items():
            for pattern in patterns:
                if pattern in query:
                    return RouteResult(
                        path=ExecutionPath.COMPLEX,
                        intent=f"complex_{category}",
                        confidence=0.8,
                        metadata={"category": category, "pattern_matched": pattern}
                    )
        return None
    
    def _update_stats(self, path: ExecutionPath, route_time: float):
        """Update routing performance statistics."""
        self.route_stats[path]["count"] += 1
        self.route_stats[path]["total_time"] += route_time
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get routing performance statistics."""
        stats = {}
        for path, data in self.route_stats.items():
            if data["count"] > 0:
                avg_time = data["total_time"] / data["count"]
                stats[path.value] = {
                    "count": data["count"],
                    "avg_route_time_ms": avg_time * 1000,
                    "total_time_ms": data["total_time"] * 1000
                }
        return stats
    
    # Fast path handlers - direct execution, no LLM needed
    def _handle_time_query(self, query: str) -> str:
        """Handle time queries directly."""
        from datetime import datetime
        now = datetime.now()
        time_str = now.strftime('%I:%M %p')
        if time_str.startswith('0'):
            time_str = time_str[1:]
        return f"It's {time_str}"
    
    def _handle_weather_query(self, query: str) -> str:
        """Handle weather queries directly."""
        # This would integrate with weather service
        return "I'd be happy to help with weather information. Let me check that for you."
    
    def _handle_music_control(self, query: str) -> str:
        """Handle music control directly."""
        return "I'd be happy to help with music. Let me start that for you."
    
    def _handle_greeting(self, query: str) -> str:
        """Handle greetings directly."""
        return "Hello! How can I help you today?"
    
    def _handle_status_check(self, query: str) -> str:
        """Handle status checks directly."""
        return "I'm working perfectly and ready to help you!"
