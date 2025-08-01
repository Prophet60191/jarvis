#!/usr/bin/env python3
"""
Test the configured Coqui TTS voice
"""

import sys
from pathlib import Path

# Add jarvis to path
sys.path.insert(0, str(Path(__file__).parent / "jarvis"))

def test_coqui_voice():
    """Test the Coqui TTS voice with p374 speaker."""
    print("🎤 Testing Coqui TTS with p374 speaker...")
    
    try:
        from jarvis.config import get_config
        from jarvis.audio.coqui_tts import CoquiTTSManager
        
        # Load config
        config = get_config()
        print(f"✅ Config loaded - Speaker ID: {config.audio.coqui_speaker_id}")
        
        # Initialize Coqui TTS
        coqui_tts = CoquiTTSManager(config.audio)
        coqui_tts.initialize()
        print("✅ Coqui TTS initialized")
        
        # Test speech
        test_text = "Hello! This is your voice assistant Jarvis. How do you like this voice?"
        print(f"🗣️  Testing with text: '{test_text}'")
        
        coqui_tts.speak(test_text)
        success = True
        
        if success:
            print("✅ Voice test successful!")
            return True
        else:
            print("❌ Voice test failed")
            return False
            
    except Exception as e:
        print(f"❌ Error testing voice: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function."""
    print("🎯 JARVIS VOICE TEST")
    print("=" * 40)
    
    if test_coqui_voice():
        print("\n🎉 Voice configuration is working!")
        print("✅ Jarvis should now use the p374 voice")
    else:
        print("\n❌ Voice configuration needs adjustment")
        print("💡 Check the logs above for details")

if __name__ == "__main__":
    main()
