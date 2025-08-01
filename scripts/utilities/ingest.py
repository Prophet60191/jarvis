#!/usr/bin/env python3
"""
Jarvis Document Ingestion Script

This standalone script processes documents and adds them to the RAG memory system.
It can be run independently to ingest documents from a specified folder.

Usage:
    python ingest.py                           # Use default documents folder
    python ingest.py --folder /path/to/docs   # Use custom folder
    python ingest.py --help                   # Show help

Supported file formats:
    - PDF files (.pdf)
    - Text files (.txt)
    - Word documents (.doc, .docx)
"""

import argparse
import sys
from pathlib import Path

# Add the jarvis package to the path
sys.path.append(str(Path(__file__).parent / "jarvis"))

from jarvis.config import get_config
from jarvis.tools.rag_service import RAGService


def main():
    """Main function to handle document ingestion."""
    parser = argparse.ArgumentParser(
        description="Ingest documents into Jarvis RAG memory system",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python ingest.py                           # Use default documents folder
    python ingest.py --folder /path/to/docs   # Use custom folder
    python ingest.py --stats                  # Show current statistics only
    python ingest.py --list                   # List ingested documents
    
Supported file formats:
    - PDF files (.pdf)
    - Text files (.txt) 
    - Word documents (.doc, .docx)
        """
    )
    
    parser.add_argument(
        "--folder", "-f",
        type=str,
        help="Path to documents folder (default: uses config setting)"
    )
    
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force re-ingestion of all documents"
    )

    parser.add_argument(
        "--update", "-u",
        action="store_true",
        help="Update only modified documents (check timestamps)"
    )

    parser.add_argument(
        "--check-updates",
        action="store_true",
        help="Check for document updates without ingesting"
    )
    
    parser.add_argument(
        "--stats", "-s",
        action="store_true", 
        help="Show document statistics only (no ingestion)"
    )
    
    parser.add_argument(
        "--list", "-l",
        action="store_true",
        help="List all ingested documents (no ingestion)"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )

    args = parser.parse_args()

    try:
        # Load configuration
        print("🔧 Loading Jarvis configuration...")
        config = get_config()
        
        if not config.rag.enabled:
            print("❌ RAG system is disabled in configuration")
            print("   Enable it by setting JARVIS_RAG_ENABLED=true or updating config")
            return 1

        # Initialize intelligent RAG service
        print("🧠 Initializing Intelligent RAG Service...")
        rag_manager = RAGService(config)
        print(f"🌡️ Using thermal-safe model: {rag_manager.document_llm.model}")
        
        # Handle stats-only request
        if args.stats:
            print_document_stats(rag_manager)
            return 0
            
        # Handle list-only request
        if args.list:
            print_ingested_documents(rag_manager)
            return 0

        # Handle check-updates request
        if args.check_updates:
            check_document_updates(rag_manager, args.folder or config.rag.documents_path)
            return 0

        # Determine documents folder
        documents_folder = args.folder or config.rag.documents_path
        print(f"📁 Documents folder: {documents_folder}")

        # Check if folder exists
        if not Path(documents_folder).exists():
            print(f"❌ Documents folder does not exist: {documents_folder}")
            print("   Create the folder and add documents, then run this script again")
            return 1

        # Show current stats before ingestion
        if args.verbose:
            print("\n📊 Current Statistics (before ingestion):")
            print_document_stats(rag_manager, prefix="  ")

        # Perform intelligent ingestion
        if args.update:
            print(f"\n🔄 Starting intelligent document update...")
            import asyncio
            results = asyncio.run(rag_manager.update_documents_from_folder(
                documents_path=documents_folder
            ))
        else:
            print(f"\n📚 Starting intelligent document ingestion...")
            import asyncio
            results = asyncio.run(rag_manager.ingest_documents_from_folder(
                documents_path=documents_folder,
                force_reingest=args.force
            ))

        # Display intelligent ingestion results
        print(f"\n✅ Intelligent Ingestion Results:")
        print(f"   Status: {results['status']}")
        print(f"   Files processed: {results['processed']}")

        # Display intelligence metrics
        if 'intelligence_metrics' in results:
            print(f"\n🧠 Intelligence Metrics:")
            metrics = results['intelligence_metrics']
            print(f"   LLM Analysis Success: {metrics['llm_analysis_success']}")
            print(f"   LLM Chunking Success: {metrics['llm_chunking_success']}")
            print(f"   Fallback Used: {metrics['fallback_used']}")
            print(f"   Total Concepts Extracted: {metrics['total_concepts_extracted']}")

        if results['files_processed']:
            print(f"\n📄 Successfully processed:")
            for filename in results['files_processed']:
                print(f"     - {filename}")

        if results['errors']:
            print(f"\n❌ Errors ({len(results['errors'])}):")
            for error in results['errors']:
                print(f"     - {error}")

        # Show final stats
        print(f"\n📈 Final Statistics:")
        print_document_stats(rag_manager, prefix="  ")

        if results['status'] == 'success' and results['processed'] > 0:
            print(f"\n🎉 Successfully ingested {results['processed']} documents!")
            print("   You can now ask Jarvis questions about the ingested content.")
        elif results['status'] == 'no_files':
            print(f"\n💡 No supported documents found in {documents_folder}")
            print("   Add .pdf, .txt, .doc, or .docx files and run again.")
        
        return 0 if results['status'] in ['success', 'no_files'] else 1

    except KeyboardInterrupt:
        print("\n⚠️ Ingestion interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Error during ingestion: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


def print_document_stats(rag_manager, prefix=""):
    """Print document statistics in a formatted way."""
    stats = rag_manager.get_document_stats()

    print(f"{prefix}Total documents: {stats['total_documents']}")
    print(f"{prefix}Unique sources: {stats['unique_sources']}")

    if stats['unique_sources'] > 0:
        print(f"{prefix}Sources:")
        for source in stats['sources']:
            print(f"{prefix}  - {source}")

    # Show error if any
    if 'error' in stats:
        print(f"{prefix}Error: {stats['error']}")


def print_ingested_documents(rag_manager):
    """Print list of all ingested documents."""
    docs = rag_manager.get_ingested_documents()
    
    if not docs:
        print("📋 No documents have been ingested yet")
        return
    
    print(f"📋 Ingested Documents ({len(docs)} total):")
    print("=" * 50)
    
    for doc in docs:
        source_type = doc.get('source_type', 'unknown')
        chunk_count = doc.get('chunk_count', 0)
        file_ext = doc.get('file_extension', '')
        
        print(f"📄 {doc['source']}")
        print(f"   Type: {source_type}")
        print(f"   Chunks: {chunk_count}")
        if file_ext:
            print(f"   Format: {file_ext}")
        print()


def check_document_updates(rag_manager, documents_folder):
    """Check for document updates without ingesting."""
    try:
        import asyncio

        print(f"🔍 Checking for document updates in: {documents_folder}")
        print("=" * 60)

        # Get update status
        update_info = asyncio.run(rag_manager.check_document_updates(documents_folder))

        if update_info['new_documents']:
            print(f"\n📄 New Documents ({len(update_info['new_documents'])}):")
            for doc in update_info['new_documents']:
                print(f"   + {doc}")

        if update_info['modified_documents']:
            print(f"\n🔄 Modified Documents ({len(update_info['modified_documents'])}):")
            for doc_info in update_info['modified_documents']:
                doc_path = doc_info['path']
                old_time = doc_info['old_modified']
                new_time = doc_info['new_modified']
                print(f"   ~ {doc_path}")
                print(f"     Old: {old_time}")
                print(f"     New: {new_time}")

        if update_info['removed_documents']:
            print(f"\n🗑️ Removed Documents ({len(update_info['removed_documents'])}):")
            for doc in update_info['removed_documents']:
                print(f"   - {doc}")

        if not any([update_info['new_documents'],
                   update_info['modified_documents'],
                   update_info['removed_documents']]):
            print("✅ All documents are up to date!")
        else:
            total_changes = (len(update_info['new_documents']) +
                           len(update_info['modified_documents']) +
                           len(update_info['removed_documents']))
            print(f"\n📊 Summary: {total_changes} changes detected")
            print("   Run with --update to apply changes")

    except Exception as e:
        print(f"❌ Error checking document updates: {e}")


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
