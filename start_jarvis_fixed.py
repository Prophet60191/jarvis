#!/usr/bin/env python3
"""
Start Jarvis - Wake Word Detection Fixed

This is the WORKING version that fixes wake word detection by using
simplified architecture instead of complex async/threading.

USAGE: python start_jarvis_fixed.py
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
from jarvis.core.wake_word import WakeWordDetector
from jarvis.tools import get_langchain_tools

# Configuration
TRIGGER_WORD = "jarvis"
CONVERSATION_TIMEOUT = 30

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

def should_use_tools(command_text):
    """
    Determine if the query needs tools or can use LLM's general knowledge.
    Returns True if tools should be used, False if LLM knowledge is sufficient.
    """
    command_lower = command_text.lower()

    # Definitely needs tools - specific actions or current information
    action_indicators = [
        'open', 'close', 'start', 'stop', 'launch', 'quit', 'exit',
        'search', 'find', 'look up', 'remember', 'save', 'store', 'delete',
        'current time', 'what time is it', 'time is it', 'what\'s the time', 'tell me the time',
        'settings', 'configuration', 'config', 'preferences',
        'logs', 'debug', 'status', 'check', 'test',
        'my name', 'my profile', 'my information',
        'web', 'website', 'browse', 'navigate',
        'file', 'document', 'folder', 'directory'
    ]

    # Special handling for time-related queries
    if 'time' in command_lower:
        # These need the time tool
        time_tool_patterns = ['what time', 'time is it', 'current time', 'tell me the time']
        if any(pattern in command_lower for pattern in time_tool_patterns):
            return True
        # Other time phrases are general knowledge
        else:
            return False

    if any(indicator in command_lower for indicator in action_indicators):
        return True

    # General knowledge patterns - use LLM knowledge
    knowledge_patterns = [
        'tell me about', 'what is', 'what are', 'what was', 'what were',
        'explain', 'describe', 'how does', 'how do', 'how did',
        'why is', 'why are', 'why do', 'why did',
        'who is', 'who was', 'who are', 'who were',
        'when did', 'when was', 'when is', 'when are',
        'where is', 'where are', 'where was', 'where were'
    ]

    if any(pattern in command_lower for pattern in knowledge_patterns):
        return False

    # Questions that sound like general knowledge
    if command_lower.endswith('?') and any(word in command_lower for word in ['what', 'how', 'why', 'who', 'when', 'where']):
        return False

    # Default to tools for ambiguous cases
    return True


def get_llm_knowledge_response(command_text, config):
    """
    Get a response using the LLM's built-in knowledge without any tools.
    This bypasses the agent entirely to avoid RAG hijacking.
    """
    try:
        # Import LLM directly to bypass agent and tools
        from jarvis.llm.openai_llm import OpenAILLM

        # Create a direct LLM instance
        llm = OpenAILLM(config.llm)
        llm.initialize()

        # Create a knowledge-focused prompt
        system_prompt = """You are Jarvis, an intelligent voice assistant. You have extensive knowledge about many topics including science, technology, history, culture, and general information.

When users ask general knowledge questions, provide helpful, informative, and conversational responses using your built-in knowledge. Keep responses appropriate for a voice assistant - clear, engaging, and not too long.

Do not mention tools, functions, or limitations. Just answer the question naturally and helpfully."""

        user_prompt = f"User question: {command_text}"

        # Get response directly from LLM without tools
        response = llm.generate_response(user_prompt, system_prompt=system_prompt)

        return response

    except Exception as e:
        logger.error(f"Direct LLM response failed: {e}")
        # Simple fallback response
        return f"I'd be happy to help with that question about {command_text.lower()}, but I'm having trouble accessing my knowledge base right now. Could you try rephrasing the question?"

def main():
    """
    WORKING Jarvis Main - Wake Word Detection Fixed
    
    This version works because it uses simple synchronous architecture
    instead of complex async/threading that was breaking wake word detection.
    """
    try:
        print("🚀 STARTING JARVIS - WAKE WORD DETECTION FIXED")
        print("=" * 60)
        print("Using simplified architecture (no async/threading issues)")
        print()

        # Clear any cached configuration
        clear_config_cache()
        config = get_config()
        
        logger.info("Starting Jarvis Voice Assistant with fixed wake word detection")

        # Initialize speech manager (WORKING)
        print("🔊 Initializing speech system...")
        speech_manager = SpeechManager(config.audio)
        speech_manager.initialize()
        print("✅ Speech system initialized")
        logger.info("Speech system initialized")

        # Initialize agent (WORKING)
        print("🧠 Initializing AI agent...")
        agent = JarvisAgent(config.llm, config.agent)
        tools = get_langchain_tools()
        agent.initialize(tools=tools)
        print(f"✅ AI agent initialized with {len(tools)} tools")
        logger.info(f"AI agent initialized with {len(tools)} tools")

        # Initialize wake word detector (WORKING - no threading issues)
        print("🎤 Initializing wake word detector...")
        wake_word_detector = WakeWordDetector(
            config.conversation,
            speech_manager
        )
        print("✅ Wake word detector initialized")
        logger.info("Wake word detector initialized")

        print("🎉 Jarvis initialization completed successfully!")
        logger.info("Jarvis initialization completed successfully!")
        
        # Show startup info
        print()
        print("JARVIS VOICE ASSISTANT - READY")
        print("=" * 40)
        print("🎤 Listening for wake word 'jarvis'")
        print("💬 Say 'jarvis' to start conversation")
        print("⏹️  Press Ctrl+C to stop")
        print("─" * 40)

        # Simple main loop (WORKING - like successful llm-guy/jarvis)
        conversation_mode = False
        last_interaction_time = None
        
        while True:
            try:
                if not conversation_mode:
                    # Listen for wake word
                    detection = wake_word_detector.listen_once(timeout=5.0)
                    
                    if detection.detected:
                        logger.info(f"Wake word detected: {detection.text} (confidence: {detection.confidence:.2f})")
                        print(f"🎉 Wake word detected: '{detection.text}'")
                        
                        # Respond with Coqui TTS (FIXED METHOD NAME)
                        try:
                            speech_manager.speak_text("Yes sir?")
                            conversation_mode = True
                            last_interaction_time = time.time()
                            print("💬 Conversation mode activated")
                        except Exception as e:
                            logger.error(f"TTS error: {e}")
                            print(f"❌ TTS error: {e}")
                
                else:
                    # Listen for command
                    print("🎤 Listening for command...")
                    command_text = speech_manager.listen_for_speech(timeout=8.0, phrase_time_limit=10.0)
                    
                    if command_text and command_text.strip():
                        logger.info(f"Processing command: {command_text}")
                        print(f"📥 Command: '{command_text}'")
                        
                        # Process with agent (FIXED METHOD NAME + QUICK RESPONSE FOR SIMPLE QUERIES)
                        try:
                            # Quick responses for simple queries (bypass slow RAG)
                            command_lower = command_text.lower()

                            if any(phrase in command_lower for phrase in ['what time', 'time is it', 'current time']):
                                # Handle time queries directly
                                print("⚡ Quick time response...")
                                try:
                                    from jarvis.tools.plugins.device_time_tool import get_current_time
                                    time_result = get_current_time.invoke({})
                                    response = f"The current time is {time_result}"
                                except Exception as e:
                                    # Fallback to system time
                                    import datetime
                                    now = datetime.datetime.now()
                                    response = f"The current time is {now.strftime('%I:%M %p on %A, %B %d, %Y')}"
                                    logger.warning(f"Time tool failed, using fallback: {e}")

                                print(f"🤖 Jarvis: {response}")
                                speech_manager.speak_text(response)
                                last_interaction_time = time.time()

                            else:
                                # Smart routing: determine if we need tools or can use LLM knowledge
                                if should_use_tools(command_text):
                                    # Use full agent with tools for specific actions
                                    print("🛠️ Processing with tools...")
                                    import asyncio
                                    try:
                                        # Try to use existing event loop
                                        loop = asyncio.get_event_loop()
                                        if loop.is_running():
                                            # Create a new event loop for this call
                                            response = asyncio.run(agent.process_input(command_text))
                                        else:
                                            response = loop.run_until_complete(agent.process_input(command_text))
                                    except RuntimeError:
                                        # No event loop, create one
                                        response = asyncio.run(agent.process_input(command_text))

                                    print(f"🤖 Jarvis: {response}")
                                    speech_manager.speak_text(response)
                                    last_interaction_time = time.time()
                                else:
                                    # Use LLM's built-in knowledge for general questions
                                    print("🧠 Using LLM knowledge...")
                                    try:
                                        response = get_llm_knowledge_response(command_text, config)
                                        print(f"🤖 Jarvis: {response}")
                                        speech_manager.speak_text(response)
                                        last_interaction_time = time.time()
                                    except Exception as e:
                                        logger.error(f"LLM knowledge response failed: {e}")
                                        # Fallback to tools if knowledge response fails
                                        print("🛠️ Fallback to tools...")
                                        import asyncio
                                        response = asyncio.run(agent.process_input(command_text))
                                        print(f"🤖 Jarvis: {response}")
                                        speech_manager.speak_text(response)
                                        last_interaction_time = time.time()

                        except Exception as e:
                            logger.error(f"Error processing command: {e}")
                            error_response = "I'm sorry, I encountered an error processing that request."
                            try:
                                speech_manager.speak_text(error_response)
                            except Exception as tts_e:
                                logger.error(f"TTS error: {tts_e}")
                            last_interaction_time = time.time()
                    else:
                        print("🔇 No command detected")
                    
                    # Check timeout
                    if last_interaction_time and time.time() - last_interaction_time > CONVERSATION_TIMEOUT:
                        logger.info("Conversation timeout - returning to wake word mode")
                        print("⌛ Conversation timeout - returning to wake word mode")
                        conversation_mode = False

            except KeyboardInterrupt:
                logger.info("Received keyboard interrupt")
                print("\n🛑 Stopping Jarvis...")
                break
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                print(f"❌ Error: {e}")
                time.sleep(1)

        return 0

    except KeyboardInterrupt:
        print("\n👋 Jarvis stopped by user")
        return 0
    except Exception as e:
        logger.critical(f"Critical error: {e}", exc_info=True)
        print(f"❌ Critical error: {e}")
        return 1
    finally:
        print("👋 Jarvis shutdown complete")


if __name__ == "__main__":
    print("🎯 JARVIS WAKE WORD DETECTION - FIXED VERSION")
    print("This version uses simplified architecture that WORKS!")
    print("Based on successful test results")
    print()
    
    exit_code = main()
    sys.exit(exit_code)
