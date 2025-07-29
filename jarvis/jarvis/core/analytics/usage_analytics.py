"""
Usage Analytics System

Tracks user behavior, tool usage patterns, conversation flows,
and provides insights for system optimization and user experience improvement.
"""

import time
import json
import threading
from typing import Dict, Any, List, Optional, Tuple, Set
from dataclasses import dataclass, field, asdict
from collections import defaultdict, Counter
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

@dataclass
class ToolUsageEvent:
    """Individual tool usage event."""
    tool_name: str
    session_id: str
    user_id: Optional[str]
    timestamp: float
    execution_time_ms: float
    success: bool
    input_size_bytes: int = 0
    output_size_bytes: int = 0
    error_message: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ConversationEvent:
    """Conversation flow event."""
    session_id: str
    user_id: Optional[str]
    event_type: str  # 'start', 'message', 'tool_call', 'end'
    timestamp: float
    content: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class UserBehaviorPattern:
    """User behavior pattern analysis."""
    user_id: str
    most_used_tools: List[Tuple[str, int]]
    preferred_tool_chains: List[List[str]]
    avg_session_duration_minutes: float
    total_sessions: int
    success_rate: float
    peak_usage_hours: List[int]
    last_activity: float

@dataclass
class SystemUsageStats:
    """Overall system usage statistics."""
    total_sessions: int
    total_tool_calls: int
    unique_users: int
    avg_session_duration_minutes: float
    most_popular_tools: List[Tuple[str, int]]
    most_successful_tool_chains: List[Tuple[List[str], float]]
    peak_usage_hours: List[int]
    error_rate_percent: float
    timestamp: float = field(default_factory=time.time)

class UsageAnalytics:
    """
    Comprehensive usage analytics system.
    
    Features:
    - Tool usage tracking
    - Conversation flow analysis
    - User behavior patterns
    - Tool chain optimization
    - Performance insights
    - Usage trend analysis
    """
    
    def __init__(self, storage_path: Optional[Path] = None, retention_days: int = 30):
        """
        Initialize usage analytics.
        
        Args:
            storage_path: Path for persistent storage
            retention_days: Days to retain analytics data
        """
        self.storage_path = storage_path or Path("data/analytics")
        self.retention_days = retention_days
        
        # Event storage
        self._tool_events: List[ToolUsageEvent] = []
        self._conversation_events: List[ConversationEvent] = []
        
        # Real-time tracking
        self._active_sessions: Dict[str, float] = {}  # session_id -> start_time
        self._tool_chains: Dict[str, List[str]] = {}  # session_id -> tool_sequence
        self._user_sessions: defaultdict = defaultdict(list)  # user_id -> session_ids
        
        # Analytics cache
        self._cached_stats: Optional[SystemUsageStats] = None
        self._cache_timestamp: float = 0
        self._cache_ttl_seconds: float = 300  # 5 minutes
        
        # Threading
        self._lock = threading.RLock()
        
        # Ensure storage directory exists
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Load existing data
        self._load_analytics_data()
        
        logger.info(f"UsageAnalytics initialized with {len(self._tool_events)} tool events")
    
    def track_tool_usage(self, tool_name: str, session_id: str, 
                        execution_time_ms: float, success: bool,
                        user_id: Optional[str] = None,
                        input_size_bytes: int = 0,
                        output_size_bytes: int = 0,
                        error_message: Optional[str] = None,
                        context: Dict[str, Any] = None) -> None:
        """
        Track tool usage event.
        
        Args:
            tool_name: Name of the tool used
            session_id: Session identifier
            execution_time_ms: Tool execution time
            success: Whether tool execution succeeded
            user_id: Optional user identifier
            input_size_bytes: Size of input data
            output_size_bytes: Size of output data
            error_message: Error message if failed
            context: Additional context data
        """
        event = ToolUsageEvent(
            tool_name=tool_name,
            session_id=session_id,
            user_id=user_id,
            timestamp=time.time(),
            execution_time_ms=execution_time_ms,
            success=success,
            input_size_bytes=input_size_bytes,
            output_size_bytes=output_size_bytes,
            error_message=error_message,
            context=context or {}
        )
        
        with self._lock:
            self._tool_events.append(event)
            
            # Track tool chains
            if session_id not in self._tool_chains:
                self._tool_chains[session_id] = []
            self._tool_chains[session_id].append(tool_name)
            
            # Track user sessions
            if user_id:
                if session_id not in self._user_sessions[user_id]:
                    self._user_sessions[user_id].append(session_id)
            
            # Invalidate cache
            self._cached_stats = None
        
        logger.debug(f"Tracked tool usage: {tool_name} in session {session_id}")
    
    def track_conversation_event(self, session_id: str, event_type: str,
                               user_id: Optional[str] = None,
                               content: str = "",
                               metadata: Dict[str, Any] = None) -> None:
        """
        Track conversation event.
        
        Args:
            session_id: Session identifier
            event_type: Type of event ('start', 'message', 'tool_call', 'end')
            user_id: Optional user identifier
            content: Event content
            metadata: Additional metadata
        """
        event = ConversationEvent(
            session_id=session_id,
            user_id=user_id,
            event_type=event_type,
            timestamp=time.time(),
            content=content,
            metadata=metadata or {}
        )
        
        with self._lock:
            self._conversation_events.append(event)
            
            # Track active sessions
            if event_type == 'start':
                self._active_sessions[session_id] = time.time()
            elif event_type == 'end' and session_id in self._active_sessions:
                del self._active_sessions[session_id]
        
        logger.debug(f"Tracked conversation event: {event_type} in session {session_id}")
    
    def get_user_behavior_pattern(self, user_id: str) -> Optional[UserBehaviorPattern]:
        """
        Get behavior pattern for specific user.
        
        Args:
            user_id: User identifier
            
        Returns:
            User behavior pattern or None if not found
        """
        with self._lock:
            user_sessions = self._user_sessions.get(user_id, [])
            if not user_sessions:
                return None
            
            # Get user's tool events
            user_tool_events = [
                event for event in self._tool_events
                if event.user_id == user_id
            ]
            
            if not user_tool_events:
                return None
            
            # Analyze tool usage
            tool_counter = Counter(event.tool_name for event in user_tool_events)
            most_used_tools = tool_counter.most_common(10)
            
            # Analyze tool chains
            user_tool_chains = [
                self._tool_chains.get(session_id, [])
                for session_id in user_sessions
                if session_id in self._tool_chains
            ]
            
            # Find common tool chain patterns
            chain_patterns = []
            for chain in user_tool_chains:
                if len(chain) >= 2:
                    # Extract subsequences of length 2-4
                    for length in range(2, min(5, len(chain) + 1)):
                        for i in range(len(chain) - length + 1):
                            subchain = chain[i:i + length]
                            chain_patterns.append(subchain)
            
            # Get most common patterns
            pattern_counter = Counter(tuple(pattern) for pattern in chain_patterns)
            preferred_tool_chains = [list(pattern) for pattern, _ in pattern_counter.most_common(5)]
            
            # Calculate session statistics
            user_conv_events = [
                event for event in self._conversation_events
                if event.user_id == user_id
            ]
            
            session_durations = []
            for session_id in user_sessions:
                session_events = [e for e in user_conv_events if e.session_id == session_id]
                if len(session_events) >= 2:
                    start_time = min(e.timestamp for e in session_events)
                    end_time = max(e.timestamp for e in session_events)
                    duration_minutes = (end_time - start_time) / 60
                    session_durations.append(duration_minutes)
            
            avg_session_duration = sum(session_durations) / len(session_durations) if session_durations else 0
            
            # Calculate success rate
            successful_tools = sum(1 for event in user_tool_events if event.success)
            success_rate = (successful_tools / len(user_tool_events) * 100) if user_tool_events else 0
            
            # Analyze peak usage hours
            usage_hours = [
                int(time.localtime(event.timestamp).tm_hour)
                for event in user_tool_events
            ]
            hour_counter = Counter(usage_hours)
            peak_usage_hours = [hour for hour, _ in hour_counter.most_common(3)]
            
            # Last activity
            last_activity = max(event.timestamp for event in user_tool_events)
            
            return UserBehaviorPattern(
                user_id=user_id,
                most_used_tools=most_used_tools,
                preferred_tool_chains=preferred_tool_chains,
                avg_session_duration_minutes=avg_session_duration,
                total_sessions=len(user_sessions),
                success_rate=success_rate,
                peak_usage_hours=peak_usage_hours,
                last_activity=last_activity
            )
    
    def get_system_usage_stats(self, force_refresh: bool = False) -> SystemUsageStats:
        """
        Get overall system usage statistics.
        
        Args:
            force_refresh: Force refresh of cached stats
            
        Returns:
            System usage statistics
        """
        current_time = time.time()
        
        # Check cache
        if (not force_refresh and 
            self._cached_stats and 
            current_time - self._cache_timestamp < self._cache_ttl_seconds):
            return self._cached_stats
        
        with self._lock:
            # Calculate statistics
            total_sessions = len(set(event.session_id for event in self._tool_events))
            total_tool_calls = len(self._tool_events)
            unique_users = len(set(event.user_id for event in self._tool_events if event.user_id))
            
            # Tool popularity
            tool_counter = Counter(event.tool_name for event in self._tool_events)
            most_popular_tools = tool_counter.most_common(10)
            
            # Session durations
            session_durations = []
            for session_id in set(event.session_id for event in self._conversation_events):
                session_events = [e for e in self._conversation_events if e.session_id == session_id]
                if len(session_events) >= 2:
                    start_time = min(e.timestamp for e in session_events)
                    end_time = max(e.timestamp for e in session_events)
                    duration_minutes = (end_time - start_time) / 60
                    session_durations.append(duration_minutes)
            
            avg_session_duration = sum(session_durations) / len(session_durations) if session_durations else 0
            
            # Tool chain success analysis
            successful_chains = []
            for session_id, chain in self._tool_chains.items():
                if len(chain) >= 2:
                    session_events = [e for e in self._tool_events if e.session_id == session_id]
                    success_rate = sum(1 for e in session_events if e.success) / len(session_events)
                    if success_rate >= 0.8:  # 80% success threshold
                        successful_chains.append((chain, success_rate))
            
            # Find most common successful patterns
            chain_counter = Counter(tuple(chain) for chain, _ in successful_chains)
            most_successful_tool_chains = [
                (list(pattern), sum(rate for chain, rate in successful_chains if tuple(chain) == pattern) / 
                 sum(1 for chain, _ in successful_chains if tuple(chain) == pattern))
                for pattern, _ in chain_counter.most_common(5)
            ]
            
            # Peak usage hours
            usage_hours = [
                int(time.localtime(event.timestamp).tm_hour)
                for event in self._tool_events
            ]
            hour_counter = Counter(usage_hours)
            peak_usage_hours = [hour for hour, _ in hour_counter.most_common(3)]
            
            # Error rate
            successful_tools = sum(1 for event in self._tool_events if event.success)
            error_rate = ((total_tool_calls - successful_tools) / total_tool_calls * 100) if total_tool_calls > 0 else 0
            
            # Create stats object
            stats = SystemUsageStats(
                total_sessions=total_sessions,
                total_tool_calls=total_tool_calls,
                unique_users=unique_users,
                avg_session_duration_minutes=avg_session_duration,
                most_popular_tools=most_popular_tools,
                most_successful_tool_chains=most_successful_tool_chains,
                peak_usage_hours=peak_usage_hours,
                error_rate_percent=error_rate
            )
            
            # Cache results
            self._cached_stats = stats
            self._cache_timestamp = current_time
            
            return stats
    
    def get_tool_chain_recommendations(self, current_tools: List[str], limit: int = 5) -> List[Tuple[str, float]]:
        """
        Get tool recommendations based on current tool chain.
        
        Args:
            current_tools: Current tool sequence
            limit: Maximum number of recommendations
            
        Returns:
            List of (tool_name, confidence_score) tuples
        """
        if not current_tools:
            return []
        
        with self._lock:
            # Find chains that start with current tools
            matching_chains = []
            for chain in self._tool_chains.values():
                if len(chain) > len(current_tools):
                    # Check if chain starts with current tools
                    if chain[:len(current_tools)] == current_tools:
                        next_tool = chain[len(current_tools)]
                        matching_chains.append(next_tool)
            
            if not matching_chains:
                return []
            
            # Count occurrences and calculate confidence
            tool_counter = Counter(matching_chains)
            total_matches = len(matching_chains)
            
            recommendations = []
            for tool, count in tool_counter.most_common(limit):
                confidence = count / total_matches
                recommendations.append((tool, confidence))
            
            return recommendations
    
    def cleanup_old_data(self) -> None:
        """Remove analytics data older than retention period."""
        cutoff_time = time.time() - (self.retention_days * 24 * 3600)
        
        with self._lock:
            # Clean tool events
            self._tool_events = [
                event for event in self._tool_events
                if event.timestamp > cutoff_time
            ]
            
            # Clean conversation events
            self._conversation_events = [
                event for event in self._conversation_events
                if event.timestamp > cutoff_time
            ]
            
            # Invalidate cache
            self._cached_stats = None
        
        logger.info(f"Cleaned up analytics data older than {self.retention_days} days")
    
    def save_analytics_data(self) -> None:
        """Save analytics data to persistent storage."""
        try:
            data = {
                'tool_events': [asdict(event) for event in self._tool_events],
                'conversation_events': [asdict(event) for event in self._conversation_events],
                'tool_chains': dict(self._tool_chains),
                'user_sessions': dict(self._user_sessions),
                'timestamp': time.time()
            }
            
            analytics_file = self.storage_path / "usage_analytics.json"
            with open(analytics_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"Saved analytics data to {analytics_file}")
            
        except Exception as e:
            logger.error(f"Failed to save analytics data: {e}")
    
    def _load_analytics_data(self) -> None:
        """Load analytics data from persistent storage."""
        try:
            analytics_file = self.storage_path / "usage_analytics.json"
            if not analytics_file.exists():
                return
            
            with open(analytics_file, 'r') as f:
                data = json.load(f)
            
            # Load tool events
            self._tool_events = [
                ToolUsageEvent(**event_data)
                for event_data in data.get('tool_events', [])
            ]
            
            # Load conversation events
            self._conversation_events = [
                ConversationEvent(**event_data)
                for event_data in data.get('conversation_events', [])
            ]
            
            # Load tool chains
            self._tool_chains = data.get('tool_chains', {})
            
            # Load user sessions
            user_sessions_data = data.get('user_sessions', {})
            self._user_sessions = defaultdict(list)
            for user_id, sessions in user_sessions_data.items():
                self._user_sessions[user_id] = sessions
            
            logger.info(f"Loaded analytics data from {analytics_file}")
            
        except Exception as e:
            logger.error(f"Failed to load analytics data: {e}")

# Global usage analytics instance
usage_analytics = UsageAnalytics()
