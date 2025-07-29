#!/usr/bin/env python3
"""
Test script for the intelligent RAG service with Qwen2.5

This script tests the new RAG service with LLM-powered document processing,
semantic chunking, and query optimization.
"""

import asyncio
import sys
from pathlib import Path

# Add the jarvis package to the path
sys.path.append(str(Path(__file__).parent / "jarvis"))

from jarvis.config import get_config
from jarvis.tools.rag_service import RAGService


async def test_document_analysis():
    """Test LLM-powered document analysis."""
    print("🔍 Testing Document Analysis")
    print("=" * 40)
    
    config = get_config()
    
    # Create RAG service with 7b model for testing
    rag_service = RAGService(config)
    
    # Override to use 7b model for testing (14b is downloading)
    rag_service.document_llm.model = "qwen2.5:7b"
    
    # Test document content
    test_content = """
    Jarvis Voice Assistant - Advanced Features
    
    Jarvis is an AI-powered voice assistant with sophisticated capabilities:
    
    1. Voice Recognition: Uses OpenAI Whisper for accurate speech-to-text
    2. Memory System: Dual memory with short-term chat and long-term facts
    3. Plugin Architecture: Zero built-in tools, everything is plugin-based
    4. RAG System: ChromaDB vector database for semantic search
    5. Web Interface: Real-time control panel for configuration
    
    The system is designed for maximum flexibility and extensibility.
    """
    
    try:
        print("📄 Analyzing test document...")
        analysis = await rag_service.analyze_document(test_content, "jarvis_features.txt")
        
        print(f"✅ Analysis Results:")
        print(f"   Title: {analysis.title}")
        print(f"   Type: {analysis.document_type}")
        print(f"   Topics: {analysis.main_topics}")
        print(f"   Concepts: {analysis.key_concepts}")
        print(f"   Summary: {analysis.summary}")
        
        return analysis
        
    except Exception as e:
        print(f"❌ Error in document analysis: {e}")
        return None


async def test_intelligent_chunking():
    """Test LLM-powered semantic chunking."""
    print("\n🧩 Testing Intelligent Chunking")
    print("=" * 40)
    
    config = get_config()
    rag_service = RAGService(config)
    rag_service.document_llm.model = "qwen2.5:7b"
    
    # Test content for chunking
    test_content = """
    Plugin Development Guide for Jarvis
    
    Creating plugins for Jarvis is straightforward and powerful. The plugin system
    allows developers to add new functionality without modifying the core application.
    
    Basic Plugin Structure:
    All plugins are Python files located in the jarvis/tools/plugins/ directory.
    Each plugin defines one or more tools using the LangChain @tool decorator.
    
    Example Plugin:
    ```python
    from langchain_core.tools import tool
    
    @tool
    def my_awesome_function(query: str) -> str:
        "Tool description for the agent."
        return f"Processed: {query}"
    ```
    
    Plugin Registration:
    Plugins are automatically discovered and loaded at startup. No manual
    registration is required, making the system truly plug-and-play.
    
    Best Practices:
    - Use descriptive function names
    - Provide clear tool descriptions
    - Handle errors gracefully
    - Test plugins independently
    """
    
    try:
        print("📄 Analyzing document for chunking...")
        analysis = await rag_service.analyze_document(test_content, "plugin_guide.txt")
        
        print("🧩 Creating intelligent chunks...")
        chunks = await rag_service.create_intelligent_chunks(test_content, analysis)
        
        print(f"✅ Created {len(chunks)} intelligent chunks:")
        for i, chunk in enumerate(chunks, 1):
            print(f"\n   Chunk {i}:")
            print(f"     Title: {chunk.title}")
            print(f"     Topics: {chunk.topics}")
            print(f"     Concepts: {chunk.concepts}")
            print(f"     Importance: {chunk.importance_score}")
            print(f"     Content: {chunk.content[:100]}...")
        
        return chunks
        
    except Exception as e:
        print(f"❌ Error in intelligent chunking: {e}")
        return None


async def test_document_ingestion():
    """Test intelligent document ingestion."""
    print("\n📚 Testing Intelligent Document Ingestion")
    print("=" * 40)
    
    config = get_config()
    rag_service = RAGService(config)
    rag_service.document_llm.model = "qwen2.5:7b"
    
    try:
        print("📁 Starting intelligent document ingestion...")
        results = await rag_service.ingest_documents_from_folder()
        
        print(f"✅ Ingestion Results:")
        print(f"   Status: {results['status']}")
        print(f"   Files processed: {results['processed']}")
        print(f"   Intelligence metrics:")
        for metric, value in results['intelligence_metrics'].items():
            print(f"     {metric}: {value}")
        
        if results['files_processed']:
            print(f"   Successfully processed:")
            for filename in results['files_processed']:
                print(f"     - {filename}")
        
        if results['errors']:
            print(f"   Errors:")
            for error in results['errors']:
                print(f"     - {error}")
        
        return results
        
    except Exception as e:
        print(f"❌ Error in document ingestion: {e}")
        return None


async def test_backward_compatibility():
    """Test backward compatibility with existing tools."""
    print("\n🔄 Testing Backward Compatibility")
    print("=" * 40)
    
    config = get_config()
    rag_service = RAGService(config)
    rag_service.document_llm.model = "qwen2.5:7b"
    
    try:
        print("💾 Testing conversational memory...")
        rag_service.add_conversational_memory("I prefer intelligent RAG systems over basic ones")
        
        print("🔧 Testing retriever tool creation...")
        retriever_tool = rag_service.get_retriever_tool()
        
        print(f"✅ Backward compatibility verified:")
        print(f"   Tool name: {retriever_tool.name}")
        print(f"   Tool description: {retriever_tool.description[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in backward compatibility test: {e}")
        return False


async def main():
    """Run all RAG service tests."""
    print("🚀 RAG Service Testing Suite")
    print("=" * 50)
    print("Testing intelligent RAG service with Qwen2.5")
    print("(Using 7b model while 14b downloads)")
    print()
    
    # Run tests
    analysis = await test_document_analysis()
    chunks = await test_intelligent_chunking()
    ingestion = await test_document_ingestion()
    compatibility = await test_backward_compatibility()
    
    # Summary
    print("\n📊 Test Summary")
    print("=" * 30)
    print(f"✅ Document Analysis: {'PASS' if analysis else 'FAIL'}")
    print(f"✅ Intelligent Chunking: {'PASS' if chunks else 'FAIL'}")
    print(f"✅ Document Ingestion: {'PASS' if ingestion else 'FAIL'}")
    print(f"✅ Backward Compatibility: {'PASS' if compatibility else 'FAIL'}")
    
    if all([analysis, chunks, ingestion, compatibility]):
        print("\n🎉 All tests passed! RAG Service is ready.")
        print("   Upgrade to Qwen2.5:14b when download completes for optimal performance.")
    else:
        print("\n⚠️ Some tests failed. Check the output above for details.")


if __name__ == "__main__":
    asyncio.run(main())
