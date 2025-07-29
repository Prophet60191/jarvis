"""
Conflict Resolver for Tool Orchestration

Handles conflicts between tools, resolves dependency issues,
and ensures safe tool execution in orchestrated workflows.
"""

import time
import logging
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
import threading

logger = logging.getLogger(__name__)

class ConflictType(Enum):
    """Types of tool conflicts."""
    RESOURCE_CONFLICT = "resource_conflict"
    DEPENDENCY_CONFLICT = "dependency_conflict"
    EXECUTION_CONFLICT = "execution_conflict"
    DATA_CONFLICT = "data_conflict"
    PERMISSION_CONFLICT = "permission_conflict"

class ResolutionStrategy(Enum):
    """Conflict resolution strategies."""
    SEQUENTIAL = "sequential"
    PRIORITY_BASED = "priority_based"
    RESOURCE_SHARING = "resource_sharing"
    ALTERNATIVE_TOOL = "alternative_tool"
    USER_INTERVENTION = "user_intervention"

@dataclass
class Conflict:
    """Represents a tool conflict."""
    conflict_id: str
    conflict_type: ConflictType
    tools_involved: List[str]
    description: str
    severity: float = 0.5  # 0.0 to 1.0
    
    # Resolution information
    resolution_strategy: Optional[ResolutionStrategy] = None
    resolution_applied: bool = False
    resolution_successful: bool = False
    
    # Metadata
    detected_at: float = field(default_factory=time.time)
    resolved_at: Optional[float] = None

class ConflictResolver:
    """
    Resolves conflicts between tools in orchestrated workflows.
    
    This component detects potential conflicts between tools and
    applies appropriate resolution strategies to ensure safe execution.
    """
    
    def __init__(self):
        """Initialize the conflict resolver."""
        # Conflict tracking
        self._active_conflicts: Dict[str, Conflict] = {}
        self._resolved_conflicts: List[Conflict] = []
        
        # Resource tracking
        self._resource_usage: Dict[str, Set[str]] = {}  # resource -> tools using it
        self._tool_dependencies: Dict[str, Set[str]] = {}  # tool -> dependencies
        
        # Configuration
        self.max_concurrent_tools = 10
        self.conflict_detection_enabled = True
        self.auto_resolution_enabled = True
        
        # Thread safety
        self._lock = threading.RLock()
        
        logger.info("ConflictResolver initialized")
    
    def detect_conflicts(self, tools: List[str], context: Dict[str, Any] = None) -> List[Conflict]:
        """
        Detect potential conflicts between tools.
        
        Args:
            tools: List of tools to check for conflicts
            context: Optional context information
            
        Returns:
            List[Conflict]: Detected conflicts
        """
        with self._lock:
            conflicts = []
            
            if not self.conflict_detection_enabled:
                return conflicts
            
            # Check for resource conflicts
            resource_conflicts = self._detect_resource_conflicts(tools)
            conflicts.extend(resource_conflicts)
            
            # Check for dependency conflicts
            dependency_conflicts = self._detect_dependency_conflicts(tools)
            conflicts.extend(dependency_conflicts)
            
            # Check for execution conflicts
            execution_conflicts = self._detect_execution_conflicts(tools, context)
            conflicts.extend(execution_conflicts)
            
            # Store active conflicts
            for conflict in conflicts:
                self._active_conflicts[conflict.conflict_id] = conflict
            
            logger.debug(f"Detected {len(conflicts)} conflicts for tools: {tools}")
            return conflicts
    
    def resolve_conflicts(self, conflicts: List[Conflict]) -> Dict[str, bool]:
        """
        Resolve detected conflicts.
        
        Args:
            conflicts: List of conflicts to resolve
            
        Returns:
            Dict[str, bool]: Resolution results (conflict_id -> success)
        """
        results = {}
        
        with self._lock:
            for conflict in conflicts:
                if not self.auto_resolution_enabled:
                    results[conflict.conflict_id] = False
                    continue
                
                success = self._resolve_conflict(conflict)
                results[conflict.conflict_id] = success
                
                # Update conflict status
                conflict.resolution_applied = True
                conflict.resolution_successful = success
                conflict.resolved_at = time.time()
                
                # Move to resolved conflicts
                if conflict.conflict_id in self._active_conflicts:
                    del self._active_conflicts[conflict.conflict_id]
                    self._resolved_conflicts.append(conflict)
        
        return results
    
    def register_tool_resources(self, tool_name: str, resources: List[str]) -> None:
        """
        Register resources used by a tool.
        
        Args:
            tool_name: Name of the tool
            resources: List of resources the tool uses
        """
        with self._lock:
            for resource in resources:
                if resource not in self._resource_usage:
                    self._resource_usage[resource] = set()
                self._resource_usage[resource].add(tool_name)
    
    def register_tool_dependencies(self, tool_name: str, dependencies: List[str]) -> None:
        """
        Register dependencies for a tool.
        
        Args:
            tool_name: Name of the tool
            dependencies: List of tool dependencies
        """
        with self._lock:
            self._tool_dependencies[tool_name] = set(dependencies)
    
    def get_active_conflicts(self) -> List[Conflict]:
        """Get currently active conflicts."""
        with self._lock:
            return list(self._active_conflicts.values())
    
    def get_conflict_statistics(self) -> Dict[str, Any]:
        """Get conflict resolution statistics."""
        with self._lock:
            total_conflicts = len(self._resolved_conflicts) + len(self._active_conflicts)
            resolved_conflicts = len(self._resolved_conflicts)
            successful_resolutions = sum(1 for c in self._resolved_conflicts if c.resolution_successful)
            
            # Conflict type distribution
            type_counts = {}
            all_conflicts = list(self._resolved_conflicts) + list(self._active_conflicts.values())
            for conflict in all_conflicts:
                conflict_type = conflict.conflict_type.value
                type_counts[conflict_type] = type_counts.get(conflict_type, 0) + 1
            
            return {
                "total_conflicts": total_conflicts,
                "active_conflicts": len(self._active_conflicts),
                "resolved_conflicts": resolved_conflicts,
                "successful_resolutions": successful_resolutions,
                "resolution_success_rate": (successful_resolutions / max(resolved_conflicts, 1)) * 100,
                "conflict_type_distribution": type_counts,
                "auto_resolution_enabled": self.auto_resolution_enabled
            }
    
    def _detect_resource_conflicts(self, tools: List[str]) -> List[Conflict]:
        """Detect resource conflicts between tools."""
        conflicts = []
        
        # Check for shared resources
        for resource, using_tools in self._resource_usage.items():
            conflicting_tools = [tool for tool in tools if tool in using_tools]
            
            if len(conflicting_tools) > 1:
                conflict = Conflict(
                    conflict_id=f"resource_{resource}_{int(time.time())}",
                    conflict_type=ConflictType.RESOURCE_CONFLICT,
                    tools_involved=conflicting_tools,
                    description=f"Multiple tools trying to use resource: {resource}",
                    severity=0.7
                )
                conflicts.append(conflict)
        
        return conflicts
    
    def _detect_dependency_conflicts(self, tools: List[str]) -> List[Conflict]:
        """Detect dependency conflicts between tools."""
        conflicts = []
        
        # Check for circular dependencies
        for tool in tools:
            if tool in self._tool_dependencies:
                dependencies = self._tool_dependencies[tool]
                
                # Check if any dependency is also in the tools list
                # and has this tool as a dependency (circular)
                for dep in dependencies:
                    if dep in tools and dep in self._tool_dependencies:
                        if tool in self._tool_dependencies[dep]:
                            conflict = Conflict(
                                conflict_id=f"circular_{tool}_{dep}_{int(time.time())}",
                                conflict_type=ConflictType.DEPENDENCY_CONFLICT,
                                tools_involved=[tool, dep],
                                description=f"Circular dependency between {tool} and {dep}",
                                severity=0.9
                            )
                            conflicts.append(conflict)
        
        return conflicts
    
    def _detect_execution_conflicts(self, tools: List[str], context: Dict[str, Any] = None) -> List[Conflict]:
        """Detect execution conflicts between tools."""
        conflicts = []
        
        # Check for too many concurrent tools
        if len(tools) > self.max_concurrent_tools:
            conflict = Conflict(
                conflict_id=f"concurrent_{int(time.time())}",
                conflict_type=ConflictType.EXECUTION_CONFLICT,
                tools_involved=tools,
                description=f"Too many concurrent tools: {len(tools)} > {self.max_concurrent_tools}",
                severity=0.6
            )
            conflicts.append(conflict)
        
        return conflicts
    
    def _resolve_conflict(self, conflict: Conflict) -> bool:
        """Resolve a specific conflict."""
        try:
            if conflict.conflict_type == ConflictType.RESOURCE_CONFLICT:
                return self._resolve_resource_conflict(conflict)
            elif conflict.conflict_type == ConflictType.DEPENDENCY_CONFLICT:
                return self._resolve_dependency_conflict(conflict)
            elif conflict.conflict_type == ConflictType.EXECUTION_CONFLICT:
                return self._resolve_execution_conflict(conflict)
            else:
                # Default resolution strategy
                conflict.resolution_strategy = ResolutionStrategy.SEQUENTIAL
                return True
                
        except Exception as e:
            logger.error(f"Failed to resolve conflict {conflict.conflict_id}: {e}")
            return False
    
    def _resolve_resource_conflict(self, conflict: Conflict) -> bool:
        """Resolve a resource conflict."""
        # Strategy: Sequential execution
        conflict.resolution_strategy = ResolutionStrategy.SEQUENTIAL
        logger.debug(f"Resolved resource conflict {conflict.conflict_id} with sequential execution")
        return True
    
    def _resolve_dependency_conflict(self, conflict: Conflict) -> bool:
        """Resolve a dependency conflict."""
        # Strategy: Remove circular dependency by prioritizing one tool
        conflict.resolution_strategy = ResolutionStrategy.PRIORITY_BASED
        logger.debug(f"Resolved dependency conflict {conflict.conflict_id} with priority-based execution")
        return True
    
    def _resolve_execution_conflict(self, conflict: Conflict) -> bool:
        """Resolve an execution conflict."""
        # Strategy: Limit concurrent execution
        conflict.resolution_strategy = ResolutionStrategy.SEQUENTIAL
        logger.debug(f"Resolved execution conflict {conflict.conflict_id} with sequential execution")
        return True
