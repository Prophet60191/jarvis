"""
Memory Service Layer - Clean abstraction for all memory operations.

This service provides a unified interface for both short-term (conversation) 
and long-term (RAG) memory systems, following proper separation of concerns.
"""

import logging
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class MemoryResult:
    """Result of a memory operation."""
    success: bool
    message: str
    data: Optional[Any] = None
    error: Optional[str] = None


class MemoryService(ABC):
    """Abstract interface for memory operations."""
    
    @abstractmethod
    async def store_fact(self, fact: str) -> MemoryResult:
        """Store a fact in long-term memory."""
        pass
    
    @abstractmethod
    async def search_memory(self, query: str) -> MemoryResult:
        """Search long-term memory."""
        pass
    
    @abstractmethod
    async def forget_information(self, query: str) -> MemoryResult:
        """Remove information from long-term memory."""
        pass
    
    @abstractmethod
    def get_conversation_context(self) -> str:
        """Get current conversation context."""
        pass
    
    @abstractmethod
    def add_to_conversation(self, message: str, role: str = "user") -> None:
        """Add message to conversation context."""
        pass


class JarvisMemoryService(MemoryService):
    """
    Concrete implementation of memory service using existing RAG tools
    and conversation memory manager.
    
    This maintains backward compatibility while providing clean abstraction.
    """
    
    def __init__(self):
        """Initialize memory service with lazy loading."""
        self._rag_tools_initialized = False
        self._remember_fact_tool = None
        self._search_memory_tool = None
        self._forget_tool = None
        self._conversation_memory = None
        
        logger.info("JarvisMemoryService initialized with lazy loading")
    
    async def _ensure_rag_tools_initialized(self):
        """Ensure RAG tools are initialized (lazy loading)."""
        if self._rag_tools_initialized:
            return
        
        try:
            from ...tools.rag_tools import get_rag_tools
            from ...tools.rag_memory_manager import RAGMemoryManager
            from ...config import get_config
            
            # Initialize RAG memory manager with proper config
            config = get_config()
            rag_manager = RAGMemoryManager(config)
            
            # Get the original tools
            rag_tools = get_rag_tools(rag_manager)
            
            # Extract the specific tools we need
            for tool in rag_tools:
                if tool.name == "remember_fact":
                    self._remember_fact_tool = tool
                elif tool.name == "search_long_term_memory":
                    self._search_memory_tool = tool
                elif tool.name == "forget_information":
                    self._forget_tool = tool
            
            self._rag_tools_initialized = True
            logger.info("RAG tools initialized successfully in memory service")
            
        except Exception as e:
            logger.error(f"Failed to initialize RAG tools: {e}")
            raise
    
    def _ensure_conversation_memory_initialized(self):
        """Ensure conversation memory is initialized."""
        if self._conversation_memory is None:
            try:
                from ..memory.conversation_memory_manager import get_conversation_memory_manager
                self._conversation_memory = get_conversation_memory_manager()
                logger.info("Conversation memory initialized in memory service")
            except Exception as e:
                logger.error(f"Failed to initialize conversation memory: {e}")
                # Create a simple fallback
                self._conversation_memory = SimpleConversationMemory()
    
    async def store_fact(self, fact: str) -> MemoryResult:
        """Store a fact in long-term memory using RAG tools."""
        try:
            await self._ensure_rag_tools_initialized()
            
            if not self._remember_fact_tool:
                return MemoryResult(
                    success=False,
                    message="Memory storage tool not available",
                    error="remember_fact_tool not initialized"
                )
            
            # Use the original working tool
            result = self._remember_fact_tool.invoke({"fact": fact})
            
            return MemoryResult(
                success=True,
                message=result,
                data={"fact": fact}
            )
            
        except Exception as e:
            logger.error(f"Failed to store fact: {e}")
            return MemoryResult(
                success=False,
                message=f"Failed to store fact: {str(e)}",
                error=str(e)
            )
    
    async def search_memory(self, query: str) -> MemoryResult:
        """Search long-term memory using RAG tools."""
        try:
            await self._ensure_rag_tools_initialized()
            
            if not self._search_memory_tool:
                return MemoryResult(
                    success=False,
                    message="Memory search tool not available",
                    error="search_memory_tool not initialized"
                )
            
            # Use the original working tool
            result = self._search_memory_tool.invoke({"query": query})
            
            return MemoryResult(
                success=True,
                message=result,
                data={"query": query, "results": result}
            )
            
        except Exception as e:
            logger.error(f"Failed to search memory: {e}")
            return MemoryResult(
                success=False,
                message=f"Failed to search memory: {str(e)}",
                error=str(e)
            )
    
    async def forget_information(self, query: str) -> MemoryResult:
        """Remove information from long-term memory using RAG tools."""
        try:
            await self._ensure_rag_tools_initialized()
            
            if not self._forget_tool:
                return MemoryResult(
                    success=False,
                    message="Memory deletion tool not available",
                    error="forget_tool not initialized"
                )
            
            # Use the original working tool
            result = self._forget_tool.invoke({"query": query})
            
            return MemoryResult(
                success=True,
                message=result,
                data={"query": query}
            )
            
        except Exception as e:
            logger.error(f"Failed to forget information: {e}")
            return MemoryResult(
                success=False,
                message=f"Failed to forget information: {str(e)}",
                error=str(e)
            )
    
    def get_conversation_context(self) -> str:
        """Get current conversation context."""
        try:
            self._ensure_conversation_memory_initialized()
            
            if hasattr(self._conversation_memory, 'get_context'):
                return self._conversation_memory.get_context()
            else:
                return "No conversation context available"
                
        except Exception as e:
            logger.error(f"Failed to get conversation context: {e}")
            return "Error retrieving conversation context"
    
    def add_to_conversation(self, message: str, role: str = "user") -> None:
        """Add message to conversation context."""
        try:
            self._ensure_conversation_memory_initialized()
            
            if hasattr(self._conversation_memory, 'add_message'):
                self._conversation_memory.add_message(message, role)
            else:
                logger.warning("Conversation memory does not support add_message")
                
        except Exception as e:
            logger.error(f"Failed to add to conversation: {e}")


class SimpleConversationMemory:
    """Simple fallback conversation memory."""
    
    def __init__(self):
        self._messages = []
    
    def get_context(self) -> str:
        return "\n".join(self._messages[-10:])  # Last 10 messages
    
    def add_message(self, message: str, role: str = "user") -> None:
        self._messages.append(f"{role}: {message}")


# Factory function for dependency injection
_memory_service_instance = None

def get_memory_service() -> MemoryService:
    """Get the memory service instance (singleton)."""
    global _memory_service_instance
    if _memory_service_instance is None:
        _memory_service_instance = JarvisMemoryService()
    return _memory_service_instance
