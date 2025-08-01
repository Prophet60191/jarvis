"""
Main entry point for Jarvis Voice Assistant.

This module provides the main application entry point with proper
initialization, error handling, and graceful shutdown.
"""

import sys
import signal
import time
from typing import Optional
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from jarvis.config import get_config, clear_config_cache
from jarvis.utils.logger import setup_logging, get_logger, setup_exception_logging
from jarvis.utils.decorators import error_handler
from jarvis.exceptions import JarvisError, InitializationError
from jarvis.core.speech import SpeechManager
from jarvis.core.agent import JarvisAgent
from jarvis.core.conversation import ConversationManager
from jarvis.core.wake_word import WakeWordDetector
from jarvis.tools import get_langchain_tools, tool_registry


logger = get_logger(__name__)


class JarvisApplication:
    """
    Main Jarvis Voice Assistant application.

    This class coordinates all components and manages the application lifecycle.
    """

    def __init__(self):
        """Initialize the Jarvis application."""
        self.config = None
        self.speech_manager: Optional[SpeechManager] = None
        self.agent: Optional[JarvisAgent] = None
        self.conversation_manager: Optional[ConversationManager] = None
        self.wake_word_detector: Optional[WakeWordDetector] = None
        self.running = False

        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        logger.info("JarvisApplication initialized")

    def _signal_handler(self, signum, _frame):
        """Handle shutdown signals."""
        logger.info(f"Received signal {signum}, initiating graceful shutdown...")
        self.running = False

    @error_handler(reraise=True)
    def initialize(self) -> None:
        """
        Initialize all application components.

        Raises:
            InitializationError: If initialization fails
        """
        try:
            logger.info("🤖 Initializing Jarvis Voice Assistant...")

            # Load configuration
            self.config = get_config()
            logger.info("✅ Configuration loaded")

            # Initialize speech manager
            self.speech_manager = SpeechManager(self.config.audio)
            self.speech_manager.initialize()
            logger.info("✅ Speech system initialized")

            # Initialize LLM agent with tools (built-in + plugins)
            self.agent = JarvisAgent(self.config.llm)
            langchain_tools = get_langchain_tools()
            self.agent.initialize(tools=langchain_tools)
            logger.info(f"✅ AI agent initialized with {len(langchain_tools)} tools")

            # Initialize conversation manager
            self.conversation_manager = ConversationManager(
                self.config.conversation,
                self.speech_manager,
                self.agent
            )
            logger.info("✅ Conversation manager initialized")

            # Initialize wake word detector
            self.wake_word_detector = WakeWordDetector(
                self.config.conversation,
                self.speech_manager
            )
            logger.info("✅ Wake word detector initialized")

            # Set up conversation callbacks
            self._setup_callbacks()

            logger.info("🎉 Jarvis initialization completed successfully!")

        except Exception as e:
            error_msg = f"Failed to initialize Jarvis: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise InitializationError(error_msg) from e

    def _setup_callbacks(self) -> None:
        """Set up callbacks for component interactions."""
        # Set wake word detection callback
        def on_wake_word_detected(detection):
            logger.info(f"Wake word detected: {detection.text} (confidence: {detection.confidence:.2f})")
            try:
                self.conversation_manager.enter_conversation_mode()
            except Exception as e:
                logger.error(f"Failed to enter conversation mode: {str(e)}")

        self.wake_word_detector.set_detection_callback(on_wake_word_detected)

    def run(self) -> None:
        """
        Run the main application loop.

        Raises:
            JarvisError: If application execution fails
        """
        if not self._is_initialized():
            raise JarvisError("Application not initialized. Call initialize() first.")

        try:
            self.running = True
            logger.info("🚀 Starting Jarvis Voice Assistant")

            # Display startup information
            self._display_startup_info()

            # Start main loop
            self._main_loop()

        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt")
        except Exception as e:
            logger.error(f"Application error: {str(e)}", exc_info=True)
            raise JarvisError(f"Application execution failed: {str(e)}") from e
        finally:
            self.shutdown()

    def _is_initialized(self) -> bool:
        """Check if all components are initialized."""
        return all([
            self.config,
            self.speech_manager and self.speech_manager.is_initialized(),
            self.agent and self.agent.is_initialized(),
            self.conversation_manager and self.conversation_manager.is_initialized(),
            self.wake_word_detector
        ])

    def _display_startup_info(self) -> None:
        """Display startup information to user."""
        print("\n" + "="*60)
        print("🤖 JARVIS VOICE ASSISTANT")
        print("="*60)
        print(f"🎤 Microphone: {self.config.audio.mic_name}")
        print(f"🧠 AI Model: {self.config.llm.model}")
        print(f"🔧 Tools: {', '.join(tool_registry.list_tools(enabled_only=True))}")
        print(f"👂 Wake Word: '{self.config.conversation.wake_word}'")
        print(f"⏱️  Timeout: {self.config.conversation.conversation_timeout}s")
        print("="*60)
        print("💡 Say the wake word to start a conversation")
        print("🛑 Press Ctrl+C to exit")
        print("="*60 + "\n")

    def _main_loop(self) -> None:
        """Main application loop (using working backup approach)."""
        logger.info("Entering main application loop")

        # Show user instructions
        print("👂 Listening for wake word...")
        print("💡 Say 'Jarvis' clearly and wait for response")
        print("🔇 If no response, check microphone permissions and try again")

        consecutive_errors = 0
        max_consecutive_errors = 5

        # Simple state management (like the working backup)
        conversation_mode = False
        last_interaction_time = None
        TRIGGER_WORD = "jarvis"
        CONVERSATION_TIMEOUT = 30  # seconds

        while self.running:
            try:
                if not conversation_mode:
                    # Listen for wake word (using the exact working backup approach)
                    logger.debug("🎧 Listening for wake word...")

                    transcript = self.speech_manager.microphone_manager.listen_for_speech(
                        timeout=10.0,
                        service="whisper"
                    )

                    if transcript:
                        logger.info(f"🗣 Heard: '{transcript}'")

                        # Simple wake word detection (like the working backup)
                        if TRIGGER_WORD.lower() in transcript.lower():
                            logger.info(f"🎯 WAKE WORD DETECTED! Triggered by: '{transcript}'")
                            print(f"🎯 WAKE WORD DETECTED! Text: '{transcript}'")

                            # Respond with TTS
                            self.speech_manager.speak_text("Yes sir?")

                            # Enter conversation mode
                            conversation_mode = True
                            last_interaction_time = time.time()
                            consecutive_errors = 0  # Reset error count
                        else:
                            logger.debug("Wake word not detected, continuing...")
                            consecutive_errors = 0  # Reset error count
                    else:
                        logger.debug("No speech detected, continuing...")
                        consecutive_errors = 0  # Reset error count

                else:
                    # In conversation mode - listen for commands
                    logger.debug("🎤 Listening for command...")

                    command = self.speech_manager.microphone_manager.listen_for_speech(
                        timeout=10.0,
                        service="whisper"
                    )

                    if command:
                        # Handle conversation (existing logic)
                        consecutive_errors = 0  # Reset error count
                        self._handle_conversation_with_command(command)
                        last_interaction_time = time.time()
                    else:
                        # Check for conversation timeout
                        if last_interaction_time and (time.time() - last_interaction_time) > CONVERSATION_TIMEOUT:
                            logger.info("Conversation timeout, returning to wake word mode")
                            conversation_mode = False
                            last_interaction_time = None

            except KeyboardInterrupt:
                break
            except Exception as e:
                consecutive_errors += 1
                logger.warning(f"Audio error ({consecutive_errors}/{max_consecutive_errors}): {str(e)}")

                if consecutive_errors >= max_consecutive_errors:
                    logger.error("Too many consecutive audio errors, shutting down")
                    print("❌ Too many audio errors. Please check:")
                    print("   - Microphone permissions")
                    print("   - Microphone is not being used by another app")
                    print("   - Internet connection (for speech recognition)")
                    break

                # Wait a bit before retrying
                time.sleep(1.0)

    def _handle_conversation(self) -> None:
        """Handle a complete conversation session."""
        try:
            logger.info("Starting conversation session")

            # Enter conversation mode
            self.conversation_manager.enter_conversation_mode()

            # Handle conversation cycles until timeout or completion
            while (self.conversation_manager.conversation_active and
                   self.running):

                try:
                    # Handle one conversation cycle
                    should_continue = self.conversation_manager.handle_conversation_cycle()

                    if not should_continue:
                        logger.info("Conversation ended")
                        break

                except Exception as e:
                    logger.error(f"Error in conversation cycle: {str(e)}")
                    break

            # Reset conversation state
            self.conversation_manager.reset_conversation()

        except Exception as e:
            logger.error(f"Error handling conversation: {str(e)}")
            try:
                self.speech_manager.speak_text("I'm having trouble. Let's try again later.")
            except:
                pass

    def _handle_conversation_with_command(self, command: str) -> None:
        """Handle conversation with a specific command (backup approach)."""
        try:
            logger.info(f"Processing command: '{command}'")

            # Get AI response
            response = self.agent.process_input(command)

            if response:
                logger.info(f"AI Response: {response}")

                # Speak the response
                self.speech_manager.speak_text(response)
            else:
                logger.warning("No response from AI agent")
                self.speech_manager.speak_text("I'm not sure how to help with that.")

        except Exception as e:
            logger.error(f"Error processing command: {str(e)}")
            self.speech_manager.speak_text("I encountered an error processing your request.")

    def test_components(self) -> bool:
        """
        Test all components to ensure they're working properly.

        Returns:
            True if all tests pass, False otherwise
        """
        logger.info("Testing Jarvis components...")

        try:
            # Test speech recognition
            print("🎤 Testing speech recognition...")
            if not self.speech_manager.test_speech_recognition(test_duration=3.0):
                logger.error("Speech recognition test failed")
                return False

            # Test text-to-speech
            print("🔊 Testing text-to-speech...")
            if not self.speech_manager.test_text_to_speech():
                logger.error("Text-to-speech test failed")
                return False

            # Test AI agent
            print("🧠 Testing AI agent...")
            if not self.agent.test_model():
                logger.error("AI agent test failed")
                return False

            # Test wake word detection
            print("👂 Testing wake word detection...")
            test_results = self.wake_word_detector.test_detection()
            logger.info(f"Wake word test results: {test_results}")

            print("✅ All component tests passed!")
            return True

        except Exception as e:
            logger.error(f"Component testing failed: {str(e)}")
            return False

    def get_status(self) -> dict:
        """
        Get current application status.

        Returns:
            Dictionary containing status information
        """
        return {
            "initialized": self._is_initialized(),
            "running": self.running,
            "speech_manager": self.speech_manager.get_system_info() if self.speech_manager else None,
            "agent": self.agent.get_model_info() if self.agent else None,
            "conversation": self.conversation_manager.get_conversation_state() if self.conversation_manager else None,
            "wake_word": self.wake_word_detector.get_statistics() if self.wake_word_detector else None,
            "tools": tool_registry.get_registry_info()
        }

    def shutdown(self) -> None:
        """Shutdown the application gracefully."""
        logger.info("🛑 Shutting down Jarvis...")

        self.running = False

        # Cleanup components in reverse order
        if self.wake_word_detector:
            try:
                self.wake_word_detector.cleanup()
                logger.info("✅ Wake word detector cleaned up")
            except Exception as e:
                logger.error(f"Error cleaning up wake word detector: {str(e)}")

        if self.conversation_manager:
            try:
                self.conversation_manager.reset_conversation()
                logger.info("✅ Conversation manager cleaned up")
            except Exception as e:
                logger.error(f"Error cleaning up conversation manager: {str(e)}")

        if self.agent:
            try:
                self.agent.cleanup()
                logger.info("✅ AI agent cleaned up")
            except Exception as e:
                logger.error(f"Error cleaning up agent: {str(e)}")

        if self.speech_manager:
            try:
                self.speech_manager.cleanup()
                logger.info("✅ Speech manager cleaned up")
            except Exception as e:
                logger.error(f"Error cleaning up speech manager: {str(e)}")

        logger.info("👋 Jarvis shutdown complete")


def main() -> int:
    """
    Main entry point for the Jarvis Voice Assistant.

    Returns:
        Exit code (0 for success, 1 for error)
    """
    try:
        # Clear any cached configuration to ensure fresh load
        clear_config_cache()

        # Load configuration first to set up logging
        config = get_config()

        # Set up logging
        setup_logging(config.logging)
        setup_exception_logging()

        logger.info("Starting Jarvis Voice Assistant")

        # Create and run application
        app = JarvisApplication()
        app.initialize()

        # Check if we should run tests first
        if config.general.debug:
            logger.info("Debug mode enabled, running component tests...")
            if not app.test_components():
                logger.error("Component tests failed")
                return 1

        # Run the application
        app.run()

        return 0

    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        return 0
    except Exception as e:
        logger.error(f"Application failed: {str(e)}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
