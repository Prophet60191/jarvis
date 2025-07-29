"""
Enhanced System Integration Layer

This module provides the integration layer between the enhanced features
and the existing Jarvis system, ensuring seamless operation while maintaining
backward compatibility.
"""

import time
import logging
from typing import Dict, List, Optional, Any, Type
from contextlib import contextmanager
from functools import wraps

from ..plugins.enhanced_manager import EnhancedPluginManager
from ..plugins.base import PluginBase
from .agent import JarvisAgent
from ..config import JarvisConfig

logger = logging.getLogger(__name__)

class EnhancedJarvisIntegration:
    """
    Integration layer for enhanced Jarvis features.
    
    This class provides a seamless integration between the enhanced plugin
    registry system and the existing Jarvis architecture.
    """
    
    def __init__(self, config: JarvisConfig, enable_enhanced_features: bool = True):
        """
        Initialize the enhanced integration layer.
        
        Args:
            config: Jarvis configuration
            enable_enhanced_features: Whether to enable enhanced features
        """
        self.config = config
        self.enhanced_features_enabled = enable_enhanced_features
        
        # Initialize enhanced plugin manager
        self.plugin_manager = EnhancedPluginManager(
            auto_discover=True,
            enable_enhanced_features=enable_enhanced_features
        )
        
        # Track tool execution for analytics
        self._tool_execution_hooks = []
        
        logger.info(f"Enhanced Jarvis integration initialized (enhanced_features={enable_enhanced_features})")
    
    def initialize_agent_with_enhanced_features(self, agent: JarvisAgent) -> JarvisAgent:
        """
        Initialize a JarvisAgent with enhanced features.
        
        Args:
            agent: JarvisAgent instance to enhance
            
        Returns:
            JarvisAgent: Enhanced agent instance
        """
        if not self.enhanced_features_enabled:
            logger.info("Enhanced features disabled - using standard agent")
            return agent
        
        # Get all tools from enhanced plugin manager
        all_tools = self.plugin_manager.get_all_tools()
        
        # Initialize agent with tools
        agent.initialize(tools=all_tools)
        
        # Wrap agent methods for enhanced tracking
        self._wrap_agent_for_analytics(agent)
        
        logger.info(f"Agent enhanced with {len(all_tools)} tools from {len(self.plugin_manager.get_loaded_plugins())} plugins")
        
        return agent
    
    def get_plugin_recommendations(self, context: Dict[str, Any]) -> List[str]:
        """
        Get plugin recommendations based on current context.
        
        Args:
            context: Current context information
            
        Returns:
            List[str]: Recommended plugin names
        """
        if not self.enhanced_features_enabled:
            return []
        
        return self.plugin_manager.get_plugin_recommendations(context)
    
    def find_tools_by_capability(self, capability: str) -> List[str]:
        """
        Find tools that provide a specific capability.
        
        Args:
            capability: Capability to search for
            
        Returns:
            List[str]: List of tool names that provide the capability
        """
        if not self.enhanced_features_enabled:
            return []
        
        # Get plugins with the capability
        plugin_names = self.plugin_manager.find_plugins_by_capability(capability)
        
        # Get tools from those plugins
        tool_names = []
        for plugin_name in plugin_names:
            tools = self.plugin_manager.get_plugin_tools(plugin_name)
            tool_names.extend([tool.name for tool in tools])
        
        return tool_names
    
    def get_system_insights(self) -> Dict[str, Any]:
        """
        Get comprehensive system insights.
        
        Returns:
            Dict[str, Any]: System insights and analytics
        """
        if not self.enhanced_features_enabled:
            return {"enhanced_features": False}
        
        insights = {
            "enhanced_features": True,
            "registry_stats": self.plugin_manager.get_registry_statistics(),
            "ecosystem_analysis": self.plugin_manager.analyze_plugin_ecosystem(),
            "plugin_health": {}
        }
        
        # Get health status for all loaded plugins
        for plugin_name in self.plugin_manager.get_loaded_plugins():
            insights["plugin_health"][plugin_name] = self.plugin_manager.get_plugin_health_status(plugin_name)
        
        return insights
    
    def optimize_plugin_selection(self, user_intent: str, context: Dict[str, Any]) -> List[str]:
        """
        Optimize plugin selection based on user intent and context.
        
        Args:
            user_intent: User's intent or request
            context: Current context
            
        Returns:
            List[str]: Optimized list of plugin names
        """
        if not self.enhanced_features_enabled:
            return list(self.plugin_manager.get_loaded_plugins().keys())
        
        # Simple intent analysis (could be enhanced with NLP)
        intent_keywords = user_intent.lower().split()
        
        # Find capabilities based on keywords
        potential_capabilities = []
        capability_keywords = {
            "file": ["file_read", "file_write", "directory_operations"],
            "web": ["web_request", "web_scraping"],
            "data": ["data_processing", "database_operations"],
            "system": ["system_command", "process_management"],
            "email": ["email_operations"],
            "text": ["text_analysis"],
            "image": ["image_processing"],
            "code": ["execute_code", "analyze_file"]
        }
        
        for keyword in intent_keywords:
            for cap_keyword, capabilities in capability_keywords.items():
                if cap_keyword in keyword:
                    potential_capabilities.extend(capabilities)
        
        # Get plugins for identified capabilities
        recommended_plugins = set()
        for capability in potential_capabilities:
            plugins = self.plugin_manager.find_plugins_by_capability(capability)
            recommended_plugins.update(plugins)
        
        # Add context-based recommendations
        context_recommendations = self.plugin_manager.get_plugin_recommendations(context)
        recommended_plugins.update(context_recommendations)
        
        # If no specific recommendations, return top performing plugins
        if not recommended_plugins:
            if hasattr(self.plugin_manager, 'unified_registry'):
                top_plugins = self.plugin_manager.unified_registry.usage_analytics.get_top_plugins("usage_frequency", 5)
                recommended_plugins.update([plugin for plugin, _ in top_plugins])
        
        return list(recommended_plugins)
    
    @contextmanager
    def monitor_tool_execution(self, tool_name: str, plugin_name: str, context: Dict[str, Any] = None):
        """
        Context manager for monitoring tool execution.
        
        Args:
            tool_name: Name of the tool being executed
            plugin_name: Name of the plugin containing the tool
            context: Optional execution context
        """
        start_time = time.time()
        success = False
        error_message = None
        
        try:
            yield
            success = True
        except Exception as e:
            error_message = str(e)
            raise
        finally:
            if self.enhanced_features_enabled:
                execution_time = time.time() - start_time
                
                # Record usage in plugin manager
                self.plugin_manager.record_plugin_usage(
                    plugin_name=plugin_name,
                    execution_time=execution_time,
                    success=success,
                    context=context,
                    error_message=error_message
                )
                
                # Call registered hooks
                for hook in self._tool_execution_hooks:
                    try:
                        hook(tool_name, plugin_name, execution_time, success, context, error_message)
                    except Exception as e:
                        logger.error(f"Error in tool execution hook: {e}")
    
    def add_tool_execution_hook(self, hook_func):
        """
        Add a hook function to be called after tool execution.
        
        Args:
            hook_func: Function to call with (tool_name, plugin_name, execution_time, success, context, error_message)
        """
        self._tool_execution_hooks.append(hook_func)
    
    def _wrap_agent_for_analytics(self, agent: JarvisAgent) -> None:
        """
        Wrap agent methods to add analytics tracking.
        
        Args:
            agent: JarvisAgent instance to wrap
        """
        if not self.enhanced_features_enabled:
            return
        
        # Store original process_input method
        original_process_input = agent.process_input
        
        @wraps(original_process_input)
        async def enhanced_process_input(user_input: str) -> str:
            """Enhanced process_input with analytics tracking."""
            start_time = time.time()
            success = False
            error_message = None
            
            try:
                # Get context for optimization
                context = {
                    "user_input": user_input,
                    "timestamp": start_time,
                    "session_id": getattr(agent, 'session_id', 'default')
                }
                
                # Optimize plugin selection based on input
                recommended_plugins = self.optimize_plugin_selection(user_input, context)
                
                # Log optimization
                logger.debug(f"Recommended plugins for '{user_input[:50]}...': {recommended_plugins}")
                
                # Call original method
                result = await original_process_input(user_input)
                success = True
                return result
                
            except Exception as e:
                error_message = str(e)
                raise
            finally:
                # Record overall agent usage
                execution_time = time.time() - start_time
                
                # This could be enhanced to track which specific tools were used
                # For now, we record it as general agent usage
                if hasattr(self.plugin_manager, 'unified_registry'):
                    self.plugin_manager.unified_registry.usage_analytics.record_usage(
                        plugin_name="jarvis_agent",
                        execution_time=execution_time,
                        success=success,
                        context={"user_input": user_input[:100]},  # Truncate for privacy
                        error_message=error_message
                    )
        
        # Replace the method
        agent.process_input = enhanced_process_input
    
    def get_plugin_analytics_summary(self) -> Dict[str, Any]:
        """
        Get a summary of plugin analytics.
        
        Returns:
            Dict[str, Any]: Analytics summary
        """
        if not self.enhanced_features_enabled:
            return {"error": "Enhanced features not enabled"}
        
        summary = {
            "total_plugins": len(self.plugin_manager.get_loaded_plugins()),
            "total_tools": len(self.plugin_manager.get_all_tools()),
            "registry_stats": self.plugin_manager.get_registry_statistics(),
            "top_plugins": {},
            "plugin_health_summary": {"healthy": 0, "warning": 0, "critical": 0, "error": 0}
        }
        
        # Get top plugins by different metrics
        if hasattr(self.plugin_manager, 'unified_registry'):
            summary["top_plugins"] = {
                "by_usage": self.plugin_manager.unified_registry.usage_analytics.get_top_plugins("usage_frequency", 5),
                "by_success": self.plugin_manager.unified_registry.usage_analytics.get_top_plugins("success_rate", 5),
                "by_rating": self.plugin_manager.unified_registry.usage_analytics.get_top_plugins("average_rating", 5)
            }
        
        # Summarize plugin health
        for plugin_name in self.plugin_manager.get_loaded_plugins():
            health = self.plugin_manager.get_plugin_health_status(plugin_name)
            status = health.get("status", "unknown")
            if status in summary["plugin_health_summary"]:
                summary["plugin_health_summary"][status] += 1
        
        return summary
    
    def export_system_data(self, export_path: str) -> bool:
        """
        Export comprehensive system data.
        
        Args:
            export_path: Path to export data to
            
        Returns:
            bool: True if export successful
        """
        if not self.enhanced_features_enabled:
            logger.warning("Enhanced features not enabled - cannot export system data")
            return False
        
        from pathlib import Path
        return self.plugin_manager.export_enhanced_data(Path(export_path))
    
    def cleanup(self) -> None:
        """Clean up resources."""
        if self.enhanced_features_enabled and hasattr(self.plugin_manager, 'unified_registry'):
            # Save registry data
            self.plugin_manager.unified_registry._save_registry_data()
        
        logger.info("Enhanced integration cleanup completed")

# Global integration instance
_integration_instance: Optional[EnhancedJarvisIntegration] = None

def get_integration_instance(config: Optional[JarvisConfig] = None, 
                           enable_enhanced_features: bool = True) -> EnhancedJarvisIntegration:
    """
    Get the global integration instance.
    
    Args:
        config: Optional Jarvis configuration
        enable_enhanced_features: Whether to enable enhanced features
        
    Returns:
        EnhancedJarvisIntegration: Global integration instance
    """
    global _integration_instance
    
    if _integration_instance is None:
        if config is None:
            raise ValueError("Config required for first initialization")
        _integration_instance = EnhancedJarvisIntegration(config, enable_enhanced_features)
    
    return _integration_instance

def initialize_enhanced_jarvis(config: JarvisConfig, 
                             enable_enhanced_features: bool = True) -> EnhancedJarvisIntegration:
    """
    Initialize enhanced Jarvis system.
    
    Args:
        config: Jarvis configuration
        enable_enhanced_features: Whether to enable enhanced features
        
    Returns:
        EnhancedJarvisIntegration: Initialized integration instance
    """
    global _integration_instance
    _integration_instance = EnhancedJarvisIntegration(config, enable_enhanced_features)
    
    logger.info("Enhanced Jarvis system initialized")
    return _integration_instance

# Convenience functions for enhanced features
def monitor_tool_execution(tool_name: str, plugin_name: str, context: Dict[str, Any] = None):
    """
    Convenience function for monitoring tool execution.
    
    Args:
        tool_name: Name of the tool being executed
        plugin_name: Name of the plugin containing the tool
        context: Optional execution context
    """
    integration = get_integration_instance()
    return integration.monitor_tool_execution(tool_name, plugin_name, context)

def get_system_insights() -> Dict[str, Any]:
    """
    Convenience function for getting system insights.
    
    Returns:
        Dict[str, Any]: System insights
    """
    try:
        integration = get_integration_instance()
        return integration.get_system_insights()
    except ValueError:
        return {"error": "Integration not initialized"}

def find_tools_by_capability(capability: str) -> List[str]:
    """
    Convenience function for finding tools by capability.
    
    Args:
        capability: Capability to search for
        
    Returns:
        List[str]: List of tool names
    """
    try:
        integration = get_integration_instance()
        return integration.find_tools_by_capability(capability)
    except ValueError:
        return []
