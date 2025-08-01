"""
Unified Plugin Registry

Core registry system that extends the existing plugin architecture with
intelligent metadata, relationship tracking, and capability analysis.
"""

import time
import logging
from typing import Dict, List, Set, Optional, Any, Union
from dataclasses import dataclass, field, asdict
from pathlib import Path
from enum import Enum
import json
import threading

from ..base import PluginBase, PluginMetadata
from .relationship_mapper import RelationshipMapper, RelationshipType
from .capability_analyzer import CapabilityAnalyzer
from .usage_analytics import UsageAnalytics, PerformanceProfile, UsageStats

logger = logging.getLogger(__name__)

class CompatibilityLevel(Enum):
    """Compatibility levels between plugins."""
    COMPATIBLE = "compatible"
    INCOMPATIBLE = "incompatible"
    UNKNOWN = "unknown"
    REQUIRES_TESTING = "requires_testing"

@dataclass
class ExecutionContext:
    """Context information for plugin execution."""
    typical_memory_mb: float = 0.0
    typical_cpu_percent: float = 0.0
    typical_duration_ms: float = 0.0
    concurrent_safe: bool = True
    requires_network: bool = False
    requires_filesystem: bool = False

@dataclass
class ResourceRequirements:
    """Resource requirements for a plugin."""
    min_memory_mb: float = 0.0
    max_memory_mb: float = 1000.0
    min_cpu_cores: int = 1
    network_required: bool = False
    disk_space_mb: float = 0.0
    python_version: str = "3.9+"

@dataclass
class EnhancedPluginMetadata:
    """
    Enhanced metadata for plugins with additional intelligence features.
    
    Extends the base PluginMetadata with relationship tracking, capability
    analysis, performance profiling, and usage analytics.
    """
    # Base metadata (from PluginMetadata)
    name: str
    version: str
    description: str
    author: str
    dependencies: List[str] = field(default_factory=list)
    min_jarvis_version: Optional[str] = None
    enabled: bool = True
    
    # Enhanced metadata
    capabilities: Set[str] = field(default_factory=set)
    performance_profile: PerformanceProfile = field(default_factory=PerformanceProfile)
    compatibility_matrix: Dict[str, CompatibilityLevel] = field(default_factory=dict)
    usage_statistics: UsageStats = field(default_factory=UsageStats)
    semantic_tags: Set[str] = field(default_factory=set)
    execution_context: ExecutionContext = field(default_factory=ExecutionContext)
    resource_requirements: ResourceRequirements = field(default_factory=ResourceRequirements)
    
    # Metadata timestamps
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    last_analyzed: Optional[float] = None
    
    def to_base_metadata(self) -> PluginMetadata:
        """Convert to base PluginMetadata for compatibility."""
        return PluginMetadata(
            name=self.name,
            version=self.version,
            description=self.description,
            author=self.author,
            dependencies=self.dependencies,
            min_jarvis_version=self.min_jarvis_version,
            enabled=self.enabled
        )
    
    @classmethod
    def from_base_metadata(cls, base_metadata: PluginMetadata) -> 'EnhancedPluginMetadata':
        """Create enhanced metadata from base metadata."""
        return cls(
            name=base_metadata.name,
            version=base_metadata.version,
            description=base_metadata.description,
            author=base_metadata.author,
            dependencies=base_metadata.dependencies,
            min_jarvis_version=base_metadata.min_jarvis_version,
            enabled=base_metadata.enabled
        )
    
    def update_timestamp(self) -> None:
        """Update the last modified timestamp."""
        self.updated_at = time.time()

class UnifiedPluginRegistry:
    """
    Unified plugin registry with enhanced metadata and intelligence features.
    
    This registry extends the existing plugin system with:
    - Enhanced metadata tracking
    - Plugin relationship mapping
    - Capability analysis and categorization
    - Usage analytics and performance monitoring
    - Intelligent plugin recommendations
    """
    
    def __init__(self, storage_path: Optional[Path] = None):
        """
        Initialize the unified plugin registry.
        
        Args:
            storage_path: Optional path for persistent storage
        """
        self._plugins: Dict[str, EnhancedPluginMetadata] = {}
        self._plugin_instances: Dict[str, PluginBase] = {}
        self._lock = threading.RLock()
        
        # Initialize sub-components
        self.relationship_mapper = RelationshipMapper()
        self.capability_analyzer = CapabilityAnalyzer()
        self.usage_analytics = UsageAnalytics()
        
        # Storage configuration
        self.storage_path = storage_path or Path("data/plugin_registry.json")
        self.auto_save = True
        
        # Load existing data if available
        self._load_registry_data()
        
        logger.info("UnifiedPluginRegistry initialized")
    
    def register_plugin(self, plugin_name: str,
                       plugin_instance_or_metadata,
                       enhanced_metadata: Optional[EnhancedPluginMetadata] = None) -> bool:
        """
        Register a plugin with enhanced metadata.

        Args:
            plugin_name: Name of the plugin
            plugin_instance_or_metadata: Plugin instance or metadata dictionary
            enhanced_metadata: Optional enhanced metadata (will be generated if not provided)

        Returns:
            bool: True if registration successful
        """
        try:
            with self._lock:
                # Handle both plugin instances and dictionary metadata
                if isinstance(plugin_instance_or_metadata, dict):
                    # Dictionary metadata provided
                    metadata_dict = plugin_instance_or_metadata
                    plugin_instance = None

                    # Create enhanced metadata from dictionary
                    if enhanced_metadata is None:
                        # Create performance profile if performance_score provided
                        performance_profile = PerformanceProfile()
                        if "performance_score" in metadata_dict:
                            performance_profile.overall_score = metadata_dict["performance_score"]

                        enhanced_metadata = EnhancedPluginMetadata(
                            name=metadata_dict.get("name", plugin_name),
                            version=metadata_dict.get("version", "1.0.0"),
                            description=metadata_dict.get("description", ""),
                            author=metadata_dict.get("author", "Unknown"),
                            capabilities=set(metadata_dict.get("capabilities", [])),
                            dependencies=metadata_dict.get("dependencies", []),
                            performance_profile=performance_profile
                        )
                else:
                    # Plugin instance provided
                    plugin_instance = plugin_instance_or_metadata

                    # Get base metadata from plugin
                    base_metadata = plugin_instance.get_metadata()

                    # Create or use enhanced metadata
                    if enhanced_metadata is None:
                        enhanced_metadata = EnhancedPluginMetadata.from_base_metadata(base_metadata)

                        # Analyze capabilities automatically
                        capabilities = self.capability_analyzer.analyze_plugin_capabilities(plugin_instance)
                        enhanced_metadata.capabilities.update(capabilities)

                        # Set analysis timestamp
                        enhanced_metadata.last_analyzed = time.time()

                # Update timestamp
                enhanced_metadata.update_timestamp()

                # Store plugin and metadata
                self._plugins[plugin_name] = enhanced_metadata
                if plugin_instance:
                    self._plugin_instances[plugin_name] = plugin_instance
                
                # Update relationships
                self.relationship_mapper.analyze_plugin_relationships(
                    plugin_name, enhanced_metadata, self._plugins
                )
                
                # Auto-save if enabled
                if self.auto_save:
                    self._save_registry_data()
                
                logger.info(f"Registered plugin '{plugin_name}' with enhanced metadata")
                return True
                
        except Exception as e:
            logger.error(f"Failed to register plugin '{plugin_name}': {e}")
            return False
    
    def unregister_plugin(self, plugin_name: str) -> bool:
        """
        Unregister a plugin and clean up its data.
        
        Args:
            plugin_name: Name of the plugin to unregister
            
        Returns:
            bool: True if unregistration successful
        """
        try:
            with self._lock:
                if plugin_name not in self._plugins:
                    logger.warning(f"Plugin '{plugin_name}' not found in registry")
                    return False
                
                # Remove plugin data
                del self._plugins[plugin_name]
                self._plugin_instances.pop(plugin_name, None)
                
                # Clean up relationships
                self.relationship_mapper.remove_plugin_relationships(plugin_name)
                
                # Clean up usage data
                self.usage_analytics.clear_plugin_data(plugin_name)
                
                # Auto-save if enabled
                if self.auto_save:
                    self._save_registry_data()
                
                logger.info(f"Unregistered plugin '{plugin_name}'")
                return True
                
        except Exception as e:
            logger.error(f"Failed to unregister plugin '{plugin_name}': {e}")
            return False
    
    def get_plugin_metadata(self, plugin_name: str) -> Optional[EnhancedPluginMetadata]:
        """
        Get enhanced metadata for a plugin.
        
        Args:
            plugin_name: Name of the plugin
            
        Returns:
            Optional[EnhancedPluginMetadata]: Plugin metadata or None if not found
        """
        with self._lock:
            return self._plugins.get(plugin_name)
    
    def get_plugin_instance(self, plugin_name: str) -> Optional[PluginBase]:
        """
        Get plugin instance.
        
        Args:
            plugin_name: Name of the plugin
            
        Returns:
            Optional[PluginBase]: Plugin instance or None if not found
        """
        with self._lock:
            return self._plugin_instances.get(plugin_name)
    
    def find_plugins_by_capability(self, capability: str) -> List[str]:
        """
        Find plugins that provide a specific capability.
        
        Args:
            capability: Capability to search for
            
        Returns:
            List[str]: List of plugin names that provide the capability
        """
        with self._lock:
            matching_plugins = []
            for plugin_name, metadata in self._plugins.items():
                if capability in metadata.capabilities:
                    matching_plugins.append(plugin_name)
            
            # Sort by usage statistics (most used first)
            matching_plugins.sort(
                key=lambda name: self._plugins[name].usage_statistics.total_executions,
                reverse=True
            )
            
            return matching_plugins
    
    def get_related_plugins(self, plugin_name: str, 
                          relationship_type: Optional[RelationshipType] = None) -> List[str]:
        """
        Get plugins related to the specified plugin.
        
        Args:
            plugin_name: Name of the plugin
            relationship_type: Optional filter by relationship type
            
        Returns:
            List[str]: List of related plugin names
        """
        return self.relationship_mapper.get_related_plugins(plugin_name, relationship_type)
    
    def get_plugin_recommendations(self, context: Dict[str, Any]) -> List[str]:
        """
        Get plugin recommendations based on context.
        
        Args:
            context: Context information for recommendations
            
        Returns:
            List[str]: List of recommended plugin names
        """
        recommendations = []
        
        with self._lock:
            # Get capabilities from context
            required_capabilities = context.get('capabilities', [])
            current_plugins = context.get('active_plugins', [])
            
            # Find plugins with required capabilities
            for capability in required_capabilities:
                capable_plugins = self.find_plugins_by_capability(capability)
                recommendations.extend(capable_plugins)
            
            # Add complementary plugins for currently active plugins
            for plugin_name in current_plugins:
                related = self.get_related_plugins(plugin_name, RelationshipType.COMPLEMENTS)
                recommendations.extend(related)
            
            # Remove duplicates and sort by usage
            unique_recommendations = list(set(recommendations))
            unique_recommendations.sort(
                key=lambda name: self._plugins.get(name, EnhancedPluginMetadata(name="", version="", description="", author="")).usage_statistics.success_rate,
                reverse=True
            )
            
            return unique_recommendations[:10]  # Return top 10 recommendations
    
    def update_usage_statistics(self, plugin_name: str, 
                              execution_time: float, 
                              success: bool,
                              context: Optional[Dict[str, Any]] = None) -> None:
        """
        Update usage statistics for a plugin.
        
        Args:
            plugin_name: Name of the plugin
            execution_time: Execution time in seconds
            success: Whether the execution was successful
            context: Optional execution context
        """
        with self._lock:
            if plugin_name not in self._plugins:
                logger.warning(f"Plugin '{plugin_name}' not found for usage update")
                return
            
            # Update usage analytics
            self.usage_analytics.record_usage(plugin_name, execution_time, success, context)
            
            # Update plugin metadata
            metadata = self._plugins[plugin_name]
            stats = self.usage_analytics.get_usage_statistics(plugin_name)
            if stats:
                metadata.usage_statistics = stats
                metadata.update_timestamp()
            
            # Auto-save if enabled
            if self.auto_save:
                self._save_registry_data()
    
    def get_all_plugins(self) -> Dict[str, EnhancedPluginMetadata]:
        """
        Get all registered plugins.
        
        Returns:
            Dict[str, EnhancedPluginMetadata]: Dictionary of all plugins
        """
        with self._lock:
            return self._plugins.copy()
    
    def get_registry_statistics(self) -> Dict[str, Any]:
        """
        Get overall registry statistics.
        
        Returns:
            Dict[str, Any]: Registry statistics
        """
        with self._lock:
            total_plugins = len(self._plugins)
            enabled_plugins = sum(1 for m in self._plugins.values() if m.enabled)
            total_capabilities = len(set().union(*(m.capabilities for m in self._plugins.values())))
            
            return {
                'total_plugins': total_plugins,
                'enabled_plugins': enabled_plugins,
                'disabled_plugins': total_plugins - enabled_plugins,
                'total_capabilities': total_capabilities,
                'total_relationships': self.relationship_mapper.get_relationship_count(),
                'registry_size_mb': self._estimate_registry_size(),
                'last_updated': max((m.updated_at for m in self._plugins.values()), default=0)
            }
    
    def _load_registry_data(self) -> None:
        """Load registry data from persistent storage."""
        try:
            if self.storage_path.exists():
                with open(self.storage_path, 'r') as f:
                    data = json.load(f)
                
                # Load plugin metadata
                for plugin_name, plugin_data in data.get('plugins', {}).items():
                    metadata = EnhancedPluginMetadata(**plugin_data)
                    self._plugins[plugin_name] = metadata
                
                # Load relationships
                self.relationship_mapper.load_relationships(data.get('relationships', {}))
                
                # Load usage analytics
                self.usage_analytics.load_analytics_data(data.get('usage_analytics', {}))
                
                logger.info(f"Loaded registry data for {len(self._plugins)} plugins")
                
        except Exception as e:
            logger.warning(f"Failed to load registry data: {e}")
    
    def _save_registry_data(self) -> None:
        """Save registry data to persistent storage."""
        try:
            # Prepare data for serialization
            data = {
                'plugins': {
                    name: asdict(metadata) for name, metadata in self._plugins.items()
                },
                'relationships': self.relationship_mapper.export_relationships(),
                'usage_analytics': self.usage_analytics.export_analytics_data(),
                'saved_at': time.time()
            }
            
            # Ensure directory exists
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save to file
            with open(self.storage_path, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            
            logger.debug("Saved registry data to storage")
            
        except Exception as e:
            logger.error(f"Failed to save registry data: {e}")
    
    def _estimate_registry_size(self) -> float:
        """Estimate registry size in MB."""
        try:
            data = {
                'plugins': {name: asdict(metadata) for name, metadata in self._plugins.items()},
                'relationships': self.relationship_mapper.export_relationships(),
                'usage_analytics': self.usage_analytics.export_analytics_data()
            }
            
            # Rough estimation based on JSON string length
            json_str = json.dumps(data, default=str)
            return len(json_str.encode('utf-8')) / (1024 * 1024)
            
        except Exception:
            return 0.0

    async def get_plugin(self, plugin_name: str):
        """
        Get a plugin instance by name for RAG-powered workflow compatibility.

        Args:
            plugin_name: Name of the plugin to retrieve

        Returns:
            Plugin instance if found, None otherwise
        """
        try:
            # Check if plugin is registered
            if plugin_name in self._plugins:
                plugin_metadata = self._plugins[plugin_name]

                # Try to import and return the plugin
                # This is a simplified version - in practice, you'd want more sophisticated plugin loading
                if plugin_name == "aider_integration":
                    from ...tools.plugins.aider_integration import aider_code_edit
                    return type('AiderPlugin', (), {'aider_code_edit': aider_code_edit})()
                elif plugin_name == "open_interpreter":
                    from ...tools.open_interpreter_direct import OpenInterpreterDirect
                    return OpenInterpreterDirect()
                elif plugin_name == "lavague_web_automation":
                    # Return a mock plugin for now
                    return type('LaVaguePlugin', (), {})()

                logger.warning(f"Plugin {plugin_name} registered but not implemented for dynamic loading")
                return None

            # If plugin not in registry, try to load common plugins anyway
            elif plugin_name == "aider_integration":
                try:
                    from ...tools.plugins.aider_integration import aider_code_edit
                    logger.info(f"Loaded {plugin_name} plugin dynamically")
                    return type('AiderPlugin', (), {'aider_code_edit': aider_code_edit})()
                except ImportError as e:
                    logger.error(f"Failed to load {plugin_name}: {e}")
                    return None
            elif plugin_name == "open_interpreter":
                try:
                    from ...tools.open_interpreter_direct import OpenInterpreterDirect
                    logger.info(f"Loaded {plugin_name} plugin dynamically")
                    return OpenInterpreterDirect()
                except ImportError as e:
                    logger.error(f"Failed to load {plugin_name}: {e}")
                    return None
            else:
                logger.warning(f"Plugin {plugin_name} not found in registry")
                return None

        except Exception as e:
            logger.error(f"Failed to get plugin {plugin_name}: {e}")
            return None

    async def get_all_plugins(self) -> dict:
        """
        Get all registered plugins for RAG-powered workflow compatibility.

        Returns:
            Dictionary of plugin names and their metadata
        """
        try:
            plugins_dict = {}
            for name, metadata in self._plugins.items():
                plugins_dict[name] = {
                    'name': name,
                    'description': metadata.description,
                    'capabilities': getattr(metadata, 'capabilities', []),
                    'tools': getattr(metadata, 'tools', []),
                    'usage_patterns': getattr(metadata, 'usage_patterns', []),
                    'limitations': getattr(metadata, 'limitations', [])
                }

            # Add common plugins even if not in registry
            common_plugins = {
                'aider_integration': {
                    'name': 'aider_integration',
                    'description': 'AI-powered code generation and editing using Aider',
                    'capabilities': ['code_generation', 'file_creation', 'code_editing'],
                    'tools': ['aider_code_edit'],
                    'usage_patterns': ['web_applications', 'desktop_applications', 'tools'],
                    'limitations': ['requires_ollama', 'no_execution']
                },
                'open_interpreter': {
                    'name': 'open_interpreter',
                    'description': 'Code execution and testing using Open Interpreter',
                    'capabilities': ['code_execution', 'testing', 'validation'],
                    'tools': ['execute_task', 'test_and_validate', 'test_and_run'],
                    'usage_patterns': ['testing', 'validation', 'execution'],
                    'limitations': ['requires_open_interpreter', 'local_execution_only']
                }
            }

            # Add common plugins if not already present
            for plugin_name, plugin_info in common_plugins.items():
                if plugin_name not in plugins_dict:
                    plugins_dict[plugin_name] = plugin_info

            logger.info(f"Retrieved {len(plugins_dict)} plugins from registry (including common plugins)")
            return plugins_dict

        except Exception as e:
            logger.error(f"Failed to get all plugins: {e}")
            return {}

    async def initialize(self):
        """
        Async initialization method for RAG-powered workflow compatibility.

        This method doesn't do anything since UnifiedPluginRegistry initializes in __init__,
        but it's provided for compatibility with the RAG-powered workflow system.
        """
        logger.info("UnifiedPluginRegistry async initialization called (no-op)")
        return True
