"""
Main entry point for Jarvis Voice Assistant.

This module provides the main application entry point with proper
initialization, error handling, and graceful shutdown.
"""

import sys
import signal
import time
import asyncio
import threading
from typing import Optional
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from jarvis.config import get_config, clear_config_cache
from jarvis.utils.logger import setup_logging, get_logger, setup_exception_logging
from jarvis.utils.decorators import error_handler
from jarvis.exceptions import JarvisError, InitializationError
from jarvis.core.speech import SpeechManager
from jarvis.core.agent import JarvisAgent
from jarvis.core.conversation import ConversationManager
from jarvis.core.wake_word import WakeWordDetector
from jarvis.core.emergency_stop import setup_emergency_stop
from jarvis.utils.terminal_ui import terminal_ui, StatusType
from jarvis.tools import get_langchain_tools, tool_registry, get_langchain_tools


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
        self.mcp_client = None  # Store MCP client for event loop access
        self.loop: Optional[asyncio.AbstractEventLoop] = None  # Persistent event loop
        self.running = False

        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        logger.info("JarvisApplication initialized")

    def _signal_handler(self, signum, _frame):
        """Handle shutdown signals."""
        logger.info(f"Received signal {signum}, initiating graceful shutdown...")
        self.running = False

    def set_event_loop(self, loop: asyncio.AbstractEventLoop):
        """Sets the single, persistent event loop for the application."""
        self.loop = loop
        logger.info("✅ Persistent event loop set for application")

    async def shutdown_async(self):
        """Perform asynchronous shutdown tasks."""
        logger.info("Running async shutdown tasks...")
        # Stop the official MCP system
        try:
            from .core.mcp_official_adapter import stop_official_mcp_system
            await stop_official_mcp_system()
            logger.info("✅ MCP system cleaned up")
        except Exception as e:
            logger.error(f"Error cleaning up MCP system: {str(e)}")

    @error_handler(reraise=True)
    async def initialize(self) -> None:
        """
        Initialize all application components.

        Raises:
            InitializationError: If initialization fails
        """
        try:
            print("🚀 ASYNC INITIALIZE METHOD CALLED - PRINT STATEMENT")
            logger.info("🚀 ASYNC INITIALIZE METHOD CALLED")
            logger.info("🤖 Initializing Jarvis Voice Assistant...")

            # Load configuration
            self.config = get_config()
            logger.info("✅ Configuration loaded")

            # Initialize speech manager
            self.speech_manager = SpeechManager(self.config.audio)
            self.speech_manager.initialize()
            logger.info("✅ Speech system initialized")

            # Start MCP system (will be handled in async agent initialization)
            from .tools import start_mcp_system, get_mcp_tool_manager, get_mcp_client
            if start_mcp_system():
                logger.info("✅ MCP system started")
            else:
                logger.warning("⚠️ MCP system failed to start, continuing without MCP tools")

            # Initialize agent with all tools (built-in + MCP)
            # Use the working synchronous approach since async causes MCP conflicts
            logger.info("🔄 Initializing agent with all available tools...")
            print("🔄 USING SYNCHRONOUS TOOL INITIALIZATION")

            # Initialize RAG system if enabled
            print("🧠 Initializing RAG memory system...")
            from .tools.rag_memory_manager import RAGMemoryManager
            from .tools.rag_tools import get_rag_tools

            rag_tools = []
            if self.config.rag.enabled:
                try:
                    self.rag_manager = RAGMemoryManager(self.config)
                    rag_tools = get_rag_tools(self.rag_manager, debug_mode=self.config.general.debug)
                    print(f"✅ RAG system initialized with {len(rag_tools)} tools")
                    logger.info(f"✅ RAG system initialized with {len(rag_tools)} tools")
                except Exception as e:
                    print(f"⚠️ RAG system initialization failed: {e}")
                    logger.warning(f"RAG system initialization failed: {e}")
                    self.rag_manager = None
            else:
                print("⚠️ RAG system disabled in configuration")
                self.rag_manager = None

            # Use official MCP adapters for proper tool conversion
            print("🔄 Starting official MCP system...")
            from .core.mcp_official_adapter import start_official_mcp_system, get_official_mcp_tools
            from .tools import tool_registry, plugin_manager

            # Start official MCP system
            mcp_success = await start_official_mcp_system(self.config)

            if mcp_success:
                print("✅ Official MCP system started successfully")

                # Get tools using official adapters
                mcp_tools = await get_official_mcp_tools()
                print(f"🎉 Official MCP adapters loaded {len(mcp_tools)} tools")

                # Get plugin tools (includes all functionality - no built-in tools)
                plugin_tools = plugin_manager.get_all_tools()

                # Combine all tools including RAG tools
                all_tools = plugin_tools + mcp_tools + rag_tools
                print(f"📊 Total tools: {len(all_tools)} (plugin: {len(plugin_tools)}, MCP: {len(mcp_tools)}, RAG: {len(rag_tools)})")

                # Store MCP manager for conversation manager access
                from .core.mcp_official_adapter import get_official_mcp_manager
                self.mcp_client = get_official_mcp_manager()
                if self.mcp_client:
                    self.mcp_client.loop = self.loop  # Pass the persistent event loop
            else:
                print("⚠️ Official MCP system failed - using plugin tools only")
                # Fallback to plugin tools + RAG tools (no built-in tools)
                plugin_tools = plugin_manager.get_all_tools()
                all_tools = plugin_tools + rag_tools
                print(f"📊 Fallback tools: {len(all_tools)} (plugin: {len(plugin_tools)}, RAG: {len(rag_tools)})")
                # Set MCP client to None in fallback case
                self.mcp_client = None

            print("🤖 Creating JarvisAgent...")
            self.agent = JarvisAgent(self.config.llm)
            print("🔧 Initializing agent with tools...")

            # Try agent initialization with timeout
            try:
                # Use asyncio.wait_for to add timeout to agent initialization
                await asyncio.wait_for(
                    asyncio.to_thread(self.agent.initialize, all_tools),
                    timeout=30.0  # 30 second timeout
                )
                print(f"✅ Agent initialized with {len(all_tools)} tools")
                print(f"🛠️ Agent tool names: {[tool.name for tool in all_tools]}")
                logger.info(f"✅ AI agent initialized with {len(all_tools)} tools")
            except asyncio.TimeoutError:
                print("❌ Agent initialization timed out - falling back to plugin tools")
                # Fallback to plugin tools + RAG tools if MCP tools cause issues
                from .tools import plugin_manager
                basic_tools = plugin_manager.get_all_tools() + rag_tools
                self.agent.initialize(tools=basic_tools)
                print(f"✅ Agent initialized with {len(basic_tools)} plugin tools (fallback)")
                logger.info(f"✅ Agent initialized with {len(basic_tools)} plugin tools (fallback)")
            except Exception as e:
                print(f"❌ Agent initialization failed: {e}")
                # Fallback to plugin tools + RAG tools
                from .tools import plugin_manager
                basic_tools = plugin_manager.get_all_tools() + rag_tools
                self.agent.initialize(tools=basic_tools)
                print(f"✅ Agent initialized with {len(basic_tools)} plugin tools (error fallback)")
                logger.error(f"Agent initialization failed, using fallback: {e}")

            # MCP tools are now handled in the async agent initialization above

            # Initialize conversation manager
            print("💬 Initializing conversation manager...")
            self.conversation_manager = ConversationManager(
                self.config.conversation,
                self.speech_manager,
                self.agent,
                self.mcp_client  # Pass MCP client for event loop access
            )
            print("✅ Conversation manager initialized")
            logger.info("✅ Conversation manager initialized")

            # Initialize wake word detector
            print("👂 Initializing wake word detector...")
            self.wake_word_detector = WakeWordDetector(
                self.config.conversation,
                self.speech_manager
            )
            print("✅ Wake word detector initialized")
            logger.info("✅ Wake word detector initialized")

            # Set up conversation callbacks
            print("🔗 Setting up callbacks...")
            self._setup_callbacks()
            print("✅ Callbacks set up")

            # Emergency stop system will be set up in main thread after initialization

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

    async def _initialize_agent_with_mcp_tools(self) -> JarvisAgent:
        """
        Initialize the agent with both built-in and MCP tools using proper async pattern.

        Returns:
            JarvisAgent: Fully initialized agent with all tools
        """
        print("🚀 _initialize_agent_with_mcp_tools() called - PRINT STATEMENT")
        logger.info("🚀 _initialize_agent_with_mcp_tools() called")
        try:
            # Get built-in tools first (using the proper conversion method)
            from .tools import tool_registry, plugin_manager
            builtin_tools = tool_registry.get_langchain_tools()
            plugin_tools = plugin_manager.get_all_tools()
            base_tools = builtin_tools + plugin_tools

            print(f"📦 FOUND: {len(builtin_tools)} built-in tools and {len(plugin_tools)} plugin tools")
            logger.info(f"📦 Found {len(builtin_tools)} built-in tools and {len(plugin_tools)} plugin tools")

            # Check if MCP system is available and wait for servers to be ready
            print("🔍 GETTING MCP TOOL MANAGER...")
            mcp_tool_manager = get_mcp_tool_manager()
            print(f"🔍 MCP TOOL MANAGER: {mcp_tool_manager is not None}")

            print("🔍 GETTING MCP CLIENT...")
            mcp_client = get_mcp_client()
            print(f"🔍 MCP CLIENT: {mcp_client is not None}")

            # Store MCP client for conversation manager access
            self.mcp_client = mcp_client

            logger.info(f"🔍 MCP tool manager available: {mcp_tool_manager is not None}")
            logger.info(f"🔍 MCP client available: {mcp_client is not None}")

            if mcp_tool_manager and mcp_client:
                # Wait for MCP servers to be connected and tools discovered
                logger.info("⏳ Waiting for MCP servers to be ready...")

                # Use the new wait method to properly wait for server connections
                servers_ready = mcp_client.wait_for_servers_ready_sync(timeout=10.0)

                if servers_ready:
                    # Get MCP tools after servers are ready
                    mcp_tools = mcp_tool_manager.get_langchain_tools()
                    mcp_count = len(mcp_tools)
                    print(f"🎉 MCP SERVERS READY! Retrieved {mcp_count} MCP tools")
                    logger.info(f"🎉 MCP servers ready! Retrieved {mcp_count} MCP tools")

                    # Log MCP tool names for debugging
                    if mcp_tools:
                        mcp_tool_names = [tool.name for tool in mcp_tools]
                        print(f"🛠️ MCP TOOL NAMES: {mcp_tool_names}")
                        logger.info(f"🛠️ MCP tool names: {mcp_tool_names}")

                    # Combine all tools
                    all_tools = base_tools + mcp_tools
                    print(f"📊 TOTAL TOOLS COMBINED: {len(all_tools)} (base: {len(base_tools)} + mcp: {len(mcp_tools)})")
                else:
                    print("⚠️ MCP SERVERS NOT READY - using only base tools")
                    logger.warning("⚠️ MCP servers not ready after timeout, using only base tools")
                    all_tools = base_tools
            else:
                print("⚠️ MCP SYSTEM NOT AVAILABLE - using only base tools")
                logger.warning("⚠️ MCP system not available, using only base tools")
                all_tools = base_tools

            # Create and initialize agent with all tools
            agent = JarvisAgent(self.config.llm)
            agent.initialize(tools=all_tools)

            print(f"✅ AGENT INITIALIZED WITH {len(all_tools)} TOTAL TOOLS")
            print(f"🛠️ TOOL NAMES: {[tool.name for tool in all_tools]}")
            logger.info(f"✅ Agent initialized with {len(all_tools)} total tools")
            logger.debug(f"🛠️ Tool names: {[tool.name for tool in all_tools]}")

            return agent

        except Exception as e:
            logger.error(f"❌ Failed to initialize agent with MCP tools: {e}")
            # Fallback to base tools only
            logger.info("🔄 Falling back to base tools only")
            agent = JarvisAgent(self.config.llm)
            agent.initialize(tools=base_tools)
            return agent

    def _refresh_agent_tools(self) -> None:
        """Refresh agent tools when MCP tools are updated."""
        try:
            if self.agent and self.agent.is_initialized():
                logger.info("🔄 MCP tools updated - refreshing agent tools...")

                # Get updated tools (includes built-in + MCP tools)
                updated_tools = get_langchain_tools()

                # Force complete re-initialization of the agent with new tools
                logger.info(f"🔧 Re-initializing agent with {len(updated_tools)} tools...")
                self.agent.initialize(tools=updated_tools)

                logger.info(f"✅ Agent completely re-initialized with {len(updated_tools)} total tools")

                # Log the tool names for debugging
                tool_names = [tool.name for tool in updated_tools]
                logger.info(f"🛠️ Available tools: {', '.join(tool_names[:10])}{'...' if len(tool_names) > 10 else ''}")

                # Verify the agent actually has the tools
                if hasattr(self.agent, 'tools') and self.agent.tools:
                    actual_count = len(self.agent.tools)
                    logger.info(f"🔍 Agent reports {actual_count} tools available")
                    if actual_count != len(updated_tools):
                        logger.warning(f"⚠️ Tool count mismatch: expected {len(updated_tools)}, agent has {actual_count}")

            else:
                logger.warning("⚠️ Agent not initialized, cannot refresh tools")
        except Exception as e:
            logger.error(f"❌ Failed to refresh agent tools: {e}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")

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

            # Start main loop (synchronous for wake word detection)
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
        # Clear screen and show header
        terminal_ui.clear_screen()
        terminal_ui.print_header()

        # Get all available tools (plugin-based architecture)
        from .tools import plugin_manager

        # Get plugin tools (includes all functionality - no built-in tools)
        plugin_tools = plugin_manager.get_all_tools()

        # Get MCP tools using official adapters (if available)
        try:
            # Check if we have an active MCP manager
            from .core.mcp_official_adapter import get_official_mcp_manager
            manager = get_official_mcp_manager()
            if manager:
                mcp_tools = manager.get_tools()
            else:
                mcp_tools = []
        except Exception:
            mcp_tools = []

        all_tools = plugin_tools + mcp_tools
        tool_names = [tool.name for tool in all_tools]

        # Show configuration
        config_info = {
            'microphone': self.config.audio.mic_name or 'Default',
            'model': self.config.llm.model,
            'tool_count': len(all_tools),
            'wake_word': self.config.conversation.wake_word,
            'timeout': self.config.conversation.conversation_timeout
        }
        terminal_ui.print_startup_info(config_info)

        # Show available tools
        terminal_ui.show_tool_list(tool_names)

        # Show controls
        terminal_ui.print_controls()

        # Show separator
        terminal_ui.print_separator()

    def _main_loop(self) -> None:
        """Main application loop."""
        logger.info("Entering main application loop")

        # Show listening prompt
        terminal_ui.show_listening_prompt()

        consecutive_errors = 0
        max_consecutive_errors = 5

        while self.running:
            try:
                # Listen for wake word (synchronous - works better)
                detection = self.wake_word_detector.listen_once(timeout=2.0)

                if detection.detected:
                    # Wake word detected, handle conversation
                    consecutive_errors = 0  # Reset error count
                    self._handle_conversation()
                else:
                    # No wake word detected, continue listening
                    consecutive_errors = 0  # Reset error count

            except KeyboardInterrupt:
                break
            except Exception as e:
                consecutive_errors += 1
                logger.warning(f"Audio error ({consecutive_errors}/{max_consecutive_errors}): {str(e)}")

                if consecutive_errors >= max_consecutive_errors:
                    logger.error("Too many consecutive audio errors, shutting down")
                    terminal_ui.show_error(
                        "Too many consecutive audio errors",
                        suggestions=[
                            "Check microphone permissions in System Preferences",
                            "Ensure microphone is not being used by another app",
                            "Verify internet connection for speech recognition",
                            "Try restarting Jarvis"
                        ]
                    )
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
                    # Handle one conversation cycle (sync wrapper for async agent)
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
        terminal_ui.show_shutdown()
        logger.info("🛑 Shutting down Jarvis...")

        self.running = False

        # Cleanup components in reverse order
        if self.wake_word_detector:
            try:
                self.wake_word_detector.cleanup()
                terminal_ui.show_component_status("Wake Word Detector", "cleaned up", True)
                logger.info("✅ Wake word detector cleaned up")
            except Exception as e:
                terminal_ui.show_component_status("Wake Word Detector", f"error: {str(e)}", False)
                logger.error(f"Error cleaning up wake word detector: {str(e)}")

        if self.conversation_manager:
            try:
                self.conversation_manager.reset_conversation()
                terminal_ui.show_component_status("Conversation Manager", "cleaned up", True)
                logger.info("✅ Conversation manager cleaned up")
            except Exception as e:
                terminal_ui.show_component_status("Conversation Manager", f"error: {str(e)}", False)
                logger.error(f"Error cleaning up conversation manager: {str(e)}")

        if self.agent:
            try:
                self.agent.cleanup()
                terminal_ui.show_component_status("AI Agent", "cleaned up", True)
                logger.info("✅ AI agent cleaned up")
            except Exception as e:
                terminal_ui.show_component_status("AI Agent", f"error: {str(e)}", False)
                logger.error(f"Error cleaning up agent: {str(e)}")

        if self.speech_manager:
            try:
                self.speech_manager.cleanup()
                terminal_ui.show_component_status("Speech Manager", "cleaned up", True)
                logger.info("✅ Speech manager cleaned up")
            except Exception as e:
                terminal_ui.show_component_status("Speech Manager", f"error: {str(e)}", False)
                logger.error(f"Error cleaning up speech manager: {str(e)}")

        # Cleanup MCP system
        try:
            from .tools import stop_mcp_system
            if stop_mcp_system():
                terminal_ui.show_component_status("MCP System", "cleaned up", True)
                logger.info("✅ MCP system cleaned up")
            else:
                terminal_ui.show_component_status("MCP System", "cleanup failed", False)
        except Exception as e:
            terminal_ui.show_component_status("MCP System", f"error: {str(e)}", False)
            logger.error(f"Error cleaning up MCP system: {str(e)}")

        terminal_ui.show_shutdown_complete()
        logger.info("👋 Jarvis shutdown complete")


def main() -> int:
    """
    Main synchronous entry point for the Jarvis Voice Assistant.
    Manages the asyncio event loop in a background thread.
    """
    loop = None
    app = None
    try:
        # Clear any cached configuration to ensure fresh load
        clear_config_cache()

        # Load config to set up logging
        config = get_config()
        setup_logging(config.logging, clean_console=True)
        setup_exception_logging()

        logger.info("Starting Jarvis Voice Assistant")

        # Create and start the single, persistent event loop in a background thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        loop_thread = threading.Thread(target=loop.run_forever, daemon=True)
        loop_thread.start()

        logger.info("🚀 Persistent event loop started in background thread.")

        # Create the application instance
        app = JarvisApplication()

        # Pass the running loop to the application for its components to use
        app.set_event_loop(loop)

        # Run initialization on the background loop and wait for it to complete
        logger.info("🤖 Submitting initialization task to event loop...")
        init_future = asyncio.run_coroutine_threadsafe(app.initialize(), loop)
        init_future.result()  # Wait for initialization to finish
        logger.info("✅ Initialization complete.")

        # Set up emergency stop system in main thread (signal handlers must be in main thread)
        logger.info("🛑 Setting up emergency stop system in main thread...")
        setup_emergency_stop(
            speech_manager=app.speech_manager,
            agent=app.agent,
            conversation_manager=app.conversation_manager,
            tts_manager=getattr(app.speech_manager, 'tts_manager', None)
        )
        logger.info("✅ Emergency stop system activated")

        # Check if we should run tests first
        if config.general.debug:
            logger.info("Debug mode enabled, running component tests...")
            if not app.test_components():
                logger.error("Component tests failed")
                return 1

        # Now that initialization is done, run the main synchronous loop
        app.run()

        return 0

    except KeyboardInterrupt:
        logger.info("Application interrupted by user.")
        return 0
    except Exception as e:
        logger.critical(f"A critical error occurred: {e}", exc_info=True)
        return 1
    finally:
        logger.info("🛑 Shutting down application...")
        if app and loop and loop.is_running():
            # Submit the async shutdown task to the loop
            shutdown_future = asyncio.run_coroutine_threadsafe(app.shutdown_async(), loop)
            try:
                shutdown_future.result(timeout=10) # Wait for shutdown to complete
            except Exception as e:
                logger.error(f"Error during async shutdown: {e}")

            # Stop the event loop
            loop.call_soon_threadsafe(loop.stop)
        logger.info("👋 Jarvis shutdown complete.")


if __name__ == "__main__":
    sys.exit(main())
