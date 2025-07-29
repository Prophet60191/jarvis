#!/usr/bin/env python3
"""
RAG Error Handler and Validation System

Provides comprehensive error handling, validation, and graceful fallbacks
for the RAG system to ensure production reliability.
"""

import os
import logging
import traceback
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable, Union
from functools import wraps
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class RAGErrorType(Enum):
    """Types of RAG system errors."""
    CONFIGURATION_ERROR = "configuration_error"
    DEPENDENCY_ERROR = "dependency_error"
    PERMISSION_ERROR = "permission_error"
    STORAGE_ERROR = "storage_error"
    DOCUMENT_ERROR = "document_error"
    MEMORY_ERROR = "memory_error"
    NETWORK_ERROR = "network_error"
    VALIDATION_ERROR = "validation_error"
    UNKNOWN_ERROR = "unknown_error"


@dataclass
class RAGError:
    """Structured RAG error information."""
    error_type: RAGErrorType
    message: str
    details: Optional[str] = None
    component: Optional[str] = None
    recoverable: bool = True
    suggested_action: Optional[str] = None
    original_exception: Optional[Exception] = None


class RAGErrorHandler:
    """Centralized error handling for RAG system."""
    
    def __init__(self):
        """Initialize the error handler."""
        self.error_history: List[RAGError] = []
        self.max_history = 100
        
    def handle_error(self, error: Union[Exception, RAGError], 
                    component: str = "unknown", 
                    context: Optional[Dict[str, Any]] = None) -> RAGError:
        """
        Handle and log an error with appropriate categorization.
        
        Args:
            error: Exception or RAGError to handle
            component: Component where error occurred
            context: Additional context information
            
        Returns:
            RAGError: Structured error information
        """
        if isinstance(error, RAGError):
            rag_error = error
        else:
            rag_error = self._categorize_error(error, component, context)
        
        # Log the error
        self._log_error(rag_error)
        
        # Add to history
        self._add_to_history(rag_error)
        
        return rag_error
    
    def _categorize_error(self, exception: Exception, component: str, 
                         context: Optional[Dict[str, Any]]) -> RAGError:
        """Categorize an exception into a structured RAG error."""
        error_type = RAGErrorType.UNKNOWN_ERROR
        message = str(exception)
        recoverable = True
        suggested_action = None
        
        # Categorize based on exception type and message
        if isinstance(exception, ImportError):
            error_type = RAGErrorType.DEPENDENCY_ERROR
            recoverable = False
            suggested_action = f"Install missing dependency: {exception.name if hasattr(exception, 'name') else 'unknown'}"
            
        elif isinstance(exception, PermissionError):
            error_type = RAGErrorType.PERMISSION_ERROR
            suggested_action = "Check file/directory permissions"
            
        elif isinstance(exception, FileNotFoundError):
            error_type = RAGErrorType.STORAGE_ERROR
            suggested_action = "Ensure required files/directories exist"
            
        elif isinstance(exception, OSError):
            if "disk" in message.lower() or "space" in message.lower():
                error_type = RAGErrorType.STORAGE_ERROR
                suggested_action = "Check available disk space"
            else:
                error_type = RAGErrorType.STORAGE_ERROR
                
        elif isinstance(exception, ValueError):
            error_type = RAGErrorType.VALIDATION_ERROR
            suggested_action = "Check input parameters and configuration"
            
        elif isinstance(exception, ConnectionError):
            error_type = RAGErrorType.NETWORK_ERROR
            suggested_action = "Check network connectivity and service availability"
            
        elif "chroma" in message.lower() or "vector" in message.lower():
            error_type = RAGErrorType.STORAGE_ERROR
            suggested_action = "Check vector database configuration and connectivity"
            
        elif "document" in message.lower() or "pdf" in message.lower():
            error_type = RAGErrorType.DOCUMENT_ERROR
            suggested_action = "Check document format and accessibility"
            
        elif "memory" in message.lower() or "embedding" in message.lower():
            error_type = RAGErrorType.MEMORY_ERROR
            suggested_action = "Check memory usage and embedding service"
            
        elif "config" in message.lower():
            error_type = RAGErrorType.CONFIGURATION_ERROR
            suggested_action = "Review RAG configuration settings"
        
        return RAGError(
            error_type=error_type,
            message=message,
            details=traceback.format_exc() if logger.isEnabledFor(logging.DEBUG) else None,
            component=component,
            recoverable=recoverable,
            suggested_action=suggested_action,
            original_exception=exception
        )
    
    def _log_error(self, error: RAGError):
        """Log the error with appropriate level."""
        log_message = f"[{error.component}] {error.error_type.value}: {error.message}"
        
        if error.suggested_action:
            log_message += f" | Suggested action: {error.suggested_action}"
        
        if error.recoverable:
            logger.warning(log_message)
        else:
            logger.error(log_message)
        
        if error.details and logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"Error details: {error.details}")
    
    def _add_to_history(self, error: RAGError):
        """Add error to history with size limit."""
        self.error_history.append(error)
        
        # Maintain history size limit
        if len(self.error_history) > self.max_history:
            self.error_history = self.error_history[-self.max_history:]
    
    def get_error_summary(self) -> Dict[str, Any]:
        """Get summary of recent errors."""
        if not self.error_history:
            return {"total_errors": 0, "error_types": {}, "recent_errors": []}
        
        # Count by type
        error_type_counts = {}
        for error in self.error_history:
            error_type = error.error_type.value
            error_type_counts[error_type] = error_type_counts.get(error_type, 0) + 1
        
        # Get recent errors (last 10)
        recent_errors = []
        for error in self.error_history[-10:]:
            recent_errors.append({
                "type": error.error_type.value,
                "message": error.message,
                "component": error.component,
                "recoverable": error.recoverable,
                "suggested_action": error.suggested_action
            })
        
        return {
            "total_errors": len(self.error_history),
            "error_types": error_type_counts,
            "recent_errors": recent_errors
        }


# Global error handler instance
_error_handler = RAGErrorHandler()


def rag_error_handler(component: str = "unknown", 
                     fallback_return: Any = None,
                     raise_on_critical: bool = True):
    """
    Decorator for RAG method error handling.
    
    Args:
        component: Component name for error tracking
        fallback_return: Value to return on recoverable errors
        raise_on_critical: Whether to raise non-recoverable errors
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error = _error_handler.handle_error(e, component)
                
                if not error.recoverable and raise_on_critical:
                    raise e
                
                return fallback_return
        return wrapper
    return decorator


class RAGValidator:
    """Validation utilities for RAG system components."""
    
    @staticmethod
    def validate_path(path: Union[str, Path], 
                     must_exist: bool = False,
                     must_be_writable: bool = False,
                     create_if_missing: bool = False) -> tuple[bool, Optional[str]]:
        """
        Validate a file system path.
        
        Args:
            path: Path to validate
            must_exist: Whether path must already exist
            must_be_writable: Whether path must be writable
            create_if_missing: Whether to create path if missing
            
        Returns:
            tuple: (is_valid, error_message)
        """
        try:
            path_obj = Path(path)
            
            # Check if path exists
            if must_exist and not path_obj.exists():
                return False, f"Path does not exist: {path}"
            
            # Create if requested and missing
            if create_if_missing and not path_obj.exists():
                try:
                    path_obj.mkdir(parents=True, exist_ok=True)
                except PermissionError:
                    return False, f"Cannot create path (permission denied): {path}"
                except OSError as e:
                    return False, f"Cannot create path: {path} - {e}"
            
            # Check writability
            if must_be_writable:
                if path_obj.exists():
                    if not os.access(path_obj, os.W_OK):
                        return False, f"Path is not writable: {path}"
                else:
                    # Check parent directory writability
                    parent = path_obj.parent
                    if not parent.exists() or not os.access(parent, os.W_OK):
                        return False, f"Parent directory is not writable: {parent}"
            
            return True, None
            
        except Exception as e:
            return False, f"Path validation error: {e}"
    
    @staticmethod
    def validate_config(config: Any) -> tuple[bool, List[str]]:
        """
        Validate RAG configuration.
        
        Args:
            config: RAG configuration object
            
        Returns:
            tuple: (is_valid, list_of_errors)
        """
        errors = []
        
        try:
            # Check required attributes
            required_attrs = [
                'vector_store_path', 'documents_path', 'backup_path',
                'collection_name', 'chunk_size', 'chunk_overlap'
            ]
            
            for attr in required_attrs:
                if not hasattr(config, attr):
                    errors.append(f"Missing required configuration: {attr}")
                elif getattr(config, attr) is None:
                    errors.append(f"Configuration cannot be None: {attr}")
            
            # Validate numeric values
            if hasattr(config, 'chunk_size') and config.chunk_size <= 0:
                errors.append("chunk_size must be positive")
            
            if hasattr(config, 'chunk_overlap') and config.chunk_overlap < 0:
                errors.append("chunk_overlap cannot be negative")
            
            if (hasattr(config, 'chunk_size') and hasattr(config, 'chunk_overlap') and
                config.chunk_overlap >= config.chunk_size):
                errors.append("chunk_overlap must be less than chunk_size")
            
            # Validate paths
            if hasattr(config, 'vector_store_path'):
                valid, error = RAGValidator.validate_path(
                    config.vector_store_path, 
                    create_if_missing=True,
                    must_be_writable=True
                )
                if not valid:
                    errors.append(f"vector_store_path: {error}")
            
            if hasattr(config, 'documents_path'):
                valid, error = RAGValidator.validate_path(
                    config.documents_path,
                    create_if_missing=True,
                    must_be_writable=True
                )
                if not valid:
                    errors.append(f"documents_path: {error}")
            
            if hasattr(config, 'backup_path'):
                valid, error = RAGValidator.validate_path(
                    config.backup_path,
                    create_if_missing=True,
                    must_be_writable=True
                )
                if not valid:
                    errors.append(f"backup_path: {error}")
            
        except Exception as e:
            errors.append(f"Configuration validation error: {e}")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_document(file_path: Union[str, Path], 
                         max_size_mb: float = 50) -> tuple[bool, Optional[str]]:
        """
        Validate a document for ingestion.
        
        Args:
            file_path: Path to document
            max_size_mb: Maximum file size in MB
            
        Returns:
            tuple: (is_valid, error_message)
        """
        try:
            path_obj = Path(file_path)
            
            # Check existence
            if not path_obj.exists():
                return False, f"Document does not exist: {file_path}"
            
            # Check if it's a file
            if not path_obj.is_file():
                return False, f"Path is not a file: {file_path}"
            
            # Check size
            size_mb = path_obj.stat().st_size / (1024 * 1024)
            if size_mb > max_size_mb:
                return False, f"Document too large: {size_mb:.1f}MB (max: {max_size_mb}MB)"
            
            # Check extension
            supported_extensions = {'.txt', '.pdf', '.doc', '.docx', '.md'}
            if path_obj.suffix.lower() not in supported_extensions:
                return False, f"Unsupported file type: {path_obj.suffix}"
            
            # Check readability
            if not os.access(path_obj, os.R_OK):
                return False, f"Document is not readable: {file_path}"
            
            return True, None
            
        except Exception as e:
            return False, f"Document validation error: {e}"


def get_error_handler() -> RAGErrorHandler:
    """Get the global error handler instance."""
    return _error_handler


def validate_dependencies() -> tuple[bool, List[str]]:
    """
    Validate that all required dependencies are available.
    
    Returns:
        tuple: (all_available, list_of_missing)
    """
    missing_deps = []
    
    # Check core dependencies
    try:
        import chromadb
    except ImportError:
        missing_deps.append("chromadb")
    
    try:
        from langchain_chroma import Chroma
    except ImportError:
        try:
            from langchain_community.vectorstores import Chroma
        except ImportError:
            missing_deps.append("langchain-chroma or langchain-community")
    
    try:
        from langchain_ollama import OllamaEmbeddings
    except ImportError:
        try:
            from langchain_community.embeddings import OllamaEmbeddings
        except ImportError:
            missing_deps.append("langchain-ollama or langchain-community")
    
    # Check document processing dependencies
    try:
        from langchain_community.document_loaders import PyPDFLoader
    except ImportError:
        missing_deps.append("pypdf (for PDF processing)")
    
    try:
        from langchain_community.document_loaders import UnstructuredWordDocumentLoader
    except ImportError:
        missing_deps.append("python-docx (for Word document processing)")
    
    return len(missing_deps) == 0, missing_deps
