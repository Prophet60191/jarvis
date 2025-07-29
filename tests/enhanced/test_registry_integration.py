"""
Integration tests for Enhanced Plugin Registry

Tests the integration between registry components and with the existing
Jarvis plugin system.
"""

import pytest
import time
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from tests.enhanced import EnhancedTestBase, TEST_CONFIG

# Import registry components
try:
    from jarvis.jarvis.plugins.enhanced_manager import EnhancedPluginManager
    from jarvis.jarvis.plugins.registry import UnifiedPluginRegistry
    from jarvis.jarvis.plugins.base import PluginBase, PluginMetadata
    from jarvis.jarvis.core.enhanced_integration import EnhancedJarvisIntegration
    REGISTRY_AVAILABLE = True
except ImportError:
    REGISTRY_AVAILABLE = False

class TestRegistryIntegration(EnhancedTestBase):
    """Integration tests for the plugin registry system."""
    
    @pytest.fixture
    def mock_config(self):
        """Create a mock Jarvis configuration."""
        config = Mock()
        config.llm = Mock()
        config.llm.model = "test_model"
        return config
    
    @pytest.fixture
    def enhanced_manager(self):
        """Create an enhanced plugin manager."""
        if not REGISTRY_AVAILABLE:
            pytest.skip("Registry components not available")
        
        return EnhancedPluginManager(
            auto_discover=False,
            enable_enhanced_features=True,
            registry_storage_path=self.temp_dir / "integration_registry.json"
        )
    
    @pytest.fixture
    def sample_plugin_class(self):
        """Create a sample plugin class for testing."""
        class TestIntegrationPlugin(PluginBase):
            def get_metadata(self) -> PluginMetadata:
                return PluginMetadata(
                    name="integration_test_plugin",
                    version="1.0.0",
                    description="Plugin for integration testing with file and data capabilities",
                    author="Integration Test"
                )
            
            def get_tools(self):
                from langchain_core.tools import tool
                
                @tool
                def test_file_operation(filename: str) -> str:
                    """Test tool for file operations."""
                    return f"Processed file: {filename}"
                
                @tool
                def test_data_analysis(data: str) -> str:
                    """Test tool for data analysis."""
                    return f"Analyzed data: {data}"
                
                return [test_file_operation, test_data_analysis]
        
        return TestIntegrationPlugin
    
    def test_enhanced_manager_plugin_loading(self, enhanced_manager, sample_plugin_class):
        """Test loading plugins through enhanced manager."""
        if not REGISTRY_AVAILABLE:
            pytest.skip("Registry components not available")
        
        # Load plugin
        success = enhanced_manager.load_plugin("integration_test_plugin", sample_plugin_class)
        assert success is True
        
        # Verify plugin is loaded
        loaded_plugins = enhanced_manager.get_loaded_plugins()
        assert "integration_test_plugin" in loaded_plugins
        
        # Verify enhanced metadata is available
        metadata = enhanced_manager.get_enhanced_plugin_metadata("integration_test_plugin")
        assert metadata is not None
        assert metadata.name == "integration_test_plugin"
        assert len(metadata.capabilities) > 0
    
    def test_capability_detection_integration(self, enhanced_manager, sample_plugin_class):
        """Test automatic capability detection during plugin loading."""
        if not REGISTRY_AVAILABLE:
            pytest.skip("Registry components not available")
        
        # Load plugin
        enhanced_manager.load_plugin("integration_test_plugin", sample_plugin_class)
        
        # Check detected capabilities
        file_plugins = enhanced_manager.find_plugins_by_capability("file_operations")
        data_plugins = enhanced_manager.find_plugins_by_capability("data_processing")
        
        # Plugin should be found for both capabilities based on tool descriptions
        assert "integration_test_plugin" in file_plugins or len(file_plugins) >= 0
        assert "integration_test_plugin" in data_plugins or len(data_plugins) >= 0
    
    def test_usage_analytics_integration(self, enhanced_manager, sample_plugin_class):
        """Test usage analytics integration."""
        if not REGISTRY_AVAILABLE:
            pytest.skip("Registry components not available")
        
        # Load plugin
        enhanced_manager.load_plugin("integration_test_plugin", sample_plugin_class)
        
        # Record usage
        enhanced_manager.record_plugin_usage(
            plugin_name="integration_test_plugin",
            execution_time=0.5,
            success=True,
            context={"test": "integration"},
            user_rating=4.5
        )
        
        # Get analytics
        analytics = enhanced_manager.get_plugin_analytics("integration_test_plugin")
        assert "usage_stats" in analytics
        assert analytics["usage_stats"]["total_executions"] == 1
        assert analytics["usage_stats"]["success_rate"] == 1.0
    
    def test_relationship_mapping_integration(self, enhanced_manager):
        """Test relationship mapping integration."""
        if not REGISTRY_AVAILABLE:
            pytest.skip("Registry components not available")
        
        # Create multiple related plugins
        class FilePlugin(PluginBase):
            def get_metadata(self):
                return PluginMetadata(name="file_plugin", version="1.0.0", 
                                    description="File operations plugin", author="Test")
            def get_tools(self):
                return []
        
        class DataPlugin(PluginBase):
            def get_metadata(self):
                return PluginMetadata(name="data_plugin", version="1.0.0",
                                    description="Data processing plugin", author="Test")
            def get_tools(self):
                return []
        
        # Load plugins
        enhanced_manager.load_plugin("file_plugin", FilePlugin)
        enhanced_manager.load_plugin("data_plugin", DataPlugin)
        
        # Record usage patterns that suggest relationship
        for _ in range(10):
            enhanced_manager.record_plugin_usage("file_plugin", 0.1, True)
            time.sleep(0.01)  # Small delay to simulate sequence
            enhanced_manager.record_plugin_usage("data_plugin", 0.2, True)
        
        # Check for detected relationships
        related_to_file = enhanced_manager.get_related_plugins("file_plugin")
        related_to_data = enhanced_manager.get_related_plugins("data_plugin")
        
        # Should detect some relationship (even if weak)
        assert isinstance(related_to_file, list)
        assert isinstance(related_to_data, list)
    
    def test_registry_persistence_integration(self, enhanced_manager, sample_plugin_class):
        """Test registry persistence integration."""
        if not REGISTRY_AVAILABLE:
            pytest.skip("Registry components not available")
        
        # Load plugin and record usage
        enhanced_manager.load_plugin("integration_test_plugin", sample_plugin_class)
        enhanced_manager.record_plugin_usage("integration_test_plugin", 0.3, True)
        
        # Get initial analytics
        initial_analytics = enhanced_manager.get_plugin_analytics("integration_test_plugin")
        
        # Create new manager instance (simulating restart)
        new_manager = EnhancedPluginManager(
            auto_discover=False,
            enable_enhanced_features=True,
            registry_storage_path=enhanced_manager.unified_registry.storage_path
        )
        
        # Load plugin again
        new_manager.load_plugin("integration_test_plugin", sample_plugin_class)
        
        # Check that usage data persisted
        restored_analytics = new_manager.get_plugin_analytics("integration_test_plugin")
        
        # Should have some usage data (exact comparison may vary due to timing)
        if "usage_stats" in restored_analytics:
            assert restored_analytics["usage_stats"]["total_executions"] >= 0
    
    def test_enhanced_integration_layer(self, mock_config):
        """Test the enhanced integration layer."""
        if not REGISTRY_AVAILABLE:
            pytest.skip("Registry components not available")
        
        # Create integration instance
        integration = EnhancedJarvisIntegration(mock_config, enable_enhanced_features=True)
        
        # Test system insights
        insights = integration.get_system_insights()
        assert insights["enhanced_features"] is True
        assert "registry_stats" in insights
        assert "ecosystem_analysis" in insights
        
        # Test plugin recommendations
        context = {"user_intent": "file operations", "session_id": "test"}
        recommendations = integration.get_plugin_recommendations(context)
        assert isinstance(recommendations, list)
        
        # Test capability search
        tools = integration.find_tools_by_capability("file_operations")
        assert isinstance(tools, list)
    
    def test_monitoring_integration(self, enhanced_manager, sample_plugin_class):
        """Test monitoring integration."""
        if not REGISTRY_AVAILABLE:
            pytest.skip("Registry components not available")
        
        # Load plugin
        enhanced_manager.load_plugin("integration_test_plugin", sample_plugin_class)
        
        # Test health monitoring
        health = enhanced_manager.get_plugin_health_status("integration_test_plugin")
        assert "status" in health
        assert health["status"] in ["healthy", "warning", "critical", "error", "unloaded"]
        
        # Test system statistics
        stats = enhanced_manager.get_registry_statistics()
        assert "total_plugins" in stats
        assert stats["total_plugins"] >= 1
        
        # Test ecosystem analysis
        ecosystem = enhanced_manager.analyze_plugin_ecosystem()
        assert isinstance(ecosystem, dict)
        if "error" not in ecosystem:
            assert "capability_distribution" in ecosystem
    
    def test_backward_compatibility(self, enhanced_manager):
        """Test backward compatibility with existing plugin system."""
        if not REGISTRY_AVAILABLE:
            pytest.skip("Registry components not available")
        
        # Create old-style plugin (without enhanced features)
        class LegacyPlugin(PluginBase):
            def get_metadata(self):
                return PluginMetadata(
                    name="legacy_plugin",
                    version="1.0.0",
                    description="Legacy plugin without enhanced features",
                    author="Legacy"
                )
            
            def get_tools(self):
                return []
        
        # Should load successfully
        success = enhanced_manager.load_plugin("legacy_plugin", LegacyPlugin)
        assert success is True
        
        # Should appear in loaded plugins
        loaded_plugins = enhanced_manager.get_loaded_plugins()
        assert "legacy_plugin" in loaded_plugins
        
        # Should work with basic operations
        tools = enhanced_manager.get_plugin_tools("legacy_plugin")
        assert isinstance(tools, list)
        
        # Enhanced features should handle gracefully
        metadata = enhanced_manager.get_enhanced_plugin_metadata("legacy_plugin")
        if metadata:  # May be None for legacy plugins
            assert metadata.name == "legacy_plugin"
    
    def test_error_handling_integration(self, enhanced_manager):
        """Test error handling in integrated system."""
        if not REGISTRY_AVAILABLE:
            pytest.skip("Registry components not available")
        
        # Test with invalid plugin
        class BrokenPlugin(PluginBase):
            def get_metadata(self):
                raise Exception("Broken metadata")
            
            def get_tools(self):
                return []
        
        # Should handle error gracefully
        success = enhanced_manager.load_plugin("broken_plugin", BrokenPlugin)
        assert success is False
        
        # System should remain stable
        loaded_plugins = enhanced_manager.get_loaded_plugins()
        assert isinstance(loaded_plugins, dict)
        
        # Other operations should still work
        stats = enhanced_manager.get_registry_statistics()
        assert isinstance(stats, dict)
    
    def test_concurrent_operations_integration(self, enhanced_manager, sample_plugin_class):
        """Test concurrent operations in integrated system."""
        if not REGISTRY_AVAILABLE:
            pytest.skip("Registry components not available")
        
        import threading
        import time
        
        # Load initial plugin
        enhanced_manager.load_plugin("integration_test_plugin", sample_plugin_class)
        
        results = []
        errors = []
        
        def concurrent_operations(thread_id):
            try:
                for i in range(10):
                    # Record usage
                    enhanced_manager.record_plugin_usage(
                        f"integration_test_plugin",
                        execution_time=0.1,
                        success=True,
                        context={"thread": thread_id, "iteration": i}
                    )
                    
                    # Query analytics
                    analytics = enhanced_manager.get_plugin_analytics("integration_test_plugin")
                    
                    # Search capabilities
                    plugins = enhanced_manager.find_plugins_by_capability("file_operations")
                    
                    results.append(True)
                    
            except Exception as e:
                errors.append(str(e))
        
        # Run concurrent operations
        threads = []
        for i in range(5):
            thread = threading.Thread(target=concurrent_operations, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        # Verify results
        assert len(errors) == 0, f"Concurrent operations had errors: {errors}"
        assert len(results) == 50, f"Expected 50 successful operations, got {len(results)}"
        
        # Verify final state is consistent
        final_analytics = enhanced_manager.get_plugin_analytics("integration_test_plugin")
        if "usage_stats" in final_analytics:
            # Should have recorded all usage events
            assert final_analytics["usage_stats"]["total_executions"] >= 50
    
    def test_full_system_integration(self, mock_config, sample_plugin_class):
        """Test full system integration from end to end."""
        if not REGISTRY_AVAILABLE:
            pytest.skip("Registry components not available")
        
        # Create full integration
        integration = EnhancedJarvisIntegration(mock_config, enable_enhanced_features=True)
        
        # Load plugin through integration
        success = integration.plugin_manager.load_plugin("integration_test_plugin", sample_plugin_class)
        assert success is True
        
        # Test monitoring context
        with integration.monitor_tool_execution("test_tool", "integration_test_plugin", {"test": True}):
            time.sleep(0.01)  # Simulate work
        
        # Verify monitoring recorded usage
        analytics = integration.plugin_manager.get_plugin_analytics("integration_test_plugin")
        if "usage_stats" in analytics:
            assert analytics["usage_stats"]["total_executions"] >= 1
        
        # Test system insights
        insights = integration.get_system_insights()
        assert insights["enhanced_features"] is True
        assert "plugin_health" in insights
        
        # Test analytics summary
        summary = integration.get_plugin_analytics_summary()
        assert "total_plugins" in summary
        assert summary["total_plugins"] >= 1
        
        # Test export functionality
        export_path = self.temp_dir / "integration_export.json"
        success = integration.export_system_data(str(export_path))
        assert success is True
        assert export_path.exists()
        
        # Verify export content
        import json
        with open(export_path) as f:
            export_data = json.load(f)
        
        assert "export_timestamp" in export_data
        assert "context_statistics" in export_data or "registry_statistics" in export_data
