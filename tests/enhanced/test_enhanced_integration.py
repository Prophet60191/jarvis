"""
Test suite for Enhanced Jarvis Integration

Tests the integration layer between enhanced features and the existing
Jarvis system.
"""

import pytest
import asyncio
import time
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from typing import Dict, Any

from tests.enhanced import EnhancedTestBase, TEST_CONFIG

# Import integration components
try:
    from jarvis.jarvis.core.enhanced_integration import (
        EnhancedJarvisIntegration, get_integration_instance, 
        initialize_enhanced_jarvis, monitor_tool_execution
    )
    from jarvis.jarvis.config import JarvisConfig
    from jarvis.jarvis.core.agent import JarvisAgent
    INTEGRATION_AVAILABLE = True
except ImportError:
    INTEGRATION_AVAILABLE = False

class TestEnhancedJarvisIntegration(EnhancedTestBase):
    """Test suite for EnhancedJarvisIntegration."""
    
    @pytest.fixture
    def mock_config(self):
        """Create a mock Jarvis configuration."""
        config = Mock(spec=JarvisConfig)
        config.llm = Mock()
        config.llm.model = "test_model"
        config.rag = Mock()
        config.rag.enabled = True
        return config
    
    @pytest.fixture
    def integration(self, mock_config):
        """Create an integration instance for testing."""
        if INTEGRATION_AVAILABLE:
            return EnhancedJarvisIntegration(mock_config, enable_enhanced_features=True)
        else:
            pytest.skip("Integration components not available")
    
    @pytest.fixture
    def mock_agent(self):
        """Create a mock JarvisAgent."""
        agent = Mock(spec=JarvisAgent)
        agent.process_input = AsyncMock(return_value="Test response")
        agent.initialize = Mock()
        agent.session_id = "test_session"
        return agent
    
    def test_integration_initialization(self, mock_config):
        """Test integration initialization."""
        if not INTEGRATION_AVAILABLE:
            pytest.skip("Integration components not available")
        
        # Test with enhanced features enabled
        integration = EnhancedJarvisIntegration(mock_config, enable_enhanced_features=True)
        assert integration.enhanced_features_enabled is True
        assert integration.plugin_manager is not None
        
        # Test with enhanced features disabled
        integration_disabled = EnhancedJarvisIntegration(mock_config, enable_enhanced_features=False)
        assert integration_disabled.enhanced_features_enabled is False
    
    def test_agent_enhancement(self, integration, mock_agent):
        """Test agent enhancement with enhanced features."""
        if not INTEGRATION_AVAILABLE:
            pytest.skip("Integration components not available")
        
        # Mock plugin manager methods
        integration.plugin_manager.get_all_tools = Mock(return_value=[])
        integration.plugin_manager.get_loaded_plugins = Mock(return_value={})
        
        # Enhance the agent
        enhanced_agent = integration.initialize_agent_with_enhanced_features(mock_agent)
        
        # Verify agent was initialized with tools
        mock_agent.initialize.assert_called_once()
        
        # Verify the agent is the same instance (enhanced in place)
        assert enhanced_agent is mock_agent
    
    @pytest.mark.asyncio
    async def test_enhanced_process_input(self, integration, mock_agent):
        """Test enhanced process_input with analytics."""
        if not INTEGRATION_AVAILABLE:
            pytest.skip("Integration components not available")
        
        # Mock plugin manager methods
        integration.plugin_manager.get_all_tools = Mock(return_value=[])
        integration.plugin_manager.get_loaded_plugins = Mock(return_value={})
        integration.plugin_manager.unified_registry = Mock()
        integration.plugin_manager.unified_registry.usage_analytics = Mock()
        
        # Enhance the agent
        enhanced_agent = integration.initialize_agent_with_enhanced_features(mock_agent)
        
        # Test enhanced process_input
        result = await enhanced_agent.process_input("test input")
        
        # Verify original method was called
        mock_agent.process_input.assert_called_once_with("test input")
        assert result == "Test response"
        
        # Verify analytics were recorded
        integration.plugin_manager.unified_registry.usage_analytics.record_usage.assert_called_once()
    
    def test_plugin_recommendations(self, integration):
        """Test plugin recommendation functionality."""
        if not INTEGRATION_AVAILABLE:
            pytest.skip("Integration components not available")
        
        # Mock plugin manager
        integration.plugin_manager.get_plugin_recommendations = Mock(return_value=['plugin1', 'plugin2'])
        
        context = {"user_intent": "file operations", "active_plugins": []}
        recommendations = integration.get_plugin_recommendations(context)
        
        assert recommendations == ['plugin1', 'plugin2']
        integration.plugin_manager.get_plugin_recommendations.assert_called_once_with(context)
    
    def test_capability_search(self, integration):
        """Test finding tools by capability."""
        if not INTEGRATION_AVAILABLE:
            pytest.skip("Integration components not available")
        
        # Mock plugin manager methods
        integration.plugin_manager.find_plugins_by_capability = Mock(return_value=['file_plugin'])
        integration.plugin_manager.get_plugin_tools = Mock(return_value=[
            Mock(name='file_read_tool'),
            Mock(name='file_write_tool')
        ])
        
        tools = integration.find_tools_by_capability('file_operations')
        
        assert 'file_read_tool' in tools
        assert 'file_write_tool' in tools
        integration.plugin_manager.find_plugins_by_capability.assert_called_once_with('file_operations')
    
    def test_system_insights(self, integration):
        """Test system insights generation."""
        if not INTEGRATION_AVAILABLE:
            pytest.skip("Integration components not available")
        
        # Mock plugin manager methods
        integration.plugin_manager.get_registry_statistics = Mock(return_value={'total_plugins': 5})
        integration.plugin_manager.analyze_plugin_ecosystem = Mock(return_value={'ecosystem_health': 'good'})
        integration.plugin_manager.get_loaded_plugins = Mock(return_value=['plugin1', 'plugin2'])
        integration.plugin_manager.get_plugin_health_status = Mock(return_value={'status': 'healthy'})
        
        insights = integration.get_system_insights()
        
        assert insights['enhanced_features'] is True
        assert insights['registry_stats']['total_plugins'] == 5
        assert insights['ecosystem_analysis']['ecosystem_health'] == 'good'
        assert 'plugin_health' in insights
    
    def test_plugin_optimization(self, integration):
        """Test plugin selection optimization."""
        if not INTEGRATION_AVAILABLE:
            pytest.skip("Integration components not available")
        
        # Mock plugin manager methods
        integration.plugin_manager.find_plugins_by_capability = Mock(return_value=['file_plugin'])
        integration.plugin_manager.get_plugin_recommendations = Mock(return_value=['recommended_plugin'])
        integration.plugin_manager.unified_registry = Mock()
        integration.plugin_manager.unified_registry.usage_analytics = Mock()
        integration.plugin_manager.unified_registry.usage_analytics.get_top_plugins = Mock(
            return_value=[('top_plugin', 0.9)]
        )
        
        # Test with file-related intent
        optimized = integration.optimize_plugin_selection("read my files", {})
        
        assert 'file_plugin' in optimized
        assert 'recommended_plugin' in optimized
    
    def test_tool_execution_monitoring(self, integration):
        """Test tool execution monitoring context manager."""
        if not INTEGRATION_AVAILABLE:
            pytest.skip("Integration components not available")
        
        # Mock plugin manager
        integration.plugin_manager.record_plugin_usage = Mock()
        
        # Test successful execution
        with integration.monitor_tool_execution('test_tool', 'test_plugin', {'context': 'test'}):
            time.sleep(0.01)  # Simulate some work
        
        # Verify usage was recorded
        integration.plugin_manager.record_plugin_usage.assert_called_once()
        call_args = integration.plugin_manager.record_plugin_usage.call_args
        assert call_args[1]['plugin_name'] == 'test_plugin'
        assert call_args[1]['success'] is True
        assert call_args[1]['execution_time'] > 0
    
    def test_tool_execution_monitoring_with_error(self, integration):
        """Test tool execution monitoring with error."""
        if not INTEGRATION_AVAILABLE:
            pytest.skip("Integration components not available")
        
        # Mock plugin manager
        integration.plugin_manager.record_plugin_usage = Mock()
        
        # Test execution with error
        with pytest.raises(ValueError):
            with integration.monitor_tool_execution('test_tool', 'test_plugin'):
                raise ValueError("Test error")
        
        # Verify usage was recorded with error
        integration.plugin_manager.record_plugin_usage.assert_called_once()
        call_args = integration.plugin_manager.record_plugin_usage.call_args
        assert call_args[1]['success'] is False
        assert call_args[1]['error_message'] == "Test error"
    
    def test_execution_hooks(self, integration):
        """Test tool execution hooks."""
        if not INTEGRATION_AVAILABLE:
            pytest.skip("Integration components not available")
        
        # Mock plugin manager
        integration.plugin_manager.record_plugin_usage = Mock()
        
        # Add a test hook
        hook_called = []
        def test_hook(tool_name, plugin_name, execution_time, success, context, error_message):
            hook_called.append({
                'tool_name': tool_name,
                'plugin_name': plugin_name,
                'success': success
            })
        
        integration.add_tool_execution_hook(test_hook)
        
        # Execute with monitoring
        with integration.monitor_tool_execution('test_tool', 'test_plugin'):
            pass
        
        # Verify hook was called
        assert len(hook_called) == 1
        assert hook_called[0]['tool_name'] == 'test_tool'
        assert hook_called[0]['plugin_name'] == 'test_plugin'
        assert hook_called[0]['success'] is True
    
    def test_analytics_summary(self, integration):
        """Test analytics summary generation."""
        if not INTEGRATION_AVAILABLE:
            pytest.skip("Integration components not available")
        
        # Mock plugin manager methods
        integration.plugin_manager.get_loaded_plugins = Mock(return_value={'plugin1': Mock(), 'plugin2': Mock()})
        integration.plugin_manager.get_all_tools = Mock(return_value=[Mock(), Mock(), Mock()])
        integration.plugin_manager.get_registry_statistics = Mock(return_value={'total_plugins': 2})
        integration.plugin_manager.get_plugin_health_status = Mock(return_value={'status': 'healthy'})
        integration.plugin_manager.unified_registry = Mock()
        integration.plugin_manager.unified_registry.usage_analytics = Mock()
        integration.plugin_manager.unified_registry.usage_analytics.get_top_plugins = Mock(
            return_value=[('plugin1', 0.9), ('plugin2', 0.8)]
        )
        
        summary = integration.get_plugin_analytics_summary()
        
        assert summary['total_plugins'] == 2
        assert summary['total_tools'] == 3
        assert summary['plugin_health_summary']['healthy'] == 2
        assert 'top_plugins' in summary
    
    def test_disabled_features(self, mock_config):
        """Test integration with enhanced features disabled."""
        if not INTEGRATION_AVAILABLE:
            pytest.skip("Integration components not available")
        
        integration = EnhancedJarvisIntegration(mock_config, enable_enhanced_features=False)
        
        # Test that methods return appropriate responses when disabled
        assert integration.get_plugin_recommendations({}) == []
        assert integration.find_tools_by_capability('test') == []
        
        insights = integration.get_system_insights()
        assert insights['enhanced_features'] is False
        
        summary = integration.get_plugin_analytics_summary()
        assert 'error' in summary

class TestGlobalIntegrationFunctions(EnhancedTestBase):
    """Test global integration functions."""
    
    def test_global_instance_management(self):
        """Test global integration instance management."""
        if not INTEGRATION_AVAILABLE:
            pytest.skip("Integration components not available")
        
        # Reset global instance
        import jarvis.jarvis.core.enhanced_integration as integration_module
        integration_module._integration_instance = None
        
        # Test initialization
        config = Mock(spec=JarvisConfig)
        instance = initialize_enhanced_jarvis(config, enable_enhanced_features=True)
        
        assert instance is not None
        assert instance.enhanced_features_enabled is True
        
        # Test getting the same instance
        same_instance = get_integration_instance()
        assert same_instance is instance
    
    def test_convenience_functions(self):
        """Test convenience functions."""
        if not INTEGRATION_AVAILABLE:
            pytest.skip("Integration components not available")
        
        # Initialize integration
        config = Mock(spec=JarvisConfig)
        initialize_enhanced_jarvis(config, enable_enhanced_features=True)
        
        # Test convenience functions
        insights = get_system_insights()
        assert isinstance(insights, dict)
        
        tools = find_tools_by_capability('test_capability')
        assert isinstance(tools, list)
    
    @pytest.mark.benchmark
    def test_integration_performance(self, benchmark):
        """Benchmark integration performance."""
        if not INTEGRATION_AVAILABLE:
            pytest.skip("Integration components not available")
        
        config = Mock(spec=JarvisConfig)
        
        def create_integration():
            return EnhancedJarvisIntegration(config, enable_enhanced_features=True)
        
        result = benchmark(create_integration)
        assert result is not None
        
        # Verify performance threshold
        assert benchmark.stats['mean'] < TEST_CONFIG['performance_thresholds']['registry_query']
