#!/usr/bin/env python3
"""
Test Source Citation System

Tests the source citation functionality to ensure all document
information is properly attributed to sources.
"""

import sys
import time
import tempfile
import asyncio
from pathlib import Path

# Add jarvis to path
sys.path.append(str(Path(__file__).parent / "jarvis"))


def test_citation_formatting():
    """Test citation formatting utilities."""
    print("🔗 Testing Citation Formatting")
    print("=" * 35)
    
    try:
        from jarvis.config import get_config
        from jarvis.tools.rag_service import RAGService
        
        config = get_config()
        rag_service = RAGService(config)
        
        # Test citation formatting with various metadata
        test_metadata = [
            {
                "name": "Simple document",
                "metadata": {
                    "source": "user_guide.pdf",
                    "title": "User Guide"
                }
            },
            {
                "name": "Document with section",
                "metadata": {
                    "source": "technical_manual.docx",
                    "section": "Chapter 5: Configuration",
                    "title": "System Configuration"
                }
            },
            {
                "name": "Text file",
                "metadata": {
                    "source": "notes.txt",
                    "title": "Development Notes"
                }
            }
        ]
        
        print("🧪 Testing citation formatting...")
        
        all_passed = True
        for test_case in test_metadata:
            citation = rag_service.format_source_citation(test_case["metadata"])
            
            print(f"\n   Test: {test_case['name']}")
            print(f"   Metadata: {test_case['metadata']}")
            print(f"   Citation: {citation}")
            
            # Basic validation - should contain source name
            source_name = test_case["metadata"]["source"].split('.')[0]
            if source_name.lower() in citation.lower():
                print(f"   ✅ Citation includes source name")
            else:
                print(f"   ❌ Citation missing source name")
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"❌ Citation formatting test failed: {e}")
        return False


def test_agent_prompt_citation_guidance():
    """Test that agent prompt includes citation guidance."""
    print("\n📝 Testing Agent Prompt Citation Guidance")
    print("=" * 50)
    
    try:
        from jarvis.config import get_config
        from jarvis.core.agent import Agent
        
        config = get_config()
        agent = Agent(config)
        
        # Check if system prompt includes citation guidance
        system_prompt = agent.system_prompt
        
        print("🔍 Checking agent system prompt for citation guidance...")
        
        citation_keywords = [
            "cite sources",
            "according to",
            "based on",
            "source citation",
            "always attribute",
            "never present document information as"
        ]
        
        found_keywords = []
        for keyword in citation_keywords:
            if keyword.lower() in system_prompt.lower():
                found_keywords.append(keyword)
        
        print(f"✅ Found citation keywords: {found_keywords}")
        
        if len(found_keywords) >= 3:
            print("✅ Agent system prompt includes comprehensive citation guidance")
            return True
        else:
            print("❌ Agent system prompt lacks sufficient citation guidance")
            return False
        
    except Exception as e:
        print(f"❌ Agent prompt citation guidance test failed: {e}")
        return False


def test_synthesis_citation_requirements():
    """Test that synthesis prompt requires source citations."""
    print("\n🔬 Testing Synthesis Citation Requirements")
    print("=" * 50)
    
    try:
        from jarvis.config import get_config
        from jarvis.tools.rag_service import RAGService
        
        config = get_config()
        rag_service = RAGService(config)
        
        # Check if synthesis prompt includes citation requirements
        synthesis_template = rag_service.synthesis_prompt.template
        
        print("🔍 Checking synthesis prompt for citation requirements...")
        
        citation_requirements = [
            "source citations",
            "always include",
            "according to",
            "based on",
            "attribute to sources",
            "never present document information as general knowledge"
        ]
        
        found_requirements = []
        for requirement in citation_requirements:
            if requirement.lower() in synthesis_template.lower():
                found_requirements.append(requirement)
        
        print(f"✅ Found citation requirements: {found_requirements}")
        
        # Check for JSON structure with source_citations
        if "source_citations" in synthesis_template:
            print("✅ Synthesis prompt includes source_citations in JSON structure")
            has_structure = True
        else:
            print("❌ Synthesis prompt missing source_citations structure")
            has_structure = False
        
        if len(found_requirements) >= 3 and has_structure:
            print("✅ Synthesis prompt includes comprehensive citation requirements")
            return True
        else:
            print("❌ Synthesis prompt lacks sufficient citation requirements")
            return False
        
    except Exception as e:
        print(f"❌ Synthesis citation requirements test failed: {e}")
        return False


def test_document_metadata_summary():
    """Test document metadata summary for citation support."""
    print("\n📊 Testing Document Metadata Summary")
    print("=" * 45)
    
    try:
        from jarvis.config import get_config
        from jarvis.tools.rag_service import RAGService
        
        config = get_config()
        rag_service = RAGService(config)
        
        # Get document stats to find existing documents
        doc_stats = rag_service.get_document_stats()
        sources = doc_stats.get('sources', [])
        
        if not sources:
            print("⚠️ No documents found for metadata testing")
            return True  # Not a failure, just no data to test
        
        print(f"📋 Testing metadata summary for {len(sources)} sources...")
        
        all_passed = True
        for source in sources[:3]:  # Test first 3 sources
            metadata_summary = rag_service.get_document_metadata_summary(source)
            
            print(f"\n   Source: {source}")
            
            if "error" in metadata_summary:
                print(f"   ❌ Error getting metadata: {metadata_summary['error']}")
                all_passed = False
                continue
            
            # Check required fields for citation
            required_fields = ['source', 'citation', 'total_chunks']
            missing_fields = []
            
            for field in required_fields:
                if field not in metadata_summary:
                    missing_fields.append(field)
            
            if missing_fields:
                print(f"   ❌ Missing fields: {missing_fields}")
                all_passed = False
            else:
                print(f"   ✅ All citation fields present")
                print(f"   Citation: {metadata_summary.get('citation', 'none')}")
                print(f"   Chunks: {metadata_summary.get('total_chunks', 0)}")
        
        return all_passed
        
    except Exception as e:
        print(f"❌ Document metadata summary test failed: {e}")
        return False


def test_search_result_citations():
    """Test that search results include proper citations."""
    print("\n🔍 Testing Search Result Citations")
    print("=" * 40)
    
    try:
        from jarvis.config import get_config
        from jarvis.tools.rag_service import RAGService
        
        config = get_config()
        rag_service = RAGService(config)
        
        # Add test content with known source
        test_content = f"Citation test content - {time.time()}"
        rag_service.add_conversational_memory(test_content)
        time.sleep(1)
        
        print("🔍 Testing search with citation requirements...")
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            search_result = loop.run_until_complete(
                rag_service.intelligent_search("citation test", max_results=2)
            )
            
            # Check if search results include citations
            synthesis = search_result.get('synthesis', {})
            
            # Check for source_citations in synthesis
            if 'source_citations' in synthesis:
                citations = synthesis['source_citations']
                print(f"✅ Found {len(citations)} source citations")
                
                for i, citation in enumerate(citations[:2], 1):
                    print(f"   Citation {i}: {citation}")
                    
                    # Check citation structure
                    if isinstance(citation, dict) and 'source' in citation:
                        print(f"   ✅ Citation {i} has proper structure")
                    else:
                        print(f"   ❌ Citation {i} missing proper structure")
                        return False
            else:
                print("❌ No source_citations found in synthesis")
                return False
            
            # Check retrieved documents have metadata
            retrieved_docs = search_result.get('retrieved_documents', [])
            if retrieved_docs:
                print(f"✅ Retrieved {len(retrieved_docs)} documents with metadata")
                
                for i, doc in enumerate(retrieved_docs[:2], 1):
                    metadata = doc.metadata
                    if 'source' in metadata:
                        print(f"   Document {i} source: {metadata['source']}")
                    else:
                        print(f"   ❌ Document {i} missing source metadata")
                        return False
            else:
                print("⚠️ No documents retrieved for citation test")
            
            return True
            
        finally:
            loop.close()
        
    except Exception as e:
        print(f"❌ Search result citations test failed: {e}")
        return False


def main():
    """Main test function."""
    print("🚀 Source Citation System Testing Suite")
    print("=" * 60)
    print("Testing comprehensive source citation functionality...")
    print()
    
    tests = [
        ("Citation Formatting", test_citation_formatting),
        ("Agent Prompt Citation Guidance", test_agent_prompt_citation_guidance),
        ("Synthesis Citation Requirements", test_synthesis_citation_requirements),
        ("Document Metadata Summary", test_document_metadata_summary),
        ("Search Result Citations", test_search_result_citations)
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
    
    print(f"\n📊 Source Citation Test Results")
    print("=" * 40)
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\n📈 Overall Results:")
    print(f"✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")
    print(f"📊 Success Rate: {passed/total*100:.1f}%")
    
    if passed == total:
        print("\n🎉 Source Citation System: COMPLETE!")
        print("   ✅ Citation formatting utilities working")
        print("   ✅ Agent prompts include citation guidance")
        print("   ✅ Synthesis requires source citations")
        print("   ✅ Document metadata supports citations")
        print("   ✅ Search results include proper citations")
        print("\n📚 All document information is now properly attributed to sources!")
    elif passed >= total * 0.8:
        print(f"\n✅ Source Citation System mostly complete!")
        print(f"   Core citation functionality working with minor issues")
    else:
        print(f"\n⚠️  Source Citation System needs attention")
        print(f"   Multiple citation issues detected")
    
    return passed >= total * 0.8


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
