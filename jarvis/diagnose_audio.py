#!/usr/bin/env python3
"""
Audio System Diagnostic Tool for Jarvis Voice Assistant

This tool diagnoses audio system issues and provides recommendations
for fixing microphone and TTS problems.
"""

import sys
import os
from pathlib import Path

# Add the jarvis package to the path
sys.path.insert(0, str(Path(__file__).parent))

from jarvis.config import get_config
from jarvis.audio.microphone import MicrophoneManager
from jarvis.core.speech import SpeechManager
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def check_pyaudio():
    """Check PyAudio installation and functionality."""
    print("🔍 Checking PyAudio...")
    try:
        import pyaudio
        print(f"✅ PyAudio version: {pyaudio.__version__}")
        
        p = pyaudio.PyAudio()
        device_count = p.get_device_count()
        print(f"✅ Found {device_count} audio devices")
        p.terminate()
        
        return True
    except ImportError:
        print("❌ PyAudio not installed. Install with: pip install pyaudio")
        return False
    except Exception as e:
        print(f"❌ PyAudio error: {e}")
        return False


def check_microphone_devices():
    """Check available microphone devices."""
    print("\n🎤 Checking microphone devices...")
    
    try:
        mics = MicrophoneManager.list_microphones()
        
        if not mics:
            print("❌ No microphone devices found")
            return False
        
        print(f"✅ Found {len(mics)} microphone devices:")
        for mic in mics:
            default_marker = " (DEFAULT)" if mic.get('is_default', False) else ""
            print(f"   {mic['index']}: {mic['name']}{default_marker}")
            print(f"      Channels: {mic.get('max_input_channels', 'Unknown')}")
            print(f"      Sample Rate: {mic.get('default_sample_rate', 'Unknown')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error checking microphones: {e}")
        return False


def check_microphone_permissions():
    """Check microphone permissions."""
    print("\n🔐 Checking microphone permissions...")
    
    try:
        has_permissions = MicrophoneManager.check_microphone_permissions()
        
        if has_permissions:
            print("✅ Microphone permissions granted")
            return True
        else:
            print("❌ Microphone permissions denied")
            print("💡 On macOS, go to System Preferences > Security & Privacy > Privacy > Microphone")
            print("   and ensure your terminal/IDE has microphone access")
            return False
            
    except Exception as e:
        print(f"❌ Error checking permissions: {e}")
        return False


def test_microphone_initialization():
    """Test microphone initialization."""
    print("\n🎤 Testing microphone initialization...")
    
    try:
        config = get_config()
        mic_manager = MicrophoneManager(config.audio)
        
        print(f"Config: mic_index={config.audio.mic_index}, mic_name='{config.audio.mic_name}'")
        
        mic_manager.initialize()
        print("✅ Microphone initialized successfully")
        
        # Test recommended microphone
        recommended = MicrophoneManager.get_recommended_microphone()
        if recommended:
            print(f"💡 Recommended microphone: {recommended['name']} (index {recommended['index']})")
        
        return True
        
    except Exception as e:
        print(f"❌ Microphone initialization failed: {e}")
        
        # Try to suggest fixes
        print("\n🔧 Suggested fixes:")
        print("1. Try a different microphone index in your .env file")
        print("2. Check microphone permissions")
        print("3. Restart your terminal/IDE")
        
        return False


def test_speech_system():
    """Test the complete speech system."""
    print("\n🗣️ Testing speech system...")
    
    try:
        config = get_config()
        speech_manager = SpeechManager(config.audio)
        
        speech_manager.initialize()
        print("✅ Speech system initialized successfully")
        
        # Test TTS
        print("🔊 Testing text-to-speech...")
        speech_manager.speak_text("Audio diagnostic test completed successfully.")
        print("✅ Text-to-speech working")
        
        return True
        
    except Exception as e:
        print(f"❌ Speech system test failed: {e}")
        return False


def main():
    """Run comprehensive audio diagnostics."""
    print("🤖 Jarvis Audio System Diagnostics")
    print("=" * 50)
    
    tests = [
        ("PyAudio Installation", check_pyaudio),
        ("Microphone Devices", check_microphone_devices),
        ("Microphone Permissions", check_microphone_permissions),
        ("Microphone Initialization", test_microphone_initialization),
        ("Speech System", test_speech_system),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n📊 Diagnostic Summary")
    print("=" * 30)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\nResults: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\n🎉 All audio system tests passed!")
        print("Your Jarvis audio system should be working correctly.")
    else:
        print(f"\n⚠️ {len(results) - passed} test(s) failed.")
        print("Please address the issues above before using Jarvis.")
    
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
