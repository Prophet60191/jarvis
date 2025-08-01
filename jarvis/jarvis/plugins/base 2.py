"""
Base classes and metadata for the Jarvis plugin system.

This module defines the core interfaces that all plugins must implement,
following MCP (Model Context Protocol) standards for extensibility.
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from langchain_core.tools import BaseTool

logger = logging.getLogger(__name__)


@dataclass
class PluginMetadata:
    """
    Metadata for a Jarvis plugin.
    
    This follows MCP standards for plugin identification and capabilities.
    """
    name: str
    version: str
    description: str
    author: str
    dependencies: List[str] = field(default_factory=list)
    min_jarvis_version: Optional[str] = None
    enabled: bool = True
    tools: List[BaseTool] = field(default_factory=list)
    config_schema: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        """Validate metadata after initialization."""
        if not self.name:
            raise ValueError("Plugin name cannot be empty")
        if not self.version:
            raise ValueError("Plugin version cannot be empty")
        if not self.description:
            raise ValueError("Plugin description cannot be empty")
        if not self.author:
            raise ValueError("Plugin author cannot be empty")


class PluginBase(ABC):
    """
    Abstract base class for all Jarvis plugins.
    
    This provides the standard interface that all plugins must implement
    to be compatible with the Jarvis plugin system.
    """
    
    def __init__(self):
        """Initialize the plugin."""
        self._initialized = False
        self._metadata: Optional[PluginMetadata] = None
        
    @abstractmethod
    def get_metadata(self) -> PluginMetadata:
        """
        Get plugin metadata.
        
        Returns:
            PluginMetadata: Plugin information and capabilities
        """
        pass
    
    @abstractmethod
    def get_tools(self) -> List[BaseTool]:
        """
        Get the tools provided by this plugin.
        
        Returns:
            List[BaseTool]: List of LangChain tools
        """
        pass
    
    def initialize(self) -> None:
        """
        Initialize the plugin.
        
        This method is called when the plugin is loaded. Override this
        to perform any setup required by your plugin.
        """
        if self._initialized:
            logger.warning(f"Plugin {self.get_metadata().name} already initialized")
            return
            
        logger.info(f"Initializing plugin: {self.get_metadata().name}")
        self._initialized = True
    
    def cleanup(self) -> None:
        """
        Clean up plugin resources.
        
        This method is called when the plugin is unloaded or Jarvis shuts down.
        Override this to perform any cleanup required by your plugin.
        """
        if not self._initialized:
            return
            
        logger.info(f"Cleaning up plugin: {self.get_metadata().name}")
        self._initialized = False
    
    def is_initialized(self) -> bool:
        """
        Check if the plugin is initialized.
        
        Returns:
            bool: True if plugin is initialized
        """
        return self._initialized
    
    def validate_dependencies(self) -> bool:
        """
        Validate that all plugin dependencies are available.
        
        Returns:
            bool: True if all dependencies are satisfied
        """
        metadata = self.get_metadata()
        
        for dependency in metadata.dependencies:
            try:
                __import__(dependency)
            except ImportError:
                logger.error(f"Plugin {metadata.name} missing dependency: {dependency}")
                return False
        
        return True
    
    def get_config_schema(self) -> Optional[Dict[str, Any]]:
        """
        Get the configuration schema for this plugin.
        
        Returns:
            Optional[Dict[str, Any]]: JSON schema for plugin configuration
        """
        return self.get_metadata().config_schema
    
    def configure(self, config: Dict[str, Any]) -> None:
        """
        Configure the plugin with the provided settings.
        
        Args:
            config: Configuration dictionary
        """
        # Default implementation does nothing
        # Override in subclasses that need configuration
        pass
