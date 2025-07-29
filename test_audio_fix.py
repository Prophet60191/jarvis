#!/usr/bin/env python3
"""
Test script to verify audio cutoff fix.

This script tests the TTS audio playback to ensure it doesn't cut out
after 4-5 words or drop in volume.
"""

import sys
import time
from pathlib import Path

# Add jarvis to path
sys.path.insert(0, str(Path(__file__).parent / "jarvis"))

def test_audio_playback():
    """Test TTS audio playback for volume drops and cutoffs."""
    print("🔊 Testing Audio Playback Fix")
    print("=" * 60)
    
    try:
        from jarvis.config import get_config
        from jarvis.audio.tts import TextToSpeechManager
        
        # Initialize TTS
        config = get_config()
        tts_manager = TextToSpeechManager(config.audio)
        tts_manager.initialize()
        
        # Test sentences that should trigger the issue
        test_sentences = [
            "Testing one two three four five six seven eight nine ten.",
            "The logs terminal has been opened showing real-time debug information.",
            "This is a longer sentence that should play completely without any volume drops or audio cutoffs in the middle of speaking.",
            "I've opened the RAG Management interface with the Document Upload panel for you to use.",
            "Jarvis is now using reliable audio playback with afplay on macOS instead of sounddevice."
        ]
        
        print("🎯 Testing for audio cutoffs and volume drops...")
        print("   Listen carefully - audio should be consistent throughout each sentence")
        print()
        
        for i, sentence in enumerate(test_sentences, 1):
            print(f"Test {i}: '{sentence[:40]}{'...' if len(sentence) > 40 else ''}'")
            print("🔊 Playing...")
            
            try:
                start_time = time.time()
                tts_manager.speak(sentence, wait=True)
                end_time = time.time()
                duration = end_time - start_time
                
                print(f"✅ Completed in {duration:.2f} seconds")
                
                # Ask user for feedback
                feedback = input("Did the audio play completely without cutoffs? (y/n): ").strip().lower()
                if feedback.startswith('n'):
                    print("❌ Audio issue detected!")
                    return False
                elif feedback.startswith('y'):
                    print("✅ Audio played correctly")
                else:
                    print("⚠️  Skipping feedback")
                
                print()
                time.sleep(1)
                
            except Exception as e:
                print(f"❌ TTS failed: {e}")
                return False
        
        print("🎉 All audio tests completed!")
        return True
        
    except Exception as e:
        print(f"❌ Test setup failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_audio_method():
    """Test which audio playback method is being used."""
    print("\n🔍 Testing Audio Playback Method")
    print("=" * 60)
    
    try:
        import os
        
        # Check if we're on macOS with afplay
        if os.name == 'posix' and os.system('which afplay > /dev/null 2>&1') == 0:
            print("✅ macOS detected - should use afplay for reliable audio")
            print("   afplay is Apple's native audio player and most reliable")
        else:
            print("ℹ️  Not macOS - will use sounddevice or other fallback")
        
        # Test a simple sentence
        from jarvis.config import get_config
        from jarvis.audio.coqui_tts import CoquiTTSManager
        
        config = get_config()
        coqui = CoquiTTSManager(config.audio)
        coqui.initialize()
        
        print("\n🔊 Testing direct Coqui TTS playback...")
        test_text = "Testing audio playback method on this system."
        
        start_time = time.time()
        coqui.speak(test_text, wait=True)
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"✅ Direct Coqui TTS completed in {duration:.2f} seconds")
        
        feedback = input("Did this test play clearly without volume drops? (y/n): ").strip().lower()
        if feedback.startswith('y'):
            print("✅ Audio method is working correctly")
            return True
        else:
            print("❌ Audio method may need further adjustment")
            return False
        
    except Exception as e:
        print(f"❌ Audio method test failed: {e}")
        return False


def test_voice_comparison():
    """Compare different Jarvis voices clearly."""
    print("\n🎤 Jarvis Voice Comparison")
    print("=" * 60)

    try:
        from jarvis.config import get_config
        from jarvis.audio.tts import TextToSpeechManager

        config = get_config()
        tts = TextToSpeechManager(config.audio)
        tts.initialize()

        test_text = "Hello, I am Jarvis. This is how I sound with this voice."

        print("🔊 Current Voice Test:")
        print(f"Speaking: '{test_text}'")

        start_time = time.time()
        tts.speak(test_text, wait=True)
        end_time = time.time()

        print(f"✅ Completed in {end_time - start_time:.2f} seconds")

        # Show what voice is actually being used
        if hasattr(tts, 'coqui_tts') and tts.coqui_tts.is_initialized():
            print("🤖 Using: Coqui TTS (Neural Voice)")
            print(f"   Model: {config.audio.coqui_model}")
            if "ljspeech" in config.audio.coqui_model.lower():
                print("   Voice: Linda Johnson (Female, American)")
        else:
            print("🍎 Using: Apple System TTS")
            print(f"   Voice: {config.audio.tts_voice_preference}")

        return True

    except Exception as e:
        print(f"❌ Voice comparison failed: {e}")
        return False


def main():
    """Run audio fix verification tests."""
    print("🧪 Jarvis Audio & Voice Testing")
    print("=" * 60)
    print("This script tests audio playback and voice options")
    print("=" * 60)
    
    # Run tests
    tests = [
        ("Audio Playback Method Test", test_audio_method),
        ("Audio Cutoff Test", test_audio_playback)
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
        print("🎉 Audio fix appears to be working!")
        print("   TTS should now play completely without cutoffs.")
    else:
        print("⚠️  Audio issues may persist. Additional fixes needed.")
    
    print("\n💡 Changes made:")
    print("   ✅ Switched to afplay on macOS (more reliable)")
    print("   ✅ Removed complex sounddevice interruption handling")
    print("   ✅ Simplified audio playback to blocking calls")
    print("   ✅ Eliminated audio session conflicts")
    
    print("\n🔧 If audio still cuts out:")
    print("   1. Check system audio settings")
    print("   2. Verify no other apps are using audio")
    print("   3. Test with different audio output devices")
    print("   4. Check macOS audio permissions for Terminal/Python")


if __name__ == "__main__":
    main()
