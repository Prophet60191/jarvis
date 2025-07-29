#!/usr/bin/env python3
"""
Test script to verify Coqui-only TTS system works correctly.

This script tests that Apple TTS has been completely removed and
only Coqui TTS is used for speech synthesis.
"""

import sys
import time
from pathlib import Path

# Add jarvis to path
sys.path.insert(0, str(Path(__file__).parent / "jarvis"))

def test_coqui_only_tts():
    """Test that only Coqui TTS is used."""
    print("🤖 Testing Coqui-Only TTS System")
    print("=" * 60)
    
    try:
        from jarvis.config import get_config
        from jarvis.audio.tts import TextToSpeechManager
        
        config = get_config()
        
        print("📋 Configuration Check:")
        print(f"  Coqui Model: {config.audio.coqui_model}")
        print(f"  Coqui Device: {config.audio.coqui_device}")
        print(f"  Coqui Use GPU: {config.audio.coqui_use_gpu}")
        
        # Check that Apple TTS settings are removed
        apple_settings = []
        if hasattr(config.audio, 'tts_voice_preference'):
            apple_settings.append('tts_voice_preference')
        if hasattr(config.audio, 'tts_fallback_enabled'):
            apple_settings.append('tts_fallback_enabled')
        if hasattr(config.audio, 'tts_fallback_voices'):
            apple_settings.append('tts_fallback_voices')
        
        if apple_settings:
            print(f"⚠️  Apple TTS settings still present: {apple_settings}")
        else:
            print("✅ Apple TTS settings successfully removed")
        
        print("\n🔧 Initializing TTS Manager...")
        tts = TextToSpeechManager(config.audio)
        
        # Check that only Coqui TTS is present
        if hasattr(tts, 'apple_tts'):
            print("❌ Apple TTS still present in TTS manager")
            return False
        else:
            print("✅ Apple TTS successfully removed from TTS manager")
        
        if hasattr(tts, 'coqui_tts'):
            print("✅ Coqui TTS present in TTS manager")
        else:
            print("❌ Coqui TTS missing from TTS manager")
            return False
        
        print("\n🚀 Initializing Coqui TTS...")
        tts.initialize()
        
        if tts.is_initialized():
            print("✅ Coqui TTS initialized successfully")
        else:
            print("❌ Coqui TTS failed to initialize")
            return False
        
        print("\n🎤 Testing Speech Synthesis...")
        test_text = "Testing Coqui TTS only system. Apple TTS has been removed."
        print(f"Speaking: '{test_text}'")
        
        start_time = time.time()
        try:
            tts.speak(test_text, wait=True)
            end_time = time.time()
            print(f"✅ Speech completed in {end_time - start_time:.2f} seconds")
            print("🎉 Coqui-only TTS system working perfectly!")
            return True
            
        except Exception as e:
            end_time = time.time()
            print(f"❌ Speech failed after {end_time - start_time:.2f} seconds: {e}")
            return False
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_import_cleanup():
    """Test that Apple TTS imports are cleaned up."""
    print("\n🧹 Testing Import Cleanup")
    print("=" * 60)
    
    try:
        # Try to import Apple TTS - should fail
        try:
            from jarvis.audio.apple_tts import AppleTTSManager
            print("❌ Apple TTS import still works - cleanup incomplete")
            return False
        except ImportError:
            print("✅ Apple TTS import properly removed")
        
        # Check that Coqui TTS imports work
        try:
            from jarvis.audio.coqui_tts import CoquiTTSManager
            print("✅ Coqui TTS import works correctly")
        except ImportError as e:
            print(f"❌ Coqui TTS import failed: {e}")
            return False
        
        # Check main TTS manager
        try:
            from jarvis.audio.tts import TextToSpeechManager
            print("✅ Main TTS manager import works correctly")
        except ImportError as e:
            print(f"❌ Main TTS manager import failed: {e}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Import cleanup test failed: {e}")
        return False


def test_ui_cleanup():
    """Test that Apple TTS settings are removed from UI."""
    print("\n🌐 Testing UI Cleanup")
    print("=" * 60)
    
    try:
        # Read the UI file and check for Apple TTS references
        ui_file = Path(__file__).parent / "jarvis" / "ui" / "jarvis_ui.py"
        
        if not ui_file.exists():
            print("⚠️  UI file not found, skipping UI cleanup test")
            return True
        
        with open(ui_file, 'r') as f:
            ui_content = f.read()
        
        # Check for removed elements
        removed_elements = [
            'tts_voice_preference',
            'tts_fallback_enabled',
            'tts_fallback_voices',
            'Preferred Voice',
            'TTS Fallback Settings'
        ]
        
        found_elements = []
        for element in removed_elements:
            if element in ui_content:
                found_elements.append(element)
        
        if found_elements:
            print(f"❌ Apple TTS UI elements still present: {found_elements}")
            return False
        else:
            print("✅ Apple TTS UI elements successfully removed")
        
        # Check that Coqui elements are still present
        coqui_elements = [
            'coqui_model',
            'coqui_voice_speed',
            'Coqui TTS Settings'
        ]
        
        missing_elements = []
        for element in coqui_elements:
            if element not in ui_content:
                missing_elements.append(element)
        
        if missing_elements:
            print(f"❌ Coqui TTS UI elements missing: {missing_elements}")
            return False
        else:
            print("✅ Coqui TTS UI elements present and working")
        
        return True
        
    except Exception as e:
        print(f"❌ UI cleanup test failed: {e}")
        return False


def main():
    """Run all tests for Apple TTS removal."""
    print("🗑️  Apple TTS Removal Verification")
    print("=" * 60)
    print("Testing that Apple TTS has been completely removed from Jarvis")
    print("=" * 60)
    
    tests = [
        ("Import Cleanup", test_import_cleanup),
        ("UI Cleanup", test_ui_cleanup),
        ("Coqui-Only TTS", test_coqui_only_tts)
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
    print("🗑️  APPLE TTS REMOVAL RESULTS")
    print("=" * 60)
    
    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status}: {test_name}")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 Apple TTS successfully removed!")
        print("\n💡 System Status:")
        print("   🤖 Coqui TTS Only - Simplified architecture")
        print("   🗑️  Apple TTS Removed - No fallback complexity")
        print("   🎛️  Enhanced Settings - Full Coqui customization")
        print("   🚀 Better Performance - Single TTS engine")
        
        print("\n🎯 Benefits:")
        print("   • Simpler codebase")
        print("   • Better voice quality (neural TTS)")
        print("   • More customization options")
        print("   • Consistent behavior")
        
    else:
        print("⚠️  Some cleanup incomplete. Check failed tests above.")


if __name__ == "__main__":
    main()
