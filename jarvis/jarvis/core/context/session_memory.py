"""
Session Memory Management

Manages session-specific data storage, retrieval, and lifecycle
for maintaining context across interactions within a session.
"""

import time
import logging
from typing import Dict, List, Optional, Any, Set, Union
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict
import threading
import json
from pathlib import Path

logger = logging.getLogger(__name__)

class MemoryScope(Enum):
    """Scopes for memory storage."""
    SESSION = "session"           # Session-specific memory
    CONVERSATION = "conversation" # Conversation-specific memory
    TASK = "task"                # Task-specific memory
    TEMPORARY = "temporary"       # Temporary memory (cleared frequently)
    PERSISTENT = "persistent"     # Persistent across sessions

class MemoryType(Enum):
    """Types of memory data."""
    USER_INPUT = "user_input"
    SYSTEM_RESPONSE = "system_response"
    TOOL_RESULT = "tool_result"
    CONTEXT_DATA = "context_data"
    PREFERENCE_DATA = "preference_data"
    STATE_DATA = "state_data"
    METADATA = "metadata"

@dataclass
class MemoryEntry:
    """Individual memory entry."""
    entry_id: str
    session_id: str
    memory_type: MemoryType
    scope: MemoryScope
    data: Any
    
    # Metadata
    created_at: float = field(default_factory=time.time)
    accessed_at: float = field(default_factory=time.time)
    access_count: int = 0
    
    # Relationships
    related_entries: List[str] = field(default_factory=list)
    tags: Set[str] = field(default_factory=set)
    
    # Lifecycle
    expires_at: Optional[float] = None
    priority: int = 1  # 1=low, 5=high
    
    def is_expired(self) -> bool:
        """Check if memory entry has expired."""
        if self.expires_at is None:
            return False
        return time.time() > self.expires_at
    
    def access(self) -> None:
        """Record access to this memory entry."""
        self.accessed_at = time.time()
        self.access_count += 1

@dataclass
class SessionData:
    """Complete session memory data."""
    session_id: str
    created_at: float = field(default_factory=time.time)
    last_accessed: float = field(default_factory=time.time)
    
    # Memory storage by scope
    session_memory: Dict[str, MemoryEntry] = field(default_factory=dict)
    conversation_memory: Dict[str, MemoryEntry] = field(default_factory=dict)
    task_memory: Dict[str, MemoryEntry] = field(default_factory=dict)
    temporary_memory: Dict[str, MemoryEntry] = field(default_factory=dict)
    
    # Indexes for fast retrieval
    type_index: Dict[MemoryType, List[str]] = field(default_factory=lambda: defaultdict(list))
    tag_index: Dict[str, List[str]] = field(default_factory=lambda: defaultdict(list))
    
    # Statistics
    total_entries: int = 0
    total_accesses: int = 0
    
    def update_access(self) -> None:
        """Update last access time."""
        self.last_accessed = time.time()
        self.total_accesses += 1

class SessionMemory:
    """
    Session memory management system.
    
    This component manages session-specific data storage and retrieval,
    providing different memory scopes and automatic cleanup.
    """
    
    def __init__(self, storage_path: Optional[Path] = None,
                 enable_persistence: bool = True):
        """
        Initialize session memory manager.
        
        Args:
            storage_path: Optional path for persistent storage
            enable_persistence: Whether to enable persistent storage
        """
        self.storage_path = storage_path
        self.enable_persistence = enable_persistence
        
        # Session storage
        self._sessions: Dict[str, SessionData] = {}
        self._persistent_memory: Dict[str, MemoryEntry] = {}
        
        # Configuration
        self.max_sessions = 100
        self.max_entries_per_session = 1000
        self.default_ttl_hours = 24
        self.cleanup_interval = 3600  # 1 hour
        
        # Memory limits by scope (in MB)
        self.memory_limits = {
            MemoryScope.SESSION: 50,
            MemoryScope.CONVERSATION: 20,
            MemoryScope.TASK: 10,
            MemoryScope.TEMPORARY: 5,
            MemoryScope.PERSISTENT: 100
        }
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Load persistent memory
        if self.enable_persistence and self.storage_path:
            self._load_memory_data()
        
        logger.info("SessionMemory initialized")
    
    def create_session(self, session_id: str) -> SessionData:
        """
        Create a new session memory space.
        
        Args:
            session_id: Session identifier
            
        Returns:
            SessionData: Created session data
        """
        with self._lock:
            if session_id in self._sessions:
                logger.warning(f"Session {session_id} already exists")
                return self._sessions[session_id]
            
            session_data = SessionData(session_id=session_id)
            self._sessions[session_id] = session_data
            
            # Cleanup old sessions if needed
            if len(self._sessions) > self.max_sessions:
                self._cleanup_old_sessions()
            
            logger.debug(f"Created session memory for {session_id}")
            return session_data
    
    def store_memory(self, session_id: str, memory_type: MemoryType,
                    data: Any, scope: MemoryScope = MemoryScope.SESSION,
                    tags: Set[str] = None, ttl_hours: Optional[float] = None,
                    priority: int = 1) -> str:
        """
        Store data in session memory.
        
        Args:
            session_id: Session identifier
            memory_type: Type of memory data
            data: Data to store
            scope: Memory scope
            tags: Optional tags for categorization
            ttl_hours: Time to live in hours
            priority: Priority level (1-5)
            
        Returns:
            str: Memory entry ID
        """
        with self._lock:
            # Ensure session exists
            if session_id not in self._sessions:
                self.create_session(session_id)
            
            session_data = self._sessions[session_id]
            session_data.update_access()
            
            # Generate entry ID
            entry_id = f"{session_id}_{memory_type.value}_{int(time.time() * 1000)}"
            
            # Calculate expiration
            expires_at = None
            if ttl_hours:
                expires_at = time.time() + (ttl_hours * 3600)
            elif scope == MemoryScope.TEMPORARY:
                expires_at = time.time() + 3600  # 1 hour for temporary
            
            # Create memory entry
            entry = MemoryEntry(
                entry_id=entry_id,
                session_id=session_id,
                memory_type=memory_type,
                scope=scope,
                data=data,
                tags=tags or set(),
                expires_at=expires_at,
                priority=priority
            )
            
            # Store in appropriate scope
            if scope == MemoryScope.SESSION:
                session_data.session_memory[entry_id] = entry
            elif scope == MemoryScope.CONVERSATION:
                session_data.conversation_memory[entry_id] = entry
            elif scope == MemoryScope.TASK:
                session_data.task_memory[entry_id] = entry
            elif scope == MemoryScope.TEMPORARY:
                session_data.temporary_memory[entry_id] = entry
            elif scope == MemoryScope.PERSISTENT:
                self._persistent_memory[entry_id] = entry
            
            # Update indexes
            session_data.type_index[memory_type].append(entry_id)
            for tag in entry.tags:
                session_data.tag_index[tag].append(entry_id)
            
            session_data.total_entries += 1
            
            # Check memory limits
            self._check_memory_limits(session_id, scope)
            
            logger.debug(f"Stored memory entry {entry_id} in {scope.value} scope")
            return entry_id
    
    def retrieve_memory(self, session_id: str, entry_id: str) -> Optional[MemoryEntry]:
        """
        Retrieve a specific memory entry.
        
        Args:
            session_id: Session identifier
            entry_id: Memory entry identifier
            
        Returns:
            Optional[MemoryEntry]: Memory entry or None if not found
        """
        with self._lock:
            if session_id not in self._sessions:
                return None
            
            session_data = self._sessions[session_id]
            session_data.update_access()
            
            # Search in all scopes
            for memory_dict in [
                session_data.session_memory,
                session_data.conversation_memory,
                session_data.task_memory,
                session_data.temporary_memory,
                self._persistent_memory
            ]:
                if entry_id in memory_dict:
                    entry = memory_dict[entry_id]
                    
                    # Check if expired
                    if entry.is_expired():
                        self._remove_entry(session_id, entry_id)
                        return None
                    
                    entry.access()
                    return entry
            
            return None
    
    def search_memory(self, session_id: str, 
                     memory_type: Optional[MemoryType] = None,
                     scope: Optional[MemoryScope] = None,
                     tags: Set[str] = None,
                     limit: int = 10) -> List[MemoryEntry]:
        """
        Search memory entries by criteria.
        
        Args:
            session_id: Session identifier
            memory_type: Optional memory type filter
            scope: Optional scope filter
            tags: Optional tags filter
            limit: Maximum number of results
            
        Returns:
            List[MemoryEntry]: Matching memory entries
        """
        with self._lock:
            if session_id not in self._sessions:
                return []
            
            session_data = self._sessions[session_id]
            session_data.update_access()
            
            candidates = set()
            
            # Filter by memory type
            if memory_type:
                candidates.update(session_data.type_index.get(memory_type, []))
            else:
                # Get all entries
                for memory_dict in [
                    session_data.session_memory,
                    session_data.conversation_memory,
                    session_data.task_memory,
                    session_data.temporary_memory
                ]:
                    candidates.update(memory_dict.keys())
                
                # Include persistent memory
                if not scope or scope == MemoryScope.PERSISTENT:
                    candidates.update(self._persistent_memory.keys())
            
            # Filter by tags
            if tags:
                tag_candidates = set()
                for tag in tags:
                    tag_candidates.update(session_data.tag_index.get(tag, []))
                candidates &= tag_candidates
            
            # Retrieve and filter entries
            results = []
            for entry_id in candidates:
                entry = self.retrieve_memory(session_id, entry_id)
                if entry:
                    # Filter by scope
                    if scope and entry.scope != scope:
                        continue
                    
                    results.append(entry)
            
            # Sort by priority and recency
            results.sort(key=lambda e: (e.priority, e.created_at), reverse=True)
            
            return results[:limit]
    
    def update_memory(self, session_id: str, entry_id: str,
                     data: Any = None, tags: Set[str] = None,
                     priority: int = None) -> bool:
        """
        Update an existing memory entry.
        
        Args:
            session_id: Session identifier
            entry_id: Memory entry identifier
            data: Optional new data
            tags: Optional new tags
            priority: Optional new priority
            
        Returns:
            bool: True if update successful
        """
        with self._lock:
            entry = self.retrieve_memory(session_id, entry_id)
            if not entry:
                return False
            
            # Update fields
            if data is not None:
                entry.data = data
            if tags is not None:
                # Update tag index
                session_data = self._sessions[session_id]
                for old_tag in entry.tags:
                    if entry_id in session_data.tag_index[old_tag]:
                        session_data.tag_index[old_tag].remove(entry_id)
                
                entry.tags = tags
                for new_tag in tags:
                    session_data.tag_index[new_tag].append(entry_id)
            
            if priority is not None:
                entry.priority = priority
            
            entry.access()
            
            logger.debug(f"Updated memory entry {entry_id}")
            return True
    
    def delete_memory(self, session_id: str, entry_id: str) -> bool:
        """
        Delete a memory entry.
        
        Args:
            session_id: Session identifier
            entry_id: Memory entry identifier
            
        Returns:
            bool: True if deletion successful
        """
        with self._lock:
            return self._remove_entry(session_id, entry_id)
    
    def clear_scope(self, session_id: str, scope: MemoryScope) -> int:
        """
        Clear all memory entries in a specific scope.
        
        Args:
            session_id: Session identifier
            scope: Memory scope to clear
            
        Returns:
            int: Number of entries cleared
        """
        with self._lock:
            if session_id not in self._sessions:
                return 0
            
            session_data = self._sessions[session_id]
            
            if scope == MemoryScope.SESSION:
                count = len(session_data.session_memory)
                session_data.session_memory.clear()
            elif scope == MemoryScope.CONVERSATION:
                count = len(session_data.conversation_memory)
                session_data.conversation_memory.clear()
            elif scope == MemoryScope.TASK:
                count = len(session_data.task_memory)
                session_data.task_memory.clear()
            elif scope == MemoryScope.TEMPORARY:
                count = len(session_data.temporary_memory)
                session_data.temporary_memory.clear()
            elif scope == MemoryScope.PERSISTENT:
                # Clear persistent memory for this session
                to_remove = [
                    entry_id for entry_id, entry in self._persistent_memory.items()
                    if entry.session_id == session_id
                ]
                for entry_id in to_remove:
                    del self._persistent_memory[entry_id]
                count = len(to_remove)
            else:
                return 0
            
            # Rebuild indexes
            self._rebuild_indexes(session_id)
            
            logger.debug(f"Cleared {count} entries from {scope.value} scope")
            return count
    
    def clear_session(self, session_id: str) -> None:
        """
        Clear all memory for a session.
        
        Args:
            session_id: Session identifier
        """
        with self._lock:
            if session_id in self._sessions:
                # Clear persistent memory for this session
                to_remove = [
                    entry_id for entry_id, entry in self._persistent_memory.items()
                    if entry.session_id == session_id
                ]
                for entry_id in to_remove:
                    del self._persistent_memory[entry_id]
                
                # Remove session
                del self._sessions[session_id]
                
                logger.debug(f"Cleared all memory for session {session_id}")
    
    def cleanup_expired_memory(self, session_id: Optional[str] = None) -> int:
        """
        Clean up expired memory entries.
        
        Args:
            session_id: Optional specific session to clean
            
        Returns:
            int: Number of entries cleaned up
        """
        with self._lock:
            cleaned_count = 0
            
            sessions_to_clean = [session_id] if session_id else list(self._sessions.keys())
            
            for sid in sessions_to_clean:
                if sid not in self._sessions:
                    continue
                
                session_data = self._sessions[sid]
                
                # Check all scopes
                for memory_dict in [
                    session_data.session_memory,
                    session_data.conversation_memory,
                    session_data.task_memory,
                    session_data.temporary_memory
                ]:
                    expired_entries = [
                        entry_id for entry_id, entry in memory_dict.items()
                        if entry.is_expired()
                    ]
                    
                    for entry_id in expired_entries:
                        self._remove_entry(sid, entry_id)
                        cleaned_count += 1
            
            # Clean persistent memory
            expired_persistent = [
                entry_id for entry_id, entry in self._persistent_memory.items()
                if entry.is_expired()
            ]
            
            for entry_id in expired_persistent:
                del self._persistent_memory[entry_id]
                cleaned_count += 1
            
            logger.debug(f"Cleaned up {cleaned_count} expired memory entries")
            return cleaned_count
    
    def get_session_summary(self, session_id: str) -> Dict[str, Any]:
        """
        Get memory summary for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Dict[str, Any]: Session memory summary
        """
        with self._lock:
            if session_id not in self._sessions:
                return {"error": "Session not found"}
            
            session_data = self._sessions[session_id]
            
            # Count entries by scope
            scope_counts = {
                "session": len(session_data.session_memory),
                "conversation": len(session_data.conversation_memory),
                "task": len(session_data.task_memory),
                "temporary": len(session_data.temporary_memory)
            }
            
            # Count persistent entries for this session
            persistent_count = sum(
                1 for entry in self._persistent_memory.values()
                if entry.session_id == session_id
            )
            scope_counts["persistent"] = persistent_count
            
            # Count by memory type
            type_counts = {}
            for memory_type, entry_ids in session_data.type_index.items():
                type_counts[memory_type.value] = len(entry_ids)
            
            return {
                "session_id": session_id,
                "created_at": session_data.created_at,
                "last_accessed": session_data.last_accessed,
                "total_entries": session_data.total_entries,
                "total_accesses": session_data.total_accesses,
                "scope_counts": scope_counts,
                "type_counts": type_counts,
                "tag_count": len(session_data.tag_index)
            }
    
    def _remove_entry(self, session_id: str, entry_id: str) -> bool:
        """Remove a memory entry from all storage and indexes."""
        if session_id not in self._sessions:
            return False
        
        session_data = self._sessions[session_id]
        entry = None
        
        # Find and remove from appropriate scope
        for memory_dict in [
            session_data.session_memory,
            session_data.conversation_memory,
            session_data.task_memory,
            session_data.temporary_memory
        ]:
            if entry_id in memory_dict:
                entry = memory_dict[entry_id]
                del memory_dict[entry_id]
                break
        
        # Check persistent memory
        if entry_id in self._persistent_memory:
            entry = self._persistent_memory[entry_id]
            del self._persistent_memory[entry_id]
        
        if not entry:
            return False
        
        # Remove from indexes
        if entry.memory_type in session_data.type_index:
            if entry_id in session_data.type_index[entry.memory_type]:
                session_data.type_index[entry.memory_type].remove(entry_id)
        
        for tag in entry.tags:
            if entry_id in session_data.tag_index[tag]:
                session_data.tag_index[tag].remove(entry_id)
        
        return True
    
    def _check_memory_limits(self, session_id: str, scope: MemoryScope) -> None:
        """Check and enforce memory limits for a scope."""
        # This is a simplified implementation
        # In practice, you'd calculate actual memory usage
        
        session_data = self._sessions[session_id]
        
        if scope == MemoryScope.SESSION and len(session_data.session_memory) > 500:
            self._evict_old_entries(session_data.session_memory, 400)
        elif scope == MemoryScope.CONVERSATION and len(session_data.conversation_memory) > 200:
            self._evict_old_entries(session_data.conversation_memory, 150)
        elif scope == MemoryScope.TASK and len(session_data.task_memory) > 100:
            self._evict_old_entries(session_data.task_memory, 75)
        elif scope == MemoryScope.TEMPORARY and len(session_data.temporary_memory) > 50:
            self._evict_old_entries(session_data.temporary_memory, 25)
    
    def _evict_old_entries(self, memory_dict: Dict[str, MemoryEntry], target_size: int) -> None:
        """Evict old entries to reach target size."""
        if len(memory_dict) <= target_size:
            return
        
        # Sort by priority (ascending) and access time (ascending)
        entries = list(memory_dict.values())
        entries.sort(key=lambda e: (e.priority, e.accessed_at))
        
        # Remove oldest, lowest priority entries
        to_remove = entries[:len(entries) - target_size]
        for entry in to_remove:
            if entry.entry_id in memory_dict:
                del memory_dict[entry.entry_id]
    
    def _cleanup_old_sessions(self) -> None:
        """Clean up old sessions to maintain session limit."""
        if len(self._sessions) <= self.max_sessions:
            return
        
        # Sort sessions by last access time
        sessions = list(self._sessions.items())
        sessions.sort(key=lambda x: x[1].last_accessed)
        
        # Remove oldest sessions
        sessions_to_remove = sessions[:len(sessions) - self.max_sessions]
        for session_id, _ in sessions_to_remove:
            self.clear_session(session_id)
    
    def _rebuild_indexes(self, session_id: str) -> None:
        """Rebuild indexes for a session."""
        session_data = self._sessions[session_id]
        
        # Clear indexes
        session_data.type_index.clear()
        session_data.tag_index.clear()
        
        # Rebuild from all scopes
        for memory_dict in [
            session_data.session_memory,
            session_data.conversation_memory,
            session_data.task_memory,
            session_data.temporary_memory
        ]:
            for entry in memory_dict.values():
                session_data.type_index[entry.memory_type].append(entry.entry_id)
                for tag in entry.tags:
                    session_data.tag_index[tag].append(entry.entry_id)
    
    def export_memory_data(self) -> Dict[str, Any]:
        """Export memory data for persistence."""
        with self._lock:
            return {
                "sessions": {
                    session_id: {
                        "session_id": data.session_id,
                        "created_at": data.created_at,
                        "last_accessed": data.last_accessed,
                        "total_entries": data.total_entries,
                        "total_accesses": data.total_accesses,
                        "session_memory": {
                            entry_id: {
                                **entry.__dict__,
                                "memory_type": entry.memory_type.value,
                                "scope": entry.scope.value,
                                "tags": list(entry.tags)
                            }
                            for entry_id, entry in data.session_memory.items()
                        }
                        # Note: Only exporting session memory for persistence
                        # Other scopes are considered temporary
                    }
                    for session_id, data in self._sessions.items()
                },
                "persistent_memory": {
                    entry_id: {
                        **entry.__dict__,
                        "memory_type": entry.memory_type.value,
                        "scope": entry.scope.value,
                        "tags": list(entry.tags)
                    }
                    for entry_id, entry in self._persistent_memory.items()
                }
            }
    
    def load_memory_data(self, data: Dict[str, Any]) -> None:
        """Load memory data from persistence."""
        with self._lock:
            # Clear current data
            self._sessions.clear()
            self._persistent_memory.clear()
            
            # Load sessions
            for session_id, session_data in data.get("sessions", {}).items():
                session = SessionData(
                    session_id=session_data["session_id"],
                    created_at=session_data.get("created_at", time.time()),
                    last_accessed=session_data.get("last_accessed", time.time()),
                    total_entries=session_data.get("total_entries", 0),
                    total_accesses=session_data.get("total_accesses", 0)
                )
                
                # Load session memory entries
                for entry_id, entry_data in session_data.get("session_memory", {}).items():
                    entry_data["memory_type"] = MemoryType(entry_data["memory_type"])
                    entry_data["scope"] = MemoryScope(entry_data["scope"])
                    entry_data["tags"] = set(entry_data["tags"])
                    
                    entry = MemoryEntry(**entry_data)
                    session.session_memory[entry_id] = entry
                
                # Rebuild indexes
                self._sessions[session_id] = session
                self._rebuild_indexes(session_id)
            
            # Load persistent memory
            for entry_id, entry_data in data.get("persistent_memory", {}).items():
                entry_data["memory_type"] = MemoryType(entry_data["memory_type"])
                entry_data["scope"] = MemoryScope(entry_data["scope"])
                entry_data["tags"] = set(entry_data["tags"])
                
                entry = MemoryEntry(**entry_data)
                self._persistent_memory[entry_id] = entry
            
            logger.info(f"Loaded memory data for {len(self._sessions)} sessions")
    
    def _load_memory_data(self) -> None:
        """Load memory data from storage file."""
        try:
            if self.storage_path and self.storage_path.exists():
                with open(self.storage_path, 'r') as f:
                    data = json.load(f)
                self.load_memory_data(data)
                logger.debug("Loaded session memory from storage")
        except Exception as e:
            logger.error(f"Failed to load session memory: {e}")
    
    def _save_memory_data(self) -> None:
        """Save memory data to storage file."""
        if not self.enable_persistence or not self.storage_path:
            return
        
        try:
            data = self.export_memory_data()
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.storage_path, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            logger.debug("Saved session memory to storage")
        except Exception as e:
            logger.error(f"Failed to save session memory: {e}")
