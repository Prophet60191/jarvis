"""
Tool Service Layer - Clean abstraction for tool selection and execution.

This service provides a unified interface for tool management, following
proper separation of concerns and dependency injection patterns.
"""

import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ToolSelectionResult:
    """Result of tool selection operation."""
    tools: List[Any]
    selection_method: str
    reasoning: str
    performance_notes: List[str]


class ToolService(ABC):
    """Abstract interface for tool operations."""
    
    @abstractmethod
    async def select_tools(self, query: str, complexity: str) -> ToolSelectionResult:
        """Select appropriate tools for a query."""
        pass
    
    @abstractmethod
    def get_available_tools(self) -> List[Any]:
        """Get all available tools."""
        pass
    
    @abstractmethod
    def get_tool_stats(self) -> Dict[str, Any]:
        """Get tool usage statistics."""
        pass


class JarvisToolService(ToolService):
    """
    Concrete implementation of tool service using existing tool selection
    and management systems.
    
    This maintains backward compatibility while providing clean abstraction.
    """
    
    def __init__(self):
        """Initialize tool service with lazy loading."""
        self._tool_selection_manager = None
        self._semantic_tool_selector = None
        self._initialized = False
        
        logger.info("JarvisToolService initialized with lazy loading")
    
    def _ensure_initialized(self):
        """Ensure tool managers are initialized (lazy loading)."""
        if self._initialized:
            return
        
        try:
            from .tool_selection_manager import get_tool_selection_manager
            from .semantic_tool_selector import get_semantic_tool_selector
            
            self._tool_selection_manager = get_tool_selection_manager()
            self._semantic_tool_selector = get_semantic_tool_selector()
            
            self._initialized = True
            logger.info("Tool managers initialized successfully in tool service")
            
        except Exception as e:
            logger.error(f"Failed to initialize tool managers: {e}")
            raise
    
    async def select_tools(self, query: str, complexity: str) -> ToolSelectionResult:
        """Select appropriate tools for a query using existing managers."""
        try:
            self._ensure_initialized()
            
            # Use existing tool selection logic
            if hasattr(self._tool_selection_manager, 'select_tools'):
                result = self._tool_selection_manager.select_tools(query, complexity)

                # Handle different return types
                if isinstance(result, tuple) and len(result) >= 3:
                    tools, selection_method, reasoning = result[:3]
                elif hasattr(result, 'tools'):
                    tools = result.tools
                    selection_method = getattr(result, 'selection_method', 'manager_selection')
                    reasoning = getattr(result, 'reasoning', 'Tool selection completed')
                else:
                    tools = result if isinstance(result, list) else []
                    selection_method = 'manager_selection'
                    reasoning = 'Tool selection completed'

                return ToolSelectionResult(
                    tools=tools,
                    selection_method=selection_method,
                    reasoning=reasoning,
                    performance_notes=[]
                )
            else:
                # Fallback to semantic selector
                tools = self._semantic_tool_selector.select_tools(query, max_tools=3)
                
                return ToolSelectionResult(
                    tools=tools,
                    selection_method="semantic_fallback",
                    reasoning="Used semantic tool selector as fallback",
                    performance_notes=["Fallback method used"]
                )
                
        except Exception as e:
            logger.error(f"Failed to select tools: {e}")
            # Return empty result as fallback
            return ToolSelectionResult(
                tools=[],
                selection_method="error_fallback",
                reasoning=f"Tool selection failed: {str(e)}",
                performance_notes=[f"Error: {str(e)}"]
            )
    
    def get_available_tools(self) -> List[Any]:
        """Get all available tools."""
        try:
            self._ensure_initialized()
            
            if hasattr(self._semantic_tool_selector, 'get_all_tools'):
                return self._semantic_tool_selector.get_all_tools()
            else:
                # Fallback to empty list
                logger.warning("No method to get available tools")
                return []
                
        except Exception as e:
            logger.error(f"Failed to get available tools: {e}")
            return []
    
    def get_tool_stats(self) -> Dict[str, Any]:
        """Get tool usage statistics."""
        try:
            self._ensure_initialized()
            
            stats = {}
            
            if hasattr(self._tool_selection_manager, 'get_selection_stats'):
                stats.update(self._tool_selection_manager.get_selection_stats())
            
            if hasattr(self._semantic_tool_selector, 'get_stats'):
                stats.update(self._semantic_tool_selector.get_stats())
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get tool stats: {e}")
            return {"error": str(e)}


# Factory function for dependency injection
_tool_service_instance = None

def get_tool_service() -> ToolService:
    """Get the tool service instance (singleton)."""
    global _tool_service_instance
    if _tool_service_instance is None:
        _tool_service_instance = JarvisToolService()
    return _tool_service_instance
