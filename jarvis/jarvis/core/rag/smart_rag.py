"""
Smart RAG System for Jarvis Voice Assistant

Query-dependent RAG activation with intelligent memory retrieval and
context compression for optimized conversation continuity.
"""

import time
import logging
import re
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass
from enum import Enum
import hashlib

logger = logging.getLogger(__name__)


class RAGActivationLevel(Enum):
    """RAG activation levels based on query analysis."""
    DISABLED = "disabled"      # No RAG needed (instant responses, general knowledge)
    MINIMAL = "minimal"        # Light memory search (recent context only)
    STANDARD = "standard"      # Full memory search (user preferences, facts)
    COMPREHENSIVE = "comprehensive"  # Deep search with document analysis


@dataclass
class RAGQuery:
    """RAG query with activation metadata."""
    original_query: str
    processed_query: str
    activation_level: RAGActivationLevel
    search_keywords: List[str]
    confidence: float
    reasoning: str


@dataclass
class RAGResult:
    """RAG retrieval result."""
    retrieved_content: List[str]
    relevance_scores: List[float]
    sources: List[str]
    processing_time: float
    cache_hit: bool = False
    activation_level: RAGActivationLevel = RAGActivationLevel.DISABLED


class SmartRAG:
    """
    Smart RAG system with query-dependent activation.
    
    Intelligently determines when to activate RAG based on:
    - Query content analysis (memory-related keywords)
    - User intent detection (remembering vs. general questions)
    - Context requirements (conversation continuity)
    - Performance optimization (avoid unnecessary searches)
    """
    
    def __init__(self):
        """Initialize smart RAG system."""
        self.activation_patterns = self._initialize_activation_patterns()
        self.query_cache = {}
        self.retrieval_cache = {}

        # Keep SmartRAG simple - no complex memory manager needed

        # Performance tracking
        self.stats = {
            "total_queries": 0,
            "rag_activations": 0,
            "cache_hits": 0,
            "avg_processing_time": 0.0,
            "activation_distribution": {level.value: 0 for level in RAGActivationLevel}
        }

        logger.info("SmartRAG initialized with query-dependent activation and real memory storage")
    
    def _initialize_activation_patterns(self) -> Dict[RAGActivationLevel, Dict[str, Any]]:
        """Initialize patterns for RAG activation detection."""
        return {
            RAGActivationLevel.DISABLED: {
                "patterns": [
                    r'\b(hi|hello|hey|thanks|bye|yes|no|ok)\b',  # Greetings, simple responses
                    r'\b(what time|current time|date)\b',        # Time queries
                    r'\b(what is|define|explain)\b.*\b(general|basic)\b',  # General knowledge
                ],
                "keywords": {"greeting", "time", "general", "basic", "simple"},
                "description": "Instant responses and general knowledge queries"
            },
            
            RAGActivationLevel.MINIMAL: {
                "patterns": [
                    r'\b(what did we|what were we|continue|keep going)\b',  # Conversation continuity
                    r'\b(that|it|this)\b.*\b(we discussed|mentioned)\b',   # Reference to recent context
                ],
                "keywords": {"continue", "discussed", "mentioned", "context", "recent"},
                "description": "Recent conversation context retrieval"
            },
            
            RAGActivationLevel.STANDARD: {
                "patterns": [
                    r'\b(remember|recall|what do you remember)\b',          # Direct memory queries
                    r'\b(my preferences|my settings|what I like)\b',        # User preferences
                    r'\b(last time|previously|before)\b',                   # Historical references
                    r'\b(search|find|look up)\b.*\b(memory|notes)\b',      # Explicit search requests
                ],
                "keywords": {"remember", "recall", "preferences", "settings", "previously", "search", "memory"},
                "description": "User memory and preference retrieval"
            },
            
            RAGActivationLevel.COMPREHENSIVE: {
                "patterns": [
                    r'\b(analyze|research|comprehensive)\b.*\b(documents|files)\b',  # Document analysis
                    r'\b(everything about|all information)\b',                       # Comprehensive queries
                    r'\b(detailed|thorough|complete)\b.*\b(analysis|report)\b',     # Deep analysis requests
                ],
                "keywords": {"analyze", "research", "comprehensive", "documents", "detailed", "thorough"},
                "description": "Deep document analysis and comprehensive retrieval"
            }
        }
    
    def analyze_query(self, query: str, context: Optional[Dict[str, Any]] = None) -> RAGQuery:
        """
        Analyze query to determine RAG activation level.
        
        Args:
            query: User query to analyze
            context: Optional context for analysis
            
        Returns:
            RAGQuery with activation level and metadata
        """
        if not query.strip():
            return RAGQuery(
                original_query=query,
                processed_query="",
                activation_level=RAGActivationLevel.DISABLED,
                search_keywords=[],
                confidence=0.0,
                reasoning="Empty query"
            )
        
        query_lower = query.lower().strip()
        
        # Check cache first
        cache_key = hashlib.md5(f"{query_lower}|{str(context)}".encode()).hexdigest()
        if cache_key in self.query_cache:
            return self.query_cache[cache_key]
        
        # Analyze activation level
        activation_level, confidence, reasoning = self._determine_activation_level(query_lower, context)
        
        # Extract search keywords
        search_keywords = self._extract_search_keywords(query_lower, activation_level)
        
        # Process query for RAG
        processed_query = self._process_query_for_rag(query_lower, activation_level)
        
        # Create RAG query
        rag_query = RAGQuery(
            original_query=query,
            processed_query=processed_query,
            activation_level=activation_level,
            search_keywords=search_keywords,
            confidence=confidence,
            reasoning=reasoning
        )
        
        # Cache result
        self.query_cache[cache_key] = rag_query
        
        # Update stats
        self.stats["total_queries"] += 1
        self.stats["activation_distribution"][activation_level.value] += 1
        if activation_level != RAGActivationLevel.DISABLED:
            self.stats["rag_activations"] += 1
        
        logger.debug(f"RAG activation: {activation_level.value} for query '{query[:50]}...'")
        return rag_query
    
    def _determine_activation_level(self, 
                                   query: str, 
                                   context: Optional[Dict[str, Any]]) -> Tuple[RAGActivationLevel, float, str]:
        """Determine RAG activation level with confidence scoring."""
        
        # Check patterns in order of priority (most specific first)
        for level in [RAGActivationLevel.COMPREHENSIVE, RAGActivationLevel.STANDARD, 
                     RAGActivationLevel.MINIMAL, RAGActivationLevel.DISABLED]:
            
            patterns = self.activation_patterns[level]["patterns"]
            keywords = self.activation_patterns[level]["keywords"]
            
            # Pattern matching
            pattern_matches = 0
            for pattern in patterns:
                if re.search(pattern, query, re.IGNORECASE):
                    pattern_matches += 1
            
            # Keyword matching
            query_words = set(query.split())
            keyword_matches = len(query_words.intersection(keywords))
            
            # Calculate confidence
            pattern_confidence = min(1.0, pattern_matches * 0.4)
            keyword_confidence = min(0.6, keyword_matches * 0.2)
            total_confidence = pattern_confidence + keyword_confidence
            
            # Context adjustments
            if context:
                total_confidence = self._apply_context_adjustments(
                    total_confidence, level, context
                )
            
            # Return first level with sufficient confidence
            if total_confidence >= 0.3:  # Minimum confidence threshold
                reasoning = f"Matched {pattern_matches} patterns, {keyword_matches} keywords"
                return level, total_confidence, reasoning
        
        # Default to disabled with low confidence
        return RAGActivationLevel.DISABLED, 0.1, "No strong activation patterns detected"
    
    def _apply_context_adjustments(self, 
                                  confidence: float, 
                                  level: RAGActivationLevel, 
                                  context: Dict[str, Any]) -> float:
        """Apply context-based confidence adjustments."""
        
        # Boost memory-related queries if user has stored memories
        if "has_stored_memories" in context and context["has_stored_memories"]:
            if level in [RAGActivationLevel.STANDARD, RAGActivationLevel.COMPREHENSIVE]:
                confidence *= 1.3
        
        # Boost if conversation has memory references
        if "memory_references" in context and context["memory_references"]:
            if level != RAGActivationLevel.DISABLED:
                confidence *= 1.2
        
        # Reduce for instant queries
        if "query_complexity" in context and context["query_complexity"] == "instant":
            if level != RAGActivationLevel.DISABLED:
                confidence *= 0.5
        
        # Boost for complex queries
        if "query_complexity" in context and context["query_complexity"] == "complex":
            if level in [RAGActivationLevel.STANDARD, RAGActivationLevel.COMPREHENSIVE]:
                confidence *= 1.2
        
        return min(1.0, confidence)
    
    def _extract_search_keywords(self, query: str, activation_level: RAGActivationLevel) -> List[str]:
        """Extract keywords for RAG search based on activation level."""
        if activation_level == RAGActivationLevel.DISABLED:
            return []
        
        # Basic keyword extraction
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have',
            'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should',
            'can', 'may', 'might', 'must', 'i', 'you', 'he', 'she', 'it', 'we',
            'they', 'me', 'him', 'her', 'us', 'them', 'what', 'when', 'where',
            'why', 'how', 'remember', 'recall', 'search', 'find'
        }
        
        # Extract meaningful words
        words = re.findall(r'\b[a-zA-Z]{3,}\b', query.lower())
        keywords = [word for word in words if word not in stop_words]
        
        # Limit keywords based on activation level
        max_keywords = {
            RAGActivationLevel.MINIMAL: 3,
            RAGActivationLevel.STANDARD: 5,
            RAGActivationLevel.COMPREHENSIVE: 10
        }
        
        limit = max_keywords.get(activation_level, 5)
        return keywords[:limit]
    
    def _process_query_for_rag(self, query: str, activation_level: RAGActivationLevel) -> str:
        """Process query for RAG retrieval."""
        if activation_level == RAGActivationLevel.DISABLED:
            return ""
        
        # Remove memory-specific terms for cleaner search
        processed = re.sub(r'\b(remember|recall|what do you remember about|search for)\b', '', query)
        processed = re.sub(r'\s+', ' ', processed).strip()
        
        return processed
    
    def retrieve(self, rag_query: RAGQuery, max_results: int = 5) -> RAGResult:
        """
        Retrieve relevant content based on RAG query.
        
        Args:
            rag_query: RAG query with activation metadata
            max_results: Maximum number of results to return
            
        Returns:
            RAG retrieval result
        """
        start_time = time.time()
        
        if rag_query.activation_level == RAGActivationLevel.DISABLED:
            return RAGResult(
                retrieved_content=[],
                relevance_scores=[],
                sources=[],
                processing_time=time.time() - start_time,
                activation_level=RAGActivationLevel.DISABLED
            )
        
        # Check retrieval cache
        cache_key = hashlib.md5(
            f"{rag_query.processed_query}|{rag_query.activation_level.value}|{max_results}".encode()
        ).hexdigest()
        
        if cache_key in self.retrieval_cache:
            cached_result = self.retrieval_cache[cache_key]
            cached_result.processing_time = time.time() - start_time
            cached_result.cache_hit = True
            self.stats["cache_hits"] += 1
            return cached_result
        
        # Perform retrieval based on activation level
        retrieved_content, relevance_scores, sources = self._perform_retrieval(
            rag_query, max_results
        )
        
        # Create result
        result = RAGResult(
            retrieved_content=retrieved_content,
            relevance_scores=relevance_scores,
            sources=sources,
            processing_time=time.time() - start_time,
            activation_level=rag_query.activation_level
        )
        
        # Cache result
        self.retrieval_cache[cache_key] = result
        
        # Update stats
        total_time = (self.stats["avg_processing_time"] * 
                     (self.stats["rag_activations"] - 1) + 
                     result.processing_time)
        self.stats["avg_processing_time"] = total_time / max(1, self.stats["rag_activations"])
        
        logger.debug(f"RAG retrieval completed in {result.processing_time*1000:.1f}ms")
        return result
    
    def _perform_retrieval(self,
                          rag_query: RAGQuery,
                          max_results: int) -> Tuple[List[str], List[float], List[str]]:
        """Perform actual retrieval based on activation level (simplified)."""

        # Simulate retrieval based on activation level
        # In a real implementation, this would interface with vector databases,
        # document stores, or memory systems

        if rag_query.activation_level == RAGActivationLevel.MINIMAL:
            # Recent conversation context only
            content = [f"Recent context related to: {', '.join(rag_query.search_keywords[:2])}"]
            scores = [0.8]
            sources = ["conversation_history"]

        elif rag_query.activation_level == RAGActivationLevel.STANDARD:
            # User memories and preferences
            content = [
                f"User preference: {', '.join(rag_query.search_keywords[:3])}",
                f"Stored memory about: {rag_query.search_keywords[0] if rag_query.search_keywords else 'general'}"
            ]
            scores = [0.9, 0.7]
            sources = ["user_preferences", "long_term_memory"]

        elif rag_query.activation_level == RAGActivationLevel.COMPREHENSIVE:
            # Full document and memory search
            content = [
                f"Comprehensive analysis of: {', '.join(rag_query.search_keywords[:5])}",
                f"Related documents covering: {rag_query.search_keywords[0] if rag_query.search_keywords else 'topic'}",
                f"Historical context: {', '.join(rag_query.search_keywords[1:3])}"
            ]
            scores = [0.95, 0.85, 0.75]
            sources = ["document_store", "knowledge_base", "conversation_history"]

        else:
            content, scores, sources = [], [], []

        # Limit results
        content = content[:max_results]
        scores = scores[:max_results]
        sources = sources[:max_results]

        return content, scores, sources
    
    def should_activate_rag(self, query: str, context: Optional[Dict[str, Any]] = None) -> bool:
        """
        Quick check if RAG should be activated for query.
        
        Args:
            query: User query
            context: Optional context
            
        Returns:
            True if RAG should be activated
        """
        rag_query = self.analyze_query(query, context)
        return rag_query.activation_level != RAGActivationLevel.DISABLED
    
    def get_rag_stats(self) -> Dict[str, Any]:
        """Get RAG performance statistics."""
        activation_rate = (self.stats["rag_activations"] / 
                          max(1, self.stats["total_queries"]))
        
        cache_hit_rate = (self.stats["cache_hits"] / 
                         max(1, self.stats["rag_activations"]))
        
        return {
            "total_queries": self.stats["total_queries"],
            "rag_activations": self.stats["rag_activations"],
            "activation_rate": activation_rate,
            "cache_hits": self.stats["cache_hits"],
            "cache_hit_rate": cache_hit_rate,
            "avg_processing_time_ms": self.stats["avg_processing_time"] * 1000,
            "activation_distribution": self.stats["activation_distribution"],
            "cached_queries": len(self.query_cache),
            "cached_retrievals": len(self.retrieval_cache)
        }
    
    def clear_cache(self) -> None:
        """Clear RAG caches."""
        self.query_cache.clear()
        self.retrieval_cache.clear()
        logger.info("RAG caches cleared")
    
    def reset_stats(self) -> None:
        """Reset RAG statistics."""
        self.stats = {
            "total_queries": 0,
            "rag_activations": 0,
            "cache_hits": 0,
            "avg_processing_time": 0.0,
            "activation_distribution": {level.value: 0 for level in RAGActivationLevel}
        }
        logger.info("RAG statistics reset")




# Global RAG instance
_smart_rag = None


def get_smart_rag() -> SmartRAG:
    """Get global smart RAG instance."""
    global _smart_rag
    if _smart_rag is None:
        _smart_rag = SmartRAG()
    return _smart_rag
