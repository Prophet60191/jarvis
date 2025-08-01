"""
Session Saving Data Models

Defines the data structures for saved conversation sessions.
"""

import uuid
from datetime import datetime
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum


class SessionState(Enum):
    """Session state enumeration."""
    UNSAVED = "unsaved"           # Regular session, not saved yet
    SAVED_ACTIVE = "saved_active" # Saved session, still active/continuing  
    SAVED_CLOSED = "saved_closed" # Saved session, ended/archived
    RECALLED = "recalled"         # Previously saved session, now active again


@dataclass
class SessionMessage:
    """Individual message in a conversation session."""
    content: str
    role: str  # "user" or "assistant"
    timestamp: datetime
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "content": self.content,
            "role": self.role,
            "timestamp": self.timestamp.isoformat(),
            "message_id": self.message_id
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SessionMessage':
        """Create from dictionary."""
        return cls(
            content=data["content"],
            role=data["role"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            message_id=data["message_id"]
        )


@dataclass
class SavedSession:
    """Complete saved conversation session."""
    name: str
    session_id: str
    timestamp: datetime
    full_conversation: List[SessionMessage]
    state: SessionState
    prompt_count: int = 0
    tags: List[str] = field(default_factory=list)
    last_updated: Optional[datetime] = None
    
    def __post_init__(self):
        """Initialize computed fields."""
        if self.prompt_count == 0:
            self.prompt_count = len(self.full_conversation)
        if self.last_updated is None:
            self.last_updated = self.timestamp
    
    def add_message(self, message: SessionMessage) -> None:
        """Add a new message to the session."""
        self.full_conversation.append(message)
        self.prompt_count = len(self.full_conversation)
        self.last_updated = datetime.now()
    
    def get_conversation_text(self) -> str:
        """Get formatted conversation text for storage/display."""
        lines = []
        for msg in self.full_conversation:
            role_prefix = "👤 User" if msg.role == "user" else "🤖 Jarvis"
            timestamp_str = msg.timestamp.strftime("%H:%M")
            lines.append(f"[{timestamp_str}] {role_prefix}: {msg.content}")
        return "\n".join(lines)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "name": self.name,
            "session_id": self.session_id,
            "timestamp": self.timestamp.isoformat(),
            "full_conversation": [msg.to_dict() for msg in self.full_conversation],
            "state": self.state.value,
            "prompt_count": self.prompt_count,
            "tags": self.tags,
            "last_updated": self.last_updated.isoformat() if self.last_updated else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SavedSession':
        """Create from dictionary."""
        return cls(
            name=data["name"],
            session_id=data["session_id"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            full_conversation=[SessionMessage.from_dict(msg) for msg in data["full_conversation"]],
            state=SessionState(data["state"]),
            prompt_count=data["prompt_count"],
            tags=data.get("tags", []),
            last_updated=datetime.fromisoformat(data["last_updated"]) if data.get("last_updated") else None
        )


@dataclass
class SessionSaveResult:
    """Result of a session save operation."""
    success: bool
    message: str
    session_id: Optional[str] = None
    error: Optional[str] = None
