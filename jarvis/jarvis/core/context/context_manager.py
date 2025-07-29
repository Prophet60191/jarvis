"""
Context Manager

Central coordination system for all context data in Jarvis, providing
unified access to conversation state, user preferences, tool states,
and session memory.
"""

import time
import logging
import threading
from typing import Dict, List, Optional, Any, Set, Union
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import json

from .conversation_state import ConversationState
from .tool_state_tracker import ToolStateTracker
from .user_preference_engine import UserPreferenceEngine
from .session_memory import SessionMemory

# Import performance optimization components
try:
    from jarvis.jarvis.core.performance.context_cache import ContextCacheManager
    from jarvis.jarvis.core.monitoring.performance_tracker import performance_tracker, track_operation
    from jarvis.jarvis.core.analytics.usage_analytics import usage_analytics
    PERFORMANCE_FEATURES_AVAILABLE = True
except ImportError:
    PERFORMANCE_FEATURES_AVAILABLE = False
    # Fallback implementations
    class ContextCacheManager:
        def __init__(self): pass
        def get_cache(self, cache_type): return None

    def track_operation(name):
        def decorator(func):
            return func
        return decorator

    class MockTracker:
        def start_operation(self, name): return "mock"
        def end_operation(self, op_id, success=True, **kwargs): return 0.0
        def record_metric(self, *args, **kwargs): pass

    performance_tracker = MockTracker()

    class MockAnalytics:
        def track_tool_usage(self, *args, **kwargs): pass
        def track_conversation_event(self, *args, **kwargs): pass

    usage_analytics = MockAnalytics()

logger = logging.getLogger(__name__)

class ContextScope(Enum):
    """Scope levels for context data."""
    GLOBAL = "global"           # System-wide context
    USER = "user"              # User-specific context
    SESSION = "session"        # Session-specific context
    CONVERSATION = "conversation"  # Current conversation context
    TOOL = "tool"              # Tool-specific context

@dataclass
class Context:
    """
    Unified context container for all contextual information.
    
    This class provides a unified interface to access all types of
    context data including conversation state, user preferences,
    tool states, and session memory.
    """
    # Identifiers
    session_id: str
    user_id: Optional[str] = None
    conversation_id: Optional[str] = None
    
    # Context data
    conversation_context: Dict[str, Any] = field(default_factory=dict)
    user_context: Dict[str, Any] = field(default_factory=dict)
    system_context: Dict[str, Any] = field(default_factory=dict)
    tool_context: Dict[str, Any] = field(default_factory=dict)
    
    # Metadata
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    access_count: int = 0
    
    def update_timestamp(self) -> None:
        """Update the last modified timestamp."""
        self.updated_at = time.time()
        self.access_count += 1
    
    def get_scoped_context(self, scope: ContextScope) -> Dict[str, Any]:
        """Get context data for a specific scope."""
        scope_mapping = {
            ContextScope.CONVERSATION: self.conversation_context,
            ContextScope.USER: self.user_context,
            ContextScope.GLOBAL: self.system_context,
            ContextScope.TOOL: self.tool_context,
            ContextScope.SESSION: {
                **self.conversation_context,
                **self.user_context,
                **self.tool_context
            }
        }
        return scope_mapping.get(scope, {})
    
    def update_scoped_context(self, scope: ContextScope, updates: Dict[str, Any]) -> None:
        """Update context data for a specific scope."""
        if scope == ContextScope.CONVERSATION:
            self.conversation_context.update(updates)
        elif scope == ContextScope.USER:
            self.user_context.update(updates)
        elif scope == ContextScope.GLOBAL:
            self.system_context.update(updates)
        elif scope == ContextScope.TOOL:
            self.tool_context.update(updates)
        
        self.update_timestamp()
    
    def merge_context(self, other_context: 'Context') -> None:
        """Merge another context into this one."""
        self.conversation_context.update(other_context.conversation_context)
        self.user_context.update(other_context.user_context)
        self.system_context.update(other_context.system_context)
        self.tool_context.update(other_context.tool_context)
        self.update_timestamp()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert context to dictionary for serialization."""
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "conversation_id": self.conversation_id,
            "conversation_context": self.conversation_context,
            "user_context": self.user_context,
            "system_context": self.system_context,
            "tool_context": self.tool_context,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "access_count": self.access_count
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Context':
        """Create context from dictionary."""
        return cls(**data)

class ContextManager:
    """
    Central context management system.
    
    This class coordinates all context-related functionality including
    conversation state, user preferences, tool states, and session memory.
    It provides a unified interface for accessing and managing context data.
    """
    
    def __init__(self, storage_path: Optional[Path] = None,
                 enable_persistence: bool = True):
        """
        Initialize the context manager.
        
        Args:
            storage_path: Optional path for persistent storage
            enable_persistence: Whether to enable persistent storage
        """
        # Storage configuration
        self.storage_path = storage_path or Path("data/context_manager.json")
        self.enable_persistence = enable_persistence
        
        # Context storage
        self._contexts: Dict[str, Context] = {}
        self._active_sessions: Set[str] = set()
        self._lock = threading.RLock()
        
        # Sub-components
        self.conversation_state = ConversationState()
        self.tool_state_tracker = ToolStateTracker()
        self.user_preference_engine = UserPreferenceEngine()
        self.session_memory = SessionMemory()

        # Performance optimization components
        if PERFORMANCE_FEATURES_AVAILABLE:
            self.cache_manager = ContextCacheManager()
            self._context_cache = self.cache_manager.get_cache('session_context')
            self._preferences_cache = self.cache_manager.get_cache('user_preferences')
            logger.info("Context caching enabled")
        else:
            self.cache_manager = None
            self._context_cache = None
            self._preferences_cache = None
            logger.info("Context caching disabled (performance features not available)")
        
        # Configuration
        self.max_contexts = 1000  # Maximum contexts to keep in memory
        self.context_ttl_hours = 24  # Context time-to-live in hours
        self.auto_cleanup_interval = 3600  # Cleanup interval in seconds
        
        # Load existing data
        if self.enable_persistence:
            self._load_context_data()
        
        logger.info("ContextManager initialized")
    
    def create_session(self, session_id: str, user_id: Optional[str] = None,
                      initial_context: Optional[Dict[str, Any]] = None) -> Context:
        """
        Create a new session with context.
        
        Args:
            session_id: Unique session identifier
            user_id: Optional user identifier
            initial_context: Optional initial context data
            
        Returns:
            Context: Created context instance
        """
        with self._lock:
            if session_id in self._contexts:
                logger.warning(f"Session {session_id} already exists, returning existing context")
                return self._contexts[session_id]
            
            # Create new context
            context = Context(
                session_id=session_id,
                user_id=user_id,
                conversation_id=f"{session_id}_conv_{int(time.time())}"
            )
            
            # Add initial context if provided
            if initial_context:
                context.conversation_context.update(initial_context)
            
            # Initialize sub-components for this session
            self.conversation_state.initialize_session(session_id)
            self.tool_state_tracker.initialize_session(session_id)
            self.session_memory.create_session(session_id)
            
            # Load user preferences if user_id provided
            if user_id:
                user_preferences = self.user_preference_engine.get_user_preferences(user_id)
                context.user_context.update({"preferences": user_preferences})
            
            # Store context
            self._contexts[session_id] = context
            self._active_sessions.add(session_id)
            
            # Auto-save if enabled
            if self.enable_persistence:
                self._save_context_data()
            
            logger.info(f"Created session {session_id} for user {user_id}")
            return context
    
    @track_operation("get_current_context")
    def get_current_context(self, session_id: str = "default") -> Context:
        """
        Get current context for a session.

        Args:
            session_id: Session identifier

        Returns:
            Context: Current context or new context if not found
        """
        # Try cache first
        if self._context_cache:
            cached_context = self._context_cache.get(session_id)
            if cached_context:
                logger.debug(f"Context cache HIT for session {session_id}")
                return cached_context

        with self._lock:
            if session_id not in self._contexts:
                # Create new session if it doesn't exist
                return self.create_session(session_id)

            context = self._contexts[session_id]
            context.update_timestamp()

            # Update with latest state from sub-components
            self._sync_context_with_components(context)

            # Cache the context
            if self._context_cache:
                self._context_cache.put(session_id, context)
                logger.debug(f"Context cached for session {session_id}")

            return context
    
    @track_operation("update_context")
    def update_context(self, session_id: str, updates: Dict[str, Any],
                      scope: ContextScope = ContextScope.CONVERSATION) -> None:
        """
        Update context for a session.

        Args:
            session_id: Session identifier
            updates: Context updates to apply
            scope: Context scope to update
        """
        with self._lock:
            context = self.get_current_context(session_id)
            context.update_scoped_context(scope, updates)
            
            # Propagate updates to sub-components
            self._propagate_context_updates(context, updates, scope)

            # Invalidate cache for this session
            if self._context_cache:
                self._context_cache.remove(session_id)

            # Track analytics
            if PERFORMANCE_FEATURES_AVAILABLE:
                usage_analytics.track_conversation_event(
                    session_id=session_id,
                    event_type='context_update',
                    user_id=context.user_context.get('user_id'),
                    metadata={'scope': scope.value, 'update_keys': list(updates.keys())}
                )

            # Auto-save if enabled
            if self.enable_persistence:
                self._save_context_data()

            logger.debug(f"Updated context for session {session_id} in scope {scope.value}")
    
    def clear_session(self, session_id: str) -> None:
        """
        Clear all context data for a session.
        
        Args:
            session_id: Session identifier
        """
        with self._lock:
            if session_id in self._contexts:
                del self._contexts[session_id]
            
            self._active_sessions.discard(session_id)
            
            # Clear sub-component data
            self.conversation_state.clear_session(session_id)
            self.tool_state_tracker.clear_session(session_id)
            self.session_memory.clear_session(session_id)
            
            # Auto-save if enabled
            if self.enable_persistence:
                self._save_context_data()
            
            logger.info(f"Cleared session {session_id}")
    
    def get_session_summary(self, session_id: str) -> Dict[str, Any]:
        """
        Get a summary of session context and activity.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Dict[str, Any]: Session summary
        """
        with self._lock:
            if session_id not in self._contexts:
                return {"error": "Session not found"}
            
            context = self._contexts[session_id]
            
            # Get summaries from sub-components
            conversation_summary = self.conversation_state.get_session_summary(session_id)
            tool_summary = self.tool_state_tracker.get_session_summary(session_id)
            memory_summary = self.session_memory.get_session_summary(session_id)
            
            return {
                "session_id": session_id,
                "user_id": context.user_id,
                "created_at": context.created_at,
                "updated_at": context.updated_at,
                "access_count": context.access_count,
                "conversation_summary": conversation_summary,
                "tool_summary": tool_summary,
                "memory_summary": memory_summary,
                "context_size": {
                    "conversation": len(context.conversation_context),
                    "user": len(context.user_context),
                    "system": len(context.system_context),
                    "tool": len(context.tool_context)
                }
            }
    
    def get_active_sessions(self) -> List[str]:
        """
        Get list of active session IDs.
        
        Returns:
            List[str]: List of active session IDs
        """
        with self._lock:
            return list(self._active_sessions)
    
    def get_context_statistics(self) -> Dict[str, Any]:
        """
        Get overall context management statistics.
        
        Returns:
            Dict[str, Any]: Context statistics
        """
        with self._lock:
            total_contexts = len(self._contexts)
            active_sessions = len(self._active_sessions)
            
            # Calculate memory usage estimation
            total_context_size = sum(
                len(str(context.to_dict())) for context in self._contexts.values()
            )
            
            # Get oldest and newest contexts
            if self._contexts:
                oldest_context = min(self._contexts.values(), key=lambda c: c.created_at)
                newest_context = max(self._contexts.values(), key=lambda c: c.created_at)
                oldest_age = time.time() - oldest_context.created_at
                newest_age = time.time() - newest_context.created_at
            else:
                oldest_age = newest_age = 0
            
            return {
                "total_contexts": total_contexts,
                "active_sessions": active_sessions,
                "estimated_memory_kb": total_context_size / 1024,
                "oldest_context_age_hours": oldest_age / 3600,
                "newest_context_age_hours": newest_age / 3600,
                "average_access_count": sum(c.access_count for c in self._contexts.values()) / max(total_contexts, 1),
                "persistence_enabled": self.enable_persistence,
                "storage_path": str(self.storage_path) if self.storage_path else None
            }
    
    def cleanup_expired_contexts(self) -> int:
        """
        Clean up expired contexts based on TTL.
        
        Returns:
            int: Number of contexts cleaned up
        """
        current_time = time.time()
        ttl_seconds = self.context_ttl_hours * 3600
        
        with self._lock:
            expired_sessions = []
            
            for session_id, context in self._contexts.items():
                if current_time - context.updated_at > ttl_seconds:
                    expired_sessions.append(session_id)
            
            # Remove expired contexts
            for session_id in expired_sessions:
                self.clear_session(session_id)
            
            logger.info(f"Cleaned up {len(expired_sessions)} expired contexts")
            return len(expired_sessions)
    
    def _sync_context_with_components(self, context: Context) -> None:
        """Synchronize context with sub-component states."""
        session_id = context.session_id
        
        # Update conversation context
        conv_state = self.conversation_state.get_current_state(session_id)
        if conv_state:
            context.conversation_context.update({
                "current_topic": conv_state.current_topic,
                "intent_history": conv_state.intent_history[-5:],  # Last 5 intents
                "conversation_flow": conv_state.conversation_flow[-10:]  # Last 10 flow items
            })
        
        # Update tool context
        active_tools = self.tool_state_tracker.get_active_tools(session_id)
        context.tool_context.update({
            "active_tools": active_tools,
            "tool_states": {
                tool: self.tool_state_tracker.get_tool_state(session_id, tool)
                for tool in active_tools
            }
        })
    
    def _propagate_context_updates(self, context: Context, updates: Dict[str, Any], 
                                 scope: ContextScope) -> None:
        """Propagate context updates to relevant sub-components."""
        session_id = context.session_id
        
        # Propagate conversation updates
        if scope == ContextScope.CONVERSATION:
            if "current_topic" in updates:
                self.conversation_state.update_topic(session_id, updates["current_topic"])
            if "user_intent" in updates:
                self.conversation_state.add_intent(session_id, updates["user_intent"])
        
        # Propagate tool updates
        if scope == ContextScope.TOOL:
            if "active_tool" in updates:
                self.tool_state_tracker.activate_tool(session_id, updates["active_tool"])
            if "tool_result" in updates:
                tool_name = updates.get("tool_name")
                if tool_name:
                    self.tool_state_tracker.update_tool_state(
                        session_id, tool_name, "completed", updates["tool_result"]
                    )
        
        # Propagate user preference updates
        if scope == ContextScope.USER and context.user_id:
            if "learned_preference" in updates:
                pref_data = updates["learned_preference"]
                self.user_preference_engine.learn_preference(
                    context.user_id,
                    pref_data["type"],
                    pref_data["value"],
                    pref_data.get("confidence", 1.0)
                )
    
    def _load_context_data(self) -> None:
        """Load context data from persistent storage."""
        try:
            if self.storage_path.exists():
                with open(self.storage_path, 'r') as f:
                    data = json.load(f)
                
                # Load contexts
                for session_id, context_data in data.get("contexts", {}).items():
                    context = Context.from_dict(context_data)
                    self._contexts[session_id] = context
                    self._active_sessions.add(session_id)
                
                # Load sub-component data
                if "conversation_state" in data:
                    self.conversation_state.load_state_data(data["conversation_state"])
                if "tool_state_tracker" in data:
                    self.tool_state_tracker.load_state_data(data["tool_state_tracker"])
                if "user_preferences" in data:
                    self.user_preference_engine.load_preferences_data(data["user_preferences"])
                if "session_memory" in data:
                    self.session_memory.load_memory_data(data["session_memory"])
                
                logger.info(f"Loaded context data for {len(self._contexts)} sessions")
                
        except Exception as e:
            logger.warning(f"Failed to load context data: {e}")
    
    def _save_context_data(self) -> None:
        """Save context data to persistent storage."""
        try:
            # Prepare data for serialization
            data = {
                "contexts": {
                    session_id: context.to_dict()
                    for session_id, context in self._contexts.items()
                },
                "conversation_state": self.conversation_state.export_state_data(),
                "tool_state_tracker": self.tool_state_tracker.export_state_data(),
                "user_preferences": self.user_preference_engine.export_preferences_data(),
                "session_memory": self.session_memory.export_memory_data(),
                "saved_at": time.time()
            }
            
            # Ensure directory exists
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save to file
            with open(self.storage_path, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            
            logger.debug("Saved context data to storage")
            
        except Exception as e:
            logger.error(f"Failed to save context data: {e}")
    
    def export_context_data(self, export_path: Path) -> bool:
        """
        Export context data to a file.
        
        Args:
            export_path: Path to export data to
            
        Returns:
            bool: True if export successful
        """
        try:
            with self._lock:
                export_data = {
                    "export_timestamp": time.time(),
                    "context_statistics": self.get_context_statistics(),
                    "session_summaries": {
                        session_id: self.get_session_summary(session_id)
                        for session_id in self._active_sessions
                    },
                    "contexts": {
                        session_id: context.to_dict()
                        for session_id, context in self._contexts.items()
                    }
                }
            
            export_path.parent.mkdir(parents=True, exist_ok=True)
            with open(export_path, 'w') as f:
                json.dump(export_data, f, indent=2, default=str)
            
            logger.info(f"Context data exported to {export_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to export context data: {e}")
            return False
