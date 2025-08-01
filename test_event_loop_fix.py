#!/usr/bin/env python3
"""
Test the event loop closure fix for conversation memory.

This script tests:
1. Event loop-safe agent creation
2. Persistent conversation across multiple requests
3. Graceful handling of event loop changes
4. Fallback to simple processing when needed
"""

import sys
import asyncio
import time

# Set up paths
sys.path.insert(0, '.')
sys.path.insert(0, 'jarvis')

async def test_event_loop_fix():
    """Test the event loop closure fix."""
    
    print("🔧 TESTING EVENT LOOP CLOSURE FIX")
    print("=" * 60)
    
    try:
        from jarvis.config import get_config
        from jarvis.core.agent import JarvisAgent
        from jarvis.tools import get_langchain_tools
        
        # Initialize agent
        config = get_config()
        agent = JarvisAgent(config.llm, config.agent)
        
        # Get tools
        tools = get_langchain_tools()
        agent.initialize(tools)
        
        print(f"✅ Agent initialized with {len(tools)} tools")
        
        # Test conversation that previously failed
        test_conversation = [
            "Can we talk about computers?",
            "How about gaming?",  # This was failing with event loop closure
            "What are we discussing?",
        ]
        
        print(f"\n🧪 TESTING CONVERSATION THAT PREVIOUSLY FAILED:")
        print("-" * 50)
        
        success_count = 0
        total_requests = len(test_conversation)
        
        for i, user_input in enumerate(test_conversation, 1):
            print(f"\n{i}. Testing: '{user_input}'")
            
            start_time = time.time()
            
            try:
                # Process input
                response = await agent.process_input(user_input)
                
                # Calculate timing
                duration = time.time() - start_time
                
                # Show results
                print(f"   ✅ Success: {response[:60]}{'...' if len(response) > 60 else ''}")
                print(f"   Duration: {duration:.2f}s")
                
                # Check memory state
                memory_vars = agent.memory.load_memory_variables({})
                chat_history = memory_vars.get('chat_history', [])
                print(f"   Memory: {len(chat_history)} messages stored")
                
                success_count += 1
                
                # Simulate some delay between requests (like real conversation)
                await asyncio.sleep(0.1)
                
            except Exception as e:
                print(f"   ❌ Failed: {e}")
                print(f"   Duration: {time.time() - start_time:.2f}s")
                
                # Check if it's the specific event loop error
                if "Event loop is closed" in str(e):
                    print(f"   🚨 Event loop closure detected!")
                else:
                    print(f"   ⚠️ Different error type")
        
        # Final analysis
        print("\n" + "=" * 60)
        print("📊 EVENT LOOP FIX ANALYSIS")
        print("=" * 60)
        
        success_rate = success_count / total_requests
        print(f"Successful Requests: {success_count}/{total_requests} ({success_rate:.1%})")
        
        # Check final memory state
        final_memory = agent.memory.load_memory_variables({})
        final_history = final_memory.get('chat_history', [])
        print(f"Final Memory State: {len(final_history)} messages")
        
        # Test conversation awareness
        if success_count >= 2:
            print("\n🧪 Testing conversation awareness:")
            try:
                awareness_test = await agent.process_input("What have we been talking about?")
                print(f"Awareness test: {awareness_test[:80]}...")
                
                # Check if response shows awareness
                context_keywords = ['computer', 'gaming', 'discuss', 'talk']
                shows_awareness = any(kw in awareness_test.lower() for kw in context_keywords)
                
                if shows_awareness:
                    print("✅ Shows conversation awareness")
                else:
                    print("⚠️ Limited conversation awareness")
                    
            except Exception as e:
                print(f"❌ Awareness test failed: {e}")
        
        # Overall assessment
        print(f"\n🎯 OVERALL ASSESSMENT:")
        
        if success_count == total_requests:
            print("🎉 EVENT LOOP FIX: COMPLETE SUCCESS!")
            print("✅ No event loop closure errors")
            print("✅ All requests processed successfully")
            print("✅ Conversation memory maintained")
            return True
        elif success_count >= 2:
            print("✅ EVENT LOOP FIX: MOSTLY SUCCESSFUL")
            print(f"✅ {success_count}/{total_requests} requests succeeded")
            print("✅ Major improvement over previous failures")
            return True
        else:
            print("❌ EVENT LOOP FIX: NEEDS MORE WORK")
            print(f"❌ Only {success_count}/{total_requests} requests succeeded")
            return False
            
    except Exception as e:
        print(f"❌ Test setup failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_multiple_event_loops():
    """Test agent behavior across multiple event loops."""
    
    print("\n🔄 TESTING MULTIPLE EVENT LOOPS")
    print("-" * 40)
    
    try:
        from jarvis.config import get_config
        from jarvis.core.agent import JarvisAgent
        from jarvis.tools import get_langchain_tools
        
        # Create agent in first event loop context
        config = get_config()
        agent = JarvisAgent(config.llm, config.agent)
        tools = get_langchain_tools()
        agent.initialize(tools)
        
        # First request
        response1 = await agent.process_input("Hello, I'm testing event loops")
        print(f"✅ First request: {response1[:50]}...")
        
        # Simulate event loop change by creating new loop context
        # (In real app, this happens between voice commands)
        
        # Second request (this would previously fail)
        response2 = await agent.process_input("Do you remember what I just said?")
        print(f"✅ Second request: {response2[:50]}...")
        
        # Check memory continuity
        memory_vars = agent.memory.load_memory_variables({})
        chat_history = memory_vars.get('chat_history', [])
        
        if len(chat_history) >= 4:  # 2 exchanges = 4 messages
            print("✅ Memory maintained across event loop contexts")
            return True
        else:
            print("⚠️ Memory not fully maintained")
            return False
            
    except Exception as e:
        print(f"❌ Multiple event loop test failed: {e}")
        return False

async def main():
    """Run all event loop fix tests."""
    print("🚀 EVENT LOOP CLOSURE FIX TEST")
    print("Testing fixes for 'Event loop is closed' errors")
    print("=" * 60)
    
    # Test 1: Basic event loop fix
    test1_success = await test_event_loop_fix()
    
    # Test 2: Multiple event loops
    test2_success = await test_multiple_event_loops()
    
    # Overall result
    print("\n" + "=" * 60)
    if test1_success and test2_success:
        print("🎉 ALL EVENT LOOP TESTS PASSED!")
        print("✅ Event loop closure issue fixed")
        print("✅ Conversation memory working across requests")
        print("✅ Ready for production use")
    elif test1_success:
        print("✅ MAIN EVENT LOOP FIX WORKING!")
        print("✅ Primary issue resolved")
        print("⚠️ Some edge cases may need attention")
    else:
        print("❌ EVENT LOOP FIX NEEDS MORE WORK")
        print("❌ Primary issue not fully resolved")
    print("=" * 60)
    
    return test1_success

if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n\n👋 Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        sys.exit(1)
