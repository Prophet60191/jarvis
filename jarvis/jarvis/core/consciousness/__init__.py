"""
Source Code Consciousness System

This package provides deep understanding of the Jarvis codebase through
semantic indexing, natural language queries, dependency analysis, and
safe self-modification capabilities.

Components:
- CodeConsciousnessSystem: Main consciousness interface
- CodebaseRAG: RAG system for code understanding
- SemanticIndex: Semantic code indexing and search
- DependencyAnalyzer: Code dependency mapping and analysis
- SafeModificationEngine: Safe code modification suggestions
- ArchitecturalKnowledge: System architecture understanding
"""

try:
    from .consciousness_system import CodeConsciousnessSystem, ConsciousnessLevel, CodeQuery
except ImportError:
    # Fallback classes
    class CodeConsciousnessSystem:
        def __init__(self, *args, **kwargs): pass
    class ConsciousnessLevel:
        BASIC = "basic"
    class CodeQuery:
        def __init__(self, *args, **kwargs): pass

try:
    from .codebase_rag import CodebaseRAG, CodeDocument, CodeChunk, CodeSearchResult
except ImportError:
    # Fallback classes
    class CodebaseRAG:
        def __init__(self, *args, **kwargs): pass
    class CodeDocument:
        def __init__(self, *args, **kwargs): pass
    class CodeChunk:
        def __init__(self, *args, **kwargs): pass
    class CodeSearchResult:
        def __init__(self, *args, **kwargs): pass

try:
    from .semantic_index import SemanticIndex, SemanticNode, SemanticQuery
except ImportError:
    # Fallback classes
    class SemanticIndex:
        def __init__(self, *args, **kwargs): pass
    class SemanticNode:
        def __init__(self, *args, **kwargs): pass
    class SemanticQuery:
        def __init__(self, *args, **kwargs): pass

try:
    from .dependency_analyzer import DependencyAnalyzer, DependencyGraph, Dependency
except ImportError:
    # Fallback classes
    class DependencyAnalyzer:
        def __init__(self, *args, **kwargs): pass
    class DependencyGraph:
        def __init__(self, *args, **kwargs): pass
    class Dependency:
        def __init__(self, *args, **kwargs): pass

try:
    from .safe_modification_engine import SafeModificationEngine, ModificationSuggestion, SafetyLevel
except ImportError:
    # Fallback classes
    class SafeModificationEngine:
        def __init__(self, *args, **kwargs): pass
    class ModificationSuggestion:
        def __init__(self, *args, **kwargs): pass
    class SafetyLevel:
        SAFE = "safe"

try:
    from .architectural_knowledge import ArchitecturalKnowledge, ArchitecturalComponent, ArchitecturalLayer
except ImportError:
    # Fallback classes
    class ArchitecturalKnowledge:
        def __init__(self, *args, **kwargs): pass
    class ArchitecturalComponent:
        def __init__(self, *args, **kwargs): pass
    class ArchitecturalLayer:
        def __init__(self, *args, **kwargs): pass

__all__ = [
    # Core consciousness system
    "CodeConsciousnessSystem",
    "ConsciousnessLevel",
    "CodeQuery",

    # Codebase RAG
    "CodebaseRAG",
    "CodeDocument",
    "CodeChunk",
    "CodeSearchResult",

    # Semantic indexing
    "SemanticIndex",
    "SemanticNode",
    "SemanticQuery",

    # Dependency analysis
    "DependencyAnalyzer",
    "DependencyGraph",
    "Dependency",

    # Safe modification
    "SafeModificationEngine",
    "ModificationSuggestion",
    "SafetyLevel",

    # Architectural knowledge
    "ArchitecturalKnowledge",
    "ArchitecturalComponent",
    "ArchitecturalLayer"
]
