#!/usr/bin/env python3
"""
RAG Backup and Restore Manager

Handles comprehensive backup and restore operations for the RAG system including:
- Vector store data (ChromaDB)
- Document library
- Configuration settings
- Chat history
- System metadata
"""

import os
import json
import shutil
import logging
import zipfile
import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import asdict

from ..config import RAGConfig, get_config

logger = logging.getLogger(__name__)


class RAGBackupManager:
    """Manages backup and restore operations for the RAG system."""
    
    def __init__(self, config: Optional[RAGConfig] = None):
        """Initialize the backup manager."""
        self.config = config or get_config().rag
        self.project_root = Path(__file__).parent.parent.parent.parent
        
        # Ensure backup directory exists
        self.backup_dir = self.get_absolute_path(self.config.backup_path)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
    def get_absolute_path(self, relative_path: str) -> Path:
        """Convert relative path to absolute path from project root."""
        if Path(relative_path).is_absolute():
            return Path(relative_path)
        return self.project_root / relative_path
    
    def create_backup(self, backup_name: Optional[str] = None, include_documents: bool = True, 
                     include_chat_history: bool = True, compress: bool = None) -> Dict[str, Any]:
        """
        Create a comprehensive backup of the RAG system.
        
        Args:
            backup_name: Custom name for backup (default: timestamp)
            include_documents: Whether to include document library
            include_chat_history: Whether to include chat history
            compress: Whether to compress backup (default: from config)
            
        Returns:
            dict: Backup operation results with metadata
        """
        if compress is None:
            compress = self.config.compress_backups
            
        # Generate backup name with timestamp
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        if backup_name is None:
            backup_name = f"rag_backup_{timestamp}"
        else:
            backup_name = f"{backup_name}_{timestamp}"
        
        backup_path = self.backup_dir / backup_name
        
        try:
            logger.info(f"Starting RAG backup: {backup_name}")
            
            # Create backup directory
            backup_path.mkdir(parents=True, exist_ok=True)
            
            backup_results = {
                "backup_name": backup_name,
                "timestamp": timestamp,
                "backup_path": str(backup_path),
                "compressed": compress,
                "components": {},
                "total_size_mb": 0,
                "status": "success",
                "errors": []
            }
            
            # 1. Backup vector store (ChromaDB)
            vector_store_result = self._backup_vector_store(backup_path)
            backup_results["components"]["vector_store"] = vector_store_result
            
            # 2. Backup documents if requested
            if include_documents:
                documents_result = self._backup_documents(backup_path)
                backup_results["components"]["documents"] = documents_result
            
            # 3. Backup chat history if requested
            if include_chat_history:
                chat_history_result = self._backup_chat_history(backup_path)
                backup_results["components"]["chat_history"] = chat_history_result
            
            # 4. Backup configuration
            config_result = self._backup_configuration(backup_path)
            backup_results["components"]["configuration"] = config_result
            
            # 5. Create backup metadata
            metadata_result = self._create_backup_metadata(backup_path, backup_results)
            backup_results["components"]["metadata"] = metadata_result
            
            # Calculate total backup size
            total_size = self._calculate_directory_size(backup_path)
            backup_results["total_size_mb"] = round(total_size / (1024 * 1024), 2)
            
            # 6. Compress backup if requested
            if compress:
                compressed_path = self._compress_backup(backup_path)
                if compressed_path:
                    backup_results["compressed_path"] = str(compressed_path)
                    backup_results["compressed_size_mb"] = round(
                        compressed_path.stat().st_size / (1024 * 1024), 2
                    )
                    # Remove uncompressed directory
                    shutil.rmtree(backup_path)
                    backup_results["backup_path"] = str(compressed_path)
            
            # 7. Clean up old backups if configured
            self._cleanup_old_backups()
            
            logger.info(f"RAG backup completed successfully: {backup_name}")
            logger.info(f"Backup size: {backup_results['total_size_mb']} MB")
            
            return backup_results
            
        except Exception as e:
            logger.error(f"RAG backup failed: {e}")
            backup_results["status"] = "failed"
            backup_results["errors"].append(str(e))
            
            # Clean up failed backup
            if backup_path.exists():
                try:
                    shutil.rmtree(backup_path)
                except Exception as cleanup_error:
                    logger.error(f"Failed to clean up failed backup: {cleanup_error}")
            
            return backup_results
    
    def _backup_vector_store(self, backup_path: Path) -> Dict[str, Any]:
        """Backup the ChromaDB vector store."""
        try:
            vector_store_path = self.get_absolute_path(self.config.vector_store_path)
            backup_vector_path = backup_path / "vector_store"
            
            if vector_store_path.exists():
                shutil.copytree(vector_store_path, backup_vector_path)
                size_mb = round(self._calculate_directory_size(backup_vector_path) / (1024 * 1024), 2)
                
                return {
                    "status": "success",
                    "source_path": str(vector_store_path),
                    "backup_path": str(backup_vector_path),
                    "size_mb": size_mb,
                    "collection_name": self.config.collection_name
                }
            else:
                return {
                    "status": "skipped",
                    "reason": "Vector store directory does not exist",
                    "source_path": str(vector_store_path)
                }
                
        except Exception as e:
            logger.error(f"Vector store backup failed: {e}")
            return {
                "status": "failed",
                "error": str(e)
            }
    
    def _backup_documents(self, backup_path: Path) -> Dict[str, Any]:
        """Backup the document library."""
        try:
            documents_path = self.get_absolute_path(self.config.documents_path)
            backup_docs_path = backup_path / "documents"
            
            if documents_path.exists():
                shutil.copytree(documents_path, backup_docs_path)
                
                # Count documents
                doc_count = len([f for f in backup_docs_path.rglob('*') if f.is_file()])
                size_mb = round(self._calculate_directory_size(backup_docs_path) / (1024 * 1024), 2)
                
                return {
                    "status": "success",
                    "source_path": str(documents_path),
                    "backup_path": str(backup_docs_path),
                    "document_count": doc_count,
                    "size_mb": size_mb
                }
            else:
                return {
                    "status": "skipped",
                    "reason": "Documents directory does not exist",
                    "source_path": str(documents_path)
                }
                
        except Exception as e:
            logger.error(f"Documents backup failed: {e}")
            return {
                "status": "failed",
                "error": str(e)
            }
    
    def _backup_chat_history(self, backup_path: Path) -> Dict[str, Any]:
        """Backup chat history."""
        try:
            chat_history_path = self.get_absolute_path(self.config.chat_history_path)
            backup_chat_path = backup_path / "chat_history"
            
            if chat_history_path.exists():
                shutil.copytree(chat_history_path, backup_chat_path)
                
                # Count chat files
                chat_count = len([f for f in backup_chat_path.rglob('*.json') if f.is_file()])
                size_mb = round(self._calculate_directory_size(backup_chat_path) / (1024 * 1024), 2)
                
                return {
                    "status": "success",
                    "source_path": str(chat_history_path),
                    "backup_path": str(backup_chat_path),
                    "chat_file_count": chat_count,
                    "size_mb": size_mb
                }
            else:
                return {
                    "status": "skipped",
                    "reason": "Chat history directory does not exist",
                    "source_path": str(chat_history_path)
                }
                
        except Exception as e:
            logger.error(f"Chat history backup failed: {e}")
            return {
                "status": "failed",
                "error": str(e)
            }
    
    def _backup_configuration(self, backup_path: Path) -> Dict[str, Any]:
        """Backup RAG configuration."""
        try:
            config_backup_path = backup_path / "configuration"
            config_backup_path.mkdir(parents=True, exist_ok=True)
            
            # Export RAG configuration
            config_dict = asdict(self.config)
            config_file = config_backup_path / "rag_config.json"
            
            with open(config_file, 'w') as f:
                json.dump(config_dict, f, indent=2)
            
            # Also backup the main config file if it exists
            main_config_path = self.project_root / "jarvis" / "config.yaml"
            if main_config_path.exists():
                shutil.copy2(main_config_path, config_backup_path / "main_config.yaml")
            
            size_mb = round(self._calculate_directory_size(config_backup_path) / (1024 * 1024), 2)
            
            return {
                "status": "success",
                "backup_path": str(config_backup_path),
                "size_mb": size_mb,
                "files_backed_up": ["rag_config.json", "main_config.yaml"]
            }
            
        except Exception as e:
            logger.error(f"Configuration backup failed: {e}")
            return {
                "status": "failed",
                "error": str(e)
            }
    
    def _create_backup_metadata(self, backup_path: Path, backup_results: Dict[str, Any]) -> Dict[str, Any]:
        """Create backup metadata file."""
        try:
            metadata = {
                "backup_info": {
                    "name": backup_results["backup_name"],
                    "timestamp": backup_results["timestamp"],
                    "created_by": "RAG Backup Manager",
                    "version": "1.0"
                },
                "system_info": {
                    "rag_enabled": self.config.enabled,
                    "collection_name": self.config.collection_name,
                    "chunk_size": self.config.chunk_size,
                    "chunk_overlap": self.config.chunk_overlap
                },
                "backup_components": backup_results["components"],
                "restore_instructions": {
                    "note": "Use RAGBackupManager.restore_backup() to restore this backup",
                    "requirements": ["ChromaDB", "RAG system configuration"]
                }
            }
            
            metadata_file = backup_path / "backup_metadata.json"
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            return {
                "status": "success",
                "metadata_file": str(metadata_file),
                "size_mb": round(metadata_file.stat().st_size / (1024 * 1024), 4)
            }
            
        except Exception as e:
            logger.error(f"Metadata creation failed: {e}")
            return {
                "status": "failed",
                "error": str(e)
            }
    
    def _compress_backup(self, backup_path: Path) -> Optional[Path]:
        """Compress backup directory to ZIP file."""
        try:
            zip_path = backup_path.with_suffix('.zip')
            
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_path in backup_path.rglob('*'):
                    if file_path.is_file():
                        arcname = file_path.relative_to(backup_path)
                        zipf.write(file_path, arcname)
            
            logger.info(f"Backup compressed to: {zip_path}")
            return zip_path
            
        except Exception as e:
            logger.error(f"Backup compression failed: {e}")
            return None
    
    def _calculate_directory_size(self, directory: Path) -> int:
        """Calculate total size of directory in bytes."""
        total_size = 0
        try:
            for file_path in directory.rglob('*'):
                if file_path.is_file():
                    total_size += file_path.stat().st_size
        except (OSError, PermissionError) as e:
            logger.warning(f"Could not calculate size for some files in {directory}: {e}")
        return total_size
    
    def _cleanup_old_backups(self):
        """Remove old backups based on configuration."""
        try:
            if not self.config.auto_backup_enabled or self.config.max_backup_files <= 0:
                return
            
            # Get all backup files/directories
            backup_items = []
            for item in self.backup_dir.iterdir():
                if item.name.startswith('rag_backup_'):
                    backup_items.append((item.stat().st_mtime, item))
            
            # Sort by modification time (newest first)
            backup_items.sort(reverse=True)
            
            # Remove excess backups
            if len(backup_items) > self.config.max_backup_files:
                items_to_remove = backup_items[self.config.max_backup_files:]
                
                for _, item_path in items_to_remove:
                    try:
                        if item_path.is_dir():
                            shutil.rmtree(item_path)
                        else:
                            item_path.unlink()
                        logger.info(f"Removed old backup: {item_path.name}")
                    except Exception as e:
                        logger.error(f"Failed to remove old backup {item_path}: {e}")
                        
        except Exception as e:
            logger.error(f"Backup cleanup failed: {e}")
    
    def list_backups(self) -> List[Dict[str, Any]]:
        """List all available backups with metadata."""
        backups = []
        
        try:
            for item in self.backup_dir.iterdir():
                # Include any backup file/directory that contains 'backup' or 'test' and has timestamp pattern
                if (('backup' in item.name or 'test' in item.name) and
                    ('_202' in item.name or '_201' in item.name) and  # Basic timestamp check
                    not item.name.startswith('.')):  # Exclude hidden files
                    backup_info = {
                        "name": item.name,
                        "path": str(item),
                        "is_compressed": item.suffix == '.zip',
                        "created": datetime.datetime.fromtimestamp(item.stat().st_mtime).isoformat(),
                        "size_mb": round(item.stat().st_size / (1024 * 1024), 2)
                    }
                    
                    # Try to read metadata if available
                    if item.is_dir():
                        metadata_file = item / "backup_metadata.json"
                        if metadata_file.exists():
                            try:
                                with open(metadata_file, 'r') as f:
                                    metadata = json.load(f)
                                backup_info["metadata"] = metadata
                            except Exception as e:
                                logger.warning(f"Could not read metadata for {item.name}: {e}")
                    
                    backups.append(backup_info)
            
            # Sort by creation time (newest first)
            backups.sort(key=lambda x: x["created"], reverse=True)
            
        except Exception as e:
            logger.error(f"Failed to list backups: {e}")
        
        return backups

    def restore_backup(self, backup_name: str, restore_vector_store: bool = True,
                      restore_documents: bool = True, restore_chat_history: bool = True,
                      backup_current: bool = True) -> Dict[str, Any]:
        """
        Restore RAG system from backup.

        Args:
            backup_name: Name of backup to restore
            restore_vector_store: Whether to restore vector store
            restore_documents: Whether to restore documents
            restore_chat_history: Whether to restore chat history
            backup_current: Whether to backup current state before restore

        Returns:
            dict: Restore operation results
        """
        try:
            logger.info(f"Starting RAG restore from backup: {backup_name}")

            # Find backup
            backup_path = self._find_backup(backup_name)
            if not backup_path:
                return {
                    "status": "failed",
                    "error": f"Backup not found: {backup_name}",
                    "available_backups": [b["name"] for b in self.list_backups()]
                }

            # Extract if compressed
            if backup_path.suffix == '.zip':
                backup_path = self._extract_backup(backup_path)
                if not backup_path:
                    return {
                        "status": "failed",
                        "error": f"Failed to extract compressed backup: {backup_name}"
                    }

            restore_results = {
                "backup_name": backup_name,
                "timestamp": datetime.datetime.now().isoformat(),
                "components_restored": {},
                "status": "success",
                "errors": []
            }

            # Backup current state if requested
            if backup_current:
                current_backup = self.create_backup(
                    backup_name=f"pre_restore_{backup_name}",
                    compress=True
                )
                restore_results["current_backup"] = current_backup

            # Restore components
            if restore_vector_store:
                vector_result = self._restore_vector_store(backup_path)
                restore_results["components_restored"]["vector_store"] = vector_result

            if restore_documents:
                docs_result = self._restore_documents(backup_path)
                restore_results["components_restored"]["documents"] = docs_result

            if restore_chat_history:
                chat_result = self._restore_chat_history(backup_path)
                restore_results["components_restored"]["chat_history"] = chat_result

            # Check for any failures
            failed_components = [
                name for name, result in restore_results["components_restored"].items()
                if result.get("status") == "failed"
            ]

            if failed_components:
                restore_results["status"] = "partial"
                restore_results["failed_components"] = failed_components

            logger.info(f"RAG restore completed: {restore_results['status']}")
            return restore_results

        except Exception as e:
            logger.error(f"RAG restore failed: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "backup_name": backup_name
            }

    def _find_backup(self, backup_name: str) -> Optional[Path]:
        """Find backup by name."""
        # Try exact match first
        backup_path = self.backup_dir / backup_name
        if backup_path.exists():
            return backup_path

        # Try with .zip extension
        zip_path = self.backup_dir / f"{backup_name}.zip"
        if zip_path.exists():
            return zip_path

        # Try partial match
        for item in self.backup_dir.iterdir():
            if backup_name in item.name:
                return item

        return None

    def _extract_backup(self, zip_path: Path) -> Optional[Path]:
        """Extract compressed backup."""
        try:
            extract_path = zip_path.with_suffix('')

            with zipfile.ZipFile(zip_path, 'r') as zipf:
                zipf.extractall(extract_path)

            logger.info(f"Extracted backup to: {extract_path}")
            return extract_path

        except Exception as e:
            logger.error(f"Failed to extract backup {zip_path}: {e}")
            return None

    def _restore_vector_store(self, backup_path: Path) -> Dict[str, Any]:
        """Restore vector store from backup."""
        try:
            backup_vector_path = backup_path / "vector_store"
            current_vector_path = self.get_absolute_path(self.config.vector_store_path)

            if not backup_vector_path.exists():
                return {
                    "status": "skipped",
                    "reason": "Vector store not found in backup"
                }

            # Remove current vector store
            if current_vector_path.exists():
                shutil.rmtree(current_vector_path)

            # Restore from backup
            shutil.copytree(backup_vector_path, current_vector_path)

            size_mb = round(self._calculate_directory_size(current_vector_path) / (1024 * 1024), 2)

            return {
                "status": "success",
                "restored_path": str(current_vector_path),
                "size_mb": size_mb
            }

        except Exception as e:
            logger.error(f"Vector store restore failed: {e}")
            return {
                "status": "failed",
                "error": str(e)
            }

    def _restore_documents(self, backup_path: Path) -> Dict[str, Any]:
        """Restore documents from backup."""
        try:
            backup_docs_path = backup_path / "documents"
            current_docs_path = self.get_absolute_path(self.config.documents_path)

            if not backup_docs_path.exists():
                return {
                    "status": "skipped",
                    "reason": "Documents not found in backup"
                }

            # Remove current documents
            if current_docs_path.exists():
                shutil.rmtree(current_docs_path)

            # Restore from backup
            shutil.copytree(backup_docs_path, current_docs_path)

            doc_count = len([f for f in current_docs_path.rglob('*') if f.is_file()])
            size_mb = round(self._calculate_directory_size(current_docs_path) / (1024 * 1024), 2)

            return {
                "status": "success",
                "restored_path": str(current_docs_path),
                "document_count": doc_count,
                "size_mb": size_mb
            }

        except Exception as e:
            logger.error(f"Documents restore failed: {e}")
            return {
                "status": "failed",
                "error": str(e)
            }

    def _restore_chat_history(self, backup_path: Path) -> Dict[str, Any]:
        """Restore chat history from backup."""
        try:
            backup_chat_path = backup_path / "chat_history"
            current_chat_path = self.get_absolute_path(self.config.chat_history_path)

            if not backup_chat_path.exists():
                return {
                    "status": "skipped",
                    "reason": "Chat history not found in backup"
                }

            # Remove current chat history
            if current_chat_path.exists():
                shutil.rmtree(current_chat_path)

            # Restore from backup
            shutil.copytree(backup_chat_path, current_chat_path)

            chat_count = len([f for f in current_chat_path.rglob('*.json') if f.is_file()])
            size_mb = round(self._calculate_directory_size(current_chat_path) / (1024 * 1024), 2)

            return {
                "status": "success",
                "restored_path": str(current_chat_path),
                "chat_file_count": chat_count,
                "size_mb": size_mb
            }

        except Exception as e:
            logger.error(f"Chat history restore failed: {e}")
            return {
                "status": "failed",
                "error": str(e)
            }

    def delete_backup(self, backup_name: str) -> Dict[str, Any]:
        """Delete a backup."""
        try:
            backup_path = self._find_backup(backup_name)
            if not backup_path:
                return {
                    "status": "failed",
                    "error": f"Backup not found: {backup_name}"
                }

            if backup_path.is_dir():
                shutil.rmtree(backup_path)
            else:
                backup_path.unlink()

            logger.info(f"Deleted backup: {backup_name}")
            return {
                "status": "success",
                "deleted_backup": backup_name,
                "deleted_path": str(backup_path)
            }

        except Exception as e:
            logger.error(f"Failed to delete backup {backup_name}: {e}")
            return {
                "status": "failed",
                "error": str(e)
            }
