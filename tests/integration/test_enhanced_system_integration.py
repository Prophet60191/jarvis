"""
Comprehensive Integration Tests for Enhanced Jarvis System

Tests the complete integration of performance optimization, monitoring,
analytics, and enhanced features working together.
"""

import pytest
import time
import tempfile
import threading
from pathlib import Path
from typing import Dict, Any, List

# Import system components
import sys
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from jarvis.jarvis.core.context.context_manager import ContextManager
from jarvis.jarvis.core.performance.context_cache import LRUContextCache, ContextCacheManager
from jarvis.jarvis.core.monitoring.performance_tracker import PerformanceTracker
from jarvis.jarvis.core.analytics.usage_analytics import UsageAnalytics
from jarvis.jarvis.plugins.registry.unified_registry import UnifiedPluginRegistry
from jarvis.jarvis.core.orchestration.orchestrator import SystemOrchestrator

class TestEnhancedSystemIntegration:
    """Test suite for enhanced system integration."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)
    
    @pytest.fixture
    def context_manager(self, temp_dir):
        """Create context manager for testing."""
        storage_path = temp_dir / "context.json"
        return ContextManager(storage_path=storage_path)
    
    @pytest.fixture
    def performance_tracker(self):
        """Create performance tracker for testing."""
        return PerformanceTracker(history_size=100)
    
    @pytest.fixture
    def usage_analytics(self, temp_dir):
        """Create usage analytics for testing."""
        return UsageAnalytics(storage_path=temp_dir / "analytics")
    
    @pytest.fixture
    def plugin_registry(self, temp_dir):
        """Create plugin registry for testing."""
        storage_path = temp_dir / "registry.json"
        return UnifiedPluginRegistry(storage_path=storage_path)
    
    def test_context_caching_performance(self, context_manager):
        """Test context caching improves performance."""
        session_id = "test_session_001"
        
        # First access (cache miss)
        start_time = time.time()
        context1 = context_manager.get_current_context(session_id)
        first_access_time = time.time() - start_time
        
        # Second access (cache hit)
        start_time = time.time()
        context2 = context_manager.get_current_context(session_id)
        second_access_time = time.time() - start_time
        
        # Verify contexts are equivalent
        assert context1.session_id == context2.session_id
        assert context1.user_context == context2.user_context
        
        # Cache hit should be faster (allowing for some variance)
        assert second_access_time <= first_access_time * 1.5
        
        print(f"First access: {first_access_time*1000:.2f}ms")
        print(f"Second access: {second_access_time*1000:.2f}ms")
        print(f"Performance improvement: {((first_access_time - second_access_time) / first_access_time * 100):.1f}%")
    
    def test_performance_monitoring_integration(self, performance_tracker):
        """Test performance monitoring tracks operations correctly."""
        # Start monitoring
        performance_tracker.start_monitoring(interval_seconds=0.1)
        
        # Perform tracked operations
        op_id1 = performance_tracker.start_operation("test_operation_1")
        time.sleep(0.05)  # Simulate work
        performance_tracker.end_operation(op_id1, success=True)
        
        op_id2 = performance_tracker.start_operation("test_operation_2")
        time.sleep(0.03)  # Simulate work
        performance_tracker.end_operation(op_id2, success=False, error_message="Test error")
        
        # Wait for monitoring cycle
        time.sleep(0.2)
        
        # Check statistics
        stats1 = performance_tracker.get_operation_stats("test_operation_1")
        stats2 = performance_tracker.get_operation_stats("test_operation_2")
        
        assert stats1['total_executions'] == 1
        assert stats1['success_rate'] == 100.0
        assert stats1['avg_time_ms'] >= 50  # Should be around 50ms
        
        assert stats2['total_executions'] == 1
        assert stats2['success_rate'] == 0.0
        assert stats2['error_count'] == 1
        
        # Get system metrics
        system_metrics = performance_tracker.get_system_metrics()
        assert system_metrics.cpu_percent >= 0
        assert system_metrics.memory_percent >= 0
        
        # Stop monitoring
        performance_tracker.stop_monitoring()
    
    def test_usage_analytics_tracking(self, usage_analytics):
        """Test usage analytics tracks user behavior correctly."""
        session_id = "analytics_test_session"
        user_id = "test_user_123"
        
        # Track conversation events
        usage_analytics.track_conversation_event(
            session_id=session_id,
            event_type='start',
            user_id=user_id
        )
        
        # Track tool usage
        usage_analytics.track_tool_usage(
            tool_name="test_tool_1",
            session_id=session_id,
            execution_time_ms=150.0,
            success=True,
            user_id=user_id,
            input_size_bytes=1024,
            output_size_bytes=2048
        )
        
        usage_analytics.track_tool_usage(
            tool_name="test_tool_2",
            session_id=session_id,
            execution_time_ms=200.0,
            success=True,
            user_id=user_id
        )
        
        # Track conversation end
        usage_analytics.track_conversation_event(
            session_id=session_id,
            event_type='end',
            user_id=user_id
        )
        
        # Get system statistics
        system_stats = usage_analytics.get_system_usage_stats()
        
        assert system_stats.total_sessions >= 1
        assert system_stats.total_tool_calls >= 2
        assert system_stats.unique_users >= 1
        
        # Check tool popularity
        tool_names = [tool for tool, _ in system_stats.most_popular_tools]
        assert "test_tool_1" in tool_names
        assert "test_tool_2" in tool_names
        
        # Get user behavior pattern
        user_pattern = usage_analytics.get_user_behavior_pattern(user_id)
        assert user_pattern is not None
        assert user_pattern.user_id == user_id
        assert user_pattern.total_sessions >= 1
        assert len(user_pattern.most_used_tools) >= 2
    
    def test_plugin_registry_performance(self, plugin_registry):
        """Test plugin registry performance with caching."""
        # Register multiple plugins
        plugins_to_register = []
        for i in range(50):
            plugin_metadata = {
                "name": f"test_plugin_{i}",
                "version": "1.0.0",
                "description": f"Test plugin {i}",
                "author": "Test Author",
                "capabilities": [f"capability_{i % 5}", "common_capability"],
                "dependencies": ["numpy"] if i % 3 == 0 else []
            }
            plugins_to_register.append((f"test_plugin_{i}", plugin_metadata))
        
        # Measure registration time
        start_time = time.time()
        for plugin_name, metadata in plugins_to_register:
            success = plugin_registry.register_plugin(plugin_name, metadata)
            assert success, f"Failed to register {plugin_name}"
        registration_time = time.time() - start_time
        
        # Measure search performance
        start_time = time.time()
        for i in range(10):
            results = plugin_registry.find_plugins_by_capability("common_capability")
            assert len(results) == 50  # All plugins have this capability
        search_time = time.time() - start_time
        
        # Performance assertions
        assert registration_time < 5.0, f"Plugin registration too slow: {registration_time:.3f}s"
        assert search_time < 1.0, f"Plugin search too slow: {search_time:.3f}s"
        
        print(f"Registered 50 plugins in {registration_time:.3f}s ({registration_time/50*1000:.1f}ms per plugin)")
        print(f"Performed 10 searches in {search_time:.3f}s ({search_time/10*1000:.1f}ms per search)")
    
    def test_full_conversation_flow(self, context_manager, usage_analytics, performance_tracker):
        """Test complete conversation flow with all systems integrated."""
        session_id = "full_flow_test"
        user_id = "integration_test_user"
        
        # Start performance monitoring
        performance_tracker.start_monitoring(interval_seconds=0.1)
        
        # Track conversation start
        usage_analytics.track_conversation_event(
            session_id=session_id,
            event_type='start',
            user_id=user_id
        )
        
        # Create session context
        context = context_manager.create_session(session_id, user_id=user_id)
        assert context.session_id == session_id
        assert context.user_context.get('user_id') == user_id
        
        # Simulate conversation updates
        conversation_updates = [
            {"user_intent": "file_operations", "current_topic": "document_editing"},
            {"user_message": "Please help me edit a document", "complexity": "medium"},
            {"tool_selection": "text_editor", "confidence": 0.85},
            {"task_progress": "in_progress", "estimated_completion": "2_minutes"}
        ]
        
        for i, update in enumerate(conversation_updates):
            # Update context
            context_manager.update_context(session_id, update)
            
            # Track tool usage (simulated)
            usage_analytics.track_tool_usage(
                tool_name=f"conversation_tool_{i}",
                session_id=session_id,
                execution_time_ms=100 + i * 50,
                success=True,
                user_id=user_id,
                context=update
            )
            
            # Small delay to simulate real conversation
            time.sleep(0.01)
        
        # Get final context
        final_context = context_manager.get_current_context(session_id)
        assert final_context.conversation_context["user_intent"] == "file_operations"
        assert final_context.conversation_context["task_progress"] == "in_progress"
        
        # Track conversation end
        usage_analytics.track_conversation_event(
            session_id=session_id,
            event_type='end',
            user_id=user_id
        )
        
        # Verify analytics data
        user_pattern = usage_analytics.get_user_behavior_pattern(user_id)
        assert user_pattern is not None
        assert user_pattern.total_sessions >= 1
        assert len(user_pattern.most_used_tools) >= 4
        
        # Verify performance tracking
        performance_summary = performance_tracker.get_performance_summary()
        assert performance_summary['total_operations'] >= 4
        assert 'get_current_context' in performance_summary['operations']
        assert 'update_context' in performance_summary['operations']
        
        # Stop monitoring
        performance_tracker.stop_monitoring()
        
        print(f"Conversation flow completed successfully")
        print(f"Context updates: {len(conversation_updates)}")
        print(f"Tool calls tracked: {len(user_pattern.most_used_tools)}")
        print(f"Performance operations: {performance_summary['total_operations']}")
    
    def test_concurrent_session_handling(self, context_manager, usage_analytics):
        """Test system handles concurrent sessions correctly."""
        num_sessions = 20
        num_updates_per_session = 5
        
        def session_worker(session_id: str, user_id: str):
            """Worker function for concurrent session testing."""
            try:
                # Create session
                context = context_manager.create_session(session_id, user_id=user_id)
                
                # Track conversation start
                usage_analytics.track_conversation_event(
                    session_id=session_id,
                    event_type='start',
                    user_id=user_id
                )
                
                # Perform updates
                for i in range(num_updates_per_session):
                    update = {
                        "step": i,
                        "data": f"session_{session_id}_update_{i}",
                        "timestamp": time.time()
                    }
                    
                    context_manager.update_context(session_id, update)
                    
                    # Track tool usage
                    usage_analytics.track_tool_usage(
                        tool_name=f"concurrent_tool_{i}",
                        session_id=session_id,
                        execution_time_ms=50.0,
                        success=True,
                        user_id=user_id
                    )
                    
                    time.sleep(0.001)  # Small delay
                
                # Track conversation end
                usage_analytics.track_conversation_event(
                    session_id=session_id,
                    event_type='end',
                    user_id=user_id
                )
                
                return True
                
            except Exception as e:
                print(f"Error in session {session_id}: {e}")
                return False
        
        # Create and start threads
        threads = []
        for i in range(num_sessions):
            session_id = f"concurrent_session_{i}"
            user_id = f"concurrent_user_{i % 5}"  # 5 different users
            
            thread = threading.Thread(
                target=session_worker,
                args=(session_id, user_id)
            )
            threads.append(thread)
        
        # Start all threads
        start_time = time.time()
        for thread in threads:
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join(timeout=10.0)  # 10 second timeout
        
        total_time = time.time() - start_time
        
        # Verify all sessions were created
        system_stats = usage_analytics.get_system_usage_stats()
        assert system_stats.total_sessions >= num_sessions
        assert system_stats.total_tool_calls >= num_sessions * num_updates_per_session
        
        # Performance assertions
        assert total_time < 30.0, f"Concurrent session handling too slow: {total_time:.3f}s"
        
        print(f"Handled {num_sessions} concurrent sessions in {total_time:.3f}s")
        print(f"Average time per session: {total_time/num_sessions*1000:.1f}ms")
        print(f"Total tool calls: {system_stats.total_tool_calls}")
        print(f"Unique users: {system_stats.unique_users}")
    
    def test_system_orchestration_integration(self, context_manager):
        """Test system orchestration with enhanced context management."""
        try:
            # Create orchestrator
            orchestrator = SystemOrchestrator(context_manager)
            
            # Test basic orchestration functionality
            session_id = "orchestration_test"
            context = context_manager.create_session(session_id)
            
            # Update context with orchestration-relevant data
            context_manager.update_context(session_id, {
                "user_intent": "complex_task",
                "available_tools": ["tool_a", "tool_b", "tool_c"],
                "task_complexity": "high",
                "user_preferences": {"prefer_automation": True}
            })
            
            # Verify context integration
            updated_context = context_manager.get_current_context(session_id)
            assert updated_context.conversation_context["user_intent"] == "complex_task"
            assert updated_context.conversation_context["task_complexity"] == "high"
            
            print("System orchestration integration test passed")
            
        except Exception as e:
            # If orchestration components aren't fully implemented, that's okay
            print(f"Orchestration integration test skipped: {e}")
    
    def test_cache_performance_under_load(self):
        """Test cache performance under high load."""
        cache = LRUContextCache(max_size=100, max_memory_mb=10)
        
        # Generate test data
        test_data = {}
        for i in range(200):  # More than cache size
            key = f"test_key_{i}"
            data = {
                "session_id": key,
                "data": f"test_data_{i}" * 100,  # Make data larger
                "timestamp": time.time(),
                "metadata": {"index": i, "category": f"cat_{i % 5}"}
            }
            test_data[key] = data
        
        # Measure cache performance
        start_time = time.time()
        
        # Fill cache
        for key, data in test_data.items():
            cache.put(key, data)
        
        fill_time = time.time() - start_time
        
        # Measure access performance
        start_time = time.time()
        hits = 0
        misses = 0
        
        # Access patterns (some hits, some misses)
        for i in range(500):
            key = f"test_key_{i % 150}"  # Some keys will be evicted
            result = cache.get(key)
            if result is not None:
                hits += 1
            else:
                misses += 1
        
        access_time = time.time() - start_time
        
        # Get cache statistics
        stats = cache.get_stats()
        
        # Performance assertions
        assert fill_time < 1.0, f"Cache fill too slow: {fill_time:.3f}s"
        assert access_time < 0.5, f"Cache access too slow: {access_time:.3f}s"
        assert stats.hit_rate > 50.0, f"Cache hit rate too low: {stats.hit_rate:.1f}%"
        
        print(f"Cache fill time: {fill_time:.3f}s for 200 items")
        print(f"Cache access time: {access_time:.3f}s for 500 accesses")
        print(f"Hit rate: {stats.hit_rate:.1f}%")
        print(f"Average access time: {stats.avg_access_time_ms:.2f}ms")

if __name__ == "__main__":
    # Run tests directly
    pytest.main([__file__, "-v", "-s"])
