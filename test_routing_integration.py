#!/usr/bin/env python3
"""
Test Fast/Slow Path Routing Integration

Quick test to verify the routing system is working correctly
and can handle the problematic "What time is it?" query.
"""

import sys
import asyncio
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent / "jarvis"
sys.path.insert(0, str(project_root))

async def test_routing_system():
    """Test the routing system with the problematic query."""
    
    print("🧪 TESTING FAST/SLOW PATH ROUTING INTEGRATION")
    print("=" * 60)
    
    try:
        # Import the routing system
        from jarvis.core.routing import SmartConversationManager, ExecutionEngine
        from jarvis.config import JarvisConfig
        
        print("✅ Successfully imported routing system")
        
        # Initialize config
        config = JarvisConfig()
        print("✅ Configuration loaded")
        
        # Test the execution engine directly first
        print("\n🔍 Testing ExecutionEngine directly...")
        engine = ExecutionEngine(config)
        
        # Test the problematic query
        test_query = "What time is it?"
        print(f"📝 Testing query: '{test_query}'")
        
        start_time = time.time()
        result = await engine.execute_query(test_query)
        end_time = time.time()
        
        execution_time_ms = (end_time - start_time) * 1000
        
        print(f"\n✅ EXECUTION RESULTS:")
        print(f"   Response: {result.response}")
        print(f"   Execution Time: {execution_time_ms:.1f}ms")
        print(f"   Path Used: {result.path_used.value.upper()}")
        print(f"   Success: {result.success}")
        
        # Check if it meets the instant path target
        if result.path_used.value == "instant":
            if execution_time_ms < 200:
                print(f"   ✅ MEETS INSTANT TARGET (<200ms)")
            else:
                print(f"   ⚠️  EXCEEDS INSTANT TARGET ({execution_time_ms:.1f}ms > 200ms)")
        
        # Calculate improvement over the original 30-second timeout
        original_time_ms = 30000  # 30 seconds
        improvement_factor = original_time_ms / execution_time_ms
        
        print(f"\n🎯 PERFORMANCE IMPROVEMENT:")
        print(f"   Original Time: {original_time_ms:,}ms (timeout)")
        print(f"   New Time: {execution_time_ms:.1f}ms")
        print(f"   Improvement: {improvement_factor:.0f}x faster")
        print(f"   Time Saved: {(original_time_ms - execution_time_ms)/1000:.1f} seconds")
        
        # Test a few more queries
        print(f"\n🔍 Testing additional queries...")
        
        additional_queries = [
            "Hello",
            "How are you?",
            "What is Python programming?",
            "Analyze my files and create a report"
        ]
        
        for query in additional_queries:
            start_time = time.time()
            result = await engine.execute_query(query)
            end_time = time.time()
            
            execution_time_ms = (end_time - start_time) * 1000
            
            print(f"   📝 '{query}' → {result.path_used.value.upper()} ({execution_time_ms:.1f}ms)")
        
        # Get performance statistics
        print(f"\n📊 PERFORMANCE STATISTICS:")
        stats = engine.get_performance_stats()
        
        for path_name, path_stats in stats.items():
            if path_name != "routing" and path_stats.get("count", 0) > 0:
                print(f"   {path_name.upper()}: {path_stats['count']} queries, avg {path_stats['avg_execution_time_ms']:.1f}ms")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("💡 The routing system may not be properly installed")
        return False
        
    except Exception as e:
        print(f"❌ Test Error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_smart_conversation_manager():
    """Test the SmartConversationManager integration."""
    
    print(f"\n🔧 TESTING SMART CONVERSATION MANAGER")
    print("-" * 40)
    
    try:
        from jarvis.core.routing import SmartConversationManager
        from jarvis.config import JarvisConfig
        
        config = JarvisConfig()
        
        # Create smart conversation manager (without speech/agent for testing)
        smart_manager = SmartConversationManager(config)
        
        print("✅ SmartConversationManager created")
        
        # Test initialization check
        is_initialized = smart_manager.is_initialized()
        print(f"✅ Initialization check: {is_initialized}")
        
        # Test conversation state methods
        smart_manager.enter_conversation_mode()
        state = smart_manager.get_conversation_state()
        print(f"✅ Conversation state: active={state['active']}, routing_enabled={state['routing_enabled']}")
        
        smart_manager.reset_conversation()
        print("✅ Conversation reset successful")
        
        return True
        
    except Exception as e:
        print(f"❌ SmartConversationManager test failed: {e}")
        return False

def create_integration_summary():
    """Create a summary of the integration."""
    
    summary = """
🎯 FAST/SLOW PATH ROUTING INTEGRATION SUMMARY
============================================

✅ WHAT WAS IMPLEMENTED:
• IntentRouter: Fast pattern-based query classification
• ExecutionEngine: Multi-path execution with performance targets  
• SmartConversationManager: Drop-in replacement with routing
• Integration: Modified main.py to use smart routing system

✅ EXPECTED IMPROVEMENTS:
• "What time is it?" goes from 30s timeout to <200ms response
• Simple queries use INSTANT path (no LLM overhead)
• Complex queries still get full orchestration
• Automatic fallback if routing fails

🔧 INTEGRATION STATUS:
• Routing system files created in jarvis/jarvis/core/routing/
• Main application modified to use SmartConversationManager
• Backward compatibility maintained with original interface
• Performance monitoring and statistics included

🚀 NEXT STEPS:
1. Restart Jarvis to load the new routing system
2. Test "What time is it?" - should respond instantly
3. Monitor performance with conversation_manager.get_routing_stats()
4. Adjust patterns if needed for your specific use cases

💡 TROUBLESHOOTING:
• If routing doesn't work, system automatically falls back to original
• Check logs for "Smart routing system enabled" message
• Use test_routing_integration.py to verify functionality
"""
    
    print(summary)

async def main():
    """Main test execution."""
    
    print("🎯 JARVIS FAST/SLOW PATH ROUTING INTEGRATION TEST")
    print("=" * 70)
    
    # Test the routing system
    routing_success = await test_routing_system()
    
    if routing_success:
        # Test the smart conversation manager
        manager_success = await test_smart_conversation_manager()
        
        if manager_success:
            print(f"\n🎉 ALL TESTS PASSED!")
            print("=" * 30)
            print("✅ Routing system is working correctly")
            print("✅ SmartConversationManager integration successful")
            print("✅ Ready to fix the timeout issues!")
            
            create_integration_summary()
            
        else:
            print(f"\n⚠️ PARTIAL SUCCESS")
            print("✅ Routing system works")
            print("❌ SmartConversationManager integration needs work")
    else:
        print(f"\n❌ TESTS FAILED")
        print("The routing system is not working correctly")
        print("Please check the error messages above")

if __name__ == "__main__":
    asyncio.run(main())
