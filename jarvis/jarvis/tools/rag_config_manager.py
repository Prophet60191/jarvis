#!/usr/bin/env python3
"""
RAG Configuration Manager

Handles RAG system configuration, path management, and validation.
Ensures all paths are properly configured and accessible.
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import asdict

from ..config import RAGConfig, get_config

logger = logging.getLogger(__name__)


class RAGConfigManager:
    """Manages RAG system configuration and path validation."""
    
    def __init__(self, config: Optional[RAGConfig] = None):
        """Initialize the configuration manager."""
        self.config = config or get_config().rag
        self.project_root = Path(__file__).parent.parent.parent.parent
        
    def get_absolute_path(self, relative_path: str) -> Path:
        """Convert relative path to absolute path from project root."""
        if Path(relative_path).is_absolute():
            return Path(relative_path)
        return self.project_root / relative_path
    
    def validate_paths(self) -> Tuple[bool, List[str]]:
        """Validate all configured paths and return status with issues."""
        issues = []
        
        # Get all path configurations
        path_configs = {
            'vector_store_path': self.config.vector_store_path,
            'documents_path': self.config.documents_path,
            'backup_path': self.config.backup_path,
            'chat_history_path': self.config.chat_history_path,
            'temp_processing_path': self.config.temp_processing_path,
            'logs_path': self.config.logs_path
        }
        
        for path_name, path_value in path_configs.items():
            abs_path = self.get_absolute_path(path_value)
            
            # Check if path is valid
            try:
                # Check parent directory exists or can be created
                parent_dir = abs_path.parent
                if not parent_dir.exists():
                    try:
                        parent_dir.mkdir(parents=True, exist_ok=True)
                        logger.info(f"Created parent directory: {parent_dir}")
                    except PermissionError:
                        issues.append(f"{path_name}: Cannot create parent directory {parent_dir} - permission denied")
                        continue
                    except Exception as e:
                        issues.append(f"{path_name}: Cannot create parent directory {parent_dir} - {e}")
                        continue
                
                # Check if we can create the directory
                if not abs_path.exists():
                    try:
                        abs_path.mkdir(parents=True, exist_ok=True)
                        logger.info(f"Created directory: {abs_path}")
                    except PermissionError:
                        issues.append(f"{path_name}: Cannot create directory {abs_path} - permission denied")
                        continue
                    except Exception as e:
                        issues.append(f"{path_name}: Cannot create directory {abs_path} - {e}")
                        continue
                
                # Check if directory is writable
                if not os.access(abs_path, os.W_OK):
                    issues.append(f"{path_name}: Directory {abs_path} is not writable")
                
            except Exception as e:
                issues.append(f"{path_name}: Path validation failed - {e}")
        
        return len(issues) == 0, issues
    
    def create_directory_structure(self) -> bool:
        """Create the complete RAG directory structure."""
        logger.info("Creating RAG directory structure...")
        
        directories = [
            self.config.vector_store_path,
            self.config.documents_path,
            self.config.backup_path,
            self.config.chat_history_path,
            self.config.temp_processing_path,
            self.config.logs_path
        ]
        
        created_dirs = []
        failed_dirs = []
        
        for dir_path in directories:
            abs_path = self.get_absolute_path(dir_path)
            try:
                abs_path.mkdir(parents=True, exist_ok=True)
                created_dirs.append(str(abs_path))
                logger.info(f"Ensured directory exists: {abs_path}")
            except Exception as e:
                failed_dirs.append((str(abs_path), str(e)))
                logger.error(f"Failed to create directory {abs_path}: {e}")
        
        if failed_dirs:
            logger.error(f"Failed to create {len(failed_dirs)} directories")
            for path, error in failed_dirs:
                logger.error(f"  {path}: {error}")
            return False
        
        logger.info(f"Successfully ensured {len(created_dirs)} directories exist")
        return True
    
    def get_path_info(self) -> Dict[str, Dict[str, str]]:
        """Get detailed information about all configured paths."""
        path_info = {}
        
        path_configs = {
            'vector_store_path': self.config.vector_store_path,
            'documents_path': self.config.documents_path,
            'backup_path': self.config.backup_path,
            'chat_history_path': self.config.chat_history_path,
            'temp_processing_path': self.config.temp_processing_path,
            'logs_path': self.config.logs_path
        }
        
        for path_name, path_value in path_configs.items():
            abs_path = self.get_absolute_path(path_value)
            
            info = {
                'relative_path': path_value,
                'absolute_path': str(abs_path),
                'exists': abs_path.exists(),
                'is_directory': abs_path.is_dir() if abs_path.exists() else False,
                'is_writable': os.access(abs_path, os.W_OK) if abs_path.exists() else False,
                'size_mb': 0,
                'item_count': 0
            }
            
            if abs_path.exists() and abs_path.is_dir():
                try:
                    items = list(abs_path.iterdir())
                    info['item_count'] = len(items)
                    
                    # Calculate directory size
                    total_size = 0
                    for item in abs_path.rglob('*'):
                        if item.is_file():
                            try:
                                total_size += item.stat().st_size
                            except (OSError, PermissionError):
                                pass
                    info['size_mb'] = round(total_size / (1024 * 1024), 2)
                    
                except PermissionError:
                    info['item_count'] = 'Permission denied'
                    info['size_mb'] = 'Permission denied'
            
            path_info[path_name] = info
        
        return path_info
    
    def validate_configuration(self) -> Tuple[bool, List[str]]:
        """Validate the entire RAG configuration."""
        issues = []
        
        # Validate paths
        paths_valid, path_issues = self.validate_paths()
        issues.extend(path_issues)
        
        # Validate numeric settings
        if self.config.chunk_size <= 0:
            issues.append("chunk_size must be positive")
        
        if self.config.chunk_overlap < 0:
            issues.append("chunk_overlap cannot be negative")
        
        if self.config.chunk_overlap >= self.config.chunk_size:
            issues.append("chunk_overlap must be less than chunk_size")
        
        if self.config.search_k <= 0:
            issues.append("search_k must be positive")
        
        if self.config.max_document_size_mb <= 0:
            issues.append("max_document_size_mb must be positive")
        
        if self.config.similarity_threshold < 0 or self.config.similarity_threshold > 1:
            issues.append("similarity_threshold must be between 0 and 1")
        
        # Validate backup settings
        if self.config.backup_frequency_hours <= 0:
            issues.append("backup_frequency_hours must be positive")
        
        if self.config.max_backup_files <= 0:
            issues.append("max_backup_files must be positive")
        
        # Validate performance settings
        if self.config.batch_size <= 0:
            issues.append("batch_size must be positive")
        
        if self.config.max_concurrent_processing <= 0:
            issues.append("max_concurrent_processing must be positive")
        
        if self.config.cache_size_mb <= 0:
            issues.append("cache_size_mb must be positive")
        
        # Validate supported formats
        if not self.config.supported_formats:
            issues.append("supported_formats cannot be empty")
        
        return len(issues) == 0, issues
    
    def export_configuration(self, output_path: Optional[str] = None) -> str:
        """Export current configuration to JSON file."""
        config_dict = asdict(self.config)
        
        # Add path information
        config_dict['path_info'] = self.get_path_info()
        config_dict['validation_timestamp'] = str(Path(__file__).stat().st_mtime)
        
        if output_path is None:
            output_path = self.get_absolute_path("data/rag_config_export.json")
        else:
            output_path = Path(output_path)
        
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(config_dict, f, indent=2)
        
        logger.info(f"Configuration exported to: {output_path}")
        return str(output_path)
    
    def get_configuration_summary(self) -> Dict[str, any]:
        """Get a summary of the current configuration."""
        is_valid, issues = self.validate_configuration()
        path_info = self.get_path_info()
        
        return {
            'enabled': self.config.enabled,
            'is_valid': is_valid,
            'issues': issues,
            'paths': {
                'total_paths': len(path_info),
                'existing_paths': sum(1 for info in path_info.values() if info['exists']),
                'writable_paths': sum(1 for info in path_info.values() if info['is_writable']),
                'total_size_mb': sum(
                    info['size_mb'] for info in path_info.values() 
                    if isinstance(info['size_mb'], (int, float))
                )
            },
            'settings': {
                'chunk_size': self.config.chunk_size,
                'chunk_overlap': self.config.chunk_overlap,
                'search_k': self.config.search_k,
                'max_document_size_mb': self.config.max_document_size_mb,
                'supported_formats': len(self.config.supported_formats),
                'intelligent_processing': self.config.intelligent_processing,
                'auto_backup_enabled': self.config.auto_backup_enabled
            }
        }


def main():
    """Test the configuration manager."""
    print("🔧 RAG Configuration Manager Test")
    print("=" * 40)
    
    try:
        config_manager = RAGConfigManager()
        
        # Validate configuration
        is_valid, issues = config_manager.validate_configuration()
        print(f"Configuration valid: {is_valid}")
        if issues:
            print("Issues found:")
            for issue in issues:
                print(f"  - {issue}")
        
        # Create directory structure
        success = config_manager.create_directory_structure()
        print(f"Directory structure created: {success}")
        
        # Get configuration summary
        summary = config_manager.get_configuration_summary()
        print(f"Configuration summary: {json.dumps(summary, indent=2)}")
        
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
