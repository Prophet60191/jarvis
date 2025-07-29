#!/usr/bin/env python3
"""
Test script to verify wake word detection is working.
"""

import sys
import os
import asyncio
import time

# Add the jarvis module to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'jarvis'))

from jarvis.config import get_config
from jarvis.core.speech import SpeechManager
from jarvis.core.wake_word import WakeWordDetector

async def test_wake_word_detection():
    """Test wake word detection in isolation."""
    print("🧪 Testing Wake Word Detection...")
    
    try:
        # Load configuration
        config = get_config()
        
        # Initialize speech manager
        print("🎤 Initializing speech manager...")
        speech_manager = SpeechManager(config.audio)
        
        # Initialize wake word detector
        print("👂 Initializing wake word detector...")
        wake_word_detector = WakeWordDetector(config.conversation, speech_manager)
        
        print(f"🔍 Listening for wake word: '{config.conversation.wake_word}'")
        print("💬 Say 'jarvis' clearly...")
        
        # Test wake word detection
        for i in range(5):
            print(f"\n🔄 Attempt {i+1}/5 - Listening...")
            
            detection = wake_word_detector.listen_once(timeout=3.0)
            
            print(f"📊 Result:")
            print(f"   Detected: {detection.detected}")
            print(f"   Confidence: {detection.confidence:.2f}")
            print(f"   Text: '{detection.text}'")
            print(f"   Method: {detection.detection_method}")
            
            if detection.detected:
                print("✅ Wake word detected successfully!")
                return True
            else:
                print("❌ No wake word detected")
                
            time.sleep(0.5)
        
        print("\n❌ Wake word detection test failed - no detection in 5 attempts")
        return False
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Starting Wake Word Detection Test")
    result = asyncio.run(test_wake_word_detection())
    
    if result:
        print("\n🎉 Wake word detection is working!")
        sys.exit(0)
    else:
        print("\n💥 Wake word detection is not working!")
        sys.exit(1)
