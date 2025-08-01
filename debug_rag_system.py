#!/usr/bin/env python3
"""
Comprehensive RAG System Debug Tests
This script will systematically test and debug the RAG memory system.
"""

import asyncio
import sys
import time
sys.path.append('jarvis')

from jarvis.tools.rag_memory_manager import RAGMemoryManager
from jarvis.config import get_config

async def debug_rag_system():
    """Run comprehensive RAG system debugging tests."""
    print("🧪 COMPREHENSIVE RAG SYSTEM DEBUG")
    print("=" * 60)
    
    try:
        # Initialize RAG system
        print("1️⃣ INITIALIZING RAG SYSTEM...")
        config = get_config()
        rag_manager = RAGMemoryManager(config)
        print("✅ RAG system initialized")
        
        # Test 1: Check current database contents
        print("\n2️⃣ CHECKING CURRENT DATABASE CONTENTS...")
        try:
            all_docs = rag_manager.vector_store.similarity_search("", k=20)
            print(f"📊 Total documents in database: {len(all_docs)}")
            
            print("\n📋 Current database contents:")
            for i, doc in enumerate(all_docs[:10], 1):
                content = doc.page_content.strip()[:80]
                print(f"  {i:2d}. {content}...")
            
            if len(all_docs) > 10:
                print(f"  ... and {len(all_docs) - 10} more documents")
                
        except Exception as e:
            print(f"❌ Error checking database: {e}")
        
        # Test 2: Store a test memory
        print("\n3️⃣ STORING TEST MEMORY...")
        test_memory = "I like jazz music for relaxing"
        try:
            rag_manager.add_conversational_memory(test_memory)
            print(f"✅ Stored: '{test_memory}'")
            
            # Wait for indexing
            print("⏳ Waiting 2 seconds for indexing...")
            time.sleep(2)
            
        except Exception as e:
            print(f"❌ Error storing memory: {e}")
        
        # Test 3: Search for the stored memory immediately
        print("\n4️⃣ IMMEDIATE SEARCH TEST...")
        search_queries = [
            "jazz",
            "music", 
            "jazz music",
            "I like jazz",
            "relaxing"
        ]
        
        for query in search_queries:
            try:
                results = rag_manager.vector_store.similarity_search(query, k=5)
                print(f"\n🔍 Search '{query}': {len(results)} results")
                
                found_test_memory = False
                for i, result in enumerate(results, 1):
                    content = result.page_content.strip()
                    if "jazz music" in content.lower():
                        found_test_memory = True
                        print(f"  ✅ {i}. {content}")
                    else:
                        print(f"  ❌ {i}. {content[:60]}...")
                
                if found_test_memory:
                    print(f"✅ Found test memory with query '{query}'")
                else:
                    print(f"❌ Test memory NOT found with query '{query}'")
                    
            except Exception as e:
                print(f"❌ Search error for '{query}': {e}")
        
        # Test 4: Check database after storage
        print("\n5️⃣ CHECKING DATABASE AFTER STORAGE...")
        try:
            all_docs_after = rag_manager.vector_store.similarity_search("", k=25)
            print(f"📊 Total documents after storage: {len(all_docs_after)}")
            
            # Look for our test memory specifically
            jazz_docs = [doc for doc in all_docs_after if "jazz" in doc.page_content.lower()]
            print(f"🎵 Documents containing 'jazz': {len(jazz_docs)}")
            
            for doc in jazz_docs:
                print(f"  🎵 {doc.page_content.strip()}")
                
        except Exception as e:
            print(f"❌ Error checking database after storage: {e}")
        
        # Test 5: Test similarity search with different parameters
        print("\n6️⃣ TESTING SIMILARITY SEARCH PARAMETERS...")
        test_queries = ["music", "jazz music", "I like jazz music"]
        
        for query in test_queries:
            print(f"\n🔍 Testing query: '{query}'")
            for k in [3, 5, 10, 15]:
                try:
                    results = rag_manager.vector_store.similarity_search(query, k=k)
                    jazz_found = any("jazz" in r.page_content.lower() for r in results)
                    print(f"  k={k:2d}: {len(results)} results, jazz found: {'✅' if jazz_found else '❌'}")
                except Exception as e:
                    print(f"  k={k:2d}: Error - {e}")
        
        # Test 6: Test with exact content search
        print("\n7️⃣ TESTING EXACT CONTENT SEARCH...")
        exact_searches = [
            "I like jazz music for relaxing",
            "jazz music for relaxing", 
            "like jazz music",
            "jazz"
        ]
        
        for exact_query in exact_searches:
            try:
                results = rag_manager.vector_store.similarity_search(exact_query, k=10)
                print(f"\n🎯 Exact search '{exact_query}': {len(results)} results")
                
                for i, result in enumerate(results[:3], 1):
                    content = result.page_content.strip()
                    similarity = "HIGH" if exact_query.lower() in content.lower() else "LOW"
                    print(f"  {i}. [{similarity}] {content[:70]}...")
                    
            except Exception as e:
                print(f"❌ Exact search error for '{exact_query}': {e}")
        
        # Test 7: Check vector store type and configuration
        print("\n8️⃣ CHECKING VECTOR STORE CONFIGURATION...")
        try:
            print(f"Vector store type: {type(rag_manager.vector_store)}")
            print(f"Embeddings type: {type(rag_manager.embeddings)}")
            
            # Try to get collection info if it's ChromaDB
            if hasattr(rag_manager.vector_store, '_collection'):
                collection = rag_manager.vector_store._collection
                print(f"Collection name: {collection.name}")
                count = collection.count()
                print(f"Collection count: {count}")
                
        except Exception as e:
            print(f"❌ Error checking vector store config: {e}")
        
        print("\n" + "=" * 60)
        print("🎯 DEBUG SUMMARY:")
        print("1. Check if test memory was stored successfully")
        print("2. Check if search queries are finding the stored memory")
        print("3. Check if there are indexing delays or similarity issues")
        print("4. Check vector store configuration and collection status")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Critical debug error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_rag_system())
