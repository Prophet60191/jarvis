"""
Tool Chain Detector

Detects and creates optimal tool chains for complex multi-step tasks
by analyzing tool capabilities, relationships, and usage patterns.
"""

import time
import logging
import statistics
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, Counter
import threading
import itertools

logger = logging.getLogger(__name__)

class ChainType(Enum):
    """Types of tool chains."""
    SEQUENTIAL = "sequential"        # Tools executed in sequence
    PARALLEL = "parallel"           # Tools executed in parallel
    CONDITIONAL = "conditional"     # Tools executed based on conditions
    ITERATIVE = "iterative"         # Tools executed in loops
    HIERARCHICAL = "hierarchical"   # Nested tool chains

class ChainConfidence(Enum):
    """Confidence levels for tool chains."""
    LOW = "low"           # < 0.4
    MEDIUM = "medium"     # 0.4 - 0.7
    HIGH = "high"         # 0.7 - 0.9
    VERY_HIGH = "very_high"  # > 0.9

@dataclass
class ChainPattern:
    """Represents a detected tool chain pattern."""
    pattern_id: str
    tools: List[str]
    chain_type: ChainType
    confidence: float = 0.0
    
    # Pattern metadata
    usage_count: int = 0
    success_rate: float = 0.0
    average_execution_time: float = 0.0
    
    # Context information
    common_contexts: List[Dict[str, Any]] = field(default_factory=list)
    trigger_conditions: List[str] = field(default_factory=list)
    
    # Relationships
    prerequisites: List[str] = field(default_factory=list)
    alternatives: List[str] = field(default_factory=list)
    
    # Temporal information
    first_observed: float = field(default_factory=time.time)
    last_used: float = field(default_factory=time.time)
    
    def get_confidence_level(self) -> ChainConfidence:
        """Get confidence level category."""
        if self.confidence < 0.4:
            return ChainConfidence.LOW
        elif self.confidence < 0.7:
            return ChainConfidence.MEDIUM
        elif self.confidence < 0.9:
            return ChainConfidence.HIGH
        else:
            return ChainConfidence.VERY_HIGH
    
    def update_usage(self, success: bool, execution_time: float) -> None:
        """Update usage statistics."""
        self.usage_count += 1
        self.last_used = time.time()
        
        # Update success rate
        if self.usage_count == 1:
            self.success_rate = 1.0 if success else 0.0
        else:
            total_successes = self.success_rate * (self.usage_count - 1) + (1.0 if success else 0.0)
            self.success_rate = total_successes / self.usage_count
        
        # Update average execution time
        if self.usage_count == 1:
            self.average_execution_time = execution_time
        else:
            total_time = self.average_execution_time * (self.usage_count - 1) + execution_time
            self.average_execution_time = total_time / self.usage_count
        
        # Update confidence based on usage and success
        usage_factor = min(self.usage_count / 10.0, 1.0)  # Max confidence from usage at 10 uses
        success_factor = self.success_rate
        self.confidence = usage_factor * success_factor

@dataclass
class ToolChain:
    """Represents a complete tool chain for execution."""
    chain_id: str
    tools: List[str]
    chain_type: ChainType = ChainType.SEQUENTIAL
    confidence: float = 0.0
    
    # Execution metadata
    estimated_duration: float = 0.0
    resource_requirements: Dict[str, Any] = field(default_factory=dict)
    
    # Dependencies and conditions
    tool_dependencies: Dict[str, List[str]] = field(default_factory=dict)
    execution_conditions: List[str] = field(default_factory=list)
    
    # Context and parameters
    context_requirements: Dict[str, Any] = field(default_factory=dict)
    tool_parameters: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    # Metadata
    created_at: float = field(default_factory=time.time)
    based_on_pattern: Optional[str] = None
    
    def get_tool_count(self) -> int:
        """Get number of tools in chain."""
        return len(self.tools)
    
    def has_tool(self, tool_name: str) -> bool:
        """Check if chain contains a specific tool."""
        return tool_name in self.tools
    
    def get_tool_position(self, tool_name: str) -> Optional[int]:
        """Get position of tool in chain."""
        try:
            return self.tools.index(tool_name)
        except ValueError:
            return None

class ToolChainDetector:
    """
    Detects optimal tool chains for complex tasks.
    
    This component analyzes tool usage patterns, capabilities, and
    relationships to automatically detect and suggest optimal tool
    chains for various tasks and contexts.
    """
    
    def __init__(self, plugin_manager: Any = None):
        """
        Initialize the tool chain detector.
        
        Args:
            plugin_manager: Plugin manager for tool access
        """
        self.plugin_manager = plugin_manager
        
        # Pattern storage
        self._chain_patterns: Dict[str, ChainPattern] = {}
        self._usage_history: List[Dict[str, Any]] = []
        
        # Tool analysis
        self._tool_capabilities: Dict[str, Set[str]] = defaultdict(set)
        self._tool_relationships: Dict[str, Dict[str, float]] = defaultdict(dict)
        self._tool_performance: Dict[str, Dict[str, float]] = defaultdict(dict)
        
        # Chain detection state
        self._sequence_buffer: List[Tuple[str, float, bool]] = []  # (tool, timestamp, success)
        self._detection_window = 300  # 5 minutes
        
        # Configuration
        self.min_pattern_occurrences = 3
        self.max_chain_length = 10
        self.confidence_threshold = 0.5
        self.pattern_decay_rate = 0.95  # Daily decay
        
        # Thread safety
        self._lock = threading.RLock()
        
        logger.info("ToolChainDetector initialized")
    
    def record_tool_usage(self, tool_name: str, success: bool = True,
                         execution_time: float = 0.0, context: Dict[str, Any] = None) -> None:
        """
        Record tool usage for pattern detection.
        
        Args:
            tool_name: Name of the tool used
            success: Whether execution was successful
            execution_time: Execution time in seconds
            context: Optional context information
        """
        timestamp = time.time()
        
        with self._lock:
            # Add to sequence buffer
            self._sequence_buffer.append((tool_name, timestamp, success))
            
            # Maintain buffer size (keep last 100 tool uses)
            if len(self._sequence_buffer) > 100:
                self._sequence_buffer = self._sequence_buffer[-100:]
            
            # Add to usage history
            usage_record = {
                "tool_name": tool_name,
                "timestamp": timestamp,
                "success": success,
                "execution_time": execution_time,
                "context": context or {}
            }
            self._usage_history.append(usage_record)
            
            # Maintain history size
            if len(self._usage_history) > 1000:
                self._usage_history = self._usage_history[-1000:]
            
            # Detect patterns in real-time
            self._detect_patterns_from_buffer()
            
            logger.debug(f"Recorded tool usage: {tool_name}")
    
    def detect_optimal_chain(self, candidate_tools: List[str],
                           intent_analysis: Dict[str, Any],
                           context: Any) -> ToolChain:
        """
        Detect optimal tool chain for given tools and intent.
        
        Args:
            candidate_tools: List of candidate tools
            intent_analysis: Analysis of user intent
            context: Current context
            
        Returns:
            ToolChain: Optimal tool chain
        """
        with self._lock:
            # Find matching patterns
            matching_patterns = self._find_matching_patterns(candidate_tools, intent_analysis)
            
            if matching_patterns:
                # Use best matching pattern
                best_pattern = max(matching_patterns, key=lambda p: p.confidence)
                return self._create_chain_from_pattern(best_pattern, context)
            
            # No patterns found, create new chain
            return self._create_new_chain(candidate_tools, intent_analysis, context)
    
    def suggest_tool_chains(self, candidate_tools: List[str],
                          intent_analysis: Dict[str, Any],
                          context: Any, max_suggestions: int = 5) -> List[ToolChain]:
        """
        Suggest multiple possible tool chains.
        
        Args:
            candidate_tools: List of candidate tools
            intent_analysis: Analysis of user intent
            context: Current context
            max_suggestions: Maximum number of suggestions
            
        Returns:
            List[ToolChain]: List of suggested tool chains
        """
        suggestions = []
        
        with self._lock:
            # Find all matching patterns
            matching_patterns = self._find_matching_patterns(candidate_tools, intent_analysis)
            
            # Create chains from patterns
            for pattern in matching_patterns[:max_suggestions]:
                chain = self._create_chain_from_pattern(pattern, context)
                suggestions.append(chain)
            
            # If we need more suggestions, create variations
            while len(suggestions) < max_suggestions and len(candidate_tools) > 1:
                # Create different arrangements
                if len(suggestions) == 0:
                    # Sequential chain
                    chain = self._create_sequential_chain(candidate_tools, intent_analysis, context)
                    suggestions.append(chain)
                elif len(suggestions) == 1:
                    # Parallel chain (if applicable)
                    chain = self._create_parallel_chain(candidate_tools, intent_analysis, context)
                    if chain:
                        suggestions.append(chain)
                else:
                    break
            
            # Sort by confidence
            suggestions.sort(key=lambda c: c.confidence, reverse=True)
            
            return suggestions[:max_suggestions]
    
    def learn_from_execution(self, chain: ToolChain, execution_result: Dict[str, Any]) -> None:
        """
        Learn from tool chain execution results.
        
        Args:
            chain: Executed tool chain
            execution_result: Execution results
        """
        with self._lock:
            success = execution_result.get("success", False)
            execution_time = execution_result.get("execution_time", 0.0)
            
            # Update pattern if chain was based on one
            if chain.based_on_pattern and chain.based_on_pattern in self._chain_patterns:
                pattern = self._chain_patterns[chain.based_on_pattern]
                pattern.update_usage(success, execution_time)
            
            # Record the sequence for future pattern detection
            for tool in chain.tools:
                self.record_tool_usage(tool, success, execution_time / len(chain.tools))
            
            logger.debug(f"Learned from chain execution: {chain.chain_id}")
    
    def get_chain_patterns(self, min_confidence: float = 0.0) -> List[ChainPattern]:
        """
        Get detected chain patterns.
        
        Args:
            min_confidence: Minimum confidence threshold
            
        Returns:
            List[ChainPattern]: List of chain patterns
        """
        with self._lock:
            patterns = [
                pattern for pattern in self._chain_patterns.values()
                if pattern.confidence >= min_confidence
            ]
            
            # Sort by confidence and usage
            patterns.sort(key=lambda p: (p.confidence, p.usage_count), reverse=True)
            
            return patterns
    
    def analyze_tool_relationships(self) -> Dict[str, Dict[str, float]]:
        """
        Analyze relationships between tools.
        
        Returns:
            Dict[str, Dict[str, float]]: Tool relationship matrix
        """
        with self._lock:
            # Analyze co-occurrence patterns
            tool_pairs = defaultdict(int)
            total_sequences = 0
            
            # Look for tools used within time window
            for i, (tool1, timestamp1, _) in enumerate(self._sequence_buffer):
                for j, (tool2, timestamp2, _) in enumerate(self._sequence_buffer[i+1:], i+1):
                    if timestamp2 - timestamp1 > self._detection_window:
                        break
                    
                    if tool1 != tool2:
                        pair_key = tuple(sorted([tool1, tool2]))
                        tool_pairs[pair_key] += 1
                        total_sequences += 1
            
            # Calculate relationship strengths
            relationships = defaultdict(dict)
            for (tool1, tool2), count in tool_pairs.items():
                strength = count / max(total_sequences, 1)
                relationships[tool1][tool2] = strength
                relationships[tool2][tool1] = strength
            
            return dict(relationships)
    
    def get_detector_statistics(self) -> Dict[str, Any]:
        """
        Get detector statistics.
        
        Returns:
            Dict[str, Any]: Detector statistics
        """
        with self._lock:
            total_patterns = len(self._chain_patterns)
            high_confidence_patterns = sum(
                1 for p in self._chain_patterns.values() if p.confidence > 0.7
            )
            
            # Calculate average pattern metrics
            if self._chain_patterns:
                avg_confidence = statistics.mean(p.confidence for p in self._chain_patterns.values())
                avg_usage = statistics.mean(p.usage_count for p in self._chain_patterns.values())
                avg_success_rate = statistics.mean(p.success_rate for p in self._chain_patterns.values())
            else:
                avg_confidence = avg_usage = avg_success_rate = 0.0
            
            return {
                "total_patterns": total_patterns,
                "high_confidence_patterns": high_confidence_patterns,
                "usage_history_size": len(self._usage_history),
                "sequence_buffer_size": len(self._sequence_buffer),
                "average_pattern_confidence": avg_confidence,
                "average_pattern_usage": avg_usage,
                "average_pattern_success_rate": avg_success_rate,
                "detection_window_seconds": self._detection_window
            }
    
    def _detect_patterns_from_buffer(self) -> None:
        """Detect patterns from the current sequence buffer."""
        if len(self._sequence_buffer) < 2:
            return
        
        # Look for sequential patterns
        current_time = time.time()
        
        # Find sequences within detection window
        sequences = []
        for i in range(len(self._sequence_buffer)):
            sequence = [self._sequence_buffer[i]]
            
            for j in range(i + 1, len(self._sequence_buffer)):
                tool, timestamp, success = self._sequence_buffer[j]
                
                # Check if within time window
                if timestamp - sequence[0][1] > self._detection_window:
                    break
                
                sequence.append((tool, timestamp, success))
                
                # Check if this is a valid pattern (2+ tools)
                if len(sequence) >= 2:
                    self._analyze_sequence_pattern(sequence)
    
    def _analyze_sequence_pattern(self, sequence: List[Tuple[str, float, bool]]) -> None:
        """Analyze a sequence for pattern creation."""
        tools = [item[0] for item in sequence]
        
        # Skip if too long or has duplicates
        if len(tools) > self.max_chain_length or len(set(tools)) != len(tools):
            return
        
        # Create pattern ID
        pattern_id = "->".join(tools)
        
        # Check if pattern exists
        if pattern_id in self._chain_patterns:
            pattern = self._chain_patterns[pattern_id]
            
            # Update existing pattern
            success = all(item[2] for item in sequence)
            execution_time = sequence[-1][1] - sequence[0][1]
            pattern.update_usage(success, execution_time)
        else:
            # Create new pattern if we've seen it enough times
            pattern_count = self._count_pattern_occurrences(tools)
            
            if pattern_count >= self.min_pattern_occurrences:
                pattern = ChainPattern(
                    pattern_id=pattern_id,
                    tools=tools,
                    chain_type=ChainType.SEQUENTIAL,
                    usage_count=pattern_count
                )
                
                # Calculate initial confidence
                success = all(item[2] for item in sequence)
                execution_time = sequence[-1][1] - sequence[0][1]
                pattern.update_usage(success, execution_time)
                
                self._chain_patterns[pattern_id] = pattern
                
                logger.debug(f"Detected new pattern: {pattern_id}")
    
    def _count_pattern_occurrences(self, tools: List[str]) -> int:
        """Count how many times a pattern has occurred."""
        count = 0
        
        for i in range(len(self._usage_history) - len(tools) + 1):
            # Check if tools match in sequence
            matches = True
            for j, tool in enumerate(tools):
                if self._usage_history[i + j]["tool_name"] != tool:
                    matches = False
                    break
            
            if matches:
                # Check if within reasonable time window
                start_time = self._usage_history[i]["timestamp"]
                end_time = self._usage_history[i + len(tools) - 1]["timestamp"]
                
                if end_time - start_time <= self._detection_window:
                    count += 1
        
        return count
    
    def _find_matching_patterns(self, candidate_tools: List[str],
                              intent_analysis: Dict[str, Any]) -> List[ChainPattern]:
        """Find patterns that match candidate tools and intent."""
        matching_patterns = []
        
        for pattern in self._chain_patterns.values():
            # Check if pattern tools are subset of candidates
            if set(pattern.tools).issubset(set(candidate_tools)):
                # Check confidence threshold
                if pattern.confidence >= self.confidence_threshold:
                    matching_patterns.append(pattern)
        
        return matching_patterns
    
    def _create_chain_from_pattern(self, pattern: ChainPattern, context: Any) -> ToolChain:
        """Create a tool chain from a detected pattern."""
        chain_id = f"pattern_{pattern.pattern_id}_{int(time.time())}"
        
        return ToolChain(
            chain_id=chain_id,
            tools=pattern.tools.copy(),
            chain_type=pattern.chain_type,
            confidence=pattern.confidence,
            estimated_duration=pattern.average_execution_time,
            based_on_pattern=pattern.pattern_id
        )
    
    def _create_new_chain(self, candidate_tools: List[str],
                         intent_analysis: Dict[str, Any], context: Any) -> ToolChain:
        """Create a new tool chain when no patterns match."""
        # Default to sequential chain
        return self._create_sequential_chain(candidate_tools, intent_analysis, context)
    
    def _create_sequential_chain(self, tools: List[str],
                               intent_analysis: Dict[str, Any], context: Any) -> ToolChain:
        """Create a sequential tool chain."""
        chain_id = f"sequential_{int(time.time())}"
        
        # Simple ordering based on tool names (could be enhanced)
        ordered_tools = sorted(tools)
        
        return ToolChain(
            chain_id=chain_id,
            tools=ordered_tools,
            chain_type=ChainType.SEQUENTIAL,
            confidence=0.5,  # Default confidence for new chains
            estimated_duration=len(ordered_tools) * 2.0  # 2 seconds per tool estimate
        )
    
    def _create_parallel_chain(self, tools: List[str],
                             intent_analysis: Dict[str, Any], context: Any) -> Optional[ToolChain]:
        """Create a parallel tool chain if applicable."""
        # Only create parallel chains for independent tools
        if len(tools) < 2:
            return None
        
        chain_id = f"parallel_{int(time.time())}"
        
        return ToolChain(
            chain_id=chain_id,
            tools=tools.copy(),
            chain_type=ChainType.PARALLEL,
            confidence=0.4,  # Lower confidence for parallel chains
            estimated_duration=max(2.0, len(tools) * 0.5)  # Parallel execution estimate
        )
