#!/usr/bin/env python3
"""
Test script to verify English-only responses from the LLM.
"""

import sys
import asyncio
from pathlib import Path

# Add jarvis to path
sys.path.insert(0, str(Path(__file__).parent / "jarvis"))

def test_english_responses():
    """Test that LLM responds in English only."""
    print("🌍 Testing English-Only LLM Responses")
    print("=" * 60)
    
    try:
        from jarvis.core.agent import JarvisAgent
        from jarvis.config import get_config
        
        config = get_config()
        
        # Create agent
        agent = JarvisAgent(config.llm)
        agent.initialize()
        
        # Test questions that might trigger mixed language
        test_questions = [
            "Can you tell me about cars?",
            "What are the different types of vehicles?",
            "Tell me about transportation methods",
            "Explain how engines work",
            "What is artificial intelligence?"
        ]
        
        print("🧪 Testing questions that previously caused mixed language:")
        
        all_english = True
        
        for i, question in enumerate(test_questions, 1):
            print(f"\n{i}. Question: '{question}'")
            
            try:
                # Get response
                response = agent.process_input(question)
                
                # Check for Chinese characters
                chinese_chars = []
                for char in response:
                    if '\u4e00' <= char <= '\u9fff':  # Chinese character range
                        chinese_chars.append(char)
                
                if chinese_chars:
                    print(f"   ❌ MIXED LANGUAGE: Found Chinese characters: {''.join(set(chinese_chars))}")
                    print(f"   Response: {response[:100]}...")
                    all_english = False
                else:
                    print(f"   ✅ ENGLISH ONLY: {response[:80]}...")
                
            except Exception as e:
                print(f"   ❌ ERROR: {e}")
                all_english = False
        
        if all_english:
            print(f"\n🎉 SUCCESS: All responses are in English only!")
            return True
        else:
            print(f"\n❌ FAILED: Some responses contain mixed languages")
            return False
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_system_prompt():
    """Check that the system prompt includes English-only instruction."""
    print("\n📝 Checking System Prompt")
    print("=" * 60)
    
    try:
        from jarvis.core.agent import JarvisAgent
        from jarvis.config import get_config
        
        config = get_config()
        agent = JarvisAgent(config.llm)
        
        prompt = agent.system_prompt
        
        print("System prompt preview:")
        print(prompt[:300] + "..." if len(prompt) > 300 else prompt)
        
        # Check for English-only instruction
        english_keywords = ["english only", "always respond in english", "never mix languages"]
        
        found_instruction = False
        for keyword in english_keywords:
            if keyword.lower() in prompt.lower():
                print(f"✅ Found English-only instruction: '{keyword}'")
                found_instruction = True
                break
        
        if not found_instruction:
            print("❌ No English-only instruction found in system prompt")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ System prompt check failed: {e}")
        return False


def main():
    """Test English-only responses."""
    print("🌍 English-Only Response Test")
    print("=" * 60)
    print("Testing that Jarvis responds only in English")
    print("=" * 60)
    
    # Check system prompt first
    prompt_ok = check_system_prompt()
    
    if prompt_ok:
        # Test actual responses
        responses_ok = test_english_responses()
        
        if responses_ok:
            print(f"\n🎉 English-only fix successful!")
            print("   • System prompt updated with language instruction")
            print("   • All test responses are in English only")
            print("   • Mixed language issue resolved")
        else:
            print(f"\n⚠️  System prompt updated but responses still mixed")
            print("   • May need to restart Jarvis for changes to take effect")
            print("   • Or consider switching to English-only LLM model")
    else:
        print(f"\n❌ System prompt not properly updated")
        print("   • English-only instruction missing")
        print("   • Need to fix system prompt first")


if __name__ == "__main__":
    main()
