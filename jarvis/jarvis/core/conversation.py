"""
Conversation management for Jarvis Voice Assistant.

This module handles conversation flow, state management, and coordination
between speech recognition, LLM processing, and text-to-speech output.
"""

import logging
import time
import threading
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, Callable, List
from enum import Enum

from ..config import ConversationConfig
from ..exceptions import ConversationError, ConversationTimeoutError
from .speech import SpeechManager
from .agent import JarvisAgent
from .visual_feedback import feedback_manager, FeedbackStatus
from .confidence import confidence_manager
from ..utils.terminal_ui import terminal_ui, StatusType
from ..utils.text_preprocessor import clean_text_for_tts


logger = logging.getLogger(__name__)


class ConversationState(Enum):
    """Enumeration of conversation states."""
    IDLE = "idle"
    LISTENING_FOR_WAKE_WORD = "listening_for_wake_word"
    WAKE_WORD_DETECTED = "wake_word_detected"
    LISTENING_FOR_COMMAND = "listening_for_command"
    PROCESSING_COMMAND = "processing_command"
    RESPONDING = "responding"
    ERROR = "error"


class ConversationManager:
    """
    Manages conversation flow for the Jarvis voice assistant.
    
    This class coordinates the entire conversation lifecycle from wake word
    detection through command processing and response generation.
    """
    
    def __init__(self, config: ConversationConfig, speech_manager: SpeechManager, agent: JarvisAgent, mcp_client=None):
        """
        Initialize the conversation manager.

        Args:
            config: Conversation configuration settings
            speech_manager: Speech management instance
            agent: LLM agent instance
            mcp_client: MCP client for event loop access (optional)
        """
        self.config = config
        self.speech_manager = speech_manager
        self.agent = agent
        self.mcp_client = mcp_client
        
        self.state = ConversationState.IDLE
        self.last_activity_time = time.time()
        self.conversation_active = False
        self.retry_count = 0

        # TTS state tracking (simplified - no full-duplex)
        self._speaking = False

        # Audio isolation support
        self._tts_active = False  # Flag to prevent processing during TTS

        # Callbacks for state changes
        self.state_change_callbacks: Dict[ConversationState, Callable] = {}

        # Chat session persistence
        self.current_session_id: Optional[str] = None
        self.chat_history: List[Dict[str, Any]] = []
        self.chat_history_enabled = config.chat_history_enabled
        self.chat_history_path = config.chat_history_path
        self.auto_save_sessions = config.auto_save_sessions
        self.max_session_history = config.max_session_history
        self.auto_start_session = config.auto_start_session

        # Create chat history directory if enabled
        if self.chat_history_enabled:
            self.chat_history_path.mkdir(parents=True, exist_ok=True)

        logger.info(f"ConversationManager initialized with config: {config}")
    
    def is_initialized(self) -> bool:
        """
        Check if the conversation manager is ready.
        
        Returns:
            True if all components are initialized, False otherwise
        """
        return (self.speech_manager.is_initialized() and 
                self.agent.is_initialized())
    
    def set_state_callback(self, state: ConversationState, callback: Callable) -> None:
        """
        Set a callback function for state changes.
        
        Args:
            state: The state to monitor
            callback: Function to call when entering this state
        """
        self.state_change_callbacks[state] = callback
        logger.debug(f"Set callback for state: {state}")
    
    def _change_state(self, new_state: ConversationState) -> None:
        """
        Change the conversation state and trigger callbacks.
        
        Args:
            new_state: The new state to transition to
        """
        if self.state != new_state:
            old_state = self.state
            self.state = new_state
            self.last_activity_time = time.time()
            
            logger.debug(f"State changed: {old_state} -> {new_state}")
            
            # Trigger callback if registered
            if new_state in self.state_change_callbacks:
                try:
                    self.state_change_callbacks[new_state]()
                except Exception as e:
                    logger.error(f"Error in state callback for {new_state}: {str(e)}")
    
    def start_listening(self) -> None:
        """
        Start listening for wake word.
        
        Raises:
            ConversationError: If conversation manager is not initialized
        """
        if not self.is_initialized():
            raise ConversationError("ConversationManager not initialized")
        
        logger.info("Starting conversation listening mode")
        self._change_state(ConversationState.LISTENING_FOR_WAKE_WORD)
        self.conversation_active = False
        self.retry_count = 0
    
    def stop_listening(self) -> None:
        """Stop all conversation activities."""
        logger.info("Stopping conversation listening mode")
        self._change_state(ConversationState.IDLE)
        self.conversation_active = False
        self.speech_manager.stop_speaking()
    
    def listen_for_wake_word(self, wake_word: Optional[str] = None) -> bool:
        """
        Listen for the wake word.
        
        Args:
            wake_word: Wake word to listen for (uses config default if None)
            
        Returns:
            True if wake word detected, False otherwise
            
        Raises:
            ConversationError: If listening fails
        """
        wake_word = wake_word or self.config.wake_word
        
        try:
            self._change_state(ConversationState.LISTENING_FOR_WAKE_WORD)
            feedback_manager.show_status(FeedbackStatus.LISTENING_WAKE_WORD)

            # Listen for speech
            text = self.speech_manager.listen_for_speech(
                timeout=2.0,
                phrase_time_limit=4.0
            )

            if text and wake_word.lower() in text.lower():
                logger.info(f"Wake word '{wake_word}' detected in: '{text}'")
                self._change_state(ConversationState.WAKE_WORD_DETECTED)
                feedback_manager.show_status(FeedbackStatus.WAKE_WORD_DETECTED, "Wake word detected!")
                time.sleep(0.5)  # Brief pause to show the status
                return True
            elif text:
                logger.debug(f"Speech detected but no wake word: '{text}'")

            return False

        except Exception as e:
            logger.error(f"Error listening for wake word: {str(e)}")
            self._change_state(ConversationState.ERROR)
            feedback_manager.show_status(FeedbackStatus.ERROR, "Wake word detection error")
            return False
    
    def enter_conversation_mode(self) -> None:
        """
        Enter active conversation mode after wake word detection.

        Raises:
            ConversationError: If entering conversation mode fails
        """
        try:
            logger.info("Entering conversation mode")
            terminal_ui.show_clean_conversation_start(terminal_ui.conversation_count + 1)
            terminal_ui.conversation_count += 1
            self.conversation_active = True
            self.retry_count = 0
            self.last_activity_time = time.time()

            # Clear short-term chat memory for new conversation session
            if hasattr(self.agent, 'clear_chat_memory'):
                self.agent.clear_chat_memory()

            # Acknowledge wake word
            terminal_ui.show_status(StatusType.SPEAKING, "Acknowledging wake word...")
            self.speech_manager.speak_text("Yes sir?")

            self._change_state(ConversationState.LISTENING_FOR_COMMAND)

        except Exception as e:
            error_msg = f"Failed to enter conversation mode: {str(e)}"
            logger.error(error_msg)
            self._change_state(ConversationState.ERROR)
            raise ConversationError(error_msg) from e
    
    def listen_for_command(self) -> Optional[str]:
        """
        Listen for a user command during conversation.
        
        Returns:
            User command text or None if no command received
            
        Raises:
            ConversationTimeoutError: If conversation times out
            ConversationError: If listening fails
        """
        try:
            self._change_state(ConversationState.LISTENING_FOR_COMMAND)
            feedback_manager.show_status(FeedbackStatus.LISTENING_COMMAND)

            # Check for timeout
            if time.time() - self.last_activity_time > self.config.conversation_timeout:
                logger.info("Conversation timeout reached")
                raise ConversationTimeoutError(
                    "Conversation timed out",
                    timeout_seconds=self.config.conversation_timeout
                )

            # Listen for command with conversation-optimized settings
            with self.speech_manager.conversation_mode():
                command = self.speech_manager.listen_for_speech(
                    timeout=5.0,
                    phrase_time_limit=8.0
                )

            if command:
                # DEBUG: Show that we got a command
                print(f"DEBUG: Speech recognition got command: '{command}'")

                # Analyze confidence in the recognized command
                confidence_result = confidence_manager.analyze_confidence(command)

                # Show confidence feedback
                feedback_manager.show_confidence(
                    FeedbackStatus.PROCESSING,
                    confidence_result.confidence,
                    f"Heard: '{command}'"
                )

                # Skip if just wake word again
                if command.lower().strip() == self.config.wake_word.lower():
                    logger.debug("Wake word repeated, waiting for actual command")
                    return None

                # Handle low confidence
                if confidence_manager.should_ask_for_clarification(confidence_result):
                    clarification = confidence_manager.format_clarification_request(confidence_result)
                    feedback_manager.show_status(FeedbackStatus.ERROR, clarification)
                    logger.warning(f"Low confidence ({confidence_result.confidence:.2f}) for: '{command}'")
                    # Still return the command but log the low confidence

                # CRITICAL: Filter out TTS audio feedback to prevent infinite loops
                if self._tts_active:
                    logger.debug(f"Ignoring command during TTS: '{command}' (TTS feedback prevention)")
                    return None

                logger.info(f"Command received: '{command}' (confidence: {confidence_result.confidence:.2f})")
                terminal_ui.show_user_input(command, confidence_result.confidence)
                self.last_activity_time = time.time()
                self.retry_count = 0
                return command
            else:
                logger.debug("No command received")
                return None
                
        except ConversationTimeoutError:
            self._change_state(ConversationState.IDLE)
            self.conversation_active = False
            raise
        except Exception as e:
            logger.error(f"Error listening for command: {str(e)}")
            self._change_state(ConversationState.ERROR)
            raise ConversationError(f"Failed to listen for command: {str(e)}") from e
    
    def process_command(self, command: str) -> str:
        """
        Process a user command using the LLM agent.

        Args:
            command: User command to process

        Returns:
            Agent response text

        Raises:
            ConversationError: If command processing fails
        """
        try:
            self._change_state(ConversationState.PROCESSING_COMMAND)
            feedback_manager.show_status(FeedbackStatus.THINKING, f"Processing: '{command[:30]}...'")
            terminal_ui.show_status(StatusType.THINKING, f"Processing: '{command[:30]}...'")
            logger.info(f"Processing command: '{command}'")

            # Process with agent using MCP client's event loop
            start_time = time.time()
            import asyncio

            try:
                logger.info("🔍 CONVERSATION DEBUG: Submitting agent task to event loop...")
                if self.mcp_client and hasattr(self.mcp_client, 'loop') and self.mcp_client.loop:
                    # Use the application's single, persistent event loop
                    app_loop = self.mcp_client.loop
                    logger.info("🔍 CONVERSATION DEBUG: Using persistent event loop from MCP manager")

                    future = asyncio.run_coroutine_threadsafe(
                        self.agent.process_input(command),
                        app_loop
                    )
                    response = future.result(timeout=30.0)  # Wait for the result
                    logger.info(f"🔍 CONVERSATION DEBUG: Persistent loop returned: '{response[:200]}{'...' if len(response) > 200 else ''}'")
                else:
                    # Fallback: MCP client not available, run in new event loop
                    logger.info("🔍 CONVERSATION DEBUG: MCP client not available, using fallback event loop")
                    try:
                        # Try to get existing event loop
                        current_loop = asyncio.get_event_loop()
                        if current_loop.is_running():
                            # We're in an event loop, use thread executor
                            import concurrent.futures
                            with concurrent.futures.ThreadPoolExecutor() as executor:
                                future = executor.submit(asyncio.run, self.agent.process_input(command))
                                response = future.result(timeout=30.0)
                        else:
                            # No running loop, use it directly
                            response = current_loop.run_until_complete(self.agent.process_input(command))
                    except RuntimeError:
                        # No event loop exists, create new one
                        logger.info("🔍 CONVERSATION DEBUG: Creating new event loop for agent processing")
                        response = asyncio.run(self.agent.process_input(command))

                    logger.info(f"🔍 CONVERSATION DEBUG: Fallback loop returned: '{response[:200]}{'...' if len(response) > 200 else ''}'")

            except asyncio.TimeoutError:
                logger.error("🔍 CONVERSATION DEBUG: Agent processing timed out after 30 seconds")
                response = "I'm sorry, that request took too long to process. Please try again."
            except Exception as e:
                logger.error(f"🔍 CONVERSATION DEBUG: Agent processing failed: {e}", exc_info=True)
                response = f"I encountered an error processing that request."

            processing_time = time.time() - start_time
            logger.info(f"🔍 CONVERSATION DEBUG: Total processing time: {processing_time:.2f}s")

            feedback_manager.show_status(FeedbackStatus.SPEAKING, "Generating response...")
            terminal_ui.show_jarvis_response(response, processing_time)
            logger.info(f"Agent response: '{response[:100]}{'...' if len(response) > 100 else ''}'")

            # Add to chat history
            self.add_to_chat_history(
                user_input=command,
                assistant_response=response,
                metadata={
                    "processing_time": processing_time,
                    "timestamp": datetime.now().isoformat()
                }
            )

            return response

        except Exception as e:
            error_msg = f"Failed to process command: {str(e)}"
            logger.error(error_msg)
            self._change_state(ConversationState.ERROR)
            raise ConversationError(error_msg) from e
    
    def respond(self, response_text: str) -> None:
        """
        Deliver response to user via text-to-speech.
        
        Args:
            response_text: Text to speak to user
            
        Raises:
            ConversationError: If response delivery fails
        """
        try:
            self._change_state(ConversationState.RESPONDING)
            logger.debug(f"Responding: '{response_text[:100]}{'...' if len(response_text) > 100 else ''}'")

            self.last_activity_time = time.time()

            # Return to listening for next command
            self._change_state(ConversationState.LISTENING_FOR_COMMAND)

            # Simple TTS mode with audio isolation (no full-duplex)
            logger.debug("Starting TTS with audio isolation")

            # CRITICAL: Set flag to prevent processing TTS audio as user input
            self._tts_active = True
            self._speaking = True

            # Speak the response with blocking wait
            logger.debug(f"🔊 CONVERSATION: Starting TTS for: '{response_text[:50]}{'...' if len(response_text) > 50 else ''}'")
            logger.debug(f"🔊 CONVERSATION: TTS flags before - _tts_active: {self._tts_active}, _speaking: {self._speaking}")

            # Clean text for TTS (remove markdown formatting, etc.)
            cleaned_text = clean_text_for_tts(response_text)
            logger.debug(f"TTS text cleaned: '{response_text[:50]}...' -> '{cleaned_text[:50]}...'")

            tts_start_time = time.time()
            try:
                self.speech_manager.speak_text(cleaned_text, wait=True)
                tts_end_time = time.time()
                tts_duration = tts_end_time - tts_start_time
                logger.debug(f"🔊 CONVERSATION: TTS completed successfully in {tts_duration:.2f} seconds")
            except Exception as tts_error:
                tts_end_time = time.time()
                tts_duration = tts_end_time - tts_start_time
                logger.error(f"🔊 CONVERSATION: TTS FAILED after {tts_duration:.2f} seconds: {tts_error}")
                # Re-raise to ensure the error is handled properly
                raise
            finally:
                # Always clear flags even if TTS fails
                self._tts_active = False
                self._speaking = False
                logger.debug(f"🔊 CONVERSATION: TTS flags cleared - _tts_active: {self._tts_active}, _speaking: {self._speaking}")

            # Wait for audio system to settle and clear any residual audio
            time.sleep(0.5)

            logger.debug("Response delivered with audio isolation, ready for next command")
            
        except Exception as e:
            error_msg = f"Failed to deliver response: {str(e)}"
            logger.error(error_msg)
            self._change_state(ConversationState.ERROR)
            raise ConversationError(error_msg) from e
    
    def handle_conversation_cycle(self) -> bool:
        """
        Handle one complete conversation cycle (listen -> process -> respond).

        Returns:
            True if conversation should continue, False if it should end

        Raises:
            ConversationError: If conversation cycle fails
        """
        try:
            # Listen for command
            command = self.listen_for_command()

            if command:
                # Process command (sync wrapper for async agent)
                response = self.process_command(command)

                # Deliver response
                self.respond(response)

                return True  # Continue conversation
            else:
                # No command received, check for timeout
                if time.time() - self.last_activity_time > self.config.conversation_timeout:
                    logger.info("Conversation timeout, ending conversation")
                    terminal_ui.show_clean_conversation_end("timeout")
                    self.conversation_active = False
                    return False
                else:
                    return True  # Continue listening

        except ConversationTimeoutError:
            logger.info("Conversation ended due to timeout")
            terminal_ui.show_clean_conversation_end("timeout")
            self.conversation_active = False
            return False
        except Exception as e:
            self.retry_count += 1
            
            if self.retry_count >= self.config.max_retries:
                logger.error(f"Max retries reached, ending conversation: {str(e)}")
                self.conversation_active = False
                try:
                    self.speech_manager.speak_text("I'm having trouble understanding. Let's try again later.")
                except Exception as tts_error:
                    logger.error(f"TTS failed during error recovery: {tts_error}")
                    # Don't pass silently - this helps identify TTS issues
                return False
            else:
                logger.warning(f"Conversation error (retry {self.retry_count}): {str(e)}")
                try:
                    self.speech_manager.speak_text("I didn't catch that. Could you please repeat?")
                except Exception as tts_error:
                    logger.error(f"TTS failed during retry: {tts_error}")
                    # Don't pass silently - this helps identify TTS issues
                return True
    
    def get_conversation_state(self) -> Dict[str, Any]:
        """
        Get current conversation state information.
        
        Returns:
            Dictionary containing state information
        """
        return {
            "state": self.state.value,
            "conversation_active": self.conversation_active,
            "last_activity_time": self.last_activity_time,
            "time_since_activity": time.time() - self.last_activity_time,
            "retry_count": self.retry_count,
            "timeout_remaining": max(0, self.config.conversation_timeout - (time.time() - self.last_activity_time)),
            "wake_word": self.config.wake_word,
            "max_retries": self.config.max_retries
        }
    
    def reset_conversation(self) -> None:
        """Reset conversation state to initial conditions."""
        logger.info("Resetting conversation state")
        self._change_state(ConversationState.IDLE)
        self.conversation_active = False
        self.retry_count = 0
        self.last_activity_time = time.time()
        self.speech_manager.stop_speaking()

        # Clear short-term chat memory when resetting conversation
        if hasattr(self.agent, 'clear_chat_memory'):
            self.agent.clear_chat_memory()

        # Clear TTS flags
        self._tts_active = False
        self._speaking = False

    # Chat Session Persistence Methods

    def start_new_session(self, session_name: Optional[str] = None) -> str:
        """
        Start a new chat session.

        Args:
            session_name: Optional custom name for the session

        Returns:
            str: Session ID
        """
        # Save current session if exists
        if self.current_session_id and self.chat_history:
            self.save_chat_history()

        # Create new session
        self.current_session_id = str(uuid.uuid4())
        self.chat_history = []

        # Create session metadata
        session_metadata = {
            "session_id": self.current_session_id,
            "name": session_name or f"Chat Session {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat()
        }

        logger.info(f"Started new chat session: {self.current_session_id}")
        return self.current_session_id

    def add_to_chat_history(self, user_input: str, assistant_response: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Add an exchange to the current chat history.

        Args:
            user_input: User's input message
            assistant_response: Assistant's response
            metadata: Optional metadata for the exchange
        """
        # Skip if chat history is disabled
        if not self.chat_history_enabled:
            return

        # Auto-start session if enabled and no current session
        if not self.current_session_id and self.auto_start_session:
            self.start_new_session()
        elif not self.current_session_id:
            return  # No session and auto-start disabled

        exchange = {
            "timestamp": datetime.now().isoformat(),
            "user_input": user_input,
            "assistant_response": assistant_response,
            "metadata": metadata or {}
        }

        self.chat_history.append(exchange)
        logger.debug(f"Added exchange to chat history (session: {self.current_session_id})")

        # Auto-save if enabled
        if self.auto_save_sessions and len(self.chat_history) % 5 == 0:  # Save every 5 exchanges
            self.save_chat_history()

    def save_chat_history(self, session_id: Optional[str] = None) -> bool:
        """
        Save current chat history to disk.

        Args:
            session_id: Optional session ID to save (defaults to current session)

        Returns:
            bool: True if saved successfully, False otherwise
        """
        try:
            target_session_id = session_id or self.current_session_id
            if not target_session_id:
                logger.warning("No session ID provided for saving chat history")
                return False

            if not self.chat_history:
                logger.info("No chat history to save")
                return True

            # Create session file
            session_file = self.chat_history_path / f"{target_session_id}.json"

            session_data = {
                "session_id": target_session_id,
                "created_at": self.chat_history[0]["timestamp"] if self.chat_history else datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
                "message_count": len(self.chat_history),
                "chat_history": self.chat_history
            }

            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, indent=2, ensure_ascii=False)

            logger.info(f"Saved chat history for session {target_session_id} ({len(self.chat_history)} messages)")
            return True

        except Exception as e:
            logger.error(f"Failed to save chat history: {e}")
            return False

    def load_chat_history(self, session_id: str) -> bool:
        """
        Load chat history from disk.

        Args:
            session_id: Session ID to load

        Returns:
            bool: True if loaded successfully, False otherwise
        """
        try:
            session_file = self.chat_history_path / f"{session_id}.json"

            if not session_file.exists():
                logger.warning(f"Chat session file not found: {session_id}")
                return False

            with open(session_file, 'r', encoding='utf-8') as f:
                session_data = json.load(f)

            # Save current session if exists
            if self.current_session_id and self.chat_history:
                self.save_chat_history()

            # Load the requested session
            self.current_session_id = session_id
            self.chat_history = session_data.get("chat_history", [])

            logger.info(f"Loaded chat history for session {session_id} ({len(self.chat_history)} messages)")
            return True

        except Exception as e:
            logger.error(f"Failed to load chat history for session {session_id}: {e}")
            return False

    def list_chat_sessions(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        List available chat sessions.

        Args:
            limit: Maximum number of sessions to return

        Returns:
            List of session metadata dictionaries
        """
        try:
            sessions = []

            for session_file in self.chat_history_path.glob("*.json"):
                try:
                    with open(session_file, 'r', encoding='utf-8') as f:
                        session_data = json.load(f)

                    session_info = {
                        "session_id": session_data.get("session_id", session_file.stem),
                        "created_at": session_data.get("created_at", "unknown"),
                        "last_updated": session_data.get("last_updated", "unknown"),
                        "message_count": session_data.get("message_count", len(session_data.get("chat_history", []))),
                        "preview": self._get_session_preview(session_data.get("chat_history", []))
                    }

                    sessions.append(session_info)

                except Exception as e:
                    logger.warning(f"Failed to read session file {session_file}: {e}")
                    continue

            # Sort by last_updated (most recent first)
            sessions.sort(key=lambda x: x["last_updated"], reverse=True)

            return sessions[:limit]

        except Exception as e:
            logger.error(f"Failed to list chat sessions: {e}")
            return []

    def _get_session_preview(self, chat_history: List[Dict[str, Any]]) -> str:
        """
        Generate a preview of the chat session.

        Args:
            chat_history: List of chat exchanges

        Returns:
            str: Preview text
        """
        if not chat_history:
            return "Empty session"

        # Get first user message as preview
        first_exchange = chat_history[0]
        user_input = first_exchange.get("user_input", "")

        if len(user_input) > 50:
            return user_input[:47] + "..."

        return user_input or "No preview available"

    def delete_chat_session(self, session_id: str) -> bool:
        """
        Delete a chat session.

        Args:
            session_id: Session ID to delete

        Returns:
            bool: True if deleted successfully, False otherwise
        """
        try:
            session_file = self.chat_history_path / f"{session_id}.json"

            if not session_file.exists():
                logger.warning(f"Chat session file not found: {session_id}")
                return False

            session_file.unlink()

            # If this is the current session, clear it
            if self.current_session_id == session_id:
                self.current_session_id = None
                self.chat_history = []

            logger.info(f"Deleted chat session: {session_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to delete chat session {session_id}: {e}")
            return False

    def cleanup_old_sessions(self) -> Dict[str, Any]:
        """
        Clean up old chat sessions based on configuration settings.

        Returns:
            dict: Cleanup results with statistics
        """
        if not self.chat_history_enabled:
            return {"status": "disabled", "message": "Chat history is disabled"}

        try:
            sessions = self.list_chat_sessions(limit=1000)  # Get all sessions

            # Sort by last_updated (oldest first)
            sessions.sort(key=lambda x: x.get("last_updated", ""), reverse=False)

            deleted_count = 0
            cleanup_results = {
                "status": "success",
                "total_sessions": len(sessions),
                "deleted_count": 0,
                "kept_count": 0,
                "errors": []
            }

            # Delete sessions beyond max_session_history limit
            if len(sessions) > self.max_session_history:
                excess_sessions = sessions[:-self.max_session_history]

                for session in excess_sessions:
                    try:
                        if self.delete_chat_session(session["session_id"]):
                            deleted_count += 1
                        else:
                            cleanup_results["errors"].append(f"Failed to delete session {session['session_id'][:8]}...")
                    except Exception as e:
                        cleanup_results["errors"].append(f"Error deleting session {session['session_id'][:8]}...: {e}")

            # Delete sessions older than cleanup_days (if configured)
            if hasattr(self.config, 'session_cleanup_days') and self.config.session_cleanup_days > 0:
                from datetime import datetime, timedelta
                cutoff_date = datetime.now() - timedelta(days=self.config.session_cleanup_days)

                for session in sessions:
                    try:
                        last_updated = session.get("last_updated", "")
                        if last_updated:
                            session_date = datetime.fromisoformat(last_updated.replace('Z', '+00:00'))
                            if session_date < cutoff_date:
                                if self.delete_chat_session(session["session_id"]):
                                    deleted_count += 1
                                else:
                                    cleanup_results["errors"].append(f"Failed to delete old session {session['session_id'][:8]}...")
                    except Exception as e:
                        cleanup_results["errors"].append(f"Error processing session date {session['session_id'][:8]}...: {e}")

            cleanup_results["deleted_count"] = deleted_count
            cleanup_results["kept_count"] = len(sessions) - deleted_count

            if deleted_count > 0:
                logger.info(f"Cleaned up {deleted_count} old chat sessions")

            return cleanup_results

        except Exception as e:
            logger.error(f"Failed to cleanup old sessions: {e}")
            return {
                "status": "error",
                "message": str(e),
                "deleted_count": 0,
                "kept_count": 0,
                "errors": [str(e)]
            }




