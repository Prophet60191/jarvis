#!/usr/bin/env python3
"""
Debug script to trace exactly what happens during voice changes.
"""

import sys
import logging
from pathlib import Path

# Add jarvis to path
sys.path.insert(0, str(Path(__file__).parent / "jarvis"))

# Set up detailed logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def debug_voice_change():
    """Debug the voice change process step by step."""
    print("🔍 Debugging Voice Change Process")
    print("=" * 60)
    
    try:
        from jarvis.config import get_config
        from jarvis.audio.tts import TextToSpeechManager
        from jarvis.audio.voice_presets import get_voice_config
        
        # Step 1: Get initial configuration
        print("📋 Step 1: Initial Configuration")
        config = get_config()
        initial_preset = config.audio.coqui_voice_preset
        print(f"Initial voice preset: {initial_preset}")
        
        initial_voice_config = get_voice_config(initial_preset)
        print(f"Initial model: {initial_voice_config.get('model')}")
        print(f"Initial speaker: {initial_voice_config.get('speaker_id')}")
        print(f"Initial voice name: {initial_voice_config.get('voice_info', {}).get('name')}")
        
        # Step 2: Initialize TTS
        print(f"\n🚀 Step 2: Initialize TTS")
        tts = TextToSpeechManager(config.audio)
        tts.initialize()
        
        if hasattr(tts.coqui_tts, 'current_voice_info'):
            current_voice = tts.coqui_tts.current_voice_info
            print(f"TTS initialized with voice: {current_voice.get('name')}")
        
        # Step 3: Change voice preset
        print(f"\n🔄 Step 3: Change Voice Preset")
        new_preset = "ljspeech_tacotron2"
        print(f"Changing from '{initial_preset}' to '{new_preset}'")
        
        new_voice_config = get_voice_config(new_preset)
        print(f"New model: {new_voice_config.get('model')}")
        print(f"New speaker: {new_voice_config.get('speaker_id')}")
        print(f"New voice name: {new_voice_config.get('voice_info', {}).get('name')}")
        
        # Step 4: Update configuration
        print(f"\n⚙️ Step 4: Update Configuration")
        config.audio.coqui_voice_preset = new_preset
        
        print("Calling tts.update_config()...")
        tts.update_config(config.audio)
        
        # Step 5: Check if voice actually changed
        print(f"\n✅ Step 5: Verify Voice Change")
        if hasattr(tts.coqui_tts, 'current_voice_info'):
            updated_voice = tts.coqui_tts.current_voice_info
            print(f"TTS now has voice: {updated_voice.get('name')}")
            
            if updated_voice.get('name') != current_voice.get('name'):
                print("🎉 SUCCESS: Voice actually changed!")
                return True
            else:
                print("❌ FAILED: Voice did not change")
                return False
        else:
            print("❌ FAILED: No voice info available")
            return False
        
    except Exception as e:
        print(f"❌ Debug failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_direct_coqui_update():
    """Test updating Coqui TTS directly."""
    print("\n🎯 Testing Direct Coqui TTS Update")
    print("=" * 60)
    
    try:
        from jarvis.config import get_config
        from jarvis.audio.coqui_tts import CoquiTTSManager
        
        config = get_config()
        
        # Initialize with first voice
        print(f"Initializing with: {config.audio.coqui_voice_preset}")
        coqui_tts = CoquiTTSManager(config.audio)
        coqui_tts.initialize()
        
        if hasattr(coqui_tts, 'current_voice_info'):
            initial_voice = coqui_tts.current_voice_info
            print(f"Initial voice: {initial_voice.get('name')}")
        
        # Change configuration
        config.audio.coqui_voice_preset = "ljspeech_glow"
        print(f"Changing to: {config.audio.coqui_voice_preset}")
        
        # Update directly
        print("Calling coqui_tts.update_config()...")
        coqui_tts.update_config(config.audio)
        
        # Check result
        if hasattr(coqui_tts, 'current_voice_info'):
            updated_voice = coqui_tts.current_voice_info
            print(f"Updated voice: {updated_voice.get('name')}")
            
            if updated_voice.get('name') != initial_voice.get('name'):
                print("🎉 SUCCESS: Direct Coqui update worked!")
                return True
            else:
                print("❌ FAILED: Direct Coqui update did not work")
                return False
        
    except Exception as e:
        print(f"❌ Direct Coqui test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run voice change debugging."""
    print("🔍 Voice Change Debug Suite")
    print("=" * 60)
    
    # Test 1: Full voice change process
    success1 = debug_voice_change()
    
    # Test 2: Direct Coqui update
    success2 = test_direct_coqui_update()
    
    print(f"\n{'='*60}")
    print("🔍 DEBUG RESULTS")
    print("=" * 60)
    print(f"Full voice change process: {'✅ SUCCESS' if success1 else '❌ FAILED'}")
    print(f"Direct Coqui update: {'✅ SUCCESS' if success2 else '❌ FAILED'}")
    
    if not success1 and not success2:
        print("\n💡 The voice change system is not working properly.")
        print("   The update_config method may not be reinitializing the TTS correctly.")
    elif success2 and not success1:
        print("\n💡 Direct Coqui update works, but TTS manager update doesn't.")
        print("   The issue is in the TTS manager's update_config method.")
    elif success1:
        print("\n🎉 Voice change system is working!")


if __name__ == "__main__":
    main()
