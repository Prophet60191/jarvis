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
    Use this tool when the user asks about the current time or what time it is.
    Returns only the current time in 12-hour format (no date).

    Returns:
        str: Current time in 12-hour format (e.g., "2:30 PM").
             Returns an error message if the time cannot be retrieved.
    """
    try:
        # Get the current local time
        now = datetime.now()
        local_now = now.astimezone()

        # Format time in 12-hour format only
        time_str = local_now.strftime('%I:%M %p')

        # Remove leading zero from hour if present (e.g., "02:30 PM" -> "2:30 PM")
        if time_str.startswith('0'):
            time_str = time_str[1:]

        logger.info(f"Successfully retrieved device time: {time_str}")
        return time_str

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
