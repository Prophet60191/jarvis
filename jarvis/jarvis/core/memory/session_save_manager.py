"""
Session Save Manager

Manages saving, retrieving, and updating conversation sessions.
Integrates with existing RAG system for persistent storage.
"""

import logging
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from .session_models import SavedSession, SessionMessage, SessionState, SessionSaveResult

logger = logging.getLogger(__name__)


class SessionSaveManager:
    """
    Manages conversation session saving and retrieval.
    
    Integrates with existing RAG system for storage while maintaining
    backward compatibility with current memory systems.
    """
    
    def __init__(self, rag_manager=None):
        """Initialize session save manager."""
        self.prompt_threshold = 15  # Suggest saving after 15 prompts
        self.auto_save_interval = 5  # Auto-save every 5 new messages
        self.active_saved_session: Optional[SavedSession] = None
        self.last_save_count = 0
        self.rag_manager = rag_manager
        
        # Initialize RAG manager if not provided
        if self.rag_manager is None:
            self._initialize_rag_manager()
        
        logger.info("SessionSaveManager initialized")
    
    def _initialize_rag_manager(self):
        """Initialize RAG manager for session storage."""
        try:
            from ...tools.rag_memory_manager import RAGMemoryManager
            from ...config import get_config

            config = get_config()
            self.rag_manager = RAGMemoryManager(config)
            logger.info("RAG manager initialized for session storage")

        except Exception as e:
            logger.error(f"Failed to initialize RAG manager: {e}")
            self.rag_manager = None
    
    def should_suggest_save(self, current_session_length: int) -> bool:
        """Check if we should suggest saving the current session."""
        return (current_session_length >= self.prompt_threshold and 
                self.active_saved_session is None)
    
    def save_session(self, conversation: List[SessionMessage], user_name: str) -> SessionSaveResult:
        """
        Save a conversation session and mark it as active for continuous updates.
        
        Args:
            conversation: List of session messages
            user_name: User-provided name for the session
            
        Returns:
            SessionSaveResult with success status and details
        """
        try:
            # Create new saved session
            session = SavedSession(
                name=user_name,
                session_id=str(uuid.uuid4()),
                timestamp=datetime.now(),
                full_conversation=conversation.copy(),
                state=SessionState.SAVED_ACTIVE
            )
            
            # Set as active session for continuous saving
            self.active_saved_session = session
            self.last_save_count = len(conversation)
            
            # Store in RAG system
            storage_success = self._store_in_rag(session)
            
            if storage_success:
                return SessionSaveResult(
                    success=True,
                    message=f"Session '{user_name}' saved and will continue to update automatically!",
                    session_id=session.session_id
                )
            else:
                return SessionSaveResult(
                    success=False,
                    message="Failed to save session to storage",
                    error="RAG storage failed"
                )
                
        except Exception as e:
            logger.error(f"Failed to save session: {e}")
            return SessionSaveResult(
                success=False,
                message=f"Failed to save session: {str(e)}",
                error=str(e)
            )
    
    def add_to_active_session(self, new_message: SessionMessage) -> bool:
        """
        Add new message to currently active saved session.
        
        Args:
            new_message: New message to add
            
        Returns:
            True if added successfully, False otherwise
        """
        if not self.active_saved_session:
            return False
        
        try:
            # Add message to active session
            self.active_saved_session.add_message(new_message)
            
            # Check if we should auto-save
            if self._should_auto_save():
                self._update_in_rag(self.active_saved_session)
                self.last_save_count = len(self.active_saved_session.full_conversation)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to add message to active session: {e}")
            return False
    
    def recall_session(self, session_name: str) -> Optional[SavedSession]:
        """
        Recall a previously saved session and make it active.
        
        Args:
            session_name: Name of the session to recall
            
        Returns:
            SavedSession if found, None otherwise
        """
        try:
            session = self._retrieve_from_rag(session_name)
            
            if session:
                # Make this the active session for continuation
                self.active_saved_session = session
                self.active_saved_session.state = SessionState.RECALLED
                self.last_save_count = len(session.full_conversation)

                return session
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to recall session '{session_name}': {e}")
            return None
    
    def list_saved_sessions(self) -> List[Dict[str, Any]]:
        """
        List all saved sessions.
        
        Returns:
            List of session summaries
        """
        try:
            return self._list_sessions_from_rag()
        except Exception as e:
            logger.error(f"Failed to list sessions: {e}")
            return []
    
    def finalize_active_session(self) -> bool:
        """
        Finalize the active session (called when session ends).
        
        Returns:
            True if finalized successfully
        """
        if not self.active_saved_session:
            return True
        
        try:
            # Final save and mark as closed
            self.active_saved_session.state = SessionState.SAVED_CLOSED
            success = self._update_in_rag(self.active_saved_session)
            
            # Clear active session
            self.active_saved_session = None
            self.last_save_count = 0
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to finalize active session: {e}")
            return False
    
    def _should_auto_save(self) -> bool:
        """Check if we should auto-save the active session."""
        if not self.active_saved_session:
            return False
        
        new_messages = len(self.active_saved_session.full_conversation) - self.last_save_count
        return new_messages >= self.auto_save_interval
    
    def _store_in_rag(self, session: SavedSession) -> bool:
        """Store session in RAG system."""
        if not self.rag_manager:
            logger.warning("No RAG manager available for session storage")
            return False
        
        try:
            # Format session for storage
            session_content = self._format_session_for_storage(session)
            
            # Store using RAG manager
            memory_id = self.rag_manager.add_memory(
                content=session_content,
                memory_type="saved_session",
                metadata={
                    "session_name": session.name,
                    "session_id": session.session_id,
                    "timestamp": session.timestamp.isoformat(),
                    "last_updated": session.last_updated.isoformat(),
                    "prompt_count": session.prompt_count,
                    "state": session.state.value,
                    "tags": session.tags
                }
            )
            
            return memory_id is not None
            
        except Exception as e:
            logger.error(f"Failed to store session in RAG: {e}")
            return False
    
    def _update_in_rag(self, session: SavedSession) -> bool:
        """Update existing session in RAG system."""
        # For now, we'll delete and re-add (can be optimized later)
        try:
            # Delete existing
            self._delete_from_rag(session.session_id)
            
            # Re-add updated version
            return self._store_in_rag(session)
            
        except Exception as e:
            logger.error(f"Failed to update session in RAG: {e}")
            return False
    
    def _retrieve_from_rag(self, session_name: str) -> Optional[SavedSession]:
        """Retrieve session from RAG system."""
        if not self.rag_manager:
            return None
        
        try:
            # Search for session by name
            search_result = self.rag_manager.search_memory(
                query=f"session_name:{session_name}",
                memory_type="saved_session",
                limit=1
            )
            
            if search_result.entries:
                entry = search_result.entries[0]
                # Parse session from stored content
                return self._parse_session_from_storage(entry.content, entry.metadata)
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to retrieve session from RAG: {e}")
            return None
    
    def _list_sessions_from_rag(self) -> List[Dict[str, Any]]:
        """List all sessions from RAG system."""
        if not self.rag_manager:
            return []
        
        try:
            # Search for all saved sessions
            search_result = self.rag_manager.search_memory(
                query="saved_session",
                memory_type="saved_session",
                limit=50
            )
            
            sessions = []
            for entry in search_result.entries:
                sessions.append({
                    "name": entry.metadata.get("session_name", "Unknown"),
                    "session_id": entry.metadata.get("session_id", ""),
                    "timestamp": entry.metadata.get("timestamp", ""),
                    "prompt_count": entry.metadata.get("prompt_count", 0),
                    "state": entry.metadata.get("state", "unknown")
                })
            
            return sessions
            
        except Exception as e:
            logger.error(f"Failed to list sessions from RAG: {e}")
            return []
    
    def _delete_from_rag(self, session_id: str) -> bool:
        """Delete session from RAG system."""
        # Implementation depends on RAG manager's delete capabilities
        # For now, return True (can be implemented when needed)
        return True
    
    def _format_session_for_storage(self, session: SavedSession) -> str:
        """Format session for RAG storage."""
        header = f"SAVED SESSION: {session.name}\n"
        header += f"Session ID: {session.session_id}\n"
        header += f"Created: {session.timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n"
        header += f"Messages: {session.prompt_count}\n"
        header += f"State: {session.state.value}\n\n"
        
        conversation = session.get_conversation_text()
        
        return header + conversation
    
    def _parse_session_from_storage(self, content: str, metadata: Dict[str, Any]) -> SavedSession:
        """Parse session from stored content and metadata."""
        # This is a simplified implementation
        # In practice, you'd parse the full conversation from content
        
        return SavedSession(
            name=metadata.get("session_name", "Unknown"),
            session_id=metadata.get("session_id", str(uuid.uuid4())),
            timestamp=datetime.fromisoformat(metadata.get("timestamp", datetime.now().isoformat())),
            full_conversation=[],  # Would parse from content
            state=SessionState(metadata.get("state", SessionState.SAVED_CLOSED.value)),
            prompt_count=metadata.get("prompt_count", 0),
            tags=metadata.get("tags", []),
            last_updated=datetime.fromisoformat(metadata.get("last_updated", datetime.now().isoformat()))
        )


# Factory function for dependency injection
_session_save_manager_instance = None

def get_session_save_manager() -> SessionSaveManager:
    """Get the session save manager instance (singleton)."""
    global _session_save_manager_instance
    if _session_save_manager_instance is None:
        _session_save_manager_instance = SessionSaveManager()
    return _session_save_manager_instance
