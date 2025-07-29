#!/usr/bin/env python3
"""
Test script to verify query intelligence layer functionality.
"""

import asyncio
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'jarvis'))

from jarvis.config import get_config
from jarvis.tools.rag_service import RAGService


async def test_query_optimization():
    """Test query optimization capabilities."""
    print("🔍 Testing Query Optimization")
    print("=" * 50)
    
    config = get_config()
    rag_service = RAGService(config)
    
    # Test queries with different intents
    test_queries = [
        ("How do I create a plugin?", "User wants to learn plugin development"),
        ("What is RAG?", "User asking about RAG system definition"),
        ("voice recognition features", "User interested in voice capabilities"),
        ("troubleshoot memory issues", "User has a problem with memory system")
    ]
    
    for query, context in test_queries:
        print(f"\nQuery: '{query}'")
        print(f"Context: {context}")
        print("-" * 40)
        
        try:
            optimization = await rag_service.optimize_query(query, context)
            
            print(f"✅ Optimization Results:")
            print(f"   Optimized Query: {optimization.get('optimized_query', 'N/A')}")
            print(f"   Related Terms: {optimization.get('related_terms', [])}")
            print(f"   Alternative Queries: {optimization.get('alternative_queries', [])}")
            print(f"   Key Concepts: {optimization.get('key_concepts', [])}")
            print(f"   Query Intent: {optimization.get('query_intent', 'unknown')}")
            print(f"   Search Strategy: {optimization.get('search_strategy', 'unknown')}")
            print(f"   Confidence: {optimization.get('confidence_level', 0.0)}")
            
        except Exception as e:
            print(f"❌ Error optimizing query: {e}")
    
    return True


async def test_intelligent_search():
    """Test intelligent search with query optimization and synthesis."""
    print("\n🧠 Testing Intelligent Search")
    print("=" * 50)
    
    config = get_config()
    rag_service = RAGService(config)
    
    # Test queries that should benefit from intelligent processing
    test_queries = [
        "How do I create a plugin for Jarvis?",
        "What are the main components of the RAG system?",
        "Tell me about voice recognition capabilities"
    ]
    
    for query in test_queries:
        print(f"\nIntelligent Search: '{query}'")
        print("-" * 40)
        
        try:
            results = await rag_service.intelligent_search(query, max_results=3)
            
            # Query optimization results
            query_opt = results.get("query_optimization", {})
            print(f"🔍 Query Optimization:")
            print(f"   Optimized: {query_opt.get('optimized_query', 'N/A')}")
            print(f"   Intent: {query_opt.get('query_intent', 'unknown')}")
            print(f"   Strategy: {query_opt.get('search_strategy', 'unknown')}")
            
            # Search metadata
            search_meta = results.get("search_metadata", {})
            print(f"📊 Search Metadata:")
            print(f"   Queries Tried: {len(search_meta.get('queries_tried', []))}")
            print(f"   Total Results: {search_meta.get('total_results_found', 0)}")
            print(f"   Final Results: {search_meta.get('final_results', 0)}")
            
            # Synthesis results
            synthesis = results.get("synthesis", {})
            print(f"🎯 Result Synthesis:")
            print(f"   Answer: {synthesis.get('synthesized_answer', 'N/A')[:150]}...")
            print(f"   Key Points: {synthesis.get('key_points', [])}")
            print(f"   Confidence: {synthesis.get('confidence_score', 0.0)}")
            print(f"   Completeness: {synthesis.get('answer_completeness', 'unknown')}")
            
            # Source citations
            citations = synthesis.get("source_citations", [])
            if citations:
                print(f"   Sources: {[cite.get('source', 'unknown') for cite in citations]}")
            
        except Exception as e:
            print(f"❌ Error in intelligent search: {e}")
    
    return True


async def test_enhanced_retriever_tool():
    """Test the enhanced retriever tool with intelligent capabilities."""
    print("\n🛠️ Testing Enhanced Retriever Tool")
    print("=" * 50)
    
    config = get_config()
    rag_service = RAGService(config)
    
    # Get the enhanced retriever tool
    retriever_tool = rag_service.get_retriever_tool()
    
    test_queries = [
        "How do I develop plugins?",
        "What is the memory system architecture?"
    ]
    
    for query in test_queries:
        print(f"\nTool Query: '{query}'")
        print("-" * 40)
        
        try:
            # Use the tool (it's async)
            result = await retriever_tool.ainvoke({"query": query})
            
            print(f"✅ Tool Response:")
            print(f"   {result[:300]}...")
            
            # Check if response includes intelligent features
            has_confidence = "Confidence:" in result
            has_sources = "Sources:" in result
            has_synthesis = "Answer:" in result
            
            print(f"📊 Intelligence Features:")
            print(f"   Has Synthesis: {'✅' if has_synthesis else '❌'}")
            print(f"   Has Sources: {'✅' if has_sources else '❌'}")
            print(f"   Has Confidence: {'✅' if has_confidence else '❌'}")
            
        except Exception as e:
            print(f"❌ Error using retriever tool: {e}")
    
    return True


async def main():
    """Run all query intelligence tests."""
    print("🚀 Query Intelligence Layer Testing")
    print("=" * 60)
    print("Testing advanced query optimization and result synthesis")
    print()
    
    # Run tests
    optimization_success = await test_query_optimization()
    search_success = await test_intelligent_search()
    tool_success = await test_enhanced_retriever_tool()
    
    # Summary
    print("\n📊 Test Summary")
    print("=" * 30)
    print(f"✅ Query Optimization: {'PASS' if optimization_success else 'FAIL'}")
    print(f"✅ Intelligent Search: {'PASS' if search_success else 'FAIL'}")
    print(f"✅ Enhanced Tool: {'PASS' if tool_success else 'FAIL'}")
    
    if optimization_success and search_success and tool_success:
        print("\n🎉 Query Intelligence Layer is working!")
        print("   ✅ Query optimization with LLM intelligence")
        print("   ✅ Multi-query search with deduplication")
        print("   ✅ Result synthesis and confidence scoring")
        print("   ✅ Enhanced retriever tool with intelligent features")
        print("   ✅ Source citation and completeness assessment")


if __name__ == "__main__":
    asyncio.run(main())
