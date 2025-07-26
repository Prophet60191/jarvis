"""
Conversation management for Jarvis Voice Assistant.

This module handles conversation flow, state management, and coordination
between speech recognition, LLM processing, and text-to-speech output.
"""

import logging
import time
from typing import Optional, Dict, Any, Callable
from enum import Enum

from ..config import ConversationConfig
from ..exceptions import ConversationError, ConversationTimeoutError
from .speech import SpeechManager
from .agent import JarvisAgent


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
            
            # Listen for speech
            text = self.speech_manager.listen_for_speech(
                timeout=2.0,
                phrase_time_limit=4.0
            )
            
            if text and wake_word.lower() in text.lower():
                logger.info(f"Wake word '{wake_word}' detected in: '{text}'")
                self._change_state(ConversationState.WAKE_WORD_DETECTED)
                return True
            elif text:
                logger.debug(f"Speech detected but no wake word: '{text}'")
            
            return False
            
        except Exception as e:
            logger.error(f"Error listening for wake word: {str(e)}")
            self._change_state(ConversationState.ERROR)
            return False
    
    def enter_conversation_mode(self) -> None:
        """
        Enter active conversation mode after wake word detection.
        
        Raises:
            ConversationError: If entering conversation mode fails
        """
        try:
            logger.info("Entering conversation mode")
            self.conversation_active = True
            self.retry_count = 0
            self.last_activity_time = time.time()
            
            # Acknowledge wake word
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
                # Skip if just wake word again
                if command.lower().strip() == self.config.wake_word.lower():
                    logger.debug("Wake word repeated, waiting for actual command")
                    return None
                
                logger.info(f"Command received: '{command}'")
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
            logger.info(f"Processing command: '{command}'")
            
            # Process with agent
            response = self.agent.process_input(command)
            
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
            
            self.speech_manager.speak_text(response_text)
            self.last_activity_time = time.time()

            # Return to listening for next command
            self._change_state(ConversationState.LISTENING_FOR_COMMAND)

            # Automatically listen for follow-up command for 5 seconds
            logger.debug("Listening for follow-up command (5 seconds)...")
            follow_up_command = self.speech_manager.listen_for_speech(
                timeout=5.0,
                phrase_time_limit=4.0,
                enhance_audio=True,
                recognition_service="whisper"
            )

            if follow_up_command:
                logger.info(f"Follow-up command received: '{follow_up_command}'")
                # Process the follow-up command immediately
                try:
                    follow_up_response = self.process_command(follow_up_command)
                    # Recursively respond (this will also listen for another follow-up)
                    self.respond(follow_up_response)
                except Exception as e:
                    logger.warning(f"Failed to process follow-up command: {e}")
            else:
                logger.debug("No follow-up command received")
            
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
                    self.conversation_active = False
                    return False
                else:
                    return True  # Continue listening
                    
        except ConversationTimeoutError:
            logger.info("Conversation ended due to timeout")
            self.conversation_active = False
            return False
        except Exception as e:
            self.retry_count += 1
            
            if self.retry_count >= self.config.max_retries:
                logger.error(f"Max retries reached, ending conversation: {str(e)}")
                self.conversation_active = False
                try:
                    self.speech_manager.speak_text("I'm having trouble understanding. Let's try again later.")
                except:
                    pass
                return False
            else:
                logger.warning(f"Conversation error (retry {self.retry_count}): {str(e)}")
                try:
                    self.speech_manager.speak_text("I didn't catch that. Could you please repeat?")
                except:
                    pass
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
