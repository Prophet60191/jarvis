"""
Test Robot Framework Plugin - Minimal Version
"""

import logging
from typing import List
from langchain_core.tools import tool
from ..tools.base import BaseTool
from .base import PluginBase, PluginMetadata

logger = logging.getLogger(__name__)


@tool
def test_robot_command() -> str:
    """
    Test Robot Framework integration.
    
    Use this tool when users ask to:
    - "Test robot framework"
    - "Run robot tests"
    - "Test the system"
    
    Returns:
        Test execution status
    """
    return "🤖 Robot Framework test command executed successfully! This is a test response."


class TestRobotPlugin(PluginBase):
    """Test Robot Framework plugin."""
    
    def get_metadata(self) -> PluginMetadata:
        """Return plugin metadata."""
        return PluginMetadata(
            name="TestRobot",
            version="1.0.0",
            description="Test Robot Framework integration",
            author="Jarvis Team"
        )
    
    def get_tools(self) -> List[BaseTool]:
        """Return the test tools."""
        return [test_robot_command]


# Required variables for plugin discovery system
PLUGIN_CLASS = TestRobotPlugin
PLUGIN_METADATA = TestRobotPlugin().get_metadata()
