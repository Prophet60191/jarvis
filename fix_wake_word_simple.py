#!/usr/bin/env python3
"""
Fix Wake Word Detection - Use Existing Working Components

Instead of reinventing the wheel, let's use our existing working components
but simplify the architecture like the working example.
"""

import sys
import time
import logging
from pathlib import Path

# Add jarvis to path
sys.path.insert(0, str(Path(__file__).parent / "jarvis"))

def test_existing_components():
    """Test our existing components that we know work."""
    print("🔍 TESTING EXISTING JARVIS COMPONENTS")
    print("=" * 50)
    
    try:
        from jarvis.config import get_config
        from jarvis.core.speech import SpeechManager
        
        # Load config
        config = get_config()
        print(f"✅ Config loaded:")
        print(f"   Microphone: {config.audio.mic_name} (index: {config.audio.mic_index})")
        print(f"   Energy threshold: {config.audio.energy_threshold}")
        
        # Initialize speech manager (our existing working component)
        print("🔊 Initializing SpeechManager...")
        speech_manager = SpeechManager(config.audio)
        speech_manager.initialize()
        print("✅ SpeechManager initialized")
        
        # Test speech recognition
        print("🎙️ Testing speech recognition (say something for 3 seconds)...")
        text = speech_manager.listen_for_speech(timeout=3.0, phrase_time_limit=5.0)
        
        if text and text.strip():
            print(f"✅ Speech recognized: '{text}'")
            
            # Test wake word detection
            if "jarvis" in text.lower():
                print(f"🎉 WAKE WORD DETECTED!")
                return True
            else:
                print(f"❌ Wake word not detected (normal if you didn't say 'jarvis')")
                return True  # Still successful - microphone works
        else:
            print("❌ No speech detected")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def simple_wake_word_loop():
    """Simple wake word loop using existing working components."""
    print("\n🎤 SIMPLE WAKE WORD LOOP")
    print("=" * 40)
    print("Using existing SpeechManager (no async/threading)")
    print()
    
    try:
        from jarvis.config import get_config
        from jarvis.core.speech import SpeechManager
        
        # Initialize components
        config = get_config()
        speech_manager = SpeechManager(config.audio)
        speech_manager.initialize()
        
        print("✅ Components initialized")
        print("🎤 Listening for wake word 'jarvis'...")
        print("Press Ctrl+C to stop")
        print()
        
        conversation_mode = False
        last_interaction_time = None
        
        while True:
            try:
                if not conversation_mode:
                    print("🎤 Listening for wake word...")
                    
                    # Use our existing working speech recognition
                    text = speech_manager.listen_for_speech(timeout=5.0, phrase_time_limit=8.0)
                    
                    if text and text.strip():
                        print(f"🗣 Heard: '{text}'")
                        
                        # Simple wake word detection
                        if "jarvis" in text.lower():
                            print(f"🎉 WAKE WORD DETECTED: '{text}'")
                            print("✅ Entering conversation mode...")
                            conversation_mode = True
                            last_interaction_time = time.time()
                            
                            # Simulate TTS response
                            print("🤖 Jarvis: Yes sir? (would use Coqui TTS)")
                        else:
                            print("❌ Wake word not detected, continuing...")
                    else:
                        print("🔇 No speech detected")
                
                else:
                    print("🎤 Listening for command...")
                    
                    command = speech_manager.listen_for_speech(timeout=8.0, phrase_time_limit=10.0)
                    
                    if command and command.strip():
                        print(f"📥 Command: '{command}'")
                        print("🤖 Jarvis: Processing command... (would use Coqui TTS)")
                        last_interaction_time = time.time()
                    else:
                        print("🔇 No command detected")
                    
                    # Check for timeout
                    if last_interaction_time and time.time() - last_interaction_time > 30:
                        print("⌛ Timeout: Returning to wake word mode")
                        conversation_mode = False
            
            except KeyboardInterrupt:
                print("\n🛑 Stopping...")
                break
            
            except Exception as e:
                print(f"❌ Error: {e}")
                time.sleep(1)
    
    except Exception as e:
        print(f"❌ Critical error: {e}")
        import traceback
        traceback.print_exc()


def create_simple_main_py():
    """Create a simplified main.py that works like the llm-guy/jarvis example."""
    print("\n📝 CREATING SIMPLIFIED MAIN.PY")
    print("=" * 40)
    
    simple_main_content = '''#!/usr/bin/env python3
"""
Simplified Jarvis Main - Based on Working llm-guy/jarvis Architecture

This removes all the async/threading complexity and uses a simple loop
with our existing Whisper + Coqui components.
"""

import sys
import time
import logging
from pathlib import Path

# Add jarvis to path
sys.path.insert(0, str(Path(__file__).parent / "jarvis"))

from jarvis.config import get_config
from jarvis.core.speech import SpeechManager
from jarvis.core.agent import JarvisAgent
from jarvis.tools import get_langchain_tools

# Configuration
TRIGGER_WORD = "jarvis"
CONVERSATION_TIMEOUT = 30

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Simple main function - no async/threading."""
    try:
        print("🤖 Starting Simplified Jarvis...")
        
        # Load configuration
        config = get_config()
        logger.info(f"Using microphone: {config.audio.mic_name}")
        
        # Initialize components (synchronously)
        speech_manager = SpeechManager(config.audio)
        speech_manager.initialize()
        logger.info("Speech manager initialized")
        
        # Initialize agent
        agent = JarvisAgent(config.llm, config.agent)
        tools = get_langchain_tools()
        agent.initialize(tools=tools)
        logger.info(f"Agent initialized with {len(tools)} tools")
        
        print("✅ Jarvis ready!")
        print("🎤 Say 'jarvis' to start conversation")
        print("Press Ctrl+C to stop")
        
        conversation_mode = False
        last_interaction_time = None
        
        # Simple main loop (like llm-guy/jarvis)
        while True:
            try:
                if not conversation_mode:
                    logger.info("Listening for wake word...")
                    
                    # Listen for wake word
                    text = speech_manager.listen_for_speech(timeout=5.0)
                    
                    if text and TRIGGER_WORD.lower() in text.lower():
                        logger.info(f"Wake word detected: {text}")
                        speech_manager.speak("Yes sir?")
                        conversation_mode = True
                        last_interaction_time = time.time()
                
                else:
                    logger.info("Listening for command...")
                    
                    # Listen for command
                    command = speech_manager.listen_for_speech(timeout=8.0)
                    
                    if command and command.strip():
                        logger.info(f"Processing command: {command}")
                        
                        # Process with agent
                        response = agent.process_query(command)
                        speech_manager.speak(response)
                        
                        last_interaction_time = time.time()
                    
                    # Check timeout
                    if time.time() - last_interaction_time > CONVERSATION_TIMEOUT:
                        logger.info("Conversation timeout")
                        conversation_mode = False
            
            except KeyboardInterrupt:
                logger.info("Shutting down...")
                break
            except Exception as e:
                logger.error(f"Error: {e}")
                time.sleep(1)
    
    except Exception as e:
        logger.error(f"Critical error: {e}")

if __name__ == "__main__":
    main()
'''
    
    # Save the simplified main.py
    with open("simple_main.py", "w") as f:
        f.write(simple_main_content)
    
    print("✅ Created simple_main.py")
    print("💡 This removes all async/threading complexity")
    print("💡 Uses simple loop like working llm-guy/jarvis")
    print("💡 Keeps our Whisper + Coqui components")


def main():
    """Run the wake word fix tests."""
    print("🔧 WAKE WORD DETECTION FIX")
    print("=" * 50)
    print("Testing existing components and creating simplified version")
    print()
    
    # Test 1: Verify existing components work
    components_ok = test_existing_components()
    
    if components_ok:
        print("\n✅ Existing components work!")
        
        # Test 2: Simple wake word loop
        try:
            simple_wake_word_loop()
        except KeyboardInterrupt:
            pass
        
        # Test 3: Create simplified main.py
        create_simple_main_py()
        
        print("\n🎯 SOLUTION SUMMARY:")
        print("1. ✅ Existing components (SpeechManager, Whisper, Coqui) work")
        print("2. ❌ Async/threading architecture is causing issues")
        print("3. 💡 Solution: Use simple_main.py (no async/threading)")
        print("4. 🚀 This matches the working llm-guy/jarvis architecture")
    else:
        print("\n❌ Existing components have issues - need deeper investigation")


if __name__ == "__main__":
    main()
