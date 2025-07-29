"""
Execution Engine for Fast/Slow Path Processing

Handles execution of queries based on routing decisions,
implementing different processing strategies for different complexity levels.
"""

import time
import asyncio
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass

from .intent_router import IntentRouter, ExecutionPath, RouteResult

logger = logging.getLogger(__name__)

@dataclass
class ExecutionResult:
    """Result of query execution."""
    response: str
    execution_time: float
    path_used: ExecutionPath
    success: bool
    metadata: Dict[str, Any] = None

class ExecutionEngine:
    """
    Multi-path execution engine that processes queries based on complexity.
    
    Implements the fast/slow path pattern:
    - INSTANT: Direct function calls, <200ms target
    - ADAPTIVE: Lightweight LLM processing, <2s target  
    - COMPLEX: Full orchestration, <30s timeout
    """
    
    def __init__(self, config=None, agent=None):
        """Initialize the execution engine."""
        self.config = config
        self.agent = agent  # Store agent reference for tool-specific queries
        self.intent_router = IntentRouter()
        
        # Performance targets (in seconds)
        self.performance_targets = {
            ExecutionPath.INSTANT: 0.2,    # 200ms
            ExecutionPath.ADAPTIVE: 2.0,   # 2 seconds
            ExecutionPath.COMPLEX: 30.0    # 30 seconds
        }
        
        # Execution statistics
        self.execution_stats = {
            ExecutionPath.INSTANT: {"count": 0, "total_time": 0.0, "timeouts": 0},
            ExecutionPath.ADAPTIVE: {"count": 0, "total_time": 0.0, "timeouts": 0},
            ExecutionPath.COMPLEX: {"count": 0, "total_time": 0.0, "timeouts": 0}
        }
        
        logger.info("ExecutionEngine initialized with fast/slow path processing")
    
    async def execute_query(self, query: str, context: Optional[Dict] = None) -> ExecutionResult:
        """
        Execute query using appropriate path based on complexity.
        
        Args:
            query: User query string
            context: Optional execution context
            
        Returns:
            ExecutionResult: Execution result with response and metadata
        """
        start_time = time.time()
        
        try:
            # Step 1: Route the query
            route_result = self.intent_router.route_query(query)
            
            # Step 2: Execute based on path
            if route_result.path == ExecutionPath.INSTANT:
                result = await self._execute_instant_path(query, route_result, context)
            elif route_result.path == ExecutionPath.ADAPTIVE:
                result = await self._execute_adaptive_path(query, route_result, context)
            else:  # COMPLEX
                result = await self._execute_complex_path(query, route_result, context)
            
            # Step 3: Update statistics
            execution_time = time.time() - start_time
            self._update_execution_stats(route_result.path, execution_time, result.success)
            
            # Step 4: Check performance targets
            target_time = self.performance_targets[route_result.path]
            if execution_time > target_time:
                logger.warning(f"Execution exceeded target: {execution_time:.2f}s > {target_time}s for {route_result.path.value}")
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Query execution failed: {e}")
            
            return ExecutionResult(
                response=f"I'm sorry, I encountered an error processing your request: {str(e)}",
                execution_time=execution_time,
                path_used=ExecutionPath.COMPLEX,  # Default for errors
                success=False,
                metadata={"error": str(e)}
            )
    
    async def _execute_instant_path(self, query: str, route_result: RouteResult, context: Optional[Dict]) -> ExecutionResult:
        """
        Execute instant path - direct function calls, no LLM.
        Target: <200ms
        """
        start_time = time.time()
        
        try:
            # Use the handler from routing if available
            if route_result.handler:
                response = route_result.handler(query)
            else:
                # Fallback for instant patterns without handlers
                response = self._get_instant_fallback_response(route_result.intent)
            
            execution_time = time.time() - start_time
            
            return ExecutionResult(
                response=response,
                execution_time=execution_time,
                path_used=ExecutionPath.INSTANT,
                success=True,
                metadata={
                    "intent": route_result.intent,
                    "confidence": route_result.confidence,
                    "handler_used": route_result.handler is not None
                }
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Instant path execution failed: {e}")
            
            return ExecutionResult(
                response="I'm sorry, I had trouble with that request.",
                execution_time=execution_time,
                path_used=ExecutionPath.INSTANT,
                success=False,
                metadata={"error": str(e)}
            )
    
    async def _execute_adaptive_path(self, query: str, route_result: RouteResult, context: Optional[Dict]) -> ExecutionResult:
        """
        Execute adaptive path - lightweight LLM processing.
        Target: <2s
        """
        start_time = time.time()
        
        try:
            # For now, use a simple LLM call without full orchestration
            # This would be replaced with lightweight LLM processing
            
            # Simulate adaptive processing
            await asyncio.sleep(0.1)  # Simulate lightweight processing
            
            response = await self._get_adaptive_response(query, route_result.intent)
            execution_time = time.time() - start_time
            
            return ExecutionResult(
                response=response,
                execution_time=execution_time,
                path_used=ExecutionPath.ADAPTIVE,
                success=True,
                metadata={
                    "intent": route_result.intent,
                    "confidence": route_result.confidence,
                    "processing_type": "lightweight_llm"
                }
            )
            
        except asyncio.TimeoutError:
            execution_time = time.time() - start_time
            logger.warning(f"Adaptive path timeout: {execution_time:.2f}s")
            
            return ExecutionResult(
                response="That's taking longer than expected. Let me try a different approach.",
                execution_time=execution_time,
                path_used=ExecutionPath.ADAPTIVE,
                success=False,
                metadata={"timeout": True}
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Adaptive path execution failed: {e}")
            
            return ExecutionResult(
                response="I'm having trouble processing that request right now.",
                execution_time=execution_time,
                path_used=ExecutionPath.ADAPTIVE,
                success=False,
                metadata={"error": str(e)}
            )
    
    async def _execute_complex_path(self, query: str, route_result: RouteResult, context: Optional[Dict]) -> ExecutionResult:
        """
        Execute complex path - full orchestration and LLM processing.
        Target: <30s
        """
        start_time = time.time()
        
        try:
            # This would integrate with the existing complex agent system
            # For now, we'll create a placeholder that calls the existing agent
            
            response = await self._get_complex_response(query, route_result.intent, context)
            execution_time = time.time() - start_time
            
            return ExecutionResult(
                response=response,
                execution_time=execution_time,
                path_used=ExecutionPath.COMPLEX,
                success=True,
                metadata={
                    "intent": route_result.intent,
                    "confidence": route_result.confidence,
                    "processing_type": "full_orchestration"
                }
            )
            
        except asyncio.TimeoutError:
            execution_time = time.time() - start_time
            logger.warning(f"Complex path timeout: {execution_time:.2f}s")
            
            return ExecutionResult(
                response="I'm sorry, that request took too long to process. Please try again or rephrase your request.",
                execution_time=execution_time,
                path_used=ExecutionPath.COMPLEX,
                success=False,
                metadata={"timeout": True}
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Complex path execution failed: {e}")
            
            return ExecutionResult(
                response="I encountered an error processing that complex request.",
                execution_time=execution_time,
                path_used=ExecutionPath.COMPLEX,
                success=False,
                metadata={"error": str(e)}
            )
    
    def _get_instant_fallback_response(self, intent: str) -> str:
        """Get fallback response for instant intents without handlers."""
        fallback_responses = {
            "time_query": "Let me check the time for you.",
            "weather_query": "Let me get the weather information.",
            "music_control": "I'll help you with music.",
            "greeting": "Hello! How can I help you?",
            "status_check": "I'm working well and ready to help!"
        }
        return fallback_responses.get(intent, "I can help you with that.")
    
    async def _get_adaptive_response(self, query: str, intent: str) -> str:
        """Get response using focused tool selection for maximum efficiency."""

        # CRITICAL FIX: Use focused tool subsets instead of all 34 tools
        tool_specific_intents = ["profile_operations", "memory_operations", "system_operations", "tool_status"]

        if intent in tool_specific_intents:
            # Use focused tool selection with only relevant tools
            try:
                if hasattr(self, 'agent') and self.agent:
                    logger.info(f"🔧 Using focused tool selection for intent: {intent}")
                    response = await self._process_with_focused_tools(query, intent)
                    return response
                else:
                    logger.warning("Agent not available for tool-specific query")
                    return f"I'll help you with that: {query}"
            except Exception as e:
                logger.error(f"Focused tool processing failed for {intent}: {e}")
                return f"I'll do my best to help you with that."

        # For simple questions, use lightweight responses
        adaptive_responses = {
            "simple_question": f"Let me answer that question for you: {query}",
            "reminder": "I'll help you set up that reminder.",
            "search": f"I'll search for information about: {query}",
            "unknown_query": "I'll do my best to help you with that."
        }

        return adaptive_responses.get(intent, "Let me process that for you.")

    async def _process_with_focused_tools(self, query: str, intent: str) -> str:
        """Process query using only relevant tools for the specific intent."""

        # Define focused tool subsets (3-5 tools per category instead of 34)
        focused_tool_sets = {
            "profile_operations": [
                "get_my_name", "set_my_name", "set_my_pronouns",
                "show_my_profile", "clear_my_profile"
            ],
            "memory_operations": [
                "remember_fact", "search_long_term_memory", "search_conversations",
                "search_documents", "search_all_memory"
            ],
            "system_operations": [
                "show_jarvis_status", "open_logs_terminal", "show_logs_status",
                "open_rag_manager", "show_rag_status"
            ],
            "tool_status": [
                "check_aider_status", "check_lavague_status", "validate_test_system",
                "list_available_tests"
            ]
        }

        relevant_tools = focused_tool_sets.get(intent, [])

        if not relevant_tools:
            logger.warning(f"No focused tools defined for intent: {intent}")
            return f"I'll help you with that: {query}"

        logger.info(f"🎯 Using {len(relevant_tools)} focused tools for {intent}: {relevant_tools}")

        # Create a focused agent with only relevant tools
        try:
            # CRITICAL OPTIMIZATION: Create temporary agent with only relevant tools
            focused_response = await self._create_focused_agent_response(query, relevant_tools)
            return focused_response
        except Exception as e:
            logger.error(f"Focused tool processing failed: {e}")
            return f"I encountered an issue processing your request: {str(e)}"

    async def _create_focused_agent_response(self, query: str, relevant_tools: list) -> str:
        """Create a temporary agent with only the relevant tools for faster processing."""

        try:
            # CRITICAL FIX: Access tools through the plugin manager
            from jarvis.tools import get_plugin_manager

            # Get the plugin manager that contains all loaded tools
            plugin_manager = get_plugin_manager()
            if not plugin_manager:
                logger.warning("Plugin manager not available, using full agent")
                response = await self.agent.process_input(query)
                return response

            # Get all available tools from plugin manager
            all_tools = plugin_manager.get_all_tools()

            # Create focused tool list with only relevant tools
            focused_tools = []
            for tool_name in relevant_tools:
                # Find the tool by name in the list of all tools
                for tool in all_tools:
                    if hasattr(tool, 'name') and tool.name == tool_name:
                        focused_tools.append(tool)
                        break
                else:
                    logger.warning(f"Tool {tool_name} not found in plugin manager")

            if not focused_tools:
                logger.warning("No focused tools found, using full agent")
                response = await self.agent.process_input(query)
                return response

            logger.info(f"🚀 Using {len(focused_tools)} focused tools instead of {len(all_tools)}: {[t.name for t in focused_tools]}")

            # OPTIMIZATION: Use existing agent architecture with focused tools for maximum compatibility
            logger.info(f"🚀 Creating focused agent with existing architecture for maximum compatibility")

            # The agent creates fresh executors using self.tools, so we need to temporarily replace that
            original_tools = None
            try:
                # Get the original agent's tools (this is what gets used in fresh executor creation)
                if hasattr(self.agent, 'tools'):
                    original_tools = self.agent.tools

                    # Temporarily replace the agent's tools with focused tools
                    self.agent.tools = focused_tools
                    logger.info(f"🎯 Temporarily replaced agent tools: {len(focused_tools)} focused tools instead of {len(original_tools)}")

                    # Process with focused tools - the agent will create a fresh executor with focused tools
                    response = await self.agent.process_input(query)

                    logger.info(f"✅ Focused processing completed successfully")
                    return response
                else:
                    # Fallback: use the agent's existing process_input method
                    logger.info(f"🔄 Using agent's existing process_input with focused tool awareness")
                    response = await self.agent.process_input(query)
                    return response

            finally:
                # Always restore original tools
                if original_tools is not None and hasattr(self.agent, 'tools'):
                    self.agent.tools = original_tools
                    logger.info(f"🔄 Restored original {len(original_tools)} tools to agent")

        except Exception as e:
            logger.error(f"Failed to create focused agent: {e}")
            # Fallback to original agent
            response = await self.agent.process_input(query)
            return response
    
    async def _get_complex_response(self, query: str, intent: str, context: Optional[Dict]) -> str:
        """Get response using full orchestration with the complete agent system."""
        logger.info(f"🔄 Processing complex query with full agent: '{query}'")

        try:
            # Use the full agent system for complex queries
            response = await self.agent.process_input(query)
            logger.info(f"✅ Complex query processed successfully")
            return response

        except Exception as e:
            logger.error(f"❌ Complex query processing failed: {e}")
            return f"I encountered an error processing your complex request: {str(e)}"
    
    def _update_execution_stats(self, path: ExecutionPath, execution_time: float, success: bool):
        """Update execution statistics."""
        stats = self.execution_stats[path]
        stats["count"] += 1
        stats["total_time"] += execution_time
        
        if not success and execution_time > self.performance_targets[path]:
            stats["timeouts"] += 1
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get execution performance statistics."""
        stats = {}
        
        for path, data in self.execution_stats.items():
            if data["count"] > 0:
                avg_time = data["total_time"] / data["count"]
                target_time = self.performance_targets[path]
                
                stats[path.value] = {
                    "count": data["count"],
                    "avg_execution_time_ms": avg_time * 1000,
                    "target_time_ms": target_time * 1000,
                    "performance_ratio": avg_time / target_time,
                    "timeout_rate": data["timeouts"] / data["count"] if data["count"] > 0 else 0
                }
        
        # Add routing stats
        stats["routing"] = self.intent_router.get_performance_stats()
        
        return stats
