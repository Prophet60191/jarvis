#!/usr/bin/env python3
"""
Test microphone permissions and basic audio capture
"""

import sys
import logging
import speech_recognition as sr
import numpy as np

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_microphone_permissions():
    """Test basic microphone access and permissions"""
    print("🎤 MICROPHONE PERMISSIONS TEST")
    print("=" * 50)
    
    try:
        # Test basic speech_recognition library
        recognizer = sr.Recognizer()
        
        # List available microphones
        print("📋 Available Microphones:")
        for i, mic_name in enumerate(sr.Microphone.list_microphone_names()):
            print(f"  {i}: {mic_name}")
        
        # Test microphone 0 (MacBook Pro Microphone)
        print(f"\n🎤 Testing microphone 0...")
        mic = sr.Microphone(device_index=0)
        
        with mic as source:
            print("🔧 Adjusting for ambient noise...")
            recognizer.adjust_for_ambient_noise(source, duration=1)
            print(f"   Energy threshold: {recognizer.energy_threshold}")
            
            print("\n🎤 Say something (5 seconds)...")
            try:
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=3)
                print(f"✅ Audio captured: {len(audio.frame_data)} bytes")
                
                # Check audio data
                audio_data = np.frombuffer(audio.frame_data, dtype=np.int16)
                max_amplitude = np.max(np.abs(audio_data))
                print(f"📊 Max amplitude: {max_amplitude}")
                print(f"📊 Sample rate: {audio.sample_rate}")
                print(f"📊 Sample width: {audio.sample_width}")
                
                if max_amplitude > 100:
                    print("✅ Audio has good amplitude - microphone is working!")
                else:
                    print("⚠️ Audio amplitude is very low - check microphone volume")
                
                # Try basic recognition
                print("\n🧠 Testing speech recognition...")
                try:
                    # Use Google for quick test (if available)
                    text = recognizer.recognize_google(audio, language='en-US')
                    print(f"✅ Recognized: '{text}'")
                except sr.UnknownValueError:
                    print("❌ Could not understand audio")
                except sr.RequestError as e:
                    print(f"❌ Recognition service error: {e}")
                
            except sr.WaitTimeoutError:
                print("❌ No audio detected - timeout")
            except Exception as e:
                print(f"❌ Error capturing audio: {e}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_microphone_permissions()
