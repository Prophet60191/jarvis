"""
Execution Engine for Tool Orchestration

Executes orchestrated tool chains with proper error handling,
monitoring, and result aggregation.
"""

import time
import logging
import asyncio
from typing import Dict, List, Optional, Any, Set, Callable
from dataclasses import dataclass, field
from enum import Enum
import threading

logger = logging.getLogger(__name__)

class ExecutionStatus(Enum):
    """Execution status values."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"

class ExecutionMode(Enum):
    """Execution modes."""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    CONDITIONAL = "conditional"
    PIPELINE = "pipeline"

@dataclass
class ExecutionStep:
    """Represents a single execution step."""
    step_id: str
    tool_name: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    
    # Dependencies
    depends_on: List[str] = field(default_factory=list)
    
    # Execution details
    status: ExecutionStatus = ExecutionStatus.PENDING
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    result: Any = None
    error: Optional[str] = None
    
    # Configuration
    timeout: Optional[float] = None
    retry_count: int = 0
    max_retries: int = 3
    
    def get_duration(self) -> Optional[float]:
        """Get execution duration."""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return None
    
    def is_complete(self) -> bool:
        """Check if step is complete."""
        return self.status in [ExecutionStatus.COMPLETED, ExecutionStatus.FAILED, 
                              ExecutionStatus.CANCELLED, ExecutionStatus.TIMEOUT]

@dataclass
class ExecutionPlan:
    """Represents an execution plan."""
    plan_id: str
    steps: List[ExecutionStep] = field(default_factory=list)
    execution_mode: ExecutionMode = ExecutionMode.SEQUENTIAL
    
    # Plan metadata
    created_at: float = field(default_factory=time.time)
    estimated_duration: Optional[float] = None
    
    # Execution state
    status: ExecutionStatus = ExecutionStatus.PENDING
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    
    def get_pending_steps(self) -> List[ExecutionStep]:
        """Get steps that are pending execution."""
        return [step for step in self.steps if step.status == ExecutionStatus.PENDING]
    
    def get_ready_steps(self) -> List[ExecutionStep]:
        """Get steps that are ready to execute (dependencies met)."""
        ready_steps = []
        
        for step in self.get_pending_steps():
            # Check if all dependencies are completed
            dependencies_met = True
            for dep_id in step.depends_on:
                dep_step = self.get_step(dep_id)
                if not dep_step or dep_step.status != ExecutionStatus.COMPLETED:
                    dependencies_met = False
                    break
            
            if dependencies_met:
                ready_steps.append(step)
        
        return ready_steps
    
    def get_step(self, step_id: str) -> Optional[ExecutionStep]:
        """Get a step by ID."""
        for step in self.steps:
            if step.step_id == step_id:
                return step
        return None

class ExecutionEngine:
    """
    Execution engine for orchestrated tool chains.
    
    This component executes tool chains according to orchestration plans,
    handling dependencies, errors, and result aggregation.
    """
    
    def __init__(self, max_concurrent_executions: int = 5):
        """
        Initialize the execution engine.
        
        Args:
            max_concurrent_executions: Maximum concurrent executions
        """
        self.max_concurrent_executions = max_concurrent_executions
        
        # Execution tracking
        self._active_executions: Dict[str, ExecutionPlan] = {}
        self._completed_executions: List[ExecutionPlan] = []
        
        # Tool registry (would be injected in real implementation)
        self._tool_registry: Dict[str, Callable] = {}
        
        # Configuration
        self.default_timeout = 300  # 5 minutes
        self.enable_retries = True
        self.enable_parallel_execution = True
        
        # Thread safety
        self._lock = threading.RLock()
        
        logger.info("ExecutionEngine initialized")
    
    def register_tool(self, tool_name: str, tool_function: Callable) -> None:
        """
        Register a tool for execution.
        
        Args:
            tool_name: Name of the tool
            tool_function: Function to execute
        """
        with self._lock:
            self._tool_registry[tool_name] = tool_function
            logger.debug(f"Registered tool: {tool_name}")
    
    async def execute_plan(self, plan: ExecutionPlan) -> Dict[str, Any]:
        """
        Execute an orchestration plan.
        
        Args:
            plan: Execution plan to run
            
        Returns:
            Dict[str, Any]: Execution results
        """
        with self._lock:
            if len(self._active_executions) >= self.max_concurrent_executions:
                raise RuntimeError("Maximum concurrent executions reached")
            
            self._active_executions[plan.plan_id] = plan
        
        try:
            logger.info(f"Starting execution of plan {plan.plan_id}")
            
            # Update plan status
            plan.status = ExecutionStatus.RUNNING
            plan.start_time = time.time()
            
            # Execute based on mode
            if plan.execution_mode == ExecutionMode.SEQUENTIAL:
                result = await self._execute_sequential(plan)
            elif plan.execution_mode == ExecutionMode.PARALLEL:
                result = await self._execute_parallel(plan)
            elif plan.execution_mode == ExecutionMode.CONDITIONAL:
                result = await self._execute_conditional(plan)
            elif plan.execution_mode == ExecutionMode.PIPELINE:
                result = await self._execute_pipeline(plan)
            else:
                raise ValueError(f"Unsupported execution mode: {plan.execution_mode}")
            
            # Update plan status
            plan.status = ExecutionStatus.COMPLETED
            plan.end_time = time.time()
            
            logger.info(f"Completed execution of plan {plan.plan_id}")
            return result
            
        except Exception as e:
            plan.status = ExecutionStatus.FAILED
            plan.end_time = time.time()
            logger.error(f"Failed to execute plan {plan.plan_id}: {e}")
            raise
        
        finally:
            # Move to completed executions
            with self._lock:
                if plan.plan_id in self._active_executions:
                    del self._active_executions[plan.plan_id]
                    self._completed_executions.append(plan)
                    
                    # Maintain completed executions list size
                    if len(self._completed_executions) > 100:
                        self._completed_executions = self._completed_executions[-100:]
    
    async def execute_step(self, step: ExecutionStep) -> Any:
        """
        Execute a single step.
        
        Args:
            step: Step to execute
            
        Returns:
            Any: Step execution result
        """
        if step.tool_name not in self._tool_registry:
            raise ValueError(f"Tool {step.tool_name} not registered")
        
        tool_function = self._tool_registry[step.tool_name]
        
        # Update step status
        step.status = ExecutionStatus.RUNNING
        step.start_time = time.time()
        
        try:
            # Execute with timeout
            timeout = step.timeout or self.default_timeout
            
            if asyncio.iscoroutinefunction(tool_function):
                result = await asyncio.wait_for(
                    tool_function(**step.parameters),
                    timeout=timeout
                )
            else:
                # Run synchronous function in executor
                loop = asyncio.get_event_loop()
                result = await asyncio.wait_for(
                    loop.run_in_executor(None, lambda: tool_function(**step.parameters)),
                    timeout=timeout
                )
            
            # Update step with result
            step.result = result
            step.status = ExecutionStatus.COMPLETED
            step.end_time = time.time()
            
            logger.debug(f"Completed step {step.step_id}")
            return result
            
        except asyncio.TimeoutError:
            step.status = ExecutionStatus.TIMEOUT
            step.end_time = time.time()
            step.error = f"Step timed out after {timeout} seconds"
            logger.error(f"Step {step.step_id} timed out")
            raise
            
        except Exception as e:
            step.status = ExecutionStatus.FAILED
            step.end_time = time.time()
            step.error = str(e)
            
            # Retry if enabled and retries remaining
            if self.enable_retries and step.retry_count < step.max_retries:
                step.retry_count += 1
                step.status = ExecutionStatus.PENDING
                step.start_time = None
                step.end_time = None
                step.error = None
                
                logger.warning(f"Retrying step {step.step_id} (attempt {step.retry_count})")
                return await self.execute_step(step)
            
            logger.error(f"Step {step.step_id} failed: {e}")
            raise
    
    def get_execution_status(self, plan_id: str) -> Optional[Dict[str, Any]]:
        """
        Get execution status for a plan.
        
        Args:
            plan_id: Plan identifier
            
        Returns:
            Optional[Dict[str, Any]]: Execution status or None if not found
        """
        with self._lock:
            # Check active executions
            if plan_id in self._active_executions:
                plan = self._active_executions[plan_id]
                return self._get_plan_status(plan)
            
            # Check completed executions
            for plan in self._completed_executions:
                if plan.plan_id == plan_id:
                    return self._get_plan_status(plan)
            
            return None
    
    def cancel_execution(self, plan_id: str) -> bool:
        """
        Cancel an active execution.
        
        Args:
            plan_id: Plan identifier
            
        Returns:
            bool: True if cancellation was successful
        """
        with self._lock:
            if plan_id not in self._active_executions:
                return False
            
            plan = self._active_executions[plan_id]
            plan.status = ExecutionStatus.CANCELLED
            plan.end_time = time.time()
            
            # Cancel running steps
            for step in plan.steps:
                if step.status == ExecutionStatus.RUNNING:
                    step.status = ExecutionStatus.CANCELLED
                    step.end_time = time.time()
            
            logger.info(f"Cancelled execution of plan {plan_id}")
            return True
    
    def get_engine_statistics(self) -> Dict[str, Any]:
        """Get execution engine statistics."""
        with self._lock:
            active_count = len(self._active_executions)
            completed_count = len(self._completed_executions)
            
            # Calculate success rate
            successful_executions = sum(
                1 for plan in self._completed_executions 
                if plan.status == ExecutionStatus.COMPLETED
            )
            
            success_rate = 0.0
            if completed_count > 0:
                success_rate = (successful_executions / completed_count) * 100
            
            return {
                "active_executions": active_count,
                "completed_executions": completed_count,
                "successful_executions": successful_executions,
                "success_rate": success_rate,
                "registered_tools": len(self._tool_registry),
                "max_concurrent_executions": self.max_concurrent_executions,
                "default_timeout": self.default_timeout
            }
    
    async def _execute_sequential(self, plan: ExecutionPlan) -> Dict[str, Any]:
        """Execute steps sequentially."""
        results = {}
        
        for step in plan.steps:
            try:
                result = await self.execute_step(step)
                results[step.step_id] = result
            except Exception as e:
                results[step.step_id] = {"error": str(e)}
                # Stop execution on failure in sequential mode
                break
        
        return results
    
    async def _execute_parallel(self, plan: ExecutionPlan) -> Dict[str, Any]:
        """Execute steps in parallel where possible."""
        results = {}
        remaining_steps = plan.steps.copy()
        
        while remaining_steps:
            # Get steps ready for execution
            ready_steps = []
            for step in remaining_steps:
                dependencies_met = True
                for dep_id in step.depends_on:
                    if dep_id not in results or "error" in results.get(dep_id, {}):
                        dependencies_met = False
                        break
                
                if dependencies_met:
                    ready_steps.append(step)
            
            if not ready_steps:
                # No steps ready - check for circular dependencies
                break
            
            # Execute ready steps in parallel
            tasks = [self.execute_step(step) for step in ready_steps]
            step_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            for step, result in zip(ready_steps, step_results):
                if isinstance(result, Exception):
                    results[step.step_id] = {"error": str(result)}
                else:
                    results[step.step_id] = result
                
                remaining_steps.remove(step)
        
        return results
    
    async def _execute_conditional(self, plan: ExecutionPlan) -> Dict[str, Any]:
        """Execute steps with conditional logic."""
        # Simplified conditional execution
        return await self._execute_sequential(plan)
    
    async def _execute_pipeline(self, plan: ExecutionPlan) -> Dict[str, Any]:
        """Execute steps as a pipeline."""
        results = {}
        previous_result = None
        
        for step in plan.steps:
            # Pass previous result as input if available
            if previous_result is not None:
                step.parameters["previous_result"] = previous_result
            
            try:
                result = await self.execute_step(step)
                results[step.step_id] = result
                previous_result = result
            except Exception as e:
                results[step.step_id] = {"error": str(e)}
                break
        
        return results
    
    def _get_plan_status(self, plan: ExecutionPlan) -> Dict[str, Any]:
        """Get status information for a plan."""
        completed_steps = sum(1 for step in plan.steps if step.is_complete())
        total_steps = len(plan.steps)
        
        return {
            "plan_id": plan.plan_id,
            "status": plan.status.value,
            "execution_mode": plan.execution_mode.value,
            "progress": {
                "completed_steps": completed_steps,
                "total_steps": total_steps,
                "percentage": (completed_steps / max(total_steps, 1)) * 100
            },
            "timing": {
                "start_time": plan.start_time,
                "end_time": plan.end_time,
                "duration": plan.end_time - plan.start_time if plan.start_time and plan.end_time else None
            },
            "steps": [
                {
                    "step_id": step.step_id,
                    "tool_name": step.tool_name,
                    "status": step.status.value,
                    "duration": step.get_duration(),
                    "error": step.error
                }
                for step in plan.steps
            ]
        }
