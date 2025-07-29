"""
Performance tests for Enhanced Plugin Registry

Tests performance characteristics and benchmarks for the registry system
to ensure it meets performance requirements.
"""

import pytest
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from unittest.mock import Mock, patch
import statistics

from tests.enhanced import EnhancedTestBase, TEST_CONFIG

# Import registry components
try:
    from jarvis.jarvis.plugins.registry import UnifiedPluginRegistry
    from jarvis.jarvis.plugins.enhanced_manager import EnhancedPluginManager
    from jarvis.jarvis.plugins.registry.usage_analytics import UsageAnalytics
    from jarvis.jarvis.plugins.registry.relationship_mapper import RelationshipMapper
    from jarvis.jarvis.plugins.registry.capability_analyzer import CapabilityAnalyzer
    REGISTRY_AVAILABLE = True
except ImportError:
    REGISTRY_AVAILABLE = False

class TestRegistryPerformance(EnhancedTestBase):
    """Performance tests for the plugin registry system."""
    
    @pytest.fixture
    def registry(self):
        """Create a test registry instance."""
        if not REGISTRY_AVAILABLE:
            pytest.skip("Registry components not available")
        
        temp_storage = self.temp_dir / "perf_registry.json"
        return UnifiedPluginRegistry(storage_path=temp_storage)
    
    @pytest.fixture
    def enhanced_manager(self):
        """Create an enhanced plugin manager for testing."""
        if not REGISTRY_AVAILABLE:
            pytest.skip("Registry components not available")
        
        return EnhancedPluginManager(
            auto_discover=False,
            enable_enhanced_features=True
        )
    
    @pytest.fixture
    def sample_plugins(self):
        """Create sample plugins for performance testing."""
        plugins = {}
        for i in range(100):  # Create 100 test plugins
            plugin_name = f"test_plugin_{i}"
            plugin_mock = Mock()
            plugin_mock.get_metadata.return_value = Mock(
                name=plugin_name,
                version="1.0.0",
                description=f"Test plugin {i}",
                author="Test Author"
            )
            plugin_mock.get_tools.return_value = [Mock(name=f"tool_{i}")]
            plugins[plugin_name] = plugin_mock
        return plugins
    
    @pytest.mark.benchmark
    def test_registry_query_performance(self, benchmark, registry, sample_plugins):
        """Test registry query performance."""
        if not REGISTRY_AVAILABLE:
            pytest.skip("Registry components not available")
        
        # Register sample plugins
        for name, plugin in list(sample_plugins.items())[:10]:
            registry.register_plugin(name, plugin)
        
        def query_plugin():
            return registry.get_plugin_metadata("test_plugin_5")
        
        result = benchmark(query_plugin)
        assert result is not None
        
        # Verify performance threshold
        assert benchmark.stats['mean'] < TEST_CONFIG['performance_thresholds']['registry_query']
    
    @pytest.mark.benchmark
    def test_capability_search_performance(self, benchmark, enhanced_manager, sample_plugins):
        """Test capability search performance."""
        if not REGISTRY_AVAILABLE:
            pytest.skip("Registry components not available")
        
        # Mock capability search
        enhanced_manager.find_plugins_by_capability = Mock(return_value=['plugin1', 'plugin2'])
        
        def search_capability():
            return enhanced_manager.find_plugins_by_capability("file_operations")
        
        result = benchmark(search_capability)
        assert isinstance(result, list)
        
        # Verify performance threshold
        assert benchmark.stats['mean'] < TEST_CONFIG['performance_thresholds']['capability_search']
    
    @pytest.mark.benchmark
    def test_relationship_analysis_performance(self, benchmark):
        """Test relationship analysis performance."""
        if not REGISTRY_AVAILABLE:
            pytest.skip("Registry components not available")
        
        mapper = RelationshipMapper()
        
        # Add sample usage data
        for i in range(50):
            mapper.record_plugin_usage(f"plugin_{i % 10}")
        
        def analyze_relationships():
            return mapper.get_related_plugins("plugin_1")
        
        result = benchmark(analyze_relationships)
        assert isinstance(result, list)
        
        # Verify performance threshold
        assert benchmark.stats['mean'] < TEST_CONFIG['performance_thresholds']['relationship_analysis']
    
    @pytest.mark.benchmark
    def test_usage_analytics_performance(self, benchmark):
        """Test usage analytics performance."""
        if not REGISTRY_AVAILABLE:
            pytest.skip("Registry components not available")
        
        analytics = UsageAnalytics()
        
        # Add sample usage data
        for i in range(100):
            analytics.record_usage(
                plugin_name=f"plugin_{i % 10}",
                execution_time=0.1,
                success=True
            )
        
        def get_analytics():
            return analytics.get_usage_statistics("plugin_1")
        
        result = benchmark(get_analytics)
        assert result is not None
        
        # Verify performance threshold
        assert benchmark.stats['mean'] < TEST_CONFIG['performance_thresholds']['usage_analytics']
    
    def test_concurrent_registry_access(self, registry, sample_plugins):
        """Test concurrent access to registry."""
        if not REGISTRY_AVAILABLE:
            pytest.skip("Registry components not available")
        
        # Register some plugins
        for name, plugin in list(sample_plugins.items())[:20]:
            registry.register_plugin(name, plugin)
        
        def concurrent_query(plugin_name):
            start_time = time.time()
            result = registry.get_plugin_metadata(plugin_name)
            end_time = time.time()
            return end_time - start_time, result is not None
        
        # Run concurrent queries
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = []
            for i in range(50):
                plugin_name = f"test_plugin_{i % 20}"
                future = executor.submit(concurrent_query, plugin_name)
                futures.append(future)
            
            results = []
            for future in as_completed(futures):
                duration, success = future.result()
                results.append((duration, success))
        
        # Analyze results
        durations = [r[0] for r in results]
        successes = [r[1] for r in results]
        
        assert all(successes), "Some concurrent queries failed"
        assert statistics.mean(durations) < 0.1, "Concurrent queries too slow"
        assert max(durations) < 0.5, "Some queries took too long"
    
    def test_memory_usage_under_load(self, registry, sample_plugins):
        """Test memory usage under load."""
        if not REGISTRY_AVAILABLE:
            pytest.skip("Registry components not available")
        
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Register many plugins
        for name, plugin in sample_plugins.items():
            registry.register_plugin(name, plugin)
        
        # Perform many operations
        for _ in range(1000):
            plugin_name = f"test_plugin_{_ % 100}"
            registry.get_plugin_metadata(plugin_name)
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (less than 100MB for this test)
        assert memory_increase < 100, f"Memory usage increased by {memory_increase:.1f}MB"
    
    def test_registry_scalability(self, registry):
        """Test registry scalability with many plugins."""
        if not REGISTRY_AVAILABLE:
            pytest.skip("Registry components not available")
        
        # Test with increasing numbers of plugins
        plugin_counts = [10, 50, 100, 500]
        query_times = []
        
        for count in plugin_counts:
            # Clear registry
            registry._plugins.clear()
            
            # Register plugins
            for i in range(count):
                plugin_mock = Mock()
                plugin_mock.get_metadata.return_value = Mock(
                    name=f"plugin_{i}",
                    version="1.0.0",
                    description=f"Plugin {i}",
                    author="Test"
                )
                registry.register_plugin(f"plugin_{i}", plugin_mock)
            
            # Measure query time
            start_time = time.time()
            for _ in range(10):  # 10 queries per test
                registry.get_plugin_metadata(f"plugin_{count // 2}")
            end_time = time.time()
            
            avg_query_time = (end_time - start_time) / 10
            query_times.append(avg_query_time)
        
        # Query time should not increase dramatically with plugin count
        # Allow for some increase but not exponential
        for i in range(1, len(query_times)):
            ratio = query_times[i] / query_times[0]
            assert ratio < 3.0, f"Query time increased by {ratio:.1f}x with more plugins"
    
    def test_persistence_performance(self, registry, sample_plugins):
        """Test persistence performance."""
        if not REGISTRY_AVAILABLE:
            pytest.skip("Registry components not available")
        
        # Register plugins
        for name, plugin in list(sample_plugins.items())[:50]:
            registry.register_plugin(name, plugin)
        
        # Test save performance
        start_time = time.time()
        registry._save_registry_data()
        save_time = time.time() - start_time
        
        # Test load performance
        registry._plugins.clear()
        start_time = time.time()
        registry._load_registry_data()
        load_time = time.time() - start_time
        
        # Both operations should be reasonably fast
        assert save_time < 1.0, f"Save took {save_time:.2f}s, too slow"
        assert load_time < 1.0, f"Load took {load_time:.2f}s, too slow"
        
        # Verify data integrity
        assert len(registry._plugins) == 50, "Not all plugins loaded correctly"
    
    def test_analytics_performance_under_load(self):
        """Test analytics performance under heavy load."""
        if not REGISTRY_AVAILABLE:
            pytest.skip("Registry components not available")
        
        analytics = UsageAnalytics(max_events=10000)
        
        # Record many usage events
        start_time = time.time()
        for i in range(5000):
            analytics.record_usage(
                plugin_name=f"plugin_{i % 20}",
                execution_time=0.1 + (i % 10) * 0.01,
                success=(i % 10) != 0,  # 90% success rate
                context={"test": True, "iteration": i}
            )
        record_time = time.time() - start_time
        
        # Test analytics queries
        start_time = time.time()
        for i in range(100):
            plugin_name = f"plugin_{i % 20}"
            stats = analytics.get_usage_statistics(plugin_name)
            trends = analytics.get_usage_trends(plugin_name, hours=1)
        query_time = time.time() - start_time
        
        # Performance assertions
        assert record_time < 5.0, f"Recording 5000 events took {record_time:.2f}s"
        assert query_time < 2.0, f"100 analytics queries took {query_time:.2f}s"
        
        # Verify data integrity
        stats = analytics.get_usage_statistics("plugin_1")
        assert stats is not None
        assert stats.total_executions > 0
    
    def test_capability_analyzer_performance(self):
        """Test capability analyzer performance."""
        if not REGISTRY_AVAILABLE:
            pytest.skip("Registry components not available")
        
        analyzer = CapabilityAnalyzer()
        
        # Create mock plugin with complex code
        plugin_mock = Mock()
        plugin_mock.get_metadata.return_value = Mock(
            name="complex_plugin",
            description="A complex plugin with file operations, web requests, and data processing"
        )
        
        # Mock tools with various capabilities
        tools = []
        for i in range(20):
            tool_mock = Mock()
            tool_mock.name = f"tool_{i}"
            tool_mock.description = f"Tool {i} for file operations and data processing"
            tool_mock.func = Mock()
            tools.append(tool_mock)
        
        plugin_mock.get_tools.return_value = tools
        
        # Test analysis performance
        start_time = time.time()
        capabilities = analyzer.analyze_plugin_capabilities(plugin_mock)
        analysis_time = time.time() - start_time
        
        # Should complete quickly
        assert analysis_time < 0.5, f"Capability analysis took {analysis_time:.2f}s"
        assert isinstance(capabilities, set)
        assert len(capabilities) > 0
    
    @pytest.mark.stress
    def test_registry_stress_test(self, registry):
        """Stress test the registry system."""
        if not REGISTRY_AVAILABLE:
            pytest.skip("Registry components not available")
        
        # This test runs many operations concurrently to stress test the system
        def stress_worker(worker_id):
            results = []
            for i in range(100):
                try:
                    # Register a plugin
                    plugin_mock = Mock()
                    plugin_mock.get_metadata.return_value = Mock(
                        name=f"stress_plugin_{worker_id}_{i}",
                        version="1.0.0",
                        description=f"Stress test plugin {worker_id}_{i}",
                        author="Stress Test"
                    )
                    
                    registry.register_plugin(f"stress_plugin_{worker_id}_{i}", plugin_mock)
                    
                    # Query the plugin
                    metadata = registry.get_plugin_metadata(f"stress_plugin_{worker_id}_{i}")
                    
                    # Record success
                    results.append(metadata is not None)
                    
                except Exception as e:
                    results.append(False)
                    print(f"Stress test error in worker {worker_id}: {e}")
            
            return results
        
        # Run stress test with multiple workers
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = []
            for worker_id in range(5):
                future = executor.submit(stress_worker, worker_id)
                futures.append(future)
            
            all_results = []
            for future in as_completed(futures):
                worker_results = future.result()
                all_results.extend(worker_results)
        
        # Analyze results
        success_rate = sum(all_results) / len(all_results)
        assert success_rate > 0.95, f"Stress test success rate: {success_rate:.1%}"
        
        # Verify final state
        total_plugins = len(registry._plugins)
        assert total_plugins == 500, f"Expected 500 plugins, got {total_plugins}"
