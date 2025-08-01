#!/usr/bin/env python3
"""
Test audio capture to see if we can hear anything
"""

import sys
import logging
sys.path.append('jarvis')

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from jarvis.config import get_config
from jarvis.audio.microphone import MicrophoneManager

def test_audio_capture():
    """Test basic audio capture"""
    print("🎤 AUDIO CAPTURE TEST")
    print("=" * 50)
    
    try:
        # Initialize components
        config = get_config()
        config.audio.mic_index = 0  # Force correct microphone
        config.audio.energy_threshold = 50  # Lower threshold for sensitivity
        config.audio.timeout = 5.0  # Longer timeout
        
        print(f"🎤 Using microphone index: {config.audio.mic_index}")
        print(f"🔊 Energy threshold: {config.audio.energy_threshold}")
        
        mic_manager = MicrophoneManager(config.audio)
        mic_manager.initialize()
        print("✅ Microphone manager ready")
        
        print("\n🎤 Say ANYTHING loudly (listening for 8 seconds)...")
        print("=" * 50)
        
        # Test basic speech recognition
        result = mic_manager.listen_for_speech(timeout=8.0, service='whisper')
        
        print(f"\n📊 RESULTS:")
        if result:
            print(f"   ✅ HEARD: '{result}'")
            print("   🎉 Audio capture is working!")
        else:
            print("   ❌ No speech detected")
            print("   🔍 Possible issues:")
            print("     - Microphone permissions")
            print("     - Audio too quiet")
            print("     - Wrong microphone selected")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_audio_capture()
