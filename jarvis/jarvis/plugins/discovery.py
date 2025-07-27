"""
Plugin discovery system for Jarvis.

This module handles automatic discovery and loading of plugins from the
filesystem, following MCP standards for plugin identification.
"""

import os
import sys
import importlib
import importlib.util
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from .base import PluginBase, PluginMetadata

logger = logging.getLogger(__name__)


class PluginDiscovery:
    """
    Handles automatic discovery of Jarvis plugins.
    
    This class scans specified directories for plugin files and loads
    them dynamically, following MCP plugin discovery patterns.
    """
    
    def __init__(self, plugin_directories: Optional[List[str]] = None):
        """
        Initialize plugin discovery.
        
        Args:
            plugin_directories: List of directories to scan for plugins
        """
        self.plugin_directories = plugin_directories or []
        self._discovered_plugins: Dict[str, Dict[str, Any]] = {}
        
        # Add default plugin directories
        self._add_default_directories()
    
    def _add_default_directories(self) -> None:
        """Add default plugin directories to the search path."""
        # Get the jarvis package directory
        jarvis_dir = Path(__file__).parent.parent
        
        # Add standard plugin directories
        default_dirs = [
            jarvis_dir / "tools" / "plugins",
            jarvis_dir / "plugins" / "builtin",
            Path.home() / ".jarvis" / "plugins",
            Path.cwd() / "plugins"
        ]
        
        for directory in default_dirs:
            if directory.exists():
                self.plugin_directories.append(str(directory))
                logger.debug(f"Added plugin directory: {directory}")
    
    def discover_plugins(self) -> Dict[str, Dict[str, Any]]:
        """
        Discover all available plugins.
        
        Returns:
            Dict[str, Dict[str, Any]]: Dictionary of discovered plugins
        """
        self._discovered_plugins.clear()
        
        for directory in self.plugin_directories:
            self._scan_directory(directory)
        
        logger.info(f"Discovered {len(self._discovered_plugins)} plugins")
        return self._discovered_plugins.copy()
    
    def _scan_directory(self, directory: str) -> None:
        """
        Scan a directory for plugin files.
        
        Args:
            directory: Directory path to scan
        """
        try:
            directory_path = Path(directory)
            if not directory_path.exists():
                logger.debug(f"Plugin directory does not exist: {directory}")
                return
            
            logger.debug(f"Scanning plugin directory: {directory}")
            
            # Scan for Python files
            for file_path in directory_path.glob("*.py"):
                if file_path.name.startswith("_"):
                    continue  # Skip private files
                
                self._examine_plugin_file(file_path)
                
        except Exception as e:
            logger.error(f"Error scanning plugin directory {directory}: {e}")
    
    def _examine_plugin_file(self, file_path: Path) -> None:
        """
        Examine a Python file to see if it's a valid plugin.
        
        Args:
            file_path: Path to the Python file
        """
        try:
            # Load the module
            module_name = f"jarvis_plugin_{file_path.stem}"
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            
            if spec is None or spec.loader is None:
                logger.debug(f"Could not load spec for {file_path}")
                return
            
            module = importlib.util.module_from_spec(spec)
            
            # Add to sys.modules temporarily for imports to work
            sys.modules[module_name] = module
            
            try:
                spec.loader.exec_module(module)
                
                # Check for plugin metadata
                plugin_info = self._extract_plugin_info(module, file_path)
                if plugin_info:
                    self._discovered_plugins[plugin_info["name"]] = plugin_info
                    logger.debug(f"Discovered plugin: {plugin_info['name']}")
                
            finally:
                # Clean up sys.modules
                if module_name in sys.modules:
                    del sys.modules[module_name]
                
        except Exception as e:
            logger.warning(f"Error examining plugin file {file_path}: {e}")
    
    def _extract_plugin_info(self, module: Any, file_path: Path) -> Optional[Dict[str, Any]]:
        """
        Extract plugin information from a loaded module.
        
        Args:
            module: Loaded Python module
            file_path: Path to the module file
            
        Returns:
            Optional[Dict[str, Any]]: Plugin information or None if not a valid plugin
        """
        plugin_info = {
            "file_path": str(file_path),
            "module_name": module.__name__,
        }
        
        # Method 1: Look for PLUGIN_METADATA
        if hasattr(module, "PLUGIN_METADATA"):
            metadata = module.PLUGIN_METADATA
            if isinstance(metadata, PluginMetadata):
                plugin_info.update({
                    "name": metadata.name,
                    "metadata": metadata,
                    "discovery_method": "metadata"
                })
                
                # Look for PLUGIN_CLASS
                if hasattr(module, "PLUGIN_CLASS"):
                    plugin_info["plugin_class"] = module.PLUGIN_CLASS
                
                return plugin_info
        
        # Method 2: Look for PLUGIN_CLASS
        if hasattr(module, "PLUGIN_CLASS"):
            plugin_class = module.PLUGIN_CLASS
            if (isinstance(plugin_class, type) and 
                issubclass(plugin_class, PluginBase)):
                
                try:
                    # Create instance to get metadata
                    instance = plugin_class()
                    metadata = instance.get_metadata()
                    
                    plugin_info.update({
                        "name": metadata.name,
                        "metadata": metadata,
                        "plugin_class": plugin_class,
                        "discovery_method": "class"
                    })
                    
                    return plugin_info
                    
                except Exception as e:
                    logger.warning(f"Error instantiating plugin class in {file_path}: {e}")
        
        # Method 3: Look for individual tool functions with @tool decorator
        tools = []
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if (hasattr(attr, "name") and hasattr(attr, "description") and 
                hasattr(attr, "func") and callable(attr.func)):
                tools.append(attr)
        
        if tools:
            # Create metadata for standalone tools
            metadata = PluginMetadata(
                name=f"{file_path.stem}_tools",
                version="1.0.0",
                description=f"Tools from {file_path.name}",
                author="Unknown",
                tools=tools
            )
            
            plugin_info.update({
                "name": metadata.name,
                "metadata": metadata,
                "tools": tools,
                "discovery_method": "tools"
            })
            
            return plugin_info
        
        return None
    
    def get_plugin_info(self, plugin_name: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a specific discovered plugin.
        
        Args:
            plugin_name: Name of the plugin
            
        Returns:
            Optional[Dict[str, Any]]: Plugin information or None if not found
        """
        return self._discovered_plugins.get(plugin_name)
    
    def list_discovered_plugins(self) -> List[str]:
        """
        Get a list of all discovered plugin names.
        
        Returns:
            List[str]: List of plugin names
        """
        return list(self._discovered_plugins.keys())
    
    def add_plugin_directory(self, directory: str) -> None:
        """
        Add a directory to the plugin search path.
        
        Args:
            directory: Directory path to add
        """
        if directory not in self.plugin_directories:
            self.plugin_directories.append(directory)
            logger.info(f"Added plugin directory: {directory}")
    
    def remove_plugin_directory(self, directory: str) -> None:
        """
        Remove a directory from the plugin search path.
        
        Args:
            directory: Directory path to remove
        """
        if directory in self.plugin_directories:
            self.plugin_directories.remove(directory)
            logger.info(f"Removed plugin directory: {directory}")

    def refresh_discovery(self) -> Dict[str, Dict[str, Any]]:
        """
        Refresh plugin discovery by rescanning all directories.

        Returns:
            Dict[str, Dict[str, Any]]: Updated dictionary of discovered plugins
        """
        logger.info("Refreshing plugin discovery")
        return self.discover_plugins()
