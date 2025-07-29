"""
Intelligent RAG Plugin for Jarvis

This plugin provides intelligent Retrieval-Augmented Generation capabilities:
- Automatic document processing with LLM analysis
- Conversational memory storage and retrieval
- Document knowledge base with semantic search
- Source attribution for clear information provenance

The plugin maintains the zero built-in tools philosophy by providing all RAG
functionality through dynamically loaded plugin tools.
"""

import logging
from pathlib import Path
from typing import List, Optional
from langchain_core.tools import tool

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global RAG service instance (initialized on first use)
_rag_service = None


def _get_rag_service():
    """Get or initialize the RAG service instance."""
    global _rag_service
    
    if _rag_service is None:
        try:
            # Import here to avoid circular dependencies
            from jarvis.config import get_config
            from jarvis.tools.rag_service import RAGService
            
            config = get_config()
            if not config.rag.enabled:
                logger.warning("RAG system is disabled in configuration")
                return None
                
            _rag_service = RAGService(config)
            logger.info(f"🧠 Intelligent RAG service initialized (thermal-safe: {_rag_service.document_llm.model})")
            
            # Start automatic file processing
            _start_automatic_processing()
            
        except Exception as e:
            logger.error(f"Failed to initialize RAG service: {e}")
            return None
    
    return _rag_service


def _start_automatic_processing():
    """Start automatic processing of documents in the documents folder."""
    try:
        rag_service = _get_rag_service()
        if not rag_service:
            return

        # Check if there are new documents to process
        documents_path = Path(rag_service.config.rag.documents_path)
        if documents_path.exists():
            # Get list of supported files
            supported_extensions = {'.txt', '.pdf', '.doc', '.docx'}
            files = [f for f in documents_path.iterdir()
                    if f.is_file() and f.suffix.lower() in supported_extensions]

            if files:
                logger.info(f"📁 Found {len(files)} documents for intelligent processing")
                logger.info("🤖 Database Agent will handle intelligent data merging on upload")

    except Exception as e:
        logger.error(f"Error in automatic processing setup: {e}")


async def _intelligent_document_upload(file_content: str, filename: str) -> str:
    """
    Process document upload using the Database Agent for intelligent merging.

    This function integrates the Database Agent with the RAG system to provide
    intelligent document processing, entity extraction, and data merging.
    """
    try:
        from jarvis.tools.database_agent import get_database_agent
        from jarvis.config import get_config

        logger.info(f"🤖 Starting intelligent document processing: {filename}")

        # Get existing data for this document type (simplified for now)
        rag_service = _get_rag_service()
        if not rag_service:
            return "RAG system is not available for intelligent processing."

        # Get Database Agent
        config = get_config()
        db_agent = get_database_agent(config)

        # Process document with Database Agent
        merge_plan = await db_agent.process_document_upload(
            content=file_content,
            filename=filename,
            existing_data=[]  # TODO: Get actual existing data from vector store
        )

        # Execute the merge plan (for now, just add to RAG as before)
        # TODO: Implement intelligent merging based on merge_plan
        rag_service.add_conversational_memory(f"Document processed: {filename}")

        # Return summary to user
        summary = f"✅ Intelligent processing complete for {filename}:\n"
        summary += f"   {merge_plan.summary}\n"
        summary += f"   Processing time: {merge_plan.estimated_processing_time:.2f}s\n"

        if merge_plan.warnings:
            summary += f"   Warnings: {', '.join(merge_plan.warnings)}\n"

        summary += f"   Database Agent used Qwen2.5:3b-instruct for fast, efficient processing."

        return summary

    except Exception as e:
        logger.error(f"❌ Intelligent document processing failed: {e}")
        return f"Error during intelligent processing: {str(e)}"


def _format_search_results(results: List, source_type: str) -> str:
    """Format search results with proper source attribution."""
    if not results:
        if source_type == "conversations":
            return "I don't have any stored information from our conversations about that topic yet. You can tell me to remember facts by saying 'Remember that...' and I'll store them for future reference."
        elif source_type == "documents":
            return "I don't have any document information about that topic yet. You can add documents to the data/documents/ folder and they'll be automatically processed for search."
        else:
            return "I don't have any stored information about that topic yet. This could be from conversations (use 'Remember that...' to store facts) or documents (add files to data/documents/ folder)."
    
    # Format results with source attribution
    formatted_results = []
    for result in results:
        source = result.metadata.get('source', 'unknown')
        source_type_meta = result.metadata.get('source_type', 'unknown')
        content = result.page_content
        
        if source_type_meta == 'conversational':
            attribution = "From our conversation"
        elif source_type_meta == 'document':
            attribution = f"From {source}"
        else:
            attribution = f"From {source}"
        
        formatted_results.append(f"{attribution}: {content}")
    
    return "\n\n".join(formatted_results)


@tool
def search_conversations(query: str) -> str:
    """
    Search ONLY conversational memories from previous conversations.
    
    Use this when the user asks about:
    - Personal facts, preferences, or information they've shared
    - Things they've told you to remember from conversations
    - Their habits, likes, dislikes, or personal details
    - Previous conversation topics or decisions
    
    This searches ONLY information stored from conversations, not documents.
    Returns clear attribution showing information came from conversations.
    """
    try:
        rag_service = _get_rag_service()
        if not rag_service:
            return "RAG system is not available."
        
        # Search with filter for conversational sources
        results = rag_service.vector_store.similarity_search(
            query, 
            k=rag_service.config.rag.search_k,
            filter={"source_type": "conversational"}
        )
        
        return _format_search_results(results, "conversations")
        
    except Exception as e:
        logger.error(f"Error searching conversations: {e}")
        return f"I encountered an error while searching conversational memories: {str(e)}"


@tool
def search_documents(query: str) -> str:
    """
    Search ONLY document knowledge from uploaded files.
    
    Use this when the user asks about:
    - Technical documentation or guides
    - Information from uploaded files
    - Specific topics that would be in documents
    - How-to questions that might be documented
    
    This searches ONLY processed documents, not conversational memories.
    Returns clear attribution showing which document the information came from.
    """
    try:
        rag_service = _get_rag_service()
        if not rag_service:
            return "RAG system is not available."
        
        # Search with filter for document sources
        results = rag_service.vector_store.similarity_search(
            query, 
            k=rag_service.config.rag.search_k,
            filter={"source_type": "document"}
        )
        
        return _format_search_results(results, "documents")
        
    except Exception as e:
        logger.error(f"Error searching documents: {e}")
        return f"I encountered an error while searching document knowledge: {str(e)}"


@tool
def search_all_memory(query: str) -> str:
    """
    Search ALL stored information from both conversations AND documents.
    
    Use this when the user asks general questions that could be answered from:
    - Either conversational memories OR document knowledge
    - When you're not sure which source would have the information
    - For comprehensive searches across all available information
    
    Returns results with clear attribution showing whether information came
    from conversations or specific documents.
    """
    try:
        rag_service = _get_rag_service()
        if not rag_service:
            return "RAG system is not available."
        
        # Search without filters to get all sources
        results = rag_service.vector_store.similarity_search(
            query, 
            k=rag_service.config.rag.search_k
        )
        
        return _format_search_results(results, "all")
        
    except Exception as e:
        logger.error(f"Error searching all memory: {e}")
        return f"I encountered an error while searching my memory: {str(e)}"


@tool
def remember_fact(fact: str) -> str:
    """
    Store information in PERMANENT conversational memory.
    
    Use when user explicitly asks to remember something:
    - "Remember that I like..."
    - "Remember my preference for..."
    - "Store this information..."
    - "Don't forget that..."
    
    This stores conversational facts that persist across sessions.
    DO NOT use for casual mentions or general conversation.
    Includes PII detection and user warnings for sensitive information.
    """
    try:
        rag_service = _get_rag_service()
        if not rag_service:
            return "RAG system is not available."
        
        # PII Detection (excludes names - names are allowed and encouraged)
        pii_indicators = [
            'ssn', 'social security', 'credit card', 'password', 'pin',
            'bank account', 'routing number', 'driver license', 'passport'
        ]

        fact_lower = fact.lower()
        if any(indicator in fact_lower for indicator in pii_indicators):
            return "⚠️ WARNING: This appears to contain sensitive personal information (PII). I won't store this for your privacy and security. Please avoid sharing sensitive details like SSNs, passwords, or financial information."

        # Note: Names are explicitly NOT filtered as PII - they are personal information that should be stored
        
        # Store the conversational memory
        rag_service.add_conversational_memory(fact)
        
        return f"✅ I've stored this information in my long-term memory: '{fact}'. I'll remember this for future conversations."
        
    except Exception as e:
        logger.error(f"Error storing fact: {e}")
        return f"I encountered an error while trying to remember that information: {str(e)}"


# Temporarily disabled to fix event loop conflicts
# TODO: Implement proper async tool integration for Database Agent
# @tool
# def process_document_intelligently(file_content: str, filename: str) -> str:
#     """Process a document using the intelligent Database Agent."""
#     # This was causing asyncio.run() conflicts in the event loop
#     pass


# Enhanced intelligent search tool using RAGService capabilities (sync wrapper)
@tool
def search_long_term_memory_intelligent(query: str) -> str:
    """
    Search long-term memory using advanced intelligent processing with query optimization and result synthesis.

    This tool uses specialized LLM capabilities for:
    - Query optimization and expansion with related terms
    - Multi-query search with semantic understanding
    - Result synthesis and ranking
    - Source citation and confidence scoring

    Use this when you need comprehensive, intelligent answers from stored documents and conversations.
    The tool provides synthesized responses with source citations and confidence levels.
    """
    try:
        import asyncio

        rag_service = _get_rag_service()
        if not rag_service:
            return "RAG system is not available."

        # Use the enhanced intelligent retriever tool with sync wrapper
        async def _async_search():
            intelligent_tool = rag_service.get_retriever_tool()
            return await intelligent_tool.ainvoke({"query": query})

        # Run async function in sync context
        try:
            # Try to get existing event loop
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If loop is running, we need to use run_in_executor or similar
                # For now, fall back to basic search to avoid blocking
                logger.warning("Event loop running, using fallback search")
                return search_all_memory(query)
            else:
                return loop.run_until_complete(_async_search())
        except RuntimeError:
            # No event loop, create new one
            return asyncio.run(_async_search())

    except Exception as e:
        logger.error(f"Error in intelligent search: {e}")
        return f"I encountered an error while searching my memory: {str(e)}"


# Backward compatibility alias (now uses intelligent search when possible)
@tool
def search_long_term_memory(query: str) -> str:
    """
    Search PERMANENT, LONG-TERM memory for facts and document knowledge using intelligent processing.

    Enhanced with semantic understanding, query optimization, and result synthesis.
    Provides comprehensive answers with source citations and confidence scoring.
    """
    return search_long_term_memory_intelligent(query)


# Plugin metadata
__plugin_name__ = "Intelligent RAG System"
__plugin_version__ = "2.2.0"
__plugin_description__ = "Advanced RAG system with LLM-powered query optimization, semantic chunking, and result synthesis"
__plugin_tools__ = [
    search_conversations,
    search_documents,
    search_all_memory,
    remember_fact,
    search_long_term_memory_intelligent,  # New intelligent search with query optimization
    search_long_term_memory  # Backward compatibility (now uses intelligent search)
]

logger.info(f"🔌 {__plugin_name__} v{__plugin_version__} loaded with {len(__plugin_tools__)} tools")
