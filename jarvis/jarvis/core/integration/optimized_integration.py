"""
Optimized Integration Layer for Jarvis Voice Assistant

Carefully replaces post-wake-word processing with optimized controller
while preserving ALL wake word functionality completely.
"""

import time
import logging
import asyncio
from typing import Optional, Dict, Any

# Import optimized components
from ..optimized_controller import get_optimized_controller, QueryProcessingResult
from ..performance.performance_monitor import get_performance_monitor

logger = logging.getLogger(__name__)


class OptimizedJarvisIntegration:
    """
    Integration layer that replaces post-wake-word processing.
    
    CRITICAL: This class ONLY handles conversation processing AFTER
    wake word detection. It does NOT modify wake word functionality.
    """
    
    def __init__(self):
        """Initialize optimized integration."""
        self.controller = get_optimized_controller()
        self.performance_monitor = get_performance_monitor()
        
        # Use dedicated managers (separation of concerns)
        from ..memory.conversation_memory_manager import get_conversation_memory_manager
        from ..tools.tool_selection_manager import get_tool_selection_manager

        self.memory_manager = get_conversation_memory_manager()
        self.tool_selection_manager = get_tool_selection_manager()

        # Initialize tool selection manager with available tools
        self._initialize_tool_selection()

        # Performance tracking
        self.session_stats = {
            "queries_processed": 0,
            "total_response_time": 0.0,
            "performance_targets_met": 0,
            "instant_responses": 0
        }
        
        logger.info("OptimizedJarvisIntegration initialized - WAKE WORD FUNCTIONALITY PRESERVED")

    def _initialize_tool_selection(self) -> None:
        """Initialize tool selection manager with available tools."""
        try:
            from ...tools import plugin_manager
            all_tools = plugin_manager.get_all_tools()
            self.tool_selection_manager.initialize_tools(all_tools)
            logger.info(f"✅ Tool selection manager initialized with {len(all_tools)} tools")
        except Exception as e:
            logger.error(f"Failed to initialize tool selection manager: {e}")
    
    def start_conversation_session(self) -> None:
        """
        Start new conversation session (replaces agent.clear_chat_memory()).

        This is called AFTER wake word detection, preserving wake word flow.
        CRITICAL: Maintains same interface for wake word compatibility.
        """
        # Delegate memory management to dedicated manager
        self.memory_manager.start_conversation_session()

        # Reset performance tracking stats only
        self.session_stats = {
            "queries_processed": 0,
            "total_response_time": 0.0,
            "performance_targets_met": 0,
            "instant_responses": 0
        }

        logger.info("🚀 Optimized conversation session started")
    
    async def process_command(self, command: str) -> str:
        """
        Process user command with optimized controller.
        
        This replaces the agent.process_input() call in the original system.
        
        Args:
            command: User command to process
            
        Returns:
            Optimized response string
        """
        if not command or not command.strip():
            return "I didn't catch that. Could you please repeat?"
        
        start_time = time.time()
        
        try:
            # Process with optimized controller
            result = await self.controller.process_query(
                query=command,
                conversation_context=self.memory_manager.get_conversation_context(),
                user_preferences=None,  # Could be loaded from user settings
                persistent_agent=self.memory_manager.get_persistent_agent()
            )

            # Update conversation context through memory manager
            self.memory_manager.add_conversation_exchange(command, result.response)
            
            # Update session statistics
            self._update_session_stats(result)
            
            # Log performance
            processing_time = time.time() - start_time
            logger.info(f"Command processed in {processing_time*1000:.1f}ms "
                       f"(budget met: {result.performance_budget_met})")
            
            # Log optimization details
            if result.optimization_notes:
                logger.debug(f"Optimizations: {', '.join(result.optimization_notes)}")
            
            return result.response
            
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"Error processing command '{command}': {e}")
            
            # Return graceful error response
            return "I apologize, but I encountered an issue processing your request. Please try again."
    
    # _update_conversation_context removed - now handled by ConversationMemoryManager
    
    def _update_session_stats(self, result: QueryProcessingResult) -> None:
        """Update session statistics."""
        self.session_stats["queries_processed"] += 1
        self.session_stats["total_response_time"] += result.processing_time
        
        if result.performance_budget_met:
            self.session_stats["performance_targets_met"] += 1
        
        if "Instant response" in result.optimization_notes:
            self.session_stats["instant_responses"] += 1
    
    def end_conversation_session(self) -> Dict[str, Any]:
        """
        End conversation session and return performance summary.

        Returns:
            Combined session summary from memory manager and performance stats
        """
        # Get memory session stats
        memory_stats = self.memory_manager.end_conversation_session()
        session_duration = memory_stats.get("session_duration", 0.0)
        
        # Calculate session metrics
        avg_response_time = (self.session_stats["total_response_time"] / 
                           max(1, self.session_stats["queries_processed"]))
        
        performance_rate = (self.session_stats["performance_targets_met"] / 
                          max(1, self.session_stats["queries_processed"]))
        
        instant_rate = (self.session_stats["instant_responses"] / 
                       max(1, self.session_stats["queries_processed"]))
        
        # Combine memory stats with performance stats
        summary = {
            "session_duration": session_duration,
            "queries_processed": self.session_stats["queries_processed"],
            "avg_response_time_ms": avg_response_time * 1000,
            "performance_targets_met_rate": performance_rate,
            "instant_response_rate": instant_rate,
            "optimization_success": performance_rate > 0.8,  # 80% target compliance
            "exchanges_tracked": memory_stats.get("exchanges_tracked", 0),
            "context_length": memory_stats.get("context_length", 0)
        }
        
        logger.info(f"Conversation session ended: {self.session_stats['queries_processed']} queries, "
                   f"{avg_response_time*1000:.1f}ms avg response time")
        
        return summary
    
    def get_performance_status(self) -> Dict[str, Any]:
        """Get current performance status."""
        controller_summary = self.controller.get_performance_summary()
        monitor_summary = self.performance_monitor.get_performance_summary()
        
        return {
            "controller_performance": controller_summary,
            "system_performance": monitor_summary,
            "session_active": self.conversation_active,
            "session_stats": self.session_stats if self.conversation_active else None
        }


# Global integration instance
_integration_instance = None


def get_optimized_integration() -> OptimizedJarvisIntegration:
    """Get global optimized integration instance."""
    global _integration_instance
    if _integration_instance is None:
        _integration_instance = OptimizedJarvisIntegration()
    return _integration_instance


# Compatibility functions for easy integration
def replace_agent_processing(speech_manager, agent) -> OptimizedJarvisIntegration:
    """
    Replace agent processing with optimized system.
    
    This function provides a drop-in replacement for the existing
    agent-based processing while preserving all wake word functionality.
    
    Args:
        speech_manager: Existing speech manager (preserved)
        agent: Existing agent (will be replaced)
        
    Returns:
        OptimizedJarvisIntegration instance
    """
    integration = get_optimized_integration()
    
    logger.info("🔄 Replaced agent processing with optimized system")
    logger.info("✅ Wake word functionality completely preserved")
    logger.info("🚀 Performance optimizations active")
    
    return integration


async def optimized_conversation_loop(speech_manager, integration: OptimizedJarvisIntegration):
    """
    Optimized conversation loop that replaces the original conversation handling.
    
    This function replaces the conversation mode processing in start_jarvis.py
    while preserving ALL wake word detection functionality.
    
    Args:
        speech_manager: Speech manager for TTS and STT
        integration: Optimized integration instance
    """
    CONVERSATION_TIMEOUT = 30  # seconds
    last_interaction_time = time.time()
    
    # Start optimized conversation session
    integration.start_conversation_session()
    
    logger.info("🎤 Optimized conversation mode active")
    
    while integration.conversation_active:
        try:
            # Listen for command (preserves original speech handling)
            print("🎤 Listening for command...")
            
            command = speech_manager.microphone_manager.listen_for_speech(
                timeout=10.0,
                service="whisper"
            )
            
            if command:
                print(f"📥 Command: '{command}'")
                last_interaction_time = time.time()
                
                # Process with optimized controller
                print("🧠 Processing with optimized AI system...")
                response = await integration.process_command(command)
                
                print(f"🤖 Jarvis: {response}")
                speech_manager.speak_text(response)
                
            else:
                # Check for conversation timeout
                if time.time() - last_interaction_time > CONVERSATION_TIMEOUT:
                    print("⏰ Conversation timeout")
                    break
                    
        except KeyboardInterrupt:
            print("\n🛑 Conversation interrupted by user")
            break
        except Exception as e:
            logger.error(f"Error in optimized conversation loop: {e}")
            print(f"❌ Error: {e}")
            break
    
    # End conversation session
    session_summary = integration.end_conversation_session()
    
    print("✅ Optimized conversation session ended")
    print(f"📊 Session summary: {session_summary['queries_processed']} queries, "
          f"{session_summary['avg_response_time_ms']:.1f}ms avg response time")
    
    return session_summary


# Performance validation functions
def validate_performance_targets() -> Dict[str, bool]:
    """Validate that performance targets are being met."""
    integration = get_optimized_integration()
    performance_status = integration.get_performance_status()
    
    controller_perf = performance_status["controller_performance"]
    
    # Check key performance indicators
    validations = {
        "budget_compliance": controller_perf.get("budget_compliance_rate", 0) > 0.8,
        "cache_effectiveness": controller_perf.get("cache_hit_rate", 0) > 0.5,
        "instant_responses": controller_perf.get("instant_response_rate", 0) > 0.2,
        "avg_response_time": controller_perf.get("avg_processing_time_ms", 1000) < 2000
    }
    
    all_passed = all(validations.values())
    
    logger.info(f"Performance validation: {'✅ PASSED' if all_passed else '❌ FAILED'}")
    for metric, passed in validations.items():
        status = "✅" if passed else "❌"
        logger.info(f"  {status} {metric}")
    
    return validations


def emergency_rollback_check() -> bool:
    """
    Emergency check to ensure system is performing adequately.
    
    Returns:
        True if system should continue, False if rollback needed
    """
    try:
        validations = validate_performance_targets()
        
        # Critical thresholds for rollback
        critical_failures = [
            validations.get("budget_compliance", True) == False,
            validations.get("avg_response_time", True) == False
        ]
        
        if any(critical_failures):
            logger.critical("🚨 CRITICAL PERFORMANCE FAILURE - ROLLBACK RECOMMENDED")
            return False
        
        logger.info("✅ Performance check passed - system operating normally")
        return True
        
    except Exception as e:
        logger.critical(f"🚨 EMERGENCY CHECK FAILED: {e} - ROLLBACK RECOMMENDED")
        return False
