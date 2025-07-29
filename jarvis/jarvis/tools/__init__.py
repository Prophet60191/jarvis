"""
Tools package for Jarvis Voice Assistant.

This package provides a modular tool system with MCP (Model Context Protocol)
plugin support, allowing tools to be added without modifying core code.
"""

import logging
from .base import BaseTool, ToolResult
from .registry import ToolRegistry
from ..plugins.manager import PluginManager
# Legacy MCP system removed - using official MCP system only

logger = logging.getLogger(__name__)

# Create global tool registry
tool_registry = ToolRegistry()

# Create global plugin manager
plugin_manager = PluginManager(auto_discover=True)

# Legacy MCP system removed - using official MCP system only

# No built-in tools registered - everything is now plugin-based for maximum flexibility

def get_langchain_tools():
    """
    Get all available LangChain tools from plugins and MCP servers.

    No built-in tools - everything is plugin-based for maximum flexibility.
    Tools can be added, removed, or modified without changing core code.

    Returns:
        List: Combined list of LangChain tools
    """
    tools = []

    # Add plugin tools (includes RAG, UI, time, etc.)
    plugin_tools = plugin_manager.get_all_tools()
    tools.extend(plugin_tools)

    # MCP tools are handled by the official MCP system in main.py
    logger.info(f"Loaded {len(plugin_tools)} plugin tools (MCP tools handled separately)")
    return tools

def refresh_plugins():
    """Refresh plugin discovery and reload all plugins."""
    plugin_manager.refresh_plugins()

def get_plugin_manager():
    """Get the global plugin manager instance."""
    return plugin_manager

# Legacy MCP functions removed - using official MCP system only

__all__ = [
    'BaseTool',
    'ToolResult',
    'ToolRegistry',
    'tool_registry',
    'plugin_manager',
    'get_langchain_tools',
    'refresh_plugins',
    'get_plugin_manager'
]