#!/usr/bin/env python3
"""
Simple wake word test without RAG system
"""

import sys
import logging
import time
sys.path.append('jarvis')

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from jarvis.config import get_config
from jarvis.core.wake_word import WakeWordDetector, WakeWordDetection
from jarvis.core.speech import SpeechManager

def test_simple_wake_word():
    """Test wake word detection without complex initialization"""
    print("🎯 SIMPLE WAKE WORD TEST")
    print("=" * 40)
    
    try:
        # Initialize components
        config = get_config()
        config.audio.mic_index = 0  # Force correct microphone
        
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
        
        # Test wake word detection directly
        print("\n🎤 Testing wake word detection (5 seconds)...")
        print("Say 'jarvis' now!")
        
        detection = wake_word_detector.listen_once(timeout=5.0)
        
        print(f"\n📊 RESULTS:")
        print(f"   Detected: {detection.detected}")
        print(f"   Text: '{detection.text}'")
        print(f"   Confidence: {detection.confidence:.2f}")
        print(f"   Method: {detection.detection_method}")
        print(f"   Timestamp: {detection.timestamp}")
        
        if detection.detected:
            print("\n🎉 SUCCESS: Wake word detected!")
            print("🔊 Testing TTS response...")
            speech_manager.speak_text("Wake word detection successful!")
        else:
            print("\n❌ Wake word not detected")
            if detection.text:
                print(f"   But heard: '{detection.text}'")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_simple_wake_word()
