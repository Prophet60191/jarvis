"""
Simplified Prompt Templates for Jarvis Voice Assistant

Reduces system prompts from 300+ lines to 50 lines max while maintaining
core functionality and conversation awareness for optimal performance.
"""

from enum import Enum
from typing import Dict, Optional
from ..classification.smart_classifier import QueryComplexity


class PromptTemplate(Enum):
    """Simplified prompt templates for different query complexities."""
    INSTANT = "instant"
    SIMPLE = "simple"
    COMPLEX = "complex"
    FALLBACK = "fallback"


class SimplifiedPrompts:
    """
    Simplified prompt system optimized for performance.
    
    Provides context-aware prompts based on query complexity:
    - Instant: Minimal prompt for pattern-based responses
    - Simple: Basic assistant prompt for factual queries
    - Complex: Enhanced prompt for multi-step workflows
    - Fallback: General-purpose prompt for unclassified queries
    """
    
    def __init__(self):
        """Initialize simplified prompt templates."""
        self.templates = self._initialize_templates()
    
    def _initialize_templates(self) -> Dict[PromptTemplate, str]:
        """Initialize all prompt templates."""
        return {
            # INSTANT: Ultra-minimal for pattern responses (5 lines)
            PromptTemplate.INSTANT: """You are Jarvis, a helpful voice assistant.
Respond naturally and briefly to greetings, acknowledgments, and simple questions.
Keep responses conversational and under 20 words.
Use chat_history for context about ongoing conversations.
Be friendly and professional like Tony Stark's Jarvis.""",
            
            # SIMPLE: Basic assistant for factual queries (15 lines)
            PromptTemplate.SIMPLE: """You are Jarvis, a helpful AI voice assistant.

CORE CAPABILITIES:
• Answer questions using your knowledge or available tools
• Remember facts when users ask (use remember_fact tool)
• Search your memory when asked (use search_long_term_memory tool)
• Execute code for calculations and analysis (use execute_code tool)
• Get current time/date information (use get_current_time tool)

MEMORY SYSTEM:
• SHORT-TERM: Use chat_history for current conversation context
• LONG-TERM: Use tools for persistent memory across sessions

RESPONSE STYLE:
• Be concise and conversational for voice interaction
• Provide direct answers without excessive explanation
• Ask clarifying questions if the request is unclear""",
            
            # COMPLEX: Enhanced for multi-step workflows (25 lines)
            PromptTemplate.COMPLEX: """You are Jarvis, an intelligent AI assistant capable of complex task coordination.

CORE CAPABILITIES:
• Coordinate multiple tools for complex workflows
• Break down multi-step requests into logical sequences
• Execute code, analyze files, and automate tasks
• Search web content and interact with websites
• Manage memory and maintain conversation context

AVAILABLE TOOLS:
• execute_code: Run Python code for calculations, data processing, automation
• analyze_file: Process CSV, JSON, Excel, text files with analysis
• create_script: Generate automation scripts and utilities
• remember_fact/search_long_term_memory: Persistent memory management
• get_current_time: Date and time information
• Web tools: For online data and automation tasks

WORKFLOW APPROACH:
1. Analyze the request complexity and required capabilities
2. Plan the sequence of tools needed
3. Execute tools in logical order, using results from previous steps
4. Provide clear status updates during multi-step processes
5. Deliver comprehensive results with actionable insights

RESPONSE STYLE:
• Explain your plan before executing complex workflows
• Provide progress updates for multi-step tasks
• Be thorough but concise in explanations""",
            
            # FALLBACK: General-purpose prompt (20 lines)
            PromptTemplate.FALLBACK: """You are Jarvis, a sophisticated AI voice assistant.

CAPABILITIES:
• Answer questions using knowledge and available tools
• Execute code for calculations, analysis, and automation
• Manage persistent memory across conversations
• Handle both simple queries and complex multi-step tasks
• Provide natural, conversational responses optimized for voice

MEMORY SYSTEM:
• Use chat_history for immediate conversation context
• Use remember_fact tool when users ask you to remember something
• Use search_long_term_memory when users ask what you remember

TOOL USAGE:
• Select appropriate tools based on the request
• For calculations/analysis: use execute_code
• For time/date: use get_current_time
• For memory: use remember_fact or search_long_term_memory

RESPONSE GUIDELINES:
• Keep responses concise and conversational
• Provide direct answers without over-explanation
• Ask for clarification when requests are ambiguous"""
        }
    
    def get_prompt(self, 
                   complexity: QueryComplexity,
                   include_tools: bool = True,
                   custom_context: Optional[str] = None) -> str:
        """
        Get optimized prompt for query complexity.
        
        Args:
            complexity: Query complexity level
            include_tools: Whether to include tool usage instructions
            custom_context: Optional custom context to append
            
        Returns:
            Optimized prompt string
        """
        # Map complexity to template
        template_map = {
            QueryComplexity.INSTANT: PromptTemplate.INSTANT,
            QueryComplexity.EXPLICIT_FACT: PromptTemplate.SIMPLE,
            QueryComplexity.SIMPLE_REASONING: PromptTemplate.SIMPLE,
            QueryComplexity.COMPLEX_MULTI_STEP: PromptTemplate.COMPLEX
        }
        
        template = template_map.get(complexity, PromptTemplate.FALLBACK)
        prompt = self.templates[template]
        
        # Add custom context if provided
        if custom_context:
            prompt += f"\n\nADDITIONAL CONTEXT:\n{custom_context}"
        
        # For instant responses, remove tool instructions if not needed
        if complexity == QueryComplexity.INSTANT and not include_tools:
            lines = prompt.split('\n')
            # Keep only the first 3 lines for ultra-minimal instant responses
            prompt = '\n'.join(lines[:3])
        
        return prompt
    
    def get_cached_prompt_key(self, 
                            complexity: QueryComplexity,
                            include_tools: bool = True,
                            custom_context: Optional[str] = None) -> str:
        """
        Get cache key for prompt configuration.
        
        Args:
            complexity: Query complexity level
            include_tools: Whether tools are included
            custom_context: Custom context string
            
        Returns:
            Cache key for this prompt configuration
        """
        context_hash = hash(custom_context) if custom_context else 0
        return f"prompt_{complexity.value}_{include_tools}_{context_hash}"
    
    def get_prompt_stats(self) -> Dict[str, Dict[str, int]]:
        """Get statistics about prompt templates."""
        stats = {}
        
        for template, prompt in self.templates.items():
            lines = len(prompt.strip().split('\n'))
            words = len(prompt.split())
            chars = len(prompt)
            
            stats[template.value] = {
                "lines": lines,
                "words": words,
                "characters": chars,
                "estimated_tokens": chars // 4  # Rough token estimation
            }
        
        return stats
    
    def validate_prompt_lengths(self) -> Dict[str, bool]:
        """Validate that prompts meet length requirements."""
        results = {}
        max_lines = 50  # Target from simplification plan
        
        for template, prompt in self.templates.items():
            lines = len(prompt.strip().split('\n'))
            results[template.value] = lines <= max_lines
        
        return results


# Specialized prompt builders for specific scenarios
class ContextAwarePromptBuilder:
    """Build context-aware prompts with conversation history."""
    
    def __init__(self, simplified_prompts: SimplifiedPrompts):
        """Initialize with simplified prompts instance."""
        self.prompts = simplified_prompts
    
    def build_prompt_with_context(self,
                                 complexity: QueryComplexity,
                                 conversation_context: str = "",
                                 user_preferences: Optional[Dict[str, str]] = None,
                                 active_tools: Optional[list] = None) -> str:
        """
        Build prompt with conversation context and user preferences.
        
        Args:
            complexity: Query complexity level
            conversation_context: Recent conversation context
            user_preferences: User preferences and settings
            active_tools: List of currently available tools
            
        Returns:
            Context-aware prompt
        """
        # Get base prompt
        base_prompt = self.prompts.get_prompt(complexity)
        
        # Add context sections
        context_parts = []
        
        # Add user preferences if available
        if user_preferences:
            prefs = []
            for key, value in user_preferences.items():
                prefs.append(f"- {key}: {value}")
            if prefs:
                context_parts.append(f"USER PREFERENCES:\n" + "\n".join(prefs))
        
        # Add tool availability for complex queries
        if complexity == QueryComplexity.COMPLEX_MULTI_STEP and active_tools:
            tool_list = ", ".join(active_tools[:5])  # Limit to 5 tools
            context_parts.append(f"AVAILABLE TOOLS: {tool_list}")
        
        # Combine all parts
        if context_parts:
            context_section = "\n\n".join(context_parts)
            return f"{base_prompt}\n\n{context_section}"
        
        return base_prompt


# Global instances
_simplified_prompts = None
_context_builder = None


def get_simplified_prompts() -> SimplifiedPrompts:
    """Get global simplified prompts instance."""
    global _simplified_prompts
    if _simplified_prompts is None:
        _simplified_prompts = SimplifiedPrompts()
    return _simplified_prompts


def get_context_aware_builder() -> ContextAwarePromptBuilder:
    """Get global context-aware prompt builder."""
    global _context_builder
    if _context_builder is None:
        _context_builder = ContextAwarePromptBuilder(get_simplified_prompts())
    return _context_builder


# Utility functions for prompt optimization
def get_optimal_prompt(complexity: QueryComplexity,
                      conversation_context: str = "",
                      enable_caching: bool = True) -> str:
    """
    Get optimal prompt for query with caching support.
    
    Args:
        complexity: Query complexity level
        conversation_context: Recent conversation context
        enable_caching: Whether to use prompt caching
        
    Returns:
        Optimized prompt string
    """
    prompts = get_simplified_prompts()
    
    if enable_caching:
        # Use cached prompt if available
        from ..caching.response_cache import get_response_cache
        cache = get_response_cache()
        
        cache_key = prompts.get_cached_prompt_key(complexity)
        cached_prompt = cache.get_cached_prompt(cache_key)
        
        if cached_prompt:
            return cached_prompt
        
        # Generate and cache prompt
        prompt = prompts.get_prompt(complexity)
        cache.cache_prompt(prompt)
        return prompt
    else:
        return prompts.get_prompt(complexity)


def validate_all_prompts() -> bool:
    """Validate that all prompts meet the 50-line requirement."""
    prompts = get_simplified_prompts()
    validation_results = prompts.validate_prompt_lengths()
    
    all_valid = all(validation_results.values())
    
    if not all_valid:
        invalid_prompts = [name for name, valid in validation_results.items() if not valid]
        raise ValueError(f"Prompts exceed 50-line limit: {invalid_prompts}")
    
    return True
