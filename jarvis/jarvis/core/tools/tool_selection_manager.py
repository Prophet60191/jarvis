#!/usr/bin/env python3
"""
Tool Selection Manager - Handles intelligent tool selection and filtering.

SEPARATION OF CONCERNS:
- This module ONLY handles tool selection logic
- It does NOT handle query processing, memory, or performance monitoring
- It provides a clean interface for tool selection operations

SINGLE RESPONSIBILITY: Smart tool selection to reduce from 45+ tools to 2-3 relevant tools
"""

import logging
from typing import List, Optional, Dict, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ToolSelectionResult:
    """Result of tool selection process."""
    selected_tools: List[Any]
    selection_reasoning: str
    tools_considered: int
    selection_time_ms: float
    cached: bool = False


class ToolSelectionManager:
    """
    Manages intelligent tool selection for queries.
    
    SINGLE RESPONSIBILITY: Tool selection and filtering only.
    
    Reduces tool overload by selecting only 2-3 most relevant tools
    instead of loading all 45+ tools for every query.
    """
    
    def __init__(self):
        """Initialize tool selection manager."""
        self.all_tools = []
        self.tool_cache = {}
        self.selection_stats = {
            "total_selections": 0,
            "cache_hits": 0,
            "avg_tools_selected": 0.0
        }
        
        logger.info("ToolSelectionManager initialized")
    
    def initialize_tools(self, all_tools: List[Any]) -> None:
        """
        Initialize with all available tools.
        
        Args:
            all_tools: List of all available tools
        """
        self.all_tools = all_tools
        self.tool_cache.clear()  # Clear cache when tools change
        
        logger.info(f"ToolSelectionManager initialized with {len(all_tools)} tools")
    
    def select_tools_for_query(self, 
                              query: str, 
                              max_tools: int = 3,
                              query_complexity: str = "simple") -> ToolSelectionResult:
        """
        Select most relevant tools for a query.
        
        Args:
            query: User query to analyze
            max_tools: Maximum number of tools to select
            query_complexity: Complexity level (instant, simple, complex)
            
        Returns:
            ToolSelectionResult with selected tools and metadata
        """
        import time
        start_time = time.time()
        
        self.selection_stats["total_selections"] += 1
        
        # Check cache first
        cache_key = f"{query.lower()[:50]}_{max_tools}_{query_complexity}"
        if cache_key in self.tool_cache:
            cached_result = self.tool_cache[cache_key]
            cached_result.cached = True
            self.selection_stats["cache_hits"] += 1
            logger.debug(f"Tool selection cache hit for query: {query[:30]}...")
            return cached_result
        
        # Select tools based on query analysis
        selected_tools = self._analyze_and_select_tools(query, max_tools, query_complexity)
        
        selection_time = (time.time() - start_time) * 1000
        
        # Create result
        result = ToolSelectionResult(
            selected_tools=selected_tools,
            selection_reasoning=self._generate_selection_reasoning(query, selected_tools, query_complexity),
            tools_considered=len(self.all_tools),
            selection_time_ms=selection_time,
            cached=False
        )
        
        # Cache result
        self.tool_cache[cache_key] = result
        
        # Update stats
        self._update_selection_stats(len(selected_tools))
        
        logger.debug(f"Selected {len(selected_tools)} tools for query: {query[:30]}... "
                    f"(from {len(self.all_tools)} available)")
        
        return result
    
    def _analyze_and_select_tools(self, 
                                 query: str, 
                                 max_tools: int, 
                                 complexity: str) -> List[Any]:
        """
        Analyze query and select most relevant tools.
        
        Args:
            query: User query
            max_tools: Maximum tools to select
            complexity: Query complexity level
            
        Returns:
            List of selected tools
        """
        if not self.all_tools:
            return []
        
        query_lower = query.lower()
        selected_tools = []
        
        # Priority 1: Memory/RAG tools for remember/recall queries
        if any(word in query_lower for word in ['remember', 'recall', 'what did', 'told you', 'my name', 'favorite']):
            memory_tools = [tool for tool in self.all_tools 
                          if any(keyword in tool.name.lower() 
                                for keyword in ['remember', 'search', 'memory', 'recall'])]
            selected_tools.extend(memory_tools[:2])  # Max 2 memory tools
        
        # Priority 2: Time tools for time queries
        elif any(word in query_lower for word in ['time', 'clock', 'hour', 'minute', 'date']):
            time_tools = [tool for tool in self.all_tools 
                         if any(keyword in tool.name.lower() 
                               for keyword in ['time', 'date', 'clock'])]
            selected_tools.extend(time_tools[:1])  # Max 1 time tool
        
        # Priority 3: File/system tools for file operations
        elif any(word in query_lower for word in ['file', 'read', 'write', 'save', 'open', 'directory']):
            file_tools = [tool for tool in self.all_tools 
                         if any(keyword in tool.name.lower() 
                               for keyword in ['file', 'read', 'write', 'directory', 'filesystem'])]
            selected_tools.extend(file_tools[:2])  # Max 2 file tools
        
        # Priority 4: Web/browser tools for web queries
        elif any(word in query_lower for word in ['web', 'browser', 'website', 'url', 'search online']):
            web_tools = [tool for tool in self.all_tools 
                        if any(keyword in tool.name.lower() 
                              for keyword in ['web', 'browser', 'http', 'url'])]
            selected_tools.extend(web_tools[:2])  # Max 2 web tools
        
        # Default: Select first few general-purpose tools
        else:
            # For general queries, prefer memory and basic tools
            general_tools = [tool for tool in self.all_tools 
                           if any(keyword in tool.name.lower() 
                                 for keyword in ['search', 'remember', 'time'])]
            if not general_tools:
                general_tools = self.all_tools[:3]  # Fallback to first 3 tools
            selected_tools.extend(general_tools[:max_tools])
        
        # Remove duplicates and limit to max_tools
        seen = set()
        unique_tools = []
        for tool in selected_tools:
            if tool.name not in seen:
                seen.add(tool.name)
                unique_tools.append(tool)
                if len(unique_tools) >= max_tools:
                    break
        
        return unique_tools
    
    def _generate_selection_reasoning(self, 
                                    query: str, 
                                    selected_tools: List[Any], 
                                    complexity: str) -> str:
        """Generate human-readable reasoning for tool selection."""
        if not selected_tools:
            return "No tools selected - query can be handled with direct LLM response"
        
        tool_names = [tool.name for tool in selected_tools]
        
        if any('remember' in name.lower() or 'search' in name.lower() for name in tool_names):
            return f"Selected memory tools for recall/storage query: {', '.join(tool_names)}"
        elif any('time' in name.lower() for name in tool_names):
            return f"Selected time tools for temporal query: {', '.join(tool_names)}"
        elif any('file' in name.lower() for name in tool_names):
            return f"Selected file tools for file operation: {', '.join(tool_names)}"
        else:
            return f"Selected general tools for {complexity} query: {', '.join(tool_names)}"
    
    def _update_selection_stats(self, tools_selected: int) -> None:
        """Update selection statistics."""
        total = self.selection_stats["total_selections"]
        current_avg = self.selection_stats["avg_tools_selected"]
        
        # Calculate new average
        new_avg = ((current_avg * (total - 1)) + tools_selected) / total
        self.selection_stats["avg_tools_selected"] = new_avg
    
    def get_selection_stats(self) -> Dict[str, Any]:
        """Get tool selection statistics."""
        stats = self.selection_stats.copy()
        if stats["total_selections"] > 0:
            stats["cache_hit_rate"] = stats["cache_hits"] / stats["total_selections"]
        else:
            stats["cache_hit_rate"] = 0.0
        
        return stats
    
    def clear_cache(self) -> None:
        """Clear tool selection cache."""
        self.tool_cache.clear()
        logger.info("Tool selection cache cleared")


# Singleton instance for global access
_tool_selection_manager = None


def get_tool_selection_manager() -> ToolSelectionManager:
    """
    Get singleton tool selection manager instance.
    
    Returns:
        ToolSelectionManager instance
    """
    global _tool_selection_manager
    if _tool_selection_manager is None:
        _tool_selection_manager = ToolSelectionManager()
    return _tool_selection_manager
