#!/usr/bin/env python3
"""
RAG System Test Runner

Convenient script to run all RAG system tests with proper setup and reporting.
"""

import sys
import subprocess
import time
from pathlib import Path


def run_rag_tests():
    """Run the comprehensive RAG test suite."""
    print("🚀 RAG System Test Runner")
    print("=" * 40)
    print("Running comprehensive RAG system tests...")
    print()
    
    # Change to jarvis directory
    jarvis_dir = Path(__file__).parent / "jarvis"
    
    try:
        # Run the test suite
        start_time = time.time()
        
        result = subprocess.run([
            sys.executable, "tests/test_rag_system.py"
        ], cwd=jarvis_dir, capture_output=True, text=True)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Print results
        print("📊 Test Results:")
        print("=" * 20)
        print(result.stdout)
        
        if result.stderr:
            print("⚠️ Warnings/Errors:")
            print(result.stderr)
        
        print(f"\n⏱️ Test Duration: {duration:.2f} seconds")
        
        if result.returncode == 0:
            print("\n🎉 All RAG tests passed!")
            print("   The RAG system is ready for production use.")
            return True
        else:
            print("\n❌ Some tests failed.")
            print("   Please review the output above and fix any issues.")
            return False
            
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return False


def run_quick_validation():
    """Run a quick validation of core RAG functionality."""
    print("\n🔍 Quick RAG Validation")
    print("=" * 30)
    
    try:
        # Add jarvis to path
        sys.path.append(str(Path(__file__).parent / "jarvis"))
        
        from jarvis.config import get_config
        from jarvis.tools.rag_service import RAGService
        
        print("📋 Testing core components...")
        
        # Test 1: Configuration loading
        config = get_config()
        print("✅ Configuration loaded")
        
        # Test 2: RAG service initialization
        rag_service = RAGService(config)
        print("✅ RAG service initialized")
        
        # Test 3: Basic functionality
        doc_stats = rag_service.get_document_stats()
        print(f"✅ Document stats: {doc_stats.get('total_documents', 0)} documents")
        
        # Test 4: Backup functionality
        backups = rag_service.list_backups()
        print(f"✅ Backup system: {len(backups)} backups available")
        
        print("\n🎯 Quick validation completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Quick validation failed: {e}")
        return False


def main():
    """Main test runner function."""
    if len(sys.argv) > 1 and sys.argv[1] == "--quick":
        # Run quick validation only
        success = run_quick_validation()
    else:
        # Run full test suite
        success = run_rag_tests()
        
        # Also run quick validation
        if success:
            run_quick_validation()
    
    print(f"\n{'🎉 SUCCESS' if success else '❌ FAILURE'}: RAG system testing {'completed' if success else 'failed'}")
    
    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
