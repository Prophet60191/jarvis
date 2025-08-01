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

# Enhanced PII detection patterns
PII_PATTERNS = {
    'ssn': r'\b\d{3}-?\d{2}-?\d{4}\b',
    'credit_card': r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
    'phone': r'\b(?:\+?1[-.\s]?)?\(?[2-9][0-9]{2}\)?[-.\s]?[2-9][0-9]{2}[-.\s]?[0-9]{4}\b',
    'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
    'address': r'\b\d+\s+[A-Za-z0-9\s,]+(?:Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Lane|Ln|Boulevard|Blvd|Way|Place|Pl|Court|Ct)\b',
    'ip_address': r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b',
    'date_of_birth': r'\b(?:born|birth|dob|birthday).*?(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}[/-]\d{1,2}[/-]\d{1,2})\b',
    'bank_account': r'\b(?:account|routing).*?(?:number|#).*?\d{8,17}\b',
    'passport': r'\b(?:passport).*?(?:number|#).*?[A-Z0-9]{6,9}\b',
    'license_plate': r'\b[A-Z]{2,3}[-\s]\d{3,4}[-\s]?[A-Z]{0,2}\b'
}

# PII severity levels for different warning messages
PII_SEVERITY = {
    'HIGH': ['ssn', 'credit_card', 'bank_account', 'passport'],
    'MEDIUM': ['phone', 'email', 'address', 'date_of_birth'],
    'LOW': ['ip_address', 'license_plate']
}

def detect_pii(text: str) -> tuple[List[str], str]:
    """
    Detect potential PII in text with severity assessment.

    Args:
        text: Text to analyze for PII

    Returns:
        Tuple of (detected PII types, severity level)
    """
    detected = []
    for pii_type, pattern in PII_PATTERNS.items():
        if re.search(pattern, text, re.IGNORECASE):
            detected.append(pii_type)

    # Determine severity level
    severity = 'LOW'
    for pii_type in detected:
        if pii_type in PII_SEVERITY['HIGH']:
            severity = 'HIGH'
            break
        elif pii_type in PII_SEVERITY['MEDIUM']:
            severity = 'MEDIUM'

    return detected, severity

def get_pii_warning_message(detected_pii: List[str], severity: str) -> str:
    """
    Generate appropriate warning message based on detected PII and severity.

    Args:
        detected_pii: List of detected PII types
        severity: Severity level (HIGH, MEDIUM, LOW)

    Returns:
        Formatted warning message
    """
    if not detected_pii:
        return ""

    pii_types = ', '.join(detected_pii)

    if severity == 'HIGH':
        return f"🚨 CRITICAL PII WARNING: Detected highly sensitive information ({pii_types}). This data should be handled with extreme care and may be subject to privacy regulations. "
    elif severity == 'MEDIUM':
        return f"⚠️ PII WARNING: Detected potentially sensitive information ({pii_types}). Please ensure this information should be stored permanently. "
    else:
        return f"ℹ️ INFO: Detected potentially identifying information ({pii_types}). "

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

        # Check for PII with enhanced detection
        detected_pii, severity = detect_pii(fact)
        pii_warning = get_pii_warning_message(detected_pii, severity)

        if detected_pii:
            logger.warning(f"PII detected in memory storage: {detected_pii} (severity: {severity})")

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

def _forget_information(query: str, rag_manager) -> str:
    """
    Internal function to remove specific information from long-term memory.

    Args:
        query: Description of what information to forget/remove
        rag_manager: RAGMemoryManager instance

    Returns:
        str: Status message about the removal operation
    """
    try:
        # Validate input
        if not query or not query.strip():
            return "❌ Please provide a description of what information to forget."

        query = query.strip()
        logger.info(f"Forget request: {query}")

        # Search for matching content first
        docs = rag_manager.vector_store.similarity_search(query, k=10)

        if not docs:
            return f"🔍 No information found matching '{query}' to forget."

        # Show what would be removed and ask for confirmation
        preview_items = []
        for i, doc in enumerate(docs[:5], 1):
            content_preview = doc.page_content[:100] + "..." if len(doc.page_content) > 100 else doc.page_content
            source = doc.metadata.get('source', 'unknown')
            preview_items.append(f"{i}. Source: {source}\n   Content: {content_preview}")

        preview_text = "\n".join(preview_items)

        # For safety, require explicit confirmation in the query
        confirmation_keywords = ['confirm', 'delete', 'remove', 'forget permanently', 'confirm delete', 'remove permanently']
        has_confirmation = any(keyword in query.lower() for keyword in confirmation_keywords)

        if not has_confirmation:
            return f"""🚨 FORGET OPERATION PREVIEW

Found {len(docs)} items matching '{query}':

{preview_text}

⚠️ This operation will permanently delete this information from memory.

To proceed, include one of these confirmation words in your request:
- "confirm delete"
- "remove permanently"
- "forget permanently"

Example: "forget information about my old job - confirm delete"
"""

        # Proceed with deletion
        deleted_count = 0
        errors = []

        # Get collection for direct deletion
        collection = rag_manager.vector_store._collection

        # Use a simpler approach: delete by content similarity
        try:
            # Get all documents with IDs
            all_results = collection.get()

            if all_results and 'documents' in all_results and 'ids' in all_results:
                documents = all_results['documents']
                ids = all_results['ids']

                # Find documents to delete based on similarity to search results
                ids_to_delete = set()  # Use set to avoid duplicates
                for doc in docs:
                    doc_content = doc.page_content.strip().lower()

                    # Find matching documents in the collection
                    for i, stored_content in enumerate(documents):
                        if stored_content and doc_content in stored_content.lower():
                            ids_to_delete.add(ids[i])
                            break

                # Delete the found documents
                if ids_to_delete:
                    ids_list = list(ids_to_delete)
                    collection.delete(ids=ids_list)
                    deleted_count = len(ids_list)
                    logger.info(f"Deleted {deleted_count} documents with IDs: {ids_list}")

        except Exception as e:
            error_msg = f"Failed to delete documents: {str(e)}"
            errors.append(error_msg)
            logger.error(error_msg)

        # Prepare result message
        result_parts = [f"🗑️ Forget operation completed"]
        result_parts.append(f"   Deleted: {deleted_count} items")

        if errors:
            result_parts.append(f"   Errors: {len(errors)}")
            result_parts.append("   Some items could not be deleted")

        if deleted_count > 0:
            result_parts.append(f"\n✅ Successfully removed information about '{query}' from memory")
            result_parts.append("   This action cannot be undone")
        else:
            result_parts.append(f"\n⚠️ No items were deleted")

        return "\n".join(result_parts)

    except Exception as e:
        logger.error(f"Error in forget operation: {e}")
        return f"❌ Error during forget operation: {str(e)}"


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

    # Create the 'forget_information' tool
    @tool
    def forget_information(query: str) -> str:
        """
        REMOVES specific information from PERMANENT long-term memory.

        Use when user explicitly says:
        - "Forget that..."
        - "Delete information about..."
        - "Remove from memory..."
        - "Don't remember..."
        - "Erase what I told you about..."

        SAFETY: Requires confirmation keywords for permanent deletion.
        Add 'confirm delete' or 'remove permanently' to proceed with deletion.

        Example: "Forget my old job information - confirm delete"
        """
        return _forget_information(query, rag_manager)

    logger.info("Created Stage 1 RAG tools: remember_fact, search_long_term_memory, forget_information")
    return [remember_fact, search_long_term_memory, forget_information]

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


# Chat Session Management Tools

def list_recent_chats(limit: int = 10) -> str:
    """
    List recent chat sessions with previews.

    Args:
        limit: Maximum number of sessions to return (default: 10)

    Returns:
        str: Formatted list of recent chat sessions
    """
    try:
        # Get conversation manager from global context
        from ..core.conversation import ConversationManager

        # This is a simplified approach - in practice, you'd get the actual conversation manager instance
        # For now, we'll create a temporary instance to access the chat history methods
        from ..config import get_config
        config = get_config()

        # Create a temporary conversation manager just to access chat session methods
        temp_manager = ConversationManager(config.conversation, None, None)

        sessions = temp_manager.list_chat_sessions(limit=limit)

        if not sessions:
            return "📭 No chat sessions found. Start a conversation to create your first session!"

        result = f"📚 Recent Chat Sessions (showing {len(sessions)} of {limit} requested):\n\n"

        for i, session in enumerate(sessions, 1):
            created_date = session.get('created_at', 'unknown')
            if created_date != 'unknown':
                try:
                    from datetime import datetime
                    created_dt = datetime.fromisoformat(created_date.replace('Z', '+00:00'))
                    created_date = created_dt.strftime('%Y-%m-%d %H:%M')
                except:
                    pass

            result += f"{i}. 💬 Session: {session.get('session_id', 'unknown')[:8]}...\n"
            result += f"   📅 Created: {created_date}\n"
            result += f"   💭 Messages: {session.get('message_count', 0)}\n"
            result += f"   📝 Preview: {session.get('preview', 'No preview')}\n\n"

        result += "💡 Use revisit_chat(session_id) to continue a previous conversation."

        return result

    except Exception as e:
        logger.error(f"Error listing recent chats: {e}")
        return f"❌ Error retrieving chat sessions: {str(e)}"


def revisit_chat(session_id: str) -> str:
    """
    Load and revisit a previous chat session.

    Args:
        session_id: ID of the chat session to revisit (can be partial ID)

    Returns:
        str: Status message about loading the session
    """
    try:
        # Get conversation manager from global context
        from ..core.conversation import ConversationManager
        from ..config import get_config

        config = get_config()

        # Create a temporary conversation manager to access chat session methods
        temp_manager = ConversationManager(config.conversation, None, None)

        # If partial ID provided, try to find matching session
        if len(session_id) < 36:  # UUID is 36 characters
            sessions = temp_manager.list_chat_sessions(limit=50)
            matching_sessions = [s for s in sessions if s['session_id'].startswith(session_id)]

            if not matching_sessions:
                return f"❌ No chat session found starting with '{session_id}'. Use list_recent_chats() to see available sessions."

            if len(matching_sessions) > 1:
                result = f"🔍 Multiple sessions found starting with '{session_id}':\n\n"
                for session in matching_sessions[:5]:
                    result += f"• {session['session_id'][:8]}... - {session.get('preview', 'No preview')}\n"
                result += "\n💡 Please provide a more specific session ID."
                return result

            session_id = matching_sessions[0]['session_id']

        # Load the session
        success = temp_manager.load_chat_history(session_id)

        if success:
            # Get session info
            sessions = temp_manager.list_chat_sessions(limit=100)
            session_info = next((s for s in sessions if s['session_id'] == session_id), None)

            if session_info:
                result = f"✅ Successfully loaded chat session!\n\n"
                result += f"📋 Session ID: {session_id[:8]}...\n"
                result += f"📅 Created: {session_info.get('created_at', 'unknown')}\n"
                result += f"💭 Messages: {session_info.get('message_count', 0)}\n"
                result += f"📝 Preview: {session_info.get('preview', 'No preview')}\n\n"
                result += "🔄 Chat history has been loaded. You can now continue the conversation where you left off!"

                return result
            else:
                return f"✅ Chat session {session_id[:8]}... loaded successfully!"
        else:
            return f"❌ Failed to load chat session '{session_id}'. The session may not exist or be corrupted."

    except Exception as e:
        logger.error(f"Error revisiting chat session {session_id}: {e}")
        return f"❌ Error loading chat session: {str(e)}"


def save_current_chat(session_name: str = None) -> str:
    """
    Save the current chat session with an optional custom name.

    Args:
        session_name: Optional custom name for the session

    Returns:
        str: Status message about saving the session
    """
    try:
        from ..core.conversation import ConversationManager
        from ..config import get_config

        config = get_config()
        temp_manager = ConversationManager(config.conversation, None, None)

        # Start a new session with custom name if provided
        if session_name:
            session_id = temp_manager.start_new_session(session_name)
            return f"✅ Started new chat session: '{session_name}' (ID: {session_id[:8]}...)"
        else:
            # Save current session
            if temp_manager.current_session_id:
                success = temp_manager.save_chat_history()
                if success:
                    return f"✅ Current chat session saved successfully! (ID: {temp_manager.current_session_id[:8]}...)"
                else:
                    return "❌ Failed to save current chat session."
            else:
                return "ℹ️ No active chat session to save. Start a conversation first!"

    except Exception as e:
        logger.error(f"Error saving current chat: {e}")
        return f"❌ Error saving chat session: {str(e)}"


# Privacy and Data Management Tools

def forget_information(query: str) -> str:
    """
    Remove specific information from the RAG system for privacy or corrections.

    This tool allows users to delete specific facts, memories, or document content
    from the long-term memory system. Use with caution as this action is irreversible.

    Args:
        query: Description of what information to forget/remove

    Returns:
        str: Status message about the removal operation
    """
    try:
        # Validate input
        if not query or not query.strip():
            return "❌ Please provide a description of what information to forget."

        query = query.strip()

        # Get RAG service from global context
        from ..config import get_config
        from ..tools.rag_service import RAGService

        config = get_config()
        rag_service = RAGService(config)

        logger.info(f"Forget request: {query}")

        # Search for matching content first
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            # Find relevant documents/memories
            search_results = loop.run_until_complete(
                rag_service.intelligent_search(query, max_results=10)
            )

            retrieved_docs = search_results.get('retrieved_documents', [])

            if not retrieved_docs:
                return f"🔍 No information found matching '{query}' to forget."

            # Show what would be removed and ask for confirmation
            preview_items = []
            for i, doc in enumerate(retrieved_docs[:5], 1):
                content_preview = doc.page_content[:100] + "..." if len(doc.page_content) > 100 else doc.page_content
                source = doc.metadata.get('source', 'unknown')
                preview_items.append(f"{i}. Source: {source}\n   Content: {content_preview}")

            preview_text = "\n".join(preview_items)

            # For safety, require explicit confirmation in the query
            confirmation_keywords = ['confirm', 'delete', 'remove', 'forget permanently']
            has_confirmation = any(keyword in query.lower() for keyword in confirmation_keywords)

            if not has_confirmation:
                return f"""🚨 FORGET OPERATION PREVIEW

Found {len(retrieved_docs)} items matching '{query}':

{preview_text}

⚠️ This operation will permanently delete this information from memory.

To proceed, include one of these confirmation words in your request:
- "confirm forget"
- "delete permanently"
- "remove confirmed"

Example: "forget information about Python programming - confirm delete"
"""

            # Proceed with deletion
            deleted_count = 0
            errors = []

            # Get collection for direct deletion
            collection = rag_service.vector_store._collection

            # Delete each matching document
            for doc in retrieved_docs:
                try:
                    # Find the document ID in the collection
                    doc_content = doc.page_content
                    doc_source = doc.metadata.get('source', '')

                    # Query for exact matches
                    if doc_source:
                        results = collection.get(
                            where={"source": {"$eq": doc_source}},
                            include=['documents', 'metadatas']
                        )
                    else:
                        # If no source, get all documents and search manually
                        results = collection.get(include=['documents', 'metadatas'])

                    # Find matching content
                    if results['documents']:
                        for i, stored_content in enumerate(results['documents']):
                            if stored_content and doc_content in stored_content:
                                doc_id = results['ids'][i]
                                collection.delete(ids=[doc_id])
                                deleted_count += 1
                                break

                except Exception as e:
                    error_msg = f"Failed to delete item: {str(e)}"
                    errors.append(error_msg)
                    logger.error(error_msg)

            # Prepare result message
            result_parts = [f"🗑️ Forget operation completed"]
            result_parts.append(f"   Deleted: {deleted_count} items")

            if errors:
                result_parts.append(f"   Errors: {len(errors)}")
                result_parts.append("   Some items could not be deleted")

            if deleted_count > 0:
                result_parts.append(f"\n✅ Successfully removed information about '{query}' from memory")
                result_parts.append("   This action cannot be undone")
            else:
                result_parts.append(f"\n⚠️ No items were deleted")

            return "\n".join(result_parts)

        finally:
            loop.close()

    except Exception as e:
        logger.error(f"Error in forget operation: {e}")
        return f"❌ Error during forget operation: {str(e)}"


def list_forgettable_content(category: str = "all") -> str:
    """
    List content that can be forgotten/removed from memory.

    Args:
        category: Category to list ('personal', 'documents', 'facts', 'all')

    Returns:
        str: List of forgettable content with previews
    """
    try:
        from ..config import get_config
        from ..tools.rag_service import RAGService

        config = get_config()
        rag_service = RAGService(config)

        # Get all documents
        all_docs = rag_service.get_ingested_documents()

        if not all_docs:
            return "📭 No content found in memory to list."

        result_parts = [f"📋 Forgettable Content ({category})"]
        result_parts.append("=" * 50)

        # Filter by category
        filtered_docs = []

        for doc in all_docs:
            source = doc.get('source', '').lower()
            source_type = doc.get('source_type', '').lower()

            if category == "all":
                filtered_docs.append(doc)
            elif category == "personal" and source_type == "conversational":
                filtered_docs.append(doc)
            elif category == "documents" and source_type == "document":
                filtered_docs.append(doc)
            elif category == "facts" and "fact" in source.lower():
                filtered_docs.append(doc)

        if not filtered_docs:
            return f"📭 No {category} content found to list."

        # Show content with previews
        for i, doc in enumerate(filtered_docs[:20], 1):  # Limit to 20 items
            source = doc.get('source', 'Unknown')
            chunk_count = doc.get('chunk_count', 0)
            source_type = doc.get('source_type', 'unknown')

            result_parts.append(f"{i:2d}. 📄 {source}")
            result_parts.append(f"    Type: {source_type}")
            result_parts.append(f"    Chunks: {chunk_count}")
            result_parts.append("")

        if len(all_docs) > 20:
            result_parts.append(f"... and {len(all_docs) - 20} more items")

        result_parts.append("\n💡 To forget specific content, use:")
        result_parts.append("   forget_information('description of what to forget - confirm delete')")

        return "\n".join(result_parts)

    except Exception as e:
        logger.error(f"Error listing forgettable content: {e}")
        return f"❌ Error listing content: {str(e)}"


def clear_all_memory(confirmation: str) -> str:
    """
    Clear ALL memory from the RAG system. EXTREMELY DANGEROUS operation.

    Args:
        confirmation: Must be exactly "CLEAR ALL MEMORY PERMANENTLY" to proceed

    Returns:
        str: Status of the clear operation
    """
    try:
        # Require exact confirmation phrase
        if confirmation != "CLEAR ALL MEMORY PERMANENTLY":
            return """🚨 DANGEROUS OPERATION WARNING

This will delete ALL information from the RAG memory system including:
- All personal facts and preferences
- All ingested documents
- All conversation history
- All learned information

This action is IRREVERSIBLE and cannot be undone.

To proceed, call this function with exactly:
clear_all_memory("CLEAR ALL MEMORY PERMANENTLY")

⚠️ Consider creating a backup first using the backup functionality.
"""

        from ..config import get_config
        from ..tools.rag_service import RAGService

        config = get_config()
        rag_service = RAGService(config)

        # Get collection
        collection = rag_service.vector_store._collection

        # Get current count
        initial_count = collection.count()

        if initial_count == 0:
            return "📭 Memory is already empty - nothing to clear."

        # Delete all documents
        collection.delete()

        # Verify deletion
        final_count = collection.count()

        if final_count == 0:
            return f"""🗑️ MEMORY CLEARED SUCCESSFULLY

Deleted {initial_count} items from memory.
All information has been permanently removed.

The RAG system is now empty and ready for new information.
"""
        else:
            return f"""⚠️ PARTIAL CLEAR

Attempted to delete {initial_count} items.
{final_count} items remain in memory.
Some items could not be deleted.
"""

    except Exception as e:
        logger.error(f"Error clearing all memory: {e}")
        return f"❌ Error during memory clear: {str(e)}"
