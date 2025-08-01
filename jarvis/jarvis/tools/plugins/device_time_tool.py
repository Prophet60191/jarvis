"""
A tool to provide the current time from the local device.

Author: Jarvis Team
"""

import logging
from datetime import datetime
from typing import List
from langchain_core.tools import BaseTool, tool
from jarvis.plugins.base import PluginBase, PluginMetadata

# Set up logging for the tool
logger = logging.getLogger(__name__)

@tool
def get_current_time() -> str:
    """
    Gets the current time from the local device.

    ALWAYS use this tool when the user asks:
    - "What time is it?"
    - "What's the time?"
    - "Tell me the time"
    - "Current time"
    - Any question about the current time

    This tool provides the current local time in 12-hour format (e.g., "It's 3:15 PM").

    Returns:
        str: Current time in readable format like "It's 7:45 AM"
    """
    try:
        # Get the current local time
        now = datetime.now()
        
        # Get the timezone information
        local_tz = now.astimezone().tzinfo
        
        # Format just the time in simple format
        time_str = now.strftime('%I:%M %p')

        result = f"It's {time_str}"
        logger.info("Successfully retrieved device time.")
        return result
    except Exception as e:
        logger.error(f"Failed to get device time: {e}")
        return f"Error: Could not retrieve the local device time. Reason: {e}"

class DeviceTimePlugin(PluginBase):
    """
    Plugin for providing the current time from the local device.
    """
    def get_metadata(self) -> PluginMetadata:
        """
        Provides metadata for the DeviceTimePlugin.
        """
        return PluginMetadata(
            name="DeviceTime",
            version="1.0.0",
            description="A tool to get the current time from the local device.",
            author="Jarvis Team"
        )

    def get_tools(self) -> List[BaseTool]:
        """
        Specifies the tools provided by this plugin.
        """
        return [get_current_time]

# Required variables for the MCP plugin discovery system
PLUGIN_CLASS = DeviceTimePlugin
PLUGIN_METADATA = DeviceTimePlugin().get_metadata()
