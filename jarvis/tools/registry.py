"""
Tool registry for Jarvis Voice Assistant.

This module provides a centralized registry for managing tools,
including registration, discovery, and LangChain integration.
"""

import logging
from typing import Dict, List, Optional, Type, Any
# LangChain tools are now created using the @tool decorator

from ..exceptions import ToolRegistrationError, ToolError
from .base import BaseTool, create_langchain_tool


logger = logging.getLogger(__name__)


class ToolRegistry:
    """
    Central registry for managing Jarvis tools.
    
    This class provides tool registration, discovery, and management
    functionality with proper error handling and validation.
    """
    
    def __init__(self):
        """Initialize the tool registry."""
        self._tools: Dict[str, BaseTool] = {}
        self._tool_classes: Dict[str, Type[BaseTool]] = {}
        
        logger.info("ToolRegistry initialized")
    
    def register(self, tool: BaseTool) -> None:
        """
        Register a tool instance.
        
        Args:
            tool: Tool instance to register
            
        Raises:
            ToolRegistrationError: If registration fails
        """
        try:
            if not isinstance(tool, BaseTool):
                raise ToolRegistrationError(
                    f"Tool must be an instance of BaseTool, got {type(tool)}",
                    tool_name=getattr(tool, 'name', 'unknown')
                )
            
            if tool.name in self._tools:
                logger.warning(f"Tool '{tool.name}' already registered, replacing")
            
            self._tools[tool.name] = tool
            logger.info(f"Registered tool: {tool.name}")
            
        except Exception as e:
            error_msg = f"Failed to register tool: {str(e)}"
            logger.error(error_msg)
            raise ToolRegistrationError(error_msg, tool_name=getattr(tool, 'name', 'unknown')) from e
    
    def register_class(self, tool_class: Type[BaseTool], name: Optional[str] = None) -> None:
        """
        Register a tool class for lazy instantiation.
        
        Args:
            tool_class: Tool class to register
            name: Optional name override (uses class name if None)
            
        Raises:
            ToolRegistrationError: If registration fails
        """
        try:
            if not issubclass(tool_class, BaseTool):
                raise ToolRegistrationError(
                    f"Tool class must be a subclass of BaseTool, got {tool_class}",
                    tool_name=name or tool_class.__name__
                )
            
            class_name = name or tool_class.__name__
            
            if class_name in self._tool_classes:
                logger.warning(f"Tool class '{class_name}' already registered, replacing")
            
            self._tool_classes[class_name] = tool_class
            logger.info(f"Registered tool class: {class_name}")
            
        except Exception as e:
            error_msg = f"Failed to register tool class: {str(e)}"
            logger.error(error_msg)
            raise ToolRegistrationError(error_msg, tool_name=name or 'unknown') from e
    
    def unregister(self, tool_name: str) -> bool:
        """
        Unregister a tool.
        
        Args:
            tool_name: Name of the tool to unregister
            
        Returns:
            True if tool was unregistered, False if not found
        """
        removed = False
        
        if tool_name in self._tools:
            del self._tools[tool_name]
            logger.info(f"Unregistered tool: {tool_name}")
            removed = True
        
        if tool_name in self._tool_classes:
            del self._tool_classes[tool_name]
            logger.info(f"Unregistered tool class: {tool_name}")
            removed = True
        
        if not removed:
            logger.warning(f"Tool '{tool_name}' not found for unregistration")
        
        return removed
    
    def get_tool(self, tool_name: str) -> Optional[BaseTool]:
        """
        Get a tool by name.
        
        Args:
            tool_name: Name of the tool to retrieve
            
        Returns:
            Tool instance or None if not found
        """
        # First check registered instances
        if tool_name in self._tools:
            return self._tools[tool_name]
        
        # Then check registered classes and instantiate if found
        if tool_name in self._tool_classes:
            try:
                tool_class = self._tool_classes[tool_name]
                tool_instance = tool_class()
                
                # Register the instance for future use
                self._tools[tool_name] = tool_instance
                logger.debug(f"Instantiated tool from class: {tool_name}")
                
                return tool_instance
                
            except Exception as e:
                logger.error(f"Failed to instantiate tool '{tool_name}': {str(e)}")
                return None
        
        logger.debug(f"Tool not found: {tool_name}")
        return None
    
    def has_tool(self, tool_name: str) -> bool:
        """
        Check if a tool is registered.
        
        Args:
            tool_name: Name of the tool to check
            
        Returns:
            True if tool is registered, False otherwise
        """
        return tool_name in self._tools or tool_name in self._tool_classes
    
    def list_tools(self, enabled_only: bool = False) -> List[str]:
        """
        List all registered tool names.
        
        Args:
            enabled_only: If True, only return enabled tools
            
        Returns:
            List of tool names
        """
        tool_names = set()
        
        # Add instance names
        for name, tool in self._tools.items():
            if not enabled_only or tool.is_enabled():
                tool_names.add(name)
        
        # Add class names (assume enabled since we can't check without instantiation)
        if not enabled_only:
            tool_names.update(self._tool_classes.keys())
        
        return sorted(list(tool_names))
    
    def get_all_tools(self, enabled_only: bool = False) -> List[BaseTool]:
        """
        Get all registered tools.
        
        Args:
            enabled_only: If True, only return enabled tools
            
        Returns:
            List of tool instances
        """
        tools = []
        
        for tool_name in self.list_tools(enabled_only=False):
            tool = self.get_tool(tool_name)
            if tool and (not enabled_only or tool.is_enabled()):
                tools.append(tool)
        
        return tools
    
    def get_langchain_tools(self, enabled_only: bool = True) -> List[Any]:
        """
        Get all tools as LangChain-compatible tools.
        
        Args:
            enabled_only: If True, only return enabled tools
            
        Returns:
            List of LangChain-compatible tools
        """
        langchain_tools = []
        
        for tool in self.get_all_tools(enabled_only=enabled_only):
            try:
                langchain_tool = create_langchain_tool(tool)
                langchain_tools.append(langchain_tool)
            except Exception as e:
                logger.error(f"Failed to create LangChain tool for '{tool.name}': {str(e)}")
        
        return langchain_tools
    
    def enable_tool(self, tool_name: str) -> bool:
        """
        Enable a tool.
        
        Args:
            tool_name: Name of the tool to enable
            
        Returns:
            True if tool was enabled, False if not found
        """
        tool = self.get_tool(tool_name)
        if tool:
            tool.enable()
            return True
        return False
    
    def disable_tool(self, tool_name: str) -> bool:
        """
        Disable a tool.
        
        Args:
            tool_name: Name of the tool to disable
            
        Returns:
            True if tool was disabled, False if not found
        """
        tool = self.get_tool(tool_name)
        if tool:
            tool.disable()
            return True
        return False
    
    def get_tool_info(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a tool.
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            Tool information dictionary or None if not found
        """
        tool = self.get_tool(tool_name)
        if tool:
            return tool.get_info()
        return None
    
    def get_registry_info(self) -> Dict[str, Any]:
        """
        Get information about the registry.
        
        Returns:
            Registry information dictionary
        """
        return {
            "total_tools": len(self._tools) + len(self._tool_classes),
            "instantiated_tools": len(self._tools),
            "registered_classes": len(self._tool_classes),
            "enabled_tools": len([t for t in self._tools.values() if t.is_enabled()]),
            "tool_names": self.list_tools(),
            "enabled_tool_names": self.list_tools(enabled_only=True)
        }
    
    def execute_tool(self, tool_name: str, **kwargs) -> Any:
        """
        Execute a tool by name.
        
        Args:
            tool_name: Name of the tool to execute
            **kwargs: Tool parameters
            
        Returns:
            Tool execution result
            
        Raises:
            ToolError: If tool is not found or execution fails
        """
        tool = self.get_tool(tool_name)
        if not tool:
            raise ToolError(f"Tool '{tool_name}' not found")
        
        if not tool.is_enabled():
            raise ToolError(f"Tool '{tool_name}' is disabled")
        
        try:
            return tool.execute(**kwargs)
        except Exception as e:
            error_msg = f"Tool '{tool_name}' execution failed: {str(e)}"
            logger.error(error_msg)
            raise ToolError(error_msg) from e
    
    def clear(self) -> None:
        """Clear all registered tools."""
        logger.info("Clearing all registered tools")
        self._tools.clear()
        self._tool_classes.clear()
    
    def __len__(self) -> int:
        """Get the number of registered tools."""
        return len(self._tools) + len(self._tool_classes)
    
    def __contains__(self, tool_name: str) -> bool:
        """Check if a tool is registered (supports 'in' operator)."""
        return self.has_tool(tool_name)
    
    def __iter__(self):
        """Iterate over tool names."""
        return iter(self.list_tools())
    
    def __str__(self) -> str:
        """String representation of the registry."""
        return f"ToolRegistry({len(self)} tools)"
    
    def __repr__(self) -> str:
        """Detailed string representation of the registry."""
        return f"ToolRegistry(tools={len(self._tools)}, classes={len(self._tool_classes)})"
