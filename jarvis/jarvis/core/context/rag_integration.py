"""
RAG Memory System Integration

Integrates the context management system with the existing RAG memory system
to provide seamless access to both conversational context and long-term memory.
"""

import time
import logging
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass
from enum import Enum
import threading

from .context_manager import ContextManager, Context
from .session_memory import SessionMemory, MemoryType, MemoryScope

logger = logging.getLogger(__name__)

class MemoryIntegrationType(Enum):
    """Types of memory integration."""
    CONTEXT_TO_RAG = "context_to_rag"      # Store context in RAG
    RAG_TO_CONTEXT = "rag_to_context"      # Retrieve RAG data to context
    BIDIRECTIONAL = "bidirectional"        # Both directions
    SEMANTIC_LINK = "semantic_link"        # Semantic linking between systems

class MemoryPriority(Enum):
    """Priority levels for memory operations."""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class MemoryBridge:
    """Bridge between context and RAG memory systems."""
    bridge_id: str
    source_type: str  # "context" or "rag"
    target_type: str  # "context" or "rag"
    integration_type: MemoryIntegrationType
    
    # Mapping configuration
    source_key: str
    target_key: str
    transformation_rules: Dict[str, Any]
    
    # Metadata
    created_at: float
    last_sync: Optional[float] = None
    sync_count: int = 0
    
    # Configuration
    auto_sync: bool = True
    sync_interval: float = 300  # 5 minutes
    priority: MemoryPriority = MemoryPriority.NORMAL

class RAGMemoryIntegration:
    """
    Integration layer between context management and RAG memory systems.
    
    This component provides seamless integration between the context management
    system and the existing RAG memory system, enabling unified memory access
    and intelligent data flow between systems.
    """
    
    def __init__(self, context_manager: ContextManager, rag_system: Any = None):
        """
        Initialize RAG memory integration.
        
        Args:
            context_manager: Context manager instance
            rag_system: RAG system instance (optional)
        """
        self.context_manager = context_manager
        self.rag_system = rag_system
        
        # Memory bridges
        self._memory_bridges: Dict[str, MemoryBridge] = {}
        self._sync_queue: List[str] = []  # Bridge IDs to sync
        
        # Integration state
        self._integration_enabled = True
        self._auto_sync_enabled = True
        self._last_cleanup = time.time()
        
        # Configuration
        self.max_context_to_rag_size = 1000  # Max characters to store in RAG
        self.rag_to_context_limit = 10       # Max RAG results to bring to context
        self.sync_batch_size = 5             # Max bridges to sync at once
        self.cleanup_interval = 3600         # 1 hour
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Setup default bridges if RAG system is available
        if self.rag_system:
            self._setup_default_bridges()
        
        logger.info("RAGMemoryIntegration initialized")
    
    def create_memory_bridge(self, bridge_id: str, source_type: str, target_type: str,
                           integration_type: MemoryIntegrationType,
                           source_key: str, target_key: str,
                           transformation_rules: Dict[str, Any] = None,
                           auto_sync: bool = True,
                           sync_interval: float = 300) -> bool:
        """
        Create a memory bridge between context and RAG systems.
        
        Args:
            bridge_id: Unique bridge identifier
            source_type: Source system type ("context" or "rag")
            target_type: Target system type ("context" or "rag")
            integration_type: Type of integration
            source_key: Key in source system
            target_key: Key in target system
            transformation_rules: Optional transformation rules
            auto_sync: Whether to auto-sync
            sync_interval: Sync interval in seconds
            
        Returns:
            bool: True if bridge created successfully
        """
        with self._lock:
            if bridge_id in self._memory_bridges:
                logger.warning(f"Memory bridge {bridge_id} already exists")
                return False
            
            bridge = MemoryBridge(
                bridge_id=bridge_id,
                source_type=source_type,
                target_type=target_type,
                integration_type=integration_type,
                source_key=source_key,
                target_key=target_key,
                transformation_rules=transformation_rules or {},
                created_at=time.time(),
                auto_sync=auto_sync,
                sync_interval=sync_interval
            )
            
            self._memory_bridges[bridge_id] = bridge
            
            # Add to sync queue if auto-sync enabled
            if auto_sync and self._auto_sync_enabled:
                self._sync_queue.append(bridge_id)
            
            logger.debug(f"Created memory bridge {bridge_id}: {source_type} -> {target_type}")
            return True
    
    def sync_memory_bridge(self, bridge_id: str, force: bool = False) -> bool:
        """
        Synchronize a memory bridge.
        
        Args:
            bridge_id: Bridge identifier
            force: Force sync even if not due
            
        Returns:
            bool: True if sync successful
        """
        with self._lock:
            if bridge_id not in self._memory_bridges:
                logger.warning(f"Memory bridge {bridge_id} not found")
                return False
            
            bridge = self._memory_bridges[bridge_id]
            
            # Check if sync is due
            if not force and bridge.last_sync:
                time_since_sync = time.time() - bridge.last_sync
                if time_since_sync < bridge.sync_interval:
                    return True  # Not due for sync yet
            
            try:
                if bridge.integration_type == MemoryIntegrationType.CONTEXT_TO_RAG:
                    success = self._sync_context_to_rag(bridge)
                elif bridge.integration_type == MemoryIntegrationType.RAG_TO_CONTEXT:
                    success = self._sync_rag_to_context(bridge)
                elif bridge.integration_type == MemoryIntegrationType.BIDIRECTIONAL:
                    success = (self._sync_context_to_rag(bridge) and 
                             self._sync_rag_to_context(bridge))
                elif bridge.integration_type == MemoryIntegrationType.SEMANTIC_LINK:
                    success = self._create_semantic_links(bridge)
                else:
                    success = False
                
                if success:
                    bridge.last_sync = time.time()
                    bridge.sync_count += 1
                    logger.debug(f"Synced memory bridge {bridge_id}")
                
                return success
                
            except Exception as e:
                logger.error(f"Failed to sync memory bridge {bridge_id}: {e}")
                return False
    
    def sync_all_bridges(self, force: bool = False) -> Dict[str, bool]:
        """
        Synchronize all memory bridges.
        
        Args:
            force: Force sync all bridges
            
        Returns:
            Dict[str, bool]: Sync results for each bridge
        """
        results = {}
        
        with self._lock:
            for bridge_id in list(self._memory_bridges.keys()):
                results[bridge_id] = self.sync_memory_bridge(bridge_id, force)
        
        return results
    
    def store_context_in_rag(self, session_id: str, context_key: str,
                           context_data: Any, metadata: Dict[str, Any] = None) -> bool:
        """
        Store context data in RAG system.
        
        Args:
            session_id: Session identifier
            context_key: Context key
            context_data: Context data to store
            metadata: Optional metadata
            
        Returns:
            bool: True if storage successful
        """
        if not self.rag_system:
            logger.warning("RAG system not available")
            return False
        
        try:
            # Prepare data for RAG storage
            rag_data = self._prepare_context_for_rag(context_data, metadata)
            
            # Store in RAG system (this would depend on the actual RAG implementation)
            if hasattr(self.rag_system, 'store_memory'):
                success = self.rag_system.store_memory(
                    key=f"context:{session_id}:{context_key}",
                    data=rag_data,
                    metadata={
                        "source": "context_system",
                        "session_id": session_id,
                        "context_key": context_key,
                        "timestamp": time.time(),
                        **(metadata or {})
                    }
                )
                
                logger.debug(f"Stored context {context_key} in RAG for session {session_id}")
                return success
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to store context in RAG: {e}")
            return False
    
    def retrieve_rag_for_context(self, session_id: str, query: str,
                                limit: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve RAG data for context enhancement.
        
        Args:
            session_id: Session identifier
            query: Query for RAG retrieval
            limit: Maximum results
            
        Returns:
            List[Dict[str, Any]]: RAG results
        """
        if not self.rag_system:
            logger.warning("RAG system not available")
            return []
        
        try:
            # Query RAG system
            if hasattr(self.rag_system, 'query_memory'):
                results = self.rag_system.query_memory(
                    query=query,
                    limit=limit,
                    filters={"session_id": session_id}
                )
                
                # Transform results for context use
                context_results = []
                for result in results:
                    context_result = self._prepare_rag_for_context(result)
                    if context_result:
                        context_results.append(context_result)
                
                logger.debug(f"Retrieved {len(context_results)} RAG results for context")
                return context_results
            
            return []
            
        except Exception as e:
            logger.error(f"Failed to retrieve RAG for context: {e}")
            return []
    
    def create_semantic_link(self, session_id: str, context_key: str,
                           rag_key: str, link_strength: float = 1.0,
                           link_type: str = "related") -> bool:
        """
        Create semantic link between context and RAG data.
        
        Args:
            session_id: Session identifier
            context_key: Context key
            rag_key: RAG key
            link_strength: Strength of the link (0.0 to 1.0)
            link_type: Type of link
            
        Returns:
            bool: True if link created successfully
        """
        try:
            # Store link in session memory
            link_data = {
                "context_key": context_key,
                "rag_key": rag_key,
                "link_strength": link_strength,
                "link_type": link_type,
                "created_at": time.time()
            }
            
            entry_id = self.context_manager.session_memory.store_memory(
                session_id=session_id,
                memory_type=MemoryType.METADATA,
                data=link_data,
                scope=MemoryScope.SESSION,
                tags={"semantic_link", f"type:{link_type}"}
            )
            
            logger.debug(f"Created semantic link {context_key} <-> {rag_key}")
            return entry_id is not None
            
        except Exception as e:
            logger.error(f"Failed to create semantic link: {e}")
            return False
    
    def get_semantic_links(self, session_id: str, context_key: str) -> List[Dict[str, Any]]:
        """
        Get semantic links for a context key.
        
        Args:
            session_id: Session identifier
            context_key: Context key
            
        Returns:
            List[Dict[str, Any]]: Semantic links
        """
        try:
            # Search for semantic links
            entries = self.context_manager.session_memory.search_memory(
                session_id=session_id,
                memory_type=MemoryType.METADATA,
                tags={"semantic_link"},
                limit=50
            )
            
            # Filter for this context key
            links = []
            for entry in entries:
                if entry.data.get("context_key") == context_key:
                    links.append(entry.data)
            
            return links
            
        except Exception as e:
            logger.error(f"Failed to get semantic links: {e}")
            return []
    
    def enhance_context_with_rag(self, session_id: str, context: Context) -> Context:
        """
        Enhance context with relevant RAG data.
        
        Args:
            session_id: Session identifier
            context: Context to enhance
            
        Returns:
            Context: Enhanced context
        """
        if not self.rag_system or not self._integration_enabled:
            return context
        
        try:
            # Extract key terms from context for RAG query
            query_terms = self._extract_query_terms_from_context(context)
            
            if query_terms:
                # Retrieve relevant RAG data
                rag_results = self.retrieve_rag_for_context(
                    session_id=session_id,
                    query=" ".join(query_terms),
                    limit=self.rag_to_context_limit
                )
                
                # Add RAG data to context
                if rag_results:
                    context.system_context["rag_enhanced_data"] = rag_results
                    context.system_context["rag_enhancement_timestamp"] = time.time()
                    context.update_timestamp()
            
            return context
            
        except Exception as e:
            logger.error(f"Failed to enhance context with RAG: {e}")
            return context
    
    def process_sync_queue(self, max_items: int = None) -> int:
        """
        Process the sync queue.
        
        Args:
            max_items: Maximum items to process
            
        Returns:
            int: Number of items processed
        """
        if not self._auto_sync_enabled:
            return 0
        
        max_items = max_items or self.sync_batch_size
        processed = 0
        
        with self._lock:
            while self._sync_queue and processed < max_items:
                bridge_id = self._sync_queue.pop(0)
                
                if bridge_id in self._memory_bridges:
                    self.sync_memory_bridge(bridge_id)
                    processed += 1
        
        return processed
    
    def cleanup_expired_bridges(self) -> int:
        """
        Clean up expired or unused bridges.
        
        Returns:
            int: Number of bridges cleaned up
        """
        current_time = time.time()
        
        # Only cleanup if interval has passed
        if current_time - self._last_cleanup < self.cleanup_interval:
            return 0
        
        cleaned_count = 0
        
        with self._lock:
            # Find bridges that haven't been synced in a long time
            expired_bridges = []
            for bridge_id, bridge in self._memory_bridges.items():
                if bridge.last_sync:
                    time_since_sync = current_time - bridge.last_sync
                    # Remove bridges not synced in 24 hours
                    if time_since_sync > 86400:
                        expired_bridges.append(bridge_id)
            
            # Remove expired bridges
            for bridge_id in expired_bridges:
                del self._memory_bridges[bridge_id]
                cleaned_count += 1
            
            self._last_cleanup = current_time
        
        if cleaned_count > 0:
            logger.debug(f"Cleaned up {cleaned_count} expired memory bridges")
        
        return cleaned_count
    
    def get_integration_statistics(self) -> Dict[str, Any]:
        """
        Get integration statistics.
        
        Returns:
            Dict[str, Any]: Integration statistics
        """
        with self._lock:
            total_bridges = len(self._memory_bridges)
            active_bridges = sum(1 for bridge in self._memory_bridges.values() if bridge.auto_sync)
            
            # Calculate sync statistics
            total_syncs = sum(bridge.sync_count for bridge in self._memory_bridges.values())
            avg_syncs = total_syncs / max(total_bridges, 1)
            
            # Bridge type distribution
            type_counts = {}
            for bridge in self._memory_bridges.values():
                bridge_type = bridge.integration_type.value
                type_counts[bridge_type] = type_counts.get(bridge_type, 0) + 1
            
            return {
                "integration_enabled": self._integration_enabled,
                "auto_sync_enabled": self._auto_sync_enabled,
                "total_bridges": total_bridges,
                "active_bridges": active_bridges,
                "sync_queue_size": len(self._sync_queue),
                "total_syncs": total_syncs,
                "average_syncs_per_bridge": avg_syncs,
                "bridge_type_distribution": type_counts,
                "rag_system_available": self.rag_system is not None
            }
    
    def _setup_default_bridges(self) -> None:
        """Setup default memory bridges."""
        # Context to RAG bridge for important conversations
        self.create_memory_bridge(
            bridge_id="context_to_rag_important",
            source_type="context",
            target_type="rag",
            integration_type=MemoryIntegrationType.CONTEXT_TO_RAG,
            source_key="conversation_context",
            target_key="important_conversations",
            auto_sync=True,
            sync_interval=600  # 10 minutes
        )
        
        # RAG to context bridge for relevant memories
        self.create_memory_bridge(
            bridge_id="rag_to_context_relevant",
            source_type="rag",
            target_type="context",
            integration_type=MemoryIntegrationType.RAG_TO_CONTEXT,
            source_key="relevant_memories",
            target_key="enhanced_context",
            auto_sync=True,
            sync_interval=300  # 5 minutes
        )
    
    def _sync_context_to_rag(self, bridge: MemoryBridge) -> bool:
        """Sync context data to RAG system."""
        # Implementation would depend on specific context and RAG structures
        # This is a placeholder for the actual implementation
        logger.debug(f"Syncing context to RAG for bridge {bridge.bridge_id}")
        return True
    
    def _sync_rag_to_context(self, bridge: MemoryBridge) -> bool:
        """Sync RAG data to context system."""
        # Implementation would depend on specific context and RAG structures
        # This is a placeholder for the actual implementation
        logger.debug(f"Syncing RAG to context for bridge {bridge.bridge_id}")
        return True
    
    def _create_semantic_links(self, bridge: MemoryBridge) -> bool:
        """Create semantic links between context and RAG data."""
        # Implementation would analyze semantic similarity
        # This is a placeholder for the actual implementation
        logger.debug(f"Creating semantic links for bridge {bridge.bridge_id}")
        return True
    
    def _prepare_context_for_rag(self, context_data: Any, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Prepare context data for RAG storage."""
        return {
            "content": str(context_data)[:self.max_context_to_rag_size],
            "metadata": metadata or {},
            "prepared_at": time.time()
        }
    
    def _prepare_rag_for_context(self, rag_result: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Prepare RAG result for context use."""
        if not rag_result:
            return None
        
        return {
            "content": rag_result.get("content", ""),
            "relevance": rag_result.get("score", 0.0),
            "source": rag_result.get("source", "rag"),
            "retrieved_at": time.time()
        }
    
    def _extract_query_terms_from_context(self, context: Context) -> List[str]:
        """Extract key terms from context for RAG queries."""
        terms = []
        
        # Extract from conversation context
        conv_context = context.conversation_context
        if "current_topic" in conv_context:
            terms.append(str(conv_context["current_topic"]))
        
        if "user_intent" in conv_context:
            terms.append(str(conv_context["user_intent"]))
        
        # Extract from recent interactions
        if "recent_interactions" in conv_context:
            for interaction in conv_context["recent_interactions"][-3:]:  # Last 3
                if isinstance(interaction, dict) and "user_input" in interaction:
                    # Simple keyword extraction (could be enhanced with NLP)
                    words = str(interaction["user_input"]).split()
                    terms.extend([word for word in words if len(word) > 3])
        
        # Remove duplicates and return
        return list(set(terms))[:10]  # Limit to 10 terms
