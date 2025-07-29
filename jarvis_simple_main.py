#!/usr/bin/env python3
"""
Simplified Jarvis Main - Wake Word Detection Fix

This removes all async/threading complexity and uses a simple loop
like the working llm-guy/jarvis example, but with our Whisper + Coqui components.
"""

import sys
import time
import logging
from pathlib import Path

# Add jarvis to path
sys.path.insert(0, str(Path(__file__).parent / "jarvis"))

from jarvis.config import get_config, clear_config_cache
from jarvis.core.speech import SpeechManager
from jarvis.core.agent import JarvisAgent
from jarvis.core.conversation import ConversationManager
from jarvis.core.wake_word import WakeWordDetector
from jarvis.tools import get_langchain_tools

# Import logging setup from the right place
try:
    from jarvis.core.emergency_stop import setup_emergency_stop
except ImportError:
    def setup_emergency_stop(*args, **kwargs):
        pass  # Skip if not available

try:
    from jarvis.logging import setup_logging, setup_exception_logging
except ImportError:
    def setup_logging(*args, **kwargs):
        logging.basicConfig(level=logging.INFO)
    def setup_exception_logging(*args, **kwargs):
        pass

# Configuration
TRIGGER_WORD = "jarvis"
CONVERSATION_TIMEOUT = 30

# Set up logging
logger = logging.getLogger(__name__)

def main() -> int:
    """
    Main entry point for the Jarvis Voice Assistant.
    Simplified version without async/threading complexity - WAKE WORD FIX.
    """
    try:
        # Clear any cached configuration to ensure fresh load
        clear_config_cache()

        # Load config to set up logging
        config = get_config()
        setup_logging(config.logging, clean_console=True)
        setup_exception_logging()

        logger.info("Starting Simplified Jarvis Voice Assistant")

        # Simple synchronous initialization (like working llm-guy/jarvis)
        print("JARVIS VOICE ASSISTANT - SIMPLIFIED")
        print("=" * 60)
        
        # Initialize speech manager
        print("🔊 Initializing speech system...")
        speech_manager = SpeechManager(config.audio)
        speech_manager.initialize()
        print("✅ Speech system initialized")
        logger.info("Speech system initialized")

        # Initialize agent
        print("🧠 Initializing AI agent...")
        agent = JarvisAgent(config.llm, config.agent)
        tools = get_langchain_tools()
        agent.initialize(tools=tools)
        print(f"✅ AI agent initialized with {len(tools)} tools")
        logger.info(f"AI agent initialized with {len(tools)} tools")

        # Initialize conversation manager (simple version)
        print("💬 Initializing conversation manager...")
        conversation_manager = ConversationManager(
            config.conversation,
            speech_manager,
            agent
        )
        print("✅ Conversation manager initialized")
        logger.info("Conversation manager initialized")

        # Initialize wake word detector (in main thread - no threading issues)
        print("🎤 Initializing wake word detector...")
        wake_word_detector = WakeWordDetector(
            config.conversation,
            speech_manager
        )
        print("✅ Wake word detector initialized")
        logger.info("Wake word detector initialized")

        # Set up emergency stop system
        print("🛑 Setting up emergency stop system...")
        setup_emergency_stop(
            speech_manager=speech_manager,
            agent=agent,
            conversation_manager=conversation_manager,
            tts_manager=getattr(speech_manager, 'tts_manager', None)
        )
        print("✅ Emergency stop system activated")
        logger.info("Emergency stop system activated")

        print("🎉 Jarvis initialization completed successfully!")
        logger.info("Jarvis initialization completed successfully!")
        
        # Show startup info
        print()
        print("System ready - listening for wake word...")
        print("Say 'jarvis' to start • Press Ctrl+C to stop")
        print("─" * 60)

        # Simple main loop (like working llm-guy/jarvis)
        conversation_mode = False
        last_interaction_time = None
        
        while True:
            try:
                if not conversation_mode:
                    logger.debug("Listening for wake word...")
                    
                    # Listen for wake word using our working detection
                    detection = wake_word_detector.listen_once(timeout=5.0)
                    
                    if detection.detected:
                        logger.info(f"Wake word detected: {detection.text} (confidence: {detection.confidence:.2f})")
                        print(f"🎉 Wake word detected: '{detection.text}'")
                        
                        # Respond with Coqui TTS
                        speech_manager.speak_text("Yes sir?")
                        conversation_mode = True
                        last_interaction_time = time.time()
                
                else:
                    logger.debug("Listening for command...")
                    
                    # Listen for command
                    command_text = speech_manager.listen_for_speech(timeout=8.0, phrase_time_limit=10.0)
                    
                    if command_text and command_text.strip():
                        logger.info(f"Processing command: {command_text}")
                        print(f"📥 Command: '{command_text}'")
                        
                        # Process with agent
                        try:
                            response = agent.process_query(command_text)
                            print(f"🤖 Jarvis: {response}")
                            
                            # Respond with Coqui TTS
                            speech_manager.speak_text(response)
                            
                            last_interaction_time = time.time()
                        except Exception as e:
                            logger.error(f"Error processing command: {e}")
                            error_response = "I'm sorry, I encountered an error processing that request."
                            speech_manager.speak_text(error_response)
                            last_interaction_time = time.time()
                    
                    # Check timeout
                    if last_interaction_time and time.time() - last_interaction_time > config.conversation.conversation_timeout:
                        logger.info("Conversation timeout - returning to wake word mode")
                        print("⌛ Conversation timeout - returning to wake word mode")
                        conversation_mode = False

            except KeyboardInterrupt:
                logger.info("Received keyboard interrupt")
                break
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                print(f"❌ Error: {e}")
                time.sleep(1)

        return 0

    except KeyboardInterrupt:
        logger.info("Application interrupted by user.")
        return 0
    except Exception as e:
        logger.critical(f"A critical error occurred: {e}", exc_info=True)
        print(f"❌ Critical error: {e}")
        return 1
    finally:
        logger.info("👋 Jarvis shutdown complete.")
        print("👋 Jarvis shutdown complete.")


if __name__ == "__main__":
    sys.exit(main())
