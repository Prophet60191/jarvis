#!/usr/bin/env python3
"""
Simple Wake Word Test - Using Original Synchronous Initialization

This test uses the original synchronous initialization method to see
if the async changes broke wake word detection.
"""

import sys
from pathlib import Path

# Add jarvis to path
sys.path.insert(0, str(Path(__file__).parent / "jarvis"))

def test_original_sync_initialization():
    """Test wake word detection using original synchronous initialization."""
    print("🔍 TESTING WAKE WORD WITH ORIGINAL SYNC INITIALIZATION")
    print("=" * 60)
    
    try:
        from jarvis.config import get_config
        from jarvis.core.speech import SpeechManager
        from jarvis.core.wake_word import WakeWordDetector
        
        print("1. 📋 Loading configuration...")
        config = get_config()
        print(f"   ✅ Config loaded: mic={config.audio.mic_name}, threshold={config.audio.energy_threshold}")
        
        print("2. 🔊 Initializing speech manager (synchronous)...")
        speech_manager = SpeechManager(config.audio)
        speech_manager.initialize()
        print("   ✅ Speech manager initialized")
        
        print("3. 👂 Initializing wake word detector (synchronous)...")
        wake_word_detector = WakeWordDetector(config.conversation, speech_manager)
        print("   ✅ Wake word detector initialized")
        
        print("4. 🎙️  Testing wake word detection (say 'jarvis' in 5 seconds)...")
        detection = wake_word_detector.listen_once(timeout=5.0)
        
        if detection.detected:
            print(f"   🎉 WAKE WORD DETECTED!")
            print(f"   Text: \"{detection.text}\"")
            print(f"   Confidence: {detection.confidence:.2f}")
            print(f"   ✅ WAKE WORD DETECTION WORKS WITH SYNC INITIALIZATION!")
            return True
        else:
            if detection.text:
                print(f"   🔊 Audio captured: \"{detection.text}\"")
                print(f"   ❌ Not wake word, but audio system is working")
            else:
                print(f"   ❌ No audio detected")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_async_initialization():
    """Test wake word detection using new async initialization."""
    print("\n🔍 TESTING WAKE WORD WITH NEW ASYNC INITIALIZATION")
    print("=" * 60)
    
    try:
        import asyncio
        from jarvis.config import get_config
        from jarvis.core.speech import SpeechManager
        from jarvis.core.wake_word import WakeWordDetector
        
        async def async_init_test():
            print("1. 📋 Loading configuration...")
            config = get_config()
            print(f"   ✅ Config loaded: mic={config.audio.mic_name}, threshold={config.audio.energy_threshold}")
            
            print("2. 🔊 Initializing speech manager (in async context)...")
            speech_manager = SpeechManager(config.audio)
            speech_manager.initialize()
            print("   ✅ Speech manager initialized")
            
            print("3. 👂 Initializing wake word detector (in async context)...")
            wake_word_detector = WakeWordDetector(config.conversation, speech_manager)
            print("   ✅ Wake word detector initialized")
            
            print("4. 🎙️  Testing wake word detection (say 'jarvis' in 5 seconds)...")
            # Run the blocking listen_once in a thread to avoid blocking the event loop
            detection = await asyncio.to_thread(wake_word_detector.listen_once, 5.0)
            
            if detection.detected:
                print(f"   🎉 WAKE WORD DETECTED!")
                print(f"   Text: \"{detection.text}\"")
                print(f"   Confidence: {detection.confidence:.2f}")
                print(f"   ✅ WAKE WORD DETECTION WORKS WITH ASYNC INITIALIZATION!")
                return True
            else:
                if detection.text:
                    print(f"   🔊 Audio captured: \"{detection.text}\"")
                    print(f"   ❌ Not wake word, but audio system is working")
                else:
                    print(f"   ❌ No audio detected")
                return False
        
        # Run the async test
        return asyncio.run(async_init_test())
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run both sync and async tests to compare."""
    print("🧪 WAKE WORD DETECTION COMPARISON TEST")
    print("=" * 70)
    print("Testing if async initialization broke wake word detection...")
    print()
    
    # Test 1: Original synchronous initialization
    sync_works = test_original_sync_initialization()
    
    # Test 2: New async initialization
    async_works = test_async_initialization()
    
    # Results
    print("\n📊 TEST RESULTS")
    print("=" * 30)
    print(f"Synchronous initialization: {'✅ WORKS' if sync_works else '❌ FAILS'}")
    print(f"Asynchronous initialization: {'✅ WORKS' if async_works else '❌ FAILS'}")
    
    if sync_works and not async_works:
        print("\n🎯 CONCLUSION: Async initialization broke wake word detection!")
        print("💡 SOLUTION: Revert to synchronous initialization or fix async issues")
    elif not sync_works and not async_works:
        print("\n🎯 CONCLUSION: Wake word detection is broken in both modes")
        print("💡 SOLUTION: Check microphone/audio configuration")
    elif sync_works and async_works:
        print("\n🎯 CONCLUSION: Both work - issue might be elsewhere")
        print("💡 SOLUTION: Check how Jarvis is being launched")
    else:
        print("\n🎯 CONCLUSION: Only async works (unexpected)")
        print("💡 SOLUTION: Investigate further")


if __name__ == "__main__":
    main()
