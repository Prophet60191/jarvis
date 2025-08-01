#!/usr/bin/env python3
"""
Debug TTS Consistency Issues

This script tests the LLM -> TTS pipeline to identify why TTS
might not be triggered consistently.
"""

import sys
import logging
import time
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set up detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_llm_to_tts_pipeline():
    """Test the complete LLM to TTS pipeline."""
    print("🔍 Testing LLM -> TTS Pipeline")
    print("=" * 50)
    
    try:
        from jarvis.config import get_config
        from jarvis.core.agent import JarvisAgent
        from jarvis.core.speech import SpeechManager
        from jarvis.core.conversation import ConversationManager
        from jarvis.tools import get_langchain_tools
        
        # Load configuration
        config = get_config()
        print("✅ Configuration loaded")
        
        # Initialize speech manager
        speech_manager = SpeechManager(config.audio)
        speech_manager.initialize()
        print("✅ Speech manager initialized")
        
        # Initialize LLM agent
        agent = JarvisAgent(config.llm)
        langchain_tools = get_langchain_tools()
        agent.initialize(tools=langchain_tools)
        print(f"✅ Agent initialized with {len(langchain_tools)} tools")
        
        # Test direct TTS
        print("\n🔊 Testing Direct TTS:")
        test_text = "This is a direct TTS test."
        print(f"Speaking: '{test_text}'")
        speech_manager.speak_text(test_text, wait=True)
        print("✅ Direct TTS completed")
        
        # Test LLM response generation
        print("\n🤖 Testing LLM Response Generation:")
        test_queries = [
            "What time is it?",
            "Hello, how are you?",
            "Tell me a joke",
            "What's 2 + 2?",
            "What can you help me with?"
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n--- Test {i}: '{query}' ---")
            
            try:
                # Generate LLM response
                print("🧠 Generating LLM response...")
                response = agent.process_input(query)
                print(f"📝 LLM Response: '{response[:100]}{'...' if len(response) > 100 else ''}'")
                
                # Test TTS of response
                print("🔊 Testing TTS of response...")
                speech_manager.speak_text(response, wait=True)
                print("✅ TTS completed successfully")
                
                # Small delay between tests
                time.sleep(1)
                
            except Exception as e:
                print(f"❌ Test {i} failed: {e}")
                import traceback
                traceback.print_exc()
                continue
        
        print("\n✅ LLM -> TTS pipeline tests completed")
        return True
        
    except Exception as e:
        print(f"❌ Pipeline test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_conversation_manager():
    """Test the conversation manager's TTS consistency."""
    print("\n🗣️ Testing Conversation Manager TTS Consistency")
    print("=" * 60)
    
    try:
        from jarvis.config import get_config
        from jarvis.core.agent import JarvisAgent
        from jarvis.core.speech import SpeechManager
        from jarvis.core.conversation import ConversationManager
        from jarvis.tools import get_langchain_tools
        
        # Load configuration
        config = get_config()
        
        # Initialize components
        speech_manager = SpeechManager(config.audio)
        speech_manager.initialize()
        
        agent = JarvisAgent(config.llm)
        langchain_tools = get_langchain_tools()
        agent.initialize(tools=langchain_tools)
        
        # Initialize conversation manager
        conversation_manager = ConversationManager(
            config.conversation,
            speech_manager,
            agent
        )
        print("✅ Conversation manager initialized")
        
        # Test conversation manager's respond method directly
        test_responses = [
            "Hello! I'm working correctly.",
            "The current time is 9:15 PM.",
            "I can help you with various tasks.",
            "This is a test of the TTS consistency.",
            "Everything seems to be functioning properly."
        ]
        
        for i, response_text in enumerate(test_responses, 1):
            print(f"\n--- Conversation Test {i} ---")
            print(f"Response: '{response_text}'")
            
            try:
                # Test the conversation manager's respond method
                conversation_manager.respond(response_text)
                print("✅ Conversation manager TTS completed")
                
                # Small delay
                time.sleep(0.5)
                
            except Exception as e:
                print(f"❌ Conversation manager TTS failed: {e}")
                import traceback
                traceback.print_exc()
        
        print("\n✅ Conversation manager tests completed")
        return True
        
    except Exception as e:
        print(f"❌ Conversation manager test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_error_conditions():
    """Test TTS behavior under error conditions."""
    print("\n⚠️ Testing TTS Under Error Conditions")
    print("=" * 45)
    
    try:
        from jarvis.config import get_config
        from jarvis.core.speech import SpeechManager
        
        config = get_config()
        speech_manager = SpeechManager(config.audio)
        speech_manager.initialize()
        
        # Test empty text
        print("🧪 Testing empty text...")
        try:
            speech_manager.speak_text("", wait=True)
            print("✅ Empty text handled")
        except Exception as e:
            print(f"❌ Empty text failed: {e}")
        
        # Test very long text
        print("\n🧪 Testing very long text...")
        long_text = "This is a very long text. " * 50
        try:
            speech_manager.speak_text(long_text, wait=True)
            print("✅ Long text handled")
        except Exception as e:
            print(f"❌ Long text failed: {e}")
        
        # Test special characters
        print("\n🧪 Testing special characters...")
        special_text = "Testing special characters: @#$%^&*()[]{}|\\:;\"'<>,.?/~`"
        try:
            speech_manager.speak_text(special_text, wait=True)
            print("✅ Special characters handled")
        except Exception as e:
            print(f"❌ Special characters failed: {e}")
        
        print("\n✅ Error condition tests completed")
        return True
        
    except Exception as e:
        print(f"❌ Error condition test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main diagnostic function."""
    print("🔧 TTS Consistency Diagnostic Tool")
    print("=" * 70)
    print("This tool tests the LLM -> TTS pipeline to identify consistency issues.\n")
    
    # Run tests
    tests = [
        ("LLM -> TTS Pipeline", test_llm_to_tts_pipeline),
        ("Conversation Manager", test_conversation_manager),
        ("Error Conditions", test_error_conditions),
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
    print("\n" + "="*70)
    print("📊 Diagnostic Summary")
    print("=" * 35)
    
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
        print("✅ TTS pipeline appears to be working consistently")
        print("   - If you're still experiencing issues, they may be:")
        print("     • Timing-related (race conditions)")
        print("     • Context-specific (certain types of responses)")
        print("     • Environment-specific (audio device conflicts)")
    else:
        print("❌ TTS consistency issues detected")
        print("   - Check the failed test details above")
        print("   - Look for patterns in the failures")
        print("   - Check system logs for additional error details")
    
    return 0 if passed == len(results) else 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n🛑 Diagnostic cancelled by user")
    except Exception as e:
        print(f"\n❌ Diagnostic script error: {e}")
        sys.exit(1)
