#!/usr/bin/env python3
"""
Test Conflict Resolution System

Tests the system's ability to handle contradictory information
from different sources appropriately.
"""

import sys
import time
import tempfile
import asyncio
from pathlib import Path

# Add jarvis to path
sys.path.append(str(Path(__file__).parent / "jarvis"))


def test_agent_conflict_guidance():
    """Test that agent prompt includes conflict resolution guidance."""
    print("🔄 Testing Agent Conflict Resolution Guidance")
    print("=" * 55)
    
    try:
        from jarvis.config import get_config
        from jarvis.core.agent import Agent
        
        config = get_config()
        agent = Agent(config)
        
        # Check if system prompt includes conflict resolution guidance
        system_prompt = agent.system_prompt
        
        print("🔍 Checking agent system prompt for conflict resolution guidance...")
        
        conflict_keywords = [
            "conflicting information",
            "contradict",
            "acknowledge the conflict",
            "present all conflicting viewpoints",
            "conflicting views",
            "never choose one source over another"
        ]
        
        found_keywords = []
        for keyword in conflict_keywords:
            if keyword.lower() in system_prompt.lower():
                found_keywords.append(keyword)
        
        print(f"✅ Found conflict resolution keywords: {found_keywords}")
        
        # Check for specific conflict handling phrases
        conflict_phrases = [
            "source a] states",
            "while [source b",
            "there are conflicting views",
            "potential reasons for the conflict"
        ]
        
        found_phrases = []
        for phrase in conflict_phrases:
            if phrase.lower() in system_prompt.lower():
                found_phrases.append(phrase)
        
        print(f"✅ Found conflict handling phrases: {found_phrases}")
        
        if len(found_keywords) >= 3 and len(found_phrases) >= 2:
            print("✅ Agent system prompt includes comprehensive conflict resolution guidance")
            return True
        else:
            print("❌ Agent system prompt lacks sufficient conflict resolution guidance")
            return False
        
    except Exception as e:
        print(f"❌ Agent conflict guidance test failed: {e}")
        return False


def test_synthesis_conflict_handling():
    """Test that synthesis prompt handles conflicts properly."""
    print("\n⚖️ Testing Synthesis Conflict Handling")
    print("=" * 45)
    
    try:
        from jarvis.config import get_config
        from jarvis.tools.rag_service import RAGService
        
        config = get_config()
        rag_service = RAGService(config)
        
        # Check if synthesis prompt includes conflict handling
        synthesis_template = rag_service.synthesis_prompt.template
        
        print("🔍 Checking synthesis prompt for conflict handling...")
        
        conflict_requirements = [
            "identify and acknowledge any contradictions",
            "do not ignore them",
            "present all viewpoints",
            "address conflicts transparently",
            "source a] states",
            "while [source b",
            "potential reasons"
        ]
        
        found_requirements = []
        for requirement in conflict_requirements:
            if requirement.lower() in synthesis_template.lower():
                found_requirements.append(requirement)
        
        print(f"✅ Found conflict handling requirements: {found_requirements}")
        
        # Check for contradictions_found in JSON structure
        if "contradictions_found" in synthesis_template:
            print("✅ Synthesis prompt includes contradictions_found in JSON structure")
            has_structure = True
        else:
            print("❌ Synthesis prompt missing contradictions_found structure")
            has_structure = False
        
        if len(found_requirements) >= 4 and has_structure:
            print("✅ Synthesis prompt includes comprehensive conflict handling")
            return True
        else:
            print("❌ Synthesis prompt lacks sufficient conflict handling")
            return False
        
    except Exception as e:
        print(f"❌ Synthesis conflict handling test failed: {e}")
        return False


def test_conflicting_document_scenario():
    """Test handling of conflicting information from documents."""
    print("\n📚 Testing Conflicting Document Scenario")
    print("=" * 50)
    
    try:
        from jarvis.config import get_config
        from jarvis.tools.rag_service import RAGService
        
        config = get_config()
        rag_service = RAGService(config)
        
        # Create conflicting documents
        doc1_content = """
# Software Configuration Guide v1.0

## Database Settings
The recommended database timeout is 30 seconds for optimal performance.
This setting ensures reliable connections without excessive waiting.
"""
        
        doc2_content = """
# Software Configuration Guide v2.0

## Database Settings  
The recommended database timeout is 60 seconds for optimal performance.
Recent testing shows that 30 seconds is too short and causes connection issues.
"""
        
        # Save test documents
        import shutil
        documents_path = Path(config.rag.documents_path)
        documents_path.mkdir(parents=True, exist_ok=True)
        
        doc1_path = documents_path / "config_guide_v1.txt"
        doc2_path = documents_path / "config_guide_v2.txt"
        
        doc1_path.write_text(doc1_content)
        doc2_path.write_text(doc2_content)
        
        try:
            print("📄 Created conflicting test documents")
            
            # Ingest documents
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                ingestion_result = loop.run_until_complete(
                    rag_service.ingest_documents_from_folder()
                )
                
                print(f"✅ Ingestion status: {ingestion_result.get('status', 'unknown')}")
                
                if ingestion_result.get('processed', 0) > 0:
                    # Wait for processing
                    time.sleep(2)
                    
                    # Search for conflicting information
                    print("\n🔍 Searching for conflicting information...")
                    
                    search_result = loop.run_until_complete(
                        rag_service.intelligent_search("database timeout recommendation")
                    )
                    
                    synthesis = search_result.get('synthesis', {})
                    answer = synthesis.get('synthesized_answer', '')
                    contradictions = synthesis.get('contradictions_found', [])
                    
                    print(f"📝 Synthesized answer: {answer[:200]}{'...' if len(answer) > 200 else ''}")
                    print(f"⚖️ Contradictions found: {contradictions}")
                    
                    # Check if conflicts were identified
                    conflict_indicators = [
                        "conflict", "contradict", "different", "while", 
                        "however", "states", "indicates", "v1", "v2"
                    ]
                    
                    found_indicators = []
                    for indicator in conflict_indicators:
                        if indicator.lower() in answer.lower():
                            found_indicators.append(indicator)
                    
                    print(f"✅ Conflict indicators in answer: {found_indicators}")
                    
                    # Check if both sources are mentioned
                    sources_mentioned = []
                    if "v1" in answer.lower() or "config_guide_v1" in answer.lower():
                        sources_mentioned.append("v1")
                    if "v2" in answer.lower() or "config_guide_v2" in answer.lower():
                        sources_mentioned.append("v2")
                    
                    print(f"✅ Sources mentioned: {sources_mentioned}")
                    
                    # Evaluation criteria
                    has_conflict_awareness = len(found_indicators) >= 2
                    mentions_both_sources = len(sources_mentioned) >= 2
                    has_contradictions_structure = len(contradictions) > 0
                    
                    if has_conflict_awareness and (mentions_both_sources or has_contradictions_structure):
                        print("✅ Conflict resolution working properly")
                        return True
                    else:
                        print("❌ Conflict resolution not working properly")
                        print(f"   Conflict awareness: {has_conflict_awareness}")
                        print(f"   Both sources mentioned: {mentions_both_sources}")
                        print(f"   Contradictions structure: {has_contradictions_structure}")
                        return False
                else:
                    print("❌ No documents were processed")
                    return False
                    
            finally:
                loop.close()
                
        finally:
            # Cleanup
            if doc1_path.exists():
                doc1_path.unlink()
            if doc2_path.exists():
                doc2_path.unlink()
        
    except Exception as e:
        print(f"❌ Conflicting document scenario test failed: {e}")
        return False


def test_conflict_resolution_patterns():
    """Test specific conflict resolution patterns."""
    print("\n🎯 Testing Conflict Resolution Patterns")
    print("=" * 50)
    
    try:
        from jarvis.config import get_config
        from jarvis.tools.rag_service import RAGService
        
        config = get_config()
        rag_service = RAGService(config)
        
        # Add conflicting memories
        memory1 = "The project deadline is March 15th according to the initial planning document."
        memory2 = "The project deadline has been moved to March 30th as per the updated schedule."
        
        print("📝 Adding conflicting memories...")
        rag_service.add_conversational_memory(memory1)
        time.sleep(0.5)
        rag_service.add_conversational_memory(memory2)
        time.sleep(1)
        
        # Search for conflicting information
        print("\n🔍 Searching for deadline information...")
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            search_result = loop.run_until_complete(
                rag_service.intelligent_search("project deadline")
            )
            
            synthesis = search_result.get('synthesis', {})
            answer = synthesis.get('synthesized_answer', '')
            
            print(f"📝 Answer: {answer}")
            
            # Check for conflict resolution patterns
            resolution_patterns = [
                "march 15" in answer.lower() and "march 30" in answer.lower(),
                any(word in answer.lower() for word in ["conflict", "different", "updated", "changed"]),
                any(phrase in answer.lower() for phrase in ["according to", "as per", "while", "however"])
            ]
            
            patterns_found = sum(resolution_patterns)
            
            print(f"✅ Conflict resolution patterns found: {patterns_found}/3")
            
            if patterns_found >= 2:
                print("✅ Conflict resolution patterns working correctly")
                return True
            else:
                print("❌ Insufficient conflict resolution patterns")
                return False
                
        finally:
            loop.close()
        
    except Exception as e:
        print(f"❌ Conflict resolution patterns test failed: {e}")
        return False


def main():
    """Main test function."""
    print("🚀 Conflict Resolution System Testing Suite")
    print("=" * 60)
    print("Testing system's ability to handle contradictory information...")
    print()
    
    tests = [
        ("Agent Conflict Guidance", test_agent_conflict_guidance),
        ("Synthesis Conflict Handling", test_synthesis_conflict_handling),
        ("Conflicting Document Scenario", test_conflicting_document_scenario),
        ("Conflict Resolution Patterns", test_conflict_resolution_patterns)
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
    
    print(f"\n📊 Conflict Resolution Test Results")
    print("=" * 45)
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\n📈 Overall Results:")
    print(f"✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")
    print(f"📊 Success Rate: {passed/total*100:.1f}%")
    
    if passed == total:
        print("\n🎉 Conflict Resolution System: COMPLETE!")
        print("   ✅ Agent prompts include conflict guidance")
        print("   ✅ Synthesis handles contradictions properly")
        print("   ✅ Conflicting documents handled correctly")
        print("   ✅ Resolution patterns working effectively")
        print("\n⚖️ System now handles contradictory information transparently!")
    elif passed >= total * 0.75:
        print(f"\n✅ Conflict Resolution System mostly complete!")
        print(f"   Core conflict handling working with minor issues")
    else:
        print(f"\n⚠️  Conflict Resolution System needs attention")
        print(f"   Multiple conflict handling issues detected")
    
    return passed >= total * 0.75


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
