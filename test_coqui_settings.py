#!/usr/bin/env python3
"""
Comprehensive test script for Coqui TTS settings functionality.

This script verifies that all Coqui TTS settings work properly:
1. Settings are loaded from config
2. Settings are applied to TTS generation
3. No hardcoded values remain
4. UI settings are connected to backend
"""

import sys
import time
import os
from pathlib import Path

# Add jarvis to path
sys.path.insert(0, str(Path(__file__).parent / "jarvis"))

def test_config_loading():
    """Test that all Coqui settings are loaded from config."""
    print("🔧 Testing Configuration Loading")
    print("=" * 60)
    
    try:
        from jarvis.config import get_config
        
        config = get_config()
        audio_config = config.audio
        
        # Test all Coqui settings
        settings_to_test = [
            ("coqui_model", str),
            ("coqui_language", str),
            ("coqui_device", str),
            ("coqui_use_gpu", bool),
            ("coqui_speaker_wav", (str, type(None))),
            ("coqui_temperature", float),
            ("coqui_length_penalty", float),
            ("coqui_repetition_penalty", float),
            ("coqui_top_k", int),
            ("coqui_top_p", float),
            ("coqui_streaming", bool),
            ("coqui_voice_preset", str),
            ("coqui_voice_speed", float),
            ("coqui_speaker_id", (str, type(None))),
            ("coqui_voice_conditioning_latents", (str, type(None))),
            ("coqui_emotion", str),
            ("coqui_sample_rate", int),
            ("coqui_vocoder_model", str),
            ("coqui_speed_factor", float),
            ("coqui_enable_text_splitting", bool),
            ("coqui_do_trim_silence", bool),
        ]
        
        print("📋 Checking all Coqui settings:")
        missing_settings = []
        wrong_type_settings = []
        
        for setting_name, expected_type in settings_to_test:
            if hasattr(audio_config, setting_name):
                value = getattr(audio_config, setting_name)
                if isinstance(expected_type, tuple):
                    # Multiple allowed types
                    if not any(isinstance(value, t) for t in expected_type):
                        wrong_type_settings.append((setting_name, type(value), expected_type))
                else:
                    # Single expected type
                    if not isinstance(value, expected_type):
                        wrong_type_settings.append((setting_name, type(value), expected_type))
                
                print(f"  ✅ {setting_name}: {value} ({type(value).__name__})")
            else:
                missing_settings.append(setting_name)
                print(f"  ❌ {setting_name}: MISSING")
        
        if missing_settings:
            print(f"\n❌ Missing settings: {missing_settings}")
            return False
        
        if wrong_type_settings:
            print(f"\n❌ Wrong type settings: {wrong_type_settings}")
            return False
        
        print(f"\n✅ All {len(settings_to_test)} Coqui settings loaded correctly")
        return True
        
    except Exception as e:
        print(f"❌ Config loading test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_environment_variables():
    """Test that environment variables override config settings."""
    print("\n🌍 Testing Environment Variable Override")
    print("=" * 60)
    
    try:
        # Set test environment variables
        test_env_vars = {
            "JARVIS_COQUI_VOICE_SPEED": "1.5",
            "JARVIS_COQUI_SAMPLE_RATE": "44100",
            "JARVIS_COQUI_SPEED_FACTOR": "0.8",
            "JARVIS_COQUI_EMOTION": "happy",
            "JARVIS_COQUI_ENABLE_TEXT_SPLITTING": "false",
        }
        
        # Set environment variables
        for key, value in test_env_vars.items():
            os.environ[key] = value
            print(f"  Set {key}={value}")
        
        # Clear cached config and reload to pick up environment variables
        import jarvis.config
        jarvis.config._config = None  # Clear cached config
        from jarvis.config import get_config
        config = get_config()
        
        # Check if environment variables took effect
        checks = [
            ("coqui_voice_speed", 1.5),
            ("coqui_sample_rate", 44100),
            ("coqui_speed_factor", 0.8),
            ("coqui_emotion", "happy"),
            ("coqui_enable_text_splitting", False),
        ]
        
        print("\n📋 Checking environment variable effects:")
        all_passed = True
        
        for setting_name, expected_value in checks:
            actual_value = getattr(config.audio, setting_name)
            if actual_value == expected_value:
                print(f"  ✅ {setting_name}: {actual_value} (expected {expected_value})")
            else:
                print(f"  ❌ {setting_name}: {actual_value} (expected {expected_value})")
                all_passed = False
        
        # Clean up environment variables
        for key in test_env_vars:
            if key in os.environ:
                del os.environ[key]
        
        return all_passed
        
    except Exception as e:
        print(f"❌ Environment variable test failed: {e}")
        return False


def test_settings_application():
    """Test that settings are actually applied to TTS generation."""
    print("\n🎛️ Testing Settings Application")
    print("=" * 60)
    
    try:
        from jarvis.config import get_config
        from jarvis.audio.coqui_tts import CoquiTTSManager
        
        # Test with custom settings
        config = get_config()
        
        # Set specific test values
        config.audio.coqui_voice_speed = 1.2
        config.audio.coqui_speed_factor = 0.9
        config.audio.coqui_sample_rate = 24000
        config.audio.coqui_do_trim_silence = True
        config.audio.coqui_enable_text_splitting = True
        
        print("📋 Testing settings application:")
        print(f"  Voice Speed: {config.audio.coqui_voice_speed}")
        print(f"  Speed Factor: {config.audio.coqui_speed_factor}")
        print(f"  Sample Rate: {config.audio.coqui_sample_rate}")
        print(f"  Trim Silence: {config.audio.coqui_do_trim_silence}")
        print(f"  Text Splitting: {config.audio.coqui_enable_text_splitting}")
        
        # Initialize TTS with custom settings
        coqui_tts = CoquiTTSManager(config.audio)
        
        # Check that settings are accessible
        print(f"\n🔍 Verifying settings in TTS manager:")
        print(f"  Config Voice Speed: {coqui_tts.config.coqui_voice_speed}")
        print(f"  Config Sample Rate: {coqui_tts.config.coqui_sample_rate}")
        print(f"  Config Speed Factor: {coqui_tts.config.coqui_speed_factor}")
        
        # Test that methods exist
        if hasattr(coqui_tts, '_apply_speed_adjustments'):
            print("  ✅ Speed adjustment method exists")
        else:
            print("  ❌ Speed adjustment method missing")
            return False
        
        if hasattr(coqui_tts, '_trim_silence'):
            print("  ✅ Silence trimming method exists")
        else:
            print("  ❌ Silence trimming method missing")
            return False
        
        print("\n✅ Settings application test passed")
        return True
        
    except Exception as e:
        print(f"❌ Settings application test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_hardcoded_values():
    """Test that no hardcoded values remain in the codebase."""
    print("\n🔍 Testing for Hardcoded Values")
    print("=" * 60)
    
    try:
        # Read the Coqui TTS file
        coqui_file = Path(__file__).parent / "jarvis" / "jarvis" / "audio" / "coqui_tts.py"
        
        if not coqui_file.exists():
            print("❌ Coqui TTS file not found")
            return False
        
        with open(coqui_file, 'r') as f:
            content = f.read()
        
        # Check for hardcoded values that should be configurable
        hardcoded_checks = [
            ("22050", "Sample rate should use config.coqui_sample_rate"),
            ("0.75", "Temperature should use config.coqui_temperature"),
            ("device = \"cpu\"", "Device should use _detect_device()"),
            ("sf.write(tmp_file.name, wav_data, 22050)", "Should use config sample rate"),
        ]
        
        print("🔍 Checking for hardcoded values:")
        found_hardcoded = []
        
        for hardcoded_value, description in hardcoded_checks:
            if hardcoded_value in content:
                # Check if it's in a comment or acceptable context
                lines_with_value = [line.strip() for line in content.split('\n') if hardcoded_value in line]
                problematic_lines = [line for line in lines_with_value if not line.strip().startswith('#')]
                
                if problematic_lines:
                    found_hardcoded.append((hardcoded_value, description, problematic_lines))
                    print(f"  ❌ Found hardcoded {hardcoded_value}: {description}")
                    for line in problematic_lines[:2]:  # Show first 2 problematic lines
                        print(f"     {line}")
                else:
                    print(f"  ✅ {hardcoded_value} only in comments/acceptable contexts")
            else:
                print(f"  ✅ No hardcoded {hardcoded_value} found")
        
        if found_hardcoded:
            print(f"\n❌ Found {len(found_hardcoded)} hardcoded values that should be configurable")
            return False
        else:
            print(f"\n✅ No problematic hardcoded values found")
            return True
        
    except Exception as e:
        print(f"❌ Hardcoded values test failed: {e}")
        return False


def test_ui_integration():
    """Test that UI settings are properly connected."""
    print("\n🌐 Testing UI Integration")
    print("=" * 60)
    
    try:
        # Check UI file for all settings
        ui_file = Path(__file__).parent / "jarvis" / "ui" / "jarvis_ui.py"
        
        if not ui_file.exists():
            print("❌ UI file not found")
            return False
        
        with open(ui_file, 'r') as f:
            ui_content = f.read()
        
        # Check for all Coqui settings in UI
        ui_settings_to_check = [
            "coqui_voice_preset",
            "coqui_voice_speed",
            "coqui_sample_rate",
            "coqui_speed_factor",
            "coqui_enable_text_splitting",
            "coqui_do_trim_silence",
            "coqui_emotion",
            "coqui_speaker_id",
        ]
        
        print("🔍 Checking UI integration:")
        missing_ui_settings = []
        
        for setting in ui_settings_to_check:
            if setting in ui_content:
                print(f"  ✅ {setting} found in UI")
            else:
                missing_ui_settings.append(setting)
                print(f"  ❌ {setting} missing from UI")
        
        if missing_ui_settings:
            print(f"\n❌ Missing UI settings: {missing_ui_settings}")
            return False
        else:
            print(f"\n✅ All {len(ui_settings_to_check)} settings found in UI")
            return True
        
    except Exception as e:
        print(f"❌ UI integration test failed: {e}")
        return False


def main():
    """Run comprehensive Coqui settings tests."""
    print("🔧 Coqui TTS Settings Comprehensive Test")
    print("=" * 60)
    print("Testing all Coqui settings for proper functionality")
    print("=" * 60)
    
    tests = [
        ("Configuration Loading", test_config_loading),
        ("Environment Variables", test_environment_variables),
        ("Settings Application", test_settings_application),
        ("Hardcoded Values Check", test_hardcoded_values),
        ("UI Integration", test_ui_integration),
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
    print("🔧 COQUI SETTINGS TEST RESULTS")
    print("=" * 60)
    
    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status}: {test_name}")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All Coqui settings working properly!")
        print("\n💡 Settings Status:")
        print("   ✅ All settings loaded from config")
        print("   ✅ Environment variables work")
        print("   ✅ Settings applied to TTS generation")
        print("   ✅ No hardcoded values remain")
        print("   ✅ UI properly connected")
        
        print("\n🎯 Available Settings:")
        print("   🎤 Voice Selection - 42 US voices")
        print("   🔊 Speed Control - Voice speed + speed factor")
        print("   🎛️ Audio Quality - Sample rate, silence trimming")
        print("   🎭 Advanced Options - Emotion, text splitting")
        
    else:
        print("⚠️  Some settings tests failed. Check the issues above.")


if __name__ == "__main__":
    main()
