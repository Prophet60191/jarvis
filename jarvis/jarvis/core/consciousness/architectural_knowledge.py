"""
Architectural Knowledge System

Maintains understanding of system architecture, design patterns,
and structural relationships within the codebase.
"""

import time
import logging
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import threading
import json

logger = logging.getLogger(__name__)

class ArchitecturalPattern(Enum):
    """Types of architectural patterns."""
    MVC = "mvc"
    MVVM = "mvvm"
    LAYERED = "layered"
    MICROSERVICES = "microservices"
    PLUGIN = "plugin"
    OBSERVER = "observer"
    FACTORY = "factory"
    SINGLETON = "singleton"
    ADAPTER = "adapter"
    FACADE = "facade"

class ComponentType(Enum):
    """Types of architectural components."""
    CONTROLLER = "controller"
    MODEL = "model"
    VIEW = "view"
    SERVICE = "service"
    REPOSITORY = "repository"
    UTILITY = "utility"
    CONFIGURATION = "configuration"
    INTERFACE = "interface"
    PLUGIN = "plugin"
    MIDDLEWARE = "middleware"

@dataclass
class ArchitecturalComponent:
    """Represents an architectural component."""
    component_id: str
    name: str
    component_type: ComponentType
    file_path: str
    
    # Relationships
    dependencies: Set[str] = field(default_factory=set)
    dependents: Set[str] = field(default_factory=set)
    interfaces: Set[str] = field(default_factory=set)
    
    # Metadata
    description: str = ""
    patterns: Set[ArchitecturalPattern] = field(default_factory=set)
    responsibilities: List[str] = field(default_factory=list)
    
    # Metrics
    complexity_score: float = 0.0
    coupling_score: float = 0.0
    cohesion_score: float = 0.0
    
    # Timestamps
    created_at: float = field(default_factory=time.time)
    last_analyzed: float = field(default_factory=time.time)

@dataclass
class ArchitecturalLayer:
    """Represents an architectural layer."""
    layer_id: str
    name: str
    level: int  # 0 = lowest level
    components: Set[str] = field(default_factory=set)
    description: str = ""

class ArchitecturalKnowledge:
    """
    System for maintaining architectural knowledge and understanding.
    
    This component analyzes and maintains knowledge about the system's
    architecture, design patterns, and structural relationships.
    """
    
    def __init__(self, codebase_path: Path):
        """
        Initialize the architectural knowledge system.
        
        Args:
            codebase_path: Path to the codebase to analyze
        """
        self.codebase_path = codebase_path
        
        # Knowledge storage
        self._components: Dict[str, ArchitecturalComponent] = {}
        self._layers: Dict[str, ArchitecturalLayer] = {}
        self._patterns: Dict[str, Set[str]] = {}  # pattern -> component_ids
        
        # Analysis state
        self._last_analysis: Optional[float] = None
        self._analysis_version = 1
        
        # Configuration
        self.auto_detect_patterns = True
        self.complexity_threshold = 0.7
        self.coupling_threshold = 0.8
        
        # Thread safety
        self._lock = threading.RLock()
        
        logger.info(f"ArchitecturalKnowledge initialized for {codebase_path}")
    
    def analyze_architecture(self) -> Dict[str, Any]:
        """
        Analyze the system architecture.
        
        Returns:
            Dict[str, Any]: Analysis results
        """
        with self._lock:
            logger.info("Starting architectural analysis...")
            
            # Clear previous analysis
            self._components.clear()
            self._layers.clear()
            self._patterns.clear()
            
            # Analyze components
            self._analyze_components()
            
            # Detect patterns
            if self.auto_detect_patterns:
                self._detect_patterns()
            
            # Analyze layers
            self._analyze_layers()
            
            # Calculate metrics
            metrics = self._calculate_metrics()
            
            self._last_analysis = time.time()
            
            logger.info(f"Architectural analysis complete: {len(self._components)} components, "
                       f"{len(self._layers)} layers, {len(self._patterns)} patterns")
            
            return {
                "components": len(self._components),
                "layers": len(self._layers),
                "patterns": len(self._patterns),
                "metrics": metrics,
                "analysis_time": self._last_analysis
            }
    
    def get_component(self, component_id: str) -> Optional[ArchitecturalComponent]:
        """
        Get an architectural component by ID.
        
        Args:
            component_id: Component identifier
            
        Returns:
            Optional[ArchitecturalComponent]: Component if found
        """
        with self._lock:
            return self._components.get(component_id)
    
    def get_components_by_type(self, component_type: ComponentType) -> List[ArchitecturalComponent]:
        """
        Get components by type.
        
        Args:
            component_type: Type of components to retrieve
            
        Returns:
            List[ArchitecturalComponent]: Components of the specified type
        """
        with self._lock:
            return [
                comp for comp in self._components.values()
                if comp.component_type == component_type
            ]
    
    def get_components_by_pattern(self, pattern: ArchitecturalPattern) -> List[ArchitecturalComponent]:
        """
        Get components that implement a specific pattern.
        
        Args:
            pattern: Architectural pattern
            
        Returns:
            List[ArchitecturalComponent]: Components implementing the pattern
        """
        with self._lock:
            pattern_components = self._patterns.get(pattern.value, set())
            return [
                self._components[comp_id] for comp_id in pattern_components
                if comp_id in self._components
            ]
    
    def get_layer(self, layer_id: str) -> Optional[ArchitecturalLayer]:
        """
        Get an architectural layer by ID.
        
        Args:
            layer_id: Layer identifier
            
        Returns:
            Optional[ArchitecturalLayer]: Layer if found
        """
        with self._lock:
            return self._layers.get(layer_id)
    
    def get_dependency_graph(self) -> Dict[str, List[str]]:
        """
        Get the component dependency graph.
        
        Returns:
            Dict[str, List[str]]: Dependency graph (component -> dependencies)
        """
        with self._lock:
            return {
                comp_id: list(comp.dependencies)
                for comp_id, comp in self._components.items()
            }
    
    def find_architectural_violations(self) -> List[Dict[str, Any]]:
        """
        Find architectural violations and anti-patterns.
        
        Returns:
            List[Dict[str, Any]]: List of violations found
        """
        violations = []
        
        with self._lock:
            # Check for high coupling
            for comp_id, component in self._components.items():
                if component.coupling_score > self.coupling_threshold:
                    violations.append({
                        "type": "high_coupling",
                        "component": comp_id,
                        "score": component.coupling_score,
                        "description": f"Component {component.name} has high coupling"
                    })
            
            # Check for high complexity
            for comp_id, component in self._components.items():
                if component.complexity_score > self.complexity_threshold:
                    violations.append({
                        "type": "high_complexity",
                        "component": comp_id,
                        "score": component.complexity_score,
                        "description": f"Component {component.name} has high complexity"
                    })
            
            # Check for circular dependencies
            circular_deps = self._find_circular_dependencies()
            for cycle in circular_deps:
                violations.append({
                    "type": "circular_dependency",
                    "components": cycle,
                    "description": f"Circular dependency detected: {' -> '.join(cycle)}"
                })
        
        return violations
    
    def get_architectural_insights(self) -> Dict[str, Any]:
        """
        Get architectural insights and recommendations.
        
        Returns:
            Dict[str, Any]: Architectural insights
        """
        with self._lock:
            insights = {
                "summary": {
                    "total_components": len(self._components),
                    "total_layers": len(self._layers),
                    "detected_patterns": list(self._patterns.keys())
                },
                "metrics": self._calculate_metrics(),
                "violations": self.find_architectural_violations(),
                "recommendations": self._generate_recommendations()
            }
            
            return insights
    
    def _analyze_components(self) -> None:
        """Analyze architectural components."""
        # Find all Python files
        for file_path in self.codebase_path.rglob("*.py"):
            if self._should_analyze_file(file_path):
                self._analyze_file_component(file_path)
    
    def _should_analyze_file(self, file_path: Path) -> bool:
        """Check if a file should be analyzed."""
        exclude_patterns = {"__pycache__", ".git", ".venv", "test_", "tests/"}
        
        for pattern in exclude_patterns:
            if pattern in str(file_path):
                return False
        
        return True
    
    def _analyze_file_component(self, file_path: Path) -> None:
        """Analyze a single file as a component."""
        try:
            # Determine component type based on file path and name
            component_type = self._determine_component_type(file_path)
            
            # Create component
            component_id = str(file_path.relative_to(self.codebase_path))
            component = ArchitecturalComponent(
                component_id=component_id,
                name=file_path.stem,
                component_type=component_type,
                file_path=str(file_path)
            )
            
            # Analyze file content for dependencies and patterns
            self._analyze_file_content(component, file_path)
            
            self._components[component_id] = component
            
        except Exception as e:
            logger.warning(f"Failed to analyze component {file_path}: {e}")
    
    def _determine_component_type(self, file_path: Path) -> ComponentType:
        """Determine component type based on file path and name."""
        path_str = str(file_path).lower()
        name = file_path.stem.lower()
        
        # Check by path patterns
        if "controller" in path_str or "controllers" in path_str:
            return ComponentType.CONTROLLER
        elif "model" in path_str or "models" in path_str:
            return ComponentType.MODEL
        elif "view" in path_str or "views" in path_str or "ui" in path_str:
            return ComponentType.VIEW
        elif "service" in path_str or "services" in path_str:
            return ComponentType.SERVICE
        elif "repository" in path_str or "repositories" in path_str:
            return ComponentType.REPOSITORY
        elif "plugin" in path_str or "plugins" in path_str:
            return ComponentType.PLUGIN
        elif "config" in path_str or "configuration" in path_str:
            return ComponentType.CONFIGURATION
        elif "util" in path_str or "utils" in path_str or "helper" in path_str:
            return ComponentType.UTILITY
        elif "interface" in name or "abstract" in name:
            return ComponentType.INTERFACE
        elif "middleware" in path_str:
            return ComponentType.MIDDLEWARE
        else:
            return ComponentType.SERVICE  # Default
    
    def _analyze_file_content(self, component: ArchitecturalComponent, file_path: Path) -> None:
        """Analyze file content for dependencies and patterns."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Simple analysis - could be enhanced with AST parsing
            lines = content.split('\n')
            
            # Count imports as dependencies
            for line in lines:
                line = line.strip()
                if line.startswith('from ') or line.startswith('import '):
                    # Extract module name
                    if 'from ' in line:
                        module = line.split('from ')[1].split(' import')[0].strip()
                    else:
                        module = line.split('import ')[1].split(' as')[0].split(',')[0].strip()
                    
                    if module and not module.startswith('.'):
                        component.dependencies.add(module)
            
            # Calculate basic complexity (lines of code)
            non_empty_lines = [line for line in lines if line.strip()]
            component.complexity_score = min(len(non_empty_lines) / 1000.0, 1.0)
            
            # Calculate coupling (number of dependencies)
            component.coupling_score = min(len(component.dependencies) / 20.0, 1.0)
            
        except Exception as e:
            logger.warning(f"Failed to analyze file content {file_path}: {e}")
    
    def _detect_patterns(self) -> None:
        """Detect architectural patterns in components."""
        # Simple pattern detection based on naming and structure
        for comp_id, component in self._components.items():
            patterns = set()
            
            # Detect patterns based on component type and structure
            if component.component_type == ComponentType.PLUGIN:
                patterns.add(ArchitecturalPattern.PLUGIN)
            
            if "factory" in component.name.lower():
                patterns.add(ArchitecturalPattern.FACTORY)
            
            if "singleton" in component.name.lower():
                patterns.add(ArchitecturalPattern.SINGLETON)
            
            if "adapter" in component.name.lower():
                patterns.add(ArchitecturalPattern.ADAPTER)
            
            if "facade" in component.name.lower():
                patterns.add(ArchitecturalPattern.FACADE)
            
            # Update component patterns
            component.patterns = patterns
            
            # Update pattern index
            for pattern in patterns:
                if pattern.value not in self._patterns:
                    self._patterns[pattern.value] = set()
                self._patterns[pattern.value].add(comp_id)
    
    def _analyze_layers(self) -> None:
        """Analyze architectural layers."""
        # Create basic layers based on component types
        layers = {
            "presentation": ArchitecturalLayer("presentation", "Presentation Layer", 3),
            "service": ArchitecturalLayer("service", "Service Layer", 2),
            "data": ArchitecturalLayer("data", "Data Layer", 1),
            "utility": ArchitecturalLayer("utility", "Utility Layer", 0)
        }
        
        # Assign components to layers
        for comp_id, component in self._components.items():
            if component.component_type in [ComponentType.VIEW, ComponentType.CONTROLLER]:
                layers["presentation"].components.add(comp_id)
            elif component.component_type in [ComponentType.SERVICE, ComponentType.MIDDLEWARE]:
                layers["service"].components.add(comp_id)
            elif component.component_type in [ComponentType.MODEL, ComponentType.REPOSITORY]:
                layers["data"].components.add(comp_id)
            else:
                layers["utility"].components.add(comp_id)
        
        self._layers = layers
    
    def _calculate_metrics(self) -> Dict[str, Any]:
        """Calculate architectural metrics."""
        if not self._components:
            return {}
        
        # Calculate average metrics
        avg_complexity = sum(c.complexity_score for c in self._components.values()) / len(self._components)
        avg_coupling = sum(c.coupling_score for c in self._components.values()) / len(self._components)
        
        # Count components by type
        type_counts = {}
        for component in self._components.values():
            comp_type = component.component_type.value
            type_counts[comp_type] = type_counts.get(comp_type, 0) + 1
        
        return {
            "average_complexity": avg_complexity,
            "average_coupling": avg_coupling,
            "component_type_distribution": type_counts,
            "total_dependencies": sum(len(c.dependencies) for c in self._components.values())
        }
    
    def _find_circular_dependencies(self) -> List[List[str]]:
        """Find circular dependencies using DFS."""
        visited = set()
        rec_stack = set()
        cycles = []
        
        def dfs(comp_id: str, path: List[str]) -> None:
            if comp_id in rec_stack:
                # Found a cycle
                cycle_start = path.index(comp_id)
                cycle = path[cycle_start:] + [comp_id]
                cycles.append(cycle)
                return
            
            if comp_id in visited:
                return
            
            visited.add(comp_id)
            rec_stack.add(comp_id)
            path.append(comp_id)
            
            # Visit dependencies
            if comp_id in self._components:
                for dep in self._components[comp_id].dependencies:
                    if dep in self._components:  # Only check internal dependencies
                        dfs(dep, path.copy())
            
            rec_stack.remove(comp_id)
        
        # Run DFS from each component
        for comp_id in self._components:
            if comp_id not in visited:
                dfs(comp_id, [])
        
        return cycles
    
    def _generate_recommendations(self) -> List[str]:
        """Generate architectural recommendations."""
        recommendations = []
        
        # Check for high coupling components
        high_coupling = [
            c for c in self._components.values()
            if c.coupling_score > self.coupling_threshold
        ]
        
        if high_coupling:
            recommendations.append(
                f"Consider reducing coupling for {len(high_coupling)} components with high coupling scores"
            )
        
        # Check for missing patterns
        if ArchitecturalPattern.FACADE.value not in self._patterns:
            recommendations.append("Consider implementing facade pattern for complex subsystems")
        
        # Check layer violations
        violations = self.find_architectural_violations()
        if violations:
            recommendations.append(f"Address {len(violations)} architectural violations found")
        
        return recommendations
