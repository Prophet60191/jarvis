"""
RAG (Retrieval-Augmented Generation) tools for Jarvis Voice Assistant.

This module provides user-facing tools that interface with the RAGMemoryManager
for long-term memory storage and retrieval with PII protection.
"""

import logging
import re
from functools import partial
from typing import List
from langchain_core.tools import tool, BaseTool

logger = logging.getLogger(__name__)

# PII detection patterns (basic implementation)
PII_PATTERNS = {
    'ssn': r'\b\d{3}-?\d{2}-?\d{4}\b',
    'credit_card': r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
    'phone': r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
    'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
    'address': r'\b\d+\s+[A-Za-z0-9\s,]+(?:Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Lane|Ln|Boulevard|Blvd)\b'
}

def detect_pii(text: str) -> List[str]:
    """
    Detect potential PII in text.
    
    Args:
        text: Text to analyze for PII
        
    Returns:
        List of detected PII types
    """
    detected = []
    for pii_type, pattern in PII_PATTERNS.items():
        if re.search(pattern, text, re.IGNORECASE):
            detected.append(pii_type)
    return detected

def _remember_fact(fact: str, manager) -> str:
    """
    Internal function to store a fact in long-term memory with enhanced feedback.

    Args:
        fact: The fact to remember
        manager: RAGMemoryManager instance

    Returns:
        Confirmation message with PII warning if applicable
    """
    try:
        # Validate input
        if not fact or fact.strip() == "":
            return "I need some information to remember. Please tell me what you'd like me to store."

        fact = fact.strip()

        # Check for PII
        detected_pii = detect_pii(fact)

        if detected_pii:
            pii_warning = f"⚠️ WARNING: Detected potential sensitive information ({', '.join(detected_pii)}). "
            logger.warning(f"PII detected in memory storage: {detected_pii}")
        else:
            pii_warning = ""

        # Store the fact
        manager.add_conversational_memory(fact)

        # Provide encouraging feedback
        confirmation = f"I've committed that to my long-term memory: '{fact}'"

        if not pii_warning:
            confirmation += " I'll remember this for all future conversations."

        return f"{pii_warning}{confirmation}"

    except Exception as e:
        logger.error(f"Failed to remember fact: {e}")
        return f"I'm sorry, I couldn't store that information in my long-term memory. Error: {str(e)}"

def _search_long_term_memory(query: str, manager) -> str:
    """
    Internal function to search long-term memory with enhanced empty handling.

    Args:
        query: Search query
        manager: RAGMemoryManager instance

    Returns:
        Search results or contextual no results message
    """
    try:
        # Get the retriever tool from the manager
        retriever_tool = manager.get_retriever_tool()

        # Execute the search
        results = retriever_tool.func(query)

        if not results or results.strip() == "":
            # Provide contextual "no results" messages based on query type
            query_lower = query.lower()

            if any(word in query_lower for word in ['preference', 'like', 'favorite', 'prefer']):
                return "I don't have any stored information about your preferences yet. You can tell me to remember your preferences by saying something like 'Remember that I like...' or 'Remember that I prefer...'"

            elif any(word in query_lower for word in ['schedule', 'meeting', 'appointment', 'work']):
                return "I don't have any information about your schedule stored yet. You can tell me to remember schedule details by saying 'Remember that I have...' or 'Remember my work schedule is...'"

            elif any(word in query_lower for word in ['family', 'personal', 'about me', 'myself']):
                return "I don't have any personal information about you stored yet. You can share facts about yourself by saying 'Remember that I...' and I'll store them for future conversations."

            else:
                return f"I don't have any stored information about '{query}' yet. You can tell me to remember facts by saying 'Remember that...' and I'll store them in my long-term memory."

        return results

    except Exception as e:
        logger.error(f"Failed to search long-term memory: {e}")
        return f"I'm sorry, I couldn't search my long-term memory right now. Error: {str(e)}"

def get_stage_one_tools(rag_manager) -> List[BaseTool]:
    """
    Bundle the tools needed for Stage 1 RAG implementation.
    
    Args:
        rag_manager: RAGMemoryManager instance
        
    Returns:
        List of RAG tools for the agent
    """
    
    # Create the 'remember_fact' tool with PII protection
    @tool
    def remember_fact(fact: str) -> str:
        """
        STORES information in PERMANENT long-term memory that persists across all conversations.

        Use ONLY when user explicitly says:
        - "Remember that..."
        - "Store this fact..."
        - "Commit to memory..."
        - "Don't forget that..."

        DO NOT use for casual mentions or general conversation.
        Includes PII detection and user warnings for sensitive information.
        """
        return _remember_fact(fact, rag_manager)

    # Create the 'search_long_term_memory' tool
    @tool
    def search_long_term_memory(query: str) -> str:
        """
        SEARCHES PERMANENT long-term memory for facts from previous conversations.

        Use when user asks:
        - "What do you remember about..."
        - "Do you remember when I told you..."
        - "What have I told you about..."
        - "Tell me what you know about my..."
        - Questions about preferences, habits, or personal facts

        This searches STORED memories, not current conversation context.
        Returns 'No relevant information found' if nothing was previously stored.
        """
        return _search_long_term_memory(query, rag_manager)
    
    logger.info("Created Stage 1 RAG tools: remember_fact, search_long_term_memory")
    return [remember_fact, search_long_term_memory]

def get_debug_tools(rag_manager, debug_mode: bool = False) -> List[BaseTool]:
    """
    Get debug tools for development and testing.
    
    Args:
        rag_manager: RAGMemoryManager instance
        debug_mode: Whether to include debug tools
        
    Returns:
        List of debug tools if debug_mode is True, empty list otherwise
    """
    if not debug_mode:
        return []
    
    @tool
    def view_all_long_term_memories() -> str:
        """Debug tool to view all facts currently stored in long-term memory with enhanced formatting."""
        try:
            # Use similarity search with a broad query to get stored documents
            docs = rag_manager.vector_store.similarity_search("", k=100)  # Get up to 100 docs

            if not docs:
                return "🧠 Long-term memory is currently empty.\n\nTo add memories, say: 'Remember that [your fact here]'"

            # Format documents for display
            memories = []
            for i, doc in enumerate(docs):
                source = doc.metadata.get('source', 'conversational')
                display_doc = doc.page_content if len(doc.page_content) <= 100 else doc.page_content[:97] + "..."
                memories.append(f"{i+1:2d}. [{source}] {display_doc}")

            header = f"🧠 Long-term Memory Contents ({len(memories)} stored facts):"
            separator = "=" * 50

            return f"{header}\n{separator}\n" + "\n".join(memories) + f"\n{separator}"

        except Exception as e:
            return f"❌ Error accessing long-term memory: {e}"

    @tool
    def get_memory_statistics() -> str:
        """Debug tool to get statistics about long-term memory usage."""
        try:
            # Use similarity search to get stored documents
            docs = rag_manager.vector_store.similarity_search("", k=100)  # Get up to 100 docs

            if not docs:
                return "📊 Memory Statistics:\n- Total memories: 0\n- Memory is empty"

            # Calculate statistics
            total_memories = len(docs)
            total_characters = sum(len(doc.page_content) for doc in docs)
            avg_length = total_characters / total_memories if total_memories > 0 else 0

            # Count by source type
            source_counts = {}
            for doc in docs:
                source = doc.metadata.get('source', 'conversational')
                source_counts[source] = source_counts.get(source, 0) + 1

            # Format statistics
            stats = [
                f"📊 Memory Statistics:",
                f"- Total memories: {total_memories}",
                f"- Total characters: {total_characters:,}",
                f"- Average length: {avg_length:.1f} characters",
                f"- Sources breakdown:"
            ]

            for source, count in sorted(source_counts.items()):
                stats.append(f"  • {source}: {count} memories")

            return "\n".join(stats)

        except Exception as e:
            return f"❌ Error getting memory statistics: {e}"
    
    logger.info("Created debug tools for RAG system")
    return [view_all_long_term_memories, get_memory_statistics]

# Main function to get all RAG tools
def get_rag_tools(rag_manager, debug_mode: bool = False) -> List[BaseTool]:
    """
    Get all RAG tools for the agent.
    
    Args:
        rag_manager: RAGMemoryManager instance
        debug_mode: Whether to include debug tools
        
    Returns:
        List of all RAG tools
    """
    tools = get_stage_one_tools(rag_manager)
    
    if debug_mode:
        tools.extend(get_debug_tools(rag_manager, debug_mode=True))
    
    logger.info(f"Providing {len(tools)} RAG tools to agent")
    return tools
