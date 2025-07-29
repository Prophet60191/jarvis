"""
Context Sharing API

Provides a unified API for tools and components to access and update
shared context across the Jarvis system.
"""

import time
import logging
from typing import Dict, List, Optional, Any, Set, Union, Callable
from dataclasses import dataclass
from enum import Enum
import threading
from functools import wraps

from .context_manager import ContextManager, Context, ContextScope
from .conversation_state import ConversationState, ConversationPhase, IntentConfidence
from .tool_state_tracker import ToolStateTracker, ToolState, ToolPriority
from .user_preference_engine import UserPreferenceEngine, PreferenceType
from .session_memory import SessionMemory, MemoryType, MemoryScope

logger = logging.getLogger(__name__)

class ContextAccessLevel(Enum):
    """Access levels for context operations."""
    READ_ONLY = "read_only"
    READ_WRITE = "read_write"
    ADMIN = "admin"

@dataclass
class ContextPermission:
    """Context access permission definition."""
    tool_name: str
    access_level: ContextAccessLevel
    allowed_scopes: Set[ContextScope]
    allowed_operations: Set[str]
    expires_at: Optional[float] = None
    
    def is_expired(self) -> bool:
        """Check if permission has expired."""
        if self.expires_at is None:
            return False
        return time.time() > self.expires_at
    
    def can_access_scope(self, scope: ContextScope) -> bool:
        """Check if permission allows access to a scope."""
        return scope in self.allowed_scopes
    
    def can_perform_operation(self, operation: str) -> bool:
        """Check if permission allows a specific operation."""
        return operation in self.allowed_operations

class ContextAPI:
    """
    Unified API for context access and manipulation.
    
    This class provides a secure, controlled interface for tools and
    components to interact with the context management system.
    """
    
    def __init__(self, context_manager: ContextManager):
        """
        Initialize the context API.
        
        Args:
            context_manager: Context manager instance
        """
        self.context_manager = context_manager
        
        # Component access
        self.conversation_state = context_manager.conversation_state
        self.tool_state_tracker = context_manager.tool_state_tracker
        self.user_preference_engine = context_manager.user_preference_engine
        self.session_memory = context_manager.session_memory
        
        # Permission management
        self._permissions: Dict[str, ContextPermission] = {}
        self._access_log: List[Dict[str, Any]] = []
        
        # Event handlers
        self._event_handlers: Dict[str, List[Callable]] = {
            "context_updated": [],
            "tool_state_changed": [],
            "preference_learned": [],
            "memory_stored": []
        }
        
        # Thread safety
        self._lock = threading.RLock()
        
        logger.info("ContextAPI initialized")
    
    def register_tool(self, tool_name: str, access_level: ContextAccessLevel = ContextAccessLevel.READ_WRITE,
                     allowed_scopes: Set[ContextScope] = None,
                     allowed_operations: Set[str] = None,
                     ttl_hours: Optional[float] = None) -> bool:
        """
        Register a tool for context access.
        
        Args:
            tool_name: Name of the tool
            access_level: Access level for the tool
            allowed_scopes: Scopes the tool can access
            allowed_operations: Operations the tool can perform
            ttl_hours: Time to live for the permission
            
        Returns:
            bool: True if registration successful
        """
        with self._lock:
            # Default permissions based on access level
            if allowed_scopes is None:
                if access_level == ContextAccessLevel.READ_ONLY:
                    allowed_scopes = {ContextScope.CONVERSATION, ContextScope.USER}
                elif access_level == ContextAccessLevel.READ_WRITE:
                    allowed_scopes = {ContextScope.CONVERSATION, ContextScope.USER, ContextScope.TOOL}
                else:  # ADMIN
                    allowed_scopes = set(ContextScope)
            
            if allowed_operations is None:
                if access_level == ContextAccessLevel.READ_ONLY:
                    allowed_operations = {"read", "search"}
                elif access_level == ContextAccessLevel.READ_WRITE:
                    allowed_operations = {"read", "write", "update", "search"}
                else:  # ADMIN
                    allowed_operations = {"read", "write", "update", "delete", "search", "clear"}
            
            # Calculate expiration
            expires_at = None
            if ttl_hours:
                expires_at = time.time() + (ttl_hours * 3600)
            
            # Create permission
            permission = ContextPermission(
                tool_name=tool_name,
                access_level=access_level,
                allowed_scopes=allowed_scopes,
                allowed_operations=allowed_operations,
                expires_at=expires_at
            )
            
            self._permissions[tool_name] = permission
            
            logger.debug(f"Registered tool {tool_name} with {access_level.value} access")
            return True
    
    def get_context(self, session_id: str, tool_name: str,
                   scope: ContextScope = ContextScope.CONVERSATION) -> Optional[Dict[str, Any]]:
        """
        Get context data for a tool.
        
        Args:
            session_id: Session identifier
            tool_name: Name of the requesting tool
            scope: Context scope to retrieve
            
        Returns:
            Optional[Dict[str, Any]]: Context data or None if access denied
        """
        if not self._check_permission(tool_name, "read", scope):
            logger.warning(f"Tool {tool_name} denied read access to {scope.value} scope")
            return None
        
        self._log_access(tool_name, "read", scope, session_id)
        
        context = self.context_manager.get_current_context(session_id)
        return context.get_scoped_context(scope)
    
    def update_context(self, session_id: str, tool_name: str,
                      updates: Dict[str, Any],
                      scope: ContextScope = ContextScope.TOOL) -> bool:
        """
        Update context data.
        
        Args:
            session_id: Session identifier
            tool_name: Name of the updating tool
            updates: Context updates to apply
            scope: Context scope to update
            
        Returns:
            bool: True if update successful
        """
        if not self._check_permission(tool_name, "write", scope):
            logger.warning(f"Tool {tool_name} denied write access to {scope.value} scope")
            return False
        
        self._log_access(tool_name, "write", scope, session_id)
        
        # Add tool metadata to updates
        enhanced_updates = {
            **updates,
            "_updated_by": tool_name,
            "_updated_at": time.time()
        }
        
        self.context_manager.update_context(session_id, enhanced_updates, scope)
        
        # Trigger event handlers
        self._trigger_event("context_updated", {
            "session_id": session_id,
            "tool_name": tool_name,
            "scope": scope,
            "updates": updates
        })
        
        return True
    
    def store_memory(self, session_id: str, tool_name: str,
                    memory_type: MemoryType, data: Any,
                    scope: MemoryScope = MemoryScope.SESSION,
                    tags: Set[str] = None, ttl_hours: Optional[float] = None) -> Optional[str]:
        """
        Store data in session memory.
        
        Args:
            session_id: Session identifier
            tool_name: Name of the storing tool
            memory_type: Type of memory data
            data: Data to store
            scope: Memory scope
            tags: Optional tags
            ttl_hours: Time to live
            
        Returns:
            Optional[str]: Memory entry ID or None if access denied
        """
        if not self._check_permission(tool_name, "write", ContextScope.SESSION):
            logger.warning(f"Tool {tool_name} denied memory write access")
            return None
        
        self._log_access(tool_name, "store_memory", ContextScope.SESSION, session_id)
        
        # Add tool metadata to tags
        enhanced_tags = (tags or set()) | {f"tool:{tool_name}"}
        
        entry_id = self.session_memory.store_memory(
            session_id=session_id,
            memory_type=memory_type,
            data=data,
            scope=scope,
            tags=enhanced_tags,
            ttl_hours=ttl_hours
        )
        
        # Trigger event handlers
        self._trigger_event("memory_stored", {
            "session_id": session_id,
            "tool_name": tool_name,
            "memory_type": memory_type,
            "entry_id": entry_id
        })
        
        return entry_id
    
    def retrieve_memory(self, session_id: str, tool_name: str,
                       entry_id: str) -> Optional[Any]:
        """
        Retrieve data from session memory.
        
        Args:
            session_id: Session identifier
            tool_name: Name of the requesting tool
            entry_id: Memory entry identifier
            
        Returns:
            Optional[Any]: Memory data or None if not found/access denied
        """
        if not self._check_permission(tool_name, "read", ContextScope.SESSION):
            logger.warning(f"Tool {tool_name} denied memory read access")
            return None
        
        self._log_access(tool_name, "retrieve_memory", ContextScope.SESSION, session_id)
        
        entry = self.session_memory.retrieve_memory(session_id, entry_id)
        return entry.data if entry else None
    
    def search_memory(self, session_id: str, tool_name: str,
                     memory_type: Optional[MemoryType] = None,
                     tags: Set[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search session memory.
        
        Args:
            session_id: Session identifier
            tool_name: Name of the requesting tool
            memory_type: Optional memory type filter
            tags: Optional tags filter
            limit: Maximum results
            
        Returns:
            List[Dict[str, Any]]: Memory search results
        """
        if not self._check_permission(tool_name, "search", ContextScope.SESSION):
            logger.warning(f"Tool {tool_name} denied memory search access")
            return []
        
        self._log_access(tool_name, "search_memory", ContextScope.SESSION, session_id)
        
        entries = self.session_memory.search_memory(
            session_id=session_id,
            memory_type=memory_type,
            tags=tags,
            limit=limit
        )
        
        # Return simplified results
        return [
            {
                "entry_id": entry.entry_id,
                "memory_type": entry.memory_type.value,
                "data": entry.data,
                "created_at": entry.created_at,
                "tags": list(entry.tags)
            }
            for entry in entries
        ]
    
    def start_tool_execution(self, session_id: str, tool_name: str,
                           parameters: Dict[str, Any] = None,
                           priority: ToolPriority = ToolPriority.NORMAL,
                           depends_on: List[str] = None) -> Optional[str]:
        """
        Start tracking a tool execution.
        
        Args:
            session_id: Session identifier
            tool_name: Name of the tool
            parameters: Tool parameters
            priority: Execution priority
            depends_on: Dependencies
            
        Returns:
            Optional[str]: Execution ID or None if access denied
        """
        if not self._check_permission(tool_name, "write", ContextScope.TOOL):
            logger.warning(f"Tool {tool_name} denied tool state write access")
            return None
        
        self._log_access(tool_name, "start_execution", ContextScope.TOOL, session_id)
        
        execution_id = self.tool_state_tracker.start_tool_execution(
            session_id=session_id,
            tool_name=tool_name,
            parameters=parameters or {},
            priority=priority,
            depends_on=depends_on or []
        )
        
        # Trigger event handlers
        self._trigger_event("tool_state_changed", {
            "session_id": session_id,
            "tool_name": tool_name,
            "execution_id": execution_id,
            "state": "started"
        })
        
        return execution_id
    
    def update_tool_state(self, execution_id: str, tool_name: str,
                         new_state: ToolState, result: Any = None,
                         error_message: str = None) -> bool:
        """
        Update tool execution state.
        
        Args:
            execution_id: Execution identifier
            tool_name: Name of the tool
            new_state: New state
            result: Optional result
            error_message: Optional error message
            
        Returns:
            bool: True if update successful
        """
        if not self._check_permission(tool_name, "update", ContextScope.TOOL):
            logger.warning(f"Tool {tool_name} denied tool state update access")
            return False
        
        success = self.tool_state_tracker.update_tool_state(
            execution_id=execution_id,
            new_state=new_state,
            result=result,
            error_message=error_message
        )
        
        if success:
            # Trigger event handlers
            self._trigger_event("tool_state_changed", {
                "execution_id": execution_id,
                "tool_name": tool_name,
                "state": new_state.value,
                "result": result
            })
        
        return success
    
    def learn_preference(self, user_id: str, tool_name: str,
                        preference_type: PreferenceType,
                        preference_key: str, preference_value: Any,
                        confidence: float = 1.0, success: bool = True) -> bool:
        """
        Learn a user preference.
        
        Args:
            user_id: User identifier
            tool_name: Name of the learning tool
            preference_type: Type of preference
            preference_key: Preference key
            preference_value: Preference value
            confidence: Learning confidence
            success: Whether preference led to success
            
        Returns:
            bool: True if learning successful
        """
        if not self._check_permission(tool_name, "write", ContextScope.USER):
            logger.warning(f"Tool {tool_name} denied preference learning access")
            return False
        
        context = {"learned_by": tool_name, "timestamp": time.time()}
        
        self.user_preference_engine.learn_preference(
            user_id=user_id,
            preference_type=preference_type,
            preference_key=preference_key,
            preference_value=preference_value,
            confidence=confidence,
            context=context,
            success=success
        )
        
        # Trigger event handlers
        self._trigger_event("preference_learned", {
            "user_id": user_id,
            "tool_name": tool_name,
            "preference_type": preference_type.value,
            "preference_key": preference_key
        })
        
        return True
    
    def get_user_preferences(self, user_id: str, tool_name: str,
                           preference_type: Optional[PreferenceType] = None) -> List[Dict[str, Any]]:
        """
        Get user preferences.
        
        Args:
            user_id: User identifier
            tool_name: Name of the requesting tool
            preference_type: Optional preference type filter
            
        Returns:
            List[Dict[str, Any]]: User preferences
        """
        if not self._check_permission(tool_name, "read", ContextScope.USER):
            logger.warning(f"Tool {tool_name} denied preference read access")
            return []
        
        preferences = self.user_preference_engine.get_user_preferences(
            user_id=user_id,
            preference_type=preference_type,
            min_confidence=0.3
        )
        
        # Return simplified results
        return [
            {
                "preference_type": pref.preference_type.value,
                "preference_key": pref.preference_key,
                "preference_value": pref.preference_value,
                "confidence": pref.confidence,
                "last_updated": pref.last_updated
            }
            for pref in preferences
        ]
    
    def add_conversation_step(self, session_id: str, tool_name: str,
                            user_input: str, system_response: str,
                            success: bool = True, tools_invoked: List[str] = None) -> bool:
        """
        Add a conversation step.
        
        Args:
            session_id: Session identifier
            tool_name: Name of the tool adding the step
            user_input: User's input
            system_response: System's response
            success: Whether interaction was successful
            tools_invoked: Tools that were invoked
            
        Returns:
            bool: True if addition successful
        """
        if not self._check_permission(tool_name, "write", ContextScope.CONVERSATION):
            logger.warning(f"Tool {tool_name} denied conversation write access")
            return False
        
        self.conversation_state.add_conversation_step(
            session_id=session_id,
            user_input=user_input,
            system_response=system_response,
            success=success,
            tools_invoked=tools_invoked or []
        )
        
        return True
    
    def add_event_handler(self, event_type: str, handler: Callable) -> bool:
        """
        Add an event handler.
        
        Args:
            event_type: Type of event to handle
            handler: Handler function
            
        Returns:
            bool: True if handler added successfully
        """
        if event_type not in self._event_handlers:
            return False
        
        with self._lock:
            self._event_handlers[event_type].append(handler)
            return True
    
    def remove_event_handler(self, event_type: str, handler: Callable) -> bool:
        """
        Remove an event handler.
        
        Args:
            event_type: Type of event
            handler: Handler function to remove
            
        Returns:
            bool: True if handler removed successfully
        """
        if event_type not in self._event_handlers:
            return False
        
        with self._lock:
            try:
                self._event_handlers[event_type].remove(handler)
                return True
            except ValueError:
                return False
    
    def get_access_log(self, tool_name: Optional[str] = None,
                      limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get access log entries.
        
        Args:
            tool_name: Optional tool name filter
            limit: Maximum number of entries
            
        Returns:
            List[Dict[str, Any]]: Access log entries
        """
        with self._lock:
            log_entries = self._access_log
            
            if tool_name:
                log_entries = [entry for entry in log_entries if entry["tool_name"] == tool_name]
            
            return log_entries[-limit:]
    
    def cleanup_expired_permissions(self) -> int:
        """
        Clean up expired permissions.
        
        Returns:
            int: Number of permissions cleaned up
        """
        with self._lock:
            expired_tools = [
                tool_name for tool_name, permission in self._permissions.items()
                if permission.is_expired()
            ]
            
            for tool_name in expired_tools:
                del self._permissions[tool_name]
            
            logger.debug(f"Cleaned up {len(expired_tools)} expired permissions")
            return len(expired_tools)
    
    def _check_permission(self, tool_name: str, operation: str, scope: ContextScope) -> bool:
        """Check if a tool has permission for an operation."""
        with self._lock:
            if tool_name not in self._permissions:
                logger.warning(f"Tool {tool_name} not registered for context access")
                return False
            
            permission = self._permissions[tool_name]
            
            # Check if permission is expired
            if permission.is_expired():
                logger.warning(f"Permission for tool {tool_name} has expired")
                del self._permissions[tool_name]
                return False
            
            # Check operation permission
            if not permission.can_perform_operation(operation):
                return False
            
            # Check scope permission
            if not permission.can_access_scope(scope):
                return False
            
            return True
    
    def _log_access(self, tool_name: str, operation: str, scope: ContextScope, session_id: str) -> None:
        """Log context access."""
        with self._lock:
            log_entry = {
                "timestamp": time.time(),
                "tool_name": tool_name,
                "operation": operation,
                "scope": scope.value,
                "session_id": session_id
            }
            
            self._access_log.append(log_entry)
            
            # Maintain log size
            if len(self._access_log) > 10000:
                self._access_log = self._access_log[-5000:]
    
    def _trigger_event(self, event_type: str, event_data: Dict[str, Any]) -> None:
        """Trigger event handlers."""
        with self._lock:
            handlers = self._event_handlers.get(event_type, [])
            
            for handler in handlers:
                try:
                    handler(event_data)
                except Exception as e:
                    logger.error(f"Error in event handler for {event_type}: {e}")

# Decorator for automatic context access
def with_context_access(tool_name: str, access_level: ContextAccessLevel = ContextAccessLevel.READ_WRITE):
    """
    Decorator to automatically register tool for context access.
    
    Args:
        tool_name: Name of the tool
        access_level: Access level for the tool
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # This would need to be connected to a global context API instance
            # For now, it's a placeholder for the pattern
            return func(*args, **kwargs)
        
        wrapper._context_tool_name = tool_name
        wrapper._context_access_level = access_level
        return wrapper
    
    return decorator

# Global context API instance (would be initialized by the main system)
_global_context_api: Optional[ContextAPI] = None

def get_context_api() -> Optional[ContextAPI]:
    """Get the global context API instance."""
    return _global_context_api

def set_context_api(api: ContextAPI) -> None:
    """Set the global context API instance."""
    global _global_context_api
    _global_context_api = api
