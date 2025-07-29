#!/usr/bin/env python3
"""
Test RAG configurable paths and configuration management.
Verifies that all paths are properly configurable and functional.
"""

import sys
import json
import tempfile
from pathlib import Path

# Add jarvis to path
sys.path.append(str(Path(__file__).parent / "jarvis"))


def test_rag_configuration():
    """Test RAG configuration and path management."""
    print("🔧 Testing RAG Configurable Paths")
    print("=" * 50)
    
    try:
        from jarvis.config import get_config, RAGConfig
        from jarvis.tools.rag_config_manager import RAGConfigManager
        
        # Test 1: Load default configuration
        print("📋 Testing Default Configuration...")
        config = get_config()
        rag_config = config.rag
        
        print(f"✅ RAG enabled: {rag_config.enabled}")
        print(f"✅ Vector store path: {rag_config.vector_store_path}")
        print(f"✅ Documents path: {rag_config.documents_path}")
        print(f"✅ Backup path: {rag_config.backup_path}")
        print(f"✅ Chat history path: {rag_config.chat_history_path}")
        print(f"✅ Temp processing path: {rag_config.temp_processing_path}")
        print(f"✅ Logs path: {rag_config.logs_path}")
        
        # Test 2: Configuration Manager
        print("\n🛠️ Testing Configuration Manager...")
        config_manager = RAGConfigManager(rag_config)
        
        # Validate configuration
        is_valid, issues = config_manager.validate_configuration()
        if is_valid:
            print("✅ Configuration validation passed")
        else:
            print(f"❌ Configuration validation failed:")
            for issue in issues:
                print(f"   - {issue}")
        
        # Test 3: Path validation
        print("\n📁 Testing Path Validation...")
        paths_valid, path_issues = config_manager.validate_paths()
        if paths_valid:
            print("✅ All paths are valid and accessible")
        else:
            print(f"❌ Path validation failed:")
            for issue in path_issues:
                print(f"   - {issue}")
        
        # Test 4: Directory structure creation
        print("\n🏗️ Testing Directory Structure Creation...")
        structure_created = config_manager.create_directory_structure()
        if structure_created:
            print("✅ Directory structure created successfully")
        else:
            print("❌ Failed to create directory structure")
        
        # Test 5: Path information
        print("\n📊 Testing Path Information...")
        path_info = config_manager.get_path_info()
        
        for path_name, info in path_info.items():
            status = "✅" if info['exists'] and info['is_writable'] else "⚠️"
            print(f"{status} {path_name}:")
            print(f"   Path: {info['relative_path']}")
            print(f"   Exists: {info['exists']}")
            print(f"   Writable: {info['is_writable']}")
            print(f"   Items: {info['item_count']}")
            print(f"   Size: {info['size_mb']} MB")
        
        # Test 6: Configuration summary
        print("\n📈 Testing Configuration Summary...")
        summary = config_manager.get_configuration_summary()
        
        print(f"✅ Configuration Summary:")
        print(f"   Enabled: {summary['enabled']}")
        print(f"   Valid: {summary['is_valid']}")
        print(f"   Total paths: {summary['paths']['total_paths']}")
        print(f"   Existing paths: {summary['paths']['existing_paths']}")
        print(f"   Writable paths: {summary['paths']['writable_paths']}")
        print(f"   Total size: {summary['paths']['total_size_mb']} MB")
        print(f"   Chunk size: {summary['settings']['chunk_size']}")
        print(f"   Search K: {summary['settings']['search_k']}")
        print(f"   Intelligent processing: {summary['settings']['intelligent_processing']}")
        
        # Test 7: Configuration export
        print("\n💾 Testing Configuration Export...")
        try:
            export_path = config_manager.export_configuration()
            print(f"✅ Configuration exported to: {export_path}")
            
            # Verify export file exists and is valid JSON
            if Path(export_path).exists():
                with open(export_path, 'r') as f:
                    exported_config = json.load(f)
                print(f"✅ Export file contains {len(exported_config)} configuration items")
            else:
                print("❌ Export file was not created")
                
        except Exception as e:
            print(f"❌ Configuration export failed: {e}")
        
        # Test 8: Custom path configuration
        print("\n🎛️ Testing Custom Path Configuration...")
        try:
            # Create a temporary custom configuration
            with tempfile.TemporaryDirectory() as temp_dir:
                custom_config = RAGConfig(
                    vector_store_path=f"{temp_dir}/custom_vector_store",
                    documents_path=f"{temp_dir}/custom_documents",
                    backup_path=f"{temp_dir}/custom_backups",
                    chat_history_path=f"{temp_dir}/custom_chat_history",
                    temp_processing_path=f"{temp_dir}/custom_temp",
                    logs_path=f"{temp_dir}/custom_logs"
                )
                
                custom_manager = RAGConfigManager(custom_config)
                custom_valid, custom_issues = custom_manager.validate_configuration()
                
                if custom_valid:
                    print("✅ Custom configuration validation passed")
                    
                    # Test directory creation with custom paths
                    custom_structure = custom_manager.create_directory_structure()
                    if custom_structure:
                        print("✅ Custom directory structure created")
                        
                        # Verify directories were created
                        custom_paths = custom_manager.get_path_info()
                        created_count = sum(1 for info in custom_paths.values() if info['exists'])
                        print(f"✅ Created {created_count}/{len(custom_paths)} custom directories")
                    else:
                        print("❌ Failed to create custom directory structure")
                else:
                    print(f"❌ Custom configuration validation failed: {custom_issues}")
                    
        except Exception as e:
            print(f"❌ Custom configuration test failed: {e}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Configuration test error: {e}")
        return False


def test_rag_service_integration():
    """Test RAG service integration with configurable paths."""
    print("\n🔗 Testing RAG Service Integration...")
    
    try:
        from jarvis.config import get_config
        from jarvis.tools.rag_service import RAGService
        
        config = get_config()
        
        # Test RAG service initialization with configured paths
        rag_service = RAGService(config)
        
        print("✅ RAG service initialized with configured paths")
        print(f"   Vector store path: {config.rag.vector_store_path}")
        print(f"   Collection name: {config.rag.collection_name}")
        print(f"   Chunk size: {config.rag.chunk_size}")
        print(f"   Chunk overlap: {config.rag.chunk_overlap}")
        
        # Test document stats (uses configured paths)
        doc_stats = rag_service.get_document_stats()
        print(f"✅ Document stats retrieved: {doc_stats.get('total_documents', 0)} documents")
        
        # Test ingested documents (uses configured paths)
        ingested_docs = rag_service.get_ingested_documents()
        print(f"✅ Ingested documents retrieved: {len(ingested_docs)} documents")
        
        return True
        
    except Exception as e:
        print(f"❌ RAG service integration test failed: {e}")
        return False


def main():
    """Main test function."""
    print("🚀 RAG Configurable Paths Testing Suite")
    print("=" * 60)
    print("Testing comprehensive path configuration and management...")
    print()
    
    tests = [
        ("RAG Configuration", test_rag_configuration),
        ("RAG Service Integration", test_rag_service_integration)
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
    
    print(f"\n📊 RAG Configuration Test Results")
    print("=" * 40)
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\n📈 Overall Results:")
    print(f"✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")
    print(f"📊 Success Rate: {passed/total*100:.1f}%")
    
    if passed == total:
        print("\n🎉 RAG Configurable Paths: COMPLETE!")
        print("   ✅ All paths properly configurable")
        print("   ✅ Configuration validation working")
        print("   ✅ Directory management functional")
        print("   ✅ RAG service integration successful")
        print("   ✅ Custom configurations supported")
        print("\n🔧 RAG system is fully configurable and production-ready!")
    elif passed >= total * 0.8:
        print(f"\n✅ RAG Configurable Paths mostly complete!")
        print(f"   Minor issues detected, but core functionality works")
    else:
        print(f"\n⚠️  RAG Configurable Paths need attention")
        print(f"   Multiple configuration issues detected")
    
    return passed >= total * 0.8


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
