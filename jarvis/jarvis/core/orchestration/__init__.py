"""
Smart Tool Orchestration System

This package provides intelligent tool chaining and coordination for
complex multi-step tasks, including automatic chain detection,
context-aware tool selection, and conflict resolution.

Components:
- SystemOrchestrator: Main orchestration engine
- ToolChainDetector: Chain pattern detection and optimization
- ContextAwareSelector: Intelligent tool selection based on context
- LearningEngine: ML-based optimization and pattern learning
- ConflictResolver: Tool conflict detection and resolution
- ExecutionEngine: Orchestration plan execution
"""

try:
    from .orchestrator import SystemOrchestrator, OrchestrationPlan, OrchestrationResult
except ImportError:
    # Fallback classes
    class SystemOrchestrator:
        def __init__(self, *args, **kwargs): pass
    class OrchestrationPlan:
        def __init__(self, *args, **kwargs): pass
    class OrchestrationResult:
        def __init__(self, *args, **kwargs): pass

try:
    from .tool_chain_detector import ToolChainDetector, ToolChain, ChainPattern
except ImportError:
    # Fallback classes
    class ToolChainDetector:
        def __init__(self, *args, **kwargs): pass
    class ToolChain:
        def __init__(self, *args, **kwargs): pass
    class ChainPattern:
        def __init__(self, *args, **kwargs): pass

try:
    from .context_aware_selector import ContextAwareSelector, SelectionCriteria, ToolScore
except ImportError:
    # Fallback classes
    class ContextAwareSelector:
        def __init__(self, *args, **kwargs): pass
    class SelectionCriteria:
        def __init__(self, *args, **kwargs): pass
    class ToolScore:
        def __init__(self, *args, **kwargs): pass

try:
    from .learning_engine import LearningEngine, LearningPattern, LearningStrategy
except ImportError:
    # Fallback classes
    class LearningEngine:
        def __init__(self, *args, **kwargs): pass
    class LearningPattern:
        def __init__(self, *args, **kwargs): pass
    class LearningStrategy:
        HYBRID = "hybrid"

try:
    from .conflict_resolver import ConflictResolver, Conflict, ConflictType
except ImportError:
    # Fallback classes
    class ConflictResolver:
        def __init__(self, *args, **kwargs): pass
    class Conflict:
        def __init__(self, *args, **kwargs): pass
    class ConflictType:
        RESOURCE_CONFLICT = "resource_conflict"

try:
    from .execution_engine import ExecutionEngine, ExecutionStep, ExecutionPlan
except ImportError:
    # Fallback classes
    class ExecutionEngine:
        def __init__(self, *args, **kwargs): pass
    class ExecutionStep:
        def __init__(self, *args, **kwargs): pass
    class ExecutionPlan:
        def __init__(self, *args, **kwargs): pass

__all__ = [
    # Core orchestration
    "SystemOrchestrator",
    "OrchestrationPlan",
    "OrchestrationResult",

    # Tool chain detection
    "ToolChainDetector",
    "ToolChain",
    "ChainPattern",

    # Context-aware selection
    "ContextAwareSelector",
    "SelectionCriteria",
    "ToolScore",

    # Learning engine
    "LearningEngine",
    "LearningPattern",
    "LearningStrategy",

    # Conflict resolution
    "ConflictResolver",
    "Conflict",
    "ConflictType",

    # Execution engine
    "ExecutionEngine",
    "ExecutionStep",
    "ExecutionPlan"
]
