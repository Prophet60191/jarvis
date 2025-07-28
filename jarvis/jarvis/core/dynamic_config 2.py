"""
Dynamic configuration support for Jarvis components.

This module provides mixins and utilities for components to automatically
respond to configuration changes without requiring manual reinitialization.
"""

import logging
from typing import Any, Optional, Callable
from abc import ABC, abstractmethod

from ..config import ConfigSection, register_config_change_callback, unregister_config_change_callback

logger = logging.getLogger(__name__)


class DynamicConfigMixin(ABC):
    """
    Mixin class for components that need to respond to configuration changes.
    
    Components that inherit from this mixin will automatically receive
    notifications when their configuration section changes and can
    update their behavior accordingly.
    """
    
    def __init__(self, config_section: ConfigSection, *args, **kwargs):
        """
        Initialize the dynamic configuration mixin.
        
        Args:
            config_section: Configuration section to monitor
        """
        super().__init__(*args, **kwargs)
        self._config_section = config_section
        self._config_callback_registered = False
        self._current_config = None
        
    def enable_dynamic_config(self, initial_config: Any) -> None:
        """
        Enable dynamic configuration updates for this component.
        
        Args:
            initial_config: Initial configuration object
        """
        self._current_config = initial_config
        
        if not self._config_callback_registered:
            register_config_change_callback(self._config_section, self._on_config_change)
            self._config_callback_registered = True
            logger.debug(f"Enabled dynamic configuration for {self.__class__.__name__}")
    
    def disable_dynamic_config(self) -> None:
        """Disable dynamic configuration updates for this component."""
        if self._config_callback_registered:
            unregister_config_change_callback(self._config_section, self._on_config_change)
            self._config_callback_registered = False
            logger.debug(f"Disabled dynamic configuration for {self.__class__.__name__}")
    
    def _on_config_change(self, new_config: Any) -> None:
        """
        Handle configuration changes.
        
        Args:
            new_config: New configuration object
        """
        try:
            old_config = self._current_config
            self._current_config = new_config
            
            logger.info(f"Configuration changed for {self.__class__.__name__}")
            self.on_config_change(old_config, new_config)
            
        except Exception as e:
            logger.error(f"Error handling config change in {self.__class__.__name__}: {e}")
    
    @abstractmethod
    def on_config_change(self, old_config: Any, new_config: Any) -> None:
        """
        Handle configuration changes. Must be implemented by subclasses.
        
        Args:
            old_config: Previous configuration object
            new_config: New configuration object
        """
        pass
    
    def get_current_config(self) -> Any:
        """Get the current configuration object."""
        return self._current_config
    
    def __del__(self):
        """Cleanup when object is destroyed."""
        try:
            self.disable_dynamic_config()
        except:
            pass  # Ignore errors during cleanup


class ConfigurableComponent(DynamicConfigMixin):
    """
    Base class for components that need dynamic configuration support.
    
    This class provides a complete implementation for components that
    want to automatically respond to configuration changes.
    """
    
    def __init__(self, config_section: ConfigSection, initial_config: Any):
        """
        Initialize the configurable component.
        
        Args:
            config_section: Configuration section to monitor
            initial_config: Initial configuration object
        """
        super().__init__(config_section)
        self.enable_dynamic_config(initial_config)
        self._is_initialized = False
    
    @abstractmethod
    def initialize_with_config(self, config: Any) -> None:
        """
        Initialize the component with the given configuration.
        
        Args:
            config: Configuration object
        """
        pass
    
    @abstractmethod
    def update_config(self, old_config: Any, new_config: Any) -> None:
        """
        Update the component configuration.
        
        Args:
            old_config: Previous configuration object
            new_config: New configuration object
        """
        pass
    
    def on_config_change(self, old_config: Any, new_config: Any) -> None:
        """
        Handle configuration changes by updating the component.
        
        Args:
            old_config: Previous configuration object
            new_config: New configuration object
        """
        if self._is_initialized:
            self.update_config(old_config, new_config)
        else:
            # Component not yet initialized, just store the new config
            logger.debug(f"Component {self.__class__.__name__} not initialized, storing new config")
    
    def initialize(self) -> None:
        """Initialize the component with current configuration."""
        if not self._is_initialized:
            self.initialize_with_config(self._current_config)
            self._is_initialized = True
            logger.info(f"Component {self.__class__.__name__} initialized with dynamic configuration")
    
    def is_initialized(self) -> bool:
        """Check if the component is initialized."""
        return self._is_initialized


def create_config_aware_wrapper(component_class, config_section: ConfigSection):
    """
    Create a wrapper that makes any component configuration-aware.
    
    Args:
        component_class: Class to wrap
        config_section: Configuration section to monitor
        
    Returns:
        Wrapped class with dynamic configuration support
    """
    class ConfigAwareWrapper(component_class, DynamicConfigMixin):
        def __init__(self, config, *args, **kwargs):
            # Initialize the original component
            component_class.__init__(self, config, *args, **kwargs)
            # Initialize the dynamic config mixin
            DynamicConfigMixin.__init__(self, config_section)
            # Enable dynamic configuration
            self.enable_dynamic_config(config)
        
        def on_config_change(self, old_config: Any, new_config: Any) -> None:
            """Default implementation that logs the change."""
            logger.info(f"Configuration changed for {component_class.__name__}")
            # If the component has an update_config method, call it
            if hasattr(self, 'update_config'):
                self.update_config(old_config, new_config)
            # If the component has a reload_config method, call it
            elif hasattr(self, 'reload_config'):
                self.reload_config(new_config)
            else:
                logger.warning(f"Component {component_class.__name__} doesn't implement config update methods")
    
    return ConfigAwareWrapper


# Decorator for making functions configuration-aware
def config_aware(config_section: ConfigSection):
    """
    Decorator to make functions automatically receive configuration updates.
    
    Args:
        config_section: Configuration section to monitor
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Register for configuration changes
            def on_config_change(new_config):
                logger.info(f"Configuration changed, calling {func.__name__}")
                # Call the function with the new configuration
                func(new_config, *args, **kwargs)
            
            register_config_change_callback(config_section, on_config_change)
            
            # Call the original function
            return func(*args, **kwargs)
        
        return wrapper
    return decorator
