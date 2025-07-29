"""
Conversation State Management

Tracks conversation flow, topics, intents, and dialogue state
across interactions within a session.
"""

import time
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from collections import deque
import threading

logger = logging.getLogger(__name__)

class ConversationPhase(Enum):
    """Phases of conversation flow."""
    GREETING = "greeting"
    CLARIFICATION = "clarification"
    TASK_EXECUTION = "task_execution"
    FOLLOW_UP = "follow_up"
    CLOSING = "closing"
    ERROR_HANDLING = "error_handling"

class IntentConfidence(Enum):
    """Confidence levels for intent detection."""
    HIGH = "high"      # > 0.8
    MEDIUM = "medium"  # 0.5 - 0.8
    LOW = "low"        # < 0.5
    UNKNOWN = "unknown"

    @classmethod
    def from_string(cls, value: str) -> 'IntentConfidence':
        """Safely create IntentConfidence from string value."""
        try:
            return cls(value)
        except ValueError:
            # If the string doesn't match any enum value, return UNKNOWN
            return cls.UNKNOWN

    @classmethod
    def from_score(cls, score: float) -> 'IntentConfidence':
        """Create IntentConfidence from numeric score."""
        if score > 0.8:
            return cls.HIGH
        elif score >= 0.5:
            return cls.MEDIUM
        else:
            return cls.LOW

@dataclass
class ConversationTopic:
    """Represents a conversation topic."""
    name: str
    keywords: List[str] = field(default_factory=list)
    confidence: float = 1.0
    started_at: float = field(default_factory=time.time)
    last_mentioned: float = field(default_factory=time.time)
    mention_count: int = 1
    related_topics: List[str] = field(default_factory=list)
    
    def update_mention(self) -> None:
        """Update topic mention statistics."""
        self.last_mentioned = time.time()
        self.mention_count += 1

@dataclass
class IntentHistory:
    """Represents an intent in the conversation history."""
    intent: str
    confidence: IntentConfidence
    timestamp: float = field(default_factory=time.time)
    context: Dict[str, Any] = field(default_factory=dict)
    fulfilled: bool = False
    tools_used: List[str] = field(default_factory=list)
    
    def mark_fulfilled(self, tools_used: List[str] = None) -> None:
        """Mark intent as fulfilled."""
        self.fulfilled = True
        if tools_used:
            self.tools_used.extend(tools_used)

@dataclass
class ConversationFlow:
    """Represents a step in the conversation flow."""
    phase: ConversationPhase
    user_input: str
    system_response: str
    timestamp: float = field(default_factory=time.time)
    duration_ms: float = 0.0
    success: bool = True
    error_message: Optional[str] = None
    tools_invoked: List[str] = field(default_factory=list)
    
    def set_duration(self, start_time: float) -> None:
        """Set the duration of this conversation step."""
        self.duration_ms = (time.time() - start_time) * 1000

@dataclass
class SessionConversationState:
    """Complete conversation state for a session."""
    session_id: str
    current_topic: Optional[ConversationTopic] = None
    current_phase: ConversationPhase = ConversationPhase.GREETING
    intent_history: List[IntentHistory] = field(default_factory=list)
    conversation_flow: List[ConversationFlow] = field(default_factory=list)
    topic_history: Dict[str, ConversationTopic] = field(default_factory=dict)
    context_stack: List[Dict[str, Any]] = field(default_factory=list)
    
    # Statistics
    total_interactions: int = 0
    successful_interactions: int = 0
    average_response_time: float = 0.0
    created_at: float = field(default_factory=time.time)
    last_activity: float = field(default_factory=time.time)
    
    def update_activity(self) -> None:
        """Update last activity timestamp."""
        self.last_activity = time.time()

class ConversationState:
    """
    Manages conversation state across all sessions.
    
    This component tracks conversation flow, topics, intents, and dialogue
    state to provide context-aware responses and maintain conversation
    continuity.
    """
    
    def __init__(self, max_history_length: int = 100):
        """
        Initialize conversation state manager.
        
        Args:
            max_history_length: Maximum length of conversation history to maintain
        """
        self._session_states: Dict[str, SessionConversationState] = {}
        self._lock = threading.RLock()
        
        # Configuration
        self.max_history_length = max_history_length
        self.topic_similarity_threshold = 0.7
        self.intent_confidence_threshold = 0.5
        
        # Topic detection patterns (simplified - could be enhanced with NLP)
        self.topic_patterns = {
            "file_operations": ["file", "document", "folder", "directory", "save", "open", "read", "write"],
            "web_search": ["search", "web", "internet", "google", "find", "lookup"],
            "data_analysis": ["analyze", "data", "chart", "graph", "statistics", "report"],
            "system_operations": ["system", "process", "command", "terminal", "shell"],
            "communication": ["email", "message", "send", "contact", "call"],
            "scheduling": ["calendar", "schedule", "appointment", "meeting", "reminder"],
            "entertainment": ["music", "video", "game", "movie", "play"],
            "productivity": ["task", "todo", "organize", "plan", "manage"]
        }
        
        logger.info("ConversationState initialized")
    
    def initialize_session(self, session_id: str) -> None:
        """
        Initialize conversation state for a new session.
        
        Args:
            session_id: Session identifier
        """
        with self._lock:
            if session_id not in self._session_states:
                self._session_states[session_id] = SessionConversationState(session_id=session_id)
                logger.debug(f"Initialized conversation state for session {session_id}")
    
    def get_current_state(self, session_id: str) -> Optional[SessionConversationState]:
        """
        Get current conversation state for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Optional[SessionConversationState]: Current state or None if not found
        """
        with self._lock:
            return self._session_states.get(session_id)
    
    def update_topic(self, session_id: str, topic_name: str, 
                    keywords: List[str] = None, confidence: float = 1.0) -> None:
        """
        Update the current conversation topic.
        
        Args:
            session_id: Session identifier
            topic_name: Name of the topic
            keywords: Optional keywords associated with the topic
            confidence: Confidence in topic detection
        """
        with self._lock:
            self.initialize_session(session_id)
            state = self._session_states[session_id]
            
            # Check if topic already exists in history
            if topic_name in state.topic_history:
                topic = state.topic_history[topic_name]
                topic.update_mention()
                topic.confidence = max(topic.confidence, confidence)
                if keywords:
                    topic.keywords.extend(keywords)
                    topic.keywords = list(set(topic.keywords))  # Remove duplicates
            else:
                # Create new topic
                topic = ConversationTopic(
                    name=topic_name,
                    keywords=keywords or [],
                    confidence=confidence
                )
                state.topic_history[topic_name] = topic
            
            # Update current topic
            state.current_topic = topic
            state.update_activity()
            
            logger.debug(f"Updated topic for session {session_id}: {topic_name}")
    
    def detect_topic_from_input(self, session_id: str, user_input: str) -> Optional[str]:
        """
        Detect conversation topic from user input.
        
        Args:
            session_id: Session identifier
            user_input: User's input text
            
        Returns:
            Optional[str]: Detected topic name or None
        """
        user_input_lower = user_input.lower()
        topic_scores = {}
        
        # Score topics based on keyword matches
        for topic_name, keywords in self.topic_patterns.items():
            score = 0
            for keyword in keywords:
                if keyword in user_input_lower:
                    score += 1
            
            if score > 0:
                topic_scores[topic_name] = score / len(keywords)  # Normalize by keyword count
        
        # Find best matching topic
        if topic_scores:
            best_topic = max(topic_scores.items(), key=lambda x: x[1])
            if best_topic[1] >= self.topic_similarity_threshold:
                self.update_topic(session_id, best_topic[0], confidence=best_topic[1])
                return best_topic[0]
        
        return None
    
    def add_intent(self, session_id: str, intent: str, 
                  confidence: IntentConfidence = IntentConfidence.MEDIUM,
                  context: Dict[str, Any] = None) -> None:
        """
        Add an intent to the conversation history.
        
        Args:
            session_id: Session identifier
            intent: Intent name
            confidence: Confidence level
            context: Optional context information
        """
        with self._lock:
            self.initialize_session(session_id)
            state = self._session_states[session_id]
            
            intent_entry = IntentHistory(
                intent=intent,
                confidence=confidence,
                context=context or {}
            )
            
            state.intent_history.append(intent_entry)
            
            # Maintain history length
            if len(state.intent_history) > self.max_history_length:
                state.intent_history = state.intent_history[-self.max_history_length:]
            
            state.update_activity()
            
            logger.debug(f"Added intent for session {session_id}: {intent}")
    
    def mark_intent_fulfilled(self, session_id: str, intent: str, 
                            tools_used: List[str] = None) -> bool:
        """
        Mark an intent as fulfilled.
        
        Args:
            session_id: Session identifier
            intent: Intent to mark as fulfilled
            tools_used: Optional list of tools used to fulfill the intent
            
        Returns:
            bool: True if intent was found and marked
        """
        with self._lock:
            state = self._session_states.get(session_id)
            if not state:
                return False
            
            # Find the most recent unfulfilled intent
            for intent_entry in reversed(state.intent_history):
                if intent_entry.intent == intent and not intent_entry.fulfilled:
                    intent_entry.mark_fulfilled(tools_used or [])
                    logger.debug(f"Marked intent '{intent}' as fulfilled for session {session_id}")
                    return True
            
            return False
    
    def update_conversation_phase(self, session_id: str, phase: ConversationPhase) -> None:
        """
        Update the current conversation phase.
        
        Args:
            session_id: Session identifier
            phase: New conversation phase
        """
        with self._lock:
            self.initialize_session(session_id)
            state = self._session_states[session_id]
            
            state.current_phase = phase
            state.update_activity()
            
            logger.debug(f"Updated conversation phase for session {session_id}: {phase.value}")
    
    def add_conversation_step(self, session_id: str, user_input: str, 
                            system_response: str, phase: ConversationPhase = None,
                            success: bool = True, error_message: str = None,
                            tools_invoked: List[str] = None,
                            start_time: float = None) -> None:
        """
        Add a step to the conversation flow.
        
        Args:
            session_id: Session identifier
            user_input: User's input
            system_response: System's response
            phase: Conversation phase (defaults to current phase)
            success: Whether the interaction was successful
            error_message: Optional error message
            tools_invoked: Optional list of tools invoked
            start_time: Optional start time for duration calculation
        """
        with self._lock:
            self.initialize_session(session_id)
            state = self._session_states[session_id]
            
            if phase is None:
                phase = state.current_phase
            
            flow_step = ConversationFlow(
                phase=phase,
                user_input=user_input,
                system_response=system_response,
                success=success,
                error_message=error_message,
                tools_invoked=tools_invoked or []
            )
            
            if start_time:
                flow_step.set_duration(start_time)
            
            state.conversation_flow.append(flow_step)
            
            # Maintain flow history length
            if len(state.conversation_flow) > self.max_history_length:
                state.conversation_flow = state.conversation_flow[-self.max_history_length:]
            
            # Update statistics
            state.total_interactions += 1
            if success:
                state.successful_interactions += 1
            
            # Update average response time
            if flow_step.duration_ms > 0:
                total_time = state.average_response_time * (state.total_interactions - 1) + flow_step.duration_ms
                state.average_response_time = total_time / state.total_interactions
            
            state.update_activity()
            
            # Auto-detect topic from user input
            self.detect_topic_from_input(session_id, user_input)
            
            logger.debug(f"Added conversation step for session {session_id}")
    
    def get_recent_context(self, session_id: str, steps: int = 5) -> List[Dict[str, Any]]:
        """
        Get recent conversation context.
        
        Args:
            session_id: Session identifier
            steps: Number of recent steps to include
            
        Returns:
            List[Dict[str, Any]]: Recent conversation context
        """
        with self._lock:
            state = self._session_states.get(session_id)
            if not state:
                return []
            
            recent_flow = state.conversation_flow[-steps:] if state.conversation_flow else []
            
            context = []
            for step in recent_flow:
                context.append({
                    "user_input": step.user_input,
                    "system_response": step.system_response,
                    "phase": step.phase.value,
                    "timestamp": step.timestamp,
                    "success": step.success,
                    "tools_invoked": step.tools_invoked
                })
            
            return context
    
    def get_unfulfilled_intents(self, session_id: str) -> List[IntentHistory]:
        """
        Get list of unfulfilled intents for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            List[IntentHistory]: Unfulfilled intents
        """
        with self._lock:
            state = self._session_states.get(session_id)
            if not state:
                return []
            
            return [intent for intent in state.intent_history if not intent.fulfilled]
    
    def get_session_summary(self, session_id: str) -> Dict[str, Any]:
        """
        Get conversation summary for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Dict[str, Any]: Session conversation summary
        """
        with self._lock:
            state = self._session_states.get(session_id)
            if not state:
                return {"error": "Session not found"}
            
            # Calculate success rate
            success_rate = (state.successful_interactions / max(state.total_interactions, 1)) * 100
            
            # Get most common topics
            topic_mentions = {
                name: topic.mention_count 
                for name, topic in state.topic_history.items()
            }
            most_common_topics = sorted(topic_mentions.items(), key=lambda x: x[1], reverse=True)[:5]
            
            # Get recent intents
            recent_intents = [
                {"intent": intent.intent, "fulfilled": intent.fulfilled, "confidence": intent.confidence.value}
                for intent in state.intent_history[-10:]
            ]
            
            return {
                "session_id": session_id,
                "current_topic": state.current_topic.name if state.current_topic else None,
                "current_phase": state.current_phase.value,
                "total_interactions": state.total_interactions,
                "successful_interactions": state.successful_interactions,
                "success_rate": success_rate,
                "average_response_time_ms": state.average_response_time,
                "session_duration_hours": (state.last_activity - state.created_at) / 3600,
                "most_common_topics": most_common_topics,
                "recent_intents": recent_intents,
                "unfulfilled_intents": len(self.get_unfulfilled_intents(session_id))
            }
    
    def clear_session(self, session_id: str) -> None:
        """
        Clear conversation state for a session.
        
        Args:
            session_id: Session identifier
        """
        with self._lock:
            if session_id in self._session_states:
                del self._session_states[session_id]
                logger.debug(f"Cleared conversation state for session {session_id}")
    
    def export_state_data(self) -> Dict[str, Any]:
        """Export conversation state data for persistence."""
        with self._lock:
            return {
                "session_states": {
                    session_id: {
                        "session_id": state.session_id,
                        "current_topic": state.current_topic.__dict__ if state.current_topic else None,
                        "current_phase": state.current_phase.value,
                        "intent_history": [intent.__dict__ for intent in state.intent_history],
                        "conversation_flow": [
                            {
                                **flow.__dict__,
                                "phase": flow.phase.value
                            }
                            for flow in state.conversation_flow
                        ],
                        "topic_history": {
                            name: topic.__dict__ for name, topic in state.topic_history.items()
                        },
                        "context_stack": state.context_stack,
                        "total_interactions": state.total_interactions,
                        "successful_interactions": state.successful_interactions,
                        "average_response_time": state.average_response_time,
                        "created_at": state.created_at,
                        "last_activity": state.last_activity
                    }
                    for session_id, state in self._session_states.items()
                }
            }
    
    def load_state_data(self, data: Dict[str, Any]) -> None:
        """Load conversation state data from persistence."""
        with self._lock:
            self._session_states.clear()
            
            for session_id, state_data in data.get("session_states", {}).items():
                # Reconstruct state object
                state = SessionConversationState(session_id=session_id)
                
                # Load basic fields
                state.current_phase = ConversationPhase(state_data.get("current_phase", "greeting"))
                state.total_interactions = state_data.get("total_interactions", 0)
                state.successful_interactions = state_data.get("successful_interactions", 0)
                state.average_response_time = state_data.get("average_response_time", 0.0)
                state.created_at = state_data.get("created_at", time.time())
                state.last_activity = state_data.get("last_activity", time.time())
                state.context_stack = state_data.get("context_stack", [])
                
                # Load current topic
                if state_data.get("current_topic"):
                    topic_data = state_data["current_topic"]
                    state.current_topic = ConversationTopic(**topic_data)
                
                # Load intent history
                for intent_data in state_data.get("intent_history", []):
                    intent_data["confidence"] = IntentConfidence(intent_data["confidence"])
                    state.intent_history.append(IntentHistory(**intent_data))
                
                # Load conversation flow
                for flow_data in state_data.get("conversation_flow", []):
                    flow_data["phase"] = ConversationPhase(flow_data["phase"])
                    state.conversation_flow.append(ConversationFlow(**flow_data))
                
                # Load topic history
                for topic_name, topic_data in state_data.get("topic_history", {}).items():
                    state.topic_history[topic_name] = ConversationTopic(**topic_data)
                
                self._session_states[session_id] = state
            
            logger.info(f"Loaded conversation state for {len(self._session_states)} sessions")
