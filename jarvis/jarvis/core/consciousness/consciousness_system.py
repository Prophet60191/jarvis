"""
Code Consciousness System

Main interface for the source code consciousness capabilities,
providing deep understanding of the Jarvis codebase through
semantic analysis and intelligent querying.
"""

import time
import logging
from typing import Dict, List, Optional, Any, Set, Union
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import threading

from .codebase_rag import CodebaseRAG, CodeSearchResult
try:
    from .semantic_index import SemanticIndex, SemanticNode, SemanticQuery
except ImportError:
    # Fallback if semantic index not available
    class SemanticIndex:
        def __init__(self, *args, **kwargs):
            pass
        def query(self, *args, **kwargs):
            return []

    class SemanticNode:
        def __init__(self, *args, **kwargs):
            pass

    class SemanticQuery:
        def __init__(self, *args, **kwargs):
            pass
try:
    from .dependency_analyzer import DependencyAnalyzer, DependencyGraph
except ImportError:
    # Fallback if dependency analyzer not available
    class DependencyAnalyzer:
        def __init__(self, *args, **kwargs):
            pass
        def analyze_dependencies(self, *args, **kwargs):
            return None

    class DependencyGraph:
        def __init__(self, *args, **kwargs):
            pass
try:
    from .safe_modification_engine import SafeModificationEngine, ModificationSuggestion
except ImportError:
    # Fallback if safe modification engine not available
    class SafeModificationEngine:
        def __init__(self, *args, **kwargs):
            pass
        def suggest_modification(self, *args, **kwargs):
            return "mock_suggestion_id"

    class ModificationSuggestion:
        def __init__(self, *args, **kwargs):
            pass
try:
    from .architectural_knowledge import ArchitecturalKnowledge
except ImportError:
    # Fallback if architectural knowledge not available
    class ArchitecturalKnowledge:
        def __init__(self, *args, **kwargs):
            pass
        def analyze_architecture(self, *args, **kwargs):
            return {}
        def get_architectural_insights(self, *args, **kwargs):
            return {}

logger = logging.getLogger(__name__)

class ConsciousnessLevel(Enum):
    """Levels of code consciousness and understanding."""
    BASIC = "basic"           # Basic file and function awareness
    SEMANTIC = "semantic"     # Semantic understanding of code meaning
    ARCHITECTURAL = "architectural"  # Understanding of system architecture
    BEHAVIORAL = "behavioral"  # Understanding of runtime behavior
    EVOLUTIONARY = "evolutionary"  # Understanding of code evolution patterns

class QueryType(Enum):
    """Types of code consciousness queries."""
    SEARCH = "search"                    # Search for specific code
    UNDERSTAND = "understand"            # Understand code functionality
    ANALYZE = "analyze"                  # Analyze code patterns or issues
    SUGGEST = "suggest"                  # Suggest improvements or modifications
    NAVIGATE = "navigate"                # Navigate code relationships
    EXPLAIN = "explain"                  # Explain code behavior

@dataclass
class CodeQuery:
    """
    Represents a query to the code consciousness system.
    
    This encapsulates natural language queries about the codebase
    and provides structured access to query results.
    """
    query_id: str
    query_text: str
    query_type: QueryType
    consciousness_level: ConsciousnessLevel = ConsciousnessLevel.SEMANTIC
    
    # Query parameters
    scope: Optional[str] = None  # Limit query to specific files/modules
    max_results: int = 10
    include_dependencies: bool = True
    include_examples: bool = True
    
    # Results
    results: List[CodeSearchResult] = field(default_factory=list)
    insights: List[str] = field(default_factory=list)
    suggestions: List[ModificationSuggestion] = field(default_factory=list)
    
    # Metadata
    created_at: float = field(default_factory=time.time)
    processed_at: Optional[float] = None
    processing_time: float = 0.0
    confidence_score: float = 0.0
    
    def mark_processed(self, confidence: float = 0.0) -> None:
        """Mark query as processed."""
        self.processed_at = time.time()
        self.processing_time = self.processed_at - self.created_at
        self.confidence_score = confidence

class CodeConsciousnessSystem:
    """
    Main code consciousness system providing deep understanding of the codebase.
    
    This system combines multiple AI techniques to provide intelligent
    code understanding, navigation, and modification capabilities.
    """
    
    def __init__(self, codebase_path: Path,
                 consciousness_level: ConsciousnessLevel = ConsciousnessLevel.SEMANTIC,
                 enable_safe_modifications: bool = True):
        """
        Initialize the code consciousness system.
        
        Args:
            codebase_path: Path to the codebase to analyze
            consciousness_level: Level of consciousness to achieve
            enable_safe_modifications: Whether to enable modification suggestions
        """
        self.codebase_path = codebase_path
        self.consciousness_level = consciousness_level
        self.enable_safe_modifications = enable_safe_modifications
        
        # Initialize sub-components
        self.codebase_rag = CodebaseRAG(codebase_path)
        self.semantic_index = SemanticIndex()
        self.dependency_analyzer = DependencyAnalyzer(codebase_path)
        self.architectural_knowledge = ArchitecturalKnowledge(codebase_path)
        
        if enable_safe_modifications:
            self.safe_modification_engine = SafeModificationEngine(codebase_path)
        else:
            self.safe_modification_engine = None
        
        # System state
        self._indexed_files: Set[str] = set()
        self._query_history: List[CodeQuery] = []
        self._dependency_graph: Optional[DependencyGraph] = None
        self._lock = threading.RLock()
        
        # Configuration
        self.max_query_history = 1000
        self.indexing_batch_size = 50
        self.consciousness_update_interval = 3600  # 1 hour
        
        # Initialize consciousness
        self._consciousness_initialized = False
        
        logger.info(f"CodeConsciousnessSystem initialized for {codebase_path}")
    
    async def initialize_consciousness(self, force_reindex: bool = False) -> bool:
        """
        Initialize code consciousness by indexing the codebase.
        
        Args:
            force_reindex: Whether to force reindexing of all files
            
        Returns:
            bool: True if initialization successful
        """
        try:
            logger.info("Initializing code consciousness...")
            start_time = time.time()
            
            # Step 1: Index codebase with RAG system
            await self.codebase_rag.index_codebase(force_reindex=force_reindex)
            
            # Step 2: Build semantic index
            await self.semantic_index.build_index(self.codebase_path)
            
            # Step 3: Analyze dependencies
            self._dependency_graph = await self.dependency_analyzer.analyze_codebase(self.codebase_path)
            
            # Step 4: Build architectural knowledge
            await self.architectural_knowledge.analyze_architecture(
                self.codebase_path, self._dependency_graph
            )
            
            # Step 5: Update indexed files tracking
            with self._lock:
                self._indexed_files = set(self.codebase_rag.get_indexed_files())
                self._consciousness_initialized = True
            
            initialization_time = time.time() - start_time
            logger.info(f"Code consciousness initialized in {initialization_time:.2f}s")
            logger.info(f"Indexed {len(self._indexed_files)} files")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize code consciousness: {e}")
            return False

    def query_codebase(self, query_text: str,
                      query_type: str = "search",
                      scope: Optional[str] = None,
                      max_results: int = 10) -> Dict[str, Any]:
        """
        Query the codebase using natural language (synchronous version).

        Args:
            query_text: Natural language query
            query_type: Type of query ("search", "explain", "find", etc.)
            scope: Optional scope limitation
            max_results: Maximum number of results

        Returns:
            Dict[str, Any]: Query results
        """
        try:
            # Convert string query type to enum
            if query_type == "search":
                qt = QueryType.SEARCH
            elif query_type == "explain":
                qt = QueryType.EXPLAIN
            elif query_type == "find":
                qt = QueryType.FIND
            else:
                qt = QueryType.SEARCH

            # Run the async query in a synchronous context
            import asyncio
            try:
                loop = asyncio.get_event_loop()
                result = loop.run_until_complete(
                    self.query_code(query_text, qt, scope, max_results)
                )
            except RuntimeError:
                # No event loop running
                result = asyncio.run(
                    self.query_code(query_text, qt, scope, max_results)
                )

            # Convert CodeQuery result to dictionary
            return {
                "query_text": result.query_text if hasattr(result, 'query_text') else query_text,
                "query_type": query_type,
                "results": result.results if hasattr(result, 'results') else [],
                "total_results": result.total_results if hasattr(result, 'total_results') else 0,
                "execution_time": result.execution_time if hasattr(result, 'execution_time') else 0.0,
                "success": True
            }

        except Exception as e:
            logger.error(f"Failed to query codebase: {e}")
            return {
                "query_text": query_text,
                "query_type": query_type,
                "results": [],
                "total_results": 0,
                "execution_time": 0.0,
                "success": False,
                "error": str(e)
            }

    async def query_code(self, query_text: str,
                        query_type: QueryType = QueryType.SEARCH,
                        scope: Optional[str] = None,
                        max_results: int = 10) -> CodeQuery:
        """
        Query the codebase using natural language.
        
        Args:
            query_text: Natural language query
            query_type: Type of query to perform
            scope: Optional scope limitation
            max_results: Maximum number of results
            
        Returns:
            CodeQuery: Query results and insights
        """
        if not self._consciousness_initialized:
            await self.initialize_consciousness()
        
        query_id = f"query_{int(time.time() * 1000)}"
        
        query = CodeQuery(
            query_id=query_id,
            query_text=query_text,
            query_type=query_type,
            consciousness_level=self.consciousness_level,
            scope=scope,
            max_results=max_results
        )
        
        try:
            # Process query based on type
            if query_type == QueryType.SEARCH:
                await self._process_search_query(query)
            elif query_type == QueryType.UNDERSTAND:
                await self._process_understand_query(query)
            elif query_type == QueryType.ANALYZE:
                await self._process_analyze_query(query)
            elif query_type == QueryType.SUGGEST:
                await self._process_suggest_query(query)
            elif query_type == QueryType.NAVIGATE:
                await self._process_navigate_query(query)
            elif query_type == QueryType.EXPLAIN:
                await self._process_explain_query(query)
            
            # Calculate confidence score
            confidence = self._calculate_query_confidence(query)
            query.mark_processed(confidence)
            
            # Store in history
            with self._lock:
                self._query_history.append(query)
                if len(self._query_history) > self.max_query_history:
                    self._query_history = self._query_history[-self.max_query_history:]
            
            logger.debug(f"Processed query {query_id}: {len(query.results)} results, confidence={confidence:.2f}")
            
        except Exception as e:
            logger.error(f"Failed to process query {query_id}: {e}")
            query.mark_processed(0.0)
        
        return query
    
    async def get_code_dependencies(self, file_path: str) -> Dict[str, Any]:
        """
        Get dependency information for a specific file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Dict[str, Any]: Dependency information
        """
        if not self._dependency_graph:
            return {"error": "Dependency graph not initialized"}
        
        return self.dependency_analyzer.get_file_dependencies(
            self._dependency_graph, file_path
        )
    
    async def suggest_improvements(self, file_path: str) -> List[ModificationSuggestion]:
        """
        Suggest improvements for a specific file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            List[ModificationSuggestion]: Improvement suggestions
        """
        if not self.safe_modification_engine:
            return []
        
        try:
            # Get file content and context
            file_content = Path(file_path).read_text()
            
            # Get dependencies for context
            dependencies = await self.get_code_dependencies(file_path)
            
            # Generate suggestions
            suggestions = await self.safe_modification_engine.suggest_improvements(
                file_path, file_content, dependencies
            )
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Failed to suggest improvements for {file_path}: {e}")
            return []
    
    def get_architectural_insights(self) -> Dict[str, Any]:
        """
        Get architectural insights about the codebase.
        
        Returns:
            Dict[str, Any]: Architectural insights
        """
        if not self._consciousness_initialized:
            return {"error": "Consciousness not initialized"}
        
        return self.architectural_knowledge.get_insights()
    
    def get_consciousness_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the consciousness system.
        
        Returns:
            Dict[str, Any]: System statistics
        """
        with self._lock:
            return {
                "consciousness_level": self.consciousness_level.value,
                "initialized": self._consciousness_initialized,
                "indexed_files": len(self._indexed_files),
                "total_queries": len(self._query_history),
                "recent_queries": len([q for q in self._query_history 
                                     if time.time() - q.created_at < 3600]),
                "average_query_time": sum(q.processing_time for q in self._query_history) / 
                                    max(len(self._query_history), 1),
                "average_confidence": sum(q.confidence_score for q in self._query_history) / 
                                    max(len(self._query_history), 1),
                "safe_modifications_enabled": self.enable_safe_modifications,
                "dependency_graph_nodes": len(self._dependency_graph.nodes) if self._dependency_graph else 0
            }
    
    async def _process_search_query(self, query: CodeQuery) -> None:
        """Process a search query."""
        # Use RAG system for semantic search
        search_results = await self.codebase_rag.search_code(
            query.query_text, 
            max_results=query.max_results,
            scope=query.scope
        )
        
        query.results.extend(search_results)
        
        # Add semantic search results
        semantic_results = await self.semantic_index.search(
            query.query_text,
            max_results=query.max_results // 2
        )
        
        # Convert semantic results to CodeSearchResult format
        for result in semantic_results:
            code_result = CodeSearchResult(
                file_path=result.file_path,
                content=result.content,
                relevance_score=result.similarity_score,
                line_number=result.line_number,
                context={"semantic_match": True}
            )
            query.results.append(code_result)
    
    async def _process_understand_query(self, query: CodeQuery) -> None:
        """Process an understanding query."""
        # First get relevant code
        await self._process_search_query(query)
        
        # Generate insights about the code
        for result in query.results[:5]:  # Analyze top 5 results
            try:
                # Get dependencies for context
                deps = await self.get_code_dependencies(result.file_path)
                
                # Generate understanding insights
                insight = f"Code in {result.file_path} appears to handle {self._infer_functionality(result.content)}"
                if deps and "imports" in deps:
                    insight += f" and depends on {len(deps['imports'])} external modules"
                
                query.insights.append(insight)
                
            except Exception as e:
                logger.debug(f"Failed to generate insight for {result.file_path}: {e}")
    
    async def _process_analyze_query(self, query: CodeQuery) -> None:
        """Process an analysis query."""
        # Get relevant code
        await self._process_search_query(query)
        
        # Perform analysis based on query content
        analysis_type = self._determine_analysis_type(query.query_text)
        
        if analysis_type == "complexity":
            await self._analyze_complexity(query)
        elif analysis_type == "patterns":
            await self._analyze_patterns(query)
        elif analysis_type == "issues":
            await self._analyze_issues(query)
        else:
            await self._analyze_general(query)
    
    async def _process_suggest_query(self, query: CodeQuery) -> None:
        """Process a suggestion query."""
        if not self.safe_modification_engine:
            query.insights.append("Safe modification engine not enabled")
            return
        
        # Get relevant code
        await self._process_search_query(query)
        
        # Generate suggestions for top results
        for result in query.results[:3]:  # Suggest for top 3 results
            try:
                suggestions = await self.suggest_improvements(result.file_path)
                query.suggestions.extend(suggestions)
                
            except Exception as e:
                logger.debug(f"Failed to generate suggestions for {result.file_path}: {e}")
    
    async def _process_navigate_query(self, query: CodeQuery) -> None:
        """Process a navigation query."""
        # Extract navigation intent (e.g., "find callers of function X")
        navigation_type = self._determine_navigation_type(query.query_text)
        
        if navigation_type == "callers":
            await self._find_callers(query)
        elif navigation_type == "dependencies":
            await self._find_dependencies(query)
        elif navigation_type == "related":
            await self._find_related_code(query)
        else:
            await self._process_search_query(query)  # Fallback to search
    
    async def _process_explain_query(self, query: CodeQuery) -> None:
        """Process an explanation query."""
        # Get relevant code
        await self._process_search_query(query)
        
        # Generate explanations
        for result in query.results[:3]:  # Explain top 3 results
            try:
                explanation = self._generate_code_explanation(result.content, result.file_path)
                query.insights.append(explanation)
                
            except Exception as e:
                logger.debug(f"Failed to generate explanation for {result.file_path}: {e}")
    
    def _calculate_query_confidence(self, query: CodeQuery) -> float:
        """Calculate confidence score for query results."""
        if not query.results:
            return 0.0
        
        # Base confidence on result relevance scores
        avg_relevance = sum(r.relevance_score for r in query.results) / len(query.results)
        
        # Adjust based on query type and results count
        type_multiplier = {
            QueryType.SEARCH: 1.0,
            QueryType.UNDERSTAND: 0.8,
            QueryType.ANALYZE: 0.7,
            QueryType.SUGGEST: 0.6,
            QueryType.NAVIGATE: 0.9,
            QueryType.EXPLAIN: 0.8
        }.get(query.query_type, 0.7)
        
        # Adjust based on number of results
        result_multiplier = min(len(query.results) / query.max_results, 1.0)
        
        return avg_relevance * type_multiplier * result_multiplier
    
    def _infer_functionality(self, code_content: str) -> str:
        """Infer functionality from code content."""
        # Simplified functionality inference
        content_lower = code_content.lower()
        
        if "def " in content_lower and "class " in content_lower:
            return "class and method definitions"
        elif "def " in content_lower:
            return "function definitions"
        elif "class " in content_lower:
            return "class definitions"
        elif "import " in content_lower:
            return "module imports and setup"
        elif "if __name__" in content_lower:
            return "main execution logic"
        else:
            return "general code logic"
    
    def _determine_analysis_type(self, query_text: str) -> str:
        """Determine type of analysis requested."""
        query_lower = query_text.lower()
        
        if any(word in query_lower for word in ["complex", "complexity", "cyclomatic"]):
            return "complexity"
        elif any(word in query_lower for word in ["pattern", "design", "architecture"]):
            return "patterns"
        elif any(word in query_lower for word in ["issue", "problem", "bug", "error"]):
            return "issues"
        else:
            return "general"
    
    def _determine_navigation_type(self, query_text: str) -> str:
        """Determine type of navigation requested."""
        query_lower = query_text.lower()
        
        if any(word in query_lower for word in ["caller", "call", "invoke", "use"]):
            return "callers"
        elif any(word in query_lower for word in ["depend", "import", "require"]):
            return "dependencies"
        elif any(word in query_lower for word in ["related", "similar", "connect"]):
            return "related"
        else:
            return "search"
    
    async def _analyze_complexity(self, query: CodeQuery) -> None:
        """Analyze code complexity."""
        for result in query.results[:3]:
            # Simple complexity analysis
            lines = result.content.split('\n')
            complexity_score = len([line for line in lines if any(keyword in line.lower() 
                                  for keyword in ['if', 'for', 'while', 'try', 'except'])])
            
            query.insights.append(f"Complexity analysis for {result.file_path}: "
                                f"{complexity_score} decision points in {len(lines)} lines")
    
    async def _analyze_patterns(self, query: CodeQuery) -> None:
        """Analyze code patterns."""
        patterns_found = []
        
        for result in query.results:
            content_lower = result.content.lower()
            
            # Detect common patterns
            if "singleton" in content_lower or "__new__" in content_lower:
                patterns_found.append(f"Singleton pattern in {result.file_path}")
            if "factory" in content_lower:
                patterns_found.append(f"Factory pattern in {result.file_path}")
            if "observer" in content_lower or "subscribe" in content_lower:
                patterns_found.append(f"Observer pattern in {result.file_path}")
        
        if patterns_found:
            query.insights.extend(patterns_found)
        else:
            query.insights.append("No common design patterns detected in the analyzed code")
    
    async def _analyze_issues(self, query: CodeQuery) -> None:
        """Analyze potential code issues."""
        issues_found = []
        
        for result in query.results:
            lines = result.content.split('\n')
            
            # Simple issue detection
            for i, line in enumerate(lines):
                line_lower = line.lower()
                if "todo" in line_lower or "fixme" in line_lower:
                    issues_found.append(f"TODO/FIXME in {result.file_path}:{i+1}")
                if "print(" in line and "debug" in line_lower:
                    issues_found.append(f"Debug print statement in {result.file_path}:{i+1}")
        
        if issues_found:
            query.insights.extend(issues_found[:10])  # Limit to 10 issues
        else:
            query.insights.append("No obvious issues detected in the analyzed code")
    
    async def _analyze_general(self, query: CodeQuery) -> None:
        """Perform general code analysis."""
        total_lines = sum(len(result.content.split('\n')) for result in query.results)
        total_files = len(query.results)
        
        query.insights.append(f"General analysis: Found {total_files} relevant files "
                            f"with {total_lines} total lines of code")
    
    async def _find_callers(self, query: CodeQuery) -> None:
        """Find callers of a function or method."""
        # Extract function name from query
        # This is simplified - could be enhanced with better NLP
        words = query.query_text.split()
        function_name = None
        
        for i, word in enumerate(words):
            if word.lower() in ["function", "method"] and i + 1 < len(words):
                function_name = words[i + 1]
                break
        
        if function_name:
            # Search for calls to this function
            call_query = f"{function_name}("
            search_results = await self.codebase_rag.search_code(call_query, max_results=20)
            query.results.extend(search_results)
            
            query.insights.append(f"Found {len(search_results)} potential callers of {function_name}")
    
    async def _find_dependencies(self, query: CodeQuery) -> None:
        """Find dependencies for code."""
        # First search for relevant code
        await self._process_search_query(query)
        
        # Then get dependencies for each result
        for result in query.results[:5]:
            deps = await self.get_code_dependencies(result.file_path)
            if deps and "imports" in deps:
                query.insights.append(f"Dependencies for {result.file_path}: "
                                    f"{', '.join(deps['imports'][:5])}")
    
    async def _find_related_code(self, query: CodeQuery) -> None:
        """Find related code."""
        # Use semantic search to find related code
        await self._process_search_query(query)
        
        # Add insight about relationships
        if query.results:
            query.insights.append(f"Found {len(query.results)} related code sections")
    
    def _generate_code_explanation(self, code_content: str, file_path: str) -> str:
        """Generate explanation for code content."""
        lines = code_content.split('\n')
        
        # Simple explanation generation
        explanation_parts = []
        
        if "class " in code_content:
            class_count = code_content.count("class ")
            explanation_parts.append(f"defines {class_count} class(es)")
        
        if "def " in code_content:
            func_count = code_content.count("def ")
            explanation_parts.append(f"contains {func_count} function(s)")
        
        if "import " in code_content:
            import_count = len([line for line in lines if line.strip().startswith("import") 
                              or line.strip().startswith("from")])
            explanation_parts.append(f"imports {import_count} module(s)")
        
        if explanation_parts:
            return f"Code in {file_path} {', '.join(explanation_parts)}"
        else:
            return f"Code in {file_path} contains {len(lines)} lines of implementation logic"
