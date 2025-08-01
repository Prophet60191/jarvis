"""
Core business logic package for Jarvis Voice Assistant.

This package contains the main business logic components including
agent management, speech processing, conversation flow, wake word detection,
and MCP (Model Context Protocol) integration.
"""

from .agent import JarvisAgent
from .speech import SpeechManager
from .conversation import ConversationManager
from .wake_word import WakeWordDetector

# MCP system components
try:
    from .mcp_config_manager import get_mcp_config_manager, MCPConfigManager
    from .mcp_client import get_mcp_client, MCPClient
    from .mcp_tool_integration import initialize_mcp_tools, get_mcp_tool_manager
    from .mcp_templates import get_mcp_templates

    __all__ = [
        'JarvisAgent', 'SpeechManager', 'ConversationManager', 'WakeWordDetector',
        'get_mcp_config_manager', 'MCPConfigManager',
        'get_mcp_client', 'MCPClient',
        'initialize_mcp_tools', 'get_mcp_tool_manager',
        'get_mcp_templates'
    ]
except ImportError as e:
    # MCP components not available, continue without them
    __all__ = ['JarvisAgent', 'SpeechManager', 'ConversationManager', 'WakeWordDetector']