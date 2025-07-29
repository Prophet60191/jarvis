#!/usr/bin/env python3
"""
Simple Wake Word Test - Based on Working Implementation

This implements wake word detection using the same simple approach
as the working llm-guy/jarvis repository.
"""

import sys
import time
import logging
from pathlib import Path

# Add jarvis to path
sys.path.insert(0, str(Path(__file__).parent / "jarvis"))

import speech_recognition as sr

# Configuration
MIC_INDEX = 2  # MacBook Pro Microphone
TRIGGER_WORD = "jarvis"
CONVERSATION_TIMEOUT = 30

# Set up logging
logging.basicConfig(level=logging.INFO)

def test_simple_wake_word():
    """Test wake word detection using the simple, working approach."""
    print("🔍 TESTING SIMPLE WAKE WORD DETECTION")
    print("=" * 50)
    print("Based on working llm-guy/jarvis implementation")
    print()
    
    # Initialize speech recognition (like their working version)
    recognizer = sr.Recognizer()
    mic = sr.Microphone(device_index=MIC_INDEX)
    
    print(f"✅ Using microphone index: {MIC_INDEX}")
    print(f"✅ Wake word: '{TRIGGER_WORD}'")
    
    conversation_mode = False
    last_interaction_time = None
    
    try:
        # Adjust for ambient noise (like their version)
        with mic as source:
            print("🔧 Adjusting for ambient noise...")
            recognizer.adjust_for_ambient_noise(source)
            print(f"✅ Energy threshold set to: {recognizer.energy_threshold}")
        
        print()
        print("🎤 WAKE WORD DETECTION ACTIVE")
        print("Say 'jarvis' to trigger conversation mode")
        print("Press Ctrl+C to stop")
        print()
        
        # Main loop (simplified like their version)
        while True:
            try:
                if not conversation_mode:
                    print("🎤 Listening for wake word...")
                    
                    with mic as source:
                        # Listen for audio (like their version)
                        audio = recognizer.listen(source, timeout=10)
                    
                    # Use Google Speech Recognition (like their working version)
                    transcript = recognizer.recognize_google(audio)
                    print(f"🗣 Heard: '{transcript}'")
                    
                    # Simple wake word detection (like their version)
                    if TRIGGER_WORD.lower() in transcript.lower():
                        print(f"🎉 WAKE WORD DETECTED: '{transcript}'")
                        print("✅ Entering conversation mode...")
                        conversation_mode = True
                        last_interaction_time = time.time()
                        
                        # Simulate response
                        print("🤖 Jarvis: Yes sir?")
                        
                    else:
                        print("❌ Wake word not detected, continuing...")
                
                else:
                    print("🎤 Listening for command...")
                    
                    with mic as source:
                        audio = recognizer.listen(source, timeout=10)
                    
                    command = recognizer.recognize_google(audio)
                    print(f"📥 Command: '{command}'")
                    
                    # Simulate processing
                    print("🤖 Jarvis: I heard your command!")
                    last_interaction_time = time.time()
                    
                    # Check for timeout
                    if time.time() - last_interaction_time > CONVERSATION_TIMEOUT:
                        print("⌛ Timeout: Returning to wake word mode")
                        conversation_mode = False
            
            except sr.WaitTimeoutError:
                print("⚠️ Timeout waiting for audio")
                if conversation_mode and last_interaction_time:
                    if time.time() - last_interaction_time > CONVERSATION_TIMEOUT:
                        print("⌛ No input in conversation mode. Returning to wake word mode")
                        conversation_mode = False
            
            except sr.UnknownValueError:
                print("⚠️ Could not understand audio")
            
            except Exception as e:
                print(f"❌ Error: {e}")
                time.sleep(1)
    
    except KeyboardInterrupt:
        print("\n🛑 Stopping wake word detection")
    
    except Exception as e:
        print(f"❌ Critical error: {e}")


def test_microphone_setup():
    """Test microphone setup like their version."""
    print("🎤 TESTING MICROPHONE SETUP")
    print("=" * 40)
    
    try:
        recognizer = sr.Recognizer()
        mic = sr.Microphone(device_index=MIC_INDEX)
        
        print(f"✅ Microphone created: index {MIC_INDEX}")
        
        with mic as source:
            print("🔧 Adjusting for ambient noise...")
            recognizer.adjust_for_ambient_noise(source)
            print(f"✅ Energy threshold: {recognizer.energy_threshold}")
        
        print("🎙️ Testing audio capture (3 seconds)...")
        with mic as source:
            audio = recognizer.listen(source, timeout=3, phrase_time_limit=5)
        
        print(f"✅ Audio captured: {len(audio.frame_data)} bytes")
        
        # Test with Google Speech Recognition
        print("🌐 Testing Google Speech Recognition...")
        text = recognizer.recognize_google(audio)
        print(f"✅ Google recognized: '{text}'")
        
        return True
        
    except Exception as e:
        print(f"❌ Microphone test failed: {e}")
        return False


def main():
    """Run the simple wake word test."""
    print("🧪 SIMPLE WAKE WORD DETECTION TEST")
    print("=" * 50)
    print("Testing wake word detection using the working approach")
    print("from llm-guy/jarvis repository")
    print()
    
    # Test 1: Microphone setup
    mic_ok = test_microphone_setup()
    
    if not mic_ok:
        print("❌ Microphone test failed - cannot proceed")
        return
    
    print()
    print("✅ Microphone test passed!")
    print()
    
    # Test 2: Wake word detection
    test_simple_wake_word()


if __name__ == "__main__":
    main()
