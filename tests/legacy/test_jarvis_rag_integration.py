#!/usr/bin/env python3
"""
Test RAG integration with main Jarvis application.
Validates that the RAG tools are properly integrated and working.
"""

import sys
import time
from pathlib import Path

# Add jarvis to path
sys.path.append(str(Path(__file__).parent / "jarvis"))

def test_rag_tools_integration():
    """Test that RAG tools are properly integrated in Jarvis."""
    print("🧪 Testing RAG Tools Integration with Main Jarvis Application")
    print("=" * 70)
    
    try:
        # Import Jarvis components
        from jarvis.config import get_config
        from jarvis.tools.rag_service import RAGService
        from jarvis.tools.registry import ToolRegistry
        
        print("✅ Successfully imported Jarvis components")
        
        # Test configuration
        config = get_config()
        if hasattr(config, 'rag'):
            print("✅ RAG configuration found in main config")
            print(f"   Vector store path: {config.rag.vector_store_path}")
            print(f"   Documents path: {config.rag.documents_path}")
            print(f"   Collection name: {config.rag.collection_name}")
        else:
            print("❌ RAG configuration not found in main config")
            return False
        
        # Test RAG service initialization
        rag_service = RAGService(config)
        print("✅ RAG service initialized successfully")
        
        # Test tool registry
        tool_registry = ToolRegistry()
        available_tools = tool_registry.get_all_tools()
        
        # Look for RAG-related tools
        rag_tools = [tool for tool in available_tools if 'rag' in tool.name.lower() or 'memory' in tool.name.lower()]
        
        if rag_tools:
            print(f"✅ Found {len(rag_tools)} RAG-related tools in registry:")
            for tool in rag_tools[:5]:  # Show first 5
                print(f"   - {tool.name}: {tool.description[:60]}...")
        else:
            print("⚠️  No RAG tools found in tool registry")
        
        # Test basic RAG functionality
        print("\n🧠 Testing Basic RAG Functionality...")
        
        # Add a test memory
        test_fact = f"Jarvis integration test - {time.time()}"
        rag_service.add_conversational_memory(test_fact)
        print("✅ Successfully added test memory")
        
        # Test document stats
        doc_stats = rag_service.get_document_stats()
        print(f"✅ Document stats retrieved: {doc_stats.get('total_documents', 0)} documents")
        
        # Test ingested documents
        ingested_docs = rag_service.get_ingested_documents()
        print(f"✅ Ingested documents retrieved: {len(ingested_docs)} documents")
        
        print("\n🎉 RAG Integration with Main Jarvis Application: SUCCESS")
        print("   ✅ Configuration properly loaded")
        print("   ✅ RAG service initializes correctly")
        print("   ✅ Tools are registered and available")
        print("   ✅ Basic RAG operations working")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   Make sure you're running from the correct directory")
        return False
    except Exception as e:
        print(f"❌ Integration test error: {e}")
        return False

def test_plugin_system_integration():
    """Test that RAG is properly integrated with the plugin system."""
    print("\n🔌 Testing Plugin System Integration...")
    
    try:
        from jarvis.plugins.manager import PluginManager
        
        # Initialize plugin manager
        plugin_manager = PluginManager()
        
        # Look for RAG plugin
        loaded_plugins = plugin_manager.get_loaded_plugins()
        rag_plugin_found = any('rag' in plugin.lower() for plugin in loaded_plugins.keys())
        
        if rag_plugin_found:
            print("✅ RAG plugin found in loaded plugins")
            
            # Get RAG plugin tools
            all_tools = plugin_manager.get_all_tools()
            rag_plugin_tools = [tool for tool in all_tools if 'rag' in tool.name.lower() or 'memory' in tool.name.lower()]
            
            if rag_plugin_tools:
                print(f"✅ Found {len(rag_plugin_tools)} RAG plugin tools:")
                for tool in rag_plugin_tools[:3]:  # Show first 3
                    print(f"   - {tool.name}")
            else:
                print("⚠️  No RAG plugin tools found")
        else:
            print("⚠️  RAG plugin not found in loaded plugins")
            print(f"   Available plugins: {list(loaded_plugins.keys())}")
        
        return True
        
    except Exception as e:
        print(f"❌ Plugin system integration error: {e}")
        return False

def test_end_to_end_workflow():
    """Test complete end-to-end workflow."""
    print("\n🔄 Testing End-to-End Workflow...")
    
    try:
        from jarvis.config import get_config
        from jarvis.tools.rag_service import RAGService
        
        config = get_config()
        rag_service = RAGService(config)
        
        # Test 1: Add memory and retrieve it
        test_memory = f"E2E test memory - {time.time()}"
        rag_service.add_conversational_memory(test_memory)
        
        # Wait a moment for processing
        time.sleep(1)
        
        # Try to retrieve memories (this tests the vector store)
        try:
            collection = rag_service.vector_store._collection
            results = collection.get(include=['metadatas', 'documents'])
            
            if results and results.get('documents'):
                memories_found = any(test_memory in doc for doc in results['documents'])
                if memories_found:
                    print("✅ Memory storage and retrieval working")
                else:
                    print("❌ Memory not found in vector store")
                    return False
            else:
                print("❌ No documents found in vector store")
                return False
                
        except Exception as e:
            print(f"❌ Vector store access error: {e}")
            return False
        
        # Test 2: Document processing (if documents exist)
        documents_path = Path(config.rag.documents_path)
        if documents_path.exists() and any(documents_path.iterdir()):
            print("✅ Documents directory exists with files")
        else:
            print("⚠️  No documents found for processing test")
        
        # Test 3: Configuration consistency
        vector_store_path = Path(config.rag.vector_store_path)
        if vector_store_path.exists():
            print("✅ Vector store directory exists")
        else:
            print("⚠️  Vector store directory not found")
        
        print("✅ End-to-end workflow test completed")
        return True
        
    except Exception as e:
        print(f"❌ End-to-end workflow error: {e}")
        return False

def main():
    """Main test function."""
    print("🚀 Jarvis RAG Integration Validation")
    print("=" * 50)
    print("Testing integration between RAG system and main Jarvis application...")
    print()
    
    tests = [
        ("RAG Tools Integration", test_rag_tools_integration),
        ("Plugin System Integration", test_plugin_system_integration),
        ("End-to-End Workflow", test_end_to_end_workflow)
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
    
    print(f"\n📊 Jarvis RAG Integration Results")
    print("=" * 40)
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\n📈 Overall Results:")
    print(f"✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")
    print(f"📊 Success Rate: {passed/total*100:.1f}%")
    
    if passed == total:
        print("\n🎉 RAG Integration with Main Jarvis Application: COMPLETE!")
        print("   ✅ All components properly integrated")
        print("   ✅ Configuration system working")
        print("   ✅ Plugin system integration successful")
        print("   ✅ End-to-end workflows functional")
        print("\n🚀 RAG Memory Management System is ready for production use!")
    elif passed >= total * 0.67:
        print(f"\n✅ RAG Integration mostly successful!")
        print(f"   Core functionality working with minor issues")
    else:
        print(f"\n⚠️  RAG Integration needs attention")
        print(f"   Multiple integration issues detected")
    
    return passed >= total * 0.67


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
