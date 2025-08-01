#!/usr/bin/env python3
"""
Test script to verify voice profile changes work properly.

This script tests:
1. Initial voice setup
2. Voice change via configuration
3. TTS reinitialization
4. Actual voice change verification
"""

import sys
import time
import os
from pathlib import Path

# Add jarvis to path
sys.path.insert(0, str(Path(__file__).parent / "jarvis"))

def test_initial_voice():
    """Test the initial voice setup."""
    print("🎤 Testing Initial Voice Setup")
    print("=" * 60)
    
    try:
        from jarvis.config import get_config
        from jarvis.audio.tts import TextToSpeechManager
        
        config = get_config()
        
        print(f"Initial voice preset: {config.audio.coqui_voice_preset}")
        
        # Initialize TTS
        tts = TextToSpeechManager(config.audio)
        tts.initialize()
        
        if tts.is_initialized():
            print("✅ TTS initialized successfully")
            
            # Get current voice info
            if hasattr(tts.coqui_tts, 'current_voice_info'):
                voice_info = tts.coqui_tts.current_voice_info
                print(f"Current voice: {voice_info.get('name', 'Unknown')}")
                print(f"Gender: {voice_info.get('gender', 'Unknown')}")
            
            return tts, config
        else:
            print("❌ TTS failed to initialize")
            return None, None
        
    except Exception as e:
        print(f"❌ Initial voice test failed: {e}")
        import traceback
        traceback.print_exc()
        return None, None


def test_voice_change(tts, config):
    """Test changing voice configuration."""
    print("\n🔄 Testing Voice Change")
    print("=" * 60)
    
    try:
        # Get current voice
        current_preset = config.audio.coqui_voice_preset
        print(f"Current preset: {current_preset}")
        
        # Change to a different voice
        if "ljspeech" in current_preset:
            new_preset = "ljspeech_glow"  # Change to different LJSpeech model
            print(f"Changing to: {new_preset} (different LJSpeech model)")
        else:
            new_preset = "ljspeech_tacotron2"  # Change to LJSpeech
            print(f"Changing to: {new_preset} (LJSpeech model)")
        
        # Update configuration
        config.audio.coqui_voice_preset = new_preset
        
        # Test if TTS manager has update_config method
        if hasattr(tts, 'update_config'):
            print("✅ TTS manager has update_config method")
            tts.update_config(config.audio)
        else:
            print("❌ TTS manager missing update_config method")
            return False
        
        # Check if voice actually changed
        if hasattr(tts.coqui_tts, 'current_voice_info'):
            voice_info = tts.coqui_tts.current_voice_info
            print(f"New voice: {voice_info.get('name', 'Unknown')}")
            print(f"Gender: {voice_info.get('gender', 'Unknown')}")
        
        # Test speech with new voice
        test_text = "Testing voice change - this should sound different now."
        print(f"Testing speech: '{test_text}'")
        
        tts.speak(test_text, wait=True)
        print("✅ Voice change test completed")
        
        return True
        
    except Exception as e:
        print(f"❌ Voice change test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_config_notification():
    """Test configuration change notification system."""
    print("\n📢 Testing Configuration Notification System")
    print("=" * 60)
    
    try:
        from jarvis.config import get_config_notifier, ConfigSection
        
        notifier = get_config_notifier()
        
        # Test callback registration
        callback_called = False
        
        def test_callback(old_config, new_config):
            nonlocal callback_called
            callback_called = True
            print(f"✅ Config change callback triggered!")
            print(f"   Old voice preset: {getattr(old_config.audio, 'coqui_voice_preset', 'Unknown')}")
            print(f"   New voice preset: {getattr(new_config.audio, 'coqui_voice_preset', 'Unknown')}")
        
        # Register callback
        notifier.register_callback(ConfigSection.AUDIO, test_callback)
        print("✅ Registered config change callback")
        
        # Trigger a config change
        from jarvis.config import trigger_config_reload
        print("Triggering config reload...")
        trigger_config_reload()
        
        # Check if callback was called
        time.sleep(0.1)  # Give callback time to execute
        
        if callback_called:
            print("✅ Configuration notification system working")
            return True
        else:
            print("❌ Configuration notification system not working")
            return False
        
    except Exception as e:
        print(f"❌ Config notification test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_environment_variable_change():
    """Test voice change via environment variable."""
    print("\n🌍 Testing Environment Variable Voice Change")
    print("=" * 60)
    
    try:
        # Set environment variable for voice change
        os.environ["JARVIS_COQUI_VOICE_PRESET"] = "ljspeech_glow"
        print("Set JARVIS_COQUI_VOICE_PRESET=ljspeech_glow")
        
        # Clear cached config and reload
        import jarvis.config
        jarvis.config._config = None
        
        from jarvis.config import get_config
        config = get_config()
        
        print(f"New voice preset from env: {config.audio.coqui_voice_preset}")
        
        if config.audio.coqui_voice_preset == "ljspeech_glow":
            print("✅ Environment variable voice change working")
            return True
        else:
            print("❌ Environment variable voice change not working")
            return False
        
    except Exception as e:
        print(f"❌ Environment variable test failed: {e}")
        return False
    finally:
        # Clean up environment variable
        if "JARVIS_COQUI_VOICE_PRESET" in os.environ:
            del os.environ["JARVIS_COQUI_VOICE_PRESET"]


def provide_voice_change_solution():
    """Provide solution for voice change issues."""
    print("\n💡 Voice Change Solution")
    print("=" * 60)
    
    print("🔧 To fix voice profile changes:")
    print("   1. TTS manager needs update_config method")
    print("   2. TTS manager should subscribe to config notifications")
    print("   3. Voice change should trigger TTS reinitialization")
    print("   4. UI should trigger config reload after saving")
    
    print("\n🎯 Current Issues:")
    print("   • TTS engine loads once and never updates")
    print("   • Voice preset changes don't trigger reinitialization")
    print("   • Configuration notifications may not reach TTS")
    
    print("\n🚀 Quick Fix:")
    print("   1. Add update_config method to TTS manager")
    print("   2. Register TTS for config change notifications")
    print("   3. Reinitialize TTS when voice preset changes")
    
    print("\n🎤 Workaround:")
    print("   1. Change voice in settings")
    print("   2. Click 'Reload Configuration' button")
    print("   3. Or restart Jarvis completely")


def main():
    """Run voice change tests."""
    print("🔄 Voice Profile Change Test Suite")
    print("=" * 60)
    print("Testing voice profile change functionality")
    print("=" * 60)
    
    tests = [
        ("Initial Voice Setup", lambda: test_initial_voice()),
        ("Configuration Notification", test_config_notification),
        ("Environment Variable Change", test_environment_variable_change),
    ]
    
    results = []
    tts = None
    config = None
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if test_name == "Initial Voice Setup":
                tts, config = test_func()
                success = tts is not None and config is not None
            else:
                success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Test voice change if we have TTS
    if tts and config:
        print(f"\n{'='*20} Voice Change Test {'='*20}")
        try:
            success = test_voice_change(tts, config)
            results.append(("Voice Change Test", success))
        except Exception as e:
            print(f"❌ Voice Change Test crashed: {e}")
            results.append(("Voice Change Test", False))
    
    # Summary
    print(f"\n{'='*60}")
    print("🔄 VOICE CHANGE TEST RESULTS")
    print("=" * 60)
    
    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status}: {test_name}")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed < total:
        provide_voice_change_solution()
    else:
        print("🎉 All voice change tests passed!")


if __name__ == "__main__":
    main()
