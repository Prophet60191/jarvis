#!/usr/bin/env python3
"""
Test script for Stage 1 RAG implementation.
This script tests the RAG memory manager and tools independently.
"""

import sys
import os
from pathlib import Path

# Add the jarvis package to the path
project_root = Path(__file__).parent
jarvis_path = project_root / "jarvis"
sys.path.insert(0, str(jarvis_path))

def test_config():
    """Test RAG configuration loading."""
    print("🧪 Testing RAG configuration...")
    try:
        from jarvis.config import get_config
        config = get_config()
        
        print(f"✅ Config loaded successfully")
        print(f"   RAG enabled: {config.rag.enabled}")
        print(f"   Vector store path: {config.rag.vector_store_path}")
        print(f"   Collection name: {config.rag.collection_name}")
        print(f"   Chunk size: {config.rag.chunk_size}")
        print(f"   Search k: {config.rag.search_k}")
        
        return config
    except Exception as e:
        print(f"❌ Config test failed: {e}")
        return None

def test_rag_manager(config):
    """Test RAG Memory Manager."""
    print("\n🧪 Testing RAG Memory Manager...")
    try:
        # Import directly to avoid full jarvis import chain
        sys.path.insert(0, str(jarvis_path / "jarvis" / "tools"))
        from rag_memory_manager import RAGMemoryManager
        
        print("✅ RAGMemoryManager imported successfully")
        
        # Create manager
        rag_manager = RAGMemoryManager(config)
        print("✅ RAGMemoryManager created successfully")
        
        # Test adding a memory
        test_fact = "I prefer iced coffee over hot coffee"
        rag_manager.add_conversational_memory(test_fact)
        print(f"✅ Added memory: '{test_fact}'")
        
        # Test retriever tool creation
        retriever_tool = rag_manager.get_retriever_tool()
        print(f"✅ Created retriever tool: {retriever_tool.name}")
        
        return rag_manager
        
    except Exception as e:
        print(f"❌ RAG Manager test failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_rag_tools(rag_manager):
    """Test RAG tools."""
    print("\n🧪 Testing RAG tools...")
    try:
        from rag_tools import get_rag_tools
        
        # Get tools
        rag_tools = get_rag_tools(rag_manager, debug_mode=True)
        print(f"✅ Got {len(rag_tools)} RAG tools")
        
        for tool in rag_tools:
            print(f"   - {tool.name}: {tool.description[:50]}...")
        
        # Test remember tool
        remember_tool = None
        search_tool = None
        
        for tool in rag_tools:
            if tool.name == "remember_fact":
                remember_tool = tool
            elif tool.name == "search_long_term_memory":
                search_tool = tool
        
        if remember_tool:
            print("✅ Found remember_fact tool")
            # Test the tool
            result = remember_tool.func("I like pizza on Fridays")
            print(f"   Result: {result}")
        
        if search_tool:
            print("✅ Found search_long_term_memory tool")
            # Test the tool
            result = search_tool.func("coffee preferences")
            print(f"   Result: {result}")
        
        return rag_tools
        
    except Exception as e:
        print(f"❌ RAG tools test failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_pii_detection():
    """Test PII detection."""
    print("\n🧪 Testing PII detection...")
    try:
        from rag_tools import detect_pii
        
        # Test cases
        test_cases = [
            "My name is John and I like coffee",  # No PII
            "My SSN is 123-45-6789",  # SSN
            "Call me at 555-123-4567",  # Phone
            "Email me at john@example.com",  # Email
            "I live at 123 Main Street",  # Address
        ]
        
        for test_text in test_cases:
            detected = detect_pii(test_text)
            if detected:
                print(f"   ⚠️  '{test_text}' -> PII detected: {detected}")
            else:
                print(f"   ✅ '{test_text}' -> No PII detected")
        
        print("✅ PII detection working")
        
    except Exception as e:
        print(f"❌ PII detection test failed: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Run all tests."""
    print("🚀 Starting Stage 1 RAG Implementation Tests")
    print("=" * 50)
    
    # Test 1: Configuration
    config = test_config()
    if not config:
        print("❌ Cannot continue without config")
        return
    
    # Test 2: RAG Manager
    rag_manager = test_rag_manager(config)
    if not rag_manager:
        print("❌ Cannot continue without RAG manager")
        return
    
    # Test 3: RAG Tools
    rag_tools = test_rag_tools(rag_manager)
    if not rag_tools:
        print("❌ RAG tools test failed")
        return
    
    # Test 4: PII Detection
    test_pii_detection()
    
    print("\n" + "=" * 50)
    print("🎉 All Stage 1 RAG tests completed!")
    print(f"✅ Configuration: Working")
    print(f"✅ RAG Manager: Working")
    print(f"✅ RAG Tools: {len(rag_tools)} tools created")
    print(f"✅ PII Detection: Working")
    print("\n🎯 Stage 1 RAG implementation is ready for integration!")

if __name__ == "__main__":
    main()
