#!/usr/bin/env python3
"""
Simple Whisper Wake Word Test

This implements wake word detection using:
- Whisper for speech recognition (like our current setup)
- Simple architecture (like the working llm-guy/jarvis)
- No async/threading complications
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

def test_whisper_wake_word():
    """Test wake word detection using Whisper with simple architecture."""
    print("🔍 TESTING WHISPER WAKE WORD DETECTION")
    print("=" * 50)
    print("Using Whisper + Simple Architecture (no async/threading)")
    print()
    
    try:
        # Import Jarvis Whisper components
        from jarvis.config import get_config
        from jarvis.audio.whisper_speech import WhisperSpeechRecognizer
        
        # Load configuration
        config = get_config()
        print(f"✅ Configuration loaded:")
        print(f"   Microphone: {config.audio.mic_name} (index: {config.audio.mic_index})")
        print(f"   Energy threshold: {config.audio.energy_threshold}")
        
        # Initialize Whisper (like our current setup)
        print("🤖 Initializing Whisper...")
        whisper = WhisperSpeechRecognizer(config.audio)
        whisper.initialize()
        print("✅ Whisper initialized")
        
        # Initialize speech recognition components
        recognizer = sr.Recognizer()
        recognizer.energy_threshold = config.audio.energy_threshold
        mic = sr.Microphone(device_index=config.audio.mic_index)
        
        print(f"✅ Microphone setup: index {config.audio.mic_index}")
        
        # Adjust for ambient noise
        with mic as source:
            print("🔧 Adjusting for ambient noise...")
            recognizer.adjust_for_ambient_noise(source, duration=1)
            print(f"✅ Energy threshold: {recognizer.energy_threshold}")
        
        print()
        print("🎤 WHISPER WAKE WORD DETECTION ACTIVE")
        print("Say 'jarvis' to trigger conversation mode")
        print("Press Ctrl+C to stop")
        print()
        
        conversation_mode = False
        last_interaction_time = None
        
        # Main loop (simple like working example)
        while True:
            try:
                if not conversation_mode:
                    print("🎤 Listening for wake word...")
                    
                    # Capture audio
                    with mic as source:
                        audio = recognizer.listen(source, timeout=10, phrase_time_limit=5)
                    
                    # Use Whisper for recognition (our preferred method)
                    transcript = whisper.recognize_speech_from_audio_data(audio)
                    
                    if transcript and transcript.strip():
                        print(f"🗣 Whisper heard: '{transcript}'")
                        
                        # Simple wake word detection (like working example)
                        if TRIGGER_WORD.lower() in transcript.lower():
                            print(f"🎉 WAKE WORD DETECTED: '{transcript}'")
                            print("✅ Entering conversation mode...")
                            conversation_mode = True
                            last_interaction_time = time.time()
                            
                            # Simulate response (would use Coqui TTS in real implementation)
                            print("🤖 Jarvis: Yes sir? (Coqui TTS would speak this)")
                            
                        else:
                            print("❌ Wake word not detected, continuing...")
                    else:
                        print("🔇 Whisper: No speech detected")
                
                else:
                    print("🎤 Listening for command...")
                    
                    with mic as source:
                        audio = recognizer.listen(source, timeout=10, phrase_time_limit=8)
                    
                    command = whisper.recognize_speech_from_audio_data(audio)
                    
                    if command and command.strip():
                        print(f"📥 Command: '{command}'")
                        
                        # Simulate processing
                        print("🤖 Jarvis: I heard your command! (Coqui TTS would speak this)")
                        last_interaction_time = time.time()
                    else:
                        print("🔇 No command detected")
                    
                    # Check for timeout
                    if last_interaction_time and time.time() - last_interaction_time > CONVERSATION_TIMEOUT:
                        print("⌛ Timeout: Returning to wake word mode")
                        conversation_mode = False
            
            except sr.WaitTimeoutError:
                print("⚠️ Timeout waiting for audio")
                if conversation_mode and last_interaction_time:
                    if time.time() - last_interaction_time > CONVERSATION_TIMEOUT:
                        print("⌛ No input in conversation mode. Returning to wake word mode")
                        conversation_mode = False
            
            except Exception as e:
                print(f"❌ Error during recognition: {e}")
                time.sleep(1)
    
    except KeyboardInterrupt:
        print("\n🛑 Stopping wake word detection")
    
    except Exception as e:
        print(f"❌ Critical error: {e}")
        import traceback
        traceback.print_exc()


def test_whisper_basic():
    """Test basic Whisper functionality."""
    print("🤖 TESTING BASIC WHISPER FUNCTIONALITY")
    print("=" * 50)
    
    try:
        from jarvis.config import get_config
        from jarvis.audio.whisper_speech import WhisperSpeechRecognizer
        
        config = get_config()
        print(f"✅ Config: mic={config.audio.mic_name}, threshold={config.audio.energy_threshold}")
        
        # Initialize Whisper
        whisper = WhisperSpeechRecognizer(config.audio)
        whisper.initialize()
        print("✅ Whisper initialized")
        
        # Test audio capture and recognition
        recognizer = sr.Recognizer()
        recognizer.energy_threshold = config.audio.energy_threshold
        mic = sr.Microphone(device_index=config.audio.mic_index)
        
        print("🎙️ Say something (3 seconds)...")
        with mic as source:
            audio = recognizer.listen(source, timeout=3, phrase_time_limit=5)
        
        print(f"✅ Audio captured: {len(audio.frame_data)} bytes")
        
        # Test Whisper recognition
        text = whisper.recognize_speech_from_audio_data(audio)
        
        if text and text.strip():
            print(f"✅ Whisper recognized: '{text}'")
            
            # Test wake word detection
            if TRIGGER_WORD.lower() in text.lower():
                print(f"🎉 WAKE WORD DETECTED in text!")
            else:
                print(f"❌ Wake word not in text (this is normal if you didn't say 'jarvis')")
            
            return True
        else:
            print("❌ Whisper returned empty/None")
            return False
            
    except Exception as e:
        print(f"❌ Whisper test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run the Whisper wake word test."""
    print("🧪 WHISPER WAKE WORD DETECTION TEST")
    print("=" * 50)
    print("Testing wake word detection using:")
    print("• Whisper for speech recognition (our preferred)")
    print("• Simple architecture (like working example)")
    print("• No async/threading complications")
    print()
    
    # Test 1: Basic Whisper functionality
    whisper_ok = test_whisper_basic()
    
    if not whisper_ok:
        print("❌ Basic Whisper test failed - cannot proceed")
        return
    
    print()
    print("✅ Basic Whisper test passed!")
    print()
    
    # Test 2: Full wake word detection
    test_whisper_wake_word()


if __name__ == "__main__":
    main()
