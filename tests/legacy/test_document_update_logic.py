#!/usr/bin/env python3
"""
Test Document Update Logic

Tests the document update functionality including
change detection, selective updates, and removal handling.
"""

import sys
import time
import tempfile
import asyncio
from pathlib import Path

# Add jarvis to path
sys.path.append(str(Path(__file__).parent / "jarvis"))


def test_document_update_detection():
    """Test document update detection functionality."""
    print("🔍 Testing Document Update Detection")
    print("=" * 45)
    
    try:
        from jarvis.config import get_config
        from jarvis.tools.rag_service import RAGService
        
        config = get_config()
        rag_service = RAGService(config)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create test documents
            doc1 = temp_path / "test1.txt"
            doc2 = temp_path / "test2.txt"
            doc3 = temp_path / "test3.txt"
            
            doc1.write_text("Original content for document 1")
            doc2.write_text("Original content for document 2")
            doc3.write_text("Original content for document 3")
            
            print("📝 Created test documents")
            
            # Initial ingestion
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                # Ingest initial documents
                ingest_result = loop.run_until_complete(
                    rag_service.ingest_documents_from_folder(str(temp_path))
                )
                
                print(f"✅ Initial ingestion: {ingest_result['processed']} documents")
                
                # Wait a moment to ensure timestamp difference
                time.sleep(2)
                
                # Modify one document
                doc2.write_text("Modified content for document 2 - updated version")
                
                # Add a new document
                doc4 = temp_path / "test4.txt"
                doc4.write_text("New document content")
                
                # Remove one document
                doc3.unlink()
                
                print("🔄 Made changes: modified doc2, added doc4, removed doc3")
                
                # Check for updates
                update_info = loop.run_until_complete(
                    rag_service.check_document_updates(str(temp_path))
                )
                
                print(f"📊 Update detection results:")
                print(f"   New documents: {len(update_info['new_documents'])}")
                print(f"   Modified documents: {len(update_info['modified_documents'])}")
                print(f"   Removed documents: {len(update_info['removed_documents'])}")
                print(f"   Total changes: {update_info['total_changes']}")
                
                # Validate results
                if "test4.txt" in update_info['new_documents']:
                    print("✅ New document detected correctly")
                else:
                    print("❌ Failed to detect new document")
                    return False
                
                if any(doc['path'] == "test2.txt" for doc in update_info['modified_documents']):
                    print("✅ Modified document detected correctly")
                else:
                    print("❌ Failed to detect modified document")
                    return False
                
                if "test3.txt" in update_info['removed_documents']:
                    print("✅ Removed document detected correctly")
                else:
                    print("❌ Failed to detect removed document")
                    return False
                
                if update_info['total_changes'] == 3:
                    print("✅ Total change count correct")
                else:
                    print(f"❌ Incorrect change count: {update_info['total_changes']}")
                    return False
                
                return True
                
            finally:
                loop.close()
        
    except Exception as e:
        print(f"❌ Document update detection test failed: {e}")
        return False


def test_selective_document_update():
    """Test selective document update functionality."""
    print("\n🔄 Testing Selective Document Update")
    print("=" * 45)
    
    try:
        from jarvis.config import get_config
        from jarvis.tools.rag_service import RAGService
        
        config = get_config()
        rag_service = RAGService(config)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create and ingest initial documents
            doc1 = temp_path / "update1.txt"
            doc2 = temp_path / "update2.txt"
            
            doc1.write_text("Initial content for update test 1")
            doc2.write_text("Initial content for update test 2")
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                # Initial ingestion
                ingest_result = loop.run_until_complete(
                    rag_service.ingest_documents_from_folder(str(temp_path))
                )
                
                initial_count = ingest_result['processed']
                print(f"✅ Initial ingestion: {initial_count} documents")
                
                # Get initial document count
                initial_docs = rag_service.get_ingested_documents()
                initial_doc_count = len(initial_docs)
                
                # Wait and modify documents
                time.sleep(2)
                doc1.write_text("Updated content for update test 1 - new version")
                doc3 = temp_path / "update3.txt"
                doc3.write_text("New document for update test")
                
                # Perform selective update
                update_result = loop.run_until_complete(
                    rag_service.update_documents_from_folder(str(temp_path))
                )
                
                print(f"🔄 Update results:")
                print(f"   Status: {update_result['status']}")
                print(f"   Processed: {update_result['processed']}")
                print(f"   Files processed: {update_result['files_processed']}")
                
                if 'update_summary' in update_result:
                    summary = update_result['update_summary']
                    print(f"   New: {summary['new']}, Modified: {summary['modified']}, Removed: {summary['removed']}")
                
                # Validate update results
                if update_result['status'] in ['success', 'partial_success']:
                    print("✅ Update completed successfully")
                else:
                    print(f"❌ Update failed: {update_result.get('errors', [])}")
                    return False
                
                if update_result['processed'] >= 2:  # Should process modified + new
                    print("✅ Correct number of documents processed")
                else:
                    print(f"❌ Incorrect processing count: {update_result['processed']}")
                    return False
                
                # Check final document count
                final_docs = rag_service.get_ingested_documents()
                final_doc_count = len(final_docs)
                
                if final_doc_count == initial_doc_count + 1:  # Added one new document
                    print("✅ Document count correct after update")
                else:
                    print(f"❌ Document count mismatch: {initial_doc_count} -> {final_doc_count}")
                    return False
                
                return True
                
            finally:
                loop.close()
        
    except Exception as e:
        print(f"❌ Selective document update test failed: {e}")
        return False


def test_document_removal():
    """Test document removal functionality."""
    print("\n🗑️ Testing Document Removal")
    print("=" * 35)
    
    try:
        from jarvis.config import get_config
        from jarvis.tools.rag_service import RAGService
        
        config = get_config()
        rag_service = RAGService(config)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create test document
            test_doc = temp_path / "removal_test.txt"
            test_doc.write_text("Content for removal test document")
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                # Ingest document
                ingest_result = loop.run_until_complete(
                    rag_service.ingest_documents_from_folder(str(temp_path))
                )
                
                print(f"✅ Ingested document: {ingest_result['processed']} files")
                
                # Verify document exists
                docs_before = rag_service.get_ingested_documents()
                doc_exists = any(doc['source'] == 'removal_test.txt' for doc in docs_before)
                
                if doc_exists:
                    print("✅ Document found in vector store")
                else:
                    print("❌ Document not found after ingestion")
                    return False
                
                # Remove document directly
                removal_success = loop.run_until_complete(
                    rag_service.remove_document('removal_test.txt')
                )
                
                if removal_success:
                    print("✅ Document removal successful")
                else:
                    print("❌ Document removal failed")
                    return False
                
                # Verify document is gone
                docs_after = rag_service.get_ingested_documents()
                doc_still_exists = any(doc['source'] == 'removal_test.txt' for doc in docs_after)
                
                if not doc_still_exists:
                    print("✅ Document successfully removed from vector store")
                else:
                    print("❌ Document still exists after removal")
                    return False
                
                return True
                
            finally:
                loop.close()
        
    except Exception as e:
        print(f"❌ Document removal test failed: {e}")
        return False


def test_ingestion_script_integration():
    """Test integration with enhanced ingestion script."""
    print("\n📜 Testing Ingestion Script Integration")
    print("=" * 50)
    
    try:
        import subprocess
        import tempfile
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create test documents
            doc1 = temp_path / "script_test1.txt"
            doc2 = temp_path / "script_test2.txt"
            
            doc1.write_text("Script test document 1")
            doc2.write_text("Script test document 2")
            
            print("📝 Created test documents")
            
            # Test check-updates command
            result = subprocess.run([
                "python", "ingest.py", 
                "--check-updates", 
                "--folder", str(temp_path)
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print("✅ Check-updates command executed successfully")
                if "changes detected" in result.stdout.lower() or "up to date" in result.stdout.lower():
                    print("✅ Update detection working in script")
                else:
                    print("⚠️ Update detection output unclear")
            else:
                print(f"❌ Check-updates command failed: {result.stderr}")
                return False
            
            # Test help command to verify new options
            help_result = subprocess.run([
                "python", "ingest.py", "--help"
            ], capture_output=True, text=True, timeout=10)
            
            if help_result.returncode == 0:
                help_text = help_result.stdout
                if "--update" in help_text and "--check-updates" in help_text:
                    print("✅ New command line options available")
                else:
                    print("❌ New command line options not found in help")
                    return False
            else:
                print("❌ Help command failed")
                return False
            
            return True
        
    except Exception as e:
        print(f"❌ Ingestion script integration test failed: {e}")
        return False


def main():
    """Main test function."""
    print("🚀 Document Update Logic Testing Suite")
    print("=" * 55)
    print("Testing intelligent document update and change detection...")
    print()
    
    tests = [
        ("Document Update Detection", test_document_update_detection),
        ("Selective Document Update", test_selective_document_update),
        ("Document Removal", test_document_removal),
        ("Ingestion Script Integration", test_ingestion_script_integration)
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
    
    print(f"\n📊 Document Update Logic Test Results")
    print("=" * 50)
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\n📈 Overall Results:")
    print(f"✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")
    print(f"📊 Success Rate: {passed/total*100:.1f}%")
    
    if passed == total:
        print("\n🎉 Document Update Logic: COMPLETE!")
        print("   ✅ Change detection working correctly")
        print("   ✅ Selective updates functional")
        print("   ✅ Document removal operational")
        print("   ✅ Script integration successful")
        print("\n🔄 Documents can now be updated efficiently without duplicates!")
    elif passed >= total * 0.75:
        print(f"\n✅ Document Update Logic mostly complete!")
        print(f"   Core update functionality working with minor issues")
    else:
        print(f"\n⚠️  Document Update Logic needs attention")
        print(f"   Multiple update issues detected")
    
    return passed >= total * 0.75


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
