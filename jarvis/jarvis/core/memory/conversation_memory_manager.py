#!/usr/bin/env python3
"""
Conversation Memory Manager - Handles conversation context and persistent agent.

SEPARATION OF CONCERNS:
- This module ONLY handles conversation memory and context
- It does NOT handle query processing, tool selection, or performance monitoring
- It provides a clean interface for memory operations

CRITICAL: This preserves wake word functionality by maintaining the same
interface that start_jarvis.py expects.
"""

import logging
import time
from typing import Optional, Dict, Any, List
from datetime import datetime
from .session_models import SessionMessage, SavedSession
from .session_save_manager import get_session_save_manager

logger = logging.getLogger(__name__)


class ConversationMemoryManager:
    """
    Manages conversation memory and persistent agent for context continuity.
    
    SINGLE RESPONSIBILITY: Conversation memory and context tracking only.
    """
    
    def __init__(self):
        """Initialize conversation memory manager."""
        # Conversation state
        self.session_active = False
        self.session_start_time = 0.0
        self.conversation_context = ""
        
        # Persistent agent for memory continuity
        self.persistent_agent = None
        
        # Session statistics (memory-related only)
        self.session_stats = {
            "session_duration": 0.0,
            "exchanges_tracked": 0,
            "context_length": 0
        }

        # Session saving functionality (new - backward compatible)
        self.session_save_manager = get_session_save_manager()
        self.current_session_messages: List[SessionMessage] = []
        self.save_suggestion_shown = False

        logger.info("ConversationMemoryManager initialized")
    
    def start_conversation_session(self) -> None:
        """
        Start new conversation session.
        
        CRITICAL: This replaces agent.clear_chat_memory() in start_jarvis.py
        and maintains the same interface for wake word compatibility.
        """
        self.session_active = True
        self.session_start_time = time.time()
        self.conversation_context = ""
        
        # Create persistent agent for memory continuity
        self._create_persistent_agent()
        
        # Reset session stats
        self.session_stats = {
            "session_duration": 0.0,
            "exchanges_tracked": 0,
            "context_length": 0
        }

        # Reset session saving state (new)
        self.current_session_messages = []
        self.save_suggestion_shown = False

        logger.info("🧠 Conversation session started with persistent agent")
    
    def _create_persistent_agent(self) -> None:
        """Create persistent agent for memory continuity."""
        try:
            from ..agent import JarvisAgent
            from ...config import get_config
            from ...tools import plugin_manager
            
            config = get_config()
            self.persistent_agent = JarvisAgent(config.llm, config.agent)
            
            # Initialize with all tools (will be filtered per query by controller)
            all_tools = plugin_manager.get_all_tools()
            self.persistent_agent.initialize(all_tools)
            
            logger.info("✅ Persistent agent created for memory continuity")
        except Exception as e:
            logger.error(f"Failed to create persistent agent: {e}")
            self.persistent_agent = None
    
    def add_conversation_exchange(self, user_input: str, assistant_response: str) -> None:
        """
        Add a conversation exchange to context.
        
        Args:
            user_input: What the user said
            assistant_response: What the assistant responded
        """
        if not self.session_active:
            logger.warning("Attempted to add exchange to inactive session")
            return
        
        # Add to conversation context (keep last 3 exchanges for efficiency)
        exchange = f"User: {user_input}\nAssistant: {assistant_response}\n"
        
        # Simple context management - keep recent exchanges
        context_lines = self.conversation_context.split('\n')
        if len(context_lines) > 12:  # 3 exchanges * 4 lines each
            # Keep only the most recent exchanges
            self.conversation_context = '\n'.join(context_lines[-12:])
        
        self.conversation_context += exchange
        
        # Update stats
        self.session_stats["exchanges_tracked"] += 1
        self.session_stats["context_length"] = len(self.conversation_context)
        
        logger.debug(f"Added conversation exchange (total: {self.session_stats['exchanges_tracked']})")
    
    def get_conversation_context(self) -> str:
        """
        Get current conversation context.
        
        Returns:
            String containing recent conversation context
        """
        return self.conversation_context
    
    def get_persistent_agent(self) -> Optional[Any]:
        """
        Get the persistent agent for this conversation session.
        
        Returns:
            Persistent agent instance or None if not available
        """
        return self.persistent_agent
    
    def is_session_active(self) -> bool:
        """Check if conversation session is active."""
        return self.session_active
    
    def end_conversation_session(self) -> Dict[str, Any]:
        """
        End conversation session and return summary.
        
        Returns:
            Dictionary with session statistics
        """
        if not self.session_active:
            return {"error": "No active session"}
        
        # Calculate final stats
        session_duration = time.time() - self.session_start_time
        self.session_stats["session_duration"] = session_duration
        
        # Finalize any active saved session (new)
        if self.session_save_manager:
            self.session_save_manager.finalize_active_session()

        # Clean up
        self.session_active = False
        self.conversation_context = ""
        self.persistent_agent = None

        logger.info(f"🧠 Conversation session ended (duration: {session_duration:.1f}s)")
        
        return self.session_stats.copy()
    
    def clear_context(self) -> None:
        """Clear conversation context while keeping session active."""
        self.conversation_context = ""
        self.session_stats["context_length"] = 0
        logger.info("Conversation context cleared")
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get current session statistics."""
        if self.session_active:
            current_duration = time.time() - self.session_start_time
            stats = self.session_stats.copy()
            stats["session_duration"] = current_duration
            return stats
        return self.session_stats.copy()

    # Session Saving Methods (New - Backward Compatible)

    def add_message_to_session(self, content: str, role: str = "user") -> Optional[str]:
        """
        Add message to current session and check for save suggestions.

        Args:
            content: Message content
            role: Message role ("user" or "assistant")

        Returns:
            Save suggestion message if applicable, None otherwise
        """
        try:
            # Create session message
            message = SessionMessage(
                content=content,
                role=role,
                timestamp=datetime.now()
            )

            # Add to current session
            self.current_session_messages.append(message)

            # Add to active saved session if exists
            if self.session_save_manager:
                self.session_save_manager.add_to_active_session(message)

            # Check if we should suggest saving (only once per session)
            if (not self.save_suggestion_shown and
                self.session_save_manager and
                self.session_save_manager.should_suggest_save(len(self.current_session_messages))):

                self.save_suggestion_shown = True
                return self._generate_save_suggestion()

            return None

        except Exception as e:
            logger.error(f"Failed to add message to session: {e}")
            return None

    def save_current_session(self, session_name: str) -> str:
        """Save the current session with the given name."""
        try:
            if not self.session_save_manager:
                return "Session saving is not available."

            if not self.current_session_messages:
                return "No messages to save in current session."

            result = self.session_save_manager.save_session(
                self.current_session_messages,
                session_name
            )

            return result.message

        except Exception as e:
            logger.error(f"Failed to save session: {e}")
            return f"Failed to save session: {str(e)}"

    def recall_session(self, session_name: str) -> Optional[str]:
        """Recall a previously saved session."""
        try:
            if not self.session_save_manager:
                return None

            session = self.session_save_manager.recall_session(session_name)

            if session:
                # Replace current session with recalled session
                self.current_session_messages = session.full_conversation.copy()

                # Format for display
                return self._format_recalled_session(session)

            return None

        except Exception as e:
            logger.error(f"Failed to recall session: {e}")
            return None

    def list_saved_sessions(self) -> str:
        """List all saved sessions."""
        try:
            if not self.session_save_manager:
                return "Session saving is not available."

            sessions = self.session_save_manager.list_saved_sessions()

            if not sessions:
                return "No saved sessions found."

            return self._format_session_list(sessions)

        except Exception as e:
            logger.error(f"Failed to list sessions: {e}")
            return f"Failed to list sessions: {str(e)}"

    def _generate_save_suggestion(self) -> str:
        """Generate a save suggestion message."""
        message_count = len(self.current_session_messages)
        return (f"We've had a great {message_count}-message conversation! "
                f"Would you like me to save this session so you can reference it later? "
                f"Just say 'Yes, save it' and I'll ask you to name it.")

    def _format_recalled_session(self, session: SavedSession) -> str:
        """Format a recalled session for display."""
        header = f"📅 Recalled Session: {session.name}\n"
        header += f"🕐 Originally saved: {session.timestamp.strftime('%B %d, %Y at %I:%M %p')}\n"
        header += f"💬 Messages: {session.prompt_count}\n\n"

        # Show last few messages as preview
        preview_messages = session.full_conversation[-5:] if len(session.full_conversation) > 5 else session.full_conversation

        conversation_preview = ""
        for msg in preview_messages:
            role_prefix = "👤 You" if msg.role == "user" else "🤖 Jarvis"
            timestamp_str = msg.timestamp.strftime("%H:%M")
            conversation_preview += f"[{timestamp_str}] {role_prefix}: {msg.content}\n"

        footer = "\n✅ Session recalled and ready to continue where we left off!"

        return header + conversation_preview + footer

    def _format_session_list(self, sessions: List[Dict[str, Any]]) -> str:
        """Format the list of saved sessions."""
        if not sessions:
            return "No saved sessions found."

        header = f"📚 Your Saved Sessions ({len(sessions)} total):\n\n"

        session_lines = []
        for i, session in enumerate(sessions, 1):
            name = session.get("name", "Unknown")
            timestamp = session.get("timestamp", "")
            prompt_count = session.get("prompt_count", 0)

            # Format timestamp
            try:
                dt = datetime.fromisoformat(timestamp)
                time_str = dt.strftime("%b %d, %Y")
            except:
                time_str = "Unknown date"

            session_lines.append(f"{i:2d}. **{name}** ({prompt_count} messages) - {time_str}")

        footer = "\n💡 Say 'Recall [session name]' to continue any of these conversations!"

        return header + "\n".join(session_lines) + footer


# Singleton instance for global access
_conversation_memory_manager = None


def get_conversation_memory_manager() -> ConversationMemoryManager:
    """
    Get singleton conversation memory manager instance.
    
    Returns:
        ConversationMemoryManager instance
    """
    global _conversation_memory_manager
    if _conversation_memory_manager is None:
        _conversation_memory_manager = ConversationMemoryManager()
    return _conversation_memory_manager
