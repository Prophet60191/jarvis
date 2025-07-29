"""
Enhanced Plugin Manager

Extends the existing PluginManager with enhanced registry capabilities
while maintaining full backward compatibility.
"""

import logging
from typing import Dict, List, Optional, Any, Type
from pathlib import Path

from .manager import PluginManager
from .base import PluginBase, PluginMetadata
from .registry import UnifiedPluginRegistry, EnhancedPluginMetadata
from .discovery import PluginDiscovery

logger = logging.getLogger(__name__)

class EnhancedPluginManager(PluginManager):
    """
    Enhanced plugin manager with intelligent registry capabilities.
    
    This class extends the existing PluginManager with:
    - Enhanced metadata tracking
    - Plugin relationship analysis
    - Capability detection
    - Usage analytics
    - Performance monitoring
    """
    
    def __init__(self, auto_discover: bool = True, 
                 plugin_directories: Optional[List[str]] = None,
                 enable_enhanced_features: bool = True,
                 registry_storage_path: Optional[Path] = None):
        """
        Initialize the enhanced plugin manager.
        
        Args:
            auto_discover: Whether to auto-discover plugins
            plugin_directories: Optional list of plugin directories
            enable_enhanced_features: Whether to enable enhanced features
            registry_storage_path: Optional path for registry storage
        """
        # Initialize base plugin manager
        super().__init__(auto_discover=auto_discover, plugin_directories=plugin_directories)
        
        # Enhanced features configuration
        self.enhanced_features_enabled = enable_enhanced_features
        
        if self.enhanced_features_enabled:
            # Initialize enhanced registry
            self.unified_registry = UnifiedPluginRegistry(storage_path=registry_storage_path)
            
            # Hook into existing plugin lifecycle
            self._setup_enhanced_hooks()
            
            logger.info("Enhanced plugin manager initialized with registry features")
        else:
            self.unified_registry = None
            logger.info("Enhanced plugin manager initialized in compatibility mode")
    
    def load_plugin(self, plugin_name: str, plugin_class: Type[PluginBase]) -> bool:
        """
        Load a plugin with enhanced metadata tracking.
        
        Args:
            plugin_name: Name of the plugin
            plugin_class: Plugin class to load
            
        Returns:
            bool: True if plugin loaded successfully
        """
        # Call parent implementation first
        success = super().load_plugin(plugin_name, plugin_class)
        
        if success and self.enhanced_features_enabled:
            try:
                # Get plugin instance
                plugin_instance = self._loaded_plugins.get(plugin_name)
                if plugin_instance:
                    # Register with enhanced registry
                    self.unified_registry.register_plugin(plugin_name, plugin_instance)
                    
                    logger.debug(f"Plugin '{plugin_name}' registered with enhanced registry")
                
            except Exception as e:
                logger.error(f"Failed to register plugin '{plugin_name}' with enhanced registry: {e}")
                # Don't fail the entire load operation for registry issues
        
        return success
    
    def unload_plugin(self, plugin_name: str) -> bool:
        """
        Unload a plugin and clean up enhanced registry data.
        
        Args:
            plugin_name: Name of the plugin to unload
            
        Returns:
            bool: True if plugin unloaded successfully
        """
        # Clean up enhanced registry first
        if self.enhanced_features_enabled and plugin_name in self._loaded_plugins:
            try:
                self.unified_registry.unregister_plugin(plugin_name)
                logger.debug(f"Plugin '{plugin_name}' unregistered from enhanced registry")
            except Exception as e:
                logger.error(f"Failed to unregister plugin '{plugin_name}' from enhanced registry: {e}")
        
        # Call parent implementation
        return super().unload_plugin(plugin_name)
    
    def get_enhanced_plugin_metadata(self, plugin_name: str) -> Optional[EnhancedPluginMetadata]:
        """
        Get enhanced metadata for a plugin.
        
        Args:
            plugin_name: Name of the plugin
            
        Returns:
            Optional[EnhancedPluginMetadata]: Enhanced metadata or None
        """
        if not self.enhanced_features_enabled:
            return None
        
        return self.unified_registry.get_plugin_metadata(plugin_name)
    
    def find_plugins_by_capability(self, capability: str) -> List[str]:
        """
        Find plugins that provide a specific capability.
        
        Args:
            capability: Capability to search for
            
        Returns:
            List[str]: List of plugin names that provide the capability
        """
        if not self.enhanced_features_enabled:
            logger.warning("Enhanced features not enabled - capability search unavailable")
            return []
        
        return self.unified_registry.find_plugins_by_capability(capability)
    
    def get_related_plugins(self, plugin_name: str) -> List[str]:
        """
        Get plugins related to the specified plugin.
        
        Args:
            plugin_name: Name of the plugin
            
        Returns:
            List[str]: List of related plugin names
        """
        if not self.enhanced_features_enabled:
            return []
        
        return self.unified_registry.get_related_plugins(plugin_name)
    
    def get_plugin_recommendations(self, context: Dict[str, Any]) -> List[str]:
        """
        Get plugin recommendations based on context.
        
        Args:
            context: Context information for recommendations
            
        Returns:
            List[str]: List of recommended plugin names
        """
        if not self.enhanced_features_enabled:
            return []
        
        return self.unified_registry.get_plugin_recommendations(context)
    
    def record_plugin_usage(self, plugin_name: str, execution_time: float, 
                          success: bool, context: Optional[Dict[str, Any]] = None,
                          error_message: Optional[str] = None,
                          user_rating: Optional[float] = None) -> None:
        """
        Record plugin usage for analytics.
        
        Args:
            plugin_name: Name of the plugin
            execution_time: Execution time in seconds
            success: Whether the execution was successful
            context: Optional execution context
            error_message: Optional error message if failed
            user_rating: Optional user rating (1-5 scale)
        """
        if not self.enhanced_features_enabled:
            return
        
        try:
            self.unified_registry.update_usage_statistics(
                plugin_name, execution_time, success, context
            )
            
            # Also record detailed usage for analytics
            self.unified_registry.usage_analytics.record_usage(
                plugin_name=plugin_name,
                execution_time=execution_time,
                success=success,
                context=context,
                error_message=error_message,
                user_rating=user_rating
            )
            
        except Exception as e:
            logger.error(f"Failed to record usage for plugin '{plugin_name}': {e}")
    
    def get_plugin_analytics(self, plugin_name: str) -> Dict[str, Any]:
        """
        Get comprehensive analytics for a plugin.
        
        Args:
            plugin_name: Name of the plugin
            
        Returns:
            Dict[str, Any]: Plugin analytics data
        """
        if not self.enhanced_features_enabled:
            return {"error": "Enhanced features not enabled"}
        
        try:
            analytics = {}
            
            # Get usage statistics
            usage_stats = self.unified_registry.usage_analytics.get_usage_statistics(plugin_name)
            if usage_stats:
                analytics["usage_stats"] = {
                    "total_executions": usage_stats.total_executions,
                    "success_rate": usage_stats.success_rate,
                    "average_rating": usage_stats.average_rating,
                    "usage_frequency": usage_stats.usage_frequency,
                    "last_used": usage_stats.last_used
                }
            
            # Get performance profile
            performance_profile = self.unified_registry.usage_analytics.get_performance_profile(plugin_name)
            if performance_profile:
                analytics["performance"] = {
                    "avg_execution_time": performance_profile.avg_execution_time,
                    "min_execution_time": performance_profile.min_execution_time,
                    "max_execution_time": performance_profile.max_execution_time,
                    "memory_usage_mb": performance_profile.memory_usage_mb,
                    "success_rate": performance_profile.success_rate
                }
            
            # Get relationships
            relationships = self.unified_registry.relationship_mapper.get_plugin_relationships(plugin_name)
            analytics["relationships"] = {
                rel_type.value: [(plugin, strength) for plugin, strength in plugins]
                for rel_type, plugins in relationships.items()
            }
            
            # Get optimization recommendations
            recommendations = self.unified_registry.usage_analytics.recommend_optimizations(plugin_name)
            analytics["recommendations"] = recommendations
            
            return analytics
            
        except Exception as e:
            logger.error(f"Failed to get analytics for plugin '{plugin_name}': {e}")
            return {"error": str(e)}
    
    def get_registry_statistics(self) -> Dict[str, Any]:
        """
        Get overall registry statistics.
        
        Returns:
            Dict[str, Any]: Registry statistics
        """
        if not self.enhanced_features_enabled:
            return {"error": "Enhanced features not enabled"}
        
        try:
            # Get basic registry stats
            registry_stats = self.unified_registry.get_registry_statistics()
            
            # Add manager-specific stats
            registry_stats.update({
                "loaded_plugins": len(self._loaded_plugins),
                "disabled_plugins": len(self._disabled_plugins),
                "total_tools": sum(len(tools) for tools in self._plugin_tools.values()),
                "enhanced_features_enabled": self.enhanced_features_enabled
            })
            
            return registry_stats
            
        except Exception as e:
            logger.error(f"Failed to get registry statistics: {e}")
            return {"error": str(e)}
    
    def analyze_plugin_ecosystem(self) -> Dict[str, Any]:
        """
        Analyze the overall plugin ecosystem.
        
        Returns:
            Dict[str, Any]: Ecosystem analysis
        """
        if not self.enhanced_features_enabled:
            return {"error": "Enhanced features not enabled"}
        
        try:
            analysis = {}
            
            # Get top plugins by various metrics
            analysis["top_by_usage"] = self.unified_registry.usage_analytics.get_top_plugins("usage_frequency")
            analysis["top_by_success"] = self.unified_registry.usage_analytics.get_top_plugins("success_rate")
            analysis["top_by_rating"] = self.unified_registry.usage_analytics.get_top_plugins("average_rating")
            
            # Analyze capability distribution
            all_plugins = self.unified_registry.get_all_plugins()
            capability_counts = {}
            for plugin_metadata in all_plugins.values():
                for capability in plugin_metadata.capabilities:
                    capability_counts[capability] = capability_counts.get(capability, 0) + 1
            
            analysis["capability_distribution"] = sorted(
                capability_counts.items(), key=lambda x: x[1], reverse=True
            )
            
            # Analyze relationship density
            total_relationships = self.unified_registry.relationship_mapper.get_relationship_count()
            total_plugins = len(all_plugins)
            if total_plugins > 1:
                max_possible_relationships = total_plugins * (total_plugins - 1)
                relationship_density = total_relationships / max_possible_relationships
            else:
                relationship_density = 0.0
            
            analysis["relationship_density"] = relationship_density
            analysis["total_relationships"] = total_relationships
            
            return analysis
            
        except Exception as e:
            logger.error(f"Failed to analyze plugin ecosystem: {e}")
            return {"error": str(e)}
    
    def export_enhanced_data(self, export_path: Path) -> bool:
        """
        Export enhanced registry data.
        
        Args:
            export_path: Path to export data to
            
        Returns:
            bool: True if export successful
        """
        if not self.enhanced_features_enabled:
            logger.warning("Enhanced features not enabled - cannot export data")
            return False
        
        try:
            # Export registry data
            export_data = {
                "registry_statistics": self.get_registry_statistics(),
                "ecosystem_analysis": self.analyze_plugin_ecosystem(),
                "all_plugins": {
                    name: {
                        "metadata": metadata.__dict__,
                        "analytics": self.get_plugin_analytics(name)
                    }
                    for name, metadata in self.unified_registry.get_all_plugins().items()
                }
            }
            
            # Save to file
            import json
            export_path.parent.mkdir(parents=True, exist_ok=True)
            with open(export_path, 'w') as f:
                json.dump(export_data, f, indent=2, default=str)
            
            logger.info(f"Enhanced registry data exported to {export_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to export enhanced data: {e}")
            return False
    
    def _setup_enhanced_hooks(self) -> None:
        """Set up hooks for enhanced features."""
        # This method sets up integration points with the existing plugin system
        # For now, we rely on the overridden methods, but this could be extended
        # to add more sophisticated hooks
        
        logger.debug("Enhanced plugin manager hooks configured")
    
    def _on_plugin_tool_executed(self, plugin_name: str, tool_name: str, 
                                execution_time: float, success: bool,
                                context: Optional[Dict[str, Any]] = None,
                                error_message: Optional[str] = None) -> None:
        """
        Hook called when a plugin tool is executed.
        
        This method should be called by the tool execution system to track usage.
        
        Args:
            plugin_name: Name of the plugin
            tool_name: Name of the tool that was executed
            execution_time: Execution time in seconds
            success: Whether the execution was successful
            context: Optional execution context
            error_message: Optional error message if failed
        """
        if self.enhanced_features_enabled:
            # Record usage with tool context
            enhanced_context = context or {}
            enhanced_context["tool_name"] = tool_name
            
            self.record_plugin_usage(
                plugin_name=plugin_name,
                execution_time=execution_time,
                success=success,
                context=enhanced_context,
                error_message=error_message
            )
            
            # Record relationship usage patterns
            self.unified_registry.relationship_mapper.record_plugin_usage(plugin_name)
    
    def get_plugin_health_status(self, plugin_name: str) -> Dict[str, Any]:
        """
        Get health status for a plugin.
        
        Args:
            plugin_name: Name of the plugin
            
        Returns:
            Dict[str, Any]: Health status information
        """
        if not self.enhanced_features_enabled:
            return {"status": "unknown", "reason": "Enhanced features not enabled"}
        
        try:
            # Check if plugin is loaded
            if plugin_name not in self._loaded_plugins:
                return {"status": "unloaded", "reason": "Plugin not loaded"}
            
            # Check if plugin is disabled
            if plugin_name in self._disabled_plugins:
                return {"status": "disabled", "reason": "Plugin disabled"}
            
            # Get usage statistics
            usage_stats = self.unified_registry.usage_analytics.get_usage_statistics(plugin_name)
            if not usage_stats:
                return {"status": "healthy", "reason": "No usage data available"}
            
            # Analyze health based on statistics
            health_issues = []
            
            if usage_stats.success_rate < 0.8:  # Less than 80% success rate
                health_issues.append(f"Low success rate: {usage_stats.success_rate:.1%}")
            
            if usage_stats.average_rating < 2.5 and usage_stats.user_feedback_count > 3:
                health_issues.append(f"Low user rating: {usage_stats.average_rating:.1f}/5")
            
            # Get performance profile
            performance = self.unified_registry.usage_analytics.get_performance_profile(plugin_name)
            if performance:
                if performance.avg_execution_time > 10.0:  # More than 10 seconds
                    health_issues.append(f"Slow execution: {performance.avg_execution_time:.1f}s average")
                
                if performance.memory_usage_mb > 500:  # More than 500MB
                    health_issues.append(f"High memory usage: {performance.memory_usage_mb:.0f}MB")
            
            # Determine overall status
            if not health_issues:
                return {"status": "healthy", "reason": "All metrics within normal ranges"}
            elif len(health_issues) == 1:
                return {"status": "warning", "reason": health_issues[0], "issues": health_issues}
            else:
                return {"status": "critical", "reason": f"{len(health_issues)} issues detected", "issues": health_issues}
            
        except Exception as e:
            logger.error(f"Failed to get health status for plugin '{plugin_name}': {e}")
            return {"status": "error", "reason": str(e)}
