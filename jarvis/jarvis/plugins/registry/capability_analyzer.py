"""
Plugin Capability Analyzer

Automatically analyzes plugin capabilities through code inspection,
metadata analysis, and behavioral observation.
"""

import re
import ast
import inspect
import logging
from typing import Dict, List, Set, Optional, Any, Type
from dataclasses import dataclass
from enum import Enum
import threading

from ..base import PluginBase
from langchain_core.tools import BaseTool

logger = logging.getLogger(__name__)

class CapabilityCategory(Enum):
    """Categories of plugin capabilities."""
    DATA_OPERATIONS = "data_operations"
    FILE_OPERATIONS = "file_operations"
    WEB_OPERATIONS = "web_operations"
    SYSTEM_OPERATIONS = "system_operations"
    USER_INTERACTION = "user_interaction"
    COMMUNICATION = "communication"
    ANALYSIS = "analysis"
    AUTOMATION = "automation"
    INTEGRATION = "integration"
    SECURITY = "security"

@dataclass
class CapabilitySignature:
    """Signature pattern for capability detection."""
    name: str
    category: CapabilityCategory
    keywords: List[str]
    patterns: List[str]  # Regex patterns
    imports: List[str]   # Import patterns
    methods: List[str]   # Method name patterns
    weight: float = 1.0  # Confidence weight

class CapabilityAnalyzer:
    """
    Analyzes plugin capabilities through multiple detection methods.
    
    This component automatically identifies what capabilities a plugin provides
    by analyzing its code, metadata, tools, and behavior patterns.
    """
    
    def __init__(self):
        """Initialize the capability analyzer."""
        self._capability_signatures = self._initialize_capability_signatures()
        self._lock = threading.RLock()
        
        # Analysis configuration
        self.confidence_threshold = 0.3
        self.max_analysis_depth = 3
        
        logger.info("CapabilityAnalyzer initialized")
    
    def analyze_plugin_capabilities(self, plugin_instance: PluginBase) -> Set[str]:
        """
        Analyze capabilities of a plugin instance.
        
        Args:
            plugin_instance: Plugin instance to analyze
            
        Returns:
            Set[str]: Set of detected capabilities
        """
        capabilities = set()
        
        with self._lock:
            try:
                # Method 1: Analyze plugin metadata
                metadata_capabilities = self._analyze_metadata_capabilities(plugin_instance)
                capabilities.update(metadata_capabilities)
                
                # Method 2: Analyze plugin tools
                tool_capabilities = self._analyze_tool_capabilities(plugin_instance)
                capabilities.update(tool_capabilities)
                
                # Method 3: Analyze plugin code
                code_capabilities = self._analyze_code_capabilities(plugin_instance)
                capabilities.update(code_capabilities)
                
                # Method 4: Analyze plugin class structure
                class_capabilities = self._analyze_class_capabilities(plugin_instance)
                capabilities.update(class_capabilities)
                
                logger.debug(f"Detected capabilities for {plugin_instance.__class__.__name__}: {capabilities}")
                
            except Exception as e:
                logger.error(f"Error analyzing plugin capabilities: {e}")
        
        return capabilities
    
    def categorize_capabilities(self, capabilities: Set[str]) -> Dict[CapabilityCategory, List[str]]:
        """
        Categorize capabilities into functional groups.
        
        Args:
            capabilities: Set of capability names
            
        Returns:
            Dict[CapabilityCategory, List[str]]: Capabilities grouped by category
        """
        categorized = {category: [] for category in CapabilityCategory}
        
        for capability in capabilities:
            category = self._determine_capability_category(capability)
            categorized[category].append(capability)
        
        # Remove empty categories
        return {cat: caps for cat, caps in categorized.items() if caps}
    
    def suggest_missing_capabilities(self, plugin_instance: PluginBase,
                                   existing_capabilities: Set[str]) -> List[str]:
        """
        Suggest potentially missing capabilities based on analysis.
        
        Args:
            plugin_instance: Plugin instance
            existing_capabilities: Currently detected capabilities
            
        Returns:
            List[str]: Suggested additional capabilities
        """
        suggestions = []
        
        try:
            # Analyze for weak signals that might indicate additional capabilities
            weak_signals = self._detect_weak_capability_signals(plugin_instance)
            
            for capability, confidence in weak_signals.items():
                if (capability not in existing_capabilities and 
                    confidence > self.confidence_threshold * 0.5):  # Lower threshold for suggestions
                    suggestions.append(capability)
            
            # Sort by confidence
            suggestions.sort(key=lambda cap: weak_signals.get(cap, 0), reverse=True)
            
        except Exception as e:
            logger.error(f"Error suggesting missing capabilities: {e}")
        
        return suggestions[:5]  # Return top 5 suggestions
    
    def validate_capability_claims(self, plugin_instance: PluginBase,
                                 claimed_capabilities: Set[str]) -> Dict[str, float]:
        """
        Validate claimed capabilities against actual analysis.
        
        Args:
            plugin_instance: Plugin instance
            claimed_capabilities: Capabilities claimed by the plugin
            
        Returns:
            Dict[str, float]: Validation confidence for each claimed capability
        """
        validation_results = {}
        
        try:
            # Analyze actual capabilities
            detected_capabilities = self.analyze_plugin_capabilities(plugin_instance)
            
            for capability in claimed_capabilities:
                if capability in detected_capabilities:
                    validation_results[capability] = 1.0  # Fully validated
                else:
                    # Check for weak signals
                    weak_signals = self._detect_weak_capability_signals(plugin_instance)
                    validation_results[capability] = weak_signals.get(capability, 0.0)
            
        except Exception as e:
            logger.error(f"Error validating capability claims: {e}")
            # Return low confidence for all claims if analysis fails
            validation_results = {cap: 0.1 for cap in claimed_capabilities}
        
        return validation_results
    
    def _analyze_metadata_capabilities(self, plugin_instance: PluginBase) -> Set[str]:
        """Analyze capabilities from plugin metadata."""
        capabilities = set()
        
        try:
            metadata = plugin_instance.get_metadata()
            
            # Analyze description for capability keywords
            description = metadata.description.lower()
            for signature in self._capability_signatures:
                for keyword in signature.keywords:
                    if keyword.lower() in description:
                        capabilities.add(signature.name)
                        break
            
            # Analyze plugin name
            plugin_name = metadata.name.lower()
            for signature in self._capability_signatures:
                for keyword in signature.keywords:
                    if keyword.lower() in plugin_name:
                        capabilities.add(signature.name)
                        break
            
        except Exception as e:
            logger.debug(f"Error analyzing metadata capabilities: {e}")
        
        return capabilities
    
    def _analyze_tool_capabilities(self, plugin_instance: PluginBase) -> Set[str]:
        """Analyze capabilities from plugin tools."""
        capabilities = set()
        
        try:
            tools = plugin_instance.get_tools()
            
            for tool in tools:
                if isinstance(tool, BaseTool):
                    # Analyze tool name
                    tool_name = tool.name.lower()
                    for signature in self._capability_signatures:
                        for keyword in signature.keywords:
                            if keyword.lower() in tool_name:
                                capabilities.add(signature.name)
                                break
                    
                    # Analyze tool description
                    if hasattr(tool, 'description') and tool.description:
                        tool_desc = tool.description.lower()
                        for signature in self._capability_signatures:
                            for keyword in signature.keywords:
                                if keyword.lower() in tool_desc:
                                    capabilities.add(signature.name)
                                    break
                    
                    # Analyze tool function if available
                    if hasattr(tool, 'func'):
                        func_capabilities = self._analyze_function_capabilities(tool.func)
                        capabilities.update(func_capabilities)
        
        except Exception as e:
            logger.debug(f"Error analyzing tool capabilities: {e}")
        
        return capabilities
    
    def _analyze_code_capabilities(self, plugin_instance: PluginBase) -> Set[str]:
        """Analyze capabilities from plugin source code."""
        capabilities = set()
        
        try:
            # Get plugin class source code
            plugin_class = plugin_instance.__class__
            source_code = inspect.getsource(plugin_class)
            
            # Analyze imports
            import_capabilities = self._analyze_imports(source_code)
            capabilities.update(import_capabilities)
            
            # Analyze method names and content
            method_capabilities = self._analyze_methods(plugin_class)
            capabilities.update(method_capabilities)
            
            # Analyze string literals and patterns
            pattern_capabilities = self._analyze_code_patterns(source_code)
            capabilities.update(pattern_capabilities)
            
        except Exception as e:
            logger.debug(f"Error analyzing code capabilities: {e}")
        
        return capabilities
    
    def _analyze_class_capabilities(self, plugin_instance: PluginBase) -> Set[str]:
        """Analyze capabilities from class structure."""
        capabilities = set()
        
        try:
            plugin_class = plugin_instance.__class__
            
            # Analyze class name
            class_name = plugin_class.__name__.lower()
            for signature in self._capability_signatures:
                for keyword in signature.keywords:
                    if keyword.lower() in class_name:
                        capabilities.add(signature.name)
                        break
            
            # Analyze base classes
            for base_class in plugin_class.__mro__:
                base_name = base_class.__name__.lower()
                for signature in self._capability_signatures:
                    for keyword in signature.keywords:
                        if keyword.lower() in base_name:
                            capabilities.add(signature.name)
                            break
            
            # Analyze class attributes
            for attr_name in dir(plugin_class):
                if not attr_name.startswith('_'):
                    attr_name_lower = attr_name.lower()
                    for signature in self._capability_signatures:
                        for keyword in signature.keywords:
                            if keyword.lower() in attr_name_lower:
                                capabilities.add(signature.name)
                                break
        
        except Exception as e:
            logger.debug(f"Error analyzing class capabilities: {e}")
        
        return capabilities
    
    def _analyze_function_capabilities(self, func) -> Set[str]:
        """Analyze capabilities from a function."""
        capabilities = set()
        
        try:
            # Analyze function name
            func_name = func.__name__.lower()
            for signature in self._capability_signatures:
                for keyword in signature.keywords:
                    if keyword.lower() in func_name:
                        capabilities.add(signature.name)
                        break
            
            # Analyze function source if available
            if hasattr(func, '__code__'):
                source = inspect.getsource(func)
                pattern_capabilities = self._analyze_code_patterns(source)
                capabilities.update(pattern_capabilities)
        
        except Exception as e:
            logger.debug(f"Error analyzing function capabilities: {e}")
        
        return capabilities
    
    def _analyze_imports(self, source_code: str) -> Set[str]:
        """Analyze capabilities from import statements."""
        capabilities = set()
        
        try:
            # Parse AST to extract imports
            tree = ast.parse(source_code)
            
            for node in ast.walk(tree):
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    import_names = []
                    
                    if isinstance(node, ast.Import):
                        import_names = [alias.name for alias in node.names]
                    elif isinstance(node, ast.ImportFrom) and node.module:
                        import_names = [node.module]
                    
                    # Check imports against capability signatures
                    for import_name in import_names:
                        import_name_lower = import_name.lower()
                        for signature in self._capability_signatures:
                            for import_pattern in signature.imports:
                                if import_pattern.lower() in import_name_lower:
                                    capabilities.add(signature.name)
                                    break
        
        except Exception as e:
            logger.debug(f"Error analyzing imports: {e}")
        
        return capabilities
    
    def _analyze_methods(self, plugin_class: Type) -> Set[str]:
        """Analyze capabilities from class methods."""
        capabilities = set()
        
        try:
            for method_name in dir(plugin_class):
                if not method_name.startswith('_'):
                    method_name_lower = method_name.lower()
                    
                    for signature in self._capability_signatures:
                        for method_pattern in signature.methods:
                            if re.search(method_pattern.lower(), method_name_lower):
                                capabilities.add(signature.name)
                                break
        
        except Exception as e:
            logger.debug(f"Error analyzing methods: {e}")
        
        return capabilities
    
    def _analyze_code_patterns(self, source_code: str) -> Set[str]:
        """Analyze capabilities from code patterns."""
        capabilities = set()
        
        try:
            source_lower = source_code.lower()
            
            for signature in self._capability_signatures:
                for pattern in signature.patterns:
                    if re.search(pattern.lower(), source_lower):
                        capabilities.add(signature.name)
                        break
        
        except Exception as e:
            logger.debug(f"Error analyzing code patterns: {e}")
        
        return capabilities
    
    def _detect_weak_capability_signals(self, plugin_instance: PluginBase) -> Dict[str, float]:
        """Detect weak signals that might indicate additional capabilities."""
        weak_signals = {}
        
        try:
            # This is a simplified implementation
            # In practice, this could use more sophisticated analysis
            
            plugin_class = plugin_instance.__class__
            source_code = inspect.getsource(plugin_class)
            
            for signature in self._capability_signatures:
                confidence = 0.0
                
                # Check for partial keyword matches
                for keyword in signature.keywords:
                    if keyword.lower() in source_code.lower():
                        confidence += 0.1
                
                # Check for related patterns
                for pattern in signature.patterns:
                    if re.search(pattern.lower(), source_code.lower()):
                        confidence += 0.2
                
                if confidence > 0:
                    weak_signals[signature.name] = min(confidence, 1.0)
        
        except Exception as e:
            logger.debug(f"Error detecting weak capability signals: {e}")
        
        return weak_signals
    
    def _determine_capability_category(self, capability: str) -> CapabilityCategory:
        """Determine the category for a capability."""
        for signature in self._capability_signatures:
            if signature.name == capability:
                return signature.category
        
        # Default category based on capability name
        capability_lower = capability.lower()
        if any(word in capability_lower for word in ['file', 'directory', 'folder']):
            return CapabilityCategory.FILE_OPERATIONS
        elif any(word in capability_lower for word in ['web', 'http', 'url', 'api']):
            return CapabilityCategory.WEB_OPERATIONS
        elif any(word in capability_lower for word in ['data', 'database', 'sql']):
            return CapabilityCategory.DATA_OPERATIONS
        elif any(word in capability_lower for word in ['system', 'process', 'command']):
            return CapabilityCategory.SYSTEM_OPERATIONS
        else:
            return CapabilityCategory.INTEGRATION
    
    def _initialize_capability_signatures(self) -> List[CapabilitySignature]:
        """Initialize capability detection signatures."""
        return [
            # File Operations
            CapabilitySignature(
                name="file_read",
                category=CapabilityCategory.FILE_OPERATIONS,
                keywords=["read", "file", "open", "load"],
                patterns=[r"open\s*\(", r"\.read\s*\(", r"pathlib", r"os\.path"],
                imports=["pathlib", "os", "io"],
                methods=["read.*file", "load.*file", "open.*file"]
            ),
            CapabilitySignature(
                name="file_write",
                category=CapabilityCategory.FILE_OPERATIONS,
                keywords=["write", "save", "create", "file"],
                patterns=[r"\.write\s*\(", r"\.save\s*\(", r"with\s+open.*w"],
                imports=["pathlib", "os", "io"],
                methods=["write.*file", "save.*file", "create.*file"]
            ),
            CapabilitySignature(
                name="directory_operations",
                category=CapabilityCategory.FILE_OPERATIONS,
                keywords=["directory", "folder", "mkdir", "listdir"],
                patterns=[r"os\.mkdir", r"os\.listdir", r"glob\.glob"],
                imports=["os", "glob", "pathlib"],
                methods=["list.*dir", "create.*dir", "scan.*dir"]
            ),
            
            # Web Operations
            CapabilitySignature(
                name="web_request",
                category=CapabilityCategory.WEB_OPERATIONS,
                keywords=["http", "request", "web", "api", "url"],
                patterns=[r"requests\.", r"urllib", r"http"],
                imports=["requests", "urllib", "httpx", "aiohttp"],
                methods=[".*request", ".*fetch", ".*download"]
            ),
            CapabilitySignature(
                name="web_scraping",
                category=CapabilityCategory.WEB_OPERATIONS,
                keywords=["scrape", "parse", "html", "beautifulsoup"],
                patterns=[r"beautifulsoup", r"selenium", r"scrapy"],
                imports=["bs4", "beautifulsoup4", "selenium", "scrapy"],
                methods=["scrape.*", "parse.*html", "extract.*"]
            ),
            
            # Data Operations
            CapabilitySignature(
                name="data_processing",
                category=CapabilityCategory.DATA_OPERATIONS,
                keywords=["data", "process", "transform", "analyze"],
                patterns=[r"pandas", r"numpy", r"\.csv", r"\.json"],
                imports=["pandas", "numpy", "json", "csv"],
                methods=["process.*data", "transform.*", "analyze.*"]
            ),
            CapabilitySignature(
                name="database_operations",
                category=CapabilityCategory.DATA_OPERATIONS,
                keywords=["database", "sql", "query", "db"],
                patterns=[r"sqlite", r"mysql", r"postgresql", r"\.execute"],
                imports=["sqlite3", "sqlalchemy", "pymongo", "psycopg2"],
                methods=[".*query", ".*execute", ".*database"]
            ),
            
            # System Operations
            CapabilitySignature(
                name="system_command",
                category=CapabilityCategory.SYSTEM_OPERATIONS,
                keywords=["command", "execute", "subprocess", "shell"],
                patterns=[r"subprocess", r"os\.system", r"shell"],
                imports=["subprocess", "os", "shlex"],
                methods=["execute.*", "run.*command", ".*shell"]
            ),
            CapabilitySignature(
                name="process_management",
                category=CapabilityCategory.SYSTEM_OPERATIONS,
                keywords=["process", "pid", "kill", "monitor"],
                patterns=[r"psutil", r"\.pid", r"multiprocessing"],
                imports=["psutil", "multiprocessing", "threading"],
                methods=[".*process", "monitor.*", "kill.*"]
            ),
            
            # Communication
            CapabilitySignature(
                name="email_operations",
                category=CapabilityCategory.COMMUNICATION,
                keywords=["email", "mail", "smtp", "send"],
                patterns=[r"smtplib", r"email", r"\.send"],
                imports=["smtplib", "email", "imaplib"],
                methods=["send.*mail", ".*email", "smtp.*"]
            ),
            CapabilitySignature(
                name="notification",
                category=CapabilityCategory.COMMUNICATION,
                keywords=["notify", "alert", "message", "notification"],
                patterns=[r"notification", r"alert", r"toast"],
                imports=["plyer", "win10toast", "notify2"],
                methods=["notify.*", "alert.*", "send.*message"]
            ),
            
            # Analysis
            CapabilitySignature(
                name="text_analysis",
                category=CapabilityCategory.ANALYSIS,
                keywords=["text", "nlp", "analyze", "sentiment"],
                patterns=[r"nltk", r"spacy", r"textblob"],
                imports=["nltk", "spacy", "textblob", "transformers"],
                methods=["analyze.*text", ".*sentiment", ".*nlp"]
            ),
            CapabilitySignature(
                name="image_processing",
                category=CapabilityCategory.ANALYSIS,
                keywords=["image", "picture", "photo", "vision"],
                patterns=[r"pillow", r"opencv", r"pil"],
                imports=["PIL", "cv2", "opencv", "skimage"],
                methods=[".*image", ".*photo", "process.*img"]
            ),
            
            # Security
            CapabilitySignature(
                name="encryption",
                category=CapabilityCategory.SECURITY,
                keywords=["encrypt", "decrypt", "crypto", "security"],
                patterns=[r"cryptography", r"hashlib", r"encrypt"],
                imports=["cryptography", "hashlib", "ssl"],
                methods=["encrypt.*", "decrypt.*", "hash.*"]
            ),
            
            # Automation
            CapabilitySignature(
                name="task_automation",
                category=CapabilityCategory.AUTOMATION,
                keywords=["automate", "schedule", "task", "cron"],
                patterns=[r"schedule", r"cron", r"automation"],
                imports=["schedule", "crontab", "celery"],
                methods=["schedule.*", "automate.*", ".*task"]
            )
        ]
