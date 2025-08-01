"""
Tools package for Jarvis Voice Assistant.

This package provides a modular tool system with MCP (Model Context Protocol)
plugin support, allowing tools to be added without modifying core code.
"""

import logging
from .base import BaseTool, ToolResult

logger = logging.getLogger(__name__)

try:
    from ..plugins.manager import PluginManager
    # Create global plugin manager
    plugin_manager = PluginManager(auto_discover=True)
except ImportError as e:
    logger.warning(f"Plugin manager not available: {e}")
    plugin_manager = None
# Legacy MCP system removed - using official MCP system only

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
    if plugin_manager:
        plugin_tools = plugin_manager.get_all_tools()
        tools.extend(plugin_tools)
        logger.info(f"Loaded {len(plugin_tools)} plugin tools (MCP tools handled separately)")
    else:
        # Fallback: Load RAG tools directly if plugin manager is not available
        try:
            from .plugins.rag_plugin import __plugin_tools__
            tools.extend(__plugin_tools__)
            logger.info(f"Loaded {len(__plugin_tools__)} RAG tools directly (plugin manager not available)")
        except ImportError:
            logger.warning("Could not load RAG tools directly")

    return tools

def refresh_plugins():
    """Refresh plugin discovery and reload all plugins."""
    plugin_manager.refresh_plugins()

def get_plugin_manager():
    """Get the global plugin manager instance."""
    return plugin_manager

# MCP System Functions
def start_mcp_system():
    """Start the MCP system (placeholder for UI compatibility)."""
    try:
        # MCP system is now initialized in main.py
        # This is a placeholder for UI compatibility
        logger.info("MCP system start requested (handled by main application)")
        return True
    except Exception as e:
        logger.error(f"Error in MCP system start: {e}")
        return False

def stop_mcp_system():
    """Stop the MCP system (placeholder for UI compatibility)."""
    try:
        # MCP system cleanup is handled in main.py
        # This is a placeholder for UI compatibility
        logger.info("MCP system stop requested (handled by main application)")
        return True
    except Exception as e:
        logger.error(f"Error in MCP system stop: {e}")
        return False

def get_mcp_client():
    """Get MCP client (placeholder for UI compatibility)."""
    try:
        from ..core.mcp_client import get_mcp_client as _get_mcp_client
        return _get_mcp_client()
    except Exception as e:
        logger.error(f"Error getting MCP client: {e}")
        return None

def get_mcp_tool_manager():
    """Get MCP tool manager (placeholder for UI compatibility)."""
    try:
        from ..core.mcp_tool_integration import get_mcp_tool_manager as _get_mcp_tool_manager
        return _get_mcp_tool_manager()
    except Exception as e:
        logger.error(f"Error getting MCP tool manager: {e}")
        return None

def get_mcp_config_manager():
    """Get MCP config manager (placeholder for UI compatibility)."""
    try:
        from ..core.mcp_config_manager import get_mcp_config_manager as _get_mcp_config_manager
        return _get_mcp_config_manager()
    except Exception as e:
        logger.error(f"Error getting MCP config manager: {e}")
        return None

__all__ = [
    'BaseTool',
    'ToolResult',
    'plugin_manager',
    'get_langchain_tools',
    'refresh_plugins',
    'get_plugin_manager'
]