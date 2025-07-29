"""
Plugin Relationship Mapper

Tracks and analyzes relationships between plugins, including which tools
work well together, have dependencies, or conflict with each other.
"""

import time
import logging
from typing import Dict, List, Set, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, Counter
import threading

logger = logging.getLogger(__name__)

class RelationshipType(Enum):
    """Types of relationships between plugins."""
    COMPLEMENTS = "complements"      # Tools that work well together
    CONFLICTS = "conflicts"          # Tools that interfere with each other
    DEPENDS_ON = "depends_on"        # Sequential dependency relationships
    ALTERNATIVES = "alternatives"     # Tools that can substitute for each other
    ENHANCES = "enhances"            # Tools that improve another tool's output
    REQUIRES = "requires"            # Hard dependency requirement
    INCOMPATIBLE = "incompatible"    # Cannot be used together

@dataclass
class Relationship:
    """Represents a relationship between two plugins."""
    source_plugin: str
    target_plugin: str
    relationship_type: RelationshipType
    strength: float  # 0.0 to 1.0, confidence in the relationship
    evidence_count: int = 0  # Number of observations supporting this relationship
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def update_strength(self, new_evidence: float, weight: float = 1.0) -> None:
        """Update relationship strength with new evidence."""
        # Weighted average of existing strength and new evidence
        total_weight = self.evidence_count + weight
        self.strength = (self.strength * self.evidence_count + new_evidence * weight) / total_weight
        self.evidence_count += 1
        self.updated_at = time.time()

class RelationshipMapper:
    """
    Maps and analyzes relationships between plugins.
    
    This component tracks how plugins interact with each other, which ones
    work well together, and which ones conflict or have dependencies.
    """
    
    def __init__(self):
        """Initialize the relationship mapper."""
        self._relationships: Dict[str, Dict[str, Relationship]] = defaultdict(dict)
        self._usage_patterns: Dict[str, List[Tuple[str, float]]] = defaultdict(list)  # plugin -> [(other_plugin, timestamp)]
        self._lock = threading.RLock()
        
        # Configuration
        self.min_evidence_threshold = 3  # Minimum evidence count for reliable relationships
        self.time_window_seconds = 300   # 5 minutes window for co-usage detection
        self.strength_decay_factor = 0.95  # Decay factor for aging relationships
        
        logger.info("RelationshipMapper initialized")
    
    def add_relationship(self, source_plugin: str, target_plugin: str,
                        relationship_type: RelationshipType, strength: float,
                        metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Add or update a relationship between two plugins.
        
        Args:
            source_plugin: Source plugin name
            target_plugin: Target plugin name
            relationship_type: Type of relationship
            strength: Relationship strength (0.0 to 1.0)
            metadata: Optional metadata about the relationship
        """
        if source_plugin == target_plugin:
            return  # No self-relationships
        
        with self._lock:
            relationship_key = f"{target_plugin}:{relationship_type.value}"
            
            if relationship_key in self._relationships[source_plugin]:
                # Update existing relationship
                existing = self._relationships[source_plugin][relationship_key]
                existing.update_strength(strength)
                if metadata:
                    existing.metadata.update(metadata)
            else:
                # Create new relationship
                self._relationships[source_plugin][relationship_key] = Relationship(
                    source_plugin=source_plugin,
                    target_plugin=target_plugin,
                    relationship_type=relationship_type,
                    strength=strength,
                    evidence_count=1,
                    metadata=metadata or {}
                )
            
            logger.debug(f"Added relationship: {source_plugin} {relationship_type.value} {target_plugin} (strength: {strength:.2f})")
    
    def remove_relationship(self, source_plugin: str, target_plugin: str,
                          relationship_type: RelationshipType) -> bool:
        """
        Remove a specific relationship.
        
        Args:
            source_plugin: Source plugin name
            target_plugin: Target plugin name
            relationship_type: Type of relationship to remove
            
        Returns:
            bool: True if relationship was removed
        """
        with self._lock:
            relationship_key = f"{target_plugin}:{relationship_type.value}"
            
            if (source_plugin in self._relationships and 
                relationship_key in self._relationships[source_plugin]):
                
                del self._relationships[source_plugin][relationship_key]
                logger.debug(f"Removed relationship: {source_plugin} {relationship_type.value} {target_plugin}")
                return True
            
            return False
    
    def get_related_plugins(self, plugin_name: str,
                          relationship_type: Optional[RelationshipType] = None,
                          min_strength: float = 0.5) -> List[str]:
        """
        Get plugins related to the specified plugin.
        
        Args:
            plugin_name: Name of the plugin
            relationship_type: Optional filter by relationship type
            min_strength: Minimum relationship strength threshold
            
        Returns:
            List[str]: List of related plugin names, sorted by strength
        """
        with self._lock:
            related_plugins = []
            
            if plugin_name not in self._relationships:
                return related_plugins
            
            for relationship_key, relationship in self._relationships[plugin_name].items():
                # Filter by relationship type if specified
                if relationship_type and relationship.relationship_type != relationship_type:
                    continue
                
                # Filter by minimum strength
                if relationship.strength < min_strength:
                    continue
                
                # Filter by minimum evidence
                if relationship.evidence_count < self.min_evidence_threshold:
                    continue
                
                related_plugins.append((relationship.target_plugin, relationship.strength))
            
            # Sort by strength (descending)
            related_plugins.sort(key=lambda x: x[1], reverse=True)
            
            return [plugin_name for plugin_name, _ in related_plugins]
    
    def get_plugin_relationships(self, plugin_name: str) -> Dict[RelationshipType, List[Tuple[str, float]]]:
        """
        Get all relationships for a plugin, grouped by type.
        
        Args:
            plugin_name: Name of the plugin
            
        Returns:
            Dict[RelationshipType, List[Tuple[str, float]]]: Relationships grouped by type
        """
        with self._lock:
            relationships_by_type = defaultdict(list)
            
            if plugin_name not in self._relationships:
                return dict(relationships_by_type)
            
            for relationship in self._relationships[plugin_name].values():
                relationships_by_type[relationship.relationship_type].append(
                    (relationship.target_plugin, relationship.strength)
                )
            
            # Sort each type by strength
            for rel_type in relationships_by_type:
                relationships_by_type[rel_type].sort(key=lambda x: x[1], reverse=True)
            
            return dict(relationships_by_type)
    
    def analyze_plugin_relationships(self, plugin_name: str, 
                                   plugin_metadata: Any,
                                   all_plugins: Dict[str, Any]) -> None:
        """
        Analyze and establish relationships for a plugin based on its metadata.
        
        Args:
            plugin_name: Name of the plugin
            plugin_metadata: Plugin metadata
            all_plugins: Dictionary of all plugins for comparison
        """
        with self._lock:
            # Analyze capability-based relationships
            self._analyze_capability_relationships(plugin_name, plugin_metadata, all_plugins)
            
            # Analyze dependency relationships
            self._analyze_dependency_relationships(plugin_name, plugin_metadata, all_plugins)
            
            # Analyze semantic relationships
            self._analyze_semantic_relationships(plugin_name, plugin_metadata, all_plugins)
    
    def record_plugin_usage(self, plugin_name: str, timestamp: Optional[float] = None) -> None:
        """
        Record plugin usage for co-usage pattern analysis.
        
        Args:
            plugin_name: Name of the plugin used
            timestamp: Optional timestamp (defaults to current time)
        """
        if timestamp is None:
            timestamp = time.time()
        
        with self._lock:
            # Add to usage patterns
            self._usage_patterns[plugin_name].append((plugin_name, timestamp))
            
            # Analyze co-usage patterns
            self._analyze_co_usage_patterns(plugin_name, timestamp)
            
            # Clean old usage data
            self._cleanup_old_usage_data(timestamp)
    
    def discover_relationships_from_usage(self, usage_history: List[Dict[str, Any]]) -> List[Relationship]:
        """
        Discover relationships from historical usage patterns.
        
        Args:
            usage_history: List of usage events with plugin names and timestamps
            
        Returns:
            List[Relationship]: Discovered relationships
        """
        discovered_relationships = []
        
        with self._lock:
            # Group usage events by time windows
            time_windows = self._group_usage_by_time_windows(usage_history)
            
            # Analyze co-occurrence patterns
            co_occurrence_counts = Counter()
            
            for window_events in time_windows:
                plugins_in_window = [event['plugin'] for event in window_events]
                
                # Count co-occurrences
                for i, plugin1 in enumerate(plugins_in_window):
                    for plugin2 in plugins_in_window[i+1:]:
                        if plugin1 != plugin2:
                            pair = tuple(sorted([plugin1, plugin2]))
                            co_occurrence_counts[pair] += 1
            
            # Create relationships from significant co-occurrences
            total_windows = len(time_windows)
            for (plugin1, plugin2), count in co_occurrence_counts.items():
                co_occurrence_rate = count / total_windows
                
                if co_occurrence_rate > 0.1:  # 10% co-occurrence threshold
                    # Determine relationship type based on usage patterns
                    rel_type = self._infer_relationship_type(plugin1, plugin2, usage_history)
                    
                    relationship = Relationship(
                        source_plugin=plugin1,
                        target_plugin=plugin2,
                        relationship_type=rel_type,
                        strength=min(co_occurrence_rate * 2, 1.0),  # Scale to 0-1
                        evidence_count=count,
                        metadata={'discovered_from_usage': True, 'co_occurrence_rate': co_occurrence_rate}
                    )
                    
                    discovered_relationships.append(relationship)
        
        return discovered_relationships
    
    def get_tool_chain_suggestions(self, starting_plugin: str, 
                                 target_capability: Optional[str] = None) -> List[List[str]]:
        """
        Suggest tool chains starting from a given plugin.
        
        Args:
            starting_plugin: Plugin to start the chain from
            target_capability: Optional target capability to reach
            
        Returns:
            List[List[str]]: List of suggested tool chains
        """
        chains = []
        
        with self._lock:
            # Use breadth-first search to find chains
            queue = [(starting_plugin, [starting_plugin])]
            visited = set()
            max_chain_length = 5
            
            while queue and len(chains) < 10:  # Limit to 10 suggestions
                current_plugin, current_chain = queue.pop(0)
                
                if len(current_chain) > max_chain_length:
                    continue
                
                if current_plugin in visited:
                    continue
                
                visited.add(current_plugin)
                
                # Get complementary and enhancing relationships
                related_plugins = []
                related_plugins.extend(self.get_related_plugins(current_plugin, RelationshipType.COMPLEMENTS))
                related_plugins.extend(self.get_related_plugins(current_plugin, RelationshipType.ENHANCES))
                
                for related_plugin in related_plugins:
                    if related_plugin not in current_chain:  # Avoid cycles
                        new_chain = current_chain + [related_plugin]
                        
                        # If we have a target capability, check if this plugin provides it
                        if target_capability:
                            # This would require access to plugin metadata
                            # For now, add all chains and let the caller filter
                            pass
                        
                        chains.append(new_chain)
                        queue.append((related_plugin, new_chain))
        
        # Sort chains by total relationship strength
        return sorted(chains, key=lambda chain: self._calculate_chain_strength(chain), reverse=True)
    
    def remove_plugin_relationships(self, plugin_name: str) -> None:
        """
        Remove all relationships involving a plugin.
        
        Args:
            plugin_name: Name of the plugin to remove
        """
        with self._lock:
            # Remove as source
            if plugin_name in self._relationships:
                del self._relationships[plugin_name]
            
            # Remove as target
            for source_plugin in self._relationships:
                to_remove = []
                for relationship_key, relationship in self._relationships[source_plugin].items():
                    if relationship.target_plugin == plugin_name:
                        to_remove.append(relationship_key)
                
                for key in to_remove:
                    del self._relationships[source_plugin][key]
            
            # Remove from usage patterns
            if plugin_name in self._usage_patterns:
                del self._usage_patterns[plugin_name]
            
            logger.debug(f"Removed all relationships for plugin: {plugin_name}")
    
    def get_relationship_count(self) -> int:
        """Get total number of relationships."""
        with self._lock:
            return sum(len(relationships) for relationships in self._relationships.values())
    
    def export_relationships(self) -> Dict[str, Any]:
        """Export relationships for persistence."""
        with self._lock:
            export_data = {}
            
            for source_plugin, relationships in self._relationships.items():
                export_data[source_plugin] = {}
                for relationship_key, relationship in relationships.items():
                    export_data[source_plugin][relationship_key] = {
                        'target_plugin': relationship.target_plugin,
                        'relationship_type': relationship.relationship_type.value,
                        'strength': relationship.strength,
                        'evidence_count': relationship.evidence_count,
                        'created_at': relationship.created_at,
                        'updated_at': relationship.updated_at,
                        'metadata': relationship.metadata
                    }
            
            return export_data
    
    def load_relationships(self, data: Dict[str, Any]) -> None:
        """Load relationships from persistence data."""
        with self._lock:
            self._relationships.clear()
            
            for source_plugin, relationships in data.items():
                for relationship_key, relationship_data in relationships.items():
                    relationship = Relationship(
                        source_plugin=source_plugin,
                        target_plugin=relationship_data['target_plugin'],
                        relationship_type=RelationshipType(relationship_data['relationship_type']),
                        strength=relationship_data['strength'],
                        evidence_count=relationship_data['evidence_count'],
                        created_at=relationship_data['created_at'],
                        updated_at=relationship_data['updated_at'],
                        metadata=relationship_data['metadata']
                    )
                    
                    self._relationships[source_plugin][relationship_key] = relationship
    
    def _analyze_capability_relationships(self, plugin_name: str, plugin_metadata: Any, all_plugins: Dict[str, Any]) -> None:
        """Analyze relationships based on plugin capabilities."""
        plugin_capabilities = getattr(plugin_metadata, 'capabilities', set())
        
        for other_plugin_name, other_metadata in all_plugins.items():
            if other_plugin_name == plugin_name:
                continue
            
            other_capabilities = getattr(other_metadata, 'capabilities', set())
            
            # Calculate capability overlap
            common_capabilities = plugin_capabilities.intersection(other_capabilities)
            total_capabilities = plugin_capabilities.union(other_capabilities)
            
            if total_capabilities:
                overlap_ratio = len(common_capabilities) / len(total_capabilities)
                
                if overlap_ratio > 0.7:  # High overlap - alternatives
                    self.add_relationship(plugin_name, other_plugin_name, 
                                        RelationshipType.ALTERNATIVES, overlap_ratio)
                elif overlap_ratio > 0.3:  # Medium overlap - complements
                    self.add_relationship(plugin_name, other_plugin_name,
                                        RelationshipType.COMPLEMENTS, overlap_ratio * 0.7)
    
    def _analyze_dependency_relationships(self, plugin_name: str, plugin_metadata: Any, all_plugins: Dict[str, Any]) -> None:
        """Analyze dependency relationships."""
        dependencies = getattr(plugin_metadata, 'dependencies', [])
        
        for dependency in dependencies:
            if dependency in all_plugins:
                self.add_relationship(plugin_name, dependency, RelationshipType.DEPENDS_ON, 1.0)
    
    def _analyze_semantic_relationships(self, plugin_name: str, plugin_metadata: Any, all_plugins: Dict[str, Any]) -> None:
        """Analyze semantic relationships based on descriptions and tags."""
        plugin_description = getattr(plugin_metadata, 'description', '').lower()
        plugin_tags = getattr(plugin_metadata, 'semantic_tags', set())
        
        for other_plugin_name, other_metadata in all_plugins.items():
            if other_plugin_name == plugin_name:
                continue
            
            other_description = getattr(other_metadata, 'description', '').lower()
            other_tags = getattr(other_metadata, 'semantic_tags', set())
            
            # Simple semantic similarity based on common words and tags
            common_tags = plugin_tags.intersection(other_tags)
            common_words = set(plugin_description.split()).intersection(set(other_description.split()))
            
            if common_tags or len(common_words) > 2:
                similarity = (len(common_tags) * 0.3 + len(common_words) * 0.1)
                similarity = min(similarity, 1.0)
                
                if similarity > 0.3:
                    self.add_relationship(plugin_name, other_plugin_name,
                                        RelationshipType.COMPLEMENTS, similarity)
    
    def _analyze_co_usage_patterns(self, plugin_name: str, timestamp: float) -> None:
        """Analyze co-usage patterns to discover relationships."""
        # Find other plugins used within the time window
        window_start = timestamp - self.time_window_seconds
        
        co_used_plugins = set()
        for other_plugin, usage_events in self._usage_patterns.items():
            if other_plugin == plugin_name:
                continue
            
            for _, event_timestamp in usage_events:
                if window_start <= event_timestamp <= timestamp:
                    co_used_plugins.add(other_plugin)
                    break
        
        # Create or strengthen complement relationships
        for co_used_plugin in co_used_plugins:
            existing_strength = 0.0
            relationship_key = f"{co_used_plugin}:{RelationshipType.COMPLEMENTS.value}"
            
            if (plugin_name in self._relationships and 
                relationship_key in self._relationships[plugin_name]):
                existing_strength = self._relationships[plugin_name][relationship_key].strength
            
            # Increase strength based on co-usage
            new_strength = min(existing_strength + 0.1, 1.0)
            self.add_relationship(plugin_name, co_used_plugin, RelationshipType.COMPLEMENTS, new_strength)
    
    def _cleanup_old_usage_data(self, current_timestamp: float) -> None:
        """Clean up old usage data to prevent memory bloat."""
        cutoff_time = current_timestamp - (self.time_window_seconds * 10)  # Keep 10x time window
        
        for plugin_name in self._usage_patterns:
            self._usage_patterns[plugin_name] = [
                (plugin, timestamp) for plugin, timestamp in self._usage_patterns[plugin_name]
                if timestamp > cutoff_time
            ]
    
    def _group_usage_by_time_windows(self, usage_history: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
        """Group usage events into time windows."""
        if not usage_history:
            return []
        
        # Sort by timestamp
        sorted_history = sorted(usage_history, key=lambda x: x.get('timestamp', 0))
        
        windows = []
        current_window = []
        window_start = None
        
        for event in sorted_history:
            timestamp = event.get('timestamp', 0)
            
            if window_start is None:
                window_start = timestamp
                current_window = [event]
            elif timestamp - window_start <= self.time_window_seconds:
                current_window.append(event)
            else:
                # Start new window
                if current_window:
                    windows.append(current_window)
                window_start = timestamp
                current_window = [event]
        
        # Add final window
        if current_window:
            windows.append(current_window)
        
        return windows
    
    def _infer_relationship_type(self, plugin1: str, plugin2: str, usage_history: List[Dict[str, Any]]) -> RelationshipType:
        """Infer relationship type from usage patterns."""
        # Simple heuristic: if plugins are often used in sequence, they complement each other
        # More sophisticated analysis could be added here
        return RelationshipType.COMPLEMENTS
    
    def _calculate_chain_strength(self, chain: List[str]) -> float:
        """Calculate the total strength of a tool chain."""
        if len(chain) < 2:
            return 0.0
        
        total_strength = 0.0
        for i in range(len(chain) - 1):
            source = chain[i]
            target = chain[i + 1]
            
            # Find relationship strength
            if source in self._relationships:
                for relationship in self._relationships[source].values():
                    if relationship.target_plugin == target:
                        total_strength += relationship.strength
                        break
        
        return total_strength / (len(chain) - 1)  # Average strength
