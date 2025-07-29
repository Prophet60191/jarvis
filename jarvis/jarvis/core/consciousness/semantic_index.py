"""
Semantic Code Index

Provides semantic indexing and search capabilities for code understanding,
enabling natural language queries over the codebase structure and content.
"""

import time
import logging
import hashlib
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import threading
import json
import re

logger = logging.getLogger(__name__)

class IndexType(Enum):
    """Types of semantic indices."""
    FUNCTION = "function"
    CLASS = "class"
    MODULE = "module"
    CONCEPT = "concept"
    RELATIONSHIP = "relationship"

@dataclass
class SemanticNode:
    """Represents a node in the semantic index."""
    node_id: str
    node_type: IndexType
    name: str
    content: str
    
    # Semantic information
    concepts: Set[str] = field(default_factory=set)
    relationships: Dict[str, List[str]] = field(default_factory=dict)
    
    # Location information
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    
    # Metadata
    created_at: float = field(default_factory=time.time)
    last_updated: float = field(default_factory=time.time)
    
    def add_relationship(self, relationship_type: str, target_node: str) -> None:
        """Add a relationship to another node."""
        if relationship_type not in self.relationships:
            self.relationships[relationship_type] = []
        
        if target_node not in self.relationships[relationship_type]:
            self.relationships[relationship_type].append(target_node)
    
    def get_relationships(self, relationship_type: str) -> List[str]:
        """Get relationships of a specific type."""
        return self.relationships.get(relationship_type, [])

@dataclass
class SemanticQuery:
    """Represents a semantic query."""
    query_text: str
    query_type: str = "general"
    filters: Dict[str, Any] = field(default_factory=dict)
    max_results: int = 10
    
    # Extracted query components
    concepts: Set[str] = field(default_factory=set)
    entities: Set[str] = field(default_factory=set)
    intent: Optional[str] = None

class SemanticIndex:
    """
    Semantic indexing system for code understanding.
    
    This component creates and maintains a semantic index of the codebase,
    enabling natural language queries and conceptual understanding.
    """
    
    def __init__(self, storage_path: Optional[Path] = None):
        """
        Initialize the semantic index.
        
        Args:
            storage_path: Optional path for persistent storage
        """
        self.storage_path = storage_path
        
        # Index storage
        self._nodes: Dict[str, SemanticNode] = {}
        self._concept_index: Dict[str, Set[str]] = {}  # concept -> node_ids
        self._relationship_index: Dict[str, Dict[str, Set[str]]] = {}  # type -> source -> targets
        
        # Query processing
        self._query_cache: Dict[str, List[Dict[str, Any]]] = {}
        self._cache_ttl = 300  # 5 minutes
        
        # Configuration
        self.max_nodes = 100000
        self.concept_threshold = 0.5
        self.relationship_threshold = 0.3
        
        # Thread safety
        self._lock = threading.RLock()
        
        logger.info("SemanticIndex initialized")
    
    def add_node(self, node: SemanticNode) -> bool:
        """
        Add a node to the semantic index.
        
        Args:
            node: Semantic node to add
            
        Returns:
            bool: True if node was added successfully
        """
        with self._lock:
            if len(self._nodes) >= self.max_nodes:
                logger.warning("Semantic index at maximum capacity")
                return False
            
            # Add node
            self._nodes[node.node_id] = node
            
            # Update concept index
            for concept in node.concepts:
                if concept not in self._concept_index:
                    self._concept_index[concept] = set()
                self._concept_index[concept].add(node.node_id)
            
            # Update relationship index
            for rel_type, targets in node.relationships.items():
                if rel_type not in self._relationship_index:
                    self._relationship_index[rel_type] = {}
                
                if node.node_id not in self._relationship_index[rel_type]:
                    self._relationship_index[rel_type][node.node_id] = set()
                
                self._relationship_index[rel_type][node.node_id].update(targets)
            
            # Clear query cache
            self._query_cache.clear()
            
            logger.debug(f"Added semantic node: {node.node_id}")
            return True
    
    def query(self, query: SemanticQuery) -> List[Dict[str, Any]]:
        """
        Execute a semantic query.
        
        Args:
            query: Semantic query to execute
            
        Returns:
            List[Dict[str, Any]]: Query results with relevance scores
        """
        # Check cache first
        cache_key = self._get_cache_key(query)
        if cache_key in self._query_cache:
            cached_result = self._query_cache[cache_key]
            if time.time() - cached_result[0]["cached_at"] < self._cache_ttl:
                return cached_result
        
        with self._lock:
            # Parse query
            parsed_query = self._parse_query(query)
            
            # Find matching nodes
            candidate_nodes = self._find_candidate_nodes(parsed_query)
            
            # Score and rank results
            scored_results = self._score_results(candidate_nodes, parsed_query)
            
            # Apply filters
            filtered_results = self._apply_filters(scored_results, query.filters)
            
            # Limit results
            final_results = filtered_results[:query.max_results]
            
            # Add to cache
            for result in final_results:
                result["cached_at"] = time.time()
            self._query_cache[cache_key] = final_results
            
            logger.debug(f"Semantic query returned {len(final_results)} results")
            return final_results
    
    def find_related_nodes(self, node_id: str, relationship_type: str = None,
                          max_depth: int = 2) -> List[Dict[str, Any]]:
        """
        Find nodes related to a given node.
        
        Args:
            node_id: Source node ID
            relationship_type: Optional relationship type filter
            max_depth: Maximum relationship depth to explore
            
        Returns:
            List[Dict[str, Any]]: Related nodes with relationship information
        """
        with self._lock:
            if node_id not in self._nodes:
                return []
            
            related_nodes = []
            visited = set()
            queue = [(node_id, 0, None)]  # (node_id, depth, relationship_type)
            
            while queue and len(related_nodes) < 50:  # Limit results
                current_id, depth, rel_type = queue.pop(0)
                
                if current_id in visited or depth > max_depth:
                    continue
                
                visited.add(current_id)
                
                if current_id != node_id:  # Don't include the source node
                    node = self._nodes[current_id]
                    related_nodes.append({
                        "node_id": current_id,
                        "node_type": node.node_type.value,
                        "name": node.name,
                        "relationship_type": rel_type,
                        "depth": depth,
                        "file_path": node.file_path,
                        "line_number": node.line_number
                    })
                
                # Add connected nodes to queue
                if depth < max_depth:
                    current_node = self._nodes[current_id]
                    for rel_type_key, targets in current_node.relationships.items():
                        if relationship_type is None or rel_type_key == relationship_type:
                            for target in targets:
                                if target in self._nodes:
                                    queue.append((target, depth + 1, rel_type_key))
            
            return related_nodes
    
    def get_concept_nodes(self, concept: str) -> List[str]:
        """
        Get all nodes associated with a concept.
        
        Args:
            concept: Concept to search for
            
        Returns:
            List[str]: Node IDs associated with the concept
        """
        with self._lock:
            return list(self._concept_index.get(concept, set()))
    
    def get_node(self, node_id: str) -> Optional[SemanticNode]:
        """
        Get a node by ID.
        
        Args:
            node_id: Node identifier
            
        Returns:
            Optional[SemanticNode]: Node if found, None otherwise
        """
        with self._lock:
            return self._nodes.get(node_id)
    
    def get_index_statistics(self) -> Dict[str, Any]:
        """
        Get semantic index statistics.
        
        Returns:
            Dict[str, Any]: Index statistics
        """
        with self._lock:
            # Count nodes by type
            type_counts = {}
            for node in self._nodes.values():
                node_type = node.node_type.value
                type_counts[node_type] = type_counts.get(node_type, 0) + 1
            
            # Count relationships by type
            relationship_counts = {}
            for rel_type, sources in self._relationship_index.items():
                total_relationships = sum(len(targets) for targets in sources.values())
                relationship_counts[rel_type] = total_relationships
            
            return {
                "total_nodes": len(self._nodes),
                "total_concepts": len(self._concept_index),
                "node_type_distribution": type_counts,
                "relationship_type_distribution": relationship_counts,
                "cache_size": len(self._query_cache),
                "max_capacity": self.max_nodes,
                "capacity_used": (len(self._nodes) / self.max_nodes) * 100
            }
    
    def _parse_query(self, query: SemanticQuery) -> Dict[str, Any]:
        """Parse a semantic query into components."""
        # Simple query parsing (could be enhanced with NLP)
        text = query.query_text.lower()
        
        # Extract concepts (simple keyword extraction)
        concepts = set()
        words = re.findall(r'\b\w+\b', text)
        for word in words:
            if len(word) > 3:  # Skip short words
                concepts.add(word)
        
        # Extract entities (capitalized words, function/class names)
        entities = set()
        for word in re.findall(r'\b[A-Z][a-zA-Z_]*\b', query.query_text):
            entities.add(word)
        
        # Determine intent
        intent = "search"  # Default intent
        if any(word in text for word in ["find", "search", "locate"]):
            intent = "find"
        elif any(word in text for word in ["explain", "describe", "what"]):
            intent = "explain"
        elif any(word in text for word in ["how", "usage", "example"]):
            intent = "usage"
        
        return {
            "concepts": concepts,
            "entities": entities,
            "intent": intent,
            "original_text": query.query_text
        }
    
    def _find_candidate_nodes(self, parsed_query: Dict[str, Any]) -> List[str]:
        """Find candidate nodes for a parsed query."""
        candidates = set()
        
        # Find nodes by concepts
        for concept in parsed_query["concepts"]:
            if concept in self._concept_index:
                candidates.update(self._concept_index[concept])
        
        # Find nodes by entities (exact name matches)
        for entity in parsed_query["entities"]:
            for node_id, node in self._nodes.items():
                if entity.lower() in node.name.lower():
                    candidates.add(node_id)
        
        # If no candidates found, do broader search
        if not candidates:
            query_text = parsed_query["original_text"].lower()
            for node_id, node in self._nodes.items():
                if any(word in node.content.lower() for word in query_text.split()):
                    candidates.add(node_id)
        
        return list(candidates)
    
    def _score_results(self, candidate_nodes: List[str], 
                      parsed_query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score and rank candidate nodes."""
        scored_results = []
        
        for node_id in candidate_nodes:
            node = self._nodes[node_id]
            score = self._calculate_relevance_score(node, parsed_query)
            
            if score > 0:
                scored_results.append({
                    "node_id": node_id,
                    "node": node,
                    "score": score,
                    "node_type": node.node_type.value,
                    "name": node.name,
                    "file_path": node.file_path,
                    "line_number": node.line_number,
                    "concepts": list(node.concepts)
                })
        
        # Sort by score
        scored_results.sort(key=lambda r: r["score"], reverse=True)
        return scored_results
    
    def _calculate_relevance_score(self, node: SemanticNode, 
                                 parsed_query: Dict[str, Any]) -> float:
        """Calculate relevance score for a node."""
        score = 0.0
        
        # Concept matching
        matching_concepts = node.concepts.intersection(parsed_query["concepts"])
        if node.concepts:
            concept_score = len(matching_concepts) / len(node.concepts)
            score += concept_score * 0.4
        
        # Entity matching
        for entity in parsed_query["entities"]:
            if entity.lower() in node.name.lower():
                score += 0.3
        
        # Content matching
        content_lower = node.content.lower()
        query_words = parsed_query["original_text"].lower().split()
        matching_words = sum(1 for word in query_words if word in content_lower)
        if query_words:
            content_score = matching_words / len(query_words)
            score += content_score * 0.3
        
        return min(score, 1.0)  # Cap at 1.0
    
    def _apply_filters(self, results: List[Dict[str, Any]], 
                      filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Apply filters to search results."""
        if not filters:
            return results
        
        filtered_results = []
        
        for result in results:
            include = True
            
            # Node type filter
            if "node_type" in filters:
                if result["node_type"] != filters["node_type"]:
                    include = False
            
            # File path filter
            if "file_path" in filters and result["file_path"]:
                if filters["file_path"] not in result["file_path"]:
                    include = False
            
            # Minimum score filter
            if "min_score" in filters:
                if result["score"] < filters["min_score"]:
                    include = False
            
            if include:
                filtered_results.append(result)
        
        return filtered_results
    
    def _get_cache_key(self, query: SemanticQuery) -> str:
        """Generate cache key for a query."""
        key_data = {
            "query_text": query.query_text,
            "query_type": query.query_type,
            "filters": query.filters,
            "max_results": query.max_results
        }
        return hashlib.md5(json.dumps(key_data, sort_keys=True).encode()).hexdigest()
