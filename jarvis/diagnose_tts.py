#!/usr/bin/env python3
"""
TTS Diagnostic Script

This script diagnoses text-to-speech issues to identify why
voice responses are inconsistent.
"""

import sys
import logging
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set up logging to see detailed TTS information
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_tts_initialization():
    """Test TTS system initialization."""
    print("🔧 Testing TTS Initialization")
    print("=" * 50)
    
    try:
        from jarvis.config import get_config
        from jarvis.audio.tts import TextToSpeechManager
        
        config = get_config()
        tts_manager = TextToSpeechManager(config.audio)
        
        print("✅ TTS Manager created")
        
        # Test initialization
        tts_manager.initialize()
        print("✅ TTS Manager initialized")
        
        # Check if initialized
        if tts_manager.is_initialized():
            print("✅ TTS Manager reports as initialized")
        else:
            print("❌ TTS Manager reports as NOT initialized")
            return False
        
        return tts_manager
        
    except Exception as e:
        print(f"❌ TTS Initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_apple_tts_directly():
    """Test Apple TTS directly."""
    print("\n🍎 Testing Apple TTS Directly")
    print("=" * 40)
    
    try:
        from jarvis.config import get_config
        from jarvis.audio.apple_tts import AppleTTSManager
        
        config = get_config()
        apple_tts = AppleTTSManager(config.audio)
        
        print("✅ Apple TTS Manager created")
        
        # Initialize
        apple_tts.initialize()
        print("✅ Apple TTS initialized")
        
        # Test speech
        test_text = "This is a test of Apple TTS."
        print(f"🔊 Testing speech: '{test_text}'")
        apple_tts.speak(test_text, wait=True)
        print("✅ Apple TTS speech completed")
        
        return True
        
    except Exception as e:
        print(f"❌ Apple TTS test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_speech_manager():
    """Test the full speech manager."""
    print("\n🎤 Testing Speech Manager")
    print("=" * 35)
    
    try:
        from jarvis.config import get_config
        from jarvis.core.speech import SpeechManager
        
        config = get_config()
        speech_manager = SpeechManager(config.audio)
        
        print("✅ Speech Manager created")
        
        # Initialize
        speech_manager.initialize()
        print("✅ Speech Manager initialized")
        
        # Test TTS
        test_text = "This is a test of the speech manager."
        print(f"🔊 Testing speech: '{test_text}'")
        speech_manager.speak_text(test_text, wait=True)
        print("✅ Speech Manager TTS completed")
        
        return True
        
    except Exception as e:
        print(f"❌ Speech Manager test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_conversation_tts():
    """Test TTS through the conversation system."""
    print("\n💬 Testing Conversation TTS")
    print("=" * 40)
    
    try:
        from jarvis.config import get_config
        from jarvis.core.conversation import ConversationManager
        
        config = get_config()
        conversation = ConversationManager(config.conversation, None)  # No agent needed for TTS test
        
        print("✅ Conversation Manager created")
        
        # Initialize
        conversation.initialize()
        print("✅ Conversation Manager initialized")
        
        # Test response delivery
        test_text = "This is a test of conversation TTS."
        print(f"🔊 Testing response: '{test_text}'")
        conversation.respond(test_text)
        print("✅ Conversation TTS completed")
        
        return True
        
    except Exception as e:
        print(f"❌ Conversation TTS test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_audio_devices():
    """Check available audio devices."""
    print("\n🔊 Checking Audio Devices")
    print("=" * 35)
    
    try:
        import subprocess
        
        # Check macOS audio devices
        result = subprocess.run(['system_profiler', 'SPAudioDataType'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Audio system information retrieved")
            # Look for output devices
            lines = result.stdout.split('\n')
            output_devices = []
            for line in lines:
                if 'Output' in line or 'Speaker' in line or 'Headphone' in line:
                    output_devices.append(line.strip())
            
            if output_devices:
                print("🔊 Found output devices:")
                for device in output_devices[:5]:  # Show first 5
                    print(f"   - {device}")
            else:
                print("⚠️  No obvious output devices found")
        else:
            print("⚠️  Could not retrieve audio system info")
        
        return True
        
    except Exception as e:
        print(f"❌ Audio device check failed: {e}")
        return False

def main():
    """Main diagnostic function."""
    print("🔧 Jarvis TTS Diagnostic Tool")
    print("=" * 60)
    print("This tool diagnoses text-to-speech inconsistency issues.\n")
    
    # Run all tests
    tests = [
        ("Audio Devices", check_audio_devices),
        ("TTS Initialization", test_tts_initialization),
        ("Apple TTS Direct", test_apple_tts_directly),
        ("Speech Manager", test_speech_manager),
        ("Conversation TTS", test_conversation_tts),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*60)
    print("📊 Diagnostic Summary")
    print("=" * 30)
    
    passed = 0
    for test_name, result in results:
        if result is True:
            status = "✅ PASS"
            passed += 1
        elif result is False:
            status = "❌ FAIL"
        else:
            status = "⚠️  PARTIAL"
            passed += 0.5
    
        print(f"{test_name}: {status}")
    
    print(f"\nOverall: {passed}/{len(results)} tests passed")
    
    # Recommendations
    print("\n💡 Recommendations:")
    if passed == len(results):
        print("✅ All TTS tests passed - issue may be intermittent")
        print("   - Check logs during actual voice conversations")
        print("   - Monitor for specific error patterns")
    elif passed < len(results) / 2:
        print("❌ Multiple TTS failures detected")
        print("   - Check audio device configuration")
        print("   - Verify Apple TTS permissions")
        print("   - Consider TTS backend fallbacks")
    else:
        print("⚠️  Some TTS issues detected")
        print("   - Review failed test details above")
        print("   - Check for intermittent audio device issues")
    
    return 0 if passed == len(results) else 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n🛑 Diagnostic cancelled by user")
    except Exception as e:
        print(f"\n❌ Diagnostic script error: {e}")
        sys.exit(1)
