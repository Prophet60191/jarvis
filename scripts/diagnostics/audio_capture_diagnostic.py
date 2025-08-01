#!/usr/bin/env python3
"""
Audio Capture Diagnostic Tool

This tool tests the audio capture pipeline step by step to identify
where the "No speech detected" issue is occurring.
"""

import sys
import time
import tempfile
import wave
from pathlib import Path

# Add jarvis to path
sys.path.insert(0, str(Path(__file__).parent / "jarvis"))

import speech_recognition as sr
from jarvis.config import get_config


def test_raw_microphone_capture():
    """Test raw microphone capture using speech_recognition library."""
    print("🎤 RAW MICROPHONE CAPTURE TEST")
    print("=" * 40)
    
    try:
        config = get_config()
        
        # Test each available microphone
        for mic_index in [1, 2, 4]:  # Skip 0 since it's failing
            print(f"\n🔍 Testing microphone index {mic_index}...")
            
            try:
                # Create recognizer and microphone
                recognizer = sr.Recognizer()
                microphone = sr.Microphone(device_index=mic_index)
                
                print(f"✅ Microphone {mic_index} created successfully")
                
                # Test ambient noise adjustment
                with microphone as source:
                    print("🔧 Adjusting for ambient noise...")
                    recognizer.adjust_for_ambient_noise(source, duration=1)
                    print(f"✅ Energy threshold set to: {recognizer.energy_threshold}")
                
                # Test audio capture
                print("🎙️  Capturing audio (say something for 3 seconds)...")
                with microphone as source:
                    audio = recognizer.listen(source, timeout=3, phrase_time_limit=5)
                    
                print(f"✅ Audio captured successfully!")
                print(f"   Sample rate: {audio.sample_rate}")
                print(f"   Sample width: {audio.sample_width}")
                print(f"   Frame data length: {len(audio.frame_data)}")
                
                # Save audio to file for inspection
                audio_file = f"test_audio_mic_{mic_index}.wav"
                with open(audio_file, "wb") as f:
                    f.write(audio.get_wav_data())
                print(f"✅ Audio saved to {audio_file}")
                
                # Test with Google Speech Recognition (online test)
                try:
                    print("🌐 Testing with Google Speech Recognition...")
                    text = recognizer.recognize_google(audio)
                    print(f"✅ Google recognized: \"{text}\"")
                    return mic_index, audio  # Return working mic and audio
                except sr.UnknownValueError:
                    print("❌ Google could not understand audio")
                except sr.RequestError as e:
                    print(f"❌ Google service error: {e}")
                
            except sr.WaitTimeoutError:
                print(f"⏰ Timeout - no audio detected on microphone {mic_index}")
            except Exception as e:
                print(f"❌ Error with microphone {mic_index}: {e}")
        
        return None, None
        
    except Exception as e:
        print(f"❌ Raw microphone test failed: {e}")
        return None, None


def test_whisper_with_captured_audio(audio_data):
    """Test Whisper recognition with captured audio."""
    print("\n🤖 WHISPER RECOGNITION TEST")
    print("=" * 40)
    
    try:
        from jarvis.audio.whisper_speech import WhisperSpeechRecognizer
        from jarvis.config import get_config
        
        config = get_config()
        
        print("🔧 Initializing Whisper...")
        whisper = WhisperSpeechRecognizer(config.audio)
        whisper.initialize()
        print("✅ Whisper initialized")
        
        print("🎯 Testing Whisper recognition...")
        text = whisper.recognize_speech_from_audio_data(audio_data)
        
        if text and text.strip():
            print(f"✅ Whisper recognized: \"{text}\"")
            return True
        else:
            print("❌ Whisper returned empty text")
            return False
            
    except Exception as e:
        print(f"❌ Whisper test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_energy_threshold_adjustment():
    """Test different energy threshold settings."""
    print("\n⚡ ENERGY THRESHOLD TEST")
    print("=" * 40)
    
    try:
        # Test with different energy thresholds
        thresholds = [50, 100, 200, 300, 500, 1000]
        
        for threshold in thresholds:
            print(f"\n🔧 Testing energy threshold: {threshold}")
            
            recognizer = sr.Recognizer()
            recognizer.energy_threshold = threshold
            
            # Try microphone 2 (MacBook Pro)
            microphone = sr.Microphone(device_index=2)
            
            try:
                with microphone as source:
                    print(f"🎙️  Listening with threshold {threshold} (2 seconds)...")
                    audio = recognizer.listen(source, timeout=2, phrase_time_limit=3)
                    
                print(f"✅ Audio captured with threshold {threshold}")
                print(f"   Frame data length: {len(audio.frame_data)}")
                
                # Quick test with Google
                try:
                    text = recognizer.recognize_google(audio)
                    print(f"✅ Recognized: \"{text}\"")
                    print(f"🎯 OPTIMAL THRESHOLD FOUND: {threshold}")
                    return threshold
                except:
                    print("❌ No speech recognized")
                    
            except sr.WaitTimeoutError:
                print(f"⏰ Timeout with threshold {threshold}")
            except Exception as e:
                print(f"❌ Error with threshold {threshold}: {e}")
        
        return None
        
    except Exception as e:
        print(f"❌ Energy threshold test failed: {e}")
        return None


def test_microphone_permissions():
    """Test if microphone permissions are actually working."""
    print("\n🔒 MICROPHONE PERMISSIONS TEST")
    print("=" * 40)
    
    try:
        import pyaudio
        
        print("🔧 Testing PyAudio microphone access...")
        
        # Try to create PyAudio instance
        p = pyaudio.PyAudio()
        
        # Get device count
        device_count = p.get_device_count()
        print(f"✅ Found {device_count} audio devices")
        
        # List input devices
        input_devices = []
        for i in range(device_count):
            device_info = p.get_device_info_by_index(i)
            if device_info['maxInputChannels'] > 0:
                input_devices.append((i, device_info['name']))
                print(f"   Input device {i}: {device_info['name']}")
        
        # Try to open a stream on each input device
        for device_index, device_name in input_devices:
            try:
                print(f"\n🎤 Testing stream on device {device_index}: {device_name}")
                
                stream = p.open(
                    format=pyaudio.paInt16,
                    channels=1,
                    rate=16000,
                    input=True,
                    input_device_index=device_index,
                    frames_per_buffer=1024
                )
                
                print("✅ Stream opened successfully")
                
                # Try to read some data
                data = stream.read(1024)
                print(f"✅ Read {len(data)} bytes of audio data")
                
                stream.stop_stream()
                stream.close()
                print("✅ Stream closed successfully")
                
            except Exception as e:
                print(f"❌ Failed to open stream on device {device_index}: {e}")
        
        p.terminate()
        return True
        
    except ImportError:
        print("❌ PyAudio not available - cannot test low-level audio access")
        return False
    except Exception as e:
        print(f"❌ PyAudio test failed: {e}")
        return False


def main():
    """Run comprehensive audio capture diagnostic."""
    print("🔍 AUDIO CAPTURE DIAGNOSTIC TOOL")
    print("=" * 50)
    print("This tool will test the audio capture pipeline step by step.")
    print()
    
    # Test 1: Microphone permissions
    permissions_ok = test_microphone_permissions()
    
    # Test 2: Raw microphone capture
    working_mic, captured_audio = test_raw_microphone_capture()
    
    # Test 3: Energy threshold optimization
    optimal_threshold = test_energy_threshold_adjustment()
    
    # Test 4: Whisper recognition (if we have audio)
    whisper_ok = False
    if captured_audio:
        whisper_ok = test_whisper_with_captured_audio(captured_audio)
    
    # Summary
    print("\n📊 DIAGNOSTIC SUMMARY")
    print("=" * 30)
    
    tests = [
        ("Microphone Permissions", permissions_ok),
        ("Raw Audio Capture", working_mic is not None),
        ("Energy Threshold", optimal_threshold is not None),
        ("Whisper Recognition", whisper_ok)
    ]
    
    for test_name, result in tests:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name}: {status}")
    
    if working_mic:
        print(f"\n🎯 WORKING MICROPHONE: Index {working_mic}")
    
    if optimal_threshold:
        print(f"🎯 OPTIMAL ENERGY THRESHOLD: {optimal_threshold}")
    
    print("\n💡 RECOMMENDATIONS:")
    if working_mic:
        print(f"  • Set JARVIS_MIC_INDEX={working_mic}")
    if optimal_threshold:
        print(f"  • Set energy threshold to {optimal_threshold}")
    if not permissions_ok:
        print("  • Check microphone permissions in System Preferences")
    if not whisper_ok and captured_audio:
        print("  • Whisper may need different audio format or settings")


if __name__ == "__main__":
    main()
