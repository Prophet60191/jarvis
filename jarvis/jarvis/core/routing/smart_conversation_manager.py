"""
Smart Conversation Manager with Fast/Slow Path Routing

Integrates the fast/slow path execution engine with the existing
conversation system, providing optimized query processing.
"""

import time
import asyncio
import logging
from typing import Optional, Dict, Any

from .execution_engine import ExecutionEngine, ExecutionResult, ExecutionPath
# We'll create a minimal base class since we can't import the full ConversationManager yet

logger = logging.getLogger(__name__)

class SmartConversationManager:
    """
    Enhanced conversation manager with intelligent routing.

    Implements fast/slow path optimization for query processing.
    """

    def __init__(self, config, speech_manager=None, agent=None, mcp_client=None):
        """Initialize the smart conversation manager."""
        # Handle both full config and conversation config
        if hasattr(config, 'conversation'):
            self.config = config
            self.conversation_config = config.conversation
        else:
            # Assume it's already the conversation config
            self.conversation_config = config
            self.config = None

        self.speech_manager = speech_manager
        self.agent = agent
        self.mcp_client = mcp_client

        # Initialize conversation state (matching original interface)
        self.conversation_active = False
        self.last_activity_time = 0
        self.retry_count = 0
        self.chat_history = []
        
        # Initialize the execution engine with agent access for tool-specific queries
        self.execution_engine = ExecutionEngine(config, self.agent)
        
        # Performance tracking
        self.total_queries = 0
        self.fast_path_usage = 0
        self.performance_improvements = []
        
        # Feature flags
        self.enable_fast_path = True
        self.enable_performance_logging = True
        self.fallback_to_original = True
        
        logger.info("SmartConversationManager initialized with fast/slow path routing")
    
    async def process_command(self, command: str, context: Optional[Dict] = None) -> str:
        """
        Process command using intelligent routing.
        
        Args:
            command: User command string
            context: Optional processing context
            
        Returns:
            str: Response string
        """
        start_time = time.time()
        self.total_queries += 1
        
        try:
            if self.enable_fast_path:
                # Use the new fast/slow path system
                result = await self._process_with_routing(command, context)
                
                # Track performance improvements
                if result.path_used == ExecutionPath.INSTANT:
                    self.fast_path_usage += 1
                    if self.enable_performance_logging:
                        self._log_performance_improvement(command, result)
                
                return result.response
            else:
                # Fall back to original system
                return await self._process_with_original_system(command, context)
                
        except Exception as e:
            logger.error(f"Smart conversation processing failed: {e}")
            
            if self.fallback_to_original:
                logger.info("Falling back to original conversation system")
                return await self._process_with_original_system(command, context)
            else:
                return "I'm sorry, I encountered an error processing your request."
    
    async def _process_with_routing(self, command: str, context: Optional[Dict]) -> ExecutionResult:
        """Process command using the routing system."""
        
        # Execute using the execution engine
        result = await self.execution_engine.execute_query(command, context)
        
        # If routing fails and we have fallback enabled, try original system
        if not result.success and self.fallback_to_original:
            logger.info(f"Routing failed for '{command}', falling back to original system")
            
            try:
                original_response = await self._process_with_original_system(command, context)
                
                # Create a result that indicates fallback was used
                result = ExecutionResult(
                    response=original_response,
                    execution_time=result.execution_time,
                    path_used=ExecutionPath.COMPLEX,
                    success=True,
                    metadata={"fallback_used": True}
                )
            except Exception as e:
                logger.error(f"Original system fallback also failed: {e}")
        
        return result
    
    async def _process_with_original_system(self, command: str, context: Optional[Dict]) -> str:
        """Process command using the original conversation system."""

        # Use the agent directly for original processing
        if self.agent:
            try:
                response = await self.agent.process_input(command)
                return response
            except Exception as e:
                logger.error(f"Original system processing failed: {e}")
                return f"I'm sorry, I encountered an error processing your request: {str(e)}"
        else:
            return "I'm sorry, the conversation system is not properly initialized."
    
    def _log_performance_improvement(self, command: str, result: ExecutionResult):
        """Log performance improvements from fast path usage."""
        
        # Estimate what the original system would have taken
        # Based on the 30-second timeout issue, assume original would take 5-30s
        estimated_original_time = 5.0  # Conservative estimate
        
        improvement = {
            "command": command[:50] + "..." if len(command) > 50 else command,
            "fast_path_time": result.execution_time,
            "estimated_original_time": estimated_original_time,
            "improvement_factor": estimated_original_time / result.execution_time,
            "time_saved": estimated_original_time - result.execution_time,
            "path_used": result.path_used.value
        }
        
        self.performance_improvements.append(improvement)
        
        # Keep only last 100 improvements
        if len(self.performance_improvements) > 100:
            self.performance_improvements = self.performance_improvements[-100:]
        
        logger.info(f"Performance improvement: {improvement['improvement_factor']:.1f}x faster "
                   f"({improvement['fast_path_time']:.3f}s vs ~{improvement['estimated_original_time']:.1f}s)")
    
    def get_routing_stats(self) -> Dict[str, Any]:
        """Get comprehensive routing and performance statistics."""
        
        # Get execution engine stats
        engine_stats = self.execution_engine.get_performance_stats()
        
        # Calculate usage percentages
        fast_path_percentage = (self.fast_path_usage / self.total_queries * 100) if self.total_queries > 0 else 0
        
        # Calculate average improvements
        if self.performance_improvements:
            avg_improvement_factor = sum(imp["improvement_factor"] for imp in self.performance_improvements) / len(self.performance_improvements)
            total_time_saved = sum(imp["time_saved"] for imp in self.performance_improvements)
        else:
            avg_improvement_factor = 0
            total_time_saved = 0
        
        return {
            "overview": {
                "total_queries": self.total_queries,
                "fast_path_usage": self.fast_path_usage,
                "fast_path_percentage": fast_path_percentage,
                "avg_improvement_factor": avg_improvement_factor,
                "total_time_saved_seconds": total_time_saved
            },
            "execution_paths": engine_stats,
            "recent_improvements": self.performance_improvements[-10:],  # Last 10
            "configuration": {
                "fast_path_enabled": self.enable_fast_path,
                "performance_logging_enabled": self.enable_performance_logging,
                "fallback_enabled": self.fallback_to_original
            }
        }
    
    def enable_fast_path_routing(self, enabled: bool = True):
        """Enable or disable fast path routing."""
        self.enable_fast_path = enabled
        logger.info(f"Fast path routing {'enabled' if enabled else 'disabled'}")
    
    def enable_performance_logging(self, enabled: bool = True):
        """Enable or disable performance logging."""
        self.enable_performance_logging = enabled
        logger.info(f"Performance logging {'enabled' if enabled else 'disabled'}")
    
    def enable_fallback(self, enabled: bool = True):
        """Enable or disable fallback to original system."""
        self.fallback_to_original = enabled
        logger.info(f"Original system fallback {'enabled' if enabled else 'disabled'}")
    
    def reset_stats(self):
        """Reset all performance statistics."""
        self.total_queries = 0
        self.fast_path_usage = 0
        self.performance_improvements = []
        
        # Reset execution engine stats
        for path in ExecutionPath:
            self.execution_engine.execution_stats[path] = {
                "count": 0, 
                "total_time": 0.0, 
                "timeouts": 0
            }
            self.execution_engine.intent_router.route_stats[path] = {
                "count": 0, 
                "total_time": 0.0
            }
        
        logger.info("Performance statistics reset")
    
    async def test_routing_performance(self) -> Dict[str, Any]:
        """Test routing performance with sample queries."""
        
        test_queries = [
            "What time is it?",
            "Hello",
            "How are you?",
            "What's the weather?",
            "Play some music",
            "What is artificial intelligence?",
            "Search for information about Python",
            "Analyze my files and create a report",
            "Create a complex automation script"
        ]
        
        results = []
        
        for query in test_queries:
            start_time = time.time()
            
            try:
                result = await self.execution_engine.execute_query(query)
                
                test_result = {
                    "query": query,
                    "path_used": result.path_used.value,
                    "execution_time_ms": result.execution_time * 1000,
                    "success": result.success,
                    "response_preview": result.response[:100] + "..." if len(result.response) > 100 else result.response
                }
                
                results.append(test_result)
                
            except Exception as e:
                results.append({
                    "query": query,
                    "path_used": "error",
                    "execution_time_ms": (time.time() - start_time) * 1000,
                    "success": False,
                    "error": str(e)
                })
        
        return {
            "test_results": results,
            "summary": {
                "total_tests": len(test_queries),
                "successful_tests": sum(1 for r in results if r["success"]),
                "avg_execution_time_ms": sum(r["execution_time_ms"] for r in results if r["success"]) / len([r for r in results if r["success"]]) if any(r["success"] for r in results) else 0,
                "path_distribution": {
                    path.value: sum(1 for r in results if r.get("path_used") == path.value)
                    for path in ExecutionPath
                }
            }
        }

    # Interface methods expected by the main application
    def is_initialized(self) -> bool:
        """Check if the conversation manager is initialized."""
        return self.execution_engine is not None

    def enter_conversation_mode(self):
        """Enter conversation mode (compatibility method)."""
        self.conversation_active = True
        self.last_activity_time = time.time()
        self.retry_count = 0
        logger.info("Entered conversation mode with smart routing")

    def handle_conversation_cycle(self) -> bool:
        """Handle one conversation cycle (compatibility method)."""
        try:
            # This would integrate with the speech system
            # For now, return False to end conversation
            return False
        except Exception as e:
            logger.error(f"Error in conversation cycle: {e}")
            return False

    def reset_conversation(self):
        """Reset conversation state (compatibility method)."""
        self.conversation_active = False
        self.last_activity_time = 0
        self.retry_count = 0
        logger.info("Conversation reset")

    def get_conversation_state(self) -> Dict[str, Any]:
        """Get current conversation state (compatibility method)."""
        return {
            "active": self.conversation_active,
            "last_activity": self.last_activity_time,
            "retry_count": self.retry_count,
            "routing_enabled": self.enable_fast_path,
            "performance_stats": self.get_routing_stats()
        }
