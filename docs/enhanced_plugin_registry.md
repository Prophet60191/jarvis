# Enhanced Plugin Registry Documentation

## Overview

The Enhanced Plugin Registry is a sophisticated system that extends Jarvis's plugin architecture with intelligent metadata tracking, relationship analysis, capability detection, and usage analytics. It provides deep insights into plugin behavior and enables intelligent tool orchestration.

## Architecture

### Core Components

```
Enhanced Plugin Registry
├── UnifiedPluginRegistry (Core registry with enhanced metadata)
├── RelationshipMapper (Tool relationship tracking and analysis)
├── CapabilityAnalyzer (Automatic capability detection)
├── UsageAnalytics (Usage pattern analysis and performance tracking)
└── EnhancedPluginManager (Integration with existing plugin system)
```

### Key Features

- **Enhanced Metadata**: Rich plugin metadata with capabilities, performance profiles, and compatibility information
- **Relationship Mapping**: Automatic detection of plugin relationships (complements, conflicts, dependencies)
- **Capability Analysis**: Intelligent detection of plugin capabilities through code analysis
- **Usage Analytics**: Comprehensive tracking of plugin usage patterns and performance metrics
- **Intelligent Recommendations**: Context-aware plugin and tool suggestions

## Getting Started

### Basic Usage

```python
from jarvis.jarvis.plugins.registry import UnifiedPluginRegistry
from jarvis.jarvis.plugins.enhanced_manager import EnhancedPluginManager

# Initialize enhanced plugin manager
plugin_manager = EnhancedPluginManager(enable_enhanced_features=True)

# Register a plugin (automatically analyzes capabilities)
plugin_manager.load_plugin("my_plugin", MyPluginClass)

# Find plugins by capability
file_plugins = plugin_manager.find_plugins_by_capability("file_operations")

# Get plugin recommendations
context = {"user_intent": "process files", "active_plugins": []}
recommendations = plugin_manager.get_plugin_recommendations(context)

# Get plugin analytics
analytics = plugin_manager.get_plugin_analytics("my_plugin")
```

### Integration with Existing System

```python
from jarvis.jarvis.core.enhanced_integration import initialize_enhanced_jarvis
from jarvis.jarvis.config import JarvisConfig

# Initialize enhanced Jarvis system
config = JarvisConfig()
integration = initialize_enhanced_jarvis(config, enable_enhanced_features=True)

# Enhance an existing agent
enhanced_agent = integration.initialize_agent_with_enhanced_features(agent)

# Monitor tool execution
with integration.monitor_tool_execution("file_tool", "file_plugin"):
    result = execute_file_operation()
```

## Enhanced Metadata

### EnhancedPluginMetadata

The `EnhancedPluginMetadata` class extends basic plugin metadata with:

```python
@dataclass
class EnhancedPluginMetadata:
    # Base metadata
    name: str
    version: str
    description: str
    author: str
    
    # Enhanced metadata
    capabilities: Set[str]                    # Detected capabilities
    performance_profile: PerformanceProfile  # Performance characteristics
    compatibility_matrix: Dict[str, CompatibilityLevel]  # Plugin compatibility
    usage_statistics: UsageStats             # Usage analytics
    semantic_tags: Set[str]                  # Semantic categorization
    execution_context: ExecutionContext      # Runtime requirements
    resource_requirements: ResourceRequirements  # System requirements
```

### Performance Profile

```python
@dataclass
class PerformanceProfile:
    avg_execution_time: float = 0.0
    min_execution_time: float = float('inf')
    max_execution_time: float = 0.0
    memory_usage_mb: float = 0.0
    cpu_usage_percent: float = 0.0
    success_rate: float = 1.0
    error_patterns: List[str] = field(default_factory=list)
```

## Capability Analysis

### Automatic Detection

The `CapabilityAnalyzer` automatically detects plugin capabilities through:

1. **Metadata Analysis**: Examines plugin descriptions and names
2. **Tool Analysis**: Analyzes tool names, descriptions, and functions
3. **Code Analysis**: Inspects source code for patterns and imports
4. **Class Structure**: Examines class hierarchy and attributes

### Capability Categories

```python
class CapabilityCategory(Enum):
    DATA_OPERATIONS = "data_operations"
    FILE_OPERATIONS = "file_operations"
    WEB_OPERATIONS = "web_operations"
    SYSTEM_OPERATIONS = "system_operations"
    USER_INTERACTION = "user_interaction"
    COMMUNICATION = "communication"
    ANALYSIS = "analysis"
    AUTOMATION = "automation"
    INTEGRATION = "integration"
    SECURITY = "security"
```

### Example Usage

```python
from jarvis.jarvis.plugins.registry import CapabilityAnalyzer

analyzer = CapabilityAnalyzer()

# Analyze plugin capabilities
capabilities = analyzer.analyze_plugin_capabilities(plugin_instance)
print(f"Detected capabilities: {capabilities}")

# Categorize capabilities
categorized = analyzer.categorize_capabilities(capabilities)
print(f"File operations: {categorized[CapabilityCategory.FILE_OPERATIONS]}")

# Suggest missing capabilities
suggestions = analyzer.suggest_missing_capabilities(plugin_instance, capabilities)
print(f"Suggested additional capabilities: {suggestions}")
```

## Relationship Mapping

### Relationship Types

```python
class RelationshipType(Enum):
    COMPLEMENTS = "complements"      # Tools that work well together
    CONFLICTS = "conflicts"          # Tools that interfere with each other
    DEPENDS_ON = "depends_on"        # Sequential dependency relationships
    ALTERNATIVES = "alternatives"     # Tools that can substitute for each other
    ENHANCES = "enhances"            # Tools that improve another tool's output
    REQUIRES = "requires"            # Hard dependency requirement
    INCOMPATIBLE = "incompatible"    # Cannot be used together
```

### Usage Pattern Analysis

```python
from jarvis.jarvis.plugins.registry import RelationshipMapper

mapper = RelationshipMapper()

# Record plugin usage for pattern analysis
mapper.record_plugin_usage("file_manager", timestamp)
mapper.record_plugin_usage("text_editor", timestamp + 5)  # Used shortly after

# Get related plugins
related = mapper.get_related_plugins("file_manager", RelationshipType.COMPLEMENTS)
print(f"Plugins that complement file_manager: {related}")

# Get tool chain suggestions
chains = mapper.get_tool_chain_suggestions("file_manager", target_capability="text_processing")
print(f"Suggested tool chains: {chains}")
```

## Usage Analytics

### Tracking Usage

```python
from jarvis.jarvis.plugins.registry import UsageAnalytics

analytics = UsageAnalytics()

# Record plugin usage
analytics.record_usage(
    plugin_name="file_manager",
    execution_time=0.5,
    success=True,
    context={"file_type": "text", "operation": "read"},
    user_rating=4.5
)

# Get usage statistics
stats = analytics.get_usage_statistics("file_manager")
print(f"Success rate: {stats.success_rate:.1%}")
print(f"Average execution time: {stats.avg_execution_time:.2f}s")
```

### Analytics Insights

```python
# Get top plugins by various metrics
top_by_usage = analytics.get_top_plugins("usage_frequency", limit=5)
top_by_success = analytics.get_top_plugins("success_rate", limit=5)

# Analyze failure patterns
failure_analysis = analytics.analyze_failure_patterns("problematic_plugin")
print(f"Common errors: {failure_analysis['common_error_patterns']}")

# Get optimization recommendations
recommendations = analytics.recommend_optimizations("slow_plugin")
print(f"Optimization suggestions: {recommendations}")
```

## Integration Examples

### Custom Plugin with Enhanced Features

```python
from jarvis.jarvis.plugins.base import PluginBase, PluginMetadata
from jarvis.jarvis.plugins.registry import EnhancedPluginMetadata, PerformanceProfile
from langchain_core.tools import tool

class MyEnhancedPlugin(PluginBase):
    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="my_enhanced_plugin",
            version="1.0.0",
            description="Plugin with file operations and data processing capabilities",
            author="Developer"
        )
    
    def get_enhanced_metadata(self) -> EnhancedPluginMetadata:
        return EnhancedPluginMetadata(
            name="my_enhanced_plugin",
            version="1.0.0",
            description="Plugin with file operations and data processing capabilities",
            author="Developer",
            capabilities={"file_operations", "data_processing"},
            performance_profile=PerformanceProfile(
                avg_execution_time=0.3,
                memory_usage_mb=15.0,
                success_rate=0.98
            ),
            semantic_tags={"productivity", "automation"}
        )
    
    def get_tools(self):
        @tool
        def process_file(filename: str) -> str:
            """Process a file and return results."""
            # Implementation here
            return f"Processed {filename}"
        
        return [process_file]

# Register with enhanced features
plugin_manager = EnhancedPluginManager(enable_enhanced_features=True)
plugin_manager.load_plugin("my_enhanced_plugin", MyEnhancedPlugin)
```

### Monitoring Tool Execution

```python
from jarvis.jarvis.core.enhanced_integration import monitor_tool_execution

# Monitor individual tool execution
with monitor_tool_execution("file_processor", "file_plugin", {"file_type": "csv"}):
    result = process_csv_file("data.csv")

# Add custom execution hooks
def my_execution_hook(tool_name, plugin_name, execution_time, success, context, error_message):
    if not success:
        logger.error(f"Tool {tool_name} failed: {error_message}")
    elif execution_time > 5.0:
        logger.warning(f"Tool {tool_name} is slow: {execution_time:.2f}s")

integration.add_tool_execution_hook(my_execution_hook)
```

## Performance Considerations

### Benchmarks

The Enhanced Plugin Registry is designed to meet these performance targets:

- **Registry Query Time**: < 50ms for metadata retrieval
- **Capability Search**: < 50ms for finding plugins by capability
- **Relationship Analysis**: < 100ms for relationship queries
- **Usage Recording**: < 5ms for recording usage events
- **Memory Overhead**: < 50MB for registry data

### Optimization Tips

1. **Batch Operations**: Use batch operations when possible for better performance
2. **Caching**: The registry automatically caches frequently accessed data
3. **Cleanup**: Regularly clean up old usage data to prevent memory bloat
4. **Storage**: Use SSD storage for registry persistence files

## Configuration

### Registry Configuration

```python
# Configure registry storage
registry = UnifiedPluginRegistry(
    storage_path=Path("data/enhanced_registry.json")
)

# Configure analytics retention
analytics = UsageAnalytics(max_events=50000)  # Keep last 50k events

# Configure relationship analysis
mapper = RelationshipMapper()
mapper.min_evidence_threshold = 5  # Minimum evidence for reliable relationships
mapper.time_window_seconds = 300   # 5-minute window for co-usage detection
```

### Feature Flags

```python
# Enable/disable enhanced features
plugin_manager = EnhancedPluginManager(
    enable_enhanced_features=True,  # Enable all enhanced features
    auto_discover=True,             # Auto-discover plugins
    plugin_directories=["plugins/", "custom_plugins/"]
)

# Integration with feature flags
integration = EnhancedJarvisIntegration(
    config=jarvis_config,
    enable_enhanced_features=config.get("enhanced_features", True)
)
```

## Troubleshooting

### Common Issues

1. **High Memory Usage**: Reduce `max_events` in UsageAnalytics or clean up old data
2. **Slow Queries**: Check if registry storage is on fast storage (SSD)
3. **Missing Capabilities**: Verify plugin code follows detectable patterns
4. **Relationship Detection**: Ensure plugins are used together within the time window

### Debug Information

```python
# Get registry statistics
stats = registry.get_registry_statistics()
print(f"Total plugins: {stats['total_plugins']}")
print(f"Registry size: {stats['registry_size_mb']:.1f}MB")

# Get plugin health status
health = plugin_manager.get_plugin_health_status("my_plugin")
print(f"Plugin health: {health['status']} - {health['reason']}")

# Export system data for analysis
integration.export_system_data("debug_export.json")
```

## API Reference

For detailed API documentation, see:
- [UnifiedPluginRegistry API](api/jarvis_plugins.html#unified-plugin-registry)
- [RelationshipMapper API](api/jarvis_plugins.html#relationship-mapper)
- [CapabilityAnalyzer API](api/jarvis_plugins.html#capability-analyzer)
- [UsageAnalytics API](api/jarvis_plugins.html#usage-analytics)

## Migration Guide

### From Standard Plugin System

1. **Update Plugin Manager**:
   ```python
   # Old
   from jarvis.jarvis.plugins.manager import PluginManager
   manager = PluginManager()
   
   # New
   from jarvis.jarvis.plugins.enhanced_manager import EnhancedPluginManager
   manager = EnhancedPluginManager(enable_enhanced_features=True)
   ```

2. **Add Enhanced Metadata** (Optional):
   ```python
   class MyPlugin(PluginBase):
       def get_enhanced_metadata(self) -> EnhancedPluginMetadata:
           return EnhancedPluginMetadata(
               # ... enhanced metadata
           )
   ```

3. **Enable Monitoring**:
   ```python
   # Wrap tool execution with monitoring
   with monitor_tool_execution("tool_name", "plugin_name"):
       result = execute_tool()
   ```

### Backward Compatibility

The Enhanced Plugin Registry maintains full backward compatibility with existing plugins. Existing plugins will work without modification, but won't benefit from enhanced features until updated.

## Contributing

To contribute to the Enhanced Plugin Registry:

1. Follow the [development guide](ENHANCED_DEVELOPMENT_GUIDE.md)
2. Add tests for new features
3. Update documentation
4. Ensure performance benchmarks are met
5. Submit a pull request

## License

The Enhanced Plugin Registry is part of the Jarvis project and is licensed under the same terms as the main project.
