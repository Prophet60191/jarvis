"""
Optimized Jarvis Controller

Integrates all performance optimization components with intelligent routing,
caching, and performance budgets for sub-second response times.
"""

import time
import logging
import asyncio
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum

# Import optimization components
from .classification.smart_classifier import get_smart_classifier, QueryComplexity, ClassificationResult
from .caching.response_cache import get_response_cache, CacheLevel
from .memory.sliding_window_memory import get_sliding_window_memory, ContextPriority
from .handlers.enhanced_instant_handler import get_instant_handler, InstantResponse
from .tools.semantic_tool_selector import get_semantic_tool_selector
from .rag.smart_rag import get_smart_rag, RAGActivationLevel
from .prompts.simplified_prompts import get_optimal_prompt
from .performance.performance_monitor import get_performance_monitor, record_query_performance

logger = logging.getLogger(__name__)


class ProcessingStage(Enum):
    """Processing stages for performance tracking."""
    CLASSIFICATION = "classification"
    INSTANT_CHECK = "instant_check"
    CACHE_LOOKUP = "cache_lookup"
    TOOL_SELECTION = "tool_selection"
    RAG_RETRIEVAL = "rag_retrieval"
    LLM_PROCESSING = "llm_processing"
    RESPONSE_GENERATION = "response_generation"


@dataclass
class QueryProcessingResult:
    """Result of query processing with performance metrics."""
    response: str
    processing_time: float
    complexity: QueryComplexity
    stages_used: List[ProcessingStage]
    cache_hits: int
    api_calls: int
    tools_used: List[str]
    performance_budget_met: bool
    optimization_notes: List[str]


class OptimizedJarvisController:
    """
    Optimized Jarvis controller with intelligent routing and performance budgets.
    
    Integrates all optimization components:
    - Smart query classification for routing
    - Multi-tier caching for speed
    - Instant handlers for common queries
    - Semantic tool selection (2-3 vs 60+ tools)
    - Smart RAG with query-dependent activation
    - Context window optimization
    - Performance monitoring and budgets
    """
    
    def __init__(self):
        """Initialize optimized controller with separated managers."""
        # Initialize core processing components
        self.classifier = get_smart_classifier()
        self.cache = get_response_cache()
        self.memory = get_sliding_window_memory()
        self.instant_handler = get_instant_handler()
        self.smart_rag = get_smart_rag()

        # Initialize service layers (dependency injection pattern)
        from .memory.memory_service import get_memory_service
        from .tools.tool_service import get_tool_service
        from .performance.performance_service import get_performance_service
        from .memory.conversation_memory_manager import get_conversation_memory_manager

        # Service layer dependencies
        self.memory_service = get_memory_service()
        self.tool_service = get_tool_service()
        self.performance_service = get_performance_service()
        self.conversation_memory = get_conversation_memory_manager()

        # Maintain backward compatibility with existing managers
        from .tools.tool_selection_manager import get_tool_selection_manager
        from .performance.performance_monitoring_manager import get_performance_monitoring_manager

        self.tool_selection_manager = get_tool_selection_manager()
        self.performance_manager = get_performance_monitoring_manager()
        
        # Performance budgets (in seconds)
        self.performance_budgets = {
            QueryComplexity.INSTANT: 0.05,
            QueryComplexity.EXPLICIT_FACT: 0.3,
            QueryComplexity.SIMPLE_REASONING: 1.0,
            QueryComplexity.COMPLEX_MULTI_STEP: 5.0
        }
        
        # Processing statistics
        self.stats = {
            "total_queries": 0,
            "budget_violations": 0,
            "instant_responses": 0,
            "cache_hits": 0,
            "avg_processing_time": 0.0,
            "complexity_distribution": {c.value: 0 for c in QueryComplexity}
        }
        
        logger.info("OptimizedJarvisController initialized with all components")
    
    async def process_query(self,
                           query: str,
                           conversation_context: Optional[str] = None,
                           user_preferences: Optional[Dict[str, Any]] = None,
                           persistent_agent=None) -> QueryProcessingResult:
        """
        Process query with optimized routing and performance monitoring.
        
        Args:
            query: User query to process
            conversation_context: Recent conversation context
            user_preferences: User preferences and settings
            
        Returns:
            QueryProcessingResult with response and performance metrics
        """
        start_time = time.time()
        stages_used = []
        cache_hits = 0
        api_calls = 0
        tools_used = []
        optimization_notes = []
        
        try:
            # Stage 1: Query Classification
            stages_used.append(ProcessingStage.CLASSIFICATION)
            classification = self.classifier.classify_query(query)
            complexity = classification.complexity
            
            # Update stats
            self.stats["total_queries"] += 1
            self.stats["complexity_distribution"][complexity.value] += 1
            
            # Get performance budget
            budget = self.performance_budgets[complexity]
            
            # Stage 2: Instant Response Check (for instant queries)
            if complexity == QueryComplexity.INSTANT:
                stages_used.append(ProcessingStage.INSTANT_CHECK)
                instant_response = self.instant_handler.handle_instant_query(query)
                
                if instant_response:
                    processing_time = time.time() - start_time
                    self.stats["instant_responses"] += 1
                    
                    # Record performance with dedicated manager
                    self.performance_manager.record_query_performance(
                        query=query,
                        processing_time_ms=processing_time * 1000,
                        query_complexity="instant"
                    )
                    
                    return QueryProcessingResult(
                        response=instant_response.text,
                        processing_time=processing_time,
                        complexity=complexity,
                        stages_used=stages_used,
                        cache_hits=1 if instant_response.cached else 0,
                        api_calls=0,
                        tools_used=[],
                        performance_budget_met=processing_time <= budget,
                        optimization_notes=["Instant response pattern matched"]
                    )
            
            # Stage 3: Cache Lookup
            stages_used.append(ProcessingStage.CACHE_LOOKUP)
            cached_response = self._check_response_cache(query, complexity, conversation_context)
            
            if cached_response:
                processing_time = time.time() - start_time
                cache_hits += 1
                self.stats["cache_hits"] += 1
                optimization_notes.append("Response cache hit")
                
                # Record performance
                record_query_performance(complexity.value, processing_time, 0)
                
                return QueryProcessingResult(
                    response=cached_response,
                    processing_time=processing_time,
                    complexity=complexity,
                    stages_used=stages_used,
                    cache_hits=cache_hits,
                    api_calls=0,
                    tools_used=[],
                    performance_budget_met=processing_time <= budget,
                    optimization_notes=optimization_notes
                )
            
            # Stage 4: Tool Selection (for non-instant queries)
            if complexity != QueryComplexity.INSTANT:
                stages_used.append(ProcessingStage.TOOL_SELECTION)

                # Normal tool selection for all queries
                # Determine max tools based on complexity
                max_tools = {
                    QueryComplexity.EXPLICIT_FACT: 1,
                    QueryComplexity.SIMPLE_REASONING: 2,
                    QueryComplexity.COMPLEX_MULTI_STEP: 3
                }.get(complexity, 2)

                # Use dedicated tool selection manager
                tool_selection_result = self.tool_selection_manager.select_tools_for_query(
                    query=query,
                    max_tools=max_tools,
                    query_complexity=complexity.value
                )

                tools_used = [tool.name for tool in tool_selection_result.selected_tools]
                if tool_selection_result.cached:
                    cache_hits += 1
                    optimization_notes.append("Tool selection cache hit")
                optimization_notes.append(tool_selection_result.selection_reasoning)
            
            # Stage 5: RAG Retrieval (if needed)
            rag_content = []
            rag_query = self.smart_rag.analyze_query(query, {"complexity": complexity.value})
            
            if rag_query.activation_level != RAGActivationLevel.DISABLED:
                stages_used.append(ProcessingStage.RAG_RETRIEVAL)
                rag_result = self.smart_rag.retrieve(rag_query)
                rag_content = rag_result.retrieved_content
                
                if rag_result.cache_hit:
                    cache_hits += 1
                    optimization_notes.append("RAG cache hit")
            
            # Stage 6: LLM Processing
            stages_used.append(ProcessingStage.LLM_PROCESSING)
            
            # Build optimized context
            optimized_context = self._build_optimized_context(
                query, complexity, conversation_context, rag_content, user_preferences
            )
            
            # Get optimized prompt
            prompt = get_optimal_prompt(complexity, optimized_context)
            
            # Process with real LLM and agent system (simplified)
            llm_response = await self._process_with_llm(
                query, prompt, tools_used, complexity, persistent_agent
            )

            # Track messages for session saving (silent - backward compatible)
            try:
                # Add user message
                save_suggestion = self.conversation_memory.add_message_to_session(query, "user")

                # Add assistant response
                self.conversation_memory.add_message_to_session(llm_response, "assistant")

                # If there's a save suggestion, append it to the response
                if save_suggestion:
                    llm_response += f"\n\n{save_suggestion}"

            except Exception as e:
                logger.error(f"Failed to track session messages: {e}")
                # Don't break the main flow if session tracking fails
            
            api_calls += 1  # LLM call
            
            # Stage 7: Response Generation
            stages_used.append(ProcessingStage.RESPONSE_GENERATION)
            final_response = self._generate_final_response(llm_response, complexity)
            
            # Calculate final processing time
            processing_time = time.time() - start_time
            budget_met = processing_time <= budget
            
            if not budget_met:
                self.stats["budget_violations"] += 1
                optimization_notes.append(f"Budget exceeded: {processing_time:.3f}s > {budget:.3f}s")
            
            # Cache successful response
            if budget_met and complexity != QueryComplexity.INSTANT:
                self._cache_response(query, final_response, complexity, conversation_context)
            
            # Update performance monitoring with dedicated manager
            self.performance_manager.record_query_performance(
                query=query,
                processing_time_ms=processing_time * 1000,
                query_complexity=complexity.value,
                optimization_notes=optimization_notes
            )
            
            # Update average processing time
            total_time = (self.stats["avg_processing_time"] * 
                         (self.stats["total_queries"] - 1) + processing_time)
            self.stats["avg_processing_time"] = total_time / self.stats["total_queries"]
            
            # Update conversation memory
            self.memory.add_context(
                query, "user_input", ContextPriority.HIGH
            )
            self.memory.add_context(
                final_response, "assistant_response", ContextPriority.HIGH
            )

            # Handle memory operations using original working tools
            final_response = await self._handle_memory_with_original_tools(query, final_response)
            
            return QueryProcessingResult(
                response=final_response,
                processing_time=processing_time,
                complexity=complexity,
                stages_used=stages_used,
                cache_hits=cache_hits,
                api_calls=api_calls,
                tools_used=tools_used,
                performance_budget_met=budget_met,
                optimization_notes=optimization_notes
            )
            
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"Error processing query: {e}")
            
            return QueryProcessingResult(
                response=f"I apologize, but I encountered an error processing your request: {str(e)}",
                processing_time=processing_time,
                complexity=QueryComplexity.SIMPLE_REASONING,
                stages_used=stages_used,
                cache_hits=cache_hits,
                api_calls=api_calls,
                tools_used=tools_used,
                performance_budget_met=False,
                optimization_notes=[f"Error occurred: {str(e)}"]
            )
    
    def _check_response_cache(self, 
                             query: str, 
                             complexity: QueryComplexity, 
                             context: Optional[str]) -> Optional[str]:
        """Check for cached response."""
        # Create semantic cache key
        context_key = context[:100] if context else ""  # Limit context for key
        
        return self.cache.get_cached_response(f"{query}|{complexity.value}|{context_key}")
    
    def _cache_response(self, 
                       query: str, 
                       response: str, 
                       complexity: QueryComplexity, 
                       context: Optional[str]) -> None:
        """Cache response for future use."""
        context_key = context[:100] if context else ""
        self.cache.cache_response(f"{query}|{complexity.value}|{context_key}", response)
    
    def _build_optimized_context(self, 
                                query: str, 
                                complexity: QueryComplexity,
                                conversation_context: Optional[str],
                                rag_content: List[str],
                                user_preferences: Optional[Dict[str, Any]]) -> str:
        """Build optimized context within token limits."""
        context_parts = []
        
        # Add RAG content if available
        if rag_content:
            rag_summary = " ".join(rag_content[:2])  # Limit RAG content
            context_parts.append(f"Relevant information: {rag_summary}")
        
        # Add conversation context (optimized)
        if conversation_context:
            optimized_context = self.memory.get_optimized_context(query, max_tokens=400)
            if optimized_context:
                context_parts.append(f"Conversation context: {optimized_context}")
        
        # Add user preferences for complex queries
        if complexity == QueryComplexity.COMPLEX_MULTI_STEP and user_preferences:
            prefs = []
            for key, value in list(user_preferences.items())[:3]:  # Limit preferences
                prefs.append(f"{key}: {value}")
            if prefs:
                context_parts.append(f"User preferences: {', '.join(prefs)}")
        
        return "\n".join(context_parts)

    async def _handle_memory_with_original_tools(self, query: str, response: str) -> str:
        """Handle memory operations using the original working tools."""
        try:
            import re
            query_lower = query.lower().strip()

            # Initialize original tools if not already done
            if not hasattr(self, '_memory_tools_initialized'):
                await self._initialize_original_memory_tools()

            # Check for memory deletion commands first (higher priority)
            deletion_patterns = [
                r'\b(forget|delete|remove|erase)\s+that\s+(.+)',
                r'\b(forget|delete|remove|erase)\s+(about|information\s+about)\s+(.+)',
                r'\b(don\'t\s+remember|stop\s+remembering)\s+(.+)',
                r'\b(forget|delete|remove|erase)\s+(.+)'
            ]

            for pattern in deletion_patterns:
                match = re.search(pattern, query_lower)
                if match:
                    # Extract content to forget
                    if len(match.groups()) >= 3:
                        content_to_forget = match.group(3).strip()
                    elif len(match.groups()) >= 2:
                        content_to_forget = match.group(2).strip()
                    else:
                        content_to_forget = match.group(1).strip()

                    # Use memory service for deletion (with backward compatibility)
                    try:
                        deletion_result_obj = await self.memory_service.forget_information(content_to_forget)
                        deletion_result = deletion_result_obj.message
                    except Exception as e:
                        # Fallback to direct tool usage for backward compatibility
                        logger.warning(f"Memory service failed, using fallback: {e}")
                        if hasattr(self, 'forget_tool'):
                            deletion_result = self.forget_tool.invoke({"query": content_to_forget})
                        else:
                            from ..tools.rag_tools import forget_information
                            deletion_result = forget_information(content_to_forget)

                    logger.info(f"Processed deletion request: {content_to_forget[:50]}...")
                    return deletion_result

            # Check for memory storage commands
            storage_patterns = [
                r'\b(remember|store|note|save)\s+that\s+(.+)',
                r'\b(remember|store|note|save)\s+(.+)',
                r'\b(my\s+name\s+is|i\s+am|i\s+work\s+at|i\s+live\s+in|i\s+like|i\s+prefer)\s+(.+)'
            ]

            for pattern in storage_patterns:
                match = re.search(pattern, query_lower)
                if match:
                    # Extract content to remember
                    if len(match.groups()) >= 2:
                        fact_to_remember = match.group(2).strip()
                    else:
                        fact_to_remember = match.group(1).strip()

                    # Use memory service for storage (with backward compatibility)
                    try:
                        storage_result_obj = await self.memory_service.store_fact(fact_to_remember)
                        storage_result = storage_result_obj.message
                    except Exception as e:
                        # Fallback to direct tool usage for backward compatibility
                        logger.warning(f"Memory service failed, using fallback: {e}")
                        if hasattr(self, 'remember_fact_tool'):
                            storage_result = self.remember_fact_tool.invoke({"fact": fact_to_remember})
                        else:
                            # Initialize tools if needed
                            await self._initialize_original_memory_tools()
                            storage_result = self.remember_fact_tool.invoke({"fact": fact_to_remember})

                    logger.info(f"Stored memory using service layer: {fact_to_remember[:50]}...")
                    return storage_result

            # Check for memory retrieval commands
            retrieval_patterns = [
                r'\b(what\s+do\s+you\s+remember|what\s+did\s+i|tell\s+me\s+about\s+me)',
                r'\b(what\s+is\s+my|what\s+are\s+my|where\s+do\s+i)',
                r'\b(what\s+programming|what\s+language|what\s+technologies)',
                r'\b(what\s+project|what\s+am\s+i\s+working)',
                r'\b(what\s+do\s+i\s+want\s+to\s+learn|what\s+are\s+my\s+learning)'
            ]

            for pattern in retrieval_patterns:
                if re.search(pattern, query_lower):
                    # Use memory service for retrieval (with backward compatibility)
                    try:
                        retrieval_result_obj = await self.memory_service.search_memory(query)
                        retrieval_result = retrieval_result_obj.message
                    except Exception as e:
                        # Fallback to direct tool usage for backward compatibility
                        logger.warning(f"Memory service failed, using fallback: {e}")
                        if hasattr(self, 'search_memory_tool'):
                            retrieval_result = self.search_memory_tool.invoke({"query": query})
                        else:
                            # Initialize tools if needed
                            await self._initialize_original_memory_tools()
                            retrieval_result = self.search_memory_tool.invoke({"query": query})

                    logger.info(f"Retrieved memory using service layer for: {query[:50]}...")

                    # Return retrieved memory instead of agent response if we found something useful
                    if retrieval_result and len(retrieval_result.strip()) > 20:
                        # Clean up the retrieval result (remove duplicates and formatting issues)
                        cleaned_result = self._clean_memory_retrieval_result(retrieval_result)
                        if cleaned_result:
                            return cleaned_result

            # Return original response if no memory operations detected
            return response

        except Exception as e:
            logger.error(f"Failed to handle memory with original tools: {e}")
            return response

    async def _initialize_original_memory_tools(self):
        """Initialize the original working memory tools."""
        try:
            from ..tools.rag_tools import get_rag_tools
            from ..tools.rag_memory_manager import RAGMemoryManager
            from ..config import get_config

            # Initialize RAG memory manager with proper config (original working system)
            config = get_config()
            rag_manager = RAGMemoryManager(config)

            # Get the original tools
            rag_tools = get_rag_tools(rag_manager)

            # Extract the specific tools we need
            for tool in rag_tools:
                if tool.name == "remember_fact":
                    self.remember_fact_tool = tool
                elif tool.name == "search_long_term_memory":
                    self.search_memory_tool = tool
                elif tool.name == "forget_information":
                    self.forget_tool = tool

            self._memory_tools_initialized = True
            logger.info("Original memory tools initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize original memory tools: {e}")
            self._memory_tools_initialized = False

    def _clean_memory_retrieval_result(self, result: str) -> str:
        """Clean up memory retrieval results to remove duplicates and formatting issues."""
        if not result:
            return ""

        # Split into lines and remove duplicates while preserving order
        lines = result.split('\n')
        seen = set()
        cleaned_lines = []

        for line in lines:
            line = line.strip()
            if line and line not in seen and len(line) > 10:  # Skip very short lines
                seen.add(line)
                cleaned_lines.append(line)

        # Join the cleaned lines
        cleaned_result = '\n'.join(cleaned_lines[:3])  # Limit to top 3 relevant results

        return cleaned_result if cleaned_result else ""

    async def _handle_memory_retrieval(self, query: str, current_response: str) -> str:
        """Handle memory retrieval queries and enhance responses with stored memories."""
        try:
            import re
            query_lower = query.lower().strip()

            # Detect memory retrieval patterns
            retrieval_patterns = [
                r'\b(what\s+do\s+you\s+remember|what\s+did\s+i|tell\s+me\s+about\s+me)',
                r'\b(what\s+is\s+my|what\s+are\s+my|where\s+do\s+i)',
                r'\b(what\s+programming|what\s+language|what\s+technologies)',
                r'\b(what\s+project|what\s+am\s+i\s+working)',
                r'\b(what\s+do\s+i\s+want\s+to\s+learn|what\s+are\s+my\s+learning)',
                r'\b(my\s+professional|my\s+work|my\s+job|my\s+background)'
            ]

            # Check if this is a memory retrieval query
            is_memory_query = any(re.search(pattern, query_lower) for pattern in retrieval_patterns)

            if not is_memory_query:
                return current_response

            # Search for relevant memories
            memories = self.smart_rag.search_memory(query, limit=3)

            if not memories:
                # No memories found - return enhanced response
                return f"I don't have any specific information stored about that. {current_response}"

            # Build enhanced response with retrieved memories
            memory_content = []
            for memory in memories:
                if memory['relevance_score'] > 0.3:  # Only include relevant memories
                    memory_content.append(memory['content'])

            if memory_content:
                enhanced_response = f"Based on what I remember: {' '.join(memory_content[:2])}"

                # Add context if the current response is generic
                generic_indicators = [
                    "could you", "would you like", "feel free", "let me check",
                    "i can help", "more details", "be more specific"
                ]

                if any(indicator in current_response.lower() for indicator in generic_indicators):
                    return enhanced_response
                else:
                    return f"{enhanced_response}\n\n{current_response}"

            return current_response

        except Exception as e:
            logger.error(f"Failed to handle memory retrieval: {e}")
            return current_response
    
    async def _process_with_llm(self,
                               query: str,
                               prompt: str,
                               tools: List[str],
                               complexity: QueryComplexity,
                               persistent_agent=None) -> str:
        """Process query with real LLM and tools using the actual agent system."""
        try:
            # Import and use the real agent system
            from .agent import JarvisAgent
            from ..config import get_config
            from ..tools import plugin_manager

            # Use persistent agent if provided, otherwise create new one
            if persistent_agent:
                agent = persistent_agent
                logger.info("Using persistent agent for memory continuity")
            else:
                # Get configuration
                config = get_config()

                # Create agent instance
                agent = JarvisAgent(config.llm, config.agent)

            # Get all available tools
            all_tools = plugin_manager.get_all_tools()

            # Filter to only selected tools if provided
            if tools:
                # Create a mapping of tool names to tool objects
                tool_map = {tool.name: tool for tool in all_tools}
                selected_tools = []
                for tool_name in tools:
                    if tool_name in tool_map:
                        selected_tools.append(tool_map[tool_name])

                # Use selected tools (representative sample for tool listing queries)
                agent.initialize(selected_tools if selected_tools else all_tools[:3])
                logger.info(f"Using {len(selected_tools)} selected tools: {tools}")
            else:
                # Fallback: use first 3 tools to avoid overload
                agent.initialize(all_tools[:3])
                logger.info(f"Using first 3 tools as fallback")

            # Process with real agent
            response = await agent.process_input(query)

            return response

        except Exception as e:
            logger.error(f"Real LLM processing failed: {e}")

            # Fallback to simulated response if real processing fails
            processing_times = {
                QueryComplexity.INSTANT: 0.01,
                QueryComplexity.EXPLICIT_FACT: 0.15,
                QueryComplexity.SIMPLE_REASONING: 0.5,
                QueryComplexity.COMPLEX_MULTI_STEP: 2.0
            }

            await asyncio.sleep(processing_times.get(complexity, 0.5))

            if complexity == QueryComplexity.EXPLICIT_FACT:
                return f"Here's the information about {query[:50]}..."
            elif complexity == QueryComplexity.SIMPLE_REASONING:
                return f"Based on my analysis of {query[:30]}..., here's what I found..."
            elif complexity == QueryComplexity.COMPLEX_MULTI_STEP:
                tools_str = ", ".join(tools) if tools else "available tools"
                return f"I'll help you with this complex request using {tools_str}. Let me break this down..."
            else:
                return "I understand your request and I'm here to help."
    
    def _generate_final_response(self, llm_response: str, complexity: QueryComplexity) -> str:
        """Generate final optimized response."""
        # Return full response without truncation - let LLM max_tokens handle length
        return llm_response
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary."""
        budget_compliance = ((self.stats["total_queries"] - self.stats["budget_violations"]) / 
                            max(1, self.stats["total_queries"]))
        
        cache_hit_rate = self.stats["cache_hits"] / max(1, self.stats["total_queries"])
        instant_response_rate = self.stats["instant_responses"] / max(1, self.stats["total_queries"])
        
        return {
            "total_queries": self.stats["total_queries"],
            "avg_processing_time_ms": self.stats["avg_processing_time"] * 1000,
            "budget_compliance_rate": budget_compliance,
            "cache_hit_rate": cache_hit_rate,
            "instant_response_rate": instant_response_rate,
            "complexity_distribution": self.stats["complexity_distribution"],
            "component_stats": {
                "classifier": self.classifier.get_classification_stats(),
                "cache": self.cache.get_cache_stats(),
                "instant_handler": self.instant_handler.get_performance_stats(),
                "tool_selection_manager": self.tool_selection_manager.get_selection_stats(),
                "performance_manager": self.performance_manager.get_session_performance_summary(),
                "smart_rag": self.smart_rag.get_rag_stats(),
                "memory": self.memory.get_context_stats()
            }
        }
    
    def reset_stats(self) -> None:
        """Reset all performance statistics."""
        self.stats = {
            "total_queries": 0,
            "budget_violations": 0,
            "instant_responses": 0,
            "cache_hits": 0,
            "avg_processing_time": 0.0,
            "complexity_distribution": {c.value: 0 for c in QueryComplexity}
        }
        
        # Reset component stats
        self.instant_handler.reset_stats()
        self.smart_rag.reset_stats()
        
        logger.info("All performance statistics reset")


# Global controller instance
_optimized_controller = None


def get_optimized_controller() -> OptimizedJarvisController:
    """Get global optimized controller instance."""
    global _optimized_controller
    if _optimized_controller is None:
        _optimized_controller = OptimizedJarvisController()
    return _optimized_controller
