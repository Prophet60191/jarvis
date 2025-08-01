#!/usr/bin/env python3
"""
RAG Management Desktop Application

Native desktop app for RAG document and memory management using pywebview.
This creates a native window that displays the RAG management interface
without requiring a separate browser.

Usage:
    python rag_app.py
    python rag_app.py --panel upload
    python rag_app.py --panel documents
"""

import argparse
import sys
import os
import threading
import signal
import time
import logging
import json
from pathlib import Path
from typing import Dict, Any, Optional

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "jarvis"))

try:
    import webview
    WEBVIEW_AVAILABLE = True
except ImportError:
    WEBVIEW_AVAILABLE = False
    print("⚠️  pywebview not installed. Install with: pip install pywebview")

logger = logging.getLogger(__name__)

# Import RAG components
try:
    from jarvis.config import get_config
    from jarvis.tools.rag_service import RAGService
    # Try to import real Database Agent, fallback to mock
    try:
        from jarvis.tools.database_agent import get_database_agent
    except ImportError:
        logger.info("Using mock Database Agent for testing")
        from jarvis.tools.mock_database_agent import get_database_agent
    RAG_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Could not import RAG components: {e}")
    RAG_AVAILABLE = False


class RAGManager:
    """Manages RAG system operations for the desktop interface."""

    def __init__(self):
        self.config = get_config() if RAG_AVAILABLE else None
        self.rag_service = None
        self.database_agent = None
        
    def get_rag_service(self):
        """Get or create RAG service instance."""
        if not self.rag_service and RAG_AVAILABLE:
            try:
                self.rag_service = RAGService(self.config)
                return self.rag_service
            except Exception as e:
                logger.error(f"Failed to initialize RAG service: {e}")
        return self.rag_service
    
    def get_database_agent(self):
        """Get or create Database Agent instance."""
        if not self.database_agent and RAG_AVAILABLE:
            try:
                self.database_agent = get_database_agent(self.config)
                return self.database_agent
            except Exception as e:
                logger.error(f"Failed to initialize Database Agent: {e}")
        return self.database_agent

    def get_documents_info(self) -> Dict[str, Any]:
        """Get information about documents in the system."""
        if not RAG_AVAILABLE:
            return {"error": "RAG system not available"}
        
        try:
            documents_path = Path(self.config.rag.documents_path)
            if not documents_path.exists():
                documents_path.mkdir(parents=True, exist_ok=True)
                return {"documents": [], "total": 0, "path": str(documents_path)}
            
            documents = []
            supported_extensions = {'.txt', '.pdf', '.doc', '.docx'}
            
            for file_path in documents_path.iterdir():
                if file_path.is_file() and file_path.suffix.lower() in supported_extensions:
                    stat = file_path.stat()
                    documents.append({
                        "name": file_path.name,
                        "size": stat.st_size,
                        "modified": time.ctime(stat.st_mtime),
                        "extension": file_path.suffix.lower()
                    })
            
            return {
                "documents": sorted(documents, key=lambda x: x["name"]),
                "total": len(documents),
                "path": str(documents_path)
            }
        except Exception as e:
            logger.error(f"Error getting documents info: {e}")
            return {"error": str(e)}

    def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory and conversation statistics."""
        if not RAG_AVAILABLE:
            return {"error": "RAG system not available"}
        
        try:
            rag_service = self.get_rag_service()
            if not rag_service:
                return {"error": "RAG service not initialized"}
            
            # Get collection info from ChromaDB
            collection = rag_service.vector_store._collection
            count = collection.count()
            
            return {
                "total_memories": count,
                "conversation_memories": count,  # TODO: Separate by type
                "document_memories": 0,  # TODO: Implement document memory count
                "database_status": "Connected",
                "model": self.config.llm.model if self.config else "Unknown",
                "database_agent": "Qwen2.5:3b-instruct (Ready)"
            }
        except Exception as e:
            logger.error(f"Error getting memory stats: {e}")
            return {"error": str(e)}

    async def upload_document(self, file_content: str, filename: str) -> Dict[str, Any]:
        """Upload and process a document using the Database Agent."""
        if not RAG_AVAILABLE:
            return {"error": "RAG system not available"}

        try:
            # Save file to documents directory
            documents_path = Path(self.config.rag.documents_path)
            documents_path.mkdir(parents=True, exist_ok=True)

            file_path = documents_path / filename
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(file_content)

            # Process with Database Agent for intelligent analysis
            db_agent = self.get_database_agent()
            if db_agent:
                try:
                    # Get existing data for comparison
                    existing_data = self._get_existing_document_data(filename)

                    # Process document with Database Agent
                    merge_plan = await db_agent.process_document_upload(
                        content=file_content,
                        filename=filename,
                        existing_data=existing_data
                    )

                    # Execute the merge plan (integrate with RAG system)
                    await self._execute_merge_plan(merge_plan)

                    return {
                        "success": True,
                        "message": f"Document '{filename}' processed intelligently",
                        "filename": filename,
                        "size": len(file_content),
                        "path": str(file_path),
                        "processing": {
                            "document_type": merge_plan.document_source,
                            "entities_processed": merge_plan.total_entities,
                            "summary": merge_plan.summary,
                            "processing_time": merge_plan.estimated_processing_time,
                            "warnings": merge_plan.warnings
                        }
                    }

                except Exception as e:
                    logger.error(f"Database Agent processing failed: {e}")
                    # Fallback to basic upload
                    return {
                        "success": True,
                        "message": f"Document '{filename}' uploaded (basic processing)",
                        "filename": filename,
                        "size": len(file_content),
                        "path": str(file_path),
                        "processing": {
                            "note": "Database Agent processing failed, used basic upload",
                            "error": str(e)
                        }
                    }
            else:
                return {
                    "success": True,
                    "message": f"Document '{filename}' uploaded (Database Agent not available)",
                    "filename": filename,
                    "size": len(file_content),
                    "path": str(file_path)
                }

        except Exception as e:
            logger.error(f"Error uploading document: {e}")
            return {"error": str(e)}

    def _get_existing_document_data(self, filename: str) -> list:
        """Get existing data for a document to enable intelligent merging."""
        try:
            # TODO: Query RAG system for existing document data
            # For now, return empty list (no existing data)
            return []
        except Exception as e:
            logger.error(f"Error getting existing document data: {e}")
            return []

    async def _execute_merge_plan(self, merge_plan) -> None:
        """Execute the Database Agent merge plan by updating the RAG system."""
        try:
            # Get RAG service
            rag_service = self.get_rag_service()
            if not rag_service:
                logger.warning("RAG service not available for merge plan execution")
                return

            # Add document processing summary to conversational memory
            summary = f"Processed document: {merge_plan.document_source} - {merge_plan.summary}"
            rag_service.add_conversational_memory(summary)

            # TODO: Implement detailed merge plan execution
            # - Update existing entities
            # - Add new entities
            # - Mark outdated entities
            # - Maintain version history

            logger.info(f"Executed merge plan for {merge_plan.document_source}")

        except Exception as e:
            logger.error(f"Error executing merge plan: {e}")
            raise


class RAGDesktopApp:
    """Native desktop application for RAG Management."""

    def __init__(self, panel: str = "main", debug: bool = False):
        """
        Initialize the RAG desktop application.

        Args:
            panel: Initial panel to display
            debug: Enable debug mode
        """
        self.panel = panel
        self.debug = debug
        self.rag_manager = RAGManager()

    def upload_file_api(self, filename: str, content: str) -> Dict[str, Any]:
        """API method for JavaScript to upload files."""
        try:
            import asyncio
            # Run the async upload method
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(
                    self.rag_manager.upload_document(content, filename)
                )
                return result
            finally:
                loop.close()
        except Exception as e:
            logger.error(f"Error in upload API: {e}")
            return {"error": str(e)}

    def get_status_api(self) -> Dict[str, Any]:
        """API method for JavaScript to get system status."""
        try:
            docs_info = self.rag_manager.get_documents_info()
            memory_stats = self.rag_manager.get_memory_stats()
            return {
                "documents": docs_info,
                "memory": memory_stats,
                "database_agent": "Qwen2.5:3b-instruct (Ready)"
            }
        except Exception as e:
            logger.error(f"Error in status API: {e}")
            return {"error": str(e)}
        
    def get_html_content(self) -> str:
        """Get the complete HTML content for the RAG Management interface."""
        # Get current data
        docs_info = self.rag_manager.get_documents_info()
        memory_stats = self.rag_manager.get_memory_stats()
        
        return f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>RAG Management - {self.panel.title()}</title>
            <style>
                * {{
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }}

                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    margin: 0;
                    padding: 0;
                    background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 50%, #16213e 100%);
                    min-height: 100vh;
                    color: #e0e6ed;
                    display: flex;
                }}

                .sidebar {{
                    width: 280px;
                    background: rgba(255, 255, 255, 0.05);
                    backdrop-filter: blur(10px);
                    border-right: 1px solid rgba(255, 255, 255, 0.1);
                    padding: 20px 0;
                    position: fixed;
                    height: 100vh;
                    overflow-y: auto;
                    z-index: 1000;
                }}

                .sidebar-header {{
                    padding: 0 20px 30px 20px;
                    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
                    margin-bottom: 20px;
                }}

                .sidebar-header h1 {{
                    color: #ffffff;
                    margin: 0;
                    font-size: 1.8em;
                    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
                    text-align: center;
                }}

                .sidebar-header .subtitle {{
                    color: #b8c5d1;
                    font-size: 0.9em;
                    text-align: center;
                    margin-top: 5px;
                }}

                .nav {{
                    padding: 0 10px;
                }}

                .nav-section {{
                    margin-bottom: 25px;
                }}

                .nav-section-title {{
                    font-size: 12px;
                    font-weight: 600;
                    color: #8892b0;
                    text-transform: uppercase;
                    letter-spacing: 1px;
                    margin-bottom: 10px;
                    padding: 0 10px;
                }}

                .nav-link {{
                    display: flex;
                    align-items: center;
                    padding: 12px 15px;
                    margin: 2px 0;
                    border-radius: 8px;
                    text-decoration: none;
                    color: #b8c5d1;
                    transition: all 0.2s ease;
                    cursor: pointer;
                    border: 1px solid transparent;
                }}

                .nav-link:hover {{
                    background: rgba(100, 255, 218, 0.1);
                    color: #64ffda;
                    border-color: rgba(100, 255, 218, 0.2);
                }}

                .nav-link.active {{
                    background: rgba(100, 255, 218, 0.15);
                    color: #64ffda;
                    border-color: rgba(100, 255, 218, 0.3);
                    box-shadow: 0 2px 8px rgba(100, 255, 218, 0.2);
                }}

                .main-content {{
                    flex: 1;
                    margin-left: 280px;
                    padding: 20px;
                    min-height: 100vh;
                }}
                
                .page-header {{
                    margin-bottom: 30px;
                    padding-bottom: 20px;
                    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
                }}

                .page-header h1 {{
                    font-size: 2.2em;
                    color: #ffffff;
                    margin-bottom: 10px;
                    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
                }}

                .breadcrumb {{
                    color: #8892b0;
                    font-size: 14px;
                }}

                .stats-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
                    gap: 20px;
                    margin-bottom: 30px;
                }}

                .stat-card {{
                    background: rgba(255, 255, 255, 0.05);
                    backdrop-filter: blur(10px);
                    padding: 25px;
                    border-radius: 12px;
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
                    transition: all 0.3s ease;
                }}

                .stat-card:hover {{
                    background: rgba(255, 255, 255, 0.08);
                    border-color: rgba(100, 255, 218, 0.3);
                    transform: translateY(-2px);
                    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
                }}

                .stat-card h3 {{
                    font-size: 18px;
                    color: #ffffff;
                    margin-bottom: 15px;
                    display: flex;
                    align-items: center;
                }}

                .stat-value {{
                    font-size: 28px;
                    font-weight: 700;
                    color: #64ffda;
                    margin-bottom: 5px;
                }}

                .stat-label {{
                    color: #8892b0;
                    font-size: 14px;
                }}
                
                .upload-area {{
                    background: rgba(255, 255, 255, 0.05);
                    backdrop-filter: blur(10px);
                    border: 2px dashed rgba(255, 255, 255, 0.2);
                    border-radius: 12px;
                    padding: 40px;
                    text-align: center;
                    margin: 20px 0;
                    transition: all 0.3s ease;
                }}

                .upload-area:hover {{
                    border-color: rgba(100, 255, 218, 0.5);
                    background: rgba(100, 255, 218, 0.05);
                }}

                .upload-area.dragover {{
                    border-color: #64ffda;
                    background: rgba(100, 255, 218, 0.1);
                    box-shadow: 0 0 20px rgba(100, 255, 218, 0.3);
                }}

                .upload-icon {{
                    font-size: 48px;
                    color: #8892b0;
                    margin-bottom: 15px;
                }}

                .upload-text {{
                    font-size: 18px;
                    color: #ffffff;
                    margin-bottom: 10px;
                }}

                .upload-subtext {{
                    color: #8892b0;
                    font-size: 14px;
                }}

                .btn {{
                    background: linear-gradient(135deg, #64ffda 0%, #4fd1c7 100%);
                    color: #0f0f23;
                    border: none;
                    padding: 12px 24px;
                    border-radius: 8px;
                    font-size: 14px;
                    font-weight: 600;
                    cursor: pointer;
                    transition: all 0.3s ease;
                    margin: 10px 5px;
                    box-shadow: 0 4px 12px rgba(100, 255, 218, 0.3);
                }}

                .btn:hover {{
                    transform: translateY(-2px);
                    box-shadow: 0 6px 16px rgba(100, 255, 218, 0.4);
                }}

                .btn-secondary {{
                    background: rgba(255, 255, 255, 0.1);
                    color: #e0e6ed;
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
                }}

                .btn-secondary:hover {{
                    background: rgba(255, 255, 255, 0.15);
                    transform: translateY(-2px);
                    box-shadow: 0 6px 16px rgba(0, 0, 0, 0.3);
                }}
                
                .document-list {{
                    background: rgba(255, 255, 255, 0.05);
                    backdrop-filter: blur(10px);
                    border-radius: 12px;
                    overflow: hidden;
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
                }}

                .document-item {{
                    padding: 15px 20px;
                    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
                    display: flex;
                    align-items: center;
                    justify-content: between;
                    transition: all 0.2s ease;
                }}

                .document-item:hover {{
                    background: rgba(255, 255, 255, 0.05);
                }}

                .document-item:last-child {{
                    border-bottom: none;
                }}

                .document-info {{
                    flex: 1;
                }}

                .document-name {{
                    font-weight: 500;
                    color: #ffffff;
                    margin-bottom: 5px;
                }}

                .document-meta {{
                    font-size: 12px;
                    color: #8892b0;
                }}
                
                .hidden {{
                    display: none;
                }}

                #file-input {{
                    display: none;
                }}

                .processing-spinner {{
                    font-size: 18px;
                    font-weight: 500;
                    color: #64ffda;
                    margin-bottom: 10px;
                }}

                .progress-bar {{
                    background: rgba(255, 255, 255, 0.1);
                    height: 6px;
                    border-radius: 3px;
                    overflow: hidden;
                    margin: 10px 0;
                }}

                .progress-fill {{
                    background: linear-gradient(90deg, #64ffda, #4fd1c7);
                    height: 100%;
                    border-radius: 3px;
                    transition: width 0.3s ease;
                    box-shadow: 0 0 10px rgba(100, 255, 218, 0.5);
                }}

                .result-item {{
                    margin: 15px 0;
                    padding: 15px;
                    border-radius: 8px;
                    border-left: 4px solid;
                    background: rgba(255, 255, 255, 0.05);
                    backdrop-filter: blur(10px);
                }}

                .result-success {{
                    border-left-color: #64ffda;
                    box-shadow: 0 0 10px rgba(100, 255, 218, 0.2);
                }}

                .result-error {{
                    border-left-color: #ff6b6b;
                    box-shadow: 0 0 10px rgba(255, 107, 107, 0.2);
                }}

                .result-title {{
                    margin: 0 0 10px 0;
                    font-weight: 500;
                }}

                .result-success .result-title {{
                    color: #64ffda;
                }}

                .result-error .result-title {{
                    color: #ff6b6b;
                }}
            </style>
        </head>
        <body>
            <div class="app-container">
                <div class="sidebar">
                    <div class="sidebar-header">
                        <h1>RAG Management</h1>
                        <div class="subtitle">Document & Memory System</div>
                    </div>

                    <nav class="nav">
                        <div class="nav-section">
                            <div class="nav-section-title">Navigation</div>
                            <div class="nav-link {'active' if self.panel == 'main' else ''}" onclick="showPanel('main')">
                                Dashboard
                            </div>
                            <div class="nav-link {'active' if self.panel == 'upload' else ''}" onclick="showPanel('upload')">
                                Upload
                            </div>
                            <div class="nav-link {'active' if self.panel == 'documents' else ''}" onclick="showPanel('documents')">
                                Documents
                            </div>
                            <div class="nav-link {'active' if self.panel == 'memory' else ''}" onclick="showPanel('memory')">
                                Memory
                            </div>
                            <div class="nav-link {'active' if self.panel == 'settings' else ''}" onclick="showPanel('settings')">
                                Settings
                            </div>
                        </div>
                    </nav>
                </div>
                
                <div class="main-content">
                    <!-- Main Dashboard Panel -->
                    <div id="main-panel" class="panel {'hidden' if self.panel != 'main' else ''}">
                        <div class="page-header">
                            <h1>RAG Management Dashboard</h1>
                            <div class="breadcrumb">Home / Dashboard</div>
                        </div>
                        
                        <div class="stats-grid">
                            <div class="stat-card">
                                <h3>Documents</h3>
                                <div class="stat-value">{docs_info.get('total', 0)}</div>
                                <div class="stat-label">Files in library</div>
                            </div>
                            <div class="stat-card">
                                <h3>Memories</h3>
                                <div class="stat-value">{memory_stats.get('total_memories', 0)}</div>
                                <div class="stat-label">Stored memories</div>
                            </div>
                            <div class="stat-card">
                                <h3>Database Agent</h3>
                                <div class="stat-value">Ready</div>
                                <div class="stat-label">Qwen2.5:3b-instruct</div>
                            </div>
                            <div class="stat-card">
                                <h3>Storage</h3>
                                <div class="stat-value">Active</div>
                                <div class="stat-label">ChromaDB connected</div>
                            </div>
                        </div>

                        <div class="stat-card">
                            <h3>Quick Actions</h3>
                            <button class="btn" onclick="showPanel('upload')">Upload Documents</button>
                            <button class="btn btn-secondary" onclick="showPanel('documents')">Browse Library</button>
                            <button class="btn btn-secondary" onclick="showPanel('memory')">View Memories</button>
                        </div>
                    </div>
                    
                    <!-- Upload Panel -->
                    <div id="upload-panel" class="panel {'hidden' if self.panel != 'upload' else ''}">
                        <div class="page-header">
                            <h1>Document Upload</h1>
                            <div class="breadcrumb">Home / Upload</div>
                        </div>
                        
                        <div class="upload-area" id="upload-area" onclick="document.getElementById('file-input').click()">
                            <div class="upload-text">Drop files here or click to browse</div>
                            <div class="upload-subtext">Supports: TXT, PDF, DOC, DOCX</div>
                        </div>

                        <input type="file" id="file-input" multiple accept=".txt,.pdf,.doc,.docx">

                        <!-- Processing Status -->
                        <div id="processing-status" class="stat-card hidden">
                            <h3>Database Agent Processing</h3>
                            <div id="processing-content">
                                <div class="processing-spinner">Processing...</div>
                            </div>
                        </div>

                        <!-- Processing Results -->
                        <div id="processing-results" class="stat-card hidden">
                            <h3>Processing Complete</h3>
                            <div id="results-content"></div>
                        </div>

                        <div class="stat-card">
                            <h3>Intelligent Processing Features</h3>
                            <p>Documents are processed by the Database Agent (Qwen2.5:3b-instruct) for:</p>
                            <ul style="margin: 15px 0; padding-left: 20px; color: #b8c5d1;">
                                <li><strong>Document Structure Analysis:</strong> Understands content organization</li>
                                <li><strong>Entity Extraction:</strong> Identifies contacts, data, relationships</li>
                                <li><strong>Intelligent Comparison:</strong> Compares with existing data</li>
                                <li><strong>Smart Merging:</strong> Updates only what changed</li>
                                <li><strong>Version Tracking:</strong> Maintains history without deletion</li>
                            </ul>
                            <div style="margin-top: 15px; padding: 15px; background: rgba(100, 255, 218, 0.1); border-radius: 8px; border-left: 3px solid #64ffda;">
                                <strong style="color: #64ffda;">Example:</strong> <span style="color: #b8c5d1;">Upload updated contacts → Agent detects Mary's phone changed → Updates only Mary's number → Keeps John's info unchanged → Adds new contact Bob</span>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Documents Panel -->
                    <div id="documents-panel" class="panel {'hidden' if self.panel != 'documents' else ''}">
                        <div class="page-header">
                            <h1>Document Library</h1>
                            <div class="breadcrumb">Home / Documents</div>
                        </div>
                        
                        <div class="stat-card">
                            <h3>Storage Location</h3>
                            <p style="color: #8892b0; font-family: monospace; background: rgba(255, 255, 255, 0.05); padding: 8px; border-radius: 4px;">{docs_info.get('path', 'Not configured')}</p>
                        </div>

                        <div class="document-list">
                            {''.join([f'''
                            <div class="document-item">
                                <div class="document-info">
                                    <div class="document-name">{doc["name"]}</div>
                                    <div class="document-meta">Size: {doc["size"]} bytes • Modified: {doc["modified"]}</div>
                                </div>
                            </div>
                            ''' for doc in docs_info.get('documents', [])]) if docs_info.get('documents') else '<div class="document-item"><div class="document-info"><div class="document-name">No documents found</div><div class="document-meta">Upload some documents to get started</div></div></div>'}
                        </div>
                    </div>
                    
                    <!-- Memory Panel -->
                    <div id="memory-panel" class="panel {'hidden' if self.panel != 'memory' else ''}">
                        <div class="page-header">
                            <h1>Memory Management</h1>
                            <div class="breadcrumb">Home / Memory</div>
                        </div>
                        
                        <div class="stats-grid">
                            <div class="stat-card">
                                <h3>Conversations</h3>
                                <div class="stat-value">{memory_stats.get('conversation_memories', 0)}</div>
                                <div class="stat-label">Chat memories</div>
                            </div>
                            <div class="stat-card">
                                <h3>Documents</h3>
                                <div class="stat-value">{memory_stats.get('document_memories', 0)}</div>
                                <div class="stat-label">Document memories</div>
                            </div>
                        </div>

                        <div class="stat-card">
                            <h3>Memory System Status</h3>
                            <div style="margin: 15px 0;">
                                <p style="margin: 8px 0; color: #b8c5d1;"><strong style="color: #64ffda;">Database:</strong> {memory_stats.get('database_status', 'Unknown')}</p>
                                <p style="margin: 8px 0; color: #b8c5d1;"><strong style="color: #64ffda;">Model:</strong> {memory_stats.get('model', 'Unknown')}</p>
                                <p style="margin: 8px 0; color: #b8c5d1;"><strong style="color: #64ffda;">Database Agent:</strong> {memory_stats.get('database_agent', 'Unknown')}</p>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Settings Panel -->
                    <div id="settings-panel" class="panel {'hidden' if self.panel != 'settings' else ''}">
                        <div class="page-header">
                            <h1>RAG Settings</h1>
                            <div class="breadcrumb">Home / Settings</div>
                        </div>
                        
                        <div class="stat-card">
                            <h3>Database Agent Configuration</h3>
                            <div style="margin: 15px 0;">
                                <p style="margin: 8px 0; color: #b8c5d1;"><strong style="color: #64ffda;">Model:</strong> Qwen2.5:3b-instruct</p>
                                <p style="margin: 8px 0; color: #b8c5d1;"><strong style="color: #64ffda;">Purpose:</strong> Intelligent document processing</p>
                                <p style="margin: 8px 0; color: #b8c5d1;"><strong style="color: #64ffda;">Features:</strong> Entity extraction, data merging, version tracking</p>
                            </div>
                        </div>

                        <div class="stat-card">
                            <h3>RAG System Configuration</h3>
                            <div style="margin: 15px 0;">
                                <p style="margin: 8px 0; color: #b8c5d1;"><strong style="color: #64ffda;">Vector Store:</strong> ChromaDB</p>
                                <p style="margin: 8px 0; color: #b8c5d1;"><strong style="color: #64ffda;">Main Model:</strong> {memory_stats.get('model', 'Unknown')}</p>
                                <p style="margin: 8px 0; color: #b8c5d1;"><strong style="color: #64ffda;">Document Path:</strong></p>
                                <div style="font-family: monospace; background: rgba(255, 255, 255, 0.05); padding: 8px; border-radius: 4px; color: #8892b0; margin-top: 5px;">{docs_info.get('path', 'Not configured')}</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <script>
                function showPanel(panelName) {{
                    // Hide all panels
                    const panels = document.querySelectorAll('.panel');
                    panels.forEach(panel => panel.classList.add('hidden'));
                    
                    // Show selected panel
                    const targetPanel = document.getElementById(panelName + '-panel');
                    if (targetPanel) {{
                        targetPanel.classList.remove('hidden');
                    }}
                    
                    // Update active nav
                    const navLinks = document.querySelectorAll('.nav-link');
                    navLinks.forEach(link => link.classList.remove('active'));
                    
                    const activeLink = document.querySelector(`.nav-link[onclick="showPanel('${{panelName}}')"]`);
                    if (activeLink) {{
                        activeLink.classList.add('active');
                    }}
                }}
                
                // File upload handling with Database Agent processing
                document.getElementById('file-input').addEventListener('change', function(e) {{
                    const files = e.target.files;
                    if (files.length > 0) {{
                        processFiles(files);
                    }}
                }});

                // Drag and drop handling
                const uploadArea = document.querySelector('.upload-area');

                uploadArea.addEventListener('dragover', function(e) {{
                    e.preventDefault();
                    uploadArea.classList.add('dragover');
                }});

                uploadArea.addEventListener('dragleave', function(e) {{
                    e.preventDefault();
                    uploadArea.classList.remove('dragover');
                }});

                uploadArea.addEventListener('drop', function(e) {{
                    e.preventDefault();
                    uploadArea.classList.remove('dragover');

                    const files = e.dataTransfer.files;
                    if (files.length > 0) {{
                        processFiles(files);
                    }}
                }});

                // Process files with Database Agent
                async function processFiles(files) {{
                    const processingStatus = document.getElementById('processing-status');
                    const processingResults = document.getElementById('processing-results');
                    const processingContent = document.getElementById('processing-content');
                    const resultsContent = document.getElementById('results-content');

                    // Show processing status
                    processingStatus.classList.remove('hidden');
                    processingResults.classList.add('hidden');

                    let allResults = [];

                    for (let i = 0; i < files.length; i++) {{
                        const file = files[i];

                        // Update processing status
                        processingContent.innerHTML = `
                            <div class="processing-spinner">Database Agent processing...</div>
                            <p style="color: #b8c5d1;">File: ${{file.name}} (${{i + 1}} of ${{files.length}})</p>
                            <div style="margin: 10px 0;">
                                <div class="progress-bar">
                                    <div class="progress-fill" style="width: ${{((i + 1) / files.length) * 100}}%;"></div>
                                </div>
                            </div>
                        `;

                        try {{
                            // Read file content
                            const content = await readFileContent(file);

                            // Process with Database Agent via Python API
                            const result = await window.pywebview.api.upload_file_api(file.name, content);

                            allResults.push({{
                                filename: file.name,
                                result: result
                            }});

                        }} catch (error) {{
                            console.error('Error processing file:', error);
                            allResults.push({{
                                filename: file.name,
                                result: {{ error: error.message }}
                            }});
                        }}
                    }}

                    // Hide processing, show results
                    processingStatus.classList.add('hidden');
                    processingResults.classList.remove('hidden');

                    // Display results
                    let resultsHtml = '<div style="max-height: 400px; overflow-y: auto;">';

                    allResults.forEach(item => {{
                        const result = item.result;
                        if (result.success) {{
                            resultsHtml += `
                                <div class="result-item result-success">
                                    <h4 class="result-title">SUCCESS: ${{item.filename}}</h4>
                                    <p style="margin: 5px 0; color: #b8c5d1;"><strong style="color: #64ffda;">Status:</strong> ${{result.message}}</p>
                                    ${{result.processing ? `
                                        <div style="margin: 10px 0;">
                                            <p style="color: #64ffda;"><strong>Database Agent Analysis:</strong></p>
                                            <ul style="margin: 5px 0; padding-left: 20px; color: #b8c5d1;">
                                                <li>Entities processed: ${{result.processing.entities_processed || 'N/A'}}</li>
                                                <li>Processing time: ${{result.processing.processing_time || 'N/A'}}s</li>
                                                <li>Summary: ${{result.processing.summary || 'N/A'}}</li>
                                            </ul>
                                            ${{result.processing.warnings && result.processing.warnings.length > 0 ?
                                                `<p style="color: #ffd700;">WARNINGS: ${{result.processing.warnings.join(', ')}}</p>` : ''
                                            }}
                                        </div>
                                    ` : ''}}
                                </div>
                            `;
                        }} else {{
                            resultsHtml += `
                                <div class="result-item result-error">
                                    <h4 class="result-title">ERROR: ${{item.filename}}</h4>
                                    <p style="margin: 5px 0; color: #b8c5d1;"><strong style="color: #ff6b6b;">Error:</strong> ${{result.error}}</p>
                                </div>
                            `;
                        }}
                    }});

                    resultsHtml += '</div>';
                    resultsHtml += `
                        <div style="margin-top: 15px; text-align: center;">
                            <button class="btn" onclick="refreshDocumentList()">Refresh Document List</button>
                            <button class="btn btn-secondary" onclick="showPanel('documents')">View Documents</button>
                        </div>
                    `;

                    resultsContent.innerHTML = resultsHtml;
                }}

                // Helper function to read file content
                function readFileContent(file) {{
                    return new Promise((resolve, reject) => {{
                        const reader = new FileReader();
                        reader.onload = e => resolve(e.target.result);
                        reader.onerror = e => reject(new Error('Failed to read file'));
                        reader.readAsText(file);
                    }});
                }}

                // Refresh document list
                async function refreshDocumentList() {{
                    try {{
                        const status = await window.pywebview.api.get_status_api();
                        // Update document count in dashboard
                        location.reload(); // Simple refresh for now
                    }} catch (error) {{
                        console.error('Error refreshing document list:', error);
                    }}
                }}
            </script>
        </body>
        </html>
        """
    
    def create_native_window(self):
        """Create the native desktop window."""
        if not WEBVIEW_AVAILABLE:
            print("❌ pywebview not available. Install with: pip install pywebview")
            return False

        try:
            # Create the native window with API exposure
            webview.create_window(
                title="RAG Management",
                html=self.get_html_content(),
                width=1200,
                height=800,
                min_size=(800, 600),
                resizable=True,
                js_api=self  # Expose this class as the JavaScript API
            )

            return True

        except Exception as e:
            logger.error(f"Error creating native window: {e}")
            return False
    
    def run(self):
        """Run the RAG desktop application."""
        if not WEBVIEW_AVAILABLE:
            print("❌ pywebview is required for the desktop app")
            print("   Install with: pip install pywebview")
            return 1
        
        try:
            print(f"🧠 Starting RAG Management Desktop App - {self.panel.title()} Panel")
            
            # Create and show the native window
            if self.create_native_window():
                if self.debug:
                    webview.start(debug=True)
                else:
                    webview.start()
                return 0
            else:
                print("❌ Failed to create native window")
                return 1
                
        except KeyboardInterrupt:
            print("\n🛑 RAG Management app stopped by user")
            return 0
        except Exception as e:
            logger.error(f"Error running RAG desktop app: {e}")
            print(f"❌ Error: {e}")
            return 1


def main():
    """Main entry point for the RAG Management desktop app."""
    parser = argparse.ArgumentParser(description="RAG Management Desktop Application")
    parser.add_argument(
        "--panel",
        default="main",
        choices=["main", "upload", "documents", "memory", "settings"],
        help="Initial panel to display"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode"
    )

    args = parser.parse_args()

    try:
        app = RAGDesktopApp(panel=args.panel, debug=args.debug)
        return app.run()
    except Exception as e:
        logger.error(f"Failed to start RAG Management app: {e}")
        print(f"Error: Failed to start RAG Management app: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
