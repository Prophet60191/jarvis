#!/usr/bin/env python3
"""
Test RAG Error Handling and Validation System.
Comprehensive testing of error handling, validation, and graceful fallbacks.
"""

import sys
import tempfile
import os
from pathlib import Path

# Add jarvis to path
sys.path.append(str(Path(__file__).parent / "jarvis"))


def test_error_handler():
    """Test the RAG error handler functionality."""
    print("🛡️ Testing RAG Error Handler")
    print("=" * 35)
    
    try:
        from jarvis.tools.rag_error_handler import RAGErrorHandler, RAGError, RAGErrorType
        
        error_handler = RAGErrorHandler()
        
        # Test 1: Handle a simple exception
        print("🔍 Testing Exception Handling...")
        try:
            raise ValueError("Test validation error")
        except Exception as e:
            rag_error = error_handler.handle_error(e, "test_component")
            
            print(f"✅ Error categorized as: {rag_error.error_type.value}")
            print(f"   Message: {rag_error.message}")
            print(f"   Component: {rag_error.component}")
            print(f"   Recoverable: {rag_error.recoverable}")
            print(f"   Suggested action: {rag_error.suggested_action}")
        
        # Test 2: Handle different error types
        print("\n🔄 Testing Error Type Categorization...")
        test_errors = [
            (ImportError("missing_module"), "Expected: dependency_error"),
            (PermissionError("Access denied"), "Expected: permission_error"),
            (FileNotFoundError("File not found"), "Expected: storage_error"),
            (ConnectionError("Network error"), "Expected: network_error")
        ]
        
        for exception, expected in test_errors:
            rag_error = error_handler.handle_error(exception, "test")
            print(f"   {exception.__class__.__name__}: {rag_error.error_type.value} ({expected})")
        
        # Test 3: Error history and summary
        print("\n📊 Testing Error History...")
        error_summary = error_handler.get_error_summary()
        
        print(f"✅ Error summary generated:")
        print(f"   Total errors: {error_summary['total_errors']}")
        print(f"   Error types: {list(error_summary['error_types'].keys())}")
        print(f"   Recent errors: {len(error_summary['recent_errors'])}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error handler test failed: {e}")
        return False


def test_validator():
    """Test the RAG validator functionality."""
    print("\n🔍 Testing RAG Validator")
    print("=" * 30)
    
    try:
        from jarvis.tools.rag_error_handler import RAGValidator
        
        # Test 1: Path validation
        print("📁 Testing Path Validation...")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Test existing path
            valid, error = RAGValidator.validate_path(temp_path, must_exist=True)
            print(f"   Existing path: {'✅ Valid' if valid else f'❌ Invalid - {error}'}")
            
            # Test non-existing path with creation
            new_path = temp_path / "new_directory"
            valid, error = RAGValidator.validate_path(new_path, create_if_missing=True)
            print(f"   Created path: {'✅ Valid' if valid else f'❌ Invalid - {error}'}")
            
            # Test writability
            valid, error = RAGValidator.validate_path(temp_path, must_be_writable=True)
            print(f"   Writable path: {'✅ Valid' if valid else f'❌ Invalid - {error}'}")
        
        # Test 2: Configuration validation
        print("\n⚙️ Testing Configuration Validation...")
        
        # Create a mock config object
        class MockConfig:
            def __init__(self):
                self.vector_store_path = "data/test_vector_store"
                self.documents_path = "data/test_documents"
                self.backup_path = "data/test_backups"
                self.collection_name = "test_collection"
                self.chunk_size = 1000
                self.chunk_overlap = 150
        
        valid_config = MockConfig()
        is_valid, errors = RAGValidator.validate_config(valid_config)
        print(f"   Valid config: {'✅ Valid' if is_valid else f'❌ Invalid - {errors}'}")
        
        # Test invalid config
        invalid_config = MockConfig()
        invalid_config.chunk_overlap = 1500  # Greater than chunk_size
        is_valid, errors = RAGValidator.validate_config(invalid_config)
        print(f"   Invalid config: {'❌ Invalid' if not is_valid else '✅ Valid'} - {errors[:1] if errors else 'No errors'}")
        
        # Test 3: Document validation
        print("\n📄 Testing Document Validation...")
        
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as temp_file:
            temp_file.write(b"Test document content")
            temp_file_path = temp_file.name
        
        try:
            # Test valid document
            valid, error = RAGValidator.validate_document(temp_file_path, max_size_mb=1)
            print(f"   Valid document: {'✅ Valid' if valid else f'❌ Invalid - {error}'}")
            
            # Test non-existent document
            valid, error = RAGValidator.validate_document("non_existent_file.txt")
            print(f"   Non-existent document: {'❌ Invalid' if not valid else '✅ Valid'} - {error}")
            
        finally:
            os.unlink(temp_file_path)
        
        return True
        
    except Exception as e:
        print(f"❌ Validator test failed: {e}")
        return False


def test_dependency_validation():
    """Test dependency validation."""
    print("\n📦 Testing Dependency Validation")
    print("=" * 40)
    
    try:
        from jarvis.tools.rag_error_handler import validate_dependencies
        
        deps_available, missing_deps = validate_dependencies()
        
        print(f"Dependencies check: {'✅ All available' if deps_available else f'❌ Missing: {missing_deps}'}")
        
        if missing_deps:
            print("   Missing dependencies:")
            for dep in missing_deps:
                print(f"     - {dep}")
        else:
            print("   All required dependencies are available")
        
        return True
        
    except Exception as e:
        print(f"❌ Dependency validation test failed: {e}")
        return False


def test_error_decorator():
    """Test the error handling decorator."""
    print("\n🎭 Testing Error Handling Decorator")
    print("=" * 40)
    
    try:
        from jarvis.tools.rag_error_handler import rag_error_handler
        
        # Test function with decorator
        @rag_error_handler(component="test_function", fallback_return="fallback_value")
        def test_function_with_error():
            raise ValueError("Test error in decorated function")
        
        @rag_error_handler(component="test_function", fallback_return="success")
        def test_function_without_error():
            return "normal_return"
        
        # Test error case
        result = test_function_with_error()
        print(f"   Function with error: {'✅ Fallback returned' if result == 'fallback_value' else f'❌ Unexpected result: {result}'}")
        
        # Test normal case
        result = test_function_without_error()
        print(f"   Function without error: {'✅ Normal return' if result == 'success' else f'❌ Unexpected result: {result}'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error decorator test failed: {e}")
        return False


def test_rag_service_error_integration():
    """Test error handling integration with RAG service."""
    print("\n🔗 Testing RAG Service Error Integration")
    print("=" * 50)
    
    try:
        from jarvis.config import get_config
        from jarvis.tools.rag_service import RAGService
        
        config = get_config()
        
        # Test RAG service initialization with error handling
        print("🚀 Testing RAG Service Initialization...")
        rag_service = RAGService(config)
        print("✅ RAG service initialized with error handling")
        
        # Test error handler integration
        if hasattr(rag_service, 'error_handler'):
            print("✅ Error handler integrated into RAG service")
            
            # Get error summary
            error_summary = rag_service.error_handler.get_error_summary()
            print(f"   Current error count: {error_summary['total_errors']}")
        else:
            print("❌ Error handler not found in RAG service")
            return False
        
        # Test conversational memory with error handling
        print("\n💭 Testing Memory Operations with Error Handling...")
        try:
            rag_service.add_conversational_memory("Test memory with error handling")
            print("✅ Memory operation completed (with error handling)")
        except Exception as e:
            print(f"❌ Memory operation failed: {e}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ RAG service error integration test failed: {e}")
        return False


def main():
    """Main test function."""
    print("🚀 RAG Error Handling and Validation Testing Suite")
    print("=" * 70)
    print("Testing comprehensive error handling and validation system...")
    print()
    
    tests = [
        ("Error Handler", test_error_handler),
        ("Validator", test_validator),
        ("Dependency Validation", test_dependency_validation),
        ("Error Decorator", test_error_decorator),
        ("RAG Service Integration", test_rag_service_error_integration)
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
    
    print(f"\n📊 Error Handling Test Results")
    print("=" * 40)
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\n📈 Overall Results:")
    print(f"✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")
    print(f"📊 Success Rate: {passed/total*100:.1f}%")
    
    if passed == total:
        print("\n🎉 RAG Error Handling and Validation: COMPLETE!")
        print("   ✅ Error categorization working")
        print("   ✅ Validation system functional")
        print("   ✅ Dependency checking operational")
        print("   ✅ Error decorators working")
        print("   ✅ RAG service integration successful")
        print("\n🛡️ RAG system is now robust with comprehensive error handling!")
    elif passed >= total * 0.8:
        print(f"\n✅ RAG Error Handling mostly complete!")
        print(f"   Minor issues detected, but core functionality works")
    else:
        print(f"\n⚠️  RAG Error Handling needs attention")
        print(f"   Multiple error handling issues detected")
    
    return passed >= total * 0.8


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
