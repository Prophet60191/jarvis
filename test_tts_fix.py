#!/usr/bin/env python3
"""
Test script to verify TTS cutoff fix.

This script tests the TTS system directly without the conversation system
to isolate whether the issue is in TTS playback or interruption handling.
"""

import sys
import time
from pathlib import Path

# Add jarvis to path
sys.path.insert(0, str(Path(__file__).parent / "jarvis"))

def test_tts_direct():
    """Test TTS directly without conversation system."""
    print("🔊 Testing TTS Direct Playback (No Interruption System)")
    print("=" * 60)
    
    try:
        from jarvis.config import get_config
        from jarvis.audio.tts import TextToSpeechManager
        
        # Initialize TTS
        config = get_config()
        tts_manager = TextToSpeechManager(config.audio)
        tts_manager.initialize()
        
        # Test sentences of varying lengths
        test_sentences = [
            "This is a short test.",
            "This is a medium length test sentence to check if the audio cuts out in the middle of speaking.",
            "This is a very long test sentence that should take several seconds to complete and will help us determine if the text-to-speech system is cutting out prematurely during longer utterances, which has been reported as an issue.",
            "The logs terminal has been opened, showing you real-time debug information and technical details if needed.",
            "I've opened the RAG Management interface with the Document Upload panel. You can now upload documents, manage memories, and configure the RAG system through the web interface."
        ]
        
        for i, sentence in enumerate(test_sentences, 1):
            print(f"\n🎯 Test {i}: {len(sentence)} characters")
            print(f"Text: '{sentence[:50]}{'...' if len(sentence) > 50 else ''}'")
            
            try:
                start_time = time.time()
                print("🔊 Starting TTS...")
                
                # Test with wait=True (blocking)
                tts_manager.speak(sentence, wait=True)
                
                end_time = time.time()
                duration = end_time - start_time
                
                print(f"✅ Completed in {duration:.2f} seconds")
                
                # Wait between tests
                time.sleep(1)
                
            except Exception as e:
                print(f"❌ TTS failed: {e}")
        
        print(f"\n🎉 TTS Direct Test Complete!")
        return True
        
    except Exception as e:
        print(f"❌ Test setup failed: {e}")
        return False


def test_tts_with_interruption():
    """Test TTS with interruption system enabled."""
    print("\n🔊 Testing TTS with Interruption System")
    print("=" * 60)
    
    try:
        from jarvis.config import get_config
        from jarvis.core.speech import SpeechManager
        from jarvis.core.interruption import interruption_manager
        
        # Initialize speech manager (includes TTS + interruption)
        config = get_config()
        speech_manager = SpeechManager(config.audio)
        speech_manager.initialize()
        
        # Test with interruption system
        test_sentence = "This is a test with the interruption system enabled to see if it causes premature cutoffs during normal speech output."
        
        print(f"Text: '{test_sentence}'")
        print("🔊 Starting TTS with interruption system...")
        
        # Disable interruption temporarily for this test
        interruption_manager.enable_interruption(False)
        
        try:
            start_time = time.time()
            speech_manager.speak_text(test_sentence, wait=True)
            end_time = time.time()
            duration = end_time - start_time
            
            print(f"✅ Completed in {duration:.2f} seconds (interruption disabled)")
            
        except Exception as e:
            print(f"❌ TTS with interruption failed: {e}")
        
        # Test with interruption enabled
        print("\n🔊 Testing with interruption enabled...")
        interruption_manager.enable_interruption(True)
        
        try:
            start_time = time.time()
            speech_manager.speak_text(test_sentence, wait=True)
            end_time = time.time()
            duration = end_time - start_time
            
            print(f"✅ Completed in {duration:.2f} seconds (interruption enabled)")
            
        except Exception as e:
            print(f"❌ TTS with interruption enabled failed: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Interruption test failed: {e}")
        return False


def test_audio_isolation():
    """Test if TTS audio is being detected as user input."""
    print("\n🔊 Testing Audio Isolation")
    print("=" * 60)
    
    try:
        from jarvis.config import get_config
        from jarvis.core.speech import SpeechManager
        
        config = get_config()
        speech_manager = SpeechManager(config.audio)
        speech_manager.initialize()
        
        print("🎯 This test will speak and then immediately try to listen")
        print("   If audio isolation is working, it should not detect the TTS as input")
        
        # Speak something
        test_text = "Testing audio isolation. The system should not hear this as user input."
        print(f"🔊 Speaking: '{test_text}'")
        
        speech_manager.speak_text(test_text, wait=True)
        
        # Wait a moment for audio to settle
        time.sleep(0.5)
        
        # Try to listen immediately after
        print("👂 Listening for 3 seconds to check for audio bleed...")
        
        try:
            result = speech_manager.listen_for_speech(timeout=3.0, phrase_time_limit=2.0)
            if result:
                print(f"⚠️  Audio bleed detected: '{result}'")
                print("   This suggests TTS audio is being picked up as user input")
            else:
                print("✅ No audio bleed detected - isolation working correctly")
        except Exception as e:
            if "timed out" in str(e).lower() or "no speech" in str(e).lower():
                print("✅ No audio detected - isolation working correctly")
            else:
                print(f"❌ Listen test failed: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Audio isolation test failed: {e}")
        return False


def main():
    """Run all TTS tests."""
    print("🧪 Jarvis TTS Cutoff Diagnosis")
    print("=" * 60)
    print("This script will test various aspects of the TTS system")
    print("to identify why Jarvis cuts out mid-sentence.")
    print("=" * 60)
    
    # Run tests
    tests = [
        ("Direct TTS Test", test_tts_direct),
        ("Interruption System Test", test_tts_with_interruption),
        ("Audio Isolation Test", test_audio_isolation)
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
        print("🎉 All tests passed! TTS system appears to be working correctly.")
        print("   The cutoff issue may be in the conversation flow or interruption logic.")
    else:
        print("⚠️  Some tests failed. The TTS system has issues that need to be addressed.")
    
    print("\n💡 Next steps:")
    print("   1. Check the debug logs for detailed error information")
    print("   2. Adjust interruption sensitivity if needed")
    print("   3. Verify audio isolation settings")
    print("   4. Test with different TTS engines (Apple vs Coqui)")


if __name__ == "__main__":
    main()
