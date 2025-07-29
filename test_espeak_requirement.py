#!/usr/bin/env python3
"""
Test script to check if espeak-ng is required for current voice setup.

This script tests:
1. Which voices work without espeak-ng
2. Which voices require espeak-ng
3. Current voice preset functionality
4. Recommendations for espeak-ng installation
"""

import sys
import subprocess
from pathlib import Path

# Add jarvis to path
sys.path.insert(0, str(Path(__file__).parent / "jarvis"))

def check_espeak_installation():
    """Check if espeak-ng is installed."""
    print("🔍 Checking espeak-ng Installation")
    print("=" * 60)
    
    try:
        # Check if espeak-ng is available
        result = subprocess.run(['espeak-ng', '--version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            version = result.stdout.strip().split('\n')[0]
            print(f"✅ espeak-ng is installed: {version}")
            return True
        else:
            print("❌ espeak-ng command failed")
            return False
    except FileNotFoundError:
        print("❌ espeak-ng not found in PATH")
        return False
    except subprocess.TimeoutExpired:
        print("❌ espeak-ng command timed out")
        return False
    except Exception as e:
        print(f"❌ Error checking espeak-ng: {e}")
        return False


def test_voice_types():
    """Test different voice types to see which work without espeak-ng."""
    print("\n🎤 Testing Voice Types")
    print("=" * 60)
    
    try:
        from jarvis.config import get_config
        from jarvis.audio.voice_presets import voice_preset_manager
        
        config = get_config()
        
        # Get available voices
        voices = voice_preset_manager.get_available_voices()
        
        print("📊 Voice Type Analysis:")
        print(f"  Single Speaker Models: {len(voices['single_speaker'])}")
        print(f"  Multi-Speaker Models: {len(voices['multi_speaker'])}")
        print(f"  US Male Voices: {len(voices['us_male'])}")
        print(f"  US Female Voices: {len(voices['us_female'])}")
        
        # Test single-speaker models (should work without espeak-ng)
        print(f"\n✅ Single-Speaker Models (No espeak-ng required):")
        for voice in voices['single_speaker']:
            print(f"  • {voice['name']} - {voice['description']}")
        
        # Multi-speaker models (may require espeak-ng)
        print(f"\n⚠️  Multi-Speaker Models (May require espeak-ng):")
        for i, voice in enumerate(voices['us_male'][:3], 1):  # Show first 3
            print(f"  • {voice['name']} - {voice['description']}")
        
        if len(voices['us_male']) > 3:
            print(f"  ... and {len(voices['us_male']) - 3} more male voices")
        
        for i, voice in enumerate(voices['us_female'][:3], 1):  # Show first 3
            print(f"  • {voice['name']} - {voice['description']}")
        
        if len(voices['us_female']) > 3:
            print(f"  ... and {len(voices['us_female']) - 3} more female voices")
        
        return True
        
    except Exception as e:
        print(f"❌ Voice type test failed: {e}")
        return False


def test_current_voice():
    """Test the current voice configuration."""
    print("\n🎯 Testing Current Voice Configuration")
    print("=" * 60)
    
    try:
        from jarvis.config import get_config
        from jarvis.audio.voice_presets import get_voice_config
        
        config = get_config()
        current_preset = config.audio.coqui_voice_preset
        
        print(f"Current Voice Preset: {current_preset}")
        
        # Get voice configuration
        voice_config = get_voice_config(current_preset)
        voice_info = voice_config.get("voice_info", {})
        
        print(f"Voice Name: {voice_info.get('name', 'Unknown')}")
        print(f"Model: {voice_config.get('model', 'Unknown')}")
        print(f"Speaker ID: {voice_config.get('speaker_id', 'None')}")
        print(f"Gender: {voice_info.get('gender', 'Unknown')}")
        
        # Determine if espeak-ng is needed
        model = voice_config.get("model", "")
        speaker_id = voice_config.get("speaker_id")
        
        if "vctk" in model.lower() and speaker_id:
            print("⚠️  Current voice uses VCTK multi-speaker model")
            print("   This MAY require espeak-ng for phoneme processing")
            needs_espeak = True
        elif "ljspeech" in model.lower():
            print("✅ Current voice uses LJSpeech single-speaker model")
            print("   This works WITHOUT espeak-ng")
            needs_espeak = False
        else:
            print("❓ Unknown model type - espeak-ng requirement unclear")
            needs_espeak = None
        
        return needs_espeak
        
    except Exception as e:
        print(f"❌ Current voice test failed: {e}")
        return None


def test_voice_synthesis():
    """Test actual voice synthesis to see if it works."""
    print("\n🗣️ Testing Voice Synthesis")
    print("=" * 60)
    
    try:
        from jarvis.config import get_config
        from jarvis.audio.tts import TextToSpeechManager
        
        config = get_config()
        
        print(f"Testing with current voice preset: {config.audio.coqui_voice_preset}")
        
        # Initialize TTS
        tts = TextToSpeechManager(config.audio)
        
        print("Initializing TTS engine...")
        tts.initialize()
        
        if tts.is_initialized():
            print("✅ TTS engine initialized successfully")
            
            # Test synthesis (without actually playing audio)
            test_text = "Testing voice synthesis without espeak-ng."
            print(f"Testing synthesis: '{test_text}'")
            
            # This will test if the voice works
            try:
                tts.speak(test_text, wait=True)
                print("✅ Voice synthesis successful!")
                return True
            except Exception as e:
                if "espeak" in str(e).lower() or "phoneme" in str(e).lower():
                    print(f"❌ Voice synthesis failed - espeak-ng required: {e}")
                    return False
                else:
                    print(f"❌ Voice synthesis failed - other issue: {e}")
                    return None
        else:
            print("❌ TTS engine failed to initialize")
            return False
        
    except Exception as e:
        print(f"❌ Voice synthesis test failed: {e}")
        import traceback
        traceback.print_exc()
        return None


def provide_recommendations():
    """Provide recommendations based on test results."""
    print("\n💡 Recommendations")
    print("=" * 60)
    
    espeak_installed = check_espeak_installation()
    needs_espeak = test_current_voice()
    synthesis_works = test_voice_synthesis()
    
    print("\n📋 Summary:")
    print(f"  espeak-ng installed: {'✅ Yes' if espeak_installed else '❌ No'}")
    print(f"  Current voice needs espeak-ng: {'✅ Yes' if needs_espeak else '❌ No' if needs_espeak is False else '❓ Unknown'}")
    print(f"  Voice synthesis works: {'✅ Yes' if synthesis_works else '❌ No' if synthesis_works is False else '❓ Unknown'}")
    
    print("\n🎯 Recommendations:")
    
    if synthesis_works:
        print("✅ Your current setup is working fine!")
        if not espeak_installed:
            print("💡 espeak-ng is NOT required for your current voice")
            print("   You can use single-speaker models without it")
        else:
            print("✅ espeak-ng is installed and working")
    
    elif synthesis_works is False and not espeak_installed:
        print("🔧 Install espeak-ng to enable multi-speaker voices:")
        print("   brew install espeak-ng  # macOS")
        print("   sudo apt install espeak-ng  # Ubuntu/Debian")
        print("   Or switch to single-speaker voices that don't need it")
    
    elif not espeak_installed:
        print("⚠️  espeak-ng is not installed")
        print("📌 Options:")
        print("   1. Install espeak-ng for full voice support:")
        print("      brew install espeak-ng  # macOS")
        print("   2. Use single-speaker voices only (Linda Johnson)")
        print("      - Change voice preset to 'ljspeech_tacotron2'")
        print("      - Works without espeak-ng")
    
    else:
        print("✅ espeak-ng is installed - you have full voice support!")
    
    print("\n🎤 Voice Options:")
    print("   Without espeak-ng:")
    print("     • Linda Johnson (Tacotron2) - Professional female")
    print("     • Linda Johnson (FastPitch) - Fast female")
    print("     • Linda Johnson (Glow-TTS) - Premium female")
    print("   With espeak-ng:")
    print("     • 13 US male voices (ages 18-28)")
    print("     • 29 US female voices (ages 18-26)")
    print("     • Natural voice variety")


def main():
    """Run espeak-ng requirement analysis."""
    print("🔍 espeak-ng Requirement Analysis for Jarvis")
    print("=" * 60)
    print("Checking if espeak-ng is needed for current voice setup")
    print("=" * 60)
    
    try:
        # Run all tests
        test_voice_types()
        provide_recommendations()
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
