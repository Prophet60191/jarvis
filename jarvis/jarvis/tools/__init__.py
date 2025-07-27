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
from ..core.mcp_client import MCPClientManager
from ..core.mcp_tool_adapter import MCPToolManager

logger = logging.getLogger(__name__)

# Create global tool registry
tool_registry = ToolRegistry()

# Create global plugin manager
plugin_manager = PluginManager(auto_discover=True)

# Create global MCP client and tool manager
mcp_client = MCPClientManager()
mcp_tool_manager = MCPToolManager(mcp_client)

# Register built-in tools
# TimeTool now available as MCP plugin (device_time_tool.py)
tool_registry.register(VideoTool())

def get_langchain_tools():
    """
    Get all available LangChain tools from built-in tools, plugins, and MCP servers.

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

    # Add MCP tools
    mcp_tools = mcp_tool_manager.get_langchain_tools()
    tools.extend(mcp_tools)

    logger.info(f"Loaded {len(builtin_tools)} built-in tools, {len(plugin_tools)} plugin tools, and {len(mcp_tools)} MCP tools")
    return tools

def refresh_plugins():
    """Refresh plugin discovery and reload all plugins."""
    plugin_manager.refresh_plugins()

def get_plugin_manager():
    """Get the global plugin manager instance."""
    return plugin_manager

def get_mcp_client():
    """Get the global MCP client manager instance."""
    return mcp_client

def get_mcp_tool_manager():
    """Get the global MCP tool manager instance."""
    return mcp_tool_manager

def start_mcp_system():
    """Start the MCP client system."""
    try:
        mcp_client.start()
        logger.info("MCP system started successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to start MCP system: {e}")
        return False

def stop_mcp_system():
    """Stop the MCP client system."""
    try:
        mcp_client.stop()
        logger.info("MCP system stopped successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to stop MCP system: {e}")
        return False

__all__ = [
    'BaseTool',
    'ToolResult',
    'ToolRegistry',
    'VideoTool',
    'tool_registry',
    'plugin_manager',
    'mcp_client',
    'mcp_tool_manager',
    'get_langchain_tools',
    'refresh_plugins',
    'get_plugin_manager',
    'get_mcp_client',
    'get_mcp_tool_manager',
    'start_mcp_system',
    'stop_mcp_system'
]