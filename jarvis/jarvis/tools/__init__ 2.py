"""
Tools package for Jarvis Voice Assistant.

This package provides a modular tool system with MCP (Model Context Protocol)
plugin support, allowing tools to be added without modifying core code.
"""

import logging
from .base import BaseTool, ToolResult
from .registry import ToolRegistry
# TimeTool moved to MCP plugin system (device_time_tool.py)
from .video_tool import VideoTool
from ..plugins.manager import PluginManager

logger = logging.getLogger(__name__)

# Create global tool registry
tool_registry = ToolRegistry()

# Create global plugin manager
plugin_manager = PluginManager(auto_discover=True)

# Register built-in tools
# TimeTool now available as MCP plugin (device_time_tool.py)
tool_registry.register(VideoTool())

def get_langchain_tools():
    """
    Get all available LangChain tools from both built-in tools and plugins.

    Returns:
        List: Combined list of LangChain tools
    """
    tools = []

    # Add built-in tools converted to LangChain format
    builtin_tools = tool_registry.get_langchain_tools()
    tools.extend(builtin_tools)

    # Add plugin tools
    plugin_tools = plugin_manager.get_all_tools()
    tools.extend(plugin_tools)

    logger.info(f"Loaded {len(builtin_tools)} built-in tools and {len(plugin_tools)} plugin tools")
    return tools

def refresh_plugins():
    """Refresh plugin discovery and reload all plugins."""
    plugin_manager.refresh_plugins()

def get_plugin_manager():
    """Get the global plugin manager instance."""
    return plugin_manager

__all__ = [
    'BaseTool',
    'ToolResult',
    'ToolRegistry',
    'VideoTool',
    'tool_registry',
    'plugin_manager',
    'get_langchain_tools',
    'refresh_plugins',
    'get_plugin_manager'
]