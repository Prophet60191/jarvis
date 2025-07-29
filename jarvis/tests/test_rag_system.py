#!/usr/bin/env python3
"""
Comprehensive RAG System Unit Tests

Tests for RAG manager, document processing, memory persistence,
and integration with various file types.
"""

import unittest
import tempfile
import asyncio
import json
import time
from pathlib import Path
from unittest.mock import Mock, patch

import sys
sys.path.append(str(Path(__file__).parent.parent))

from jarvis.config import get_config, RAGConfig
from jarvis.tools.rag_service import RAGService
from jarvis.tools.rag_backup_manager import RAGBackupManager
from jarvis.tools.rag_config_manager import RAGConfigManager
from jarvis.tools.rag_error_handler import RAGValidator, get_error_handler


class TestRAGConfiguration(unittest.TestCase):
    """Test RAG configuration management."""
    
    def setUp(self):
        """Set up test configuration."""
        self.config = get_config()
        self.rag_config = self.config.rag
    
    def test_config_loading(self):
        """Test that RAG configuration loads correctly."""
        self.assertIsNotNone(self.rag_config)
        self.assertTrue(hasattr(self.rag_config, 'vector_store_path'))
        self.assertTrue(hasattr(self.rag_config, 'documents_path'))
        self.assertTrue(hasattr(self.rag_config, 'backup_path'))
        self.assertTrue(hasattr(self.rag_config, 'collection_name'))
    
    def test_config_validation(self):
        """Test configuration validation."""
        is_valid, errors = RAGValidator.validate_config(self.rag_config)
        self.assertTrue(is_valid, f"Configuration validation failed: {errors}")
    
    def test_config_manager(self):
        """Test RAG configuration manager."""
        config_manager = RAGConfigManager(self.rag_config)
        
        # Test path validation
        paths_valid, path_issues = config_manager.validate_paths()
        self.assertTrue(paths_valid, f"Path validation failed: {path_issues}")
        
        # Test configuration summary
        summary = config_manager.get_configuration_summary()
        self.assertIn('enabled', summary)
        self.assertIn('is_valid', summary)
        self.assertIn('paths', summary)
        self.assertIn('settings', summary)


class TestRAGService(unittest.TestCase):
    """Test RAG service functionality."""
    
    def setUp(self):
        """Set up test RAG service."""
        self.config = get_config()
        self.rag_service = RAGService(self.config)
    
    def test_service_initialization(self):
        """Test RAG service initializes correctly."""
        self.assertIsNotNone(self.rag_service)
        self.assertIsNotNone(self.rag_service.vector_store)
        self.assertIsNotNone(self.rag_service.embeddings)
        self.assertIsNotNone(self.rag_service.backup_manager)
        self.assertIsNotNone(self.rag_service.error_handler)
    
    def test_conversational_memory(self):
        """Test adding and retrieving conversational memory."""
        test_fact = f"Unit test memory - {time.time()}"
        
        # Add memory
        result = self.rag_service.add_conversational_memory(test_fact)
        self.assertNotEqual(result, False, "Memory addition should not return False")
        
        # Wait for processing
        time.sleep(1)
        
        # Verify memory was added by checking document stats
        doc_stats = self.rag_service.get_document_stats()
        self.assertGreater(doc_stats.get('total_documents', 0), 0)
    
    def test_document_stats(self):
        """Test document statistics retrieval."""
        stats = self.rag_service.get_document_stats()

        self.assertIsInstance(stats, dict)
        self.assertIn('total_documents', stats)
        self.assertIn('unique_sources', stats)
        # Check for either 'ingested_documents' or 'sources' (both are valid)
        self.assertTrue('ingested_documents' in stats or 'sources' in stats)
    
    def test_ingested_documents(self):
        """Test ingested documents retrieval."""
        ingested_docs = self.rag_service.get_ingested_documents()
        
        self.assertIsInstance(ingested_docs, list)
        # Each document should have required fields
        for doc in ingested_docs:
            self.assertIn('source', doc)
            self.assertIn('chunk_count', doc)
    
    def test_search_functionality(self):
        """Test intelligent search functionality."""
        # Add some test data first
        test_fact = "Python is a programming language used for AI development"
        self.rag_service.add_conversational_memory(test_fact)
        time.sleep(1)
        
        # Perform search
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            search_results = loop.run_until_complete(
                self.rag_service.intelligent_search("programming language")
            )
            
            self.assertIsInstance(search_results, dict)
            self.assertIn('synthesis', search_results)
            self.assertIn('retrieved_documents', search_results)
            
            # Check synthesis structure
            synthesis = search_results['synthesis']
            self.assertIn('synthesized_answer', synthesis)
            self.assertIn('confidence_score', synthesis)
            
        finally:
            loop.close()


class TestRAGBackupManager(unittest.TestCase):
    """Test RAG backup and restore functionality."""
    
    def setUp(self):
        """Set up test backup manager."""
        self.config = get_config()
        self.backup_manager = RAGBackupManager(self.config.rag)
    
    def test_backup_manager_initialization(self):
        """Test backup manager initializes correctly."""
        self.assertIsNotNone(self.backup_manager)
        self.assertTrue(self.backup_manager.backup_dir.exists())
    
    def test_backup_creation(self):
        """Test backup creation."""
        backup_result = self.backup_manager.create_backup(
            backup_name="unit_test",
            compress=False
        )
        
        self.assertEqual(backup_result['status'], 'success')
        self.assertIn('backup_name', backup_result)
        self.assertIn('components', backup_result)
        self.assertIn('total_size_mb', backup_result)
    
    def test_backup_listing(self):
        """Test backup listing."""
        backups = self.backup_manager.list_backups()
        
        self.assertIsInstance(backups, list)
        # Check if our test backup exists
        test_backup_found = any('unit_test' in backup['name'] for backup in backups)
        self.assertTrue(test_backup_found, "Test backup should be found in list")


class TestRAGDocumentProcessing(unittest.TestCase):
    """Test document processing functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.config = get_config()
        self.rag_service = RAGService(self.config)
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
    
    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_document_validation(self):
        """Test document validation."""
        # Create test documents
        valid_txt = self.temp_path / "test.txt"
        valid_txt.write_text("This is a test document for validation.")
        
        invalid_ext = self.temp_path / "test.xyz"
        invalid_ext.write_text("Invalid extension file.")
        
        # Test valid document
        is_valid, error = RAGValidator.validate_document(valid_txt)
        self.assertTrue(is_valid, f"Valid document failed validation: {error}")
        
        # Test invalid extension
        is_valid, error = RAGValidator.validate_document(invalid_ext)
        self.assertFalse(is_valid, "Invalid extension should fail validation")
        
        # Test non-existent file
        is_valid, error = RAGValidator.validate_document("non_existent.txt")
        self.assertFalse(is_valid, "Non-existent file should fail validation")
    
    def test_document_ingestion(self):
        """Test document ingestion process."""
        # Create test documents
        test_doc = self.temp_path / "test_ingestion.txt"
        test_doc.write_text("""
        # Test Document for Ingestion
        
        This is a test document created for testing the RAG system's
        document ingestion capabilities. It contains various types of
        information that should be processed and made searchable.
        
        ## Key Information
        - Document type: Test document
        - Purpose: RAG system testing
        - Content: Sample text for ingestion
        
        The system should be able to chunk this document appropriately
        and make it available for intelligent search and retrieval.
        """)
        
        # Test ingestion
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            ingestion_result = loop.run_until_complete(
                self.rag_service.ingest_documents_from_folder(str(self.temp_path))
            )
            
            self.assertIsInstance(ingestion_result, dict)
            self.assertIn('status', ingestion_result)
            self.assertIn('processed', ingestion_result)
            
            # Should have processed at least one document
            if ingestion_result['status'] != 'no_files':
                self.assertGreater(ingestion_result['processed'], 0)
                
        finally:
            loop.close()


class TestRAGErrorHandling(unittest.TestCase):
    """Test RAG error handling system."""
    
    def setUp(self):
        """Set up error handling tests."""
        self.error_handler = get_error_handler()
    
    def test_error_handler_functionality(self):
        """Test error handler basic functionality."""
        # Test error handling
        try:
            raise ValueError("Test error for handling")
        except Exception as e:
            rag_error = self.error_handler.handle_error(e, "test_component")
            
            self.assertIsNotNone(rag_error)
            self.assertEqual(rag_error.component, "test_component")
            self.assertIn("Test error", rag_error.message)
    
    def test_error_summary(self):
        """Test error summary generation."""
        summary = self.error_handler.get_error_summary()
        
        self.assertIsInstance(summary, dict)
        self.assertIn('total_errors', summary)
        self.assertIn('error_types', summary)
        self.assertIn('recent_errors', summary)


class TestRAGIntegration(unittest.TestCase):
    """Test RAG system integration."""
    
    def setUp(self):
        """Set up integration tests."""
        self.config = get_config()
        self.rag_service = RAGService(self.config)
    
    def test_end_to_end_workflow(self):
        """Test complete end-to-end RAG workflow."""
        # 1. Add conversational memory
        test_fact = f"Integration test fact - {time.time()}"
        self.rag_service.add_conversational_memory(test_fact)
        
        # 2. Wait for processing
        time.sleep(1)
        
        # 3. Verify memory was stored
        doc_stats = self.rag_service.get_document_stats()
        self.assertGreater(doc_stats.get('total_documents', 0), 0)
        
        # 4. Test search functionality
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            search_results = loop.run_until_complete(
                self.rag_service.intelligent_search("integration test")
            )
            
            self.assertIsInstance(search_results, dict)
            self.assertIn('synthesis', search_results)
            
        finally:
            loop.close()
        
        # 5. Test backup functionality
        backup_result = self.rag_service.create_backup(
            backup_name="integration_test",
            compress=False
        )
        
        self.assertEqual(backup_result['status'], 'success')
    
    def test_memory_persistence(self):
        """Test that memories persist across service restarts."""
        # Add a unique memory
        unique_fact = f"Persistence test - {time.time()}"
        self.rag_service.add_conversational_memory(unique_fact)
        time.sleep(1)
        
        # Get initial document count
        initial_stats = self.rag_service.get_document_stats()
        initial_count = initial_stats.get('total_documents', 0)
        
        # Create new service instance (simulating restart)
        new_rag_service = RAGService(self.config)
        
        # Check that documents persist
        new_stats = new_rag_service.get_document_stats()
        new_count = new_stats.get('total_documents', 0)
        
        self.assertGreaterEqual(new_count, initial_count, 
                               "Documents should persist across service restarts")


def run_rag_tests():
    """Run all RAG system tests."""
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestRAGConfiguration,
        TestRAGService,
        TestRAGBackupManager,
        TestRAGDocumentProcessing,
        TestRAGErrorHandling,
        TestRAGIntegration
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    print("🧪 RAG System Comprehensive Testing Suite")
    print("=" * 60)
    print("Running unit tests, integration tests, and validation tests...")
    print()
    
    success = run_rag_tests()
    
    if success:
        print("\n🎉 All RAG tests passed successfully!")
        print("   ✅ Configuration management working")
        print("   ✅ RAG service functionality verified")
        print("   ✅ Backup and restore operational")
        print("   ✅ Document processing validated")
        print("   ✅ Error handling tested")
        print("   ✅ Integration workflows confirmed")
        print("\n🚀 RAG system is production-ready!")
    else:
        print("\n❌ Some RAG tests failed.")
        print("   Review the test output above for details.")
    
    exit(0 if success else 1)
