#!/usr/bin/env python3
"""
Complete Codebase Ingestion for Jarvis Self-Awareness

This script ingests the entire Jarvis application codebase into the RAG system,
giving Jarvis complete self-awareness and the ability to answer technical questions
about its own implementation.
"""

import os
import sys
from pathlib import Path
import time
from typing import List, Dict, Set
import mimetypes

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def get_file_type_category(file_path: Path) -> str:
    """Categorize file types for better organization."""
    suffix = file_path.suffix.lower()
    
    # Code files
    if suffix in ['.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c', '.h', '.cs', '.php', '.rb', '.go', '.rs', '.swift']:
        return 'source_code'
    
    # Documentation
    elif suffix in ['.md', '.rst', '.txt', '.doc', '.docx', '.pdf']:
        return 'documentation'
    
    # Configuration
    elif suffix in ['.json', '.yaml', '.yml', '.toml', '.ini', '.cfg', '.conf', '.env']:
        return 'configuration'
    
    # Web files
    elif suffix in ['.html', '.css', '.scss', '.less']:
        return 'web_files'
    
    # Data files
    elif suffix in ['.csv', '.xml', '.sql', '.db', '.sqlite']:
        return 'data_files'
    
    # Scripts
    elif suffix in ['.sh', '.bat', '.ps1', '.command']:
        return 'scripts'
    
    # Other
    else:
        return 'other'

def should_include_file(file_path: Path, exclude_patterns: Set[str]) -> bool:
    """Determine if a file should be included in the ingestion."""
    
    # Skip hidden files and directories
    if any(part.startswith('.') for part in file_path.parts):
        # But include important config files
        if file_path.name not in ['.gitignore', '.env.example', '.env']:
            return False
    
    # Skip common exclude patterns
    path_str = str(file_path).lower()
    for pattern in exclude_patterns:
        if pattern in path_str:
            return False
    
    # Skip binary files (basic check)
    try:
        mime_type, _ = mimetypes.guess_type(str(file_path))
        if mime_type and mime_type.startswith(('image/', 'video/', 'audio/')):
            return False
    except:
        pass
    
    # Skip very large files (>10MB)
    try:
        if file_path.stat().st_size > 10 * 1024 * 1024:
            return False
    except:
        pass
    
    return True

def read_file_content(file_path: Path) -> str:
    """Safely read file content with encoding detection."""
    encodings = ['utf-8', 'utf-16', 'latin-1', 'cp1252']
    
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                return f.read()
        except UnicodeDecodeError:
            continue
        except Exception as e:
            print(f"⚠️  Error reading {file_path}: {e}")
            return ""
    
    # If all encodings fail, try binary mode and decode with errors='ignore'
    try:
        with open(file_path, 'rb') as f:
            content = f.read()
            return content.decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"❌ Failed to read {file_path}: {e}")
        return ""

def ingest_complete_codebase():
    """Ingest the entire Jarvis codebase into RAG system."""
    
    print("🚀 JARVIS COMPLETE CODEBASE INGESTION")
    print("=" * 50)
    print("Giving Jarvis complete self-awareness...")
    print()
    
    # Import RAG manager and config
    try:
        from jarvis.jarvis.tools.rag_memory_manager import RAGMemoryManager
        from jarvis.jarvis.config import JarvisConfig
        from langchain.schema import Document
        print("✅ RAG manager imported successfully")

        # Initialize config and RAG manager
        config = JarvisConfig()
        rag_manager = RAGMemoryManager(config)
        print("✅ RAG manager initialized")
    except ImportError as e:
        print(f"❌ Failed to import RAG manager: {e}")
        print("Make sure the RAG system is properly set up")
        return False
    except Exception as e:
        print(f"❌ Failed to initialize RAG manager: {e}")
        return False
    
    # Define exclude patterns
    exclude_patterns = {
        '__pycache__',
        '.pyc',
        '.pyo',
        '.git',
        'node_modules',
        '.vscode',
        '.idea',
        'venv',
        'env',
        '.DS_Store',
        'Thumbs.db',
        '.pytest_cache',
        'test_results',
        '.coverage',
        'htmlcov',
        'dist',
        'build',
        '*.egg-info',
        '.tox',
        '.mypy_cache'
    }
    
    # File type counters
    file_counts = {}
    total_files = 0
    total_size = 0
    ingested_files = 0
    
    # Start ingestion
    start_time = time.time()
    
    print("📁 Scanning codebase...")
    
    # Walk through all files
    for root, dirs, files in os.walk(project_root):
        root_path = Path(root)
        
        # Skip excluded directories
        dirs[:] = [d for d in dirs if not any(pattern in d.lower() for pattern in exclude_patterns)]
        
        for file in files:
            file_path = root_path / file
            relative_path = file_path.relative_to(project_root)
            
            total_files += 1
            
            if should_include_file(file_path, exclude_patterns):
                try:
                    # Get file info
                    file_size = file_path.stat().st_size
                    total_size += file_size
                    
                    file_category = get_file_type_category(file_path)
                    file_counts[file_category] = file_counts.get(file_category, 0) + 1
                    
                    # Read file content
                    content = read_file_content(file_path)
                    
                    if content.strip():  # Only ingest non-empty files
                        # Create comprehensive metadata
                        metadata = {
                            'file_path': str(relative_path),
                            'file_name': file_path.name,
                            'file_type': file_path.suffix,
                            'file_category': file_category,
                            'file_size': file_size,
                            'directory': str(relative_path.parent),
                            'source': 'jarvis_codebase',
                            'ingestion_type': 'complete_codebase',
                            'timestamp': time.time()
                        }
                        
                        # Create document title
                        doc_title = f"Jarvis Codebase: {relative_path}"
                        
                        # Create document with metadata
                        document = Document(
                            page_content=content,
                            metadata=metadata
                        )

                        # Store in RAG system
                        try:
                            rag_manager.vector_store.add_documents([document])
                            ingested_files += 1
                            if ingested_files % 50 == 0:
                                print(f"📄 Ingested {ingested_files} files...")
                        except Exception as e:
                            print(f"⚠️  Failed to ingest {relative_path}: {e}")
                    
                except Exception as e:
                    print(f"❌ Error processing {relative_path}: {e}")
    
    # Completion summary
    end_time = time.time()
    duration = end_time - start_time
    
    print("\n🎉 CODEBASE INGESTION COMPLETE!")
    print("=" * 50)
    print(f"⏱️  Duration: {duration:.2f} seconds")
    print(f"📁 Total files scanned: {total_files}")
    print(f"📄 Files ingested: {ingested_files}")
    print(f"💾 Total size processed: {total_size / (1024*1024):.2f} MB")
    print()
    
    print("📊 File types ingested:")
    for category, count in sorted(file_counts.items()):
        print(f"   {category}: {count} files")
    
    print()
    print("🧠 JARVIS NOW HAS COMPLETE SELF-AWARENESS!")
    print("Jarvis can now answer questions about:")
    print("• Its own source code and implementation")
    print("• System architecture and design patterns")
    print("• Plugin development and integration")
    print("• Configuration files and settings")
    print("• Documentation and user guides")
    print("• Test files and quality assurance")
    print("• Scripts and automation tools")
    print()
    print("Try asking Jarvis:")
    print('• "How does the analytics dashboard work?"')
    print('• "Show me the user help UI implementation"')
    print('• "What plugins are available and how do they work?"')
    print('• "How is the RAG system implemented?"')
    print('• "What are the main components of the system?"')
    
    return True

if __name__ == "__main__":
    success = ingest_complete_codebase()
    sys.exit(0 if success else 1)
