"""
Enhanced Instant Handler for Jarvis Voice Assistant

Provides ultra-fast pattern-based responses for instant queries (greetings, 
acknowledgments) targeting 0.05s response time with 0 API calls.
"""

import time
import logging
import re
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import random

logger = logging.getLogger(__name__)


class ResponseType(Enum):
    """Types of instant responses."""
    GREETING = "greeting"
    ACKNOWLEDGMENT = "acknowledgment"
    FAREWELL = "farewell"
    CONFIRMATION = "confirmation"
    NEGATION = "negation"
    APPRECIATION = "appreciation"
    CASUAL = "casual"
    TOOL_LISTING = "tool_listing"


@dataclass
class InstantResponse:
    """Instant response with metadata."""
    text: str
    response_type: ResponseType
    confidence: float
    processing_time: float
    cached: bool = False


class EnhancedInstantHandler:
    """
    Enhanced instant response handler with pattern matching and caching.
    
    Provides sub-50ms responses for common conversational patterns without
    requiring LLM processing or API calls. Uses pre-defined response templates
    with natural variation and context awareness.
    """
    
    def __init__(self):
        """Initialize enhanced instant handler."""
        self.response_patterns = self._initialize_patterns()
        self.response_cache = {}
        self.usage_stats = {
            "total_requests": 0,
            "cache_hits": 0,
            "pattern_matches": 0,
            "avg_response_time": 0.0
        }
        
        logger.info("EnhancedInstantHandler initialized with pattern matching")
    
    def _initialize_patterns(self) -> Dict[ResponseType, Dict[str, List[str]]]:
        """Initialize response patterns and templates."""
        return {
            ResponseType.GREETING: {
                "patterns": [
                    r'\b(hi|hello|hey|good morning|good afternoon|good evening)\b',
                    r'^(morning|afternoon|evening)$',
                    r'\b(what\'s up|how are you|how\'s it going)\b'
                ],
                "responses": [
                    "Hello! How can I help you?",
                    "Hi there! What can I do for you?",
                    "Good to hear from you! What do you need?",
                    "Hello! I'm here to assist you.",
                    "Hi! Ready to help with whatever you need.",
                    "Hey! What's on your mind?",
                    "Good to see you! How can I assist?",
                    "Hello! What would you like to know?"
                ]
            },
            
            ResponseType.ACKNOWLEDGMENT: {
                "patterns": [
                    r'\b(thanks?|thank you|thx|appreciate it)\b',
                    r'^(got it|understood|makes sense|i see)$'
                ],
                "responses": [
                    "You're welcome!",
                    "Happy to help!",
                    "Glad I could assist!",
                    "Anytime!",
                    "My pleasure!",
                    "You got it!",
                    "No problem at all!",
                    "Always here to help!"
                ]
            },
            
            ResponseType.FAREWELL: {
                "patterns": [
                    r'\b(bye|goodbye|see you|talk later|catch you later)\b',
                    r'^(later|peace|take care)$'
                ],
                "responses": [
                    "Goodbye! Have a great day!",
                    "See you later!",
                    "Take care!",
                    "Until next time!",
                    "Catch you later!",
                    "Have a wonderful day!",
                    "Talk to you soon!",
                    "Farewell!"
                ]
            },
            
            ResponseType.CONFIRMATION: {
                "patterns": [
                    r'^(yes|yeah|yep|yup|sure|ok|okay|alright|right|correct)$',
                    r'^(absolutely|definitely|of course|certainly)$'
                ],
                "responses": [
                    "Great! What's next?",
                    "Perfect! How can I help further?",
                    "Excellent! What else do you need?",
                    "Sounds good! What would you like to do?",
                    "Wonderful! I'm ready for your next request.",
                    "Got it! What's the next step?",
                    "Perfect! How else can I assist?",
                    "Excellent! What can I do for you now?"
                ]
            },
            
            ResponseType.NEGATION: {
                "patterns": [
                    r'^(no|nope|nah|not really|not now)$',
                    r'^(never mind|forget it|cancel)$'
                ],
                "responses": [
                    "No problem! Let me know if you need anything else.",
                    "Understood! I'm here when you're ready.",
                    "Got it! Feel free to ask if you change your mind.",
                    "No worries! I'll be here if you need me.",
                    "Alright! Just let me know if you need help later.",
                    "Sure thing! I'm available whenever you need assistance.",
                    "Okay! Don't hesitate to reach out if you need anything.",
                    "Understood! I'm here whenever you're ready."
                ]
            },
            
            ResponseType.CASUAL: {
                "patterns": [
                    r'^(cool|nice|great|awesome|sweet|neat)$',
                    r'^(wow|amazing|incredible|fantastic)$'
                ],
                "responses": [
                    "Right? Glad you think so!",
                    "I'm happy you like it!",
                    "Awesome! Anything else I can help with?",
                    "Great to hear! What's next?",
                    "Fantastic! How else can I assist?",
                    "Nice! What would you like to do now?",
                    "Excellent! I'm here for whatever you need.",
                    "Wonderful! What can I help you with next?"
                ]
            },
            
            ResponseType.APPRECIATION: {
                "patterns": [
                    r'\b(good job|well done|nice work|excellent)\b',
                    r'\b(impressive|helpful|useful)\b'
                ],
                "responses": [
                    "Thank you! I'm glad I could help!",
                    "I appreciate that! Happy to assist anytime.",
                    "Thanks! That means a lot. What else can I do?",
                    "Thank you! I'm here whenever you need help.",
                    "I'm so glad it was helpful! What's next?",
                    "Thanks! I love being able to help you out.",
                    "That's wonderful to hear! How else can I assist?",
                    "Thank you! I'm always ready to help."
                ]
            },
            ResponseType.TOOL_LISTING: {
                "patterns": [
                    r'(what tools|all tools|available tools|tools you have)',
                    r'(what can you do|your capabilities|list tools)',
                    r'(show tools|show all tools|tools available)',
                    r'(what are your tools|what tools do you have)',
                    r'(list all tools|show me tools)'
                ],
                "responses": [
                    # This will be dynamically generated
                    "I have access to many tools! Let me list them for you."
                ]
            }
        }
    
    def handle_instant_query(self, query: str, context: Optional[Dict[str, Any]] = None) -> Optional[InstantResponse]:
        """
        Handle instant query with pattern matching.
        
        Args:
            query: User query to process
            context: Optional context for response customization
            
        Returns:
            InstantResponse if pattern matched, None otherwise
        """
        start_time = time.time()
        self.usage_stats["total_requests"] += 1
        
        if not query or not query.strip():
            return None
        
        query_lower = query.lower().strip()
        
        # Check cache first
        cache_key = f"instant_{hash(query_lower)}"
        if cache_key in self.response_cache:
            cached_response = self.response_cache[cache_key]
            cached_response.processing_time = time.time() - start_time
            cached_response.cached = True
            self.usage_stats["cache_hits"] += 1
            return cached_response
        
        # Try pattern matching
        response = self._match_patterns(query_lower, context)
        
        if response:
            response.processing_time = time.time() - start_time
            
            # Cache successful response
            self.response_cache[cache_key] = response
            self.usage_stats["pattern_matches"] += 1
            
            # Update average response time
            total_time = (self.usage_stats["avg_response_time"] * 
                         (self.usage_stats["total_requests"] - 1) + 
                         response.processing_time)
            self.usage_stats["avg_response_time"] = total_time / self.usage_stats["total_requests"]
            
            logger.debug(f"Instant response generated in {response.processing_time*1000:.1f}ms")
            return response
        
        return None
    
    def _match_patterns(self, query: str, context: Optional[Dict[str, Any]] = None) -> Optional[InstantResponse]:
        """Match query against response patterns."""
        
        for response_type, pattern_data in self.response_patterns.items():
            patterns = pattern_data["patterns"]
            responses = pattern_data["responses"]
            
            for pattern in patterns:
                match = re.search(pattern, query, re.IGNORECASE)
                if match:
                    # Calculate confidence based on match quality
                    confidence = self._calculate_confidence(match, query, pattern)
                    
                    # Select appropriate response
                    response_text = self._select_response(responses, context, response_type)
                    
                    return InstantResponse(
                        text=response_text,
                        response_type=response_type,
                        confidence=confidence,
                        processing_time=0.0  # Will be set by caller
                    )
        
        return None
    
    def _calculate_confidence(self, match: re.Match, query: str, pattern: str) -> float:
        """Calculate confidence score for pattern match."""
        # Base confidence
        confidence = 0.8
        
        # Boost for exact matches
        if match.group(0) == query:
            confidence = 0.95
        
        # Boost for full word matches
        elif match.start() == 0 and match.end() == len(query):
            confidence = 0.9
        
        # Reduce for partial matches in longer queries
        elif len(query) > len(match.group(0)) * 2:
            confidence = 0.6
        
        return min(1.0, confidence)
    
    def _select_response(self,
                        responses: List[str],
                        context: Optional[Dict[str, Any]],
                        response_type: ResponseType) -> str:
        """Select appropriate response with variation and context awareness."""

        # Special handling for tool listing
        if response_type == ResponseType.TOOL_LISTING:
            return self._generate_tool_listing_response()

        # Context-aware response selection
        if context:
            # Time-based responses for greetings
            if response_type == ResponseType.GREETING and "time_of_day" in context:
                time_of_day = context["time_of_day"]
                if time_of_day == "morning":
                    morning_responses = [r for r in responses if "morning" in r.lower() or "day" in r.lower()]
                    if morning_responses:
                        return random.choice(morning_responses)
                elif time_of_day == "evening":
                    evening_responses = [r for r in responses if "evening" in r.lower() or "night" in r.lower()]
                    if evening_responses:
                        return random.choice(evening_responses)
            
            # User name personalization
            if "user_name" in context and context["user_name"]:
                user_name = context["user_name"]
                selected = random.choice(responses)
                # Add name to some responses
                if response_type in [ResponseType.GREETING, ResponseType.FAREWELL] and random.random() < 0.3:
                    return f"{selected.rstrip('!')} {user_name}!"
        
        # Default random selection for natural variation
        return random.choice(responses)

    def _generate_tool_listing_response(self) -> str:
        """Generate a comprehensive tool listing response."""
        try:
            # Import plugin manager to get all tools
            from ...plugins.manager import PluginManager

            plugin_manager = PluginManager(auto_discover=True)
            all_tools = plugin_manager.get_all_tools()

            if not all_tools:
                return "I don't have any tools available at the moment."

            # Categorize tools for better organization
            categories = {
                'Time & Date': [],
                'Memory & Knowledge': [],
                'Web & Automation': [],
                'Files & Code': [],
                'User Interface': [],
                'Profile & Settings': [],
                'MCP Servers': [],
                'Testing & Debug': [],
                'Other Tools': []
            }

            # Categorize tools based on their names and descriptions
            for tool in all_tools:
                tool_name = tool.name.lower()
                tool_desc = getattr(tool, 'description', '').lower()

                if any(keyword in tool_name for keyword in ['time', 'date', 'clock']):
                    categories['Time & Date'].append(tool)
                elif any(keyword in tool_name for keyword in ['remember', 'search', 'memory', 'fact', 'rag', 'vault']):
                    categories['Memory & Knowledge'].append(tool)
                elif any(keyword in tool_name for keyword in ['web', 'browser', 'automation', 'scraping']):
                    categories['Web & Automation'].append(tool)
                elif any(keyword in tool_name for keyword in ['file', 'aider', 'code', 'edit']):
                    categories['Files & Code'].append(tool)
                elif any(keyword in tool_name for keyword in ['jarvis_ui', 'open', 'close', 'show', 'ui']):
                    categories['User Interface'].append(tool)
                elif any(keyword in tool_name for keyword in ['name', 'profile', 'pronouns']):
                    categories['Profile & Settings'].append(tool)
                elif any(keyword in tool_name for keyword in ['mcp', 'server', 'add', 'list']):
                    categories['MCP Servers'].append(tool)
                elif any(keyword in tool_name for keyword in ['test', 'robot', 'validate', 'logs', 'terminal', 'debug']):
                    categories['Testing & Debug'].append(tool)
                else:
                    categories['Other Tools'].append(tool)

            # Build the response
            response_parts = [
                f"I have access to **{len(all_tools)} tools** across multiple categories:",
                ""
            ]

            # Add each category with tools
            for category, tools in categories.items():
                if tools:
                    response_parts.append(f"**{category}:**")
                    for tool in tools[:3]:  # Show first 3 tools per category
                        tool_desc = getattr(tool, 'description', 'No description available')
                        # Clean up the description
                        if len(tool_desc) > 80:
                            tool_desc = tool_desc[:77] + "..."
                        response_parts.append(f"• **{tool.name}**: {tool_desc}")

                    if len(tools) > 3:
                        response_parts.append(f"  ... and {len(tools) - 3} more {category.lower()} tools")
                    response_parts.append("")

            # Add summary
            response_parts.extend([
                f"**Total capabilities:** {len(all_tools)} tools covering time, memory, web automation, file editing, UI control, and much more!",
                "",
                "Ask me to use any of these tools or say something like 'What time is it?' or 'Remember that I like coffee' to see them in action!"
            ])

            return "\n".join(response_parts)

        except Exception as e:
            logger.error(f"Failed to generate tool listing: {e}")
            return f"I have access to many tools for time, memory, web automation, file editing, and more! Try asking me 'What time is it?' or 'Remember something' to see them in action."
    
    def add_custom_pattern(self, 
                          response_type: ResponseType, 
                          pattern: str, 
                          responses: List[str]) -> None:
        """
        Add custom response pattern.
        
        Args:
            response_type: Type of response
            pattern: Regex pattern to match
            responses: List of possible responses
        """
        if response_type not in self.response_patterns:
            self.response_patterns[response_type] = {"patterns": [], "responses": []}
        
        self.response_patterns[response_type]["patterns"].append(pattern)
        self.response_patterns[response_type]["responses"].extend(responses)
        
        # Clear cache to ensure new patterns are used
        self.response_cache.clear()
        
        logger.info(f"Added custom pattern for {response_type.value}: {pattern}")
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics."""
        cache_hit_rate = (self.usage_stats["cache_hits"] / 
                         max(1, self.usage_stats["total_requests"]))
        
        pattern_match_rate = (self.usage_stats["pattern_matches"] / 
                             max(1, self.usage_stats["total_requests"]))
        
        return {
            "total_requests": self.usage_stats["total_requests"],
            "cache_hits": self.usage_stats["cache_hits"],
            "pattern_matches": self.usage_stats["pattern_matches"],
            "cache_hit_rate": cache_hit_rate,
            "pattern_match_rate": pattern_match_rate,
            "avg_response_time_ms": self.usage_stats["avg_response_time"] * 1000,
            "cached_responses": len(self.response_cache),
            "total_patterns": sum(len(data["patterns"]) for data in self.response_patterns.values())
        }
    
    def clear_cache(self) -> None:
        """Clear response cache."""
        self.response_cache.clear()
        logger.info("Instant response cache cleared")
    
    def reset_stats(self) -> None:
        """Reset usage statistics."""
        self.usage_stats = {
            "total_requests": 0,
            "cache_hits": 0,
            "pattern_matches": 0,
            "avg_response_time": 0.0
        }
        logger.info("Instant handler statistics reset")
    
    def is_instant_query(self, query: str) -> bool:
        """
        Check if query can be handled instantly.
        
        Args:
            query: Query to check
            
        Returns:
            True if query matches instant patterns
        """
        if not query or not query.strip():
            return False
        
        query_lower = query.lower().strip()
        
        # Check cache first
        cache_key = f"instant_{hash(query_lower)}"
        if cache_key in self.response_cache:
            return True
        
        # Check patterns
        for pattern_data in self.response_patterns.values():
            for pattern in pattern_data["patterns"]:
                if re.search(pattern, query_lower, re.IGNORECASE):
                    return True
        
        return False


# Global handler instance
_instant_handler = None


def get_instant_handler() -> EnhancedInstantHandler:
    """Get global enhanced instant handler instance."""
    global _instant_handler
    if _instant_handler is None:
        _instant_handler = EnhancedInstantHandler()
    return _instant_handler


# Convenience function for quick instant response checking
def try_instant_response(query: str, context: Optional[Dict[str, Any]] = None) -> Optional[str]:
    """
    Try to get instant response for query.
    
    Args:
        query: User query
        context: Optional context
        
    Returns:
        Instant response text or None
    """
    handler = get_instant_handler()
    response = handler.handle_instant_query(query, context)
    return response.text if response else None
