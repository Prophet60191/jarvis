"""
Dependency Analyzer

Analyzes and maps code dependencies and relationships within the codebase,
providing insights into system architecture and component interactions.
"""

import time
import logging
import ast
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import threading

logger = logging.getLogger(__name__)

class DependencyType(Enum):
    """Types of dependencies."""
    IMPORT = "import"
    INHERITANCE = "inheritance"
    COMPOSITION = "composition"
    FUNCTION_CALL = "function_call"
    METHOD_CALL = "method_call"
    VARIABLE_REFERENCE = "variable_reference"

@dataclass
class Dependency:
    """Represents a dependency relationship."""
    source: str
    target: str
    dependency_type: DependencyType
    strength: float = 1.0
    
    # Location information
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    
    # Metadata
    created_at: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class DependencyGraph:
    """Represents a dependency graph."""
    nodes: Set[str] = field(default_factory=set)
    edges: List[Dependency] = field(default_factory=list)
    
    def add_dependency(self, dependency: Dependency) -> None:
        """Add a dependency to the graph."""
        self.nodes.add(dependency.source)
        self.nodes.add(dependency.target)
        self.edges.append(dependency)
    
    def get_dependencies(self, node: str) -> List[Dependency]:
        """Get all dependencies for a node."""
        return [dep for dep in self.edges if dep.source == node]
    
    def get_dependents(self, node: str) -> List[Dependency]:
        """Get all dependents of a node."""
        return [dep for dep in self.edges if dep.target == node]

class DependencyAnalyzer:
    """
    Analyzes code dependencies and relationships.
    
    This component examines the codebase to understand how different
    components depend on each other and interact.
    """
    
    def __init__(self, codebase_path: Path):
        """
        Initialize the dependency analyzer.
        
        Args:
            codebase_path: Path to the codebase to analyze
        """
        self.codebase_path = codebase_path
        
        # Analysis results
        self._dependency_graph = DependencyGraph()
        self._module_dependencies: Dict[str, Set[str]] = {}
        self._circular_dependencies: List[List[str]] = []
        
        # Configuration
        self.supported_extensions = {".py", ".js", ".ts", ".java"}
        self.exclude_patterns = {"__pycache__", ".git", ".venv", "node_modules"}
        
        # Thread safety
        self._lock = threading.RLock()
        
        logger.info(f"DependencyAnalyzer initialized for {codebase_path}")
    
    def analyze_dependencies(self) -> DependencyGraph:
        """
        Analyze dependencies in the codebase.
        
        Returns:
            DependencyGraph: Complete dependency graph
        """
        with self._lock:
            logger.info("Starting dependency analysis...")
            
            # Find all code files
            code_files = self._find_code_files()
            
            # Analyze each file
            for file_path in code_files:
                try:
                    self._analyze_file(file_path)
                except Exception as e:
                    logger.warning(f"Failed to analyze {file_path}: {e}")
            
            # Detect circular dependencies
            self._detect_circular_dependencies()
            
            logger.info(f"Dependency analysis complete: {len(self._dependency_graph.nodes)} nodes, "
                       f"{len(self._dependency_graph.edges)} edges")
            
            return self._dependency_graph
    
    def get_dependency_graph(self) -> DependencyGraph:
        """Get the current dependency graph."""
        with self._lock:
            return self._dependency_graph
    
    def get_circular_dependencies(self) -> List[List[str]]:
        """Get detected circular dependencies."""
        with self._lock:
            return self._circular_dependencies.copy()
    
    def get_module_dependencies(self, module_name: str) -> Set[str]:
        """Get dependencies for a specific module."""
        with self._lock:
            return self._module_dependencies.get(module_name, set()).copy()
    
    def get_dependency_statistics(self) -> Dict[str, Any]:
        """Get dependency analysis statistics."""
        with self._lock:
            # Calculate statistics
            total_nodes = len(self._dependency_graph.nodes)
            total_edges = len(self._dependency_graph.edges)
            
            # Dependency type distribution
            type_counts = {}
            for edge in self._dependency_graph.edges:
                dep_type = edge.dependency_type.value
                type_counts[dep_type] = type_counts.get(dep_type, 0) + 1
            
            # Calculate complexity metrics
            avg_dependencies = 0
            max_dependencies = 0
            
            if total_nodes > 0:
                dependency_counts = []
                for node in self._dependency_graph.nodes:
                    deps = len(self._dependency_graph.get_dependencies(node))
                    dependency_counts.append(deps)
                    max_dependencies = max(max_dependencies, deps)
                
                avg_dependencies = sum(dependency_counts) / len(dependency_counts)
            
            return {
                "total_nodes": total_nodes,
                "total_edges": total_edges,
                "circular_dependencies": len(self._circular_dependencies),
                "dependency_type_distribution": type_counts,
                "average_dependencies_per_node": avg_dependencies,
                "max_dependencies_per_node": max_dependencies,
                "modules_analyzed": len(self._module_dependencies)
            }
    
    def _find_code_files(self) -> List[Path]:
        """Find all code files in the codebase."""
        code_files = []
        
        for file_path in self.codebase_path.rglob("*"):
            # Skip directories
            if file_path.is_dir():
                continue
            
            # Skip excluded patterns
            if any(pattern in str(file_path) for pattern in self.exclude_patterns):
                continue
            
            # Check file extension
            if file_path.suffix in self.supported_extensions:
                code_files.append(file_path)
        
        return code_files
    
    def _analyze_file(self, file_path: Path) -> None:
        """Analyze dependencies in a single file."""
        if file_path.suffix == ".py":
            self._analyze_python_file(file_path)
        else:
            # Generic analysis for other file types
            self._analyze_generic_file(file_path)
    
    def _analyze_python_file(self, file_path: Path) -> None:
        """Analyze dependencies in a Python file."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Parse AST
            tree = ast.parse(content)
            
            # Get module name
            module_name = self._get_module_name(file_path)
            
            # Initialize module dependencies
            if module_name not in self._module_dependencies:
                self._module_dependencies[module_name] = set()
            
            # Analyze imports
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        self._add_import_dependency(module_name, alias.name, file_path, node.lineno)
                
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        self._add_import_dependency(module_name, node.module, file_path, node.lineno)
                
                elif isinstance(node, ast.ClassDef):
                    # Analyze inheritance
                    for base in node.bases:
                        if isinstance(base, ast.Name):
                            self._add_inheritance_dependency(module_name, base.id, file_path, node.lineno)
                
                elif isinstance(node, ast.FunctionDef):
                    # Analyze function calls within the function
                    for child in ast.walk(node):
                        if isinstance(child, ast.Call):
                            if isinstance(child.func, ast.Name):
                                self._add_function_call_dependency(module_name, child.func.id, file_path, child.lineno)
        
        except Exception as e:
            logger.warning(f"Failed to parse Python file {file_path}: {e}")
    
    def _analyze_generic_file(self, file_path: Path) -> None:
        """Generic analysis for non-Python files."""
        # Simple text-based analysis
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            module_name = self._get_module_name(file_path)
            
            # Look for import-like patterns
            import_patterns = [
                r'import\s+([a-zA-Z_][a-zA-Z0-9_]*)',
                r'require\s*\(\s*["\']([^"\']+)["\']\s*\)',
                r'from\s+([a-zA-Z_][a-zA-Z0-9_]*)\s+import'
            ]
            
            import re
            for pattern in import_patterns:
                matches = re.findall(pattern, content)
                for match in matches:
                    self._add_import_dependency(module_name, match, file_path, 0)
        
        except Exception as e:
            logger.warning(f"Failed to analyze generic file {file_path}: {e}")
    
    def _get_module_name(self, file_path: Path) -> str:
        """Get module name from file path."""
        # Convert file path to module name
        relative_path = file_path.relative_to(self.codebase_path)
        module_parts = list(relative_path.parts[:-1])  # Exclude filename
        
        # Add filename without extension
        filename = relative_path.stem
        if filename != "__init__":
            module_parts.append(filename)
        
        return ".".join(module_parts) if module_parts else filename
    
    def _add_import_dependency(self, source: str, target: str, file_path: Path, line_number: int) -> None:
        """Add an import dependency."""
        dependency = Dependency(
            source=source,
            target=target,
            dependency_type=DependencyType.IMPORT,
            file_path=str(file_path),
            line_number=line_number
        )
        
        self._dependency_graph.add_dependency(dependency)
        self._module_dependencies[source].add(target)
    
    def _add_inheritance_dependency(self, source: str, target: str, file_path: Path, line_number: int) -> None:
        """Add an inheritance dependency."""
        dependency = Dependency(
            source=source,
            target=target,
            dependency_type=DependencyType.INHERITANCE,
            strength=0.9,  # High strength for inheritance
            file_path=str(file_path),
            line_number=line_number
        )
        
        self._dependency_graph.add_dependency(dependency)
        self._module_dependencies[source].add(target)
    
    def _add_function_call_dependency(self, source: str, target: str, file_path: Path, line_number: int) -> None:
        """Add a function call dependency."""
        dependency = Dependency(
            source=source,
            target=target,
            dependency_type=DependencyType.FUNCTION_CALL,
            strength=0.3,  # Lower strength for function calls
            file_path=str(file_path),
            line_number=line_number
        )
        
        self._dependency_graph.add_dependency(dependency)
    
    def _detect_circular_dependencies(self) -> None:
        """Detect circular dependencies using DFS."""
        visited = set()
        rec_stack = set()
        cycles = []
        
        def dfs(node: str, path: List[str]) -> None:
            if node in rec_stack:
                # Found a cycle
                cycle_start = path.index(node)
                cycle = path[cycle_start:] + [node]
                cycles.append(cycle)
                return
            
            if node in visited:
                return
            
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            
            # Visit dependencies
            dependencies = self._dependency_graph.get_dependencies(node)
            for dep in dependencies:
                dfs(dep.target, path.copy())
            
            rec_stack.remove(node)
        
        # Run DFS from each node
        for node in self._dependency_graph.nodes:
            if node not in visited:
                dfs(node, [])
        
        self._circular_dependencies = cycles
