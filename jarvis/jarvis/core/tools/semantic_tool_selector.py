"""
Semantic Tool Selector for Jarvis Voice Assistant

Intelligently selects 2-3 semantically relevant tools per query instead of
loading all 60+ tools, using pre-computed embeddings and similarity matching.
"""

import time
import logging
import re
from typing import Dict, List, Optional, Tuple, Set, Any
from dataclasses import dataclass
from collections import defaultdict
import hashlib

logger = logging.getLogger(__name__)


@dataclass
class ToolMetadata:
    """Metadata for tool selection."""
    name: str
    description: str
    keywords: Set[str]
    category: str
    usage_frequency: int = 0
    last_used: float = 0.0
    success_rate: float = 1.0


@dataclass
class ToolSelection:
    """Result of tool selection process."""
    selected_tools: List[str]
    confidence_scores: Dict[str, float]
    selection_reasoning: str
    processing_time: float
    cached: bool = False


class SemanticToolSelector:
    """
    Semantic tool selector using keyword matching and usage patterns.
    
    Reduces tool loading from 60+ tools to 2-3 most relevant tools per query
    using intelligent selection based on:
    - Keyword matching between query and tool descriptions
    - Historical usage patterns and success rates
    - Tool category relevance
    - Query complexity and context
    """
    
    def __init__(self):
        """Initialize semantic tool selector."""
        self.tool_metadata: Dict[str, ToolMetadata] = {}
        self.tool_categories = self._initialize_categories()
        self.selection_cache = {}
        self.usage_stats = {
            "total_selections": 0,
            "cache_hits": 0,
            "avg_selection_time": 0.0,
            "tools_selected_distribution": defaultdict(int)
        }
        
        # Initialize with common tools
        self._initialize_common_tools()
        
        logger.info("SemanticToolSelector initialized")
    
    def _initialize_categories(self) -> Dict[str, List[str]]:
        """Initialize tool categories for semantic grouping."""
        return {
            "time": ["get_current_time", "datetime", "calendar"],
            "memory": ["remember_fact", "search_long_term_memory", "rag"],
            "code": ["execute_code", "analyze_file", "create_script", "aider"],
            "web": ["web_automation_task", "web_scraping", "lavague"],
            "files": ["filesystem", "file_operations", "directory"],
            "system": ["system_task", "process_management", "monitoring"],
            "communication": ["email", "messaging", "notifications"],
            "data": ["analyze_data", "csv_processing", "json_operations"],
            "testing": ["robot_framework", "run_tests", "validation"],
            "ai": ["llm_operations", "text_processing", "nlp"]
        }
    
    def _initialize_common_tools(self) -> None:
        """Initialize metadata for common tools."""
        common_tools = [
            # Time tools
            ToolMetadata(
                name="get_current_time",
                description="Get current time, date, and datetime information",
                keywords={"time", "date", "datetime", "current", "now", "today", "clock"},
                category="time"
            ),
            
            # Memory tools
            ToolMetadata(
                name="remember_fact",
                description="Store information in long-term memory for future recall",
                keywords={"remember", "save", "store", "memory", "fact", "information"},
                category="memory"
            ),
            ToolMetadata(
                name="search_long_term_memory",
                description="Search stored memories and information from previous conversations",
                keywords={"search", "memory", "recall", "find", "remember", "previous", "stored"},
                category="memory"
            ),
            
            # Code execution tools
            ToolMetadata(
                name="execute_code",
                description="Execute Python code for calculations, data processing, and automation",
                keywords={"code", "execute", "run", "python", "calculate", "compute", "script"},
                category="code"
            ),
            ToolMetadata(
                name="analyze_file",
                description="Analyze CSV, JSON, Excel, text, and other data files",
                keywords={"analyze", "file", "csv", "json", "excel", "data", "process"},
                category="data"
            ),
            ToolMetadata(
                name="create_script",
                description="Generate Python, JavaScript, Bash scripts for automation",
                keywords={"create", "script", "generate", "automation", "python", "javascript", "bash"},
                category="code"
            ),
            
            # System tools
            ToolMetadata(
                name="system_task",
                description="System monitoring, disk usage, process management, file organization",
                keywords={"system", "monitor", "disk", "process", "file", "organization", "cleanup"},
                category="system"
            ),
            
            # Web tools
            ToolMetadata(
                name="web_automation_task",
                description="AI-powered web interactions, scraping, and form filling",
                keywords={"web", "website", "scrape", "automation", "browser", "form", "internet"},
                category="web"
            ),
            
            # File operations
            ToolMetadata(
                name="filesystem",
                description="File and directory operations, reading, writing, listing",
                keywords={"file", "directory", "folder", "read", "write", "list", "filesystem"},
                category="files"
            )
        ]
        
        for tool in common_tools:
            self.tool_metadata[tool.name] = tool
    
    def register_tool(self, 
                     name: str, 
                     description: str, 
                     category: str = "general",
                     keywords: Optional[Set[str]] = None) -> None:
        """
        Register a new tool for selection.
        
        Args:
            name: Tool name
            description: Tool description
            category: Tool category
            keywords: Optional custom keywords
        """
        if keywords is None:
            keywords = self._extract_keywords(description)
        
        self.tool_metadata[name] = ToolMetadata(
            name=name,
            description=description,
            keywords=keywords,
            category=category
        )
        
        logger.debug(f"Registered tool: {name} in category {category}")
    
    def select_tools(self, 
                    query: str, 
                    max_tools: int = 3,
                    context: Optional[Dict[str, Any]] = None) -> ToolSelection:
        """
        Select most relevant tools for query.
        
        Args:
            query: User query to analyze
            max_tools: Maximum number of tools to select
            context: Optional context for selection
            
        Returns:
            ToolSelection with selected tools and metadata
        """
        start_time = time.time()
        self.usage_stats["total_selections"] += 1
        
        if not query.strip():
            return ToolSelection(
                selected_tools=[],
                confidence_scores={},
                selection_reasoning="Empty query",
                processing_time=time.time() - start_time
            )
        
        # Check cache first
        cache_key = self._get_cache_key(query, max_tools, context)
        if cache_key in self.selection_cache:
            cached_result = self.selection_cache[cache_key]
            cached_result.processing_time = time.time() - start_time
            cached_result.cached = True
            self.usage_stats["cache_hits"] += 1
            return cached_result
        
        # Extract query keywords
        query_keywords = self._extract_keywords(query)
        
        # Score all tools
        tool_scores = self._score_tools(query, query_keywords, context)
        
        # Select top tools
        selected_tools = self._select_top_tools(tool_scores, max_tools)
        
        # Generate reasoning
        reasoning = self._generate_reasoning(query, selected_tools, tool_scores)
        
        # Create result
        result = ToolSelection(
            selected_tools=selected_tools,
            confidence_scores={tool: tool_scores[tool] for tool in selected_tools},
            selection_reasoning=reasoning,
            processing_time=time.time() - start_time
        )
        
        # Cache result
        self.selection_cache[cache_key] = result
        
        # Update statistics
        for tool in selected_tools:
            self.usage_stats["tools_selected_distribution"][tool] += 1
        
        # Update average selection time
        total_time = (self.usage_stats["avg_selection_time"] * 
                     (self.usage_stats["total_selections"] - 1) + 
                     result.processing_time)
        self.usage_stats["avg_selection_time"] = total_time / self.usage_stats["total_selections"]
        
        logger.debug(f"Selected {len(selected_tools)} tools in {result.processing_time*1000:.1f}ms")
        return result
    
    def _score_tools(self, 
                    query: str, 
                    query_keywords: Set[str], 
                    context: Optional[Dict[str, Any]]) -> Dict[str, float]:
        """Score all tools based on relevance to query."""
        scores = {}
        query_lower = query.lower()
        
        for tool_name, metadata in self.tool_metadata.items():
            score = 0.0
            
            # Keyword matching score (0-0.6)
            keyword_matches = len(query_keywords.intersection(metadata.keywords))
            if keyword_matches > 0:
                score += min(0.6, keyword_matches * 0.2)
            
            # Description similarity score (0-0.3)
            desc_lower = metadata.description.lower()
            for keyword in query_keywords:
                if keyword in desc_lower:
                    score += 0.1
            
            # Direct name/category mention (0-0.4)
            if tool_name.lower() in query_lower:
                score += 0.4
            elif metadata.category in query_lower:
                score += 0.2
            
            # Usage frequency bonus (0-0.1)
            if metadata.usage_frequency > 0:
                frequency_bonus = min(0.1, metadata.usage_frequency / 100)
                score += frequency_bonus
            
            # Success rate bonus (0-0.1)
            success_bonus = metadata.success_rate * 0.1
            score += success_bonus
            
            # Recency bonus (0-0.05)
            if metadata.last_used > 0:
                hours_since_use = (time.time() - metadata.last_used) / 3600
                recency_bonus = max(0, 0.05 * (1 - hours_since_use / 24))  # Decay over 24 hours
                score += recency_bonus
            
            # Context-based adjustments
            if context:
                score = self._apply_context_adjustments(score, tool_name, metadata, context)
            
            scores[tool_name] = min(1.0, score)  # Cap at 1.0
        
        return scores
    
    def _apply_context_adjustments(self, 
                                  score: float, 
                                  tool_name: str, 
                                  metadata: ToolMetadata, 
                                  context: Dict[str, Any]) -> float:
        """Apply context-based score adjustments."""
        
        # Query complexity adjustments
        if "complexity" in context:
            complexity = context["complexity"]
            if complexity == "instant" and metadata.category in ["time", "memory"]:
                score *= 1.2  # Boost simple tools for instant queries
            elif complexity == "complex" and metadata.category in ["code", "web", "system"]:
                score *= 1.3  # Boost complex tools for complex queries
        
        # Time-based adjustments
        if "time_sensitive" in context and context["time_sensitive"]:
            if metadata.category == "time":
                score *= 1.5
        
        # Previous tool usage in conversation
        if "recent_tools" in context:
            recent_tools = context["recent_tools"]
            if tool_name in recent_tools:
                score *= 0.8  # Slightly reduce recently used tools for variety
        
        return score
    
    def _select_top_tools(self, tool_scores: Dict[str, float], max_tools: int) -> List[str]:
        """Select top scoring tools with diversity."""
        if not tool_scores:
            return []
        
        # Sort by score
        sorted_tools = sorted(tool_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Select top tools with category diversity
        selected = []
        used_categories = set()
        
        # First pass: select highest scoring tools from different categories
        for tool_name, score in sorted_tools:
            if len(selected) >= max_tools:
                break
            
            if score < 0.1:  # Minimum relevance threshold
                continue
            
            metadata = self.tool_metadata[tool_name]
            if metadata.category not in used_categories or len(selected) == 0:
                selected.append(tool_name)
                used_categories.add(metadata.category)
        
        # Second pass: fill remaining slots with highest scoring tools
        for tool_name, score in sorted_tools:
            if len(selected) >= max_tools:
                break
            
            if tool_name not in selected and score >= 0.1:
                selected.append(tool_name)
        
        return selected[:max_tools]
    
    def _generate_reasoning(self, 
                           query: str, 
                           selected_tools: List[str], 
                           tool_scores: Dict[str, float]) -> str:
        """Generate human-readable reasoning for tool selection."""
        if not selected_tools:
            return "No relevant tools found for query"
        
        reasoning_parts = []
        
        for tool in selected_tools:
            score = tool_scores[tool]
            metadata = self.tool_metadata[tool]
            
            if score > 0.7:
                confidence = "high"
            elif score > 0.4:
                confidence = "medium"
            else:
                confidence = "low"
            
            reasoning_parts.append(f"{tool} ({confidence} relevance, {metadata.category} category)")
        
        return f"Selected {len(selected_tools)} tools: " + ", ".join(reasoning_parts)
    
    def _extract_keywords(self, text: str) -> Set[str]:
        """Extract keywords from text."""
        # Simple keyword extraction
        text_lower = text.lower()
        
        # Remove common stop words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have',
            'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should',
            'can', 'may', 'might', 'must', 'i', 'you', 'he', 'she', 'it', 'we',
            'they', 'me', 'him', 'her', 'us', 'them'
        }
        
        # Extract words (alphanumeric, 3+ characters)
        words = re.findall(r'\b[a-zA-Z0-9]{3,}\b', text_lower)
        keywords = {word for word in words if word not in stop_words}
        
        return keywords
    
    def _get_cache_key(self, 
                      query: str, 
                      max_tools: int, 
                      context: Optional[Dict[str, Any]]) -> str:
        """Generate cache key for tool selection."""
        context_str = str(sorted(context.items())) if context else ""
        combined = f"{query}|{max_tools}|{context_str}"
        return hashlib.md5(combined.encode()).hexdigest()
    
    def update_tool_usage(self, tool_name: str, success: bool = True) -> None:
        """Update tool usage statistics."""
        if tool_name in self.tool_metadata:
            metadata = self.tool_metadata[tool_name]
            metadata.usage_frequency += 1
            metadata.last_used = time.time()
            
            # Update success rate (exponential moving average)
            alpha = 0.1  # Learning rate
            if success:
                metadata.success_rate = metadata.success_rate * (1 - alpha) + alpha
            else:
                metadata.success_rate = metadata.success_rate * (1 - alpha)
    
    def get_selection_stats(self) -> Dict[str, Any]:
        """Get tool selection statistics."""
        cache_hit_rate = (self.usage_stats["cache_hits"] / 
                         max(1, self.usage_stats["total_selections"]))
        
        return {
            "total_selections": self.usage_stats["total_selections"],
            "cache_hits": self.usage_stats["cache_hits"],
            "cache_hit_rate": cache_hit_rate,
            "avg_selection_time_ms": self.usage_stats["avg_selection_time"] * 1000,
            "registered_tools": len(self.tool_metadata),
            "cached_selections": len(self.selection_cache),
            "most_selected_tools": dict(sorted(
                self.usage_stats["tools_selected_distribution"].items(),
                key=lambda x: x[1], reverse=True
            )[:10])
        }
    
    def clear_cache(self) -> None:
        """Clear selection cache."""
        self.selection_cache.clear()
        logger.info("Tool selection cache cleared")


# Global selector instance
_tool_selector = None


def get_semantic_tool_selector() -> SemanticToolSelector:
    """Get global semantic tool selector instance."""
    global _tool_selector
    if _tool_selector is None:
        _tool_selector = SemanticToolSelector()
    return _tool_selector
