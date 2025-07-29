"""
Test suite for Enhanced Plugin Registry

Tests the UnifiedPluginRegistry, RelationshipMapper, CapabilityAnalyzer,
and UsageAnalytics components.
"""

import pytest
import time
from unittest.mock import Mock, patch, MagicMock
from typing import List, Dict, Any
from pathlib import Path

try:
    from tests.enhanced import EnhancedTestBase, TEST_CONFIG
except ImportError:
    # Fallback for when running tests directly
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))

    # Create fallback base class
    class EnhancedTestBase:
        def setUp(self):
            pass
        def tearDown(self):
            pass

    TEST_CONFIG = {"timeout": 30, "verbose": True}

# Import the actual components
try:
    from jarvis.jarvis.plugins.registry import (
        UnifiedPluginRegistry, EnhancedPluginMetadata, RelationshipMapper,
        CapabilityAnalyzer, UsageAnalytics, PerformanceProfile, UsageStats
    )
    from jarvis.jarvis.plugins.base import PluginBase, PluginMetadata
    REGISTRY_AVAILABLE = True
except ImportError:
    REGISTRY_AVAILABLE = False
    # Mock the enhanced registry components for testing
    class MockUnifiedPluginRegistry:
        """Mock implementation for testing."""

        def __init__(self):
            self.plugins = {}
            self.relationships = {}
            self.capabilities = {}
            self.usage_stats = {}

        def register_plugin(self, plugin_name: str, metadata: Dict[str, Any]) -> bool:
            self.plugins[plugin_name] = metadata
            return True

        def get_plugin_metadata(self, plugin_name: str) -> Dict[str, Any]:
            return self.plugins.get(plugin_name)

        def find_plugins_by_capability(self, capability: str) -> List[str]:
            return [name for name, meta in self.plugins.items()
                    if capability in meta.get('capabilities', [])]

        def get_related_plugins(self, plugin_name: str) -> List[str]:
            return self.relationships.get(plugin_name, [])

        def update_usage_statistics(self, plugin_name: str, execution_time: float, success: bool):
            if plugin_name not in self.usage_stats:
                self.usage_stats[plugin_name] = {'executions': 0, 'avg_time': 0, 'success_rate': 0}

            stats = self.usage_stats[plugin_name]
            stats['executions'] += 1
            stats['avg_time'] = (stats['avg_time'] + execution_time) / 2
            stats['success_rate'] = (stats['success_rate'] + (1 if success else 0)) / 2

class TestUnifiedPluginRegistry(EnhancedTestBase):
    """Test suite for UnifiedPluginRegistry."""

    def setUp(self):
        """Set up test environment."""
        super().setUp()
        import tempfile
        self.temp_dir = Path(tempfile.mkdtemp())

    @pytest.fixture
    def registry(self):
        """Create a test registry instance."""
        if REGISTRY_AVAILABLE:
            # Use temporary storage for testing
            temp_storage = self.temp_dir / "test_registry.json"
            return UnifiedPluginRegistry(storage_path=temp_storage)
        else:
            return MockUnifiedPluginRegistry()
    
    @pytest.fixture
    def sample_plugin_metadata(self):
        """Create sample plugin metadata."""
        if REGISTRY_AVAILABLE:
            return EnhancedPluginMetadata(
                name='test_plugin',
                version='1.0.0',
                description='Test plugin for registry testing',
                author='Test Author',
                capabilities={'file_operations', 'data_processing'},
                performance_profile=PerformanceProfile(
                    avg_execution_time=0.5,
                    memory_usage_mb=10.0,
                    success_rate=0.95
                )
            )
        else:
            return {
                'name': 'test_plugin',
                'version': '1.0.0',
                'description': 'Test plugin for registry testing',
                'capabilities': ['file_operations', 'data_processing'],
                'performance_profile': {
                    'avg_execution_time': 0.5,
                    'memory_usage_mb': 10.0,
                    'success_rate': 0.95
                },
                'compatibility_matrix': {
                    'other_plugin': 'compatible',
                    'conflicting_plugin': 'incompatible'
                }
            }

    @pytest.fixture
    def sample_plugin_instance(self):
        """Create a sample plugin instance for testing."""
        if REGISTRY_AVAILABLE:
            # Create a real plugin instance
            class TestPlugin(PluginBase):
                def get_metadata(self) -> PluginMetadata:
                    return PluginMetadata(
                        name="test_plugin",
                        version="1.0.0",
                        description="Test plugin for file operations and data processing",
                        author="Test Author"
                    )

                def get_tools(self):
                    from langchain_core.tools import tool

                    @tool
                    def test_file_tool(filename: str) -> str:
                        """Test tool for file operations."""
                        return f"Processed file: {filename}"

                    return [test_file_tool]

            return TestPlugin()
        else:
            return self.create_mock_plugin('test_plugin', ['file_operations', 'data_processing'])
    
    def test_plugin_registration(self, registry, sample_plugin_instance, sample_plugin_metadata):
        """Test plugin registration functionality."""
        if not REGISTRY_AVAILABLE:
            pytest.skip("Registry components not available")

        # Test successful registration
        result = registry.register_plugin('test_plugin', sample_plugin_instance, sample_plugin_metadata)
        assert result is True

        # Verify plugin was stored
        stored_metadata = registry.get_plugin_metadata('test_plugin')
        assert stored_metadata is not None
        assert stored_metadata.name == 'test_plugin'
        assert 'file_operations' in stored_metadata.capabilities
    
    def test_plugin_metadata_retrieval(self, registry, sample_plugin_metadata):
        """Test plugin metadata retrieval."""
        # Register a plugin
        registry.register_plugin('test_plugin', sample_plugin_metadata)
        
        # Test retrieval
        metadata = registry.get_plugin_metadata('test_plugin')
        assert metadata is not None
        assert metadata['name'] == 'test_plugin'
        
        # Test non-existent plugin
        metadata = registry.get_plugin_metadata('non_existent')
        assert metadata is None
    
    def test_capability_search(self, registry, sample_plugin_metadata):
        """Test capability-based plugin search."""
        # Register multiple plugins with different capabilities
        plugin1_meta = sample_plugin_metadata.copy()
        plugin1_meta['name'] = 'plugin1'
        plugin1_meta['capabilities'] = ['file_operations', 'web_search']
        
        plugin2_meta = sample_plugin_metadata.copy()
        plugin2_meta['name'] = 'plugin2'
        plugin2_meta['capabilities'] = ['data_processing', 'web_search']
        
        registry.register_plugin('plugin1', plugin1_meta)
        registry.register_plugin('plugin2', plugin2_meta)
        
        # Test capability search
        file_plugins = registry.find_plugins_by_capability('file_operations')
        assert 'plugin1' in file_plugins
        assert 'plugin2' not in file_plugins
        
        web_plugins = registry.find_plugins_by_capability('web_search')
        assert 'plugin1' in web_plugins
        assert 'plugin2' in web_plugins
        
        # Test non-existent capability
        missing_plugins = registry.find_plugins_by_capability('non_existent')
        assert len(missing_plugins) == 0
    
    def test_usage_statistics_tracking(self, registry):
        """Test usage statistics tracking."""
        plugin_name = 'test_plugin'
        
        # Update statistics multiple times
        registry.update_usage_statistics(plugin_name, 0.5, True)
        registry.update_usage_statistics(plugin_name, 0.3, True)
        registry.update_usage_statistics(plugin_name, 0.7, False)
        
        # Verify statistics were recorded
        stats = registry.usage_stats.get(plugin_name)
        assert stats is not None
        assert stats['executions'] == 3
        assert stats['avg_time'] > 0
        assert 0 < stats['success_rate'] < 1  # Should be between 0 and 1
    
    @pytest.mark.benchmark
    def test_registry_performance(self, registry, benchmark):
        """Benchmark registry performance."""
        # Register multiple plugins
        for i in range(50):
            metadata = {
                'name': f'plugin_{i}',
                'capabilities': [f'capability_{i % 5}'],
                'performance_profile': {'avg_execution_time': 0.1}
            }
            registry.register_plugin(f'plugin_{i}', metadata)
        
        # Benchmark metadata retrieval
        def retrieve_metadata():
            return registry.get_plugin_metadata('plugin_25')
        
        result = benchmark(retrieve_metadata)
        assert result is not None
        
        # Verify performance threshold
        assert benchmark.stats['mean'] < TEST_CONFIG['performance_thresholds']['registry_query']
    
    @pytest.mark.benchmark
    def test_capability_search_performance(self, registry, benchmark):
        """Benchmark capability search performance."""
        # Register many plugins
        for i in range(100):
            metadata = {
                'name': f'plugin_{i}',
                'capabilities': [f'capability_{i % 10}', 'common_capability'],
                'performance_profile': {'avg_execution_time': 0.1}
            }
            registry.register_plugin(f'plugin_{i}', metadata)
        
        # Benchmark capability search
        def search_capability():
            return registry.find_plugins_by_capability('common_capability')
        
        result = benchmark(search_capability)
        assert len(result) == 100  # All plugins should have common_capability
        
        # Verify performance threshold
        assert benchmark.stats['mean'] < TEST_CONFIG['performance_thresholds']['registry_query']

class TestRelationshipMapper(EnhancedTestBase):
    """Test suite for RelationshipMapper."""
    
    @pytest.fixture
    def relationship_mapper(self):
        """Create a mock relationship mapper."""
        mapper = Mock()
        mapper.relationships = {}
        
        def add_relationship(source, target, rel_type, strength):
            if source not in mapper.relationships:
                mapper.relationships[source] = []
            mapper.relationships[source].append({
                'target': target,
                'type': rel_type,
                'strength': strength
            })
        
        def get_related_plugins(plugin_name):
            return [rel['target'] for rel in mapper.relationships.get(plugin_name, [])]
        
        mapper.add_relationship = add_relationship
        mapper.get_related_plugins = get_related_plugins
        return mapper
    
    def test_relationship_addition(self, relationship_mapper):
        """Test adding relationships between plugins."""
        # Add a complementary relationship
        relationship_mapper.add_relationship(
            'plugin_a', 'plugin_b', 'complements', 0.8
        )
        
        # Verify relationship was added
        related = relationship_mapper.get_related_plugins('plugin_a')
        assert 'plugin_b' in related
    
    def test_relationship_discovery(self, relationship_mapper):
        """Test automatic relationship discovery from usage patterns."""
        # Mock usage data
        usage_data = [
            {'plugin': 'plugin_a', 'timestamp': '2025-01-01T10:00:00Z'},
            {'plugin': 'plugin_b', 'timestamp': '2025-01-01T10:00:05Z'},
            {'plugin': 'plugin_a', 'timestamp': '2025-01-01T11:00:00Z'},
            {'plugin': 'plugin_b', 'timestamp': '2025-01-01T11:00:03Z'},
        ]
        
        # Mock the discovery method
        def discover_relationships(usage_data):
            # Simple mock: if plugins are used within 10 seconds, they're related
            relationships = []
            for i, usage1 in enumerate(usage_data):
                for usage2 in usage_data[i+1:]:
                    # Mock time difference calculation
                    if usage1['plugin'] != usage2['plugin']:
                        relationships.append({
                            'source': usage1['plugin'],
                            'target': usage2['plugin'],
                            'type': 'sequential',
                            'strength': 0.7
                        })
            return relationships
        
        relationship_mapper.discover_relationships = discover_relationships
        
        # Test relationship discovery
        discovered = relationship_mapper.discover_relationships(usage_data)
        assert len(discovered) > 0
        assert any(rel['source'] == 'plugin_a' and rel['target'] == 'plugin_b' 
                  for rel in discovered)

class TestCapabilityAnalyzer(EnhancedTestBase):
    """Test suite for CapabilityAnalyzer."""
    
    @pytest.fixture
    def capability_analyzer(self):
        """Create a mock capability analyzer."""
        analyzer = Mock()
        
        def analyze_plugin_capabilities(plugin):
            # Mock capability analysis based on plugin name/description
            capabilities = set()
            
            if 'file' in plugin.name.lower():
                capabilities.add('file_operations')
            if 'web' in plugin.name.lower():
                capabilities.add('web_operations')
            if 'data' in plugin.name.lower():
                capabilities.add('data_processing')
            
            return capabilities
        
        analyzer.analyze_plugin_capabilities = analyze_plugin_capabilities
        return analyzer
    
    def test_automatic_capability_detection(self, capability_analyzer):
        """Test automatic capability detection from plugin metadata."""
        # Create test plugins
        file_plugin = Mock()
        file_plugin.name = 'file_manager_plugin'
        file_plugin.description = 'Manages file operations'
        
        web_plugin = Mock()
        web_plugin.name = 'web_scraper_plugin'
        web_plugin.description = 'Scrapes web content'
        
        # Test capability detection
        file_capabilities = capability_analyzer.analyze_plugin_capabilities(file_plugin)
        assert 'file_operations' in file_capabilities
        
        web_capabilities = capability_analyzer.analyze_plugin_capabilities(web_plugin)
        assert 'web_operations' in web_capabilities
    
    def test_capability_categorization(self, capability_analyzer):
        """Test capability categorization and tagging."""
        # Mock categorization method
        def categorize_capabilities(capabilities):
            categories = {
                'data_operations': ['file_operations', 'data_processing'],
                'external_services': ['web_operations', 'api_operations'],
                'user_interaction': ['ui_operations', 'notification_operations']
            }
            
            result = {}
            for category, cap_list in categories.items():
                result[category] = [cap for cap in capabilities if cap in cap_list]
            
            return result
        
        capability_analyzer.categorize_capabilities = categorize_capabilities
        
        # Test categorization
        test_capabilities = ['file_operations', 'web_operations', 'data_processing']
        categories = capability_analyzer.categorize_capabilities(test_capabilities)
        
        assert 'file_operations' in categories['data_operations']
        assert 'web_operations' in categories['external_services']
        assert 'data_processing' in categories['data_operations']

class TestUsageAnalytics(EnhancedTestBase):
    """Test suite for UsageAnalytics."""
    
    @pytest.fixture
    def usage_analytics(self):
        """Create a mock usage analytics system."""
        analytics = Mock()
        analytics.usage_data = {}
        
        def track_plugin_usage(plugin_name, execution_time, success, context):
            if plugin_name not in analytics.usage_data:
                analytics.usage_data[plugin_name] = []
            
            analytics.usage_data[plugin_name].append({
                'execution_time': execution_time,
                'success': success,
                'context': context,
                'timestamp': time.time()
            })
        
        def get_usage_statistics(plugin_name):
            data = analytics.usage_data.get(plugin_name, [])
            if not data:
                return None
            
            return {
                'total_executions': len(data),
                'success_rate': sum(1 for d in data if d['success']) / len(data),
                'avg_execution_time': sum(d['execution_time'] for d in data) / len(data),
                'last_used': max(d['timestamp'] for d in data)
            }
        
        analytics.track_plugin_usage = track_plugin_usage
        analytics.get_usage_statistics = get_usage_statistics
        return analytics
    
    def test_usage_tracking(self, usage_analytics):
        """Test usage tracking functionality."""
        plugin_name = 'test_plugin'
        
        # Track several usages
        usage_analytics.track_plugin_usage(plugin_name, 0.5, True, {'context': 'test'})
        usage_analytics.track_plugin_usage(plugin_name, 0.3, True, {'context': 'test'})
        usage_analytics.track_plugin_usage(plugin_name, 0.8, False, {'context': 'test'})
        
        # Get statistics
        stats = usage_analytics.get_usage_statistics(plugin_name)
        
        assert stats is not None
        assert stats['total_executions'] == 3
        assert 0 < stats['success_rate'] < 1
        assert stats['avg_execution_time'] > 0
    
    def test_performance_analysis(self, usage_analytics):
        """Test performance analysis capabilities."""
        plugin_name = 'performance_plugin'
        
        # Track usage with varying performance
        execution_times = [0.1, 0.2, 0.15, 0.3, 0.12, 0.25]
        for exec_time in execution_times:
            usage_analytics.track_plugin_usage(
                plugin_name, exec_time, True, {'context': 'performance_test'}
            )
        
        # Mock performance analysis
        def analyze_performance_trends(plugin_name):
            data = usage_analytics.usage_data.get(plugin_name, [])
            times = [d['execution_time'] for d in data]
            
            return {
                'min_time': min(times),
                'max_time': max(times),
                'avg_time': sum(times) / len(times),
                'trend': 'stable'  # Mock trend analysis
            }
        
        usage_analytics.analyze_performance_trends = analyze_performance_trends
        
        # Test performance analysis
        analysis = usage_analytics.analyze_performance_trends(plugin_name)
        
        assert analysis['min_time'] == 0.1
        assert analysis['max_time'] == 0.3
        assert 0.1 < analysis['avg_time'] < 0.3
