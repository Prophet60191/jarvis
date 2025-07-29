#!/usr/bin/env python3
"""
Debug Agent Response Issue

Test why the agent isn't returning responses or speaking.
"""

import sys
import time
import asyncio
from pathlib import Path

# Add jarvis to path
sys.path.insert(0, str(Path(__file__).parent / "jarvis"))

def test_agent_directly():
    """Test the agent directly to see if it responds."""
    print("🔍 TESTING AGENT DIRECTLY")
    print("=" * 40)
    
    try:
        from jarvis.config import get_config
        from jarvis.core.agent import JarvisAgent
        from jarvis.tools import get_langchain_tools
        
        config = get_config()
        
        # Initialize agent
        print("🧠 Initializing agent...")
        agent = JarvisAgent(config.llm, config.agent)
        tools = get_langchain_tools()
        agent.initialize(tools=tools)
        print(f"✅ Agent initialized with {len(tools)} tools")
        
        # Test simple query
        print("\n🧪 Testing simple query...")
        test_query = "What time is it?"
        print(f"Query: '{test_query}'")
        
        try:
            # Test async method directly
            print("⏳ Processing with async...")
            start_time = time.time()
            
            response = asyncio.run(agent.process_input(test_query))
            
            end_time = time.time()
            duration = end_time - start_time
            
            print(f"✅ Response received in {duration:.2f}s:")
            print(f"🤖 Agent: {response}")
            
            return response
            
        except Exception as e:
            print(f"❌ Agent processing failed: {e}")
            import traceback
            traceback.print_exc()
            return None
            
    except Exception as e:
        print(f"❌ Agent initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_tts_directly():
    """Test TTS directly to see if it works."""
    print("\n🔊 TESTING TTS DIRECTLY")
    print("=" * 40)
    
    try:
        from jarvis.config import get_config
        from jarvis.core.speech import SpeechManager
        
        config = get_config()
        
        # Initialize speech manager
        print("🔊 Initializing speech manager...")
        speech_manager = SpeechManager(config.audio)
        speech_manager.initialize()
        print("✅ Speech manager initialized")
        
        # Test TTS
        test_text = "This is a test of the text to speech system."
        print(f"\n🎤 Testing TTS with: '{test_text}'")
        
        try:
            start_time = time.time()
            speech_manager.speak_text(test_text)
            end_time = time.time()
            duration = end_time - start_time
            
            print(f"✅ TTS completed in {duration:.2f}s")
            return True
            
        except Exception as e:
            print(f"❌ TTS failed: {e}")
            import traceback
            traceback.print_exc()
            return False
            
    except Exception as e:
        print(f"❌ Speech manager initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_combined_flow():
    """Test the combined flow like in the main app."""
    print("\n🔄 TESTING COMBINED FLOW")
    print("=" * 40)
    
    try:
        from jarvis.config import get_config
        from jarvis.core.speech import SpeechManager
        from jarvis.core.agent import JarvisAgent
        from jarvis.tools import get_langchain_tools
        
        config = get_config()
        
        # Initialize components
        print("🔊 Initializing speech manager...")
        speech_manager = SpeechManager(config.audio)
        speech_manager.initialize()
        
        print("🧠 Initializing agent...")
        agent = JarvisAgent(config.llm, config.agent)
        tools = get_langchain_tools()
        agent.initialize(tools=tools)
        
        print("✅ Both components initialized")
        
        # Test the exact flow from the main app
        command_text = "What time is it?"
        print(f"\n🧪 Testing combined flow with: '{command_text}'")
        
        try:
            # Process with agent (same as main app)
            print("⏳ Processing with agent...")
            start_time = time.time()
            
            # Handle async process_input method (same as main app)
            try:
                # Try to use existing event loop
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # Create a new event loop for this call
                    response = asyncio.run(agent.process_input(command_text))
                else:
                    response = loop.run_until_complete(agent.process_input(command_text))
            except RuntimeError:
                # No event loop, create one
                response = asyncio.run(agent.process_input(command_text))
            
            end_time = time.time()
            duration = end_time - start_time
            
            print(f"✅ Agent response in {duration:.2f}s: '{response}'")
            
            # Test TTS response
            print("🔊 Testing TTS response...")
            tts_start = time.time()
            speech_manager.speak_text(response)
            tts_end = time.time()
            tts_duration = tts_end - tts_start
            
            print(f"✅ TTS completed in {tts_duration:.2f}s")
            print(f"🎉 COMBINED FLOW SUCCESSFUL!")
            
            return True
            
        except Exception as e:
            print(f"❌ Combined flow failed: {e}")
            import traceback
            traceback.print_exc()
            return False
            
    except Exception as e:
        print(f"❌ Combined flow initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all diagnostic tests."""
    print("🔍 AGENT RESPONSE DIAGNOSTIC")
    print("=" * 50)
    print("Testing why agent isn't responding or speaking...")
    print()
    
    # Test 1: Agent directly
    agent_response = test_agent_directly()
    
    # Test 2: TTS directly
    tts_works = test_tts_directly()
    
    # Test 3: Combined flow
    combined_works = test_combined_flow()
    
    # Summary
    print("\n📊 DIAGNOSTIC SUMMARY")
    print("=" * 30)
    print(f"Agent Response: {'✅ WORKS' if agent_response else '❌ FAILS'}")
    print(f"TTS System: {'✅ WORKS' if tts_works else '❌ FAILS'}")
    print(f"Combined Flow: {'✅ WORKS' if combined_works else '❌ FAILS'}")
    
    if agent_response and tts_works and combined_works:
        print("\n🎉 ALL SYSTEMS WORKING!")
        print("The issue might be in the main app's error handling or timing.")
    else:
        print("\n❌ ISSUES FOUND:")
        if not agent_response:
            print("  • Agent not responding properly")
        if not tts_works:
            print("  • TTS system not working")
        if not combined_works:
            print("  • Combined flow has issues")


if __name__ == "__main__":
    main()
