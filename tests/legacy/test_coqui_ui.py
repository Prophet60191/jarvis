#!/usr/bin/env python3
"""
Test script to verify the enhanced Coqui TTS settings are working.

This script tests the configuration loading and validates that all
the new Coqui TTS settings are properly accessible.
"""

import sys
from pathlib import Path

# Add jarvis to path
sys.path.insert(0, str(Path(__file__).parent / "jarvis"))

def test_coqui_config():
    """Test that all Coqui TTS configuration options are available."""
    print("🔧 Testing Enhanced Coqui TTS Configuration")
    print("=" * 60)
    
    try:
        from jarvis.config import get_config
        
        config = get_config()
        audio_config = config.audio
        
        print("📋 Basic Coqui TTS Settings:")
        print(f"  Model: {audio_config.coqui_model}")
        print(f"  Language: {audio_config.coqui_language}")
        print(f"  Device: {audio_config.coqui_device}")
        print(f"  Use GPU: {audio_config.coqui_use_gpu}")
        print(f"  Speaker WAV: {audio_config.coqui_speaker_wav}")
        
        print("\n🎛️ Advanced Generation Settings:")
        print(f"  Temperature: {audio_config.coqui_temperature}")
        print(f"  Length Penalty: {audio_config.coqui_length_penalty}")
        print(f"  Repetition Penalty: {audio_config.coqui_repetition_penalty}")
        print(f"  Top K: {audio_config.coqui_top_k}")
        print(f"  Top P: {audio_config.coqui_top_p}")
        print(f"  Streaming: {audio_config.coqui_streaming}")
        
        print("\n🎤 New Voice Control Settings:")
        print(f"  Voice Speed: {audio_config.coqui_voice_speed}x")
        print(f"  Speaker ID: {audio_config.coqui_speaker_id}")
        print(f"  Voice Conditioning Latents: {audio_config.coqui_voice_conditioning_latents}")
        print(f"  Emotion: {audio_config.coqui_emotion}")
        
        print("\n🔊 Audio Quality Settings:")
        print(f"  Sample Rate: {audio_config.coqui_sample_rate} Hz")
        print(f"  Vocoder Model: {audio_config.coqui_vocoder_model}")
        print(f"  Speed Factor: {audio_config.coqui_speed_factor}x")
        print(f"  Enable Text Splitting: {audio_config.coqui_enable_text_splitting}")
        print(f"  Trim Silence: {audio_config.coqui_do_trim_silence}")
        
        print("\n✅ All Coqui TTS settings loaded successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_ui_integration():
    """Test that the UI can access all the settings."""
    print("\n🌐 Testing UI Integration")
    print("=" * 60)
    
    try:
        # Test that we can import the UI module
        from jarvis.ui.jarvis_ui import JarvisUI
        
        print("✅ UI module imported successfully")
        
        # Test that the UI can be instantiated
        ui = JarvisUI()
        print("✅ UI instance created successfully")
        
        # Test that the audio config endpoint exists
        audio_content = ui.get_audio_config_content()
        
        # Check for key elements in the UI
        required_elements = [
            'coqui_voice_speed',
            'coqui_speaker_id',
            'coqui_emotion',
            'coqui_sample_rate',
            'coqui_vocoder_model',
            'coqui_speed_factor',
            'coqui_enable_text_splitting',
            'coqui_do_trim_silence'
        ]
        
        missing_elements = []
        for element in required_elements:
            if element not in audio_content:
                missing_elements.append(element)
        
        if missing_elements:
            print(f"❌ Missing UI elements: {missing_elements}")
            return False
        else:
            print("✅ All new Coqui TTS UI elements found")
            return True
        
    except Exception as e:
        print(f"❌ UI integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests for the enhanced Coqui TTS settings."""
    print("🧪 Enhanced Coqui TTS Settings Test Suite")
    print("=" * 60)
    print("Testing the new comprehensive Coqui TTS configuration system")
    print("=" * 60)
    
    tests = [
        ("Configuration Loading", test_coqui_config),
        ("UI Integration", test_ui_integration)
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
    print("🧪 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status}: {test_name}")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Enhanced Coqui TTS settings are ready!")
        print("\n💡 New Features Available:")
        print("   🎤 Voice Speed Control - Adjust speech rate")
        print("   🎭 Voice Cloning Settings - Advanced speaker control")
        print("   🎛️ Audio Quality Settings - Sample rate, vocoder selection")
        print("   🔧 Performance Settings - Text splitting, silence trimming")
        print("   🌍 Multi-Speaker Support - Speaker ID selection")
        print("   😊 Emotion Control - Emotional tone settings")
        
        print("\n🚀 Access via: http://localhost:8080/audio")
    else:
        print("⚠️  Some tests failed. Check the configuration and UI integration.")


if __name__ == "__main__":
    main()
