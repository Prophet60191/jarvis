#!/usr/bin/env python3
"""
Wake Word Detection Diagnostic Tool

This tool helps diagnose wake word detection issues by testing:
1. Microphone functionality
2. Speech recognition accuracy
3. Wake word detection logic
4. Audio configuration
"""

import sys
import time
from pathlib import Path

# Add jarvis to path
sys.path.insert(0, str(Path(__file__).parent / "jarvis"))

from jarvis.config import get_config
from jarvis.core.speech import SpeechManager
from jarvis.core.wake_word import WakeWordDetector
from jarvis.audio.microphone import MicrophoneManager


def test_microphone_list():
    """Test and list available microphones."""
    print("🎤 MICROPHONE DIAGNOSTIC")
    print("=" * 40)
    
    try:
        config = get_config()
        mic_manager = MicrophoneManager(config.audio)
        
        available_mics = mic_manager.list_microphones()
        print(f"Found {len(available_mics)} microphones:")
        
        for i, mic_name in enumerate(available_mics):
            current = " ← CURRENT" if i == config.audio.mic_index else ""
            print(f"  {i}: {mic_name}{current}")
        
        print(f"\nConfigured microphone: {config.audio.mic_name}")
        print(f"Configured index: {config.audio.mic_index}")
        
        return True
        
    except Exception as e:
        print(f"❌ Microphone test failed: {e}")
        return False


def test_speech_recognition():
    """Test speech recognition functionality."""
    print("\n🔊 SPEECH RECOGNITION TEST")
    print("=" * 40)
    
    try:
        config = get_config()
        speech_manager = SpeechManager(config.audio)
        speech_manager.initialize()
        
        print("✅ Speech manager initialized")
        print(f"Audio timeout: {config.audio.timeout}s")
        print(f"Phrase time limit: {config.audio.phrase_time_limit}s")
        
        print("\n🎙️  Say something (you have 5 seconds)...")
        print("Try saying: 'jarvis', 'hello', or 'testing'")
        
        start_time = time.time()
        text = speech_manager.listen_for_speech(timeout=5.0, phrase_time_limit=10.0)
        end_time = time.time()
        
        if text:
            print(f"✅ Heard: \"{text}\"")
            print(f"⏱️  Recognition took: {end_time - start_time:.2f}s")
            return text
        else:
            print("❌ No speech detected or recognition failed")
            print("💡 Try speaking louder or closer to the microphone")
            return None
            
    except Exception as e:
        print(f"❌ Speech recognition test failed: {e}")
        return None


def test_wake_word_detection(test_text=None):
    """Test wake word detection with optional test text."""
    print("\n👂 WAKE WORD DETECTION TEST")
    print("=" * 40)
    
    try:
        config = get_config()
        speech_manager = SpeechManager(config.audio)
        speech_manager.initialize()
        wake_word_detector = WakeWordDetector(config.conversation, speech_manager)
        
        print("✅ Wake word detector initialized")
        print(f"Wake word: \"{config.conversation.wake_word}\"")
        print(f"Sensitivity: {wake_word_detector.sensitivity}")
        
        # Test with provided text if available
        if test_text:
            print(f"\n📝 Testing with recognized text: \"{test_text}\"")
            detection = wake_word_detector.detect_in_text(test_text)
            
            if detection.detected:
                print(f"✅ Wake word detected! Confidence: {detection.confidence:.2f}")
            else:
                print(f"❌ Wake word not detected. Confidence: {detection.confidence:.2f}")
                print("💡 The text didn't contain 'jarvis' or wasn't clear enough")
        
        # Test live detection
        print(f"\n🎙️  Live wake word test - say 'jarvis' (you have 8 seconds)...")
        
        start_time = time.time()
        detection = wake_word_detector.listen_once(timeout=8.0)
        end_time = time.time()
        
        print(f"⏱️  Listen time: {end_time - start_time:.2f}s")
        
        if detection.detected:
            print(f"🎉 WAKE WORD DETECTED!")
            print(f"   Text: \"{detection.text}\"")
            print(f"   Confidence: {detection.confidence:.2f}")
            print(f"   Method: {detection.detection_method}")
            return True
        else:
            print(f"❌ Wake word not detected")
            if detection.text:
                print(f"   Heard: \"{detection.text}\"")
                print(f"   Confidence: {detection.confidence:.2f}")
                print("💡 Try saying 'jarvis' more clearly")
            else:
                print("   No speech detected")
                print("💡 Try speaking louder or check microphone")
            return False
            
    except Exception as e:
        print(f"❌ Wake word detection test failed: {e}")
        return False


def test_audio_configuration():
    """Test audio configuration settings."""
    print("\n⚙️  AUDIO CONFIGURATION ANALYSIS")
    print("=" * 40)
    
    config = get_config()
    
    print("Current Settings:")
    print(f"  Audio timeout: {config.audio.timeout}s")
    print(f"  Phrase time limit: {config.audio.phrase_time_limit}s")
    print(f"  Microphone index: {config.audio.mic_index}")
    print(f"  Microphone name: {config.audio.mic_name}")
    
    # Check for potential issues
    issues = []
    recommendations = []
    
    if config.audio.timeout < 3:
        issues.append(f"Audio timeout is short ({config.audio.timeout}s)")
        recommendations.append("Increase audio timeout to 5-8 seconds in Settings UI")
    
    if config.audio.phrase_time_limit < 5:
        issues.append(f"Phrase time limit is short ({config.audio.phrase_time_limit}s)")
        recommendations.append("Increase phrase time limit to 8-10 seconds in Settings UI")
    
    if issues:
        print("\n⚠️  POTENTIAL ISSUES:")
        for issue in issues:
            print(f"  • {issue}")
        
        print("\n💡 RECOMMENDATIONS:")
        for rec in recommendations:
            print(f"  • {rec}")
    else:
        print("\n✅ Audio configuration looks good")
    
    return len(issues) == 0


def main():
    """Run comprehensive wake word diagnostic."""
    print("🔍 JARVIS WAKE WORD DIAGNOSTIC TOOL")
    print("=" * 50)
    print("This tool will help diagnose wake word detection issues.")
    print()
    
    # Test 1: Microphone
    mic_ok = test_microphone_list()
    
    # Test 2: Audio configuration
    config_ok = test_audio_configuration()
    
    # Test 3: Speech recognition
    recognized_text = test_speech_recognition()
    
    # Test 4: Wake word detection
    wake_word_ok = test_wake_word_detection(recognized_text)
    
    # Summary
    print("\n📊 DIAGNOSTIC SUMMARY")
    print("=" * 30)
    
    tests = [
        ("Microphone Detection", mic_ok),
        ("Audio Configuration", config_ok),
        ("Speech Recognition", recognized_text is not None),
        ("Wake Word Detection", wake_word_ok)
    ]
    
    for test_name, result in tests:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name}: {status}")
    
    if all(result for _, result in tests):
        print("\n🎉 ALL TESTS PASSED!")
        print("Wake word detection should be working.")
        print("If you're still having issues, try:")
        print("  • Speaking more clearly")
        print("  • Getting closer to the microphone")
        print("  • Reducing background noise")
    else:
        print("\n⚠️  SOME TESTS FAILED")
        print("Check the failed tests above for specific issues.")
        print("Common solutions:")
        print("  • Adjust microphone settings in Jarvis Settings UI")
        print("  • Increase audio timeouts")
        print("  • Check microphone permissions")
        print("  • Try a different microphone")


if __name__ == "__main__":
    main()
