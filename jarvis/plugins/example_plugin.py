"""
example_plugin Plugin for Jarvis Voice Assistant.

Example plugin for testing MCP system

Author: Jarvis Team
Date: 2025-07-26
"""

import logging
from typing import List
from langchain_core.tools import BaseTool, tool

from jarvis.plugins.base import PluginBase, PluginMetadata

logger = logging.getLogger(__name__)


class ExamplePluginPlugin(PluginBase):
    """
    example_plugin plugin for Jarvis.
    
    Example plugin for testing MCP system
    """
    
    def __init__(self):
        """Initialize the example_plugin plugin."""
        super().__init__()
        logger.info("Initialized example_plugin plugin")
    
    def get_metadata(self) -> PluginMetadata:
        """Get plugin metadata."""
        return PluginMetadata(
            name="example_plugin",
            version="1.0.0",
            description="Example plugin for testing MCP system",
            author="Jarvis Team",
            dependencies=[],
            min_jarvis_version="1.0.0"
        )
    
    def get_tools(self) -> List[BaseTool]:
        """Get tools provided by this plugin."""
        tools = []
        
        # Add your tools here
        # Example:
        # tools.append(self._create_example_tool())
        
        return tools
    
    def _create_example_tool(self) -> BaseTool:
        """Create an example tool."""
        @tool
        def example_tool(query: str = "") -> str:
            """
            Example tool implementation.
            
            Args:
                query: Input query for the tool
                
            Returns:
                str: Tool result
            """
            return f"Example tool result: {query}"
        
        return example_tool


# Plugin class for automatic discovery
PLUGIN_CLASS = ExamplePluginPlugin

# Plugin metadata for discovery
PLUGIN_METADATA = ExamplePluginPlugin().get_metadata()
