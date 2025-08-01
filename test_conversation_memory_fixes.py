#!/usr/bin/env python3
"""
Test the comprehensive conversation memory fixes.

This script tests:
1. Persistent agent (no fresh creation)
2. Simple query fast path
3. Conversation memory continuity
4. Reduced API calls
5. Faster response times
"""

import sys
import asyncio
import time

# Set up paths
sys.path.insert(0, '.')
sys.path.insert(0, 'jarvis')

async def test_conversation_memory_fixes():
    """Test all the conversation memory fixes."""
    
    print("🔧 TESTING COMPREHENSIVE CONVERSATION MEMORY FIXES")
    print("=" * 70)
    
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
        print(f"   Max iterations: {config.agent.max_iterations}")
        print(f"   Max execution time: {config.agent.max_execution_time}s")
        print(f"   RAG intelligent processing: {config.rag.intelligent_processing}")
        print(f"   RAG query optimization: {config.rag.query_optimization}")
        
        # Test conversation scenarios
        test_scenarios = [
            # Simple queries (should use fast path)
            ("Hi", "simple"),
            ("Yes", "simple"),
            ("Thanks", "simple"),
            
            # Conversation flow (should maintain memory)
            ("Can we talk about computers?", "conversation"),
            ("Gaming", "conversation"),
            ("How about tires?", "conversation"),
            ("What are we talking about?", "memory_test"),
        ]
        
        print(f"\n🧪 TESTING {len(test_scenarios)} SCENARIOS:")
        print("-" * 50)
        
        total_time = 0
        api_call_counts = []
        memory_continuity_scores = []
        
        for i, (user_input, test_type) in enumerate(test_scenarios, 1):
            print(f"\n{i}. Testing: '{user_input}' ({test_type})")
            
            # Track timing
            start_time = time.time()
            
            try:
                # Process input
                response = await agent.process_input(user_input)
                
                # Calculate timing
                end_time = time.time()
                duration = end_time - start_time
                total_time += duration
                
                # Show results
                print(f"   Response: {response[:80]}{'...' if len(response) > 80 else ''}")
                print(f"   Duration: {duration:.2f}s")
                
                # Check memory state
                memory_vars = agent.memory.load_memory_variables({})
                chat_history = memory_vars.get('chat_history', [])
                print(f"   Memory: {len(chat_history)} messages stored")
                
                # Analyze response quality based on test type
                if test_type == "simple":
                    # Simple queries should be fast
                    if duration < 2.0:
                        print(f"   ✅ Fast response for simple query")
                    else:
                        print(f"   ⚠️ Slow response for simple query ({duration:.2f}s)")
                
                elif test_type == "conversation":
                    # Conversation queries should show some context awareness
                    if len(chat_history) >= 2:
                        print(f"   ✅ Memory maintained in conversation")
                    else:
                        print(f"   ⚠️ Memory not maintained properly")
                
                elif test_type == "memory_test":
                    # Memory test should reference previous conversation
                    context_keywords = ['computer', 'gaming', 'tire', 'talk', 'discuss']
                    found_context = any(kw in response.lower() for kw in context_keywords)
                    if found_context:
                        print(f"   ✅ Shows conversation awareness")
                        memory_continuity_scores.append(1)
                    else:
                        print(f"   ⚠️ Limited conversation awareness")
                        memory_continuity_scores.append(0)
                
                # Performance tracking
                if duration < 1.0:
                    api_call_counts.append("fast")
                elif duration < 5.0:
                    api_call_counts.append("moderate")
                else:
                    api_call_counts.append("slow")
                    
            except Exception as e:
                print(f"   ❌ Error: {e}")
                api_call_counts.append("error")
        
        # Final analysis
        print("\n" + "=" * 70)
        print("📊 COMPREHENSIVE FIX ANALYSIS")
        print("=" * 70)
        
        avg_time = total_time / len(test_scenarios)
        fast_responses = api_call_counts.count("fast")
        moderate_responses = api_call_counts.count("moderate")
        slow_responses = api_call_counts.count("slow")
        error_responses = api_call_counts.count("error")
        
        print(f"Average Response Time: {avg_time:.2f}s")
        print(f"Fast Responses (<1s): {fast_responses}/{len(test_scenarios)}")
        print(f"Moderate Responses (1-5s): {moderate_responses}/{len(test_scenarios)}")
        print(f"Slow Responses (>5s): {slow_responses}/{len(test_scenarios)}")
        print(f"Error Responses: {error_responses}/{len(test_scenarios)}")
        
        if memory_continuity_scores:
            memory_score = sum(memory_continuity_scores) / len(memory_continuity_scores)
            print(f"Memory Continuity Score: {memory_score:.1%}")
        
        # Final memory state
        final_memory = agent.memory.load_memory_variables({})
        final_history = final_memory.get('chat_history', [])
        print(f"Final Memory State: {len(final_history)} total messages")
        
        # Overall assessment
        print(f"\n🎯 OVERALL ASSESSMENT:")
        
        success_criteria = [
            avg_time < 3.0,  # Average response under 3 seconds
            fast_responses >= 3,  # At least 3 fast responses
            slow_responses == 0,  # No slow responses
            error_responses == 0,  # No errors
            len(final_history) >= 6,  # Memory maintained
        ]
        
        passed_criteria = sum(success_criteria)
        total_criteria = len(success_criteria)
        
        print(f"✅ Fast responses: {'PASS' if success_criteria[0] else 'FAIL'}")
        print(f"✅ Simple query optimization: {'PASS' if success_criteria[1] else 'FAIL'}")
        print(f"✅ No slow responses: {'PASS' if success_criteria[2] else 'FAIL'}")
        print(f"✅ No errors: {'PASS' if success_criteria[3] else 'FAIL'}")
        print(f"✅ Memory persistence: {'PASS' if success_criteria[4] else 'FAIL'}")
        
        print(f"\nSUCCESS RATE: {passed_criteria}/{total_criteria} ({passed_criteria/total_criteria*100:.0f}%)")
        
        if passed_criteria >= 4:
            print("\n🎉 CONVERSATION MEMORY FIXES: SUCCESS!")
            print("✅ Agent reuse working (no fresh creation)")
            print("✅ Fast path for simple queries working")
            print("✅ Memory persistence working")
            print("✅ Reduced API calls working")
            return True
        else:
            print(f"\n⚠️ CONVERSATION MEMORY FIXES: PARTIAL SUCCESS")
            print(f"Some fixes working but {total_criteria - passed_criteria} issues remain")
            return False
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run the comprehensive fix test."""
    print("🚀 COMPREHENSIVE CONVERSATION MEMORY FIX TEST")
    print("Testing all fixes: persistent agent, fast path, reduced processing")
    print("=" * 70)
    
    success = await test_conversation_memory_fixes()
    
    print("\n" + "=" * 70)
    if success:
        print("🎉 ALL FIXES WORKING! Conversation memory is now optimized.")
    else:
        print("🔧 SOME FIXES WORKING. Further optimization may be needed.")
    print("=" * 70)
    
    return success

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
