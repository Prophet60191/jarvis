#!/usr/bin/env python3
"""
Test Jarvis Memory Update

This script tests if Jarvis's memory was properly updated with the recent changes.
"""

import sys
from pathlib import Path

# Add jarvis to path
sys.path.insert(0, str(Path(__file__).parent / "jarvis"))

def test_jarvis_memory():
    """Test Jarvis's memory for recent updates."""
    
    print("🧠 TESTING JARVIS MEMORY UPDATE")
    print("=" * 50)
    print("Checking if Jarvis knows about recent changes...")
    print()
    
    try:
        from jarvis.tools.plugins.rag_plugin import search_long_term_memory
        
        # Test queries about recent changes
        test_queries = [
            "wake word detection fix July 2025",
            "start_jarvis_fixed.py startup method",
            "smart routing implementation",
            "simplified architecture",
            "performance improvements 46 seconds",
            "MacBook Pro Microphone index 2",
            "Coqui TTS vctk_p374 voice",
            "async threading issues resolved"
        ]
        
        successful_queries = 0
        
        for i, query in enumerate(test_queries, 1):
            print(f"{i}. 🔍 Testing: '{query}'")
            
            try:
                result = search_long_term_memory.invoke({"query": query})
                
                if result and len(result.strip()) > 50:
                    print(f"   ✅ FOUND: {len(result)} characters")
                    # Show relevant snippet
                    snippet = result[:150].replace('\n', ' ')
                    print(f"   📄 Preview: {snippet}...")
                    successful_queries += 1
                else:
                    print(f"   ❌ NOT FOUND or insufficient information")
                    
            except Exception as e:
                print(f"   ❌ ERROR: {e}")
            
            print()
        
        # Summary
        success_rate = (successful_queries / len(test_queries)) * 100
        
        print("📊 MEMORY TEST RESULTS")
        print("=" * 30)
        print(f"Successful queries: {successful_queries}/{len(test_queries)}")
        print(f"Success rate: {success_rate:.1f}%")
        
        if success_rate >= 75:
            print("🎉 EXCELLENT: Jarvis has good knowledge of recent changes!")
        elif success_rate >= 50:
            print("✅ GOOD: Jarvis has some knowledge of recent changes")
        else:
            print("⚠️ POOR: Jarvis may not have sufficient knowledge of recent changes")
        
        return success_rate >= 50
        
    except Exception as e:
        print(f"❌ Error testing Jarvis memory: {e}")
        return False


def test_specific_knowledge():
    """Test specific knowledge about the fixes."""
    
    print("\n🎯 TESTING SPECIFIC KNOWLEDGE")
    print("=" * 40)
    
    try:
        from jarvis.tools.plugins.rag_plugin import search_long_term_memory
        
        # Test specific knowledge
        specific_tests = [
            {
                "query": "How do I start Jarvis with working wake word detection?",
                "expected_keywords": ["start_jarvis_fixed.py", "python", "simplified"]
            },
            {
                "query": "What was the wake word detection problem?",
                "expected_keywords": ["async", "threading", "complex", "architecture"]
            },
            {
                "query": "What are the performance improvements?",
                "expected_keywords": ["46 seconds", "instant", "smart routing", "time queries"]
            },
            {
                "query": "What microphone settings work?",
                "expected_keywords": ["MacBook Pro", "index 2", "energy threshold", "100"]
            }
        ]
        
        passed_tests = 0
        
        for i, test in enumerate(specific_tests, 1):
            print(f"{i}. 🧪 Testing: '{test['query']}'")
            
            try:
                result = search_long_term_memory.invoke({"query": test["query"]})
                
                if result:
                    result_lower = result.lower()
                    found_keywords = []
                    
                    for keyword in test["expected_keywords"]:
                        if keyword.lower() in result_lower:
                            found_keywords.append(keyword)
                    
                    if found_keywords:
                        print(f"   ✅ PASS: Found keywords: {', '.join(found_keywords)}")
                        passed_tests += 1
                    else:
                        print(f"   ❌ FAIL: No expected keywords found")
                        print(f"   Expected: {', '.join(test['expected_keywords'])}")
                else:
                    print(f"   ❌ FAIL: No information found")
                    
            except Exception as e:
                print(f"   ❌ ERROR: {e}")
            
            print()
        
        # Summary
        pass_rate = (passed_tests / len(specific_tests)) * 100
        
        print("📊 SPECIFIC KNOWLEDGE TEST RESULTS")
        print("=" * 40)
        print(f"Passed tests: {passed_tests}/{len(specific_tests)}")
        print(f"Pass rate: {pass_rate:.1f}%")
        
        if pass_rate >= 75:
            print("🎉 EXCELLENT: Jarvis has detailed knowledge of the fixes!")
        elif pass_rate >= 50:
            print("✅ GOOD: Jarvis has reasonable knowledge of the fixes")
        else:
            print("⚠️ POOR: Jarvis lacks detailed knowledge of the fixes")
        
        return pass_rate >= 50
        
    except Exception as e:
        print(f"❌ Error testing specific knowledge: {e}")
        return False


def main():
    """Main function to test Jarvis's memory."""
    
    print("🧠 JARVIS MEMORY VERIFICATION TEST")
    print("=" * 60)
    print("Testing if Jarvis properly learned about recent changes")
    print()
    
    # Test 1: General memory
    general_ok = test_jarvis_memory()
    
    # Test 2: Specific knowledge
    specific_ok = test_specific_knowledge()
    
    # Final assessment
    print("\n🎯 FINAL ASSESSMENT")
    print("=" * 30)
    
    if general_ok and specific_ok:
        print("🎉 SUCCESS: Jarvis's memory was properly updated!")
        print("✅ Jarvis knows about wake word detection fixes")
        print("✅ Jarvis knows about smart routing implementation")
        print("✅ Jarvis knows about performance improvements")
        print("✅ Jarvis knows about the new startup method")
        print()
        print("🚀 Jarvis is now self-aware of recent improvements!")
        
    elif general_ok or specific_ok:
        print("⚠️ PARTIAL SUCCESS: Jarvis has some knowledge but may need more updates")
        
    else:
        print("❌ FAILURE: Jarvis's memory was not properly updated")
        print("💡 Consider running the memory update script again")


if __name__ == "__main__":
    main()
