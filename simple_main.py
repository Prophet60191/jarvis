#!/usr/bin/env python3
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
