"""
Emergency Stop System for Jarvis Voice Assistant

Provides reliable hotkey-based stop functionality that works during:
- TTS playback
- LLM processing
- Audio recording
- Any other system state

Author: Jarvis Team
"""

import logging
import signal
import sys
import threading
from typing import Optional, Callable

logger = logging.getLogger(__name__)

class EmergencyStopManager:
    """
    Manages emergency stop functionality with multiple trigger methods.
    """
    
    def __init__(self):
        self.stop_callbacks = []
        self.is_stopping = False
        self._keyboard_available = False

        # Note: Keyboard library requires admin privileges on macOS
        # We'll focus on the enhanced Ctrl+C functionality instead
        logger.info("Emergency stop manager initialized - using enhanced Ctrl+C")
    
    def add_stop_callback(self, callback: Callable[[], None]) -> None:
        """
        Add a callback to be executed when emergency stop is triggered.
        
        Args:
            callback: Function to call during emergency stop
        """
        self.stop_callbacks.append(callback)
        logger.debug(f"Added stop callback: {callback.__name__}")
    
    def setup_signal_handlers(self) -> None:
        """Setup enhanced Ctrl+C handling."""
        def signal_handler(signum, frame):
            self._execute_emergency_stop("Ctrl+C")
        
        signal.signal(signal.SIGINT, signal_handler)
        if hasattr(signal, 'SIGTERM'):
            signal.signal(signal.SIGTERM, signal_handler)
        
        logger.info("Enhanced signal handlers setup (Ctrl+C)")
    
    def setup_hotkeys(self) -> None:
        """Setup additional hotkey combinations (disabled for compatibility)."""
        # Note: Keyboard library requires admin privileges on macOS and can be unreliable
        # We focus on the enhanced Ctrl+C functionality which is more reliable
        logger.info("Using enhanced Ctrl+C for emergency stop (most reliable)")
    
    def _execute_emergency_stop(self, trigger: str) -> None:
        """
        Execute emergency stop sequence.
        
        Args:
            trigger: What triggered the stop (for logging)
        """
        if self.is_stopping:
            return  # Prevent multiple simultaneous stops
        
        self.is_stopping = True
        
        # Import here to avoid circular imports
        try:
            from ..utils.terminal_ui import terminal_ui
            terminal_ui.show_emergency_stop()
        except ImportError:
            print(f"\n🛑 EMERGENCY STOP ACTIVATED ({trigger})")

        logger.info(f"Emergency stop triggered by: {trigger}")

        # Execute all registered callbacks
        for callback in self.stop_callbacks:
            try:
                callback()
                logger.debug(f"Executed stop callback: {callback.__name__}")
            except Exception as e:
                logger.error(f"Stop callback failed: {callback.__name__} - {e}")

        logger.info("Emergency stop completed")
        
        # Force exit after brief delay
        threading.Timer(1.0, lambda: sys.exit(0)).start()
    
    def register_with_components(self, speech_manager=None, agent=None, 
                                conversation_manager=None, tts_manager=None) -> None:
        """
        Register stop callbacks with major Jarvis components.
        
        Args:
            speech_manager: SpeechManager instance
            agent: JarvisAgent instance  
            conversation_manager: ConversationManager instance
            tts_manager: TextToSpeechManager instance
        """
        if speech_manager:
            self.add_stop_callback(lambda: self._stop_speech_manager(speech_manager))
        
        if agent:
            self.add_stop_callback(lambda: self._stop_agent(agent))
        
        if conversation_manager:
            self.add_stop_callback(lambda: self._stop_conversation_manager(conversation_manager))
        
        if tts_manager:
            self.add_stop_callback(lambda: self._stop_tts_manager(tts_manager))
        
        logger.info(f"Registered stop callbacks for {len(self.stop_callbacks)} components")
    
    def _stop_speech_manager(self, speech_manager) -> None:
        """Stop speech manager operations."""
        try:
            if hasattr(speech_manager, 'stop_listening'):
                speech_manager.stop_listening()
            if hasattr(speech_manager, 'stop_speaking'):
                speech_manager.stop_speaking()
            logger.debug("Speech manager stopped")
        except Exception as e:
            logger.error(f"Failed to stop speech manager: {e}")
    
    def _stop_agent(self, agent) -> None:
        """Stop LLM agent processing."""
        try:
            if hasattr(agent, 'cleanup'):
                agent.cleanup()
            logger.debug("Agent stopped")
        except Exception as e:
            logger.error(f"Failed to stop agent: {e}")
    
    def _stop_conversation_manager(self, conversation_manager) -> None:
        """Stop conversation manager."""
        try:
            if hasattr(conversation_manager, 'stop'):
                conversation_manager.stop()
            logger.debug("Conversation manager stopped")
        except Exception as e:
            logger.error(f"Failed to stop conversation manager: {e}")
    
    def _stop_tts_manager(self, tts_manager) -> None:
        """Stop TTS operations immediately."""
        try:
            if hasattr(tts_manager, 'stop_speaking'):
                tts_manager.stop_speaking()
            if hasattr(tts_manager, 'interrupt'):
                tts_manager.interrupt()
            logger.debug("TTS manager stopped")
        except Exception as e:
            logger.error(f"Failed to stop TTS manager: {e}")

# Global instance
_emergency_stop_manager: Optional[EmergencyStopManager] = None

def get_emergency_stop_manager() -> EmergencyStopManager:
    """Get the global emergency stop manager instance."""
    global _emergency_stop_manager
    if _emergency_stop_manager is None:
        _emergency_stop_manager = EmergencyStopManager()
    return _emergency_stop_manager

def setup_emergency_stop(speech_manager=None, agent=None, 
                        conversation_manager=None, tts_manager=None) -> EmergencyStopManager:
    """
    Setup complete emergency stop system.
    
    Args:
        speech_manager: SpeechManager instance
        agent: JarvisAgent instance
        conversation_manager: ConversationManager instance
        tts_manager: TextToSpeechManager instance
    
    Returns:
        EmergencyStopManager instance
    """
    manager = get_emergency_stop_manager()
    
    # Setup all stop mechanisms
    manager.setup_signal_handlers()
    manager.setup_hotkeys()
    
    # Register component callbacks
    manager.register_with_components(
        speech_manager=speech_manager,
        agent=agent,
        conversation_manager=conversation_manager,
        tts_manager=tts_manager
    )
    
    # Emergency stop system is now active (silent setup)
    
    return manager
