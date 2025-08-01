#!/usr/bin/env python3
"""
Test the fixed conversation memory system in Jarvis.

This script simulates the conversation that was failing before the fix
to verify that conversation memory now works properly.
"""

import sys
import asyncio

# Set up paths
sys.path.insert(0, '.')
sys.path.insert(0, 'jarvis')

async def test_conversation_memory():
    """Test the conversation memory with the exact scenario that was failing."""
    
    print("🧠 TESTING FIXED CONVERSATION MEMORY SYSTEM")
    print("=" * 60)
    
    try:
        from jarvis.config import get_config
        from jarvis.core.agent import JarvisAgent
        from jarvis.tools import get_langchain_tools
        
        # Initialize agent like the fixed start_jarvis.py
        config = get_config()
        agent = JarvisAgent(config.llm, config.agent)
        
        # Get tools
        tools = get_langchain_tools()
        agent.initialize(tools)
        
        print(f"✅ Agent initialized with {len(tools)} tools and conversation memory")
        print(f"   Memory type: {type(agent.memory)}")
        
        # Simulate the failing conversation
        print("\n🎭 SIMULATING THE FAILING CONVERSATION:")
        print("-" * 50)
        
        conversations = [
            "Would you be willing to ask me?",
            "Cars", 
            "How about tires?",
            "What are we talking about?"
        ]
        
        responses = []
        
        for i, user_input in enumerate(conversations, 1):
            print(f"\n{i}. User: '{user_input}'")
            
            try:
                response = await agent.process_input(user_input)
                responses.append(response)
                print(f"   Jarvis: {response[:100]}{'...' if len(response) > 100 else ''}")
                
                # Check memory after each exchange
                memory_vars = agent.memory.load_memory_variables({})
                chat_history = memory_vars.get('chat_history', [])
                print(f"   📊 Memory: {len(chat_history)} messages stored")
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
                responses.append(f"Error: {e}")
        
        # Analyze the final response to "What are we talking about?"
        final_response = responses[-1] if responses else ""
        
        print("\n" + "=" * 60)
        print("📊 CONVERSATION MEMORY ANALYSIS:")
        print("=" * 60)
        
        # Check if the final response shows conversation awareness
        conversation_keywords = [
            'cars', 'tires', 'automotive', 'vehicle', 'discussing', 'talking about',
            'conversation', 'topic', 'questions', 'ask'
        ]
        
        final_response_lower = final_response.lower()
        awareness_indicators = [kw for kw in conversation_keywords if kw in final_response_lower]
        
        print(f"Final response: {final_response}")
        print(f"Awareness indicators found: {awareness_indicators}")
        
        # Get final memory state
        memory_vars = agent.memory.load_memory_variables({})
        chat_history = memory_vars.get('chat_history', [])
        
        print(f"\nFinal memory state: {len(chat_history)} messages")
        for i, msg in enumerate(chat_history[-4:], 1):  # Show last 4 messages
            msg_type = "User" if hasattr(msg, 'content') and i % 2 == 1 else "Jarvis"
            content = msg.content if hasattr(msg, 'content') else str(msg)
            print(f"  {i}. {msg_type}: {content[:60]}{'...' if len(content) > 60 else ''}")
        
        # Determine if fix was successful
        success_criteria = [
            len(chat_history) >= 6,  # Should have at least 6 messages (3 exchanges)
            len(awareness_indicators) > 0,  # Should show conversation awareness
            'error' not in final_response.lower()  # Should not have errors
        ]
        
        success_count = sum(success_criteria)
        
        print(f"\n🎯 SUCCESS CRITERIA ({success_count}/3):")
        print(f"✅ Memory retention: {'PASS' if success_criteria[0] else 'FAIL'}")
        print(f"✅ Conversation awareness: {'PASS' if success_criteria[1] else 'FAIL'}")
        print(f"✅ No errors: {'PASS' if success_criteria[2] else 'FAIL'}")
        
        if success_count == 3:
            print("\n🎉 CONVERSATION MEMORY FIX: COMPLETE SUCCESS!")
            print("✅ Jarvis now maintains conversation context properly")
            print("✅ The failing conversation scenario now works correctly")
            return True
        else:
            print(f"\n⚠️ PARTIAL SUCCESS: {success_count}/3 criteria met")
            print("Some aspects of conversation memory may need further improvement")
            return False
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run the conversation memory test."""
    success = await test_conversation_memory()
    
    print("\n" + "=" * 60)
    if success:
        print("🚀 JARVIS CONVERSATION MEMORY: FULLY FIXED!")
    else:
        print("🔧 JARVIS CONVERSATION MEMORY: NEEDS MORE WORK")
    print("=" * 60)
    
    return success

if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)
