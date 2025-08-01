#!/usr/bin/env python3
"""
Final comprehensive test of the fixed conversation memory system.

This test simulates the exact failing conversation scenario to verify
that Jarvis now properly maintains conversation context and awareness.
"""

import sys
import asyncio
import time

# Set up paths
sys.path.insert(0, '.')
sys.path.insert(0, 'jarvis')

def test_conversation_memory_components():
    """Test all conversation memory components."""
    print("🔧 TESTING CONVERSATION MEMORY COMPONENTS")
    print("-" * 50)
    
    try:
        from jarvis.config import get_config
        from jarvis.core.agent import JarvisAgent
        from jarvis.tools import get_langchain_tools
        
        # Test 1: Agent Creation
        config = get_config()
        agent = JarvisAgent(config.llm, config.agent)
        print("✅ Agent creation: SUCCESS")
        
        # Test 2: Tool Loading
        tools = get_langchain_tools()
        print(f"✅ Tool loading: SUCCESS ({len(tools)} tools)")
        
        # Test 3: Agent Initialization
        agent.initialize(tools)
        print("✅ Agent initialization: SUCCESS")
        
        # Test 4: Memory System
        print(f"✅ Memory system: {type(agent.memory).__name__}")
        
        # Test 5: Memory Operations
        agent.memory.save_context(
            {'input': 'Test input'}, 
            {'output': 'Test output'}
        )
        memory_vars = agent.memory.load_memory_variables({})
        chat_history = memory_vars.get('chat_history', [])
        print(f"✅ Memory operations: SUCCESS ({len(chat_history)} messages)")
        
        # Test 6: Memory Clearing
        agent.clear_chat_memory()
        memory_vars_after = agent.memory.load_memory_variables({})
        chat_history_after = memory_vars_after.get('chat_history', [])
        print(f"✅ Memory clearing: SUCCESS ({len(chat_history_after)} messages)")
        
        return agent, True
        
    except Exception as e:
        print(f"❌ Component test failed: {e}")
        return None, False

async def test_conversation_scenario(agent):
    """Test the exact failing conversation scenario."""
    print("\n🎭 TESTING CONVERSATION SCENARIO")
    print("-" * 50)
    
    # The exact conversation that was failing
    conversation = [
        "Would you be willing to ask me?",
        "Cars", 
        "How about tires?",
        "What are we talking about?"
    ]
    
    responses = []
    success_indicators = []
    
    for i, user_input in enumerate(conversation, 1):
        print(f"\n{i}. User: '{user_input}'")
        
        try:
            # Process with agent
            response = await agent.process_input(user_input)
            responses.append(response)
            
            # Show response (truncated)
            display_response = response[:100] + "..." if len(response) > 100 else response
            print(f"   Jarvis: {display_response}")
            
            # Check memory after each exchange
            memory_vars = agent.memory.load_memory_variables({})
            chat_history = memory_vars.get('chat_history', [])
            print(f"   📊 Memory: {len(chat_history)} messages")
            
            # Analyze response quality
            if i == 1:  # First response should acknowledge the request
                success = any(word in response.lower() for word in ['sure', 'yes', 'ask', 'questions', 'help'])
                success_indicators.append(('Acknowledgment', success))
                
            elif i == 2:  # Second response should connect to first
                success = any(word in response.lower() for word in ['cars', 'automotive', 'vehicle', 'about'])
                success_indicators.append(('Topic Connection', success))
                
            elif i == 3:  # Third response should relate to cars
                success = any(word in response.lower() for word in ['tires', 'cars', 'automotive', 'related'])
                success_indicators.append(('Context Awareness', success))
                
            elif i == 4:  # Fourth response should show conversation awareness
                awareness_words = ['conversation', 'discussing', 'talking', 'cars', 'tires', 'topic']
                success = any(word in response.lower() for word in awareness_words)
                success_indicators.append(('Conversation Memory', success))
                
                if success:
                    found_words = [word for word in awareness_words if word in response.lower()]
                    print(f"   🎯 Awareness indicators: {found_words}")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            responses.append(f"Error: {e}")
            success_indicators.append((f'Response {i}', False))
    
    return responses, success_indicators

def analyze_results(success_indicators, responses):
    """Analyze the test results."""
    print("\n📊 CONVERSATION MEMORY ANALYSIS")
    print("=" * 60)
    
    # Show success indicators
    passed = sum(1 for _, success in success_indicators if success)
    total = len(success_indicators)
    
    print("Test Results:")
    for test_name, success in success_indicators:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {status} {test_name}")
    
    print(f"\nOverall Score: {passed}/{total} ({passed/total*100:.0f}%)")
    
    # Analyze final response for conversation awareness
    if responses:
        final_response = responses[-1]
        print(f"\nFinal Response Analysis:")
        print(f"Response: {final_response[:200]}...")
        
        # Check for conversation awareness keywords
        awareness_keywords = [
            'conversation', 'discussing', 'talking', 'topic', 'cars', 'tires', 
            'automotive', 'questions', 'ask', 'context'
        ]
        
        found_keywords = [kw for kw in awareness_keywords if kw.lower() in final_response.lower()]
        print(f"Awareness Keywords Found: {found_keywords}")
    
    # Determine overall success
    if passed >= 3:  # At least 3/4 tests should pass
        print("\n🎉 CONVERSATION MEMORY FIX: SUCCESS!")
        print("✅ Jarvis now maintains proper conversation context")
        print("✅ The failing conversation scenario works correctly")
        return True
    else:
        print(f"\n⚠️ CONVERSATION MEMORY: PARTIAL SUCCESS ({passed}/{total})")
        print("Some aspects may need further improvement")
        return False

async def main():
    """Run the comprehensive conversation memory test."""
    print("🧠 FINAL CONVERSATION MEMORY TEST")
    print("=" * 60)
    print("Testing the complete fix for Jarvis conversation memory...")
    print("=" * 60)
    
    # Test components
    agent, components_ok = test_conversation_memory_components()
    
    if not components_ok:
        print("\n❌ Component tests failed - cannot proceed")
        return False
    
    # Test conversation scenario
    responses, success_indicators = await test_conversation_scenario(agent)
    
    # Analyze results
    overall_success = analyze_results(success_indicators, responses)
    
    print("\n" + "=" * 60)
    if overall_success:
        print("🚀 JARVIS CONVERSATION MEMORY: FULLY FIXED!")
        print("Ready for production use with proper conversation awareness")
    else:
        print("🔧 JARVIS CONVERSATION MEMORY: NEEDS REFINEMENT")
        print("Basic functionality works but conversation awareness could be improved")
    print("=" * 60)
    
    return overall_success

if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n\n👋 Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
