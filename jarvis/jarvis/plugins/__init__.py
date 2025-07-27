"""
Jarvis Plugin System

This module provides the plugin architecture for Jarvis, allowing tools to be
added without modifying the core codebase. Plugins are automatically discovered
and loaded at startup.
"""

from .base import PluginBase, PluginMetadata
from .manager import PluginManager
from .discovery import PluginDiscovery

__all__ = [
    'PluginBase',
    'PluginMetadata', 
    'PluginManager',
    'PluginDiscovery'
]
