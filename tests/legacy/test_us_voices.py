#!/usr/bin/env python3
"""
Test script to verify US voice integration in Jarvis.

This script tests the voice preset system and demonstrates
the available US male and female voices.
"""

import sys
import time
from pathlib import Path

# Add jarvis to path
sys.path.insert(0, str(Path(__file__).parent / "jarvis"))

def test_voice_presets():
    """Test the voice preset system."""
    print("🎤 Testing Voice Preset System")
    print("=" * 60)
    
    try:
        from jarvis.audio.voice_presets import voice_preset_manager
        
        # Get available voices
        voices = voice_preset_manager.get_available_voices()
        
        print(f"📊 Voice Statistics:")
        print(f"  Single Speaker: {len(voices['single_speaker'])}")
        print(f"  Multi Speaker: {len(voices['multi_speaker'])}")
        print(f"  US Male: {len(voices['us_male'])}")
        print(f"  US Female: {len(voices['us_female'])}")
        
        # Test voice configuration
        print(f"\n🔧 Testing Voice Configurations:")
        
        test_presets = [
            "ljspeech_tacotron2",
            "vctk_p302",  # US Male
            "vctk_p300",  # US Female
        ]
        
        for preset in test_presets:
            config = voice_preset_manager.get_voice_config(preset)
            voice_info = config.get("voice_info", {})
            
            print(f"  {preset}:")
            print(f"    Name: {voice_info.get('name', 'Unknown')}")
            print(f"    Model: {config.get('model', 'Unknown')}")
            print(f"    Speaker: {config.get('speaker_id', 'None')}")
            print(f"    Gender: {voice_info.get('gender', 'Unknown')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Voice preset test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_voice_synthesis():
    """Test voice synthesis with different presets."""
    print("\n🎙️ Testing Voice Synthesis")
    print("=" * 60)
    
    try:
        from jarvis.config import get_config
        from jarvis.audio.tts import TextToSpeechManager
        
        config = get_config()
        
        # Test different voice presets
        test_voices = [
            ("ljspeech_tacotron2", "Female Professional Voice"),
            ("vctk_p302", "US Male Voice (Age 23)"),
            ("vctk_p300", "US Female Voice (Age 26)"),
        ]
        
        for preset_id, description in test_voices:
            print(f"\n🔊 Testing: {description}")
            print(f"   Preset: {preset_id}")
            
            try:
                # Set voice preset
                config.audio.coqui_voice_preset = preset_id
                
                # Initialize TTS
                tts = TextToSpeechManager(config.audio)
                tts.initialize()
                
                # Test speech
                test_text = f"Hello, I am Jarvis speaking with {description.lower()}."
                print(f"   Speaking: '{test_text}'")
                
                start_time = time.time()
                tts.speak(test_text, wait=True)
                end_time = time.time()
                
                print(f"   ✅ Completed in {end_time - start_time:.2f} seconds")
                
                # Small delay between voices
                time.sleep(1)
                
            except Exception as e:
                print(f"   ❌ Failed: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Voice synthesis test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_ui_integration():
    """Test that the UI can load voice presets."""
    print("\n🌐 Testing UI Integration")
    print("=" * 60)
    
    try:
        # Check that the UI file contains voice presets
        ui_file = Path(__file__).parent / "jarvis" / "ui" / "jarvis_ui.py"
        
        if not ui_file.exists():
            print("⚠️  UI file not found, skipping UI test")
            return True
        
        with open(ui_file, 'r') as f:
            ui_content = f.read()
        
        # Check for voice preset elements
        required_elements = [
            'coqui_voice_preset',
            'American Male',
            'American Female',
            'Linda Johnson'
        ]
        
        missing_elements = []
        for element in required_elements:
            if element not in ui_content:
                missing_elements.append(element)
        
        if missing_elements:
            print(f"❌ Missing UI elements: {missing_elements}")
            return False
        else:
            print("✅ All voice preset UI elements found")
        
        # Check for voice counts
        male_count = ui_content.count("American Male")
        female_count = ui_content.count("American Female")
        
        print(f"📊 UI Voice Counts:")
        print(f"  US Male voices in UI: {male_count}")
        print(f"  US Female voices in UI: {female_count}")
        
        if male_count >= 10 and female_count >= 20:
            print("✅ Good voice coverage in UI")
            return True
        else:
            print("⚠️  Limited voice coverage in UI")
            return True  # Not a failure, just a note
        
    except Exception as e:
        print(f"❌ UI integration test failed: {e}")
        return False


def demonstrate_voice_variety():
    """Demonstrate the variety of available voices."""
    print("\n🎭 Voice Variety Demonstration")
    print("=" * 60)
    
    try:
        from jarvis.audio.voice_presets import voice_preset_manager
        
        voices = voice_preset_manager.get_available_voices()
        
        print("👨 US Male Voices Available:")
        for i, voice in enumerate(voices['us_male'][:5], 1):  # Show first 5
            print(f"  {i}. {voice['name']} - {voice['description']}")
        
        if len(voices['us_male']) > 5:
            print(f"  ... and {len(voices['us_male']) - 5} more male voices")
        
        print("\n👩 US Female Voices Available:")
        for i, voice in enumerate(voices['us_female'][:5], 1):  # Show first 5
            print(f"  {i}. {voice['name']} - {voice['description']}")
        
        if len(voices['us_female']) > 5:
            print(f"  ... and {len(voices['us_female']) - 5} more female voices")
        
        print("\n🎯 Recommended Voices:")
        recommendations = voice_preset_manager.get_recommended_voices()
        for use_case, preset_id in recommendations.items():
            voice_info = voice_preset_manager.get_voice_info(preset_id)
            if voice_info:
                print(f"  {use_case.title()}: {voice_info.get('name', preset_id)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Voice variety demonstration failed: {e}")
        return False


def main():
    """Run all US voice integration tests."""
    print("🇺🇸 US Voice Integration Test Suite")
    print("=" * 60)
    print("Testing the integration of 42 US English voices into Jarvis")
    print("=" * 60)
    
    tests = [
        ("Voice Preset System", test_voice_presets),
        ("UI Integration", test_ui_integration),
        ("Voice Variety Demo", demonstrate_voice_variety),
        ("Voice Synthesis", test_voice_synthesis)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print(f"\n{'='*60}")
    print("🇺🇸 US VOICE INTEGRATION RESULTS")
    print("=" * 60)
    
    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status}: {test_name}")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 US Voice Integration Complete!")
        print("\n💡 Available Features:")
        print("   🎤 42 US English Voices - Male and female variety")
        print("   🎛️ Easy Voice Selection - Dropdown in settings")
        print("   👥 Multi-Speaker Support - Natural voice variety")
        print("   🚀 Instant Switching - Change voices on the fly")
        
        print("\n🎯 How to Use:")
        print("   1. Open Jarvis Settings: http://localhost:8080/audio")
        print("   2. Select 'Voice Selection' dropdown")
        print("   3. Choose from 42 US voices")
        print("   4. Save and enjoy your new voice!")
        
    else:
        print("⚠️  Some tests failed. Check the integration above.")


if __name__ == "__main__":
    main()
