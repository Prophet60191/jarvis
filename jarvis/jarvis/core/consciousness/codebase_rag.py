"""
Codebase RAG System

Implements RAG (Retrieval-Augmented Generation) for codebase understanding,
enabling semantic search and intelligent code analysis.
"""

import asyncio
import time
import logging
import hashlib
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import threading
import json
import ast
import re

logger = logging.getLogger(__name__)

class CodeType(Enum):
    """Types of code content."""
    FUNCTION = "function"
    CLASS = "class"
    METHOD = "method"
    MODULE = "module"
    IMPORT = "import"
    COMMENT = "comment"
    DOCSTRING = "docstring"
    VARIABLE = "variable"
    CONSTANT = "constant"

class CodeLanguage(Enum):
    """Supported programming languages."""
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    JAVA = "java"
    CPP = "cpp"
    C = "c"
    GO = "go"
    RUST = "rust"
    UNKNOWN = "unknown"

@dataclass
class CodeChunk:
    """Represents a chunk of code for RAG processing."""
    chunk_id: str
    file_path: str
    content: str
    code_type: CodeType
    language: CodeLanguage
    
    # Position information
    start_line: int
    end_line: int
    
    # Metadata
    function_name: Optional[str] = None
    class_name: Optional[str] = None
    module_name: Optional[str] = None
    
    # Semantic information
    summary: Optional[str] = None
    keywords: Set[str] = field(default_factory=set)
    dependencies: List[str] = field(default_factory=list)
    
    # Indexing
    embedding: Optional[List[float]] = None
    indexed_at: float = field(default_factory=time.time)
    
    def get_identifier(self) -> str:
        """Get unique identifier for this chunk."""
        if self.function_name:
            return f"{self.module_name}.{self.function_name}" if self.module_name else self.function_name
        elif self.class_name:
            return f"{self.module_name}.{self.class_name}" if self.module_name else self.class_name
        else:
            return f"{self.file_path}:{self.start_line}-{self.end_line}"

@dataclass
class CodeDocument:
    """Represents a complete code file."""
    file_path: str
    language: CodeLanguage
    content: str
    
    # Metadata
    file_size: int
    last_modified: float
    encoding: str = "utf-8"
    
    # Analysis results
    chunks: List[CodeChunk] = field(default_factory=list)
    imports: List[str] = field(default_factory=list)
    exports: List[str] = field(default_factory=list)
    
    # Indexing
    indexed_at: Optional[float] = None
    content_hash: Optional[str] = None
    
    def calculate_hash(self) -> str:
        """Calculate content hash for change detection."""
        return hashlib.md5(self.content.encode()).hexdigest()
    
    def needs_reindexing(self) -> bool:
        """Check if document needs reindexing."""
        current_hash = self.calculate_hash()
        return self.content_hash != current_hash

@dataclass
class CodeSearchResult:
    """Result from code search."""
    chunk: CodeChunk
    relevance_score: float
    file_path: str
    content: str
    line_number: int
    context: Dict[str, Any] = field(default_factory=dict)

class CodebaseRAG:
    """
    RAG system for codebase understanding and search.
    
    This component provides semantic search capabilities over the codebase,
    enabling intelligent code discovery and understanding.
    """
    
    def __init__(self, codebase_path: Path, storage_path: Optional[Path] = None):
        """
        Initialize the codebase RAG system.
        
        Args:
            codebase_path: Path to the codebase to index
            storage_path: Optional path for persistent storage
        """
        self.codebase_path = codebase_path
        self.storage_path = storage_path or (codebase_path / ".jarvis_rag")
        
        # Document storage
        self._documents: Dict[str, CodeDocument] = {}
        self._chunks: Dict[str, CodeChunk] = {}
        
        # Indexing state
        self._indexed_files: Set[str] = set()
        self._index_version = 1
        self._last_index_time: Optional[float] = None
        
        # Configuration
        self.supported_extensions = {
            ".py": CodeLanguage.PYTHON,
            ".js": CodeLanguage.JAVASCRIPT,
            ".ts": CodeLanguage.TYPESCRIPT,
            ".java": CodeLanguage.JAVA,
            ".cpp": CodeLanguage.CPP,
            ".c": CodeLanguage.C,
            ".go": CodeLanguage.GO,
            ".rs": CodeLanguage.RUST
        }
        
        self.chunk_size = 1000  # Characters per chunk
        self.chunk_overlap = 150  # Overlap between chunks
        self.max_file_size = 1024 * 1024  # 1MB max file size
        
        # Exclusion patterns
        self.exclude_patterns = {
            "__pycache__", ".git", ".venv", "node_modules",
            ".pytest_cache", ".mypy_cache", "dist", "build"
        }
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Create storage directory
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"CodebaseRAG initialized for {codebase_path}")
    
    async def index_codebase(self, force_reindex: bool = False) -> bool:
        """
        Index the entire codebase.
        
        Args:
            force_reindex: Whether to force reindexing of all files
            
        Returns:
            bool: True if indexing successful
        """
        try:
            logger.info("Starting codebase indexing...")
            start_time = time.time()
            
            # Find all code files
            code_files = self._find_code_files()
            
            indexed_count = 0
            skipped_count = 0
            
            for file_path in code_files:
                try:
                    # Check if file needs indexing
                    if not force_reindex and self._is_file_indexed(file_path):
                        skipped_count += 1
                        continue
                    
                    # Index the file
                    success = await self._index_file(file_path)
                    if success:
                        indexed_count += 1
                    
                except Exception as e:
                    logger.warning(f"Failed to index {file_path}: {e}")
            
            # Update index metadata
            self._last_index_time = time.time()
            
            # Save index
            await self._save_index()
            
            duration = time.time() - start_time
            logger.info(f"Indexing complete: {indexed_count} files indexed, "
                       f"{skipped_count} skipped in {duration:.2f}s")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to index codebase: {e}")
            return False
    
    async def search_code(self, query: str, max_results: int = 10,
                         scope: Optional[str] = None) -> List[CodeSearchResult]:
        """
        Search code using semantic similarity.
        
        Args:
            query: Search query
            max_results: Maximum number of results
            scope: Optional scope limitation (file pattern)
            
        Returns:
            List[CodeSearchResult]: Search results
        """
        with self._lock:
            results = []
            
            # Simple text-based search (could be enhanced with embeddings)
            query_lower = query.lower()
            query_terms = set(query_lower.split())
            
            for chunk in self._chunks.values():
                # Apply scope filter
                if scope and scope not in chunk.file_path:
                    continue
                
                # Calculate relevance score
                score = self._calculate_relevance_score(chunk, query_terms, query_lower)
                
                if score > 0.1:  # Minimum relevance threshold
                    result = CodeSearchResult(
                        chunk=chunk,
                        relevance_score=score,
                        file_path=chunk.file_path,
                        content=chunk.content,
                        line_number=chunk.start_line,
                        context={
                            "code_type": chunk.code_type.value,
                            "language": chunk.language.value,
                            "identifier": chunk.get_identifier()
                        }
                    )
                    results.append(result)
            
            # Sort by relevance
            results.sort(key=lambda r: r.relevance_score, reverse=True)
            
            return results[:max_results]
    
    def get_file_analysis(self, file_path: str) -> Optional[CodeDocument]:
        """
        Get analysis results for a specific file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Optional[CodeDocument]: File analysis or None if not found
        """
        with self._lock:
            return self._documents.get(file_path)
    
    def get_function_info(self, function_name: str) -> List[CodeChunk]:
        """
        Get information about a specific function.
        
        Args:
            function_name: Name of the function
            
        Returns:
            List[CodeChunk]: Function chunks
        """
        with self._lock:
            results = []
            
            for chunk in self._chunks.values():
                if (chunk.function_name == function_name or 
                    function_name in chunk.content):
                    results.append(chunk)
            
            return results
    
    def get_class_info(self, class_name: str) -> List[CodeChunk]:
        """
        Get information about a specific class.
        
        Args:
            class_name: Name of the class
            
        Returns:
            List[CodeChunk]: Class chunks
        """
        with self._lock:
            results = []
            
            for chunk in self._chunks.values():
                if (chunk.class_name == class_name or 
                    class_name in chunk.content):
                    results.append(chunk)
            
            return results
    
    def get_indexed_files(self) -> List[str]:
        """
        Get list of indexed files.
        
        Returns:
            List[str]: List of indexed file paths
        """
        with self._lock:
            return list(self._indexed_files)
    
    def get_index_statistics(self) -> Dict[str, Any]:
        """
        Get indexing statistics.
        
        Returns:
            Dict[str, Any]: Index statistics
        """
        with self._lock:
            # Count by language
            language_counts = {}
            for doc in self._documents.values():
                lang = doc.language.value
                language_counts[lang] = language_counts.get(lang, 0) + 1
            
            # Count by code type
            type_counts = {}
            for chunk in self._chunks.values():
                code_type = chunk.code_type.value
                type_counts[code_type] = type_counts.get(code_type, 0) + 1
            
            return {
                "total_files": len(self._documents),
                "total_chunks": len(self._chunks),
                "indexed_files": len(self._indexed_files),
                "last_index_time": self._last_index_time,
                "language_distribution": language_counts,
                "code_type_distribution": type_counts,
                "index_version": self._index_version
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
                # Check file size
                if file_path.stat().st_size <= self.max_file_size:
                    code_files.append(file_path)
        
        return code_files
    
    def _is_file_indexed(self, file_path: Path) -> bool:
        """Check if a file is already indexed and up to date."""
        file_str = str(file_path)
        
        if file_str not in self._indexed_files:
            return False
        
        if file_str not in self._documents:
            return False
        
        # Check if file has been modified
        doc = self._documents[file_str]
        current_mtime = file_path.stat().st_mtime
        
        return doc.last_modified >= current_mtime
    
    async def _index_file(self, file_path: Path) -> bool:
        """Index a single file."""
        try:
            # Read file content
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Determine language
            language = self.supported_extensions.get(file_path.suffix, CodeLanguage.UNKNOWN)
            
            # Create document
            doc = CodeDocument(
                file_path=str(file_path),
                language=language,
                content=content,
                file_size=len(content),
                last_modified=file_path.stat().st_mtime
            )
            
            # Analyze and chunk the file
            await self._analyze_file(doc)
            
            # Store document
            with self._lock:
                self._documents[str(file_path)] = doc
                self._indexed_files.add(str(file_path))
                
                # Store chunks
                for chunk in doc.chunks:
                    self._chunks[chunk.chunk_id] = chunk
            
            doc.indexed_at = time.time()
            doc.content_hash = doc.calculate_hash()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to index file {file_path}: {e}")
            return False
    
    async def _analyze_file(self, doc: CodeDocument) -> None:
        """Analyze a file and create chunks."""
        if doc.language == CodeLanguage.PYTHON:
            await self._analyze_python_file(doc)
        else:
            # Generic analysis for other languages
            await self._analyze_generic_file(doc)
    
    async def _analyze_python_file(self, doc: CodeDocument) -> None:
        """Analyze a Python file."""
        try:
            # Parse AST
            tree = ast.parse(doc.content)
            
            # Extract imports
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        doc.imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        doc.imports.append(node.module)
            
            # Extract functions and classes
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    await self._create_function_chunk(doc, node)
                elif isinstance(node, ast.ClassDef):
                    await self._create_class_chunk(doc, node)
            
            # Create module-level chunk
            await self._create_module_chunk(doc)
            
        except SyntaxError:
            # Fallback to generic analysis if parsing fails
            await self._analyze_generic_file(doc)
    
    async def _analyze_generic_file(self, doc: CodeDocument) -> None:
        """Generic file analysis for non-Python files."""
        lines = doc.content.split('\n')
        
        # Create chunks based on size
        current_chunk = []
        current_size = 0
        chunk_start_line = 1
        
        for i, line in enumerate(lines, 1):
            current_chunk.append(line)
            current_size += len(line)
            
            if current_size >= self.chunk_size:
                # Create chunk
                chunk_content = '\n'.join(current_chunk)
                chunk = CodeChunk(
                    chunk_id=f"{doc.file_path}:{chunk_start_line}-{i}",
                    file_path=doc.file_path,
                    content=chunk_content,
                    code_type=CodeType.MODULE,
                    language=doc.language,
                    start_line=chunk_start_line,
                    end_line=i,
                    module_name=Path(doc.file_path).stem
                )
                
                doc.chunks.append(chunk)
                
                # Start new chunk with overlap
                overlap_lines = current_chunk[-self.chunk_overlap//20:]  # Rough overlap
                current_chunk = overlap_lines
                current_size = sum(len(line) for line in overlap_lines)
                chunk_start_line = i - len(overlap_lines) + 1
        
        # Add remaining content as final chunk
        if current_chunk:
            chunk_content = '\n'.join(current_chunk)
            chunk = CodeChunk(
                chunk_id=f"{doc.file_path}:{chunk_start_line}-{len(lines)}",
                file_path=doc.file_path,
                content=chunk_content,
                code_type=CodeType.MODULE,
                language=doc.language,
                start_line=chunk_start_line,
                end_line=len(lines),
                module_name=Path(doc.file_path).stem
            )
            
            doc.chunks.append(chunk)
    
    async def _create_function_chunk(self, doc: CodeDocument, node: ast.FunctionDef) -> None:
        """Create a chunk for a function."""
        # Get function source
        lines = doc.content.split('\n')
        start_line = node.lineno
        end_line = node.end_lineno or start_line
        
        function_lines = lines[start_line-1:end_line]
        content = '\n'.join(function_lines)
        
        # Extract docstring
        docstring = ast.get_docstring(node)
        
        chunk = CodeChunk(
            chunk_id=f"{doc.file_path}:func:{node.name}:{start_line}",
            file_path=doc.file_path,
            content=content,
            code_type=CodeType.FUNCTION,
            language=doc.language,
            start_line=start_line,
            end_line=end_line,
            function_name=node.name,
            module_name=Path(doc.file_path).stem,
            summary=docstring
        )
        
        # Extract keywords
        chunk.keywords.add(node.name)
        if docstring:
            chunk.keywords.update(docstring.lower().split())
        
        doc.chunks.append(chunk)
    
    async def _create_class_chunk(self, doc: CodeDocument, node: ast.ClassDef) -> None:
        """Create a chunk for a class."""
        # Get class source
        lines = doc.content.split('\n')
        start_line = node.lineno
        end_line = node.end_lineno or start_line
        
        class_lines = lines[start_line-1:end_line]
        content = '\n'.join(class_lines)
        
        # Extract docstring
        docstring = ast.get_docstring(node)
        
        chunk = CodeChunk(
            chunk_id=f"{doc.file_path}:class:{node.name}:{start_line}",
            file_path=doc.file_path,
            content=content,
            code_type=CodeType.CLASS,
            language=doc.language,
            start_line=start_line,
            end_line=end_line,
            class_name=node.name,
            module_name=Path(doc.file_path).stem,
            summary=docstring
        )
        
        # Extract keywords
        chunk.keywords.add(node.name)
        if docstring:
            chunk.keywords.update(docstring.lower().split())
        
        doc.chunks.append(chunk)
    
    async def _create_module_chunk(self, doc: CodeDocument) -> None:
        """Create a chunk for module-level content."""
        # Get module docstring
        try:
            tree = ast.parse(doc.content)
            docstring = ast.get_docstring(tree)
        except:
            docstring = None
        
        # Create summary chunk with first part of file
        summary_content = doc.content[:self.chunk_size]
        
        chunk = CodeChunk(
            chunk_id=f"{doc.file_path}:module:0",
            file_path=doc.file_path,
            content=summary_content,
            code_type=CodeType.MODULE,
            language=doc.language,
            start_line=1,
            end_line=len(summary_content.split('\n')),
            module_name=Path(doc.file_path).stem,
            summary=docstring
        )
        
        # Extract keywords from imports and docstring
        chunk.keywords.update(doc.imports)
        if docstring:
            chunk.keywords.update(docstring.lower().split())
        
        doc.chunks.append(chunk)
    
    def _calculate_relevance_score(self, chunk: CodeChunk, query_terms: Set[str], 
                                 query_lower: str) -> float:
        """Calculate relevance score for a chunk."""
        score = 0.0
        content_lower = chunk.content.lower()
        
        # Exact query match
        if query_lower in content_lower:
            score += 1.0
        
        # Term matches
        chunk_terms = set(content_lower.split())
        matching_terms = query_terms.intersection(chunk_terms)
        if query_terms:
            score += len(matching_terms) / len(query_terms) * 0.8
        
        # Keyword matches
        matching_keywords = query_terms.intersection(chunk.keywords)
        if chunk.keywords:
            score += len(matching_keywords) / len(chunk.keywords) * 0.6
        
        # Identifier matches
        identifier = chunk.get_identifier().lower()
        if any(term in identifier for term in query_terms):
            score += 0.5
        
        # Summary matches
        if chunk.summary:
            summary_lower = chunk.summary.lower()
            if query_lower in summary_lower:
                score += 0.4
        
        return min(score, 1.0)  # Cap at 1.0
    
    async def _save_index(self) -> None:
        """Save index to persistent storage."""
        try:
            index_data = {
                "version": self._index_version,
                "last_index_time": self._last_index_time,
                "indexed_files": list(self._indexed_files),
                "documents": {
                    path: {
                        "file_path": doc.file_path,
                        "language": doc.language.value,
                        "file_size": doc.file_size,
                        "last_modified": doc.last_modified,
                        "indexed_at": doc.indexed_at,
                        "content_hash": doc.content_hash,
                        "imports": doc.imports,
                        "exports": doc.exports
                    }
                    for path, doc in self._documents.items()
                },
                "chunks": {
                    chunk_id: {
                        "chunk_id": chunk.chunk_id,
                        "file_path": chunk.file_path,
                        "code_type": chunk.code_type.value,
                        "language": chunk.language.value,
                        "start_line": chunk.start_line,
                        "end_line": chunk.end_line,
                        "function_name": chunk.function_name,
                        "class_name": chunk.class_name,
                        "module_name": chunk.module_name,
                        "summary": chunk.summary,
                        "keywords": list(chunk.keywords),
                        "dependencies": chunk.dependencies,
                        "indexed_at": chunk.indexed_at
                    }
                    for chunk_id, chunk in self._chunks.items()
                }
            }
            
            index_file = self.storage_path / "index.json"
            with open(index_file, 'w') as f:
                json.dump(index_data, f, indent=2)
            
            logger.debug("Saved RAG index to storage")
            
        except Exception as e:
            logger.error(f"Failed to save RAG index: {e}")
    
    async def _load_index(self) -> None:
        """Load index from persistent storage."""
        try:
            index_file = self.storage_path / "index.json"
            if not index_file.exists():
                return
            
            with open(index_file, 'r') as f:
                index_data = json.load(f)
            
            # Load basic metadata
            self._index_version = index_data.get("version", 1)
            self._last_index_time = index_data.get("last_index_time")
            self._indexed_files = set(index_data.get("indexed_files", []))
            
            # Note: Full document and chunk loading would require storing content
            # For now, we just load metadata and reindex as needed
            
            logger.debug("Loaded RAG index from storage")
            
        except Exception as e:
            logger.error(f"Failed to load RAG index: {e}")
