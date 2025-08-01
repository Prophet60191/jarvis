#!/usr/bin/env python3
"""
Simple Conversation Test

This script tests the conversation flow directly to identify
where TTS is being skipped.
"""

import sys
import logging
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_direct_conversation_flow():
    """Test the conversation flow directly."""
    print("🧪 Testing Direct Conversation Flow")
    print("=" * 50)
    
    try:
        from jarvis.config import get_config
        from jarvis.core.conversation import ConversationManager
        from jarvis.core.agent import JarvisAgent
        from jarvis.core.speech import SpeechManager
        from jarvis.tools import get_langchain_tools
        
        config = get_config()
        
        # Create components
        speech_manager = SpeechManager(config.audio)
        speech_manager.initialize()
        print("✅ Speech Manager initialized")
        
        agent = JarvisAgent(config.llm)
        tools = get_langchain_tools()
        agent.initialize(tools)
        print("✅ Agent initialized")
        
        conversation = ConversationManager(config.conversation, speech_manager, agent)
        if not conversation.is_initialized():
            raise Exception("ConversationManager failed to initialize properly")
        print("✅ Conversation Manager initialized")
        
        # Test the complete flow with a simple command
        test_command = "What is 2 plus 2?"
        print(f"\n🧪 Testing command: '{test_command}'")
        
        # Step 1: Process command (should generate response)
        print("📝 Step 1: Processing command...")
        response = conversation.process_command(test_command)
        print(f"✅ Response generated: '{response[:100]}...'")
        
        # Step 2: Deliver response (should speak)
        print("🔊 Step 2: Delivering response via TTS...")
        conversation.respond(response)
        print("✅ Response delivered")
        
        print("\n🎉 Direct conversation flow test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Direct conversation flow test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_agent_only():
    """Test just the agent to see if it generates responses."""
    print("\n🤖 Testing Agent Only")
    print("=" * 30)
    
    try:
        from jarvis.config import get_config
        from jarvis.core.agent import JarvisAgent
        from jarvis.tools import get_langchain_tools
        
        config = get_config()
        
        agent = JarvisAgent(config.llm)
        tools = get_langchain_tools()
        agent.initialize(tools)
        print("✅ Agent initialized")
        
        # Test multiple commands
        test_commands = [
            "What is 2 plus 2?",
            "Tell me a joke",
            "What time is it?",
            "Hello Jarvis"
        ]
        
        for i, command in enumerate(test_commands, 1):
            print(f"\n🧪 Test {i}: '{command}'")
            try:
                response = agent.process_input(command)
                print(f"✅ Response: '{response[:100]}...'")
            except Exception as e:
                print(f"❌ Failed: {e}")
                return False
        
        print("\n✅ All agent tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Agent test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_tts_only():
    """Test just the TTS system."""
    print("\n🔊 Testing TTS Only")
    print("=" * 25)
    
    try:
        from jarvis.config import get_config
        from jarvis.core.speech import SpeechManager
        
        config = get_config()
        
        speech_manager = SpeechManager(config.audio)
        speech_manager.initialize()
        print("✅ Speech Manager initialized")
        
        # Test multiple TTS calls
        test_texts = [
            "This is test number one.",
            "Here is test number two.",
            "And this is test number three.",
            "Final test number four."
        ]
        
        for i, text in enumerate(test_texts, 1):
            print(f"\n🔊 TTS Test {i}: '{text}'")
            try:
                speech_manager.speak_text(text, wait=True)
                print(f"✅ TTS completed for test {i}")
            except Exception as e:
                print(f"❌ TTS failed for test {i}: {e}")
                return False
        
        print("\n✅ All TTS tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ TTS test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function."""
    print("🔧 Simple Conversation Test")
    print("=" * 60)
    print("This test isolates each component to identify TTS issues.\n")
    
    # Run individual tests
    tests = [
        ("TTS System", test_tts_only),
        ("Agent System", test_agent_only),
        ("Complete Conversation Flow", test_direct_conversation_flow),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*60)
    print("📊 Test Summary")
    print("=" * 30)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{len(results)} tests passed")
    
    # Analysis
    print("\n🔍 Analysis:")
    if passed == len(results):
        print("✅ All components working correctly")
        print("   If you're still experiencing inconsistent voice responses,")
        print("   the issue may be in the main application loop or")
        print("   specific conversation scenarios.")
    elif results[0][1] and not results[2][1]:  # TTS works but conversation fails
        print("❌ TTS system works but conversation integration fails")
        print("   The issue is in how the conversation system calls TTS")
    elif not results[0][1]:  # TTS doesn't work
        print("❌ TTS system has issues")
        print("   Fix the TTS system first before testing conversation")
    else:
        print("❌ Multiple system failures detected")
        print("   Check the failed test details above")
    
    return 0 if passed == len(results) else 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n🛑 Test cancelled by user")
    except Exception as e:
        print(f"\n❌ Test script error: {e}")
        sys.exit(1)
