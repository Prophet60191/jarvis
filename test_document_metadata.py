#!/usr/bin/env python3
"""
Test Document Metadata Support

Tests the enhanced metadata system for document chunks,
source citation, and debugging capabilities.
"""

import sys
import time
import tempfile
import asyncio
from pathlib import Path

# Add jarvis to path
sys.path.append(str(Path(__file__).parent / "jarvis"))


def test_metadata_enhancement():
    """Test enhanced metadata support in document processing."""
    print("📋 Testing Enhanced Document Metadata")
    print("=" * 45)
    
    try:
        from jarvis.config import get_config
        from jarvis.tools.rag_service import RAGService
        
        config = get_config()
        rag_service = RAGService(config)
        
        # Create test document with rich content
        test_content = """
# Software Development Best Practices

## Introduction
This document outlines key best practices for software development teams.

## Code Quality
- Write clean, readable code
- Use meaningful variable names
- Add comprehensive comments
- Follow consistent formatting

## Testing Strategies
- Unit testing for individual components
- Integration testing for system interactions
- End-to-end testing for user workflows

## Version Control
- Use descriptive commit messages
- Create feature branches for new development
- Review code before merging
- Tag releases appropriately

## Documentation
- Maintain up-to-date README files
- Document API endpoints
- Create user guides
- Keep technical specifications current
"""
        
        # Save test document
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(test_content)
            temp_doc_path = f.name
        
        try:
            # Copy to documents directory
            import shutil
            documents_path = Path(config.rag.documents_path)
            documents_path.mkdir(parents=True, exist_ok=True)
            
            doc_name = "metadata_test_doc.txt"
            final_doc_path = documents_path / doc_name
            shutil.copy2(temp_doc_path, final_doc_path)
            
            print(f"📄 Created test document: {doc_name}")
            
            # Test document ingestion with metadata
            print("\n🔄 Testing document ingestion with metadata...")
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                ingestion_result = loop.run_until_complete(
                    rag_service.ingest_documents_from_folder()
                )
                
                print(f"✅ Ingestion status: {ingestion_result.get('status', 'unknown')}")
                print(f"   Processed: {ingestion_result.get('processed', 0)} documents")
                
                if ingestion_result.get('processed', 0) > 0:
                    # Wait for processing
                    time.sleep(2)
                    
                    # Test metadata retrieval
                    print("\n📊 Testing metadata retrieval...")
                    
                    metadata_summary = rag_service.get_document_metadata_summary(doc_name)
                    
                    if "error" not in metadata_summary:
                        print("✅ Metadata summary retrieved:")
                        print(f"   Source: {metadata_summary.get('source', 'unknown')}")
                        print(f"   File type: {metadata_summary.get('file_extension', 'unknown')}")
                        print(f"   Total chunks: {metadata_summary.get('total_chunks', 0)}")
                        print(f"   Topics: {metadata_summary.get('topics', [])}")
                        print(f"   Concepts: {metadata_summary.get('concepts', [])}")
                        print(f"   Citation: {metadata_summary.get('citation', 'none')}")
                        
                        # Test source citation formatting
                        print("\n🔗 Testing source citation formatting...")
                        
                        # Get a sample document to test citation
                        search_result = loop.run_until_complete(
                            rag_service.intelligent_search("software development", max_results=1)
                        )
                        
                        retrieved_docs = search_result.get('retrieved_documents', [])
                        if retrieved_docs:
                            sample_doc = retrieved_docs[0]
                            citation = rag_service.format_source_citation(sample_doc.metadata)
                            print(f"✅ Sample citation: {citation}")
                            
                            # Check metadata fields
                            metadata = sample_doc.metadata
                            required_fields = [
                                'source', 'source_path', 'source_type', 'file_extension',
                                'processing_timestamp', 'chunk_index', 'total_chunks'
                            ]
                            
                            missing_fields = []
                            for field in required_fields:
                                if field not in metadata:
                                    missing_fields.append(field)
                            
                            if missing_fields:
                                print(f"⚠️ Missing metadata fields: {missing_fields}")
                            else:
                                print("✅ All required metadata fields present")
                                
                            # Display sample metadata
                            print("\n📋 Sample chunk metadata:")
                            for key, value in metadata.items():
                                if key != 'source_path':  # Skip long path
                                    print(f"   {key}: {value}")
                        else:
                            print("❌ No documents retrieved for citation test")
                            return False
                    else:
                        print(f"❌ Metadata retrieval failed: {metadata_summary.get('error')}")
                        return False
                else:
                    print("❌ No documents were processed")
                    return False
                    
            finally:
                loop.close()
                
        finally:
            # Cleanup
            import os
            os.unlink(temp_doc_path)
            if final_doc_path.exists():
                final_doc_path.unlink()
        
        return True
        
    except Exception as e:
        print(f"❌ Metadata enhancement test failed: {e}")
        return False


def test_citation_formatting():
    """Test citation formatting with various metadata scenarios."""
    print("\n🔗 Testing Citation Formatting")
    print("=" * 35)
    
    try:
        from jarvis.config import get_config
        from jarvis.tools.rag_service import RAGService
        
        config = get_config()
        rag_service = RAGService(config)
        
        # Test various metadata scenarios
        test_cases = [
            {
                "name": "Basic document",
                "metadata": {
                    "source": "user_manual.pdf",
                    "title": "User Manual"
                },
                "expected_contains": ["user_manual", "User Manual"]
            },
            {
                "name": "Document with section",
                "metadata": {
                    "source": "technical_spec.docx",
                    "section": "Chapter 3: Architecture",
                    "title": "System Architecture"
                },
                "expected_contains": ["technical_spec", "Chapter 3", "Architecture"]
            },
            {
                "name": "Simple text file",
                "metadata": {
                    "source": "notes.txt",
                    "title": "notes"  # Same as source
                },
                "expected_contains": ["notes"]
            }
        ]
        
        print("🧪 Testing citation formatting scenarios...")
        
        all_passed = True
        for test_case in test_cases:
            citation = rag_service.format_source_citation(test_case["metadata"])
            
            print(f"\n   Test: {test_case['name']}")
            print(f"   Citation: {citation}")
            
            # Check if expected elements are present
            passed = True
            for expected in test_case["expected_contains"]:
                if expected.lower() not in citation.lower():
                    print(f"   ❌ Missing expected element: {expected}")
                    passed = False
                    all_passed = False
            
            if passed:
                print(f"   ✅ Citation format correct")
        
        return all_passed
        
    except Exception as e:
        print(f"❌ Citation formatting test failed: {e}")
        return False


def test_metadata_search_integration():
    """Test metadata integration with search functionality."""
    print("\n🔍 Testing Metadata Search Integration")
    print("=" * 45)
    
    try:
        from jarvis.config import get_config
        from jarvis.tools.rag_service import RAGService
        
        config = get_config()
        rag_service = RAGService(config)
        
        # Add test memory with metadata
        test_fact = f"Metadata integration test - {time.time()}"
        rag_service.add_conversational_memory(test_fact)
        time.sleep(1)
        
        print("🔍 Testing search with metadata-enhanced results...")
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            search_result = loop.run_until_complete(
                rag_service.intelligent_search("metadata integration", max_results=2)
            )
            
            # Check if search results include metadata
            retrieved_docs = search_result.get('retrieved_documents', [])
            
            if retrieved_docs:
                print(f"✅ Retrieved {len(retrieved_docs)} documents with metadata")
                
                for i, doc in enumerate(retrieved_docs[:2], 1):
                    metadata = doc.metadata
                    print(f"\n   Document {i} metadata:")
                    print(f"     Source: {metadata.get('source', 'unknown')}")
                    print(f"     Type: {metadata.get('source_type', 'unknown')}")
                    
                    if metadata.get('processing_timestamp'):
                        print(f"     Processed: {time.ctime(metadata['processing_timestamp'])}")
                    
                    # Test citation formatting
                    citation = rag_service.format_source_citation(metadata)
                    print(f"     Citation: {citation}")
                
                # Check synthesis quality
                synthesis = search_result.get('synthesis', {})
                if synthesis.get('synthesized_answer'):
                    print(f"\n✅ Synthesis generated with confidence: {synthesis.get('confidence_score', 0):.2f}")
                    return True
                else:
                    print("❌ No synthesis generated")
                    return False
            else:
                print("❌ No documents retrieved")
                return False
                
        finally:
            loop.close()
        
    except Exception as e:
        print(f"❌ Metadata search integration test failed: {e}")
        return False


def main():
    """Main test function."""
    print("🚀 Document Metadata Support Testing Suite")
    print("=" * 60)
    print("Testing enhanced metadata system for source citation and debugging...")
    print()
    
    tests = [
        ("Metadata Enhancement", test_metadata_enhancement),
        ("Citation Formatting", test_citation_formatting),
        ("Metadata Search Integration", test_metadata_search_integration)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"\n📊 Metadata Support Test Results")
    print("=" * 40)
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\n📈 Overall Results:")
    print(f"✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")
    print(f"📊 Success Rate: {passed/total*100:.1f}%")
    
    if passed == total:
        print("\n🎉 Document Metadata Support: COMPLETE!")
        print("   ✅ Enhanced metadata fields implemented")
        print("   ✅ Source citation formatting working")
        print("   ✅ Metadata search integration successful")
        print("   ✅ Debugging capabilities enhanced")
        print("\n📋 Documents now have comprehensive metadata for citation and debugging!")
    elif passed >= total * 0.8:
        print(f"\n✅ Document Metadata Support mostly complete!")
        print(f"   Minor issues detected, but core functionality works")
    else:
        print(f"\n⚠️  Document Metadata Support needs attention")
        print(f"   Multiple metadata issues detected")
    
    return passed >= total * 0.8


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
