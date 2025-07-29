#!/usr/bin/env python3
"""
Check which voice is currently being used by Jarvis.
"""

import sys
from pathlib import Path

# Add jarvis to path
sys.path.insert(0, str(Path(__file__).parent / "jarvis"))

def check_current_voice():
    """Check the current voice configuration."""
    print("🎤 Current Voice Configuration Check")
    print("=" * 60)
    
    try:
        from jarvis.config import get_config
        from jarvis.audio.voice_presets import get_voice_config
        
        config = get_config()
        
        # Get current voice preset
        current_preset = config.audio.coqui_voice_preset
        print(f"📋 Current Voice Preset: {current_preset}")
        
        # Get voice configuration details
        voice_config = get_voice_config(current_preset)
        voice_info = voice_config.get("voice_info", {})
        
        print(f"\n🎭 Voice Details:")
        print(f"   Name: {voice_info.get('name', 'Unknown')}")
        print(f"   Gender: {voice_info.get('gender', 'Unknown')}")
        print(f"   Age: {voice_info.get('age', 'Unknown')}")
        print(f"   Description: {voice_info.get('description', 'No description')}")
        
        print(f"\n🔧 Technical Details:")
        print(f"   Model: {voice_config.get('model', 'Unknown')}")
        print(f"   Speaker ID: {voice_config.get('speaker_id', 'None')}")
        
        # Check if it's a female voice
        gender = voice_info.get('gender', '').lower()
        if gender == 'female':
            print(f"\n✅ This is a FEMALE voice!")
            
            # Check which type of female voice
            model = voice_config.get('model', '')
            if 'ljspeech' in model.lower():
                print(f"   🎯 Voice Type: Linda Johnson (LJSpeech) - Single-speaker model")
                print(f"   🌟 Quality: Professional, clear female voice")
                if 'tacotron2' in model:
                    print(f"   🔬 Technology: Tacotron2 (classic neural TTS)")
                elif 'glow' in model:
                    print(f"   🔬 Technology: Glow-TTS (premium quality)")
                elif 'fastpitch' in model:
                    print(f"   🔬 Technology: FastPitch (fast synthesis)")
            elif 'vctk' in model.lower():
                speaker_id = voice_config.get('speaker_id', '')
                print(f"   🎯 Voice Type: VCTK Multi-speaker - {speaker_id}")
                print(f"   🌟 Quality: Natural American female voice")
                print(f"   🔬 Technology: VITS neural synthesis")
        else:
            print(f"\n❓ Current voice gender: {gender}")
        
        return current_preset, voice_info
        
    except Exception as e:
        print(f"❌ Error checking current voice: {e}")
        import traceback
        traceback.print_exc()
        return None, None


def list_available_female_voices():
    """List all available female voices for comparison."""
    print(f"\n👩 Available Female Voices")
    print("=" * 60)
    
    try:
        from jarvis.audio.voice_presets import voice_preset_manager
        
        voices = voice_preset_manager.get_available_voices()
        
        # Single-speaker female voices
        print("🎤 Single-Speaker Female Voices (Linda Johnson):")
        for voice in voices['single_speaker']:
            if voice['gender'].lower() == 'female':
                print(f"   • {voice['preset_id']}: {voice['name']}")
                print(f"     Description: {voice['description']}")
        
        # Multi-speaker female voices
        print(f"\n👥 Multi-Speaker Female Voices (US):")
        female_count = 0
        for voice in voices['us_female'][:5]:  # Show first 5
            print(f"   • {voice['preset_id']}: {voice['name']}")
            print(f"     Description: {voice['description']}")
            female_count += 1
        
        if len(voices['us_female']) > 5:
            print(f"   ... and {len(voices['us_female']) - 5} more female voices")
        
        print(f"\nTotal: {len(voices['single_speaker'])} single-speaker + {len(voices['us_female'])} multi-speaker female voices")
        
    except Exception as e:
        print(f"❌ Error listing female voices: {e}")


def main():
    """Check current voice and show options."""
    print("🎤 Jarvis Voice Identification")
    print("=" * 60)
    print("Identifying your current appealing female voice")
    print("=" * 60)
    
    # Check current voice
    current_preset, voice_info = check_current_voice()
    
    if current_preset and voice_info:
        gender = voice_info.get('gender', '').lower()
        if gender == 'female':
            print(f"\n🎉 IDENTIFIED: Your appealing female voice is:")
            print(f"   🎭 {voice_info.get('name', 'Unknown')}")
            print(f"   🔧 Preset ID: {current_preset}")
            print(f"   📝 {voice_info.get('description', 'No description')}")
            
            # Provide recommendation
            if 'ljspeech' in current_preset.lower():
                print(f"\n💡 Voice Analysis:")
                print(f"   ✅ This is Linda Johnson - a high-quality single-speaker voice")
                print(f"   ✅ Works without espeak-ng installation")
                print(f"   ✅ Professional, clear, and natural sounding")
                print(f"   ✅ Excellent choice for voice assistant!")
            else:
                print(f"\n💡 Voice Analysis:")
                print(f"   ✅ This is a VCTK multi-speaker voice")
                print(f"   ✅ Natural American female voice")
                print(f"   ⚠️  Requires espeak-ng to be installed")
        else:
            print(f"\n❓ Current voice is not female (gender: {gender})")
    
    # Show other female options
    list_available_female_voices()
    
    print(f"\n🎯 Voice Recommendation:")
    print(f"   If you like your current female voice, keep it!")
    print(f"   You can always change it in settings: http://localhost:8080/audio")


if __name__ == "__main__":
    main()
