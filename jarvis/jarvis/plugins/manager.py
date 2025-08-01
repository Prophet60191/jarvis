"""
Plugin manager for the Jarvis plugin system.

This module manages the lifecycle of plugins, including loading, initialization,
and cleanup, following MCP standards for plugin management.
"""

import logging
import importlib.util
import sys
from typing import Dict, List, Optional, Any, Set
from pathlib import Path
from langchain_core.tools import BaseTool

from .base import PluginBase, PluginMetadata
from .discovery import PluginDiscovery
from .hot_reload_manager import get_hot_reload_manager

logger = logging.getLogger(__name__)


class PluginManager:
    """
    Manages the lifecycle of Jarvis plugins.
    
    This class handles loading, initialization, and cleanup of plugins,
    providing a centralized interface for plugin management.
    """
    
    def __init__(self, auto_discover: bool = True, plugin_directories: Optional[List[str]] = None, enable_hot_reload: bool = True):
        """
        Initialize the plugin manager.

        Args:
            auto_discover: Whether to automatically discover plugins on startup
            plugin_directories: Custom plugin directories to search
            enable_hot_reload: Whether to enable hot-reload of new plugins
        """
        self.discovery = PluginDiscovery(plugin_directories)
        self._loaded_plugins: Dict[str, PluginBase] = {}
        self._plugin_tools: Dict[str, List[BaseTool]] = {}
        self._disabled_plugins: Set[str] = set()

        # Initialize hot reload manager for dynamic plugin loading
        self.hot_reload_manager = None
        if enable_hot_reload:
            # Get the plugins directory from discovery
            plugins_dir = self.discovery.plugin_directories[0] if self.discovery.plugin_directories else None
            if plugins_dir:
                # Monitor the plugins directory directly (not plugins/plugins)
                self.hot_reload_manager = get_hot_reload_manager(str(plugins_dir))
                self.hot_reload_manager.plugin_manager = self  # Set reference
                self.hot_reload_manager.start_monitoring()
                logger.info("🔥 Hot reload enabled for dynamic plugin loading")

        if auto_discover:
            self.discover_and_load_all()
    
    def discover_and_load_all(self) -> None:
        """Discover and load all available plugins."""
        logger.info("Discovering and loading plugins...")
        
        discovered = self.discovery.discover_plugins()
        
        for plugin_name, plugin_info in discovered.items():
            try:
                self.load_plugin_from_info(plugin_info)
            except Exception as e:
                logger.error(f"Failed to load plugin {plugin_name}: {e}")
        
        logger.info(f"Loaded {len(self._loaded_plugins)} plugins successfully")
    
    def load_plugin_from_info(self, plugin_info: Dict[str, Any]) -> bool:
        """
        Load a plugin from discovery information.
        
        Args:
            plugin_info: Plugin information from discovery
            
        Returns:
            bool: True if plugin loaded successfully
        """
        plugin_name = plugin_info["name"]
        
        if plugin_name in self._disabled_plugins:
            logger.info(f"Plugin {plugin_name} is disabled, skipping")
            return False
        
        try:
            # Check if already loaded
            if plugin_name in self._loaded_plugins:
                logger.warning(f"Plugin {plugin_name} already loaded")
                return True
            
            metadata = plugin_info["metadata"]
            
            # Handle different discovery methods
            if plugin_info["discovery_method"] == "tools":
                # Standalone tools without plugin class
                self._load_standalone_tools(plugin_info)
                return True
            
            elif "plugin_class" in plugin_info:
                # Plugin with class
                plugin_class = plugin_info["plugin_class"]
                return self.load_plugin(plugin_name, plugin_class)
            
            else:
                logger.error(f"No valid loading method for plugin {plugin_name}")
                return False
                
        except Exception as e:
            logger.error(f"Error loading plugin {plugin_name}: {e}")
            return False
    
    def _load_standalone_tools(self, plugin_info: Dict[str, Any]) -> None:
        """
        Load standalone tools that don't have a plugin class.
        
        Args:
            plugin_info: Plugin information containing tools
        """
        plugin_name = plugin_info["name"]
        tools = plugin_info.get("tools", [])
        
        if tools:
            self._plugin_tools[plugin_name] = tools
            logger.info(f"Loaded {len(tools)} standalone tools from {plugin_name}")
    
    def load_plugin(self, plugin_name: str, plugin_class: type) -> bool:
        """
        Load a plugin by instantiating its class.
        
        Args:
            plugin_name: Name of the plugin
            plugin_class: Plugin class to instantiate
            
        Returns:
            bool: True if plugin loaded successfully
        """
        try:
            # Validate plugin class
            if not issubclass(plugin_class, PluginBase):
                logger.error(f"Plugin {plugin_name} does not inherit from PluginBase")
                return False
            
            # Create plugin instance
            plugin_instance = plugin_class()
            
            # Validate dependencies
            if not plugin_instance.validate_dependencies():
                logger.error(f"Plugin {plugin_name} has unmet dependencies")
                return False
            
            # Initialize plugin
            plugin_instance.initialize()
            
            # Get tools
            tools = plugin_instance.get_tools()
            
            # Store plugin and tools
            self._loaded_plugins[plugin_name] = plugin_instance
            self._plugin_tools[plugin_name] = tools
            
            logger.info(f"Successfully loaded plugin {plugin_name} with {len(tools)} tools")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load plugin {plugin_name}: {e}")
            return False
    
    def unload_plugin(self, plugin_name: str) -> bool:
        """
        Unload a plugin and clean up its resources.
        
        Args:
            plugin_name: Name of the plugin to unload
            
        Returns:
            bool: True if plugin unloaded successfully
        """
        try:
            if plugin_name in self._loaded_plugins:
                plugin = self._loaded_plugins[plugin_name]
                plugin.cleanup()
                del self._loaded_plugins[plugin_name]
            
            if plugin_name in self._plugin_tools:
                del self._plugin_tools[plugin_name]
            
            logger.info(f"Successfully unloaded plugin {plugin_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to unload plugin {plugin_name}: {e}")
            return False
    
    def reload_plugin(self, plugin_name: str) -> bool:
        """
        Reload a plugin by unloading and loading it again.
        
        Args:
            plugin_name: Name of the plugin to reload
            
        Returns:
            bool: True if plugin reloaded successfully
        """
        logger.info(f"Reloading plugin {plugin_name}")
        
        # Get plugin info before unloading
        plugin_info = self.discovery.get_plugin_info(plugin_name)
        if not plugin_info:
            logger.error(f"Plugin {plugin_name} not found in discovery")
            return False
        
        # Unload if currently loaded
        if plugin_name in self._loaded_plugins:
            self.unload_plugin(plugin_name)
        
        # Reload the plugin
        return self.load_plugin_from_info(plugin_info)
    
    def get_plugin(self, plugin_name: str) -> Optional[PluginBase]:
        """
        Get a loaded plugin instance.
        
        Args:
            plugin_name: Name of the plugin
            
        Returns:
            Optional[PluginBase]: Plugin instance or None if not found
        """
        return self._loaded_plugins.get(plugin_name)
    
    def get_plugin_tools(self, plugin_name: str) -> List[BaseTool]:
        """
        Get tools provided by a specific plugin.
        
        Args:
            plugin_name: Name of the plugin
            
        Returns:
            List[BaseTool]: List of tools from the plugin
        """
        return self._plugin_tools.get(plugin_name, [])
    
    def get_all_tools(self) -> List[BaseTool]:
        """
        Get all tools from all loaded plugins, including dynamically loaded ones.

        Returns:
            List[BaseTool]: List of all available tools
        """
        all_tools = []

        # Get tools from regular plugins
        for tools in self._plugin_tools.values():
            all_tools.extend(tools)

        # Get tools from hot-reloaded plugins
        if self.hot_reload_manager:
            all_tools.extend(self.hot_reload_manager.active_tools)

        return all_tools
    
    def get_loaded_plugin_names(self) -> List[str]:
        """
        Get names of all loaded plugins.
        
        Returns:
            List[str]: List of loaded plugin names
        """
        return list(self._loaded_plugins.keys())
    
    def get_plugin_metadata(self, plugin_name: str) -> Optional[PluginMetadata]:
        """
        Get metadata for a specific plugin.
        
        Args:
            plugin_name: Name of the plugin
            
        Returns:
            Optional[PluginMetadata]: Plugin metadata or None if not found
        """
        plugin = self._loaded_plugins.get(plugin_name)
        if plugin:
            return plugin.get_metadata()
        return None
    
    def disable_plugin(self, plugin_name: str) -> None:
        """
        Disable a plugin (prevent it from loading).
        
        Args:
            plugin_name: Name of the plugin to disable
        """
        self._disabled_plugins.add(plugin_name)
        if plugin_name in self._loaded_plugins:
            self.unload_plugin(plugin_name)
        logger.info(f"Disabled plugin {plugin_name}")
    
    def enable_plugin(self, plugin_name: str) -> bool:
        """
        Enable a previously disabled plugin.
        
        Args:
            plugin_name: Name of the plugin to enable
            
        Returns:
            bool: True if plugin enabled and loaded successfully
        """
        if plugin_name in self._disabled_plugins:
            self._disabled_plugins.remove(plugin_name)
        
        # Try to load the plugin
        plugin_info = self.discovery.get_plugin_info(plugin_name)
        if plugin_info:
            return self.load_plugin_from_info(plugin_info)
        
        logger.error(f"Plugin {plugin_name} not found for enabling")
        return False
    
    def cleanup_all(self) -> None:
        """Clean up all loaded plugins."""
        logger.info("Cleaning up all plugins")
        
        for plugin_name in list(self._loaded_plugins.keys()):
            self.unload_plugin(plugin_name)
        
        self._loaded_plugins.clear()
        self._plugin_tools.clear()
    
    def refresh_plugins(self) -> None:
        """Refresh plugin discovery and reload all plugins."""
        logger.info("Refreshing all plugins")
        
        # Clean up current plugins
        self.cleanup_all()
        
        # Rediscover and reload
        self.discover_and_load_all()
