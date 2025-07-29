"""
Enhanced Plugin Registry System

This package provides intelligent plugin metadata and relationship tracking
for the Jarvis plugin system, extending the existing plugin architecture
with advanced capabilities.

Components:
- UnifiedPluginRegistry: Core registry with enhanced metadata
- RelationshipMapper: Tool relationship tracking and analysis
- CapabilityAnalyzer: Automatic capability detection and categorization
- UsageAnalytics: Usage pattern analysis and performance tracking
"""

from .unified_registry import UnifiedPluginRegistry, EnhancedPluginMetadata
from .relationship_mapper import RelationshipMapper, RelationshipType, Relationship
from .capability_analyzer import CapabilityAnalyzer, CapabilityCategory
from .usage_analytics import UsageAnalytics, UsageStats, PerformanceProfile

__all__ = [
    # Core registry
    "UnifiedPluginRegistry",
    "EnhancedPluginMetadata",
    
    # Relationship mapping
    "RelationshipMapper", 
    "RelationshipType",
    "Relationship",
    
    # Capability analysis
    "CapabilityAnalyzer",
    "CapabilityCategory",
    
    # Usage analytics
    "UsageAnalytics",
    "UsageStats", 
    "PerformanceProfile"
]
