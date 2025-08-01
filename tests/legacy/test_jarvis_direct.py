#!/usr/bin/env python3
"""
Direct test of Jarvis optimized system - send prompts directly to test
conversation flow, memory tracking, and remember/recall functionality.
"""

import sys
import asyncio
import time
sys.path.append('jarvis')

async def test_jarvis_direct():
    """Test Jarvis by sending prompts directly to the optimized system."""
    
    print("🎯 TESTING JARVIS DIRECTLY - NO VOICE NEEDED")
    print("=" * 60)
    
    # Import and initialize the optimized system
    from jarvis.core.integration.optimized_integration import get_optimized_integration
    
    integration = get_optimized_integration()
    integration.start_conversation_session()
    
    print("✅ Optimized Jarvis system initialized")
    print("🚀 Starting direct conversation tests...")
    print()
    
    # Test 1: Basic conversation
    print("📝 TEST 1: BASIC CONVERSATION")
    print("-" * 40)
    
    basic_tests = [
        "Hello, how are you?",
        "What's your name?",
        "What time is it?",
        "Thank you for helping me"
    ]
    
    for prompt in basic_tests:
        print(f"👤 User: {prompt}")
        
        start_time = time.time()
        response = await integration.process_command(prompt)
        response_time = (time.time() - start_time) * 1000
        
        print(f"🤖 Jarvis: {response}")
        print(f"⏱️  {response_time:.1f}ms")
        print()
    
    # Test 2: Memory storage
    print("📝 TEST 2: MEMORY STORAGE")
    print("-" * 40)
    
    memory_tests = [
        "Remember that my favorite color is blue",
        "Please remember that I work as a software engineer",
        "Remember that I live in San Francisco", 
        "Also remember that I have a dog named Max"
    ]
    
    for prompt in memory_tests:
        print(f"👤 User: {prompt}")
        
        start_time = time.time()
        response = await integration.process_command(prompt)
        response_time = (time.time() - start_time) * 1000
        
        print(f"🤖 Jarvis: {response}")
        print(f"⏱️  {response_time:.1f}ms")
        print()
    
    # Test 3: Memory recall
    print("📝 TEST 3: MEMORY RECALL")
    print("-" * 40)
    
    recall_tests = [
        "What's my favorite color?",
        "What do you remember about my job?",
        "Where do I live?",
        "Tell me about my pet",
        "What do you know about me?"
    ]
    
    for prompt in recall_tests:
        print(f"👤 User: {prompt}")
        
        start_time = time.time()
        response = await integration.process_command(prompt)
        response_time = (time.time() - start_time) * 1000
        
        print(f"🤖 Jarvis: {response}")
        print(f"⏱️  {response_time:.1f}ms")
        print()
    
    # Test 4: Conversation tracking
    print("📝 TEST 4: CONVERSATION TRACKING")
    print("-" * 40)
    
    context_tests = [
        "Let's talk about Python programming",
        "What are the main benefits of Python?",
        "Which benefit did you mention first?",  # Should reference previous response
        "Going back to what we discussed earlier, what was my job again?"  # Should recall stored memory
    ]
    
    for prompt in context_tests:
        print(f"👤 User: {prompt}")
        
        start_time = time.time()
        response = await integration.process_command(prompt)
        response_time = (time.time() - start_time) * 1000
        
        print(f"🤖 Jarvis: {response}")
        print(f"⏱️  {response_time:.1f}ms")
        print()
    
    # Get session summary
    session_summary = integration.end_conversation_session()
    
    print("=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("-" * 40)
    print(f"✅ All tests completed successfully")
    print(f"📈 Session stats: {session_summary}")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_jarvis_direct())
