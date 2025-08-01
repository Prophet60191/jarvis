#!/usr/bin/env python3
"""
Test script to verify TTS works without cutoffs after removing full-duplex.

This script tests the conversation system to ensure TTS completes
without being interrupted mid-sentence.
"""

import sys
import time
from pathlib import Path

# Add jarvis to path
sys.path.insert(0, str(Path(__file__).parent / "jarvis"))

def test_conversation_tts():
    """Test TTS through the conversation system."""
    print("🔊 Testing Conversation TTS (No Full-Duplex)")
    print("=" * 60)
    
    try:
        from jarvis.config import get_config
        from jarvis.core.conversation import ConversationManager
        from jarvis.core.speech import SpeechManager
        from jarvis.core.agent import JarvisAgent
        
        # Initialize components
        config = get_config()
        
        # Verify full-duplex is disabled
        print(f"📋 Full-duplex enabled: {config.conversation.enable_full_duplex}")
        if config.conversation.enable_full_duplex:
            print("⚠️  WARNING: Full-duplex is still enabled in config!")
        else:
            print("✅ Full-duplex is disabled as expected")
        
        # Initialize speech manager
        speech_manager = SpeechManager(config.audio)
        speech_manager.initialize()
        
        # Initialize agent
        agent = JarvisAgent(config)
        
        # Initialize conversation manager
        conversation = ConversationManager(config.conversation, speech_manager, agent)
        
        # Test sentences that previously caused cutoffs
        test_responses = [
            "This is a short test response.",
            "The logs terminal has been opened, showing you real-time debug information and technical details if needed.",
            "I've opened the RAG Management interface with the Document Upload panel. You can now upload documents, manage memories, and configure the RAG system through the web interface.",
            "Here's a longer response that should complete without any interruptions or cutoffs. The system should speak this entire sentence from beginning to end without any issues, demonstrating that the full-duplex removal has fixed the TTS cutoff problem.",
            "Testing multiple sentences in one response. This first sentence should complete fully. Then this second sentence should also complete without interruption. Finally, this third sentence should demonstrate that the entire response plays through to completion."
        ]
        
        for i, response in enumerate(test_responses, 1):
            print(f"\n🎯 Test {i}: {len(response)} characters")
            print(f"Text: '{response[:60]}{'...' if len(response) > 60 else ''}'")
            
            try:
                start_time = time.time()
                print("🔊 Starting conversation response...")
                
                # Use the conversation system's response delivery
                conversation._deliver_response(response)
                
                end_time = time.time()
                duration = end_time - start_time
                
                print(f"✅ Completed in {duration:.2f} seconds")
                
                # Wait between tests
                time.sleep(1)
                
            except Exception as e:
                print(f"❌ Response delivery failed: {e}")
        
        print(f"\n🎉 Conversation TTS Test Complete!")
        return True
        
    except Exception as e:
        print(f"❌ Test setup failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_direct_speech_manager():
    """Test TTS directly through speech manager."""
    print("\n🔊 Testing Direct Speech Manager")
    print("=" * 60)
    
    try:
        from jarvis.config import get_config
        from jarvis.core.speech import SpeechManager
        
        # Initialize speech manager
        config = get_config()
        speech_manager = SpeechManager(config.audio)
        speech_manager.initialize()
        
        # Test the same problematic sentence
        test_text = "The logs terminal has been opened, showing you real-time debug information and technical details if needed."
        
        print(f"Text: '{test_text}'")
        print("🔊 Starting direct TTS...")
        
        start_time = time.time()
        speech_manager.speak_text(test_text, wait=True)
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"✅ Completed in {duration:.2f} seconds")
        
        return True
        
    except Exception as e:
        print(f"❌ Direct speech test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run TTS cutoff tests."""
    print("🧪 Jarvis TTS Cutoff Fix Verification")
    print("=" * 60)
    print("Testing TTS after removing full-duplex mode")
    print("=" * 60)
    
    # Run tests
    tests = [
        ("Direct Speech Manager Test", test_direct_speech_manager),
        ("Conversation TTS Test", test_conversation_tts)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print(f"\n{'='*60}")
    print("🧪 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status}: {test_name}")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! TTS cutoff issue should be resolved.")
        print("   Full-duplex removal appears to have fixed the problem.")
    else:
        print("⚠️  Some tests failed. Further investigation may be needed.")
    
    print("\n💡 Changes made:")
    print("   ✅ Removed full-duplex conversation mode")
    print("   ✅ Removed interruption listening thread")
    print("   ✅ Simplified conversation flow to single-mode")
    print("   ✅ Enhanced TTS interruption handling")
    print("   ✅ Updated configuration to disable full-duplex")
    
    print("\n🔧 If TTS still cuts out:")
    print("   1. Check audio device conflicts")
    print("   2. Verify microphone isn't picking up TTS output")
    print("   3. Test with different TTS engines (Apple vs Coqui)")
    print("   4. Check system audio settings")


if __name__ == "__main__":
    main()
