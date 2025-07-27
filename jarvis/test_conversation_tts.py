#!/usr/bin/env python3
"""
Test Conversation TTS Integration

This script tests the conversation system's TTS integration
to identify why voice responses are inconsistent.
"""

import sys
import logging
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set up logging to see TTS details
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_conversation_respond():
    """Test the conversation respond method directly."""
    print("💬 Testing Conversation Respond Method")
    print("=" * 50)
    
    try:
        from jarvis.config import get_config
        from jarvis.core.conversation import ConversationManager
        from jarvis.core.agent import JarvisAgent
        
        config = get_config()
        
        # Create a minimal agent (not needed for TTS test)
        agent = JarvisAgent(config.llm)
        
        # Create conversation manager
        conversation = ConversationManager(config.conversation, agent)
        
        print("✅ Conversation Manager created")
        
        # Initialize
        conversation.initialize()
        print("✅ Conversation Manager initialized")
        
        # Test response delivery multiple times
        test_responses = [
            "This is the first test response.",
            "Here's a second test to check consistency.",
            "And a third response to verify reliability.",
            "Final test response to confirm TTS works every time."
        ]
        
        for i, test_text in enumerate(test_responses, 1):
            print(f"\n🔊 Test {i}: '{test_text}'")
            try:
                conversation.respond(test_text)
                print(f"✅ Test {i} completed successfully")
            except Exception as e:
                print(f"❌ Test {i} failed: {e}")
                return False
        
        print("\n✅ All conversation TTS tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Conversation TTS test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_speech_manager_consistency():
    """Test speech manager consistency with multiple calls."""
    print("\n🎤 Testing Speech Manager Consistency")
    print("=" * 45)
    
    try:
        from jarvis.config import get_config
        from jarvis.core.speech import SpeechManager
        
        config = get_config()
        speech_manager = SpeechManager(config.audio)
        
        print("✅ Speech Manager created")
        
        # Initialize
        speech_manager.initialize()
        print("✅ Speech Manager initialized")
        
        # Test multiple TTS calls in sequence
        test_texts = [
            "Testing speech consistency, attempt one.",
            "Second attempt to verify reliability.",
            "Third test for consistent voice output.",
            "Fourth and final consistency check."
        ]
        
        for i, text in enumerate(test_texts, 1):
            print(f"\n🔊 Consistency Test {i}: '{text[:30]}...'")
            try:
                speech_manager.speak_text(text, wait=True)
                print(f"✅ Consistency Test {i} completed")
            except Exception as e:
                print(f"❌ Consistency Test {i} failed: {e}")
                return False
        
        print("\n✅ All speech manager consistency tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Speech Manager consistency test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function."""
    print("🔧 Conversation TTS Integration Test")
    print("=" * 60)
    print("This test identifies why voice responses are inconsistent.\n")
    
    # Run tests
    tests = [
        ("Speech Manager Consistency", test_speech_manager_consistency),
        ("Conversation Respond Method", test_conversation_respond),
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
        print("✅ All tests passed - TTS integration is working correctly")
        print("   If you're still experiencing inconsistent voice responses:")
        print("   - Check the actual Jarvis conversation logs during use")
        print("   - Look for specific error patterns in the logs")
        print("   - The issue may be intermittent or context-specific")
    else:
        print("❌ TTS integration issues detected")
        print("   - Review the failed test details above")
        print("   - Check error logs for specific TTS failures")
        print("   - Consider audio device or system-level issues")
    
    return 0 if passed == len(results) else 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n🛑 Test cancelled by user")
    except Exception as e:
        print(f"\n❌ Test script error: {e}")
        sys.exit(1)
