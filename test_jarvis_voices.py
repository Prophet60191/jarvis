#!/usr/bin/env python3
"""
Test script to demo different Jarvis voices.

This script lets you test various voice options available in Jarvis.
"""

import sys
import time
from pathlib import Path

# Add jarvis to path
sys.path.insert(0, str(Path(__file__).parent / "jarvis"))

def test_system_voices():
    """Test Apple system voices (fallback TTS)."""
    print("🎤 Testing Apple System Voices")
    print("=" * 50)
    
    try:
        from jarvis.config import get_config
        from jarvis.audio.apple_tts import AppleTTSManager
        
        config = get_config()
        
        # Available system voices
        voices = [
            ("Daniel", "British Male"),
            ("Alex", "US Male"), 
            ("Victoria", "US Female"),
            ("Samantha", "US Female"),
            ("Karen", "Australian Female")
        ]
        
        test_text = "Hello, I am Jarvis with a different voice."
        
        for voice_name, description in voices:
            print(f"\n🔊 Testing {voice_name} ({description})")
            
            try:
                # Create TTS with specific voice
                config.audio.tts_voice_preference = voice_name
                tts = AppleTTSManager(config.audio)
                tts.initialize()
                
                print(f"Speaking: '{test_text}'")
                tts.speak(test_text, wait=True)
                
                print("✅ Voice test completed")
                time.sleep(1)
                
            except Exception as e:
                print(f"❌ Failed to test {voice_name}: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ System voice test failed: {e}")
        return False


def test_coqui_models():
    """Test different Coqui TTS models."""
    print("\n🤖 Testing Coqui TTS Models")
    print("=" * 50)
    
    try:
        from jarvis.config import get_config
        from jarvis.audio.coqui_tts import CoquiTTSManager
        
        config = get_config()
        
        # Available Coqui models
        models = [
            ("tts_models/en/ljspeech/tacotron2-DDC", "LJSpeech Tacotron2 (Female)"),
            ("tts_models/en/ljspeech/fast_pitch", "FastPitch (Female, Fast)"),
            ("tts_models/en/ljspeech/glow-tts", "Glow-TTS (Female, High Quality)")
        ]
        
        test_text = "This is Jarvis using advanced neural text to speech."
        
        for model_name, description in models:
            print(f"\n🔊 Testing {description}")
            print(f"Model: {model_name}")
            
            try:
                # Force CPU mode for stability
                config.audio.coqui_model = model_name
                config.audio.coqui_device = "cpu"
                config.audio.coqui_use_gpu = False
                
                coqui = CoquiTTSManager(config.audio)
                coqui.initialize()
                
                print(f"Speaking: '{test_text}'")
                coqui.speak(test_text, wait=True)
                
                print("✅ Coqui model test completed")
                time.sleep(1)
                
            except Exception as e:
                print(f"❌ Failed to test {model_name}: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Coqui model test failed: {e}")
        return False


def test_multi_speaker():
    """Test multi-speaker VCTK model."""
    print("\n👥 Testing Multi-Speaker Voices (VCTK)")
    print("=" * 50)
    
    try:
        from jarvis.config import get_config
        from jarvis.audio.coqui_tts import CoquiTTSManager
        
        config = get_config()
        
        # VCTK speakers (sample)
        speakers = [
            ("p225", "Female, English"),
            ("p226", "Male, English"), 
            ("p227", "Male, English"),
            ("p228", "Female, English"),
            ("p229", "Female, English")
        ]
        
        test_text = "Hello, I am speaker {} from the VCTK dataset."
        
        print("Note: Multi-speaker models require specific setup.")
        print("This is a demonstration of available speaker IDs.")
        
        for speaker_id, description in speakers:
            print(f"\n🔊 Speaker {speaker_id} ({description})")
            print(f"Would speak: '{test_text.format(speaker_id)}'")
            
            # Note: Actual implementation would require:
            # config.audio.coqui_model = "tts_models/en/vctk/vits"
            # config.audio.coqui_speaker_id = speaker_id
            # But this requires more complex setup
        
        print("\n💡 To use multi-speaker voices:")
        print("   1. Set model to 'tts_models/en/vctk/vits' in settings")
        print("   2. Set Speaker ID to desired speaker (p225, p226, etc.)")
        print("   3. Save configuration and restart Jarvis")
        
        return True
        
    except Exception as e:
        print(f"❌ Multi-speaker test failed: {e}")
        return False


def show_voice_options():
    """Show all available voice options."""
    print("\n📋 Complete Jarvis Voice Options")
    print("=" * 50)
    
    print("🎤 SYSTEM VOICES (Always Available):")
    print("   • Daniel (British Male) - Default")
    print("   • Alex (US Male)")
    print("   • Victoria (US Female)")
    print("   • Samantha (US Female)")
    print("   • Karen (Australian Female)")
    
    print("\n🤖 COQUI NEURAL VOICES:")
    print("   • LJSpeech Tacotron2 (Female, High Quality)")
    print("   • FastPitch (Female, Very Fast)")
    print("   • Glow-TTS (Female, Premium Quality)")
    
    print("\n👥 MULTI-SPEAKER VOICES (109 Available):")
    print("   • VCTK Dataset: p225-p376")
    print("   • Various accents: British, American, Scottish")
    print("   • Male and female speakers")
    
    print("\n🎭 VOICE CLONING (Advanced):")
    print("   • Clone any voice with 3-10 second audio sample")
    print("   • 49 languages supported")
    print("   • Emotional control available")
    
    print("\n🔧 HOW TO CHANGE:")
    print("   1. Web UI: http://localhost:8080/audio")
    print("   2. Change 'Preferred Voice' or 'TTS Model'")
    print("   3. Save settings")


def main():
    """Demo Jarvis voice options."""
    print("🎤 Jarvis Voice Demo")
    print("=" * 50)
    print("Demonstrating different voice options available in Jarvis")
    print("=" * 50)
    
    # Show all options first
    show_voice_options()
    
    # Ask user what they want to test
    print("\n🎯 What would you like to test?")
    print("1. System Voices (Apple TTS)")
    print("2. Coqui Neural Voices") 
    print("3. Multi-Speaker Info")
    print("4. All of the above")
    
    try:
        choice = input("\nEnter choice (1-4): ").strip()
        
        if choice == "1":
            test_system_voices()
        elif choice == "2":
            test_coqui_models()
        elif choice == "3":
            test_multi_speaker()
        elif choice == "4":
            test_system_voices()
            test_coqui_models() 
            test_multi_speaker()
        else:
            print("Invalid choice. Showing voice options only.")
    
    except KeyboardInterrupt:
        print("\n\nDemo cancelled by user.")
    except Exception as e:
        print(f"\nDemo error: {e}")
    
    print("\n🎉 Voice demo complete!")
    print("💡 Use the Jarvis settings UI for easy voice switching!")


if __name__ == "__main__":
    main()
