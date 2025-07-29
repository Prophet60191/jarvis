"""
System Orchestrator

Main orchestration engine that coordinates tool selection, chaining,
and execution for complex multi-step tasks.
"""

import time
import logging
import asyncio
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
import threading

from ..context.context_manager import Context, ContextManager
from .tool_chain_detector import ToolChainDetector, ToolChain
from .context_aware_selector import ContextAwareSelector, SelectionCriteria
try:
    from .learning_engine import LearningEngine, LearningStrategy, LearningPattern
except ImportError:
    # Fallback if learning engine not available
    class LearningEngine:
        def __init__(self, *args, **kwargs):
            pass
        def learn_from_experience(self, *args, **kwargs):
            pass
        def get_recommendations(self, *args, **kwargs):
            return []

    class LearningStrategy:
        HYBRID = "hybrid"

    class LearningPattern:
        def __init__(self, *args, **kwargs):
            pass

    class LearningPattern:
        def __init__(self, *args, **kwargs):
            pass
try:
    from .conflict_resolver import ConflictResolver, Conflict
except ImportError:
    # Fallback if conflict resolver not available
    class ConflictResolver:
        def __init__(self, *args, **kwargs):
            pass
        def detect_conflicts(self, *args, **kwargs):
            return []
        def resolve_conflicts(self, *args, **kwargs):
            return {}

    class Conflict:
        def __init__(self, *args, **kwargs):
            pass
try:
    from .execution_engine import ExecutionEngine, ExecutionStep, ExecutionPlan
except ImportError:
    # Fallback if execution engine not available
    class ExecutionEngine:
        def __init__(self, *args, **kwargs):
            pass
        async def execute_plan(self, *args, **kwargs):
            return {}

    class ExecutionStep:
        def __init__(self, *args, **kwargs):
            pass

    class ExecutionPlan:
        def __init__(self, *args, **kwargs):
            pass

logger = logging.getLogger(__name__)

class OrchestrationStrategy(Enum):
    """Orchestration strategies for different scenarios."""
    SEQUENTIAL = "sequential"        # Execute tools in sequence
    PARALLEL = "parallel"           # Execute compatible tools in parallel
    CONDITIONAL = "conditional"     # Execute based on conditions
    ADAPTIVE = "adaptive"           # Adapt strategy based on context
    OPTIMIZED = "optimized"         # Use learned optimizations

class PlanStatus(Enum):
    """Status of orchestration plan."""
    CREATED = "created"
    VALIDATED = "validated"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class OrchestrationPlan:
    """
    Represents a complete orchestration plan for a user request.
    
    This plan includes the sequence of tools to execute, their parameters,
    dependencies, and execution strategy.
    """
    plan_id: str
    user_request: str
    tool_chain: ToolChain
    execution_steps: List[ExecutionStep] = field(default_factory=list)
    strategy: OrchestrationStrategy = OrchestrationStrategy.SEQUENTIAL
    estimated_duration: float = 0.0
    confidence_score: float = 0.0
    
    # Execution tracking
    status: PlanStatus = PlanStatus.CREATED
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    
    # Context and metadata
    context_snapshot: Dict[str, Any] = field(default_factory=dict)
    required_capabilities: Set[str] = field(default_factory=set)
    resource_requirements: Dict[str, Any] = field(default_factory=dict)
    
    def get_duration(self) -> float:
        """Get actual execution duration."""
        if self.started_at and self.completed_at:
            return self.completed_at - self.started_at
        elif self.started_at:
            return time.time() - self.started_at
        return 0.0
    
    def mark_started(self) -> None:
        """Mark plan as started."""
        self.started_at = time.time()
        self.status = PlanStatus.EXECUTING
    
    def mark_completed(self, success: bool = True) -> None:
        """Mark plan as completed."""
        self.completed_at = time.time()
        self.status = PlanStatus.COMPLETED if success else PlanStatus.FAILED

@dataclass
class OrchestrationResult:
    """
    Result of orchestration plan execution.
    
    Contains the results from each tool execution, overall success status,
    performance metrics, and any errors encountered.
    """
    plan_id: str
    success: bool
    results: List[Any] = field(default_factory=list)
    execution_time: float = 0.0
    tools_executed: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    
    # Performance metrics
    total_steps: int = 0
    successful_steps: int = 0
    failed_steps: int = 0
    average_step_time: float = 0.0
    
    # Resource usage
    peak_memory_mb: float = 0.0
    total_cpu_time: float = 0.0
    
    # Learning data
    optimization_opportunities: List[str] = field(default_factory=list)
    pattern_insights: Dict[str, Any] = field(default_factory=dict)
    
    def get_success_rate(self) -> float:
        """Get success rate of executed steps."""
        if self.total_steps == 0:
            return 0.0
        return self.successful_steps / self.total_steps

class SystemOrchestrator:
    """
    Main orchestration engine for intelligent tool coordination.
    
    This class provides the primary interface for orchestrating complex
    multi-step tasks by intelligently selecting, chaining, and executing
    tools based on user requests and context.
    """
    
    def __init__(self, context_manager: ContextManager,
                 plugin_manager: Any = None,
                 enable_learning: bool = True):
        """
        Initialize the system orchestrator.
        
        Args:
            context_manager: Context manager instance
            plugin_manager: Plugin manager for tool access
            enable_learning: Whether to enable learning optimizations
        """
        self.context_manager = context_manager
        self.plugin_manager = plugin_manager
        self.enable_learning = enable_learning
        
        # Initialize sub-components
        self.tool_chain_detector = ToolChainDetector()
        self.context_aware_selector = ContextAwareSelector()
        self.learning_engine = LearningEngine() if enable_learning else None
        self.conflict_resolver = ConflictResolver()
        self.execution_engine = ExecutionEngine()
        
        # Orchestration state
        self._active_plans: Dict[str, OrchestrationPlan] = {}
        self._plan_history: List[OrchestrationPlan] = []
        self._lock = threading.RLock()
        
        # Configuration
        self.max_chain_length = 10
        self.max_parallel_tools = 3
        self.default_timeout = 300  # 5 minutes
        self.confidence_threshold = 0.6
        
        logger.info("SystemOrchestrator initialized")
    
    def orchestrate_request(self, user_input: str, context: Context,
                          strategy: OrchestrationStrategy = OrchestrationStrategy.ADAPTIVE) -> OrchestrationPlan:
        """
        Create an orchestration plan for a user request.
        
        Args:
            user_input: The user's natural language request
            context: Current conversation and system context
            strategy: Orchestration strategy to use
            
        Returns:
            OrchestrationPlan: Detailed execution plan
        """
        with self._lock:
            plan_id = f"plan_{int(time.time() * 1000)}"
            
            try:
                # Step 1: Analyze user request and extract intent
                intent_analysis = self._analyze_user_intent(user_input, context)
                
                # Step 2: Identify required capabilities
                required_capabilities = self._identify_required_capabilities(intent_analysis)
                
                # Step 3: Select candidate tools
                candidate_tools = self._select_candidate_tools(required_capabilities, context)
                
                # Step 4: Detect optimal tool chain
                tool_chain = self.tool_chain_detector.detect_optimal_chain(
                    candidate_tools, intent_analysis, context
                )
                
                # Step 5: Resolve conflicts
                resolved_chain = self.conflict_resolver.resolve_conflicts(tool_chain, context)
                
                # Step 6: Create execution steps
                execution_steps = self._create_execution_steps(resolved_chain, context)
                
                # Step 7: Estimate duration and confidence
                estimated_duration = self._estimate_execution_duration(execution_steps)
                confidence_score = self._calculate_confidence_score(resolved_chain, intent_analysis)
                
                # Step 8: Apply learning optimizations
                if self.learning_engine:
                    optimized_steps = self.learning_engine.optimize_execution_plan(
                        execution_steps, context, intent_analysis
                    )
                    if optimized_steps:
                        execution_steps = optimized_steps
                
                # Create orchestration plan
                plan = OrchestrationPlan(
                    plan_id=plan_id,
                    user_request=user_input,
                    tool_chain=resolved_chain,
                    execution_steps=execution_steps,
                    strategy=strategy,
                    estimated_duration=estimated_duration,
                    confidence_score=confidence_score,
                    context_snapshot=context.to_dict(),
                    required_capabilities=required_capabilities
                )
                
                # Validate plan
                validation_result = self._validate_plan(plan)
                if validation_result["valid"]:
                    plan.status = PlanStatus.VALIDATED
                else:
                    logger.warning(f"Plan validation failed: {validation_result['errors']}")
                    plan.status = PlanStatus.FAILED
                
                # Store plan
                self._active_plans[plan_id] = plan
                
                logger.info(f"Created orchestration plan {plan_id} with {len(execution_steps)} steps")
                return plan
                
            except Exception as e:
                logger.error(f"Failed to create orchestration plan: {e}")
                # Return minimal plan with error
                return OrchestrationPlan(
                    plan_id=plan_id,
                    user_request=user_input,
                    tool_chain=ToolChain(tools=[], confidence=0.0),
                    status=PlanStatus.FAILED
                )
    
    async def execute_plan(self, plan: OrchestrationPlan,
                          timeout: Optional[float] = None) -> OrchestrationResult:
        """
        Execute an orchestration plan.
        
        Args:
            plan: Orchestration plan to execute
            timeout: Optional execution timeout
            
        Returns:
            OrchestrationResult: Execution results
        """
        timeout = timeout or self.default_timeout
        plan.mark_started()
        
        try:
            # Execute plan using execution engine
            result = await self.execution_engine.execute_plan(plan, timeout)
            
            # Update plan status
            plan.mark_completed(result.success)
            
            # Learn from execution if learning is enabled
            if self.learning_engine and result.success:
                await self._learn_from_execution(plan, result)
            
            # Move to history
            with self._lock:
                if plan.plan_id in self._active_plans:
                    del self._active_plans[plan.plan_id]
                self._plan_history.append(plan)
                
                # Maintain history size
                if len(self._plan_history) > 100:
                    self._plan_history = self._plan_history[-100:]
            
            logger.info(f"Executed plan {plan.plan_id}: success={result.success}, time={result.execution_time:.2f}s")
            return result
            
        except asyncio.TimeoutError:
            plan.status = PlanStatus.FAILED
            logger.error(f"Plan {plan.plan_id} execution timed out after {timeout}s")
            
            return OrchestrationResult(
                plan_id=plan.plan_id,
                success=False,
                execution_time=timeout,
                errors=["Execution timed out"]
            )
        except Exception as e:
            plan.status = PlanStatus.FAILED
            logger.error(f"Plan {plan.plan_id} execution failed: {e}")
            
            return OrchestrationResult(
                plan_id=plan.plan_id,
                success=False,
                execution_time=plan.get_duration(),
                errors=[str(e)]
            )
    
    def get_active_plans(self) -> List[OrchestrationPlan]:
        """Get list of currently active plans."""
        with self._lock:
            return list(self._active_plans.values())
    
    def get_plan_status(self, plan_id: str) -> Optional[PlanStatus]:
        """Get status of a specific plan."""
        with self._lock:
            if plan_id in self._active_plans:
                return self._active_plans[plan_id].status
            
            # Check history
            for plan in self._plan_history:
                if plan.plan_id == plan_id:
                    return plan.status
            
            return None
    
    def cancel_plan(self, plan_id: str) -> bool:
        """
        Cancel an active orchestration plan.
        
        Args:
            plan_id: Plan identifier
            
        Returns:
            bool: True if plan was cancelled
        """
        with self._lock:
            if plan_id in self._active_plans:
                plan = self._active_plans[plan_id]
                if plan.status == PlanStatus.EXECUTING:
                    # Request cancellation from execution engine
                    self.execution_engine.cancel_execution(plan_id)
                
                plan.status = PlanStatus.CANCELLED
                logger.info(f"Cancelled plan {plan_id}")
                return True
            
            return False
    
    def suggest_tool_chain(self, intent: str, context: Context) -> List[ToolChain]:
        """
        Suggest possible tool chains for an intent.
        
        Args:
            intent: User intent or capability requirement
            context: Current context
            
        Returns:
            List[ToolChain]: Suggested tool chains
        """
        # Analyze intent
        intent_analysis = {"primary_intent": intent, "confidence": 1.0}
        
        # Get required capabilities
        required_capabilities = self._identify_required_capabilities(intent_analysis)
        
        # Get candidate tools
        candidate_tools = self._select_candidate_tools(required_capabilities, context)
        
        # Generate multiple chain suggestions
        suggestions = self.tool_chain_detector.suggest_tool_chains(
            candidate_tools, intent_analysis, context, max_suggestions=5
        )
        
        return suggestions
    
    def get_orchestration_statistics(self) -> Dict[str, Any]:
        """
        Get orchestration statistics and performance metrics.
        
        Returns:
            Dict[str, Any]: Orchestration statistics
        """
        with self._lock:
            total_plans = len(self._plan_history) + len(self._active_plans)
            completed_plans = [p for p in self._plan_history if p.status == PlanStatus.COMPLETED]
            failed_plans = [p for p in self._plan_history if p.status == PlanStatus.FAILED]
            
            if completed_plans:
                avg_execution_time = sum(p.get_duration() for p in completed_plans) / len(completed_plans)
                avg_steps = sum(len(p.execution_steps) for p in completed_plans) / len(completed_plans)
            else:
                avg_execution_time = avg_steps = 0.0
            
            return {
                "total_plans": total_plans,
                "active_plans": len(self._active_plans),
                "completed_plans": len(completed_plans),
                "failed_plans": len(failed_plans),
                "success_rate": len(completed_plans) / max(total_plans, 1),
                "average_execution_time": avg_execution_time,
                "average_steps_per_plan": avg_steps,
                "learning_enabled": self.enable_learning,
                "max_chain_length": self.max_chain_length,
                "confidence_threshold": self.confidence_threshold
            }
    
    def _analyze_user_intent(self, user_input: str, context: Context) -> Dict[str, Any]:
        """Analyze user input to extract intent and requirements."""
        # Simplified intent analysis - could be enhanced with NLP
        user_input_lower = user_input.lower()
        
        intent_patterns = {
            "file_operations": ["file", "document", "folder", "save", "open", "read", "write"],
            "data_analysis": ["analyze", "data", "chart", "graph", "statistics"],
            "web_search": ["search", "web", "find", "lookup", "google"],
            "system_operations": ["system", "process", "command", "run", "execute"],
            "communication": ["email", "message", "send", "contact"],
            "automation": ["automate", "schedule", "batch", "bulk"]
        }
        
        intent_scores = {}
        for intent, keywords in intent_patterns.items():
            score = sum(1 for keyword in keywords if keyword in user_input_lower)
            if score > 0:
                intent_scores[intent] = score / len(keywords)
        
        primary_intent = max(intent_scores.items(), key=lambda x: x[1]) if intent_scores else ("general", 0.5)
        
        return {
            "primary_intent": primary_intent[0],
            "confidence": primary_intent[1],
            "secondary_intents": [intent for intent, score in intent_scores.items() 
                                if intent != primary_intent[0] and score > 0.2],
            "user_input": user_input,
            "complexity": len(user_input.split()) / 10.0  # Simple complexity measure
        }
    
    def _identify_required_capabilities(self, intent_analysis: Dict[str, Any]) -> Set[str]:
        """Identify required capabilities based on intent analysis."""
        primary_intent = intent_analysis["primary_intent"]
        
        capability_mapping = {
            "file_operations": {"file_read", "file_write", "directory_operations"},
            "data_analysis": {"data_processing", "visualization", "statistics"},
            "web_search": {"web_request", "web_scraping", "search"},
            "system_operations": {"system_command", "process_management"},
            "communication": {"email_operations", "notification"},
            "automation": {"task_automation", "scheduling"}
        }
        
        required_capabilities = capability_mapping.get(primary_intent, {"general"})
        
        # Add secondary capabilities
        for secondary_intent in intent_analysis.get("secondary_intents", []):
            required_capabilities.update(capability_mapping.get(secondary_intent, set()))
        
        return required_capabilities
    
    def _select_candidate_tools(self, required_capabilities: Set[str], context: Context) -> List[str]:
        """Select candidate tools based on required capabilities."""
        if not self.plugin_manager:
            return []
        
        candidate_tools = []
        
        # Get tools for each required capability
        for capability in required_capabilities:
            if hasattr(self.plugin_manager, 'find_plugins_by_capability'):
                plugins = self.plugin_manager.find_plugins_by_capability(capability)
                for plugin_name in plugins:
                    tools = self.plugin_manager.get_plugin_tools(plugin_name)
                    candidate_tools.extend([tool.name for tool in tools])
        
        # Remove duplicates and return
        return list(set(candidate_tools))
    
    def _create_execution_steps(self, tool_chain: ToolChain, context: Context) -> List[ExecutionStep]:
        """Create execution steps from tool chain."""
        steps = []
        
        for i, tool_name in enumerate(tool_chain.tools):
            step = ExecutionStep(
                step_id=f"step_{i}",
                tool_name=tool_name,
                parameters={},  # Would be populated based on context and previous steps
                dependencies=[f"step_{j}" for j in range(i)],  # Simple sequential dependency
                timeout=60.0,  # Default timeout per step
                retry_count=1
            )
            steps.append(step)
        
        return steps
    
    def _estimate_execution_duration(self, execution_steps: List[ExecutionStep]) -> float:
        """Estimate total execution duration for steps."""
        # Simple estimation - could be enhanced with historical data
        return sum(step.timeout for step in execution_steps) * 0.7  # Assume 70% of timeout on average
    
    def _calculate_confidence_score(self, tool_chain: ToolChain, intent_analysis: Dict[str, Any]) -> float:
        """Calculate confidence score for the orchestration plan."""
        # Combine tool chain confidence with intent analysis confidence
        chain_confidence = tool_chain.confidence
        intent_confidence = intent_analysis.get("confidence", 0.5)
        
        # Weight them (chain confidence is more important)
        return (chain_confidence * 0.7) + (intent_confidence * 0.3)
    
    def _validate_plan(self, plan: OrchestrationPlan) -> Dict[str, Any]:
        """Validate an orchestration plan."""
        errors = []
        
        # Check if plan has execution steps
        if not plan.execution_steps:
            errors.append("Plan has no execution steps")
        
        # Check confidence threshold
        if plan.confidence_score < self.confidence_threshold:
            errors.append(f"Confidence score {plan.confidence_score:.2f} below threshold {self.confidence_threshold}")
        
        # Check chain length
        if len(plan.tool_chain.tools) > self.max_chain_length:
            errors.append(f"Tool chain length {len(plan.tool_chain.tools)} exceeds maximum {self.max_chain_length}")
        
        # Check for circular dependencies
        if self._has_circular_dependencies(plan.execution_steps):
            errors.append("Plan has circular dependencies")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
    
    def _has_circular_dependencies(self, steps: List[ExecutionStep]) -> bool:
        """Check if execution steps have circular dependencies."""
        # Simple cycle detection - could be enhanced
        step_deps = {step.step_id: set(step.dependencies) for step in steps}
        
        def has_cycle(node, visited, rec_stack):
            visited.add(node)
            rec_stack.add(node)
            
            for neighbor in step_deps.get(node, set()):
                if neighbor not in visited:
                    if has_cycle(neighbor, visited, rec_stack):
                        return True
                elif neighbor in rec_stack:
                    return True
            
            rec_stack.remove(node)
            return False
        
        visited = set()
        for step in steps:
            if step.step_id not in visited:
                if has_cycle(step.step_id, visited, set()):
                    return True
        
        return False
    
    async def _learn_from_execution(self, plan: OrchestrationPlan, result: OrchestrationResult) -> None:
        """Learn from successful plan execution."""
        if self.learning_engine:
            learning_data = {
                "plan": plan,
                "result": result,
                "context": plan.context_snapshot,
                "performance_metrics": {
                    "execution_time": result.execution_time,
                    "success_rate": result.get_success_rate(),
                    "tool_sequence": result.tools_executed
                }
            }
            
            await self.learning_engine.learn_from_execution(learning_data)
