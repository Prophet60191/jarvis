"""
Hot Reload Manager for Dynamic Plugin Loading

Monitors the plugins directory for new tools and automatically loads them
without requiring a restart. Enables true dynamic plugin system.
"""

import os
import time
import logging
import importlib
import importlib.util
from typing import List, Dict, Any, Optional
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from langchain.tools import BaseTool

logger = logging.getLogger(__name__)


class PluginFileHandler(FileSystemEventHandler):
    """Handles file system events for plugin directory."""
    
    def __init__(self, hot_reload_manager):
        self.hot_reload_manager = hot_reload_manager
        
    def on_created(self, event):
        """Handle file creation events."""
        if not event.is_directory and event.src_path.endswith('.py'):
            logger.info(f"🔥 New plugin file detected: {event.src_path}")
            self.hot_reload_manager.load_new_plugin(event.src_path)
    
    def on_modified(self, event):
        """Handle file modification events."""
        if not event.is_directory and event.src_path.endswith('.py'):
            logger.info(f"🔄 Plugin file modified: {event.src_path}")
            self.hot_reload_manager.reload_plugin(event.src_path)


class HotReloadManager:
    """
    Manages dynamic loading and reloading of plugins without restart.
    
    Features:
    - File system monitoring
    - Hot-reload of new plugins
    - Runtime tool registration
    - Plugin validation
    """
    
    def __init__(self, plugins_directory: str):
        self.plugins_directory = Path(plugins_directory)
        self.observer = None  # Initialize as None, create when needed
        self.loaded_plugins: Dict[str, Any] = {}
        self.active_tools: List[BaseTool] = []
        self.plugin_manager = None  # Will be set by PluginManager
        self.monitoring_active = False

        # Ensure plugins directory exists
        self.plugins_directory.mkdir(parents=True, exist_ok=True)

        logger.info(f"🔥 Hot reload manager initialized for: {self.plugins_directory}")
    
    def start_monitoring(self):
        """Start file system monitoring for new plugins."""
        try:
            # Only start if not already monitoring
            if not self.monitoring_active:
                # Create new observer each time
                self.observer = Observer()
                event_handler = PluginFileHandler(self)
                self.observer.schedule(event_handler, str(self.plugins_directory), recursive=True)
                self.observer.start()
                self.monitoring_active = True

                logger.info("🔥 Hot reload monitoring started")
            else:
                logger.info("🔥 Hot reload monitoring already running")

        except Exception as e:
            logger.error(f"Failed to start hot reload monitoring: {e}")
    
    def stop_monitoring(self):
        """Stop file system monitoring."""
        try:
            if self.observer and self.monitoring_active:
                self.observer.stop()
                self.observer.join()
                self.monitoring_active = False
                logger.info("🔥 Hot reload monitoring stopped")

        except Exception as e:
            logger.error(f"Failed to stop hot reload monitoring: {e}")
    
    def load_new_plugin(self, file_path: str):
        """Load a newly created plugin file."""
        try:
            # Wait a moment for file to be fully written
            time.sleep(0.5)

            # Validate it's a Python file in plugins directory
            if not self._is_valid_plugin_file(file_path):
                return

            # Skip if already loaded (prevent duplicates)
            if file_path in self.loaded_plugins:
                logger.debug(f"Plugin already loaded: {file_path}")
                return

            # Load the module
            module = self._load_module_from_file(file_path)
            if not module:
                return

            # Extract tools from module
            new_tools = self._extract_tools_from_module(module)

            if new_tools:
                # Register tools with plugin manager
                self._register_new_tools(new_tools, file_path)

                logger.info(f"🎉 Successfully loaded {len(new_tools)} new tools from {file_path}")

                # Notify active sessions about new tools
                self._notify_new_tools_available(new_tools)

        except Exception as e:
            logger.error(f"Failed to load new plugin {file_path}: {e}")
    
    def reload_plugin(self, file_path: str):
        """Reload a modified plugin file."""
        try:
            # Remove old version first
            self._unload_plugin(file_path)
            
            # Load new version
            self.load_new_plugin(file_path)
            
        except Exception as e:
            logger.error(f"Failed to reload plugin {file_path}: {e}")
    
    def _is_valid_plugin_file(self, file_path: str) -> bool:
        """Check if file is a valid plugin file."""
        path = Path(file_path)
        
        # Must be Python file
        if not path.suffix == '.py':
            return False
        
        # Must be in plugins directory
        if not str(self.plugins_directory) in str(path.parent):
            return False
        
        # Skip __init__.py and __pycache__
        if path.name.startswith('__'):
            return False
        
        return True
    
    def _load_module_from_file(self, file_path: str) -> Optional[Any]:
        """Load Python module from file path."""
        try:
            path = Path(file_path)
            module_name = f"dynamic_plugin_{path.stem}_{int(time.time())}"
            
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            if not spec or not spec.loader:
                logger.error(f"Could not create module spec for {file_path}")
                return None
            
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            self.loaded_plugins[file_path] = module
            return module
            
        except Exception as e:
            logger.error(f"Failed to load module from {file_path}: {e}")
            return None
    
    def _extract_tools_from_module(self, module: Any) -> List[BaseTool]:
        """Extract LangChain tools from a module."""
        tools = []
        
        try:
            # Look for functions decorated with @tool
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                
                # Check if it's a LangChain tool
                if isinstance(attr, BaseTool):
                    tools.append(attr)
                    logger.debug(f"Found tool: {attr.name}")
                
                # Check if it's a function with tool decorator
                elif hasattr(attr, 'name') and hasattr(attr, 'description') and callable(attr):
                    # This might be a @tool decorated function
                    if hasattr(attr, 'func') or str(type(attr)).find('Tool') != -1:
                        tools.append(attr)
                        logger.debug(f"Found decorated tool: {attr.name}")
            
            # Look for get_tools() function
            if hasattr(module, 'get_tools') and callable(module.get_tools):
                module_tools = module.get_tools()
                if isinstance(module_tools, list):
                    tools.extend(module_tools)
                    logger.debug(f"Found {len(module_tools)} tools from get_tools()")
            
        except Exception as e:
            logger.error(f"Failed to extract tools from module: {e}")
        
        return tools
    
    def _register_new_tools(self, tools: List[BaseTool], source_file: str):
        """Register new tools with the plugin manager."""
        try:
            if self.plugin_manager:
                # Add tools to plugin manager's tool list
                if hasattr(self.plugin_manager, '_plugin_tools'):
                    # Use the plugin manager's internal tool storage
                    plugin_name = Path(source_file).stem
                    if plugin_name not in self.plugin_manager._plugin_tools:
                        self.plugin_manager._plugin_tools[plugin_name] = []
                    self.plugin_manager._plugin_tools[plugin_name].extend(tools)

                # Update active tools list
                self.active_tools.extend(tools)

                # Store source mapping for unloading
                for tool in tools:
                    tool._source_file = source_file
                    tool._hot_loaded = True  # Mark as hot-loaded
                    logger.info(f"🔧 Hot-loaded new tool: {tool.name}")

        except Exception as e:
            logger.error(f"Failed to register new tools: {e}")
    
    def _notify_new_tools_available(self, tools: List[BaseTool]):
        """Notify that new tools are available."""
        tool_names = [tool.name for tool in tools]
        logger.info(f"🎉 NEW TOOLS AVAILABLE: {', '.join(tool_names)}")
        
        # Could emit event or update UI here
        # For now, just log the availability
    
    def _unload_plugin(self, file_path: str):
        """Unload a plugin and remove its tools."""
        try:
            if file_path in self.loaded_plugins:
                # Remove tools from active tools list
                tools_to_remove = [
                    tool for tool in self.active_tools
                    if hasattr(tool, '_source_file') and tool._source_file == file_path
                ]

                for tool in tools_to_remove:
                    self.active_tools.remove(tool)
                    logger.info(f"🗑️ Unloaded hot-loaded tool: {tool.name}")

                # Remove from plugin manager's tool storage if it exists
                if self.plugin_manager and hasattr(self.plugin_manager, '_plugin_tools'):
                    plugin_name = Path(file_path).stem
                    if plugin_name in self.plugin_manager._plugin_tools:
                        del self.plugin_manager._plugin_tools[plugin_name]

                # Remove from loaded plugins
                del self.loaded_plugins[file_path]

        except Exception as e:
            logger.error(f"Failed to unload plugin {file_path}: {e}")
    
    def get_loaded_plugin_count(self) -> int:
        """Get count of dynamically loaded plugins."""
        return len(self.loaded_plugins)
    
    def get_active_tool_count(self) -> int:
        """Get count of active tools."""
        return len(self.active_tools)


# Global instance
_hot_reload_manager = None

def get_hot_reload_manager(plugins_directory: str = None) -> HotReloadManager:
    """Get the hot reload manager instance."""
    global _hot_reload_manager
    
    if _hot_reload_manager is None:
        if plugins_directory is None:
            # Default to plugins directory
            import os
            plugins_directory = os.path.join(os.path.dirname(__file__), 'plugins')
        
        _hot_reload_manager = HotReloadManager(plugins_directory)
    
    return _hot_reload_manager
