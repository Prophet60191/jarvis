"""
RAG-Powered Workflow System

Replaces hardcoded workflows with intelligent, knowledge-driven workflow construction.
Uses RAG to dynamically discover plugins, learn from past experiences, and build
optimal workflows based on accumulated knowledge.
"""

import asyncio
import logging
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class WorkflowStage(Enum):
    """Stages in any workflow."""
    ANALYSIS = "analysis"
    PLANNING = "planning"
    EXECUTION = "execution"
    VALIDATION = "validation"
    LEARNING = "learning"
    COMPLETE = "complete"


@dataclass
class WorkflowStep:
    """Individual step in a workflow."""
    plugin_name: str
    tool_name: str
    parameters: Dict[str, Any]
    expected_output: str
    success_criteria: List[str]
    fallback_options: List[str] = None


@dataclass
class WorkflowPlan:
    """Complete workflow plan."""
    workflow_id: str
    request: str
    steps: List[WorkflowStep]
    estimated_duration: int
    confidence_score: float
    reasoning: str


class RAGPoweredWorkflowBuilder:
    """
    Intelligent workflow builder that uses RAG to:
    1. Discover available plugins dynamically
    2. Learn from past workflow experiences
    3. Build optimal workflows based on knowledge
    4. Adapt and improve over time
    """
    
    def __init__(self, rag_service=None, plugin_registry=None):
        self.rag_service = rag_service
        self.plugin_registry = plugin_registry
        self.workflow_history = []
        self.learning_enabled = True
        
    async def initialize(self):
        """Initialize the RAG-powered workflow builder."""
        if not self.rag_service:
            await self._initialize_rag_service()
        
        if not self.plugin_registry:
            await self._initialize_plugin_registry()
        
        # Index current plugin capabilities in RAG
        await self._index_plugin_knowledge()
        
        logger.info("RAG-Powered Workflow Builder initialized")
    
    async def build_workflow(self, user_request: str) -> WorkflowPlan:
        """
        Build an optimal workflow for the user request using RAG knowledge.
        """
        workflow_id = f"workflow_{int(time.time())}"
        
        logger.info(f"🧠 Building RAG-powered workflow for: {user_request}")
        
        # Step 1: Analyze the request using RAG
        request_analysis = await self._analyze_request_with_rag(user_request)
        
        # Step 2: Query RAG for relevant plugins
        plugin_knowledge = await self._query_plugin_knowledge(user_request, request_analysis)
        
        # Step 3: Query RAG for workflow patterns
        workflow_patterns = await self._query_workflow_patterns(user_request, request_analysis)
        
        # Step 4: Query RAG for past experiences
        past_experiences = await self._query_past_experiences(user_request, request_analysis)
        
        # Step 5: Synthesize optimal workflow
        workflow_plan = await self._synthesize_workflow(
            workflow_id, user_request, request_analysis,
            plugin_knowledge, workflow_patterns, past_experiences
        )
        
        logger.info(f"✅ Workflow plan created with {len(workflow_plan.steps)} steps")
        return workflow_plan
    
    async def execute_workflow(self, workflow_plan: WorkflowPlan) -> Dict[str, Any]:
        """Execute the workflow plan and learn from the results."""
        logger.info(f"🚀 Executing workflow: {workflow_plan.workflow_id}")
        
        execution_results = {
            "workflow_id": workflow_plan.workflow_id,
            "request": workflow_plan.request,
            "steps_completed": 0,
            "total_steps": len(workflow_plan.steps),
            "results": [],
            "success": False,
            "errors": [],
            "duration": 0
        }
        
        start_time = time.time()
        
        try:
            for i, step in enumerate(workflow_plan.steps):
                logger.info(f"📋 Executing step {i+1}/{len(workflow_plan.steps)}: {step.plugin_name}.{step.tool_name}")
                
                step_result = await self._execute_workflow_step(step)
                execution_results["results"].append(step_result)
                
                if step_result["success"]:
                    execution_results["steps_completed"] += 1
                else:
                    # Try fallback options if available
                    if step.fallback_options:
                        fallback_success = await self._try_fallback_options(step, step.fallback_options)
                        if fallback_success:
                            execution_results["steps_completed"] += 1
                        else:
                            execution_results["errors"].append(f"Step {i+1} failed: {step_result.get('error', 'Unknown error')}")
                            break
                    else:
                        execution_results["errors"].append(f"Step {i+1} failed: {step_result.get('error', 'Unknown error')}")
                        break
            
            execution_results["success"] = execution_results["steps_completed"] == execution_results["total_steps"]
            execution_results["duration"] = time.time() - start_time
            
            # Learn from this execution
            if self.learning_enabled:
                await self._learn_from_execution(workflow_plan, execution_results)
            
            logger.info(f"✅ Workflow completed: {execution_results['success']}")
            return execution_results
            
        except Exception as e:
            execution_results["errors"].append(f"Workflow execution failed: {str(e)}")
            execution_results["duration"] = time.time() - start_time
            logger.error(f"❌ Workflow execution failed: {e}")
            return execution_results
    
    async def _analyze_request_with_rag(self, user_request: str) -> Dict[str, Any]:
        """Use RAG to analyze and categorize the user request."""
        analysis_query = f"""
        Analyze this user request for workflow planning:
        Request: "{user_request}"
        
        Provide analysis including:
        - Request type (web_app, desktop_app, tool, script, api, etc.)
        - Complexity level (simple, medium, complex)
        - Required technologies (python, javascript, html, css, etc.)
        - Key requirements and constraints
        - Expected deliverables
        """
        
        try:
            if self.rag_service:
                rag_response = await self.rag_service.query(analysis_query)
                # Parse RAG response into structured analysis
                return self._parse_analysis_response(rag_response)
            else:
                # Fallback to simple analysis
                return self._simple_request_analysis(user_request)
        except Exception as e:
            logger.warning(f"RAG analysis failed, using fallback: {e}")
            return self._simple_request_analysis(user_request)
    
    async def _query_plugin_knowledge(self, user_request: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Query RAG for knowledge about available plugins."""
        plugin_query = f"""
        What plugins are available for this type of request?
        Request: "{user_request}"
        Type: {analysis.get('request_type', 'unknown')}
        Technologies: {analysis.get('technologies', [])}
        
        For each relevant plugin, provide:
        - Plugin name and capabilities
        - What it can do and cannot do
        - Typical usage patterns
        - Integration requirements
        - Performance characteristics
        """
        
        try:
            if self.rag_service:
                response = await self.rag_service.query(plugin_query)
                return response
            else:
                return self._get_available_plugins_fallback(analysis)
        except Exception as e:
            logger.warning(f"Plugin knowledge query failed: {e}")
            return self._get_available_plugins_fallback(analysis)
    
    async def _query_workflow_patterns(self, user_request: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Query RAG for successful workflow patterns."""
        pattern_query = f"""
        What are successful workflow patterns for this type of request?
        Request: "{user_request}"
        Type: {analysis.get('request_type', 'unknown')}
        
        Provide information about:
        - Typical workflow stages and order
        - Which tools work well together
        - Common pitfalls and how to avoid them
        - Success criteria for each stage
        - Optimization opportunities
        """
        
        try:
            if self.rag_service:
                response = await self.rag_service.query(pattern_query)
                return response
            else:
                return self._get_default_workflow_patterns(analysis)
        except Exception as e:
            logger.warning(f"Workflow pattern query failed: {e}")
            return self._get_default_workflow_patterns(analysis)
    
    async def _query_past_experiences(self, user_request: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Query RAG for past experiences with similar requests."""
        experience_query = f"""
        What past experiences are relevant to this request?
        Request: "{user_request}"
        Type: {analysis.get('request_type', 'unknown')}
        
        Look for:
        - Similar requests that were handled successfully
        - Common challenges and their solutions
        - Performance insights and optimizations
        - User feedback and improvements made
        - Lessons learned from failures
        """
        
        try:
            if self.rag_service:
                response = await self.rag_service.query(experience_query)
                return {"experiences": [response], "lessons": []}
            else:
                return {"experiences": [], "lessons": []}
        except Exception as e:
            logger.warning(f"Past experience query failed: {e}")
            return {"experiences": [], "lessons": []}
    
    def _parse_analysis_response(self, rag_response: str) -> Dict[str, Any]:
        """Parse RAG response into structured analysis."""
        # Simple parsing - in production, this would be more sophisticated
        analysis = {
            "request_type": "application",
            "complexity": "medium",
            "technologies": ["python"],
            "requirements": [],
            "deliverables": []
        }
        
        response_lower = rag_response.lower()
        
        # Extract request type
        if any(term in response_lower for term in ["web", "html", "css", "javascript"]):
            analysis["request_type"] = "web_application"
        elif any(term in response_lower for term in ["desktop", "gui", "tkinter"]):
            analysis["request_type"] = "desktop_application"
        elif any(term in response_lower for term in ["api", "rest", "endpoint"]):
            analysis["request_type"] = "api_application"
        elif any(term in response_lower for term in ["tool", "utility", "script"]):
            analysis["request_type"] = "tool"
        
        # Extract complexity
        if any(term in response_lower for term in ["simple", "basic", "easy"]):
            analysis["complexity"] = "simple"
        elif any(term in response_lower for term in ["complex", "advanced", "sophisticated"]):
            analysis["complexity"] = "complex"
        
        # Extract technologies
        technologies = []
        if "python" in response_lower:
            technologies.append("python")
        if any(term in response_lower for term in ["javascript", "js"]):
            technologies.append("javascript")
        if "html" in response_lower:
            technologies.append("html")
        if "css" in response_lower:
            technologies.append("css")
        
        if technologies:
            analysis["technologies"] = technologies
        
        return analysis
    
    def _simple_request_analysis(self, user_request: str) -> Dict[str, Any]:
        """Fallback simple analysis when RAG is not available."""
        request_lower = user_request.lower()
        
        analysis = {
            "request_type": "application",
            "complexity": "medium",
            "technologies": ["python"],
            "requirements": [user_request],
            "deliverables": ["working application"]
        }
        
        # Simple keyword-based analysis
        if any(term in request_lower for term in ["ui", "interface", "web", "html", "button"]):
            analysis["request_type"] = "web_application"
            analysis["technologies"] = ["html", "css", "javascript"]
        elif any(term in request_lower for term in ["tool", "script", "utility"]):
            analysis["request_type"] = "tool"
            analysis["technologies"] = ["python"]
        
        return analysis

    async def _synthesize_workflow(self, workflow_id: str, user_request: str,
                                 analysis: Dict[str, Any], plugin_knowledge: Any,
                                 workflow_patterns: Any, past_experiences: Any) -> WorkflowPlan:
        """Synthesize all knowledge into an optimal workflow plan."""

        steps = []

        # Based on analysis, create workflow steps
        request_type = analysis.get("request_type", "application")
        complexity = analysis.get("complexity", "medium")
        technologies = analysis.get("technologies", ["python"])

        if request_type == "web_application":
            # Web application workflow
            steps.extend([
                WorkflowStep(
                    plugin_name="aider_integration",
                    tool_name="aider_code_edit",
                    parameters={
                        "task_description": f"Create a web application for: {user_request}",
                        "technologies": technologies,
                        "complexity": complexity
                    },
                    expected_output="HTML, CSS, JavaScript files",
                    success_criteria=["Files created", "Valid HTML structure", "Working functionality"],
                    fallback_options=["manual_code_generation"]
                ),
                WorkflowStep(
                    plugin_name="open_interpreter",
                    tool_name="test_and_validate",
                    parameters={
                        "files_to_test": "generated web files",
                        "test_type": "web_application"
                    },
                    expected_output="Test results and validation",
                    success_criteria=["No syntax errors", "Basic functionality works"],
                    fallback_options=["manual_testing"]
                )
            ])

        elif request_type == "tool":
            # Tool creation workflow
            steps.extend([
                WorkflowStep(
                    plugin_name="aider_integration",
                    tool_name="aider_code_edit",
                    parameters={
                        "task_description": f"Create a tool for: {user_request}",
                        "technologies": technologies,
                        "complexity": complexity
                    },
                    expected_output="Python script or tool",
                    success_criteria=["Script created", "Proper error handling", "Documentation included"],
                    fallback_options=["template_based_generation"]
                ),
                WorkflowStep(
                    plugin_name="open_interpreter",
                    tool_name="test_and_run",
                    parameters={
                        "script_path": "generated tool",
                        "test_type": "tool"
                    },
                    expected_output="Tool execution results",
                    success_criteria=["Tool runs without errors", "Produces expected output"],
                    fallback_options=["manual_execution"]
                )
            ])

        else:
            # Generic application workflow
            steps.extend([
                WorkflowStep(
                    plugin_name="aider_integration",
                    tool_name="aider_code_edit",
                    parameters={
                        "task_description": user_request,
                        "technologies": technologies,
                        "complexity": complexity
                    },
                    expected_output="Application files",
                    success_criteria=["Files created", "Code compiles", "Basic functionality"],
                    fallback_options=["template_based_generation"]
                ),
                WorkflowStep(
                    plugin_name="open_interpreter",
                    tool_name="validate_and_test",
                    parameters={
                        "application_files": "generated files",
                        "test_type": "application"
                    },
                    expected_output="Validation results",
                    success_criteria=["Application runs", "No critical errors"],
                    fallback_options=["manual_validation"]
                )
            ])

        # Calculate confidence score based on available knowledge
        confidence_score = self._calculate_confidence_score(
            analysis, plugin_knowledge, workflow_patterns, past_experiences
        )

        # Estimate duration based on complexity and steps
        estimated_duration = len(steps) * (30 if complexity == "simple" else 60 if complexity == "medium" else 120)

        reasoning = f"Workflow built for {request_type} using {len(steps)} steps based on RAG knowledge analysis"

        return WorkflowPlan(
            workflow_id=workflow_id,
            request=user_request,
            steps=steps,
            estimated_duration=estimated_duration,
            confidence_score=confidence_score,
            reasoning=reasoning
        )

    async def _execute_workflow_step(self, step: WorkflowStep) -> Dict[str, Any]:
        """Execute a single workflow step."""
        try:
            # Get the plugin dynamically
            if self.plugin_registry:
                plugin = await self.plugin_registry.get_plugin(step.plugin_name)
                if plugin:
                    tool = getattr(plugin, step.tool_name, None)
                    if tool:
                        # Check if tool has invoke method
                        if hasattr(tool, 'invoke'):
                            # Try async first, then sync
                            try:
                                if asyncio.iscoroutinefunction(tool.invoke):
                                    result = await tool.invoke(step.parameters)
                                else:
                                    result = tool.invoke(step.parameters)
                            except TypeError:
                                # Fallback for different invoke signatures
                                result = tool.invoke(**step.parameters)
                        else:
                            # Direct method call
                            if asyncio.iscoroutinefunction(tool):
                                result = await tool(**step.parameters)
                            else:
                                result = tool(**step.parameters)

                        return {
                            "success": True,
                            "result": result,
                            "step": step.plugin_name + "." + step.tool_name
                        }

            # Fallback to hardcoded execution (temporary)
            return await self._execute_step_fallback(step)

        except Exception as e:
            logger.error(f"Step execution failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "step": step.plugin_name + "." + step.tool_name
            }

    async def _execute_step_fallback(self, step: WorkflowStep) -> Dict[str, Any]:
        """Fallback execution for when dynamic plugin loading fails."""
        # This is temporary - eventually all execution should be dynamic
        if step.plugin_name == "aider_integration":
            try:
                from ...tools.plugins.aider_integration import aider_code_edit
                result = aider_code_edit.invoke(step.parameters)
                return {"success": True, "result": result, "step": "aider_integration.aider_code_edit"}
            except Exception as e:
                return {"success": False, "error": str(e), "step": "aider_integration.aider_code_edit"}

        elif step.plugin_name == "open_interpreter":
            try:
                from ...tools.open_interpreter_direct import OpenInterpreterDirect
                oi = OpenInterpreterDirect()
                result = await oi.execute_task(step.parameters.get("task_description", "Test the generated code"))
                return {"success": True, "result": result, "step": "open_interpreter.execute"}
            except Exception as e:
                return {"success": False, "error": str(e), "step": "open_interpreter.execute"}

        return {"success": False, "error": "Unknown plugin", "step": step.plugin_name}

    async def _try_fallback_options(self, step: WorkflowStep, fallback_options: List[str]) -> bool:
        """Try fallback options when a step fails."""
        for fallback in fallback_options:
            try:
                logger.info(f"🔄 Trying fallback: {fallback}")
                # Implement fallback logic here
                # For now, just return False to indicate fallback failed
                return False
            except Exception as e:
                logger.warning(f"Fallback {fallback} failed: {e}")
                continue
        return False

    def _calculate_confidence_score(self, analysis: Dict[str, Any], plugin_knowledge: Any,
                                  workflow_patterns: Any, past_experiences: Any) -> float:
        """Calculate confidence score for the workflow plan."""
        base_score = 0.5

        # Boost confidence based on available knowledge
        if plugin_knowledge:
            base_score += 0.2
        if workflow_patterns:
            base_score += 0.2
        if past_experiences:
            base_score += 0.1

        # Adjust based on complexity
        complexity = analysis.get("complexity", "medium")
        if complexity == "simple":
            base_score += 0.1
        elif complexity == "complex":
            base_score -= 0.1

        return min(1.0, max(0.1, base_score))

    async def _learn_from_execution(self, workflow_plan: WorkflowPlan, execution_results: Dict[str, Any]):
        """Learn from workflow execution to improve future workflows."""
        if not self.rag_service:
            return

        # Create learning document
        learning_doc = {
            "timestamp": datetime.now().isoformat(),
            "request": workflow_plan.request,
            "workflow_id": workflow_plan.workflow_id,
            "success": execution_results["success"],
            "duration": execution_results["duration"],
            "steps_completed": execution_results["steps_completed"],
            "total_steps": execution_results["total_steps"],
            "errors": execution_results["errors"],
            "lessons": []
        }

        # Extract lessons
        if execution_results["success"]:
            learning_doc["lessons"].append(f"Successful workflow pattern for {workflow_plan.request}")
            learning_doc["lessons"].append(f"Optimal step sequence: {[step.plugin_name for step in workflow_plan.steps]}")
        else:
            learning_doc["lessons"].append(f"Failed workflow - avoid this pattern for similar requests")
            if execution_results["errors"]:
                learning_doc["lessons"].append(f"Common errors: {execution_results['errors']}")

        # Store in RAG for future reference
        try:
            learning_text = f"""
            Workflow Learning Entry:
            Request: {workflow_plan.request}
            Success: {execution_results['success']}
            Duration: {execution_results['duration']}s
            Steps: {[step.plugin_name + '.' + step.tool_name for step in workflow_plan.steps]}
            Lessons: {'; '.join(learning_doc['lessons'])}
            """

            # Add to RAG knowledge base
            await self.rag_service.add_document(learning_text, {
                "type": "workflow_learning",
                "success": execution_results["success"],
                "request_type": workflow_plan.request
            })

            logger.info(f"📚 Learned from workflow execution: {workflow_plan.workflow_id}")

        except Exception as e:
            logger.warning(f"Failed to store learning: {e}")

    async def _initialize_rag_service(self):
        """Initialize RAG service if not provided."""
        try:
            from ...tools.rag_service import RAGService
            from ...config import LLMConfig

            # Create config for RAG service
            config = LLMConfig()
            self.rag_service = RAGService(config)
            # RAGService doesn't have an async initialize method, it initializes in __init__
            logger.info("RAG service initialized successfully")
        except Exception as e:
            logger.warning(f"Could not initialize RAG service: {e}")
            self.rag_service = None

    async def _initialize_plugin_registry(self):
        """Initialize plugin registry if not provided."""
        try:
            from ...plugins.registry.unified_registry import UnifiedPluginRegistry
            self.plugin_registry = UnifiedPluginRegistry()
            # UnifiedPluginRegistry initializes in __init__, no async initialize method needed
            logger.info("Plugin registry initialized successfully")
        except Exception as e:
            logger.warning(f"Could not initialize plugin registry: {e}")
            self.plugin_registry = None

    async def _index_plugin_knowledge(self):
        """Index current plugin capabilities in RAG."""
        if not self.rag_service or not self.plugin_registry:
            return

        try:
            # Get all available plugins
            plugins = await self.plugin_registry.get_all_plugins()

            for plugin_name, plugin_info in plugins.items():
                # Create knowledge document for each plugin
                plugin_doc = f"""
                Plugin: {plugin_name}
                Capabilities: {plugin_info.get('capabilities', [])}
                Tools: {plugin_info.get('tools', [])}
                Description: {plugin_info.get('description', 'No description')}
                Usage Patterns: {plugin_info.get('usage_patterns', [])}
                Limitations: {plugin_info.get('limitations', [])}
                """

                await self.rag_service.add_document(plugin_doc, {
                    "type": "plugin_knowledge",
                    "plugin_name": plugin_name
                })

            logger.info(f"📚 Indexed {len(plugins)} plugins in RAG knowledge base")

        except Exception as e:
            logger.warning(f"Failed to index plugin knowledge: {e}")

    def _get_available_plugins_fallback(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback method to get available plugins when RAG is not available."""
        return {
            "available_plugins": [
                "aider_integration - Code generation and editing",
                "open_interpreter - Code execution and testing",
                "lavague_web_automation - Web automation and testing"
            ],
            "recommended": ["aider_integration", "open_interpreter"]
        }

    def _get_default_workflow_patterns(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback workflow patterns when RAG is not available."""
        request_type = analysis.get("request_type", "application")

        patterns = {
            "web_application": ["code_generation", "testing", "validation"],
            "desktop_application": ["code_generation", "testing", "packaging"],
            "tool": ["code_generation", "testing", "documentation"],
            "api_application": ["code_generation", "testing", "deployment"]
        }

        return {
            "pattern": patterns.get(request_type, ["code_generation", "testing"]),
            "reasoning": f"Standard pattern for {request_type}"
        }
