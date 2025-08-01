#!/usr/bin/env python3
"""
Direct Wake Word Test - Bypass complex main loop
"""

import sys
import logging
sys.path.append('jarvis')

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from jarvis.config import get_config
from jarvis.core.wake_word import WakeWordDetector
from jarvis.core.speech import SpeechManager

def test_direct_wake_word():
    """Test wake word detection directly"""
    print("🎤 DIRECT WAKE WORD TEST")
    print("=" * 50)
    
    try:
        # Initialize components
        config = get_config()

        # Force correct microphone index
        config.audio.mic_index = 0
        print(f"🎤 Using microphone index: {config.audio.mic_index}")

        print("📡 Initializing speech manager...")
        speech_manager = SpeechManager(config.audio)
        speech_manager.initialize()
        print("✅ Speech manager ready")
        
        print("🎯 Initializing wake word detector...")
        wake_word_detector = WakeWordDetector(
            config.conversation,
            speech_manager
        )
        print("✅ Wake word detector ready")
        
        print("\n🎤 Say 'jarvis' now (listening for 10 seconds)...")
        print("=" * 50)
        
        # Test wake word detection
        detection = wake_word_detector.listen_once(timeout=10.0)
        
        print(f"\n📊 RESULTS:")
        print(f"   Detected: {detection.detected}")
        print(f"   Text: '{detection.text}'")
        print(f"   Confidence: {detection.confidence:.2f}")
        print(f"   Method: {detection.detection_method}")
        
        if detection.detected:
            print("\n🎉 WAKE WORD DETECTED!")
            print("🔊 Testing response...")
            speech_manager.speak_text("Yes sir? Wake word detection is working!")
            print("✅ Response test complete")
        else:
            print("\n❌ Wake word not detected")
            if detection.text:
                print(f"   But heard: '{detection.text}'")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_direct_wake_word()
