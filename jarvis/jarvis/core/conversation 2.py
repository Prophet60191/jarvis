"""
Conversation management for Jarvis Voice Assistant.

This module handles conversation flow, state management, and coordination
between speech recognition, LLM processing, and text-to-speech output.
"""

import logging
import time
import threading
from typing import Optional, Dict, Any, Callable
from enum import Enum

from ..config import ConversationConfig
from ..exceptions import ConversationError, ConversationTimeoutError
from .speech import SpeechManager
from .agent import JarvisAgent
from .visual_feedback import feedback_manager, FeedbackStatus
from .confidence import confidence_manager
from ..utils.terminal_ui import terminal_ui, StatusType


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
    
    def __init__(self, config: ConversationConfig, speech_manager: SpeechManager, agent: JarvisAgent):
        """
        Initialize the conversation manager.
        
        Args:
            config: Conversation configuration settings
            speech_manager: Speech management instance
            agent: LLM agent instance
        """
        self.config = config
        self.speech_manager = speech_manager
        self.agent = agent
        
        self.state = ConversationState.IDLE
        self.last_activity_time = time.time()
        self.conversation_active = False
        self.retry_count = 0

        # Full-duplex conversation support
        self._speaking = False
        self._listening_thread = None
        self._stop_listening = threading.Event()
        self._current_response = None

        # Audio isolation support
        self._tts_active = False  # Flag to prevent processing during TTS

        # Callbacks for state changes
        self.state_change_callbacks: Dict[ConversationState, Callable] = {}
        
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
            terminal_ui.show_conversation_start()
            self.conversation_active = True
            self.retry_count = 0
            self.last_activity_time = time.time()

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

            # Process with agent
            start_time = time.time()
            response = self.agent.process_input(command)
            processing_time = time.time() - start_time

            feedback_manager.show_status(FeedbackStatus.SPEAKING, "Generating response...")
            terminal_ui.show_jarvis_response(response, processing_time)
            logger.info(f"Agent response: '{response[:100]}{'...' if len(response) > 100 else ''}'")
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

            # Choose response mode based on configuration
            if self.config.enable_full_duplex:
                # Start full-duplex mode: speak while listening for interruptions
                self._start_full_duplex_response(response_text)
            else:
                # Traditional mode with audio isolation: speak then listen
                logger.debug("Starting TTS with audio isolation")

                # CRITICAL: Set flag to prevent processing TTS audio as user input
                self._tts_active = True

                # Speak the response with blocking wait
                logger.debug(f"🔊 Starting TTS for: '{response_text[:50]}{'...' if len(response_text) > 50 else ''}'")
                try:
                    self.speech_manager.speak_text(response_text, wait=True)
                    logger.debug("🔊 TTS completed successfully")
                except Exception as tts_error:
                    logger.error(f"🔊 TTS FAILED: {tts_error}")
                    # Re-raise to ensure the error is handled properly
                    raise

                # Wait for audio system to settle and clear any residual audio
                time.sleep(0.5)  # Reduced delay - was too long and might cause issues

                # Clear the TTS flag
                self._tts_active = False

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
                # Process command
                response = self.process_command(command)
                
                # Deliver response
                self.respond(response)
                
                return True  # Continue conversation
            else:
                # No command received, check for timeout
                if time.time() - self.last_activity_time > self.config.conversation_timeout:
                    logger.info("Conversation timeout, ending conversation")
                    terminal_ui.show_conversation_end("timeout")
                    self.conversation_active = False
                    return False
                else:
                    return True  # Continue listening
                    
        except ConversationTimeoutError:
            logger.info("Conversation ended due to timeout")
            terminal_ui.show_conversation_end("timeout")
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

        # Stop any full-duplex operations
        self._stop_full_duplex()

        # Clear TTS flag
        self._tts_active = False

    def _start_full_duplex_response(self, response_text: str) -> None:
        """
        Start full-duplex response: speak while listening for interruptions.

        Args:
            response_text: Text to speak
        """
        try:
            logger.debug("Starting full-duplex response mode")

            # Stop any existing listening thread
            self._stop_full_duplex()

            # Start TTS in async mode (non-blocking)
            self._speaking = True
            self._current_response = response_text

            # Start TTS asynchronously
            try:
                self.speech_manager.speak_text(response_text, wait=False)
                logger.debug("🔊 Full-duplex TTS started successfully")
            except Exception as tts_error:
                logger.error(f"🔊 Full-duplex TTS FAILED: {tts_error}")
                raise

            # Start listening for interruptions in a separate thread
            self._stop_listening.clear()
            self._listening_thread = threading.Thread(
                target=self._listen_for_interruptions,
                daemon=True
            )
            self._listening_thread.start()

            logger.debug("Full-duplex mode started successfully")

        except Exception as e:
            logger.error(f"Failed to start full-duplex response: {e}")
            # Fallback to traditional mode
            self.speech_manager.speak_text(response_text, wait=True)
            self._speaking = False

    def _listen_for_interruptions(self) -> None:
        """
        Listen for user interruptions while TTS is playing.
        Runs in a separate thread.
        """
        try:
            logger.debug("Started listening for interruptions")

            # Wait a short time for TTS to start
            time.sleep(0.5)

            while self._speaking and not self._stop_listening.is_set():
                try:
                    # Listen for speech with short timeout
                    command = self.speech_manager.listen_for_speech(
                        timeout=2.0,  # Increased timeout to reduce false positives
                        phrase_time_limit=4.0,  # Longer phrases for real interruptions
                        enhance_audio=True,
                        recognition_service="whisper"
                    )

                    # Much stricter filtering for real interruptions
                    if (command and
                        len(command.strip()) > 5 and  # Longer minimum length
                        not any(word in command.lower() for word in ['...', '.', 'uh', 'um', 'ah']) and  # Filter noise
                        any(word in command.lower() for word in ['stop', 'wait', 'jarvis', 'hey', 'what', 'how', 'can', 'tell', 'help'])):  # Real command words
                        logger.info(f"Interruption detected: '{command}'")

                        # Stop current TTS
                        self.speech_manager.stop_speaking()
                        self._speaking = False

                        # Process the interruption
                        try:
                            interruption_response = self.process_command(command)
                            # Start new full-duplex response
                            self._start_full_duplex_response(interruption_response)
                        except Exception as e:
                            logger.warning(f"Failed to process interruption: {e}")

                        break

                except Exception as e:
                    # Ignore listening errors (expected when no speech)
                    if "No speech detected" not in str(e):
                        logger.debug(f"Interruption listening error: {e}")

                # Small delay to prevent excessive CPU usage
                time.sleep(0.1)

            # TTS finished naturally
            if self._speaking:
                self._speaking = False
                logger.debug("TTS completed, ready for next command")

        except Exception as e:
            logger.error(f"Error in interruption listening: {e}")
        finally:
            self._speaking = False

    def _stop_full_duplex(self) -> None:
        """Stop full-duplex operations."""
        try:
            self._stop_listening.set()
            self._speaking = False

            if self._listening_thread and self._listening_thread.is_alive():
                self._listening_thread.join(timeout=1.0)

        except Exception as e:
            logger.debug(f"Error stopping full-duplex: {e}")
