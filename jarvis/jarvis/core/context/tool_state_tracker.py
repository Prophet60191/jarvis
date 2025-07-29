"""
Tool State Tracker

Tracks the state of active tools and their execution context
across sessions and interactions.
"""

import time
import logging
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict
import threading

logger = logging.getLogger(__name__)

class ToolState(Enum):
    """States that a tool can be in."""
    INACTIVE = "inactive"
    INITIALIZING = "initializing"
    ACTIVE = "active"
    EXECUTING = "executing"
    WAITING = "waiting"
    COMPLETED = "completed"
    FAILED = "failed"
    SUSPENDED = "suspended"
    CLEANUP = "cleanup"

class ToolPriority(Enum):
    """Priority levels for tool execution."""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class ToolExecutionContext:
    """Context information for tool execution."""
    tool_name: str
    session_id: str
    execution_id: str
    state: ToolState = ToolState.INACTIVE
    priority: ToolPriority = ToolPriority.NORMAL
    
    # Execution details
    parameters: Dict[str, Any] = field(default_factory=dict)
    result: Optional[Any] = None
    error_message: Optional[str] = None
    
    # Timing information
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    last_activity: float = field(default_factory=time.time)
    
    # Dependencies and relationships
    depends_on: List[str] = field(default_factory=list)  # Tool execution IDs
    blocks: List[str] = field(default_factory=list)      # Tool execution IDs
    parent_execution: Optional[str] = None
    child_executions: List[str] = field(default_factory=list)
    
    # Resource usage
    memory_usage_mb: float = 0.0
    cpu_usage_percent: float = 0.0
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def get_duration(self) -> float:
        """Get execution duration in seconds."""
        if self.started_at and self.completed_at:
            return self.completed_at - self.started_at
        elif self.started_at:
            return time.time() - self.started_at
        return 0.0
    
    def update_activity(self) -> None:
        """Update last activity timestamp."""
        self.last_activity = time.time()
    
    def is_active(self) -> bool:
        """Check if tool is in an active state."""
        return self.state in [ToolState.ACTIVE, ToolState.EXECUTING, ToolState.WAITING]
    
    def is_completed(self) -> bool:
        """Check if tool execution is completed."""
        return self.state in [ToolState.COMPLETED, ToolState.FAILED]

class ToolStateTracker:
    """
    Tracks tool states and execution contexts across sessions.
    
    This component maintains the state of all active tools, their
    execution contexts, dependencies, and resource usage.
    """
    
    def __init__(self, max_history_per_session: int = 1000):
        """
        Initialize the tool state tracker.
        
        Args:
            max_history_per_session: Maximum execution history per session
        """
        # Session-based tool tracking
        self._session_tools: Dict[str, Dict[str, ToolExecutionContext]] = defaultdict(dict)
        self._session_history: Dict[str, List[ToolExecutionContext]] = defaultdict(list)
        
        # Global tool tracking
        self._active_executions: Dict[str, ToolExecutionContext] = {}
        self._execution_queue: List[str] = []  # Execution IDs in queue
        
        # Dependencies and relationships
        self._dependency_graph: Dict[str, Set[str]] = defaultdict(set)
        self._blocking_graph: Dict[str, Set[str]] = defaultdict(set)
        
        # Configuration
        self.max_history_per_session = max_history_per_session
        self.execution_timeout = 300  # 5 minutes default timeout
        self.cleanup_interval = 3600  # 1 hour cleanup interval
        
        # Thread safety
        self._lock = threading.RLock()
        
        logger.info("ToolStateTracker initialized")
    
    def initialize_session(self, session_id: str) -> None:
        """
        Initialize tool tracking for a session.
        
        Args:
            session_id: Session identifier
        """
        with self._lock:
            if session_id not in self._session_tools:
                self._session_tools[session_id] = {}
                self._session_history[session_id] = []
                logger.debug(f"Initialized tool tracking for session {session_id}")
    
    def start_tool_execution(self, session_id: str, tool_name: str,
                           parameters: Dict[str, Any] = None,
                           priority: ToolPriority = ToolPriority.NORMAL,
                           depends_on: List[str] = None) -> str:
        """
        Start tracking a tool execution.
        
        Args:
            session_id: Session identifier
            tool_name: Name of the tool
            parameters: Tool parameters
            priority: Execution priority
            depends_on: List of execution IDs this depends on
            
        Returns:
            str: Execution ID
        """
        execution_id = f"{session_id}_{tool_name}_{int(time.time() * 1000)}"
        
        with self._lock:
            self.initialize_session(session_id)
            
            # Create execution context
            context = ToolExecutionContext(
                tool_name=tool_name,
                session_id=session_id,
                execution_id=execution_id,
                state=ToolState.INITIALIZING,
                priority=priority,
                parameters=parameters or {},
                depends_on=depends_on or []
            )
            
            # Store in session and global tracking
            self._session_tools[session_id][execution_id] = context
            self._active_executions[execution_id] = context
            
            # Update dependency graph
            if depends_on:
                for dep_id in depends_on:
                    self._dependency_graph[execution_id].add(dep_id)
                    self._blocking_graph[dep_id].add(execution_id)
            
            # Add to execution queue if no dependencies or dependencies are met
            if self._can_execute(execution_id):
                self._execution_queue.append(execution_id)
                context.state = ToolState.ACTIVE
            
            logger.debug(f"Started tool execution {execution_id} for {tool_name}")
            return execution_id
    
    def update_tool_state(self, execution_id: str, new_state: ToolState,
                         result: Any = None, error_message: str = None,
                         metadata: Dict[str, Any] = None) -> bool:
        """
        Update the state of a tool execution.
        
        Args:
            execution_id: Execution identifier
            new_state: New state
            result: Optional execution result
            error_message: Optional error message
            metadata: Optional metadata updates
            
        Returns:
            bool: True if update successful
        """
        with self._lock:
            if execution_id not in self._active_executions:
                logger.warning(f"Execution {execution_id} not found")
                return False
            
            context = self._active_executions[execution_id]
            old_state = context.state
            
            # Update state and timing
            context.state = new_state
            context.update_activity()
            
            if new_state == ToolState.EXECUTING and not context.started_at:
                context.started_at = time.time()
            elif new_state in [ToolState.COMPLETED, ToolState.FAILED]:
                context.completed_at = time.time()
                if result is not None:
                    context.result = result
                if error_message:
                    context.error_message = error_message
            
            # Update metadata
            if metadata:
                context.metadata.update(metadata)
            
            # Handle state transitions
            self._handle_state_transition(context, old_state, new_state)
            
            logger.debug(f"Updated tool {execution_id} state: {old_state.value} -> {new_state.value}")
            return True
    
    def complete_tool_execution(self, execution_id: str, result: Any = None,
                              success: bool = True, error_message: str = None) -> bool:
        """
        Complete a tool execution.
        
        Args:
            execution_id: Execution identifier
            result: Execution result
            success: Whether execution was successful
            error_message: Optional error message
            
        Returns:
            bool: True if completion successful
        """
        final_state = ToolState.COMPLETED if success else ToolState.FAILED
        
        with self._lock:
            success = self.update_tool_state(
                execution_id, final_state, result, error_message
            )
            
            if success:
                # Move to history
                context = self._active_executions[execution_id]
                session_id = context.session_id
                
                self._session_history[session_id].append(context)
                
                # Maintain history size
                if len(self._session_history[session_id]) > self.max_history_per_session:
                    self._session_history[session_id] = self._session_history[session_id][-self.max_history_per_session:]
                
                # Clean up active tracking
                del self._active_executions[execution_id]
                if execution_id in self._session_tools[session_id]:
                    del self._session_tools[session_id][execution_id]
                
                # Update dependency graph and check for newly executable tools
                self._cleanup_dependencies(execution_id)
                self._check_dependent_tools(execution_id)
                
                logger.debug(f"Completed tool execution {execution_id}")
            
            return success
    
    def get_tool_state(self, session_id: str, tool_name: str) -> Optional[ToolState]:
        """
        Get the current state of a tool in a session.
        
        Args:
            session_id: Session identifier
            tool_name: Tool name
            
        Returns:
            Optional[ToolState]: Current state or None if not found
        """
        with self._lock:
            if session_id not in self._session_tools:
                return None
            
            # Find most recent execution of this tool
            for context in reversed(list(self._session_tools[session_id].values())):
                if context.tool_name == tool_name:
                    return context.state
            
            return None
    
    def get_active_tools(self, session_id: str) -> List[str]:
        """
        Get list of active tools in a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            List[str]: List of active tool names
        """
        with self._lock:
            if session_id not in self._session_tools:
                return []
            
            active_tools = []
            for context in self._session_tools[session_id].values():
                if context.is_active():
                    active_tools.append(context.tool_name)
            
            return list(set(active_tools))  # Remove duplicates
    
    def get_execution_context(self, execution_id: str) -> Optional[ToolExecutionContext]:
        """
        Get execution context for a specific execution.
        
        Args:
            execution_id: Execution identifier
            
        Returns:
            Optional[ToolExecutionContext]: Execution context or None
        """
        with self._lock:
            return self._active_executions.get(execution_id)
    
    def get_session_executions(self, session_id: str, 
                             include_history: bool = False) -> List[ToolExecutionContext]:
        """
        Get all executions for a session.
        
        Args:
            session_id: Session identifier
            include_history: Whether to include completed executions
            
        Returns:
            List[ToolExecutionContext]: List of execution contexts
        """
        with self._lock:
            executions = []
            
            # Add active executions
            if session_id in self._session_tools:
                executions.extend(self._session_tools[session_id].values())
            
            # Add history if requested
            if include_history and session_id in self._session_history:
                executions.extend(self._session_history[session_id])
            
            # Sort by creation time
            executions.sort(key=lambda x: x.created_at)
            
            return executions
    
    def get_tool_dependencies(self, execution_id: str) -> Dict[str, Any]:
        """
        Get dependency information for a tool execution.
        
        Args:
            execution_id: Execution identifier
            
        Returns:
            Dict[str, Any]: Dependency information
        """
        with self._lock:
            context = self._active_executions.get(execution_id)
            if not context:
                return {"error": "Execution not found"}
            
            return {
                "execution_id": execution_id,
                "depends_on": context.depends_on,
                "blocks": list(self._blocking_graph.get(execution_id, set())),
                "can_execute": self._can_execute(execution_id),
                "dependency_status": {
                    dep_id: self._active_executions.get(dep_id, {}).get("state", "unknown")
                    for dep_id in context.depends_on
                }
            }
    
    def cancel_tool_execution(self, execution_id: str, reason: str = "Cancelled") -> bool:
        """
        Cancel a tool execution.
        
        Args:
            execution_id: Execution identifier
            reason: Cancellation reason
            
        Returns:
            bool: True if cancellation successful
        """
        with self._lock:
            if execution_id not in self._active_executions:
                return False
            
            context = self._active_executions[execution_id]
            
            # Update state
            context.state = ToolState.FAILED
            context.error_message = f"Cancelled: {reason}"
            context.completed_at = time.time()
            
            # Complete the execution
            return self.complete_tool_execution(execution_id, success=False, error_message=reason)
    
    def get_session_summary(self, session_id: str) -> Dict[str, Any]:
        """
        Get summary of tool activity for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Dict[str, Any]: Session summary
        """
        with self._lock:
            if session_id not in self._session_tools and session_id not in self._session_history:
                return {"error": "Session not found"}
            
            # Get all executions
            all_executions = self.get_session_executions(session_id, include_history=True)
            
            if not all_executions:
                return {
                    "session_id": session_id,
                    "total_executions": 0,
                    "active_executions": 0,
                    "completed_executions": 0,
                    "failed_executions": 0
                }
            
            # Calculate statistics
            active_count = sum(1 for e in all_executions if e.is_active())
            completed_count = sum(1 for e in all_executions if e.state == ToolState.COMPLETED)
            failed_count = sum(1 for e in all_executions if e.state == ToolState.FAILED)
            
            # Calculate average execution time for completed tools
            completed_executions = [e for e in all_executions if e.is_completed()]
            avg_execution_time = 0.0
            if completed_executions:
                total_time = sum(e.get_duration() for e in completed_executions)
                avg_execution_time = total_time / len(completed_executions)
            
            # Get most used tools
            tool_usage = defaultdict(int)
            for execution in all_executions:
                tool_usage[execution.tool_name] += 1
            
            most_used_tools = sorted(tool_usage.items(), key=lambda x: x[1], reverse=True)[:5]
            
            return {
                "session_id": session_id,
                "total_executions": len(all_executions),
                "active_executions": active_count,
                "completed_executions": completed_count,
                "failed_executions": failed_count,
                "success_rate": completed_count / max(completed_count + failed_count, 1),
                "average_execution_time": avg_execution_time,
                "most_used_tools": most_used_tools,
                "active_tools": self.get_active_tools(session_id)
            }
    
    def clear_session(self, session_id: str) -> None:
        """
        Clear all tool state for a session.
        
        Args:
            session_id: Session identifier
        """
        with self._lock:
            # Cancel active executions
            if session_id in self._session_tools:
                for execution_id in list(self._session_tools[session_id].keys()):
                    self.cancel_tool_execution(execution_id, "Session cleared")
            
            # Clear session data
            if session_id in self._session_tools:
                del self._session_tools[session_id]
            if session_id in self._session_history:
                del self._session_history[session_id]
            
            logger.debug(f"Cleared tool state for session {session_id}")
    
    def _can_execute(self, execution_id: str) -> bool:
        """Check if a tool execution can proceed based on dependencies."""
        context = self._active_executions.get(execution_id)
        if not context:
            return False
        
        # Check if all dependencies are completed
        for dep_id in context.depends_on:
            dep_context = self._active_executions.get(dep_id)
            if not dep_context or not dep_context.is_completed():
                return False
        
        return True
    
    def _handle_state_transition(self, context: ToolExecutionContext, 
                                old_state: ToolState, new_state: ToolState) -> None:
        """Handle state transition side effects."""
        # Remove from queue if moving out of active states
        if old_state in [ToolState.ACTIVE, ToolState.WAITING] and new_state not in [ToolState.ACTIVE, ToolState.WAITING]:
            if context.execution_id in self._execution_queue:
                self._execution_queue.remove(context.execution_id)
        
        # Add to queue if becoming active
        if new_state == ToolState.ACTIVE and context.execution_id not in self._execution_queue:
            self._execution_queue.append(context.execution_id)
    
    def _cleanup_dependencies(self, execution_id: str) -> None:
        """Clean up dependency graph for completed execution."""
        # Remove from dependency graph
        if execution_id in self._dependency_graph:
            del self._dependency_graph[execution_id]
        
        # Remove from blocking relationships
        for blocked_id in self._blocking_graph.get(execution_id, set()):
            if execution_id in self._dependency_graph.get(blocked_id, set()):
                self._dependency_graph[blocked_id].discard(execution_id)
        
        if execution_id in self._blocking_graph:
            del self._blocking_graph[execution_id]
    
    def _check_dependent_tools(self, completed_execution_id: str) -> None:
        """Check if any dependent tools can now execute."""
        for blocked_id in self._blocking_graph.get(completed_execution_id, set()):
            if self._can_execute(blocked_id):
                context = self._active_executions.get(blocked_id)
                if context and context.state == ToolState.WAITING:
                    context.state = ToolState.ACTIVE
                    if blocked_id not in self._execution_queue:
                        self._execution_queue.append(blocked_id)
    
    def export_state_data(self) -> Dict[str, Any]:
        """Export tool state data for persistence."""
        with self._lock:
            return {
                "session_tools": {
                    session_id: {
                        exec_id: {
                            **context.__dict__,
                            "state": context.state.value,
                            "priority": context.priority.value
                        }
                        for exec_id, context in tools.items()
                    }
                    for session_id, tools in self._session_tools.items()
                },
                "session_history": {
                    session_id: [
                        {
                            **context.__dict__,
                            "state": context.state.value,
                            "priority": context.priority.value
                        }
                        for context in history
                    ]
                    for session_id, history in self._session_history.items()
                }
            }
    
    def load_state_data(self, data: Dict[str, Any]) -> None:
        """Load tool state data from persistence."""
        with self._lock:
            # Clear current state
            self._session_tools.clear()
            self._session_history.clear()
            self._active_executions.clear()
            
            # Load session tools
            for session_id, tools_data in data.get("session_tools", {}).items():
                self._session_tools[session_id] = {}
                for exec_id, context_data in tools_data.items():
                    # Reconstruct context
                    context_data["state"] = ToolState(context_data["state"])
                    context_data["priority"] = ToolPriority(context_data["priority"])
                    context = ToolExecutionContext(**context_data)
                    
                    self._session_tools[session_id][exec_id] = context
                    if context.is_active():
                        self._active_executions[exec_id] = context
            
            # Load session history
            for session_id, history_data in data.get("session_history", {}).items():
                self._session_history[session_id] = []
                for context_data in history_data:
                    context_data["state"] = ToolState(context_data["state"])
                    context_data["priority"] = ToolPriority(context_data["priority"])
                    context = ToolExecutionContext(**context_data)
                    self._session_history[session_id].append(context)
            
            logger.info(f"Loaded tool state for {len(self._session_tools)} sessions")
