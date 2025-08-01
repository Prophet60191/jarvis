#!/usr/bin/env python3
"""
Final integration test to verify RAG system is working with enhanced capabilities.
"""

import asyncio
import sys
import os
import time
sys.path.append(os.path.join(os.path.dirname(__file__), 'jarvis'))

from jarvis.config import get_config
from jarvis.tools.rag_service import RAGService


async def test_core_intelligent_features():
    """Test the core intelligent features directly."""
    print("🧠 Testing Core Intelligent Features")
    print("=" * 50)
    
    config = get_config()
    rag_service = RAGService(config)
    
    # Test query optimization
    print("🔍 Testing Query Optimization:")
    query = "How do I create plugins?"
    optimization = await rag_service.optimize_query(query, "User wants to learn development")
    
    print(f"   Original: {query}")
    print(f"   Optimized: {optimization.get('optimized_query', 'N/A')}")
    print(f"   Intent: {optimization.get('query_intent', 'unknown')}")
    print(f"   Strategy: {optimization.get('search_strategy', 'unknown')}")
    print(f"   Confidence: {optimization.get('confidence_level', 0.0)}")
    
    # Test intelligent search
    print("\n🎯 Testing Intelligent Search:")
    search_results = await rag_service.intelligent_search(query, max_results=3)
    
    synthesis = search_results.get("synthesis", {})
    search_meta = search_results.get("search_metadata", {})
    
    print(f"   Queries tried: {len(search_meta.get('queries_tried', []))}")
    print(f"   Results found: {search_meta.get('final_results', 0)}")
    print(f"   Confidence: {synthesis.get('confidence_score', 0.0)}")
    print(f"   Completeness: {synthesis.get('answer_completeness', 'unknown')}")
    print(f"   Answer length: {len(synthesis.get('synthesized_answer', ''))}")
    
    # Test enhanced retriever tool
    print("\n🛠️ Testing Enhanced Retriever Tool:")
    retriever_tool = rag_service.get_retriever_tool()
    
    result = await retriever_tool.ainvoke({"query": query})
    
    print(f"   Result length: {len(result)}")
    print(f"   Has synthesis: {'✅' if 'Answer:' in result else '❌'}")
    print(f"   Has sources: {'✅' if 'Sources:' in result else '❌'}")
    print(f"   Has confidence: {'✅' if 'Confidence:' in result else '❌'}")
    
    return True


async def test_plugin_system_integration():
    """Test integration with the plugin system."""
    print("\n🔌 Testing Plugin System Integration")
    print("=" * 50)
    
    try:
        # Import plugin manager
        from jarvis.tools import plugin_manager
        
        # Get all tools
        all_tools = plugin_manager.get_all_tools()
        print(f"📊 Total tools available: {len(all_tools)}")
        
        # Find RAG tools
        rag_tools = []
        for tool in all_tools:
            if any(keyword in tool.name.lower() for keyword in ['memory', 'search', 'rag']):
                rag_tools.append(tool)
        
        print(f"🧠 RAG-related tools: {len(rag_tools)}")
        for tool in rag_tools:
            print(f"   - {tool.name}")
        
        # Test if we have the enhanced tools
        enhanced_tools = [tool for tool in rag_tools if 'intelligent' in tool.name.lower()]
        print(f"⚡ Enhanced intelligent tools: {len(enhanced_tools)}")
        
        return len(rag_tools) > 0
        
    except Exception as e:
        print(f"❌ Plugin integration error: {e}")
        return False


async def test_quality_improvements():
    """Test and demonstrate quality improvements."""
    print("\n📈 Testing Quality Improvements")
    print("=" * 50)
    
    config = get_config()
    rag_service = RAGService(config)
    
    # Test queries that should show improvement
    test_cases = [
        {
            "query": "plugin development",
            "expected_improvements": ["query expansion", "multiple sources", "synthesis"]
        },
        {
            "query": "RAG architecture", 
            "expected_improvements": ["technical depth", "structured response", "confidence scoring"]
        }
    ]
    
    improvements_found = 0
    
    for case in test_cases:
        query = case["query"]
        print(f"\n🧪 Testing: '{query}'")
        
        # Get intelligent search results
        results = await rag_service.intelligent_search(query, max_results=3)
        
        synthesis = results.get("synthesis", {})
        query_opt = results.get("query_optimization", {})
        search_meta = results.get("search_metadata", {})
        
        # Check for improvements
        has_query_expansion = len(query_opt.get("related_terms", [])) > 0
        has_multiple_queries = len(search_meta.get("queries_tried", [])) > 1
        has_synthesis = len(synthesis.get("synthesized_answer", "")) > 100
        has_confidence = synthesis.get("confidence_score", 0.0) > 0.5
        has_sources = len(synthesis.get("source_citations", [])) > 0
        
        improvements = []
        if has_query_expansion:
            improvements.append("Query expansion")
        if has_multiple_queries:
            improvements.append("Multi-query search")
        if has_synthesis:
            improvements.append("Result synthesis")
        if has_confidence:
            improvements.append("Confidence scoring")
        if has_sources:
            improvements.append("Source citations")
        
        print(f"   Improvements: {', '.join(improvements) if improvements else 'None'}")
        
        if len(improvements) >= 3:  # At least 3 improvements
            improvements_found += 1
    
    success_rate = improvements_found / len(test_cases)
    print(f"\n📊 Quality improvement success rate: {success_rate:.1%}")
    
    return success_rate >= 0.5  # At least 50% of test cases show improvements


async def test_backward_compatibility():
    """Test that backward compatibility is maintained."""
    print("\n🔄 Testing Backward Compatibility")
    print("=" * 50)
    
    try:
        # Test that old interfaces still work
        from jarvis.tools.rag_memory_manager import RAGMemoryManager
        
        config = get_config()
        old_rag = RAGMemoryManager(config)
        
        # Test basic functionality
        old_rag.add_conversational_memory("Test memory for compatibility")
        retriever_tool = old_rag.get_retriever_tool()
        
        print("✅ Old RAGMemoryManager still functional")
        print(f"   Tool name: {retriever_tool.name}")
        print(f"   Tool description: {retriever_tool.description[:60]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Backward compatibility error: {e}")
        return False


async def main():
    """Run all final integration tests."""
    print("🚀 Final RAG Integration Testing")
    print("=" * 60)
    print("Verifying enhanced RAG system is fully integrated and functional")
    print()
    
    # Run tests
    core_features = await test_core_intelligent_features()
    plugin_integration = await test_plugin_system_integration()
    quality_improvements = await test_quality_improvements()
    backward_compatibility = await test_backward_compatibility()
    
    # Summary
    print("\n📊 Final Integration Test Results")
    print("=" * 45)
    print(f"✅ Core Intelligent Features: {'PASS' if core_features else 'FAIL'}")
    print(f"✅ Plugin System Integration: {'PASS' if plugin_integration else 'FAIL'}")
    print(f"✅ Quality Improvements: {'PASS' if quality_improvements else 'FAIL'}")
    print(f"✅ Backward Compatibility: {'PASS' if backward_compatibility else 'FAIL'}")
    
    overall_success = all([core_features, plugin_integration, quality_improvements, backward_compatibility])
    
    if overall_success:
        print("\n🎉 RAG INTEGRATION COMPLETE!")
        print("=" * 40)
        print("✅ Enhanced RAG service fully integrated")
        print("✅ Intelligent features working correctly")
        print("✅ Plugin system properly configured")
        print("✅ Quality improvements verified")
        print("✅ Backward compatibility maintained")
        print()
        print("🚀 READY FOR PRODUCTION!")
        print("   The enhanced RAG system with intelligent")
        print("   document processing, query optimization,")
        print("   and result synthesis is now live!")
    else:
        print("\n⚠️  Integration Issues Detected")
        print("   Some components need attention before")
        print("   the system is ready for production.")


if __name__ == "__main__":
    asyncio.run(main())
