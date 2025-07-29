#!/usr/bin/env python3
"""
Functional Test Suite for Enhanced Jarvis Features

This script provides functional testing of the enhanced Jarvis system
without relying on pytest, demonstrating all the key features.
"""

import sys
import time
import tempfile
from pathlib import Path
from typing import Dict, Any

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_plugin_registry():
    """Test the enhanced plugin registry functionality."""
    print("🔌 Testing Enhanced Plugin Registry...")
    
    try:
        from jarvis.jarvis.plugins.registry.unified_registry import UnifiedPluginRegistry
        from jarvis.jarvis.plugins.registry.relationship_mapper import RelationshipMapper
        from jarvis.jarvis.plugins.registry.capability_analyzer import CapabilityAnalyzer
        from jarvis.jarvis.plugins.registry.usage_analytics import UsageAnalytics
        
        # Test UnifiedPluginRegistry
        registry = UnifiedPluginRegistry()
        
        # Test plugin registration
        test_metadata = {
            "name": "test_plugin",
            "version": "1.0.0",
            "capabilities": ["text_processing", "data_analysis"],
            "dependencies": ["numpy", "pandas"]
        }
        
        success = registry.register_plugin("test_plugin", test_metadata)
        assert success, "Plugin registration failed"
        
        # Test metadata retrieval
        retrieved = registry.get_plugin_metadata("test_plugin")
        assert retrieved is not None, "Failed to retrieve plugin metadata"
        assert retrieved.name == "test_plugin", "Metadata mismatch"
        
        # Test capability search
        plugins = registry.find_plugins_by_capability("text_processing")
        assert "test_plugin" in plugins, "Capability search failed"
        
        print("✅ Plugin Registry: All tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Plugin Registry: Test failed - {e}")
        return False

def test_context_management():
    """Test the context management system."""
    print("🧠 Testing Context Management System...")
    
    try:
        from jarvis.jarvis.core.context.context_manager import ContextManager
        from jarvis.jarvis.core.context.conversation_state import ConversationState
        from jarvis.jarvis.core.context.user_preference_engine import UserPreferenceEngine
        from jarvis.jarvis.core.context.session_memory import SessionMemory, MemoryType, MemoryScope
        
        # Test ContextManager
        context_manager = ContextManager()
        
        # Test session creation
        session_id = "test_session_001"
        context = context_manager.get_current_context(session_id)
        assert context is not None, "Failed to create context"
        
        # Test context updates
        updates = {"user_intent": "testing", "current_topic": "context_management"}
        context_manager.update_context(session_id, updates)
        
        updated_context = context_manager.get_current_context(session_id)
        assert updated_context.conversation_context["user_intent"] == "testing", "Context update failed"
        
        # Test SessionMemory
        session_memory = SessionMemory()
        
        # Test memory storage
        memory_id = session_memory.store_memory(
            session_id=session_id,
            memory_type=MemoryType.CONTEXT_DATA,
            data={"test": "data"},
            scope=MemoryScope.SESSION
        )
        assert memory_id is not None, "Memory storage failed"
        
        # Test memory retrieval
        retrieved_memory = session_memory.retrieve_memory(session_id, memory_id)
        assert retrieved_memory is not None, "Memory retrieval failed"
        assert retrieved_memory.data["test"] == "data", "Memory data mismatch"
        
        print("✅ Context Management: All tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Context Management: Test failed - {e}")
        return False

def test_orchestration():
    """Test the smart tool orchestration system."""
    print("⚡ Testing Smart Tool Orchestration...")
    
    try:
        from jarvis.jarvis.core.orchestration.orchestrator import SystemOrchestrator
        from jarvis.jarvis.core.orchestration.tool_chain_detector import ToolChainDetector
        from jarvis.jarvis.core.orchestration.context_aware_selector import ContextAwareSelector, SelectionCriteria
        from jarvis.jarvis.core.context.context_manager import ContextManager
        
        # Test SystemOrchestrator
        context_manager = ContextManager()
        orchestrator = SystemOrchestrator(context_manager)
        
        # Test tool chain detection
        chain_detector = ToolChainDetector()
        
        # Record some tool usage for pattern detection
        chain_detector.record_tool_usage("tool_a", success=True, execution_time=1.5)
        chain_detector.record_tool_usage("tool_b", success=True, execution_time=2.0)
        chain_detector.record_tool_usage("tool_c", success=True, execution_time=1.0)
        
        # Test context-aware selection
        selector = ContextAwareSelector()
        
        criteria = SelectionCriteria(
            required_capabilities={"text_processing"},
            conversation_topic="testing",
            user_intent="analysis"
        )
        
        # This will return empty since we don't have real tools registered,
        # but it should not crash
        selected_tools = selector.select_tools(criteria, max_tools=3)
        assert isinstance(selected_tools, list), "Tool selection failed"
        
        print("✅ Orchestration: All tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Orchestration: Test failed - {e}")
        return False

def test_code_consciousness():
    """Test the source code consciousness system."""
    print("🔍 Testing Source Code Consciousness...")
    
    try:
        from jarvis.jarvis.core.consciousness.consciousness_system import CodeConsciousnessSystem
        from jarvis.jarvis.core.consciousness.codebase_rag import CodebaseRAG
        from jarvis.jarvis.core.consciousness.semantic_index import SemanticIndex
        
        # Create temporary directory for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create a simple test file
            test_file = temp_path / "test_module.py"
            test_file.write_text("""
def hello_world():
    '''A simple hello world function.'''
    return "Hello, World!"

class TestClass:
    '''A test class for demonstration.'''
    
    def __init__(self):
        self.value = 42
    
    def get_value(self):
        return self.value
""")
            
            # Test CodebaseRAG
            rag_system = CodebaseRAG(temp_path)
            
            # Test indexing (this will be minimal since we have a small test file)
            index_result = await_if_needed(rag_system.index_codebase())
            assert index_result, "Codebase indexing failed"
            
            # Test search
            search_results = await_if_needed(rag_system.search_code("hello", max_results=5))
            assert isinstance(search_results, list), "Code search failed"
            
            # Test CodeConsciousnessSystem
            consciousness = CodeConsciousnessSystem(temp_path, enable_safe_modifications=False)
            
            # Test natural language query
            query_result = consciousness.query_codebase("find functions")
            assert isinstance(query_result, dict), "Codebase query failed"
            
            print("✅ Code Consciousness: All tests passed")
            return True
        
    except Exception as e:
        print(f"❌ Code Consciousness: Test failed - {e}")
        return False

def test_integration():
    """Test integration between components."""
    print("🔗 Testing Component Integration...")
    
    try:
        from jarvis.jarvis.core.context.context_manager import ContextManager
        from jarvis.jarvis.core.orchestration.orchestrator import SystemOrchestrator
        from jarvis.jarvis.plugins.enhanced_manager import EnhancedPluginManager
        
        # Test integration between context manager and orchestrator
        context_manager = ContextManager()
        orchestrator = SystemOrchestrator(context_manager)
        
        # Test session creation and context sharing
        session_id = "integration_test_001"
        context = context_manager.get_current_context(session_id)
        
        # Update context with orchestration-relevant data
        context_manager.update_context(session_id, {
            "user_intent": "integration_testing",
            "available_tools": ["tool_a", "tool_b"],
            "complexity_level": "medium"
        })
        
        # Test enhanced plugin manager
        plugin_manager = EnhancedPluginManager()
        
        # Get registry statistics
        stats = plugin_manager.get_registry_statistics()
        assert isinstance(stats, dict), "Registry statistics failed"
        
        print("✅ Integration: All tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Integration: Test failed - {e}")
        return False

def await_if_needed(result):
    """Helper to handle async results if needed."""
    import asyncio
    if asyncio.iscoroutine(result):
        try:
            loop = asyncio.get_event_loop()
            return loop.run_until_complete(result)
        except RuntimeError:
            # No event loop running
            return asyncio.run(result)
    return result

def run_performance_test():
    """Run basic performance tests."""
    print("⚡ Running Performance Tests...")
    
    try:
        from jarvis.jarvis.plugins.registry.unified_registry import UnifiedPluginRegistry
        from jarvis.jarvis.core.context.context_manager import ContextManager
        
        # Test plugin registry performance
        registry = UnifiedPluginRegistry()
        
        start_time = time.time()
        
        # Register multiple plugins
        for i in range(100):
            metadata = {
                "name": f"test_plugin_{i}",
                "version": "1.0.0",
                "capabilities": [f"capability_{i % 10}"],
                "performance_score": i * 0.01
            }
            registry.register_plugin(f"test_plugin_{i}", metadata)
        
        registration_time = time.time() - start_time
        
        # Test search performance
        start_time = time.time()
        
        for i in range(10):
            results = registry.find_plugins_by_capability(f"capability_{i}")
        
        search_time = time.time() - start_time
        
        # Test context manager performance
        context_manager = ContextManager()
        
        start_time = time.time()
        
        # Create multiple sessions
        for i in range(50):
            session_id = f"perf_test_{i}"
            context = context_manager.get_current_context(session_id)
            context_manager.update_context(session_id, {"test_data": f"data_{i}"})
        
        context_time = time.time() - start_time
        
        print(f"📊 Performance Results:")
        print(f"   Plugin Registration (100 plugins): {registration_time:.3f}s")
        print(f"   Plugin Search (10 searches): {search_time:.3f}s")
        print(f"   Context Management (50 sessions): {context_time:.3f}s")
        
        # Performance assertions
        assert registration_time < 5.0, f"Plugin registration too slow: {registration_time:.3f}s"
        assert search_time < 1.0, f"Plugin search too slow: {search_time:.3f}s"
        assert context_time < 2.0, f"Context management too slow: {context_time:.3f}s"
        
        print("✅ Performance: All tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Performance: Test failed - {e}")
        return False

def main():
    """Run all functional tests."""
    print("🚀 Starting Enhanced Jarvis Functional Test Suite")
    print("=" * 60)
    
    test_results = []
    
    # Run all test categories
    test_functions = [
        ("Plugin Registry", test_plugin_registry),
        ("Context Management", test_context_management),
        ("Orchestration", test_orchestration),
        ("Code Consciousness", test_code_consciousness),
        ("Integration", test_integration),
        ("Performance", run_performance_test)
    ]
    
    for test_name, test_func in test_functions:
        print(f"\n📋 Running {test_name} Tests...")
        try:
            result = test_func()
            test_results.append((test_name, result))
        except Exception as e:
            print(f"💥 {test_name}: CRASHED - {e}")
            test_results.append((test_name, False))
    
    # Print final summary
    print("\n" + "=" * 60)
    print("📊 FUNCTIONAL TEST SUMMARY")
    print("=" * 60)
    
    passed_tests = sum(1 for _, result in test_results if result)
    total_tests = len(test_results)
    success_rate = (passed_tests / total_tests) * 100
    
    print(f"📈 Tests Passed: {passed_tests}/{total_tests}")
    print(f"📈 Success Rate: {success_rate:.1f}%")
    
    print("\n📋 Test Details:")
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} {test_name}")
    
    if success_rate == 100:
        print("\n🎉 ALL FUNCTIONAL TESTS PASSED! 🎉")
        print("✅ Enhanced Jarvis system is working correctly!")
    elif success_rate >= 80:
        print("\n✅ Most functional tests passed!")
        print("⚠️  Some minor issues found - check details above")
    else:
        print("\n⚠️  Multiple test failures!")
        print("❌ Enhanced Jarvis system needs attention")
    
    return success_rate == 100

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
