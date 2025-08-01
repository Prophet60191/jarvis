"""
Unified Coding Workflow Integration

This module integrates the unified coding workflow with the Jarvis agent system.
It replaces the complex orchestration system with a simpler, more reliable approach.
"""

import asyncio
import logging
import re
from typing import Optional

from .rag_powered_workflow import RAGPoweredWorkflowBuilder
from ..context import Context
from dataclasses import dataclass
from typing import List


@dataclass
class OrchestrationResult:
    """Result of workflow orchestration."""
    plan_id: str
    success: bool
    execution_time: float
    tools_executed: List[str]
    results: List[str]
    errors: List[str]

logger = logging.getLogger(__name__)


class UnifiedCodingIntegration:
    """
    Integration layer for the unified coding workflow.
    
    This class:
    1. Detects coding requests
    2. Routes them to the unified workflow
    3. Provides fallback for non-coding requests
    """
    
    def __init__(self):
        self.enabled = True
        self.rag_workflow_builder = None
        self.use_rag_workflow = True  # Flag to enable/disable RAG-powered workflow
        self._initialization_attempted = False
        logger.info("UnifiedCodingIntegration initialized")

    async def initialize_rag_workflow(self):
        """Initialize the RAG-powered workflow builder."""
        try:
            self.rag_workflow_builder = RAGPoweredWorkflowBuilder()
            await self.rag_workflow_builder.initialize()
            logger.info("🧠 RAG-powered workflow builder initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize RAG workflow builder: {e}")
            self.use_rag_workflow = False
    
    def is_coding_request(self, user_request: str) -> bool:
        """
        Determine if a request should be handled by the coding workflow.

        This is more inclusive than the previous system - any request that involves
        creating, building, or implementing something gets routed to the coding workflow.

        EXCLUDES execution requests like "run", "execute", "launch" existing files.
        """
        request_lower = user_request.lower()

        # First check for execution verbs that should NOT trigger coding workflow
        execution_verbs = [
            "run", "execute", "launch", "start", "open", "show", "display"
        ]

        # If request starts with execution verb + existing file, it's NOT coding
        for verb in execution_verbs:
            if re.search(rf"\b{verb}\b.*\.(py|js|html|css|sh|exe)\b", request_lower):
                return False

        # Check for "how to" questions about existing files - these are NOT coding requests
        if re.search(r"\bhow\b.*\b(run|execute|launch|start)\b.*\.(py|js|html|css|sh|exe)\b", request_lower):
            return False

        # Primary coding indicators
        coding_verbs = [
            "create", "build", "make", "develop", "generate", "implement",
            "write", "code", "program", "script", "automate"
        ]
        
        # Things that can be coded
        coding_targets = [
            "tool", "script", "application", "app", "program", "system",
            "automation", "bot", "function", "class", "module", "plugin",
            "website", "web", "browser", "gui", "interface", "api",
            "database", "scraper", "parser", "converter", "calculator",
            "game", "utility", "service", "component", "button", "form",
            "page", "site", "widget", "element", "dashboard", "chart"
        ]
        
        # Check for verb + target combinations
        for verb in coding_verbs:
            for target in coding_targets:
                # Pattern: "create a tool", "build web scraper", etc.
                pattern = rf"\b{verb}\b.*\b{target}\b"
                if re.search(pattern, request_lower):
                    return True
        
        # Direct coding requests
        direct_coding_patterns = [
            r"\bcode\b.*\bfor\b",  # "code for..."
            r"\bwrite\b.*\bcode\b",  # "write code"
            r"\bpython\b.*\bscript\b",  # "python script"
            r"\bjavascript\b.*\bfunction\b",  # "javascript function"
            r"\bhtml\b.*\bpage\b",  # "html page"
            r"\bmake.*appear",  # "make ... appear" (like browser windows)
            r"\bshow.*in.*browser\b",  # "show ... in browser"
            r"\bopen.*browser.*window\b",  # "open browser window"
        ]
        
        for pattern in direct_coding_patterns:
            if re.search(pattern, request_lower):
                return True
        
        # Technology-specific requests
        tech_patterns = [
            r"\bwith\s+(python|javascript|html|css|react|vue|node)\b",
            r"\busing\s+(selenium|playwright|requests|flask|django)\b",
            r"\b(api|database|sql|mongodb|postgresql)\b.*\b(integration|connection)\b"
        ]
        
        for pattern in tech_patterns:
            if re.search(pattern, request_lower):
                return True
        
        return False
    
    async def process_request(self, user_request: str, context: Context) -> Optional[OrchestrationResult]:
        """
        Process a request through the unified coding workflow if applicable.
        
        Args:
            user_request: User's natural language request
            context: Current conversation and system context
            
        Returns:
            OrchestrationResult if this was a coding request, None otherwise
        """
        if not self.enabled:
            return None
            
        if not self.is_coding_request(user_request):
            logger.debug(f"Request not identified as coding request: {user_request}")
            return None
        
        logger.info(f"🎯 Routing to coding workflow: {user_request}")

        try:
            # Ensure RAG workflow is initialized before use
        if not self._initialization_attempted:
            try:
                await self.initialize_rag_workflow()
                self._initialization_attempted = True
            except Exception as e:
                logger.warning(f"Failed to initialize RAG workflow: {e}")

        # Use RAG-powered workflow exclusively
            if not (self.use_rag_workflow and self.rag_workflow_builder):
                logger.error("RAG-powered workflow not available")
                return OrchestrationResult(
                    plan_id=f"rag_unavailable_{int(asyncio.get_event_loop().time())}",
                    success=False,
                    execution_time=0.0,
                    tools_executed=[],
                    results=["RAG-powered workflow system is not available"],
                    errors=["RAG workflow builder not initialized"]
                )

            logger.info("🧠 Using RAG-powered workflow")

            # Build workflow using RAG knowledge
            workflow_plan = await self.rag_workflow_builder.build_workflow(user_request)
            logger.info(f"📋 Workflow plan created: {workflow_plan.reasoning}")

            # Execute the workflow
            execution_results = await self.rag_workflow_builder.execute_workflow(workflow_plan)

            # Convert to OrchestrationResult format
            result = OrchestrationResult(
                plan_id=workflow_plan.workflow_id,
                success=execution_results["success"],
                execution_time=execution_results["duration"],
                tools_executed=[step["step"] for step in execution_results["results"]],
                results=[f"🎉 **RAG-Powered Workflow Complete!**\n\n**Request**: {user_request}\n\n**✅ Workflow Execution**:\n- Steps completed: {execution_results['steps_completed']}/{execution_results['total_steps']}\n- Duration: {execution_results['duration']:.1f}s\n- Success: {execution_results['success']}\n\n**The RAG-powered workflow has successfully delivered your solution!** 🚀"],
                errors=execution_results["errors"]
            )

            if result.success:
                logger.info(f"✅ RAG-powered workflow completed successfully")
            else:
                logger.error(f"❌ RAG-powered workflow failed: {result.errors}")

            return result
            
        except Exception as e:
            logger.error(f"Unified coding workflow error: {e}")
            
            # Return error result
            return OrchestrationResult(
                plan_id=f"unified_coding_error_{int(asyncio.get_event_loop().time())}",
                success=False,
                execution_time=0.0,
                tools_executed=[],
                results=[f"Coding workflow encountered an error: {str(e)}"],
                errors=[str(e)]
            )


# Global integration instance
unified_integration = UnifiedCodingIntegration()

# Initialize RAG workflow on module import
import asyncio
import threading

def _initialize_rag_workflow_sync():
    """Initialize RAG workflow in a thread-safe manner."""
    try:
        # Create new event loop for this thread if needed
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        # Run the initialization
        if not loop.is_running():
            loop.run_until_complete(unified_integration.initialize_rag_workflow())
        else:
            # If loop is already running, schedule the initialization
            asyncio.create_task(unified_integration.initialize_rag_workflow())

    except Exception as e:
        logger.warning(f"Failed to initialize RAG workflow on import: {e}")

# Initialize in a separate thread to avoid blocking import
initialization_thread = threading.Thread(target=_initialize_rag_workflow_sync, daemon=True)
initialization_thread.start()


def _extract_context_from_agent(agent, user_request: str) -> Context:
    """
    Extract proper context from the Jarvis agent.

    Args:
        agent: Jarvis agent instance
        user_request: User's request for additional context

    Returns:
        Context object with extracted information
    """
    import time
    import uuid

    # Generate unique session ID based on timestamp and request
    session_id = f"coding_session_{int(time.time())}_{str(uuid.uuid4())[:8]}"

    # Create context
    context = Context(session_id=session_id)

    # Extract conversation history if available
    if hasattr(agent, 'memory') and agent.memory:
        try:
            # Get recent conversation history
            chat_history = agent.memory.chat_memory.messages
            if chat_history:
                # Store recent messages for context
                recent_messages = []
                for msg in chat_history[-5:]:  # Last 5 messages
                    recent_messages.append({
                        'type': msg.__class__.__name__,
                        'content': str(msg.content)[:200]  # Truncate for context
                    })
                context.conversation_context['recent_conversation'] = recent_messages
        except Exception as e:
            logger.warning(f"Failed to extract conversation history: {e}")

    # Extract agent configuration if available
    if hasattr(agent, 'config'):
        try:
            context.system_context['agent_model'] = getattr(agent.config, 'model', 'unknown')
            context.system_context['agent_temperature'] = getattr(agent.config, 'temperature', 0.7)
        except Exception as e:
            logger.warning(f"Failed to extract agent config: {e}")

    # Store current request context
    context.conversation_context['current_request'] = user_request
    context.conversation_context['request_timestamp'] = time.time()
    context.conversation_context['request_type'] = 'coding_workflow'

    # Extract available tools if present
    if hasattr(agent, 'tools') and agent.tools:
        try:
            tool_names = [getattr(tool, 'name', str(tool)) for tool in agent.tools[:10]]  # First 10 tools
            context.tool_context['available_tools'] = tool_names
        except Exception as e:
            logger.warning(f"Failed to extract tool information: {e}")

    return context


async def process_with_unified_coding(user_request: str, agent) -> Optional[str]:
    """
    Process a request through the unified coding workflow.
    
    This function is designed to be called from the Jarvis agent's process_input method.
    
    Args:
        user_request: User's natural language request
        agent: Jarvis agent instance (for context)
        
    Returns:
        Response string if handled by unified coding workflow, None otherwise
    """
    try:
        # Create context from agent
        context = _extract_context_from_agent(agent, user_request)
        
        # Process through unified integration
        result = await unified_integration.process_request(user_request, context)
        
        if result is None:
            # Not a coding request
            return None
        
        if result.success and result.results:
            # Return the workflow result
            return result.results[0]
        else:
            # Return error message
            error_msg = "I encountered an issue with the coding workflow."
            if result.errors:
                error_msg += f" Error: {result.errors[0]}"
            return error_msg
            
    except Exception as e:
        logger.error(f"Unified coding processing error: {e}")
        return f"I encountered an error while processing your coding request: {str(e)}"


def should_use_unified_coding(user_request: str) -> bool:
    """
    Quick check if a request should use unified coding workflow.
    
    This is a lightweight version of the detection logic for use in routing decisions.
    """
    return unified_integration.is_coding_request(user_request)
