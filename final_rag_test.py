#!/usr/bin/env python3
"""
Final RAG System Comprehensive Test

This script runs a complete test of all RAG functionality after improvements.
"""

import sys
import os
sys.path.insert(0, '.')
os.environ['PYTHONPATH'] = '/Users/josed/Desktop/Voice App'

def test_memory_storage_and_retrieval():
    """Test memory storage and retrieval with improved system."""
    
    print("🧠 FINAL TEST: Memory Storage and Retrieval")
    print("=" * 60)
    
    try:
        from jarvis.tools.plugins.rag_plugin import remember_fact, search_long_term_memory
        
        # Store a new test fact
        test_fact = "I completed the RAG system testing on July 31, 2025 and it works perfectly"
        
        print(f"Storing: {test_fact}")
        result = remember_fact.invoke({"fact": test_fact})
        print(f"Storage result: {result}")
        
        # Test retrieval
        print(f"\nTesting retrieval...")
        search_result = search_long_term_memory.invoke({"query": "When did I complete RAG testing?"})
        print(f"Search result: {search_result[:200]}...")
        
        return "RAG testing" in search_result or "July 31" in search_result
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_document_search():
    """Test document search functionality."""
    
    print("\n📚 FINAL TEST: Document Search")
    print("=" * 60)
    
    try:
        from jarvis.tools.plugins.rag_plugin import search_documents
        
        queries = [
            "What is Jarvis and what are its key features?",
            "How does the plugin system work in Jarvis?",
            "What are the technical details of the RAG system?",
            "Tell me about the architecture and memory system"
        ]
        
        success_count = 0
        
        for query in queries:
            print(f"\nQuery: {query}")
            result = search_documents.invoke({"query": query})
            
            # Check if we got actual document content (not the "no information" message)
            if "data/documents/" in result and len(result) > 100:
                print("✅ SUCCESS: Got detailed document information")
                success_count += 1
            else:
                print("❌ FAILED: No document information found")
            
            print(f"Answer preview: {result[:150]}...")
        
        return success_count >= 3  # At least 3 out of 4 should work
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_comprehensive_search():
    """Test comprehensive search across all sources."""
    
    print("\n🔍 FINAL TEST: Comprehensive Search")
    print("=" * 60)
    
    try:
        from jarvis.tools.plugins.rag_plugin import search_all_memory
        
        queries = [
            "What do you know about Jarvis?",
            "Tell me about my preferences and the system capabilities",
            "What information do you have about RAG and plugins?"
        ]
        
        success_count = 0
        
        for query in queries:
            print(f"\nQuery: {query}")
            result = search_all_memory.invoke({"query": query})
            
            # Check if we got meaningful results
            if len(result) > 50 and ("conversation" in result.lower() or "document" in result.lower()):
                print("✅ SUCCESS: Got comprehensive information")
                success_count += 1
            else:
                print("❌ LIMITED: Got limited information")
            
            print(f"Answer preview: {result[:150]}...")
        
        return success_count >= 2  # At least 2 out of 3 should work well
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_conversation_search():
    """Test conversational memory search."""
    
    print("\n💬 FINAL TEST: Conversational Memory Search")
    print("=" * 60)
    
    try:
        from jarvis.tools.plugins.rag_plugin import search_conversations
        
        queries = [
            "What programming language do I prefer?",
            "What are my work preferences?",
            "What do you know about my personal preferences?"
        ]
        
        success_count = 0
        
        for query in queries:
            print(f"\nQuery: {query}")
            result = search_conversations.invoke({"query": query})
            
            # Check if we got conversational results
            if "conversation" in result.lower() and len(result) > 30:
                print("✅ SUCCESS: Found conversational memories")
                success_count += 1
            else:
                print("❌ LIMITED: Limited conversational results")
            
            print(f"Answer preview: {result[:150]}...")
        
        return success_count >= 1  # At least 1 should work
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Run all final tests."""
    
    print("🚀 FINAL RAG SYSTEM COMPREHENSIVE TEST")
    print("=" * 80)
    print("Testing all improvements and functionality...")
    print("=" * 80)
    
    results = {
        "Memory Storage & Retrieval": test_memory_storage_and_retrieval(),
        "Document Search": test_document_search(),
        "Comprehensive Search": test_comprehensive_search(),
        "Conversational Search": test_conversation_search()
    }
    
    print("\n" + "=" * 80)
    print("📊 FINAL TEST RESULTS")
    print("=" * 80)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:<30} {status}")
        if result:
            passed += 1
    
    print("=" * 80)
    print(f"OVERALL SCORE: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 EXCELLENT! All tests passed - RAG system is fully functional!")
        grade = "A+"
    elif passed >= total * 0.8:
        print("🎯 GREAT! Most tests passed - RAG system is working well!")
        grade = "A"
    elif passed >= total * 0.6:
        print("👍 GOOD! Majority of tests passed - RAG system is functional!")
        grade = "B+"
    else:
        print("⚠️ NEEDS WORK! Some tests failed - improvements needed!")
        grade = "B-"
    
    print(f"FINAL GRADE: {grade}")
    print("=" * 80)
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
