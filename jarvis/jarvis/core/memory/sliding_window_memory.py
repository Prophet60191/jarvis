"""
Context Window Optimizer for Jarvis Voice Assistant

Provides relevance-based context selection and compression system to optimize
context windows from unlimited to 800 tokens maximum with intelligent prioritization.
"""

import time
import logging
import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Any
from collections import deque
from enum import Enum

logger = logging.getLogger(__name__)


class ContextPriority(Enum):
    """Context priority levels for relevance scoring."""
    CRITICAL = 5    # Current query context, user preferences
    HIGH = 4        # Recent conversation, active topics
    MEDIUM = 3      # Related topics, tool results
    LOW = 2         # Background information
    MINIMAL = 1     # Filler content, old exchanges


@dataclass
class ContextEntry:
    """Context entry with relevance scoring."""
    content: str
    timestamp: float
    priority: ContextPriority
    relevance_score: float
    token_count: int
    entry_type: str  # 'user_input', 'assistant_response', 'system_info', 'tool_result'
    keywords: List[str]
    
    def age_penalty(self) -> float:
        """Calculate age penalty (newer content is more relevant)."""
        age_hours = (time.time() - self.timestamp) / 3600
        # Exponential decay: 100% relevance at 0 hours, 50% at 2 hours, 25% at 4 hours
        return max(0.1, 1.0 / (1.0 + age_hours / 2.0))
    
    def get_weighted_score(self) -> float:
        """Get relevance score weighted by priority and age."""
        age_factor = self.age_penalty()
        priority_factor = self.priority.value / 5.0
        return self.relevance_score * priority_factor * age_factor


class SlidingWindowMemory:
    """
    Sliding window memory with intelligent context compression.
    
    Maintains conversation context within 800 token limit using:
    - Relevance scoring based on keyword matching
    - Priority-based selection (user preferences > recent exchanges > background)
    - Age-based decay (newer content prioritized)
    - Semantic compression (summarization of old content)
    """
    
    def __init__(self, 
                 max_tokens: int = 800,
                 max_entries: int = 50,
                 compression_threshold: float = 0.8):
        """
        Initialize sliding window memory.
        
        Args:
            max_tokens: Maximum token count for context window
            max_entries: Maximum number of context entries
            compression_threshold: Trigger compression when this ratio of max_tokens is reached
        """
        self.max_tokens = max_tokens
        self.max_entries = max_entries
        self.compression_threshold = compression_threshold
        
        # Context storage
        self.context_entries: deque[ContextEntry] = deque(maxlen=max_entries)
        self.current_token_count = 0
        
        # Keyword tracking for relevance scoring
        self.active_keywords: Dict[str, float] = {}  # keyword -> importance score
        self.keyword_decay_rate = 0.95  # Keywords decay over time
        
        # Compression history
        self.compressed_summaries: List[str] = []
        
        logger.info(f"SlidingWindowMemory initialized: max_tokens={max_tokens}, "
                   f"max_entries={max_entries}")
    
    def add_context(self, 
                   content: str, 
                   entry_type: str,
                   priority: ContextPriority = ContextPriority.MEDIUM,
                   keywords: Optional[List[str]] = None) -> None:
        """
        Add new context entry with relevance scoring.
        
        Args:
            content: Context content to add
            entry_type: Type of entry ('user_input', 'assistant_response', etc.)
            priority: Priority level for this entry
            keywords: Optional keywords for relevance scoring
        """
        if not content.strip():
            return
        
        # Extract keywords if not provided
        if keywords is None:
            keywords = self._extract_keywords(content)
        
        # Calculate token count (rough approximation)
        token_count = self._estimate_tokens(content)
        
        # Calculate relevance score
        relevance_score = self._calculate_relevance(content, keywords)
        
        # Create context entry
        entry = ContextEntry(
            content=content.strip(),
            timestamp=time.time(),
            priority=priority,
            relevance_score=relevance_score,
            token_count=token_count,
            entry_type=entry_type,
            keywords=keywords
        )
        
        # Add to context
        self.context_entries.append(entry)
        self.current_token_count += token_count
        
        # Update active keywords
        self._update_keywords(keywords)
        
        # Check if compression is needed
        if self.current_token_count > self.max_tokens * self.compression_threshold:
            self._compress_context()
        
        logger.debug(f"Added context entry: {entry_type} ({token_count} tokens, "
                    f"relevance: {relevance_score:.2f})")
    
    def get_optimized_context(self, 
                            current_query: str = "",
                            max_tokens: Optional[int] = None) -> str:
        """
        Get optimized context within token limit.
        
        Args:
            current_query: Current user query for relevance boosting
            max_tokens: Override default max tokens
            
        Returns:
            Optimized context string within token limit
        """
        target_tokens = max_tokens or self.max_tokens
        
        # Boost relevance for entries related to current query
        if current_query:
            query_keywords = self._extract_keywords(current_query)
            self._boost_query_relevance(query_keywords)
        
        # Sort entries by weighted relevance score
        sorted_entries = sorted(
            self.context_entries,
            key=lambda e: e.get_weighted_score(),
            reverse=True
        )
        
        # Select entries within token limit
        selected_entries = []
        token_count = 0
        
        # Always include compressed summaries first (if any)
        context_parts = []
        if self.compressed_summaries:
            summary_text = " ".join(self.compressed_summaries[-2:])  # Last 2 summaries
            summary_tokens = self._estimate_tokens(summary_text)
            if summary_tokens < target_tokens * 0.3:  # Max 30% for summaries
                context_parts.append(f"[Previous context: {summary_text}]")
                token_count += summary_tokens
        
        # Add high-priority entries
        for entry in sorted_entries:
            if token_count + entry.token_count <= target_tokens:
                selected_entries.append(entry)
                token_count += entry.token_count
            elif entry.priority == ContextPriority.CRITICAL:
                # Always include critical entries, even if over limit
                selected_entries.append(entry)
                token_count += entry.token_count
                break
        
        # Sort selected entries by timestamp for chronological order
        selected_entries.sort(key=lambda e: e.timestamp)
        
        # Build context string
        for entry in selected_entries:
            if entry.entry_type == 'user_input':
                context_parts.append(f"User: {entry.content}")
            elif entry.entry_type == 'assistant_response':
                context_parts.append(f"Assistant: {entry.content}")
            elif entry.entry_type == 'system_info':
                context_parts.append(f"[System: {entry.content}]")
            elif entry.entry_type == 'tool_result':
                context_parts.append(f"[Tool result: {entry.content}]")
            else:
                context_parts.append(entry.content)
        
        optimized_context = "\n".join(context_parts)
        
        logger.debug(f"Generated optimized context: {len(selected_entries)} entries, "
                    f"{token_count} tokens")
        
        return optimized_context
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text for relevance scoring."""
        # Simple keyword extraction (can be enhanced with NLP)
        text_lower = text.lower()
        
        # Remove common stop words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have',
            'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should',
            'can', 'may', 'might', 'must', 'i', 'you', 'he', 'she', 'it', 'we',
            'they', 'me', 'him', 'her', 'us', 'them', 'my', 'your', 'his', 'her',
            'its', 'our', 'their', 'this', 'that', 'these', 'those'
        }
        
        # Extract words (alphanumeric, 3+ characters)
        words = re.findall(r'\b[a-zA-Z0-9]{3,}\b', text_lower)
        keywords = [word for word in words if word not in stop_words]
        
        # Return unique keywords, limited to top 10
        return list(dict.fromkeys(keywords))[:10]
    
    def _calculate_relevance(self, content: str, keywords: List[str]) -> float:
        """Calculate relevance score based on keyword matching."""
        if not keywords:
            return 0.5  # Default relevance
        
        relevance = 0.0
        content_lower = content.lower()
        
        for keyword in keywords:
            if keyword in self.active_keywords:
                # Boost score for active keywords
                keyword_importance = self.active_keywords[keyword]
                if keyword in content_lower:
                    relevance += keyword_importance
                    
        # Normalize by number of keywords
        if keywords:
            relevance = min(1.0, relevance / len(keywords))
        
        return max(0.1, relevance)  # Minimum relevance of 0.1
    
    def _update_keywords(self, keywords: List[str]) -> None:
        """Update active keywords with decay."""
        # Decay existing keywords
        for keyword in list(self.active_keywords.keys()):
            self.active_keywords[keyword] *= self.keyword_decay_rate
            if self.active_keywords[keyword] < 0.1:
                del self.active_keywords[keyword]
        
        # Add/boost new keywords
        for keyword in keywords:
            if keyword in self.active_keywords:
                self.active_keywords[keyword] = min(1.0, self.active_keywords[keyword] + 0.3)
            else:
                self.active_keywords[keyword] = 0.5
    
    def _boost_query_relevance(self, query_keywords: List[str]) -> None:
        """Boost relevance for entries matching current query keywords."""
        for entry in self.context_entries:
            boost = 0.0
            for keyword in query_keywords:
                if keyword in entry.keywords or keyword in entry.content.lower():
                    boost += 0.2
            
            if boost > 0:
                entry.relevance_score = min(1.0, entry.relevance_score + boost)
    
    def _compress_context(self) -> None:
        """Compress old context entries to free up token space."""
        if len(self.context_entries) < 10:
            return  # Not enough entries to compress
        
        # Find entries to compress (oldest 30% with low relevance)
        sorted_by_age = sorted(self.context_entries, key=lambda e: e.timestamp)
        compress_count = max(3, len(sorted_by_age) // 3)
        
        entries_to_compress = []
        for entry in sorted_by_age[:compress_count]:
            if entry.get_weighted_score() < 0.3:  # Low relevance threshold
                entries_to_compress.append(entry)
        
        if not entries_to_compress:
            return
        
        # Create summary of compressed entries
        compressed_content = []
        tokens_freed = 0
        
        for entry in entries_to_compress:
            # Simple compression: keep key information
            if entry.entry_type == 'user_input':
                compressed_content.append(f"User asked about {', '.join(entry.keywords[:3])}")
            elif entry.entry_type == 'assistant_response':
                compressed_content.append(f"Discussed {', '.join(entry.keywords[:3])}")
            
            tokens_freed += entry.token_count
            self.context_entries.remove(entry)
        
        if compressed_content:
            summary = "; ".join(compressed_content)
            self.compressed_summaries.append(summary)
            
            # Keep only last 5 summaries
            if len(self.compressed_summaries) > 5:
                self.compressed_summaries = self.compressed_summaries[-5:]
        
        self.current_token_count -= tokens_freed
        
        logger.info(f"Compressed {len(entries_to_compress)} entries, freed {tokens_freed} tokens")
    
    def _estimate_tokens(self, text: str) -> int:
        """Rough token count estimation (1 token ≈ 4 characters)."""
        return max(1, len(text) // 4)
    
    def clear_context(self) -> None:
        """Clear all context entries."""
        self.context_entries.clear()
        self.current_token_count = 0
        self.active_keywords.clear()
        self.compressed_summaries.clear()
        logger.info("Context cleared")
    
    def get_context_stats(self) -> Dict[str, Any]:
        """Get context statistics."""
        return {
            "total_entries": len(self.context_entries),
            "current_tokens": self.current_token_count,
            "max_tokens": self.max_tokens,
            "utilization": self.current_token_count / self.max_tokens,
            "active_keywords": len(self.active_keywords),
            "compressed_summaries": len(self.compressed_summaries),
            "priority_distribution": {
                priority.name: sum(1 for e in self.context_entries if e.priority == priority)
                for priority in ContextPriority
            }
        }


# Global memory instance
_memory_instance = None


def get_sliding_window_memory() -> SlidingWindowMemory:
    """Get the global sliding window memory instance."""
    global _memory_instance
    if _memory_instance is None:
        _memory_instance = SlidingWindowMemory()
    return _memory_instance
