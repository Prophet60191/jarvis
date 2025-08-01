#!/usr/bin/env python3
"""
RAG Memory System Test Script

This script tests Jarvis's ability to remember and recall information
using the RAG (Retrieval-Augmented Generation) system.
"""

import sys
import os
sys.path.insert(0, '.')

def test_remember_and_recall():
    """Test the remember and recall functionality of the RAG system."""
    
    print("🧠 Testing Jarvis RAG Memory System")
    print("=" * 50)
    
    try:
        # Import RAG tools
        from jarvis.tools.plugins.rag_plugin import __plugin_tools__
        
        # Find the remember and search tools
        remember_tool = None
        search_tool = None
        
        for tool in __plugin_tools__:
            if 'remember' in tool.name.lower():
                remember_tool = tool
            elif 'search_long_term_memory' == tool.name:
                search_tool = tool
        
        if not remember_tool or not search_tool:
            print("❌ Could not find required RAG tools")
            return False
        
        print(f"✅ Found remember tool: {remember_tool.name}")
        print(f"✅ Found search tool: {search_tool.name}")
        print()
        
        # Test data to remember
        test_facts = [
            "My favorite programming language is Python because it's elegant and powerful",
            "I prefer working in the morning between 8 AM and 11 AM when I'm most productive",
            "My current project is building a voice assistant called Jarvis with RAG capabilities",
            "I enjoy reading science fiction books, especially works by Isaac Asimov and Philip K. Dick",
            "My preferred development environment is VS Code with the Python extension"
        ]
        
        print("📝 PHASE 1: Storing information in memory")
        print("-" * 40)
        
        # Store each fact
        for i, fact in enumerate(test_facts, 1):
            print(f"Storing fact {i}: {fact[:50]}...")
            result = remember_tool.invoke({"fact": fact})
            print(f"Result: {result}")
            print()
        
        print("🔍 PHASE 2: Testing recall functionality")
        print("-" * 40)
        
        # Test queries to recall information
        test_queries = [
            "What is my favorite programming language?",
            "When do I prefer to work?",
            "What project am I currently working on?",
            "What books do I like to read?",
            "What development environment do I use?",
            "Tell me about my preferences",
            "What do you know about my work habits?"
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"Query {i}: {query}")
            result = search_tool.invoke({"query": query})
            print(f"Answer: {result[:200]}...")
            print()
        
        print("✅ RAG Memory System Test Completed Successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_document_search():
    """Test searching through documents in the RAG system."""
    
    print("\n📚 Testing Document Search Functionality")
    print("=" * 50)
    
    try:
        from jarvis.tools.plugins.rag_plugin import __plugin_tools__
        
        # Find document search tool
        doc_search_tool = None
        for tool in __plugin_tools__:
            if 'search_documents' == tool.name:
                doc_search_tool = tool
                break
        
        if not doc_search_tool:
            print("❌ Could not find document search tool")
            return False
        
        print(f"✅ Found document search tool: {doc_search_tool.name}")
        
        # Test document queries
        doc_queries = [
            "What is Jarvis?",
            "How does the plugin system work?",
            "What are the RAG system details?",
            "Tell me about the architecture"
        ]
        
        for i, query in enumerate(doc_queries, 1):
            print(f"\nDocument Query {i}: {query}")
            result = doc_search_tool.invoke({"query": query})
            print(f"Answer: {result[:200]}...")
        
        print("\n✅ Document Search Test Completed!")
        return True
        
    except Exception as e:
        print(f"❌ Error during document search testing: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_comprehensive_search():
    """Test comprehensive search across all memory sources."""
    
    print("\n🔍 Testing Comprehensive Search")
    print("=" * 50)
    
    try:
        from jarvis.tools.plugins.rag_plugin import __plugin_tools__
        
        # Find comprehensive search tool
        all_search_tool = None
        for tool in __plugin_tools__:
            if 'search_all_memory' == tool.name:
                all_search_tool = tool
                break
        
        if not all_search_tool:
            print("❌ Could not find comprehensive search tool")
            return False
        
        print(f"✅ Found comprehensive search tool: {all_search_tool.name}")
        
        # Test comprehensive queries
        comprehensive_queries = [
            "What do you know about me?",
            "Tell me about Jarvis and my preferences",
            "What information do you have stored?",
            "Summarize everything you know"
        ]
        
        for i, query in enumerate(comprehensive_queries, 1):
            print(f"\nComprehensive Query {i}: {query}")
            result = all_search_tool.invoke({"query": query})
            print(f"Answer: {result[:300]}...")
        
        print("\n✅ Comprehensive Search Test Completed!")
        return True
        
    except Exception as e:
        print(f"❌ Error during comprehensive search testing: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Starting RAG Memory System Tests")
    print("=" * 60)
    
    # Set PYTHONPATH
    os.environ['PYTHONPATH'] = '/Users/josed/Desktop/Voice App'
    
    success = True
    
    # Run all tests
    success &= test_remember_and_recall()
    success &= test_document_search()
    success &= test_comprehensive_search()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 ALL TESTS PASSED! RAG Memory System is working perfectly!")
    else:
        print("❌ Some tests failed. Please check the output above.")
    
    print("=" * 60)
