"""
Context Management System

This package provides comprehensive context management for Jarvis,
including conversation state, user preferences, tool states, and
session memory management.

Components:
- ContextManager: Central context coordination
- ConversationState: Conversation state tracking
- ToolStateTracker: Tool execution state management
- UserPreferenceEngine: User behavior learning and adaptation
- SessionMemory: Session-specific data storage
"""

from .context_manager import ContextManager, Context, ContextScope
from .conversation_state import ConversationState, ConversationTopic, IntentHistory
from .tool_state_tracker import ToolStateTracker, ToolState, ToolExecutionContext
from .user_preference_engine import UserPreferenceEngine, UserPreference, PreferenceType
from .session_memory import SessionMemory, SessionData, MemoryScope

__all__ = [
    # Core context management
    "ContextManager",
    "Context",
    "ContextScope",
    
    # Conversation state
    "ConversationState",
    "ConversationTopic",
    "IntentHistory",
    
    # Tool state tracking
    "ToolStateTracker",
    "ToolState",
    "ToolExecutionContext",
    
    # User preferences
    "UserPreferenceEngine",
    "UserPreference",
    "PreferenceType",
    
    # Session memory
    "SessionMemory",
    "SessionData",
    "MemoryScope"
]
