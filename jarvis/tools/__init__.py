"""
Tools package for Jarvis Voice Assistant.

This package provides a modular tool system with proper registration,
base classes, and interface-based design for extensibility.
"""

from .base import BaseTool, ToolResult
from .registry import ToolRegistry
from .time_tool import TimeTool
from .video_tool import VideoTool

# Create global tool registry
tool_registry = ToolRegistry()

# Register built-in tools
tool_registry.register(TimeTool())
tool_registry.register(VideoTool())

__all__ = [
    'BaseTool',
    'ToolResult',
    'ToolRegistry',
    'TimeTool',
    'VideoTool',
    'tool_registry'
]