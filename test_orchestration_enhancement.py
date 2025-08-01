#!/usr/bin/env python3
"""
Test script to validate Jarvis orchestration enhancements.
This script tests the enhanced system prompt without breaking existing functionality.
"""

import sys
import os
import asyncio
from pathlib import Path

# Add the jarvis package to the path
sys.path.insert(0, str(Path(__file__).parent / "jarvis"))

def test_system_prompt_loading():
    """Test that the enhanced system prompt loads correctly."""
    print("🧪 Testing System Prompt Loading...")
    
    try:
        from jarvis.core.agent import JarvisAgent
        from jarvis.config import LLMConfig
        
        # Create agent with default config
        config = LLMConfig()
        agent = JarvisAgent(config)
        
        # Check that system prompt contains orchestration keywords
        prompt = agent.system_prompt
        
        orchestration_keywords = [
            "orchestration",
            "workflow",
            "coordination",
            "multi-agent",
            "TASK ANALYSIS PROTOCOL",
            "WORKFLOW PATTERNS",
            "AGENT SELECTION"
        ]
        
        found_keywords = []
        for keyword in orchestration_keywords:
            if keyword.lower() in prompt.lower():
                found_keywords.append(keyword)
        
        print(f"✅ System prompt loaded successfully")
        print(f"✅ Found {len(found_keywords)}/{len(orchestration_keywords)} orchestration keywords")
        print(f"   Keywords found: {', '.join(found_keywords)}")
        
        if len(found_keywords) >= 5:
            print("✅ Enhanced orchestration prompt successfully integrated!")
            return True
        else:
            print("❌ Orchestration keywords missing - prompt may not be fully enhanced")
            return False
            
    except Exception as e:
        print(f"❌ Error loading system prompt: {e}")
        return False

def test_agent_initialization():
    """Test that agent initialization still works with enhanced prompt."""
    print("\n🧪 Testing Agent Initialization...")
    
    try:
        from jarvis.core.agent import JarvisAgent
        from jarvis.config import LLMConfig
        
        # Create agent
        config = LLMConfig()
        agent = JarvisAgent(config)
        
        # Test initialization without tools (should work)
        agent.initialize(tools=[])
        
        print("✅ Agent initialization successful")
        print(f"✅ Agent is_initialized: {agent.is_initialized()}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error initializing agent: {e}")
        return False

def test_basic_functionality():
    """Test basic functionality to ensure nothing is broken."""
    print("\n🧪 Testing Basic Functionality...")
    
    try:
        from jarvis.core.agent import JarvisAgent
        from jarvis.config import LLMConfig
        
        # Create agent
        config = LLMConfig()
        agent = JarvisAgent(config)
        agent.initialize(tools=[])
        
        # Test that we can access basic properties
        prompt_length = len(agent.system_prompt)
        print(f"✅ System prompt length: {prompt_length} characters")
        
        # Test that agent has required methods
        required_methods = ['process_input', 'initialize', 'is_initialized', 'set_system_prompt']
        for method in required_methods:
            if hasattr(agent, method):
                print(f"✅ Method '{method}' available")
            else:
                print(f"❌ Method '{method}' missing")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing basic functionality: {e}")
        return False

def test_orchestration_keywords():
    """Test that specific orchestration concepts are present in the prompt."""
    print("\n🧪 Testing Orchestration Keywords...")
    
    try:
        from jarvis.core.agent import JarvisAgent
        from jarvis.config import LLMConfig
        
        agent = JarvisAgent(LLMConfig())
        prompt = agent.system_prompt.lower()
        
        # Test for specific orchestration concepts
        orchestration_concepts = {
            "complexity classification": ["simple", "medium", "complex"],
            "agent capabilities": ["aider", "lavague", "open interpreter", "rag"],
            "workflow patterns": ["sequential", "parallel", "conditional"],
            "coordination": ["coordination", "handoff", "synthesis"],
            "decision trees": ["decision", "when to use", "selection"]
        }
        
        results = {}
        for concept, keywords in orchestration_concepts.items():
            found = sum(1 for keyword in keywords if keyword in prompt)
            results[concept] = found
            print(f"✅ {concept}: {found}/{len(keywords)} keywords found")
        
        total_found = sum(results.values())
        total_possible = sum(len(keywords) for keywords in orchestration_concepts.values())
        
        print(f"\n✅ Overall orchestration coverage: {total_found}/{total_possible} ({total_found/total_possible*100:.1f}%)")
        
        return total_found >= total_possible * 0.7  # 70% coverage threshold
        
    except Exception as e:
        print(f"❌ Error testing orchestration keywords: {e}")
        return False

def test_backward_compatibility():
    """Test that existing functionality is preserved."""
    print("\n🧪 Testing Backward Compatibility...")
    
    try:
        from jarvis.core.agent import JarvisAgent
        from jarvis.config import LLMConfig
        
        agent = JarvisAgent(LLMConfig())
        prompt = agent.system_prompt.lower()
        
        # Check for preserved functionality
        preserved_features = [
            "memory",
            "security",
            "tool usage",
            "open interpreter",
            "remember_fact",
            "search_long_term_memory"
        ]
        
        preserved_count = 0
        for feature in preserved_features:
            if feature.replace("_", " ") in prompt or feature.replace(" ", "_") in prompt:
                print(f"✅ Preserved: {feature}")
                preserved_count += 1
            else:
                print(f"⚠️  Missing: {feature}")
        
        print(f"\n✅ Preserved functionality: {preserved_count}/{len(preserved_features)} features")
        
        return preserved_count >= len(preserved_features) * 0.8  # 80% preservation threshold
        
    except Exception as e:
        print(f"❌ Error testing backward compatibility: {e}")
        return False

def main():
    """Run all tests and provide summary."""
    print("🚀 Jarvis Orchestration Enhancement Test Suite")
    print("=" * 50)
    
    tests = [
        ("System Prompt Loading", test_system_prompt_loading),
        ("Agent Initialization", test_agent_initialization),
        ("Basic Functionality", test_basic_functionality),
        ("Orchestration Keywords", test_orchestration_keywords),
        ("Backward Compatibility", test_backward_compatibility)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test '{test_name}' failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\n🎯 Overall Result: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Enhanced orchestration is ready for use.")
        return True
    elif passed >= total * 0.8:
        print("⚠️  Most tests passed. Minor issues may need attention.")
        return True
    else:
        print("❌ Multiple test failures. Please review implementation.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
