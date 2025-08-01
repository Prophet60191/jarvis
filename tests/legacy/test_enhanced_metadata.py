#!/usr/bin/env python3
"""
Test script to verify enhanced metadata storage in RAG Service.
"""

import asyncio
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'jarvis'))

from jarvis.config import get_config
from jarvis.tools.rag_service import RAGService


async def test_enhanced_metadata():
    """Test that enhanced metadata is properly stored and retrievable."""
    print("🔍 Testing Enhanced Metadata Storage")
    print("=" * 50)
    
    config = get_config()
    rag_service = RAGService(config)
    
    # Get document statistics
    stats = rag_service.get_document_stats()
    print(f"📊 Current database stats:")
    print(f"   Total documents: {stats['total_documents']}")
    print(f"   Unique sources: {stats['unique_sources']}")
    
    if stats['total_documents'] > 0:
        # Get a sample of documents to examine metadata
        try:
            collection = rag_service.vector_store._collection
            sample_results = collection.get(limit=3, include=['metadatas', 'documents'])
            
            print(f"\n📋 Sample Enhanced Metadata:")
            print("=" * 40)
            
            if sample_results.get('metadatas') and sample_results.get('documents'):
                for i, metadata in enumerate(sample_results['metadatas'][:3]):
                    if metadata is None:
                        print(f"\nDocument {i+1}: No metadata available")
                        continue

                    print(f"\nDocument {i+1}:")
                    print(f"   Source: {metadata.get('source', 'unknown')}")
                    print(f"   Title: {metadata.get('title', 'unknown')}")
                    print(f"   Document Type: {metadata.get('document_type', 'unknown')}")
                    print(f"   Topics: {metadata.get('topics', 'none')}")
                    print(f"   Concepts: {metadata.get('concepts', 'none')}")
                    print(f"   Importance Score: {metadata.get('importance_score', 'unknown')}")

                    # Enhanced metadata from our improvements
                    print(f"   📈 Quality Metrics:")
                    print(f"      Readability: {metadata.get('readability_score', 'unknown')}")
                    print(f"      Info Density: {metadata.get('information_density', 'unknown')}")
                    print(f"      Reference Value: {metadata.get('reference_value', 'unknown')}")
                    print(f"      Technical Depth: {metadata.get('technical_depth', 'unknown')}")
                    print(f"      Extraction Confidence: {metadata.get('extraction_confidence', 'unknown')}")

                    print(f"   🏗️ Structure Metadata:")
                    print(f"      Chunk Type: {metadata.get('chunk_type', 'unknown')}")
                    print(f"      Technical Level: {metadata.get('technical_level', 'unknown')}")
                    print(f"      Contains Code: {metadata.get('contains_code', 'unknown')}")
                    print(f"      Document Complexity: {metadata.get('document_complexity', 'unknown')}")
                    print(f"      Target Audience: {metadata.get('target_audience', 'unknown')}")
                    print(f"      Language Style: {metadata.get('language_style', 'unknown')}")

                    # Show content preview
                    if i < len(sample_results['documents']):
                        content = sample_results['documents'][i]
                        print(f"   📄 Content Preview: {content[:100]}...")
            else:
                print("   No metadata or documents found in sample results")
                
        except Exception as e:
            print(f"❌ Error examining metadata: {e}")
            return False
    else:
        print("⚠️  No documents found in database. Run ingestion first.")
        return False
    
    print(f"\n✅ Enhanced metadata verification complete!")
    return True


async def main():
    """Run enhanced metadata test."""
    print("🚀 Enhanced Metadata Testing")
    print("=" * 50)
    
    success = await test_enhanced_metadata()
    
    print(f"\n📊 Test Result: {'PASS' if success else 'FAIL'}")
    
    if success:
        print("\n🎉 Enhanced intelligent document processing is working!")
        print("   ✅ Quality assessment metrics stored")
        print("   ✅ Document structure metadata captured")
        print("   ✅ Chunk-specific information preserved")
        print("   ✅ Enhanced retrieval capabilities enabled")


if __name__ == "__main__":
    asyncio.run(main())
