#!/usr/bin/env python3
"""
Test script to simulate real user conversations with Jarvis.
Tests conversation flow, memory tracking, and remember/recall functionality.
"""

import sys
import asyncio
import time
sys.path.append('jarvis')

from jarvis.core.integration.optimized_integration import get_optimized_integration

async def simulate_conversation():
    """Simulate a real conversation with Jarvis like a user would have."""
    
    print("🎯 SIMULATING REAL JARVIS CONVERSATION")
    print("=" * 60)
    print("Testing: General conversation + Memory tracking + Remember/Recall")
    print("=" * 60)
    
    # Initialize optimized system
    integration = get_optimized_integration()
    
    # Start conversation session (like wake word activation)
    integration.start_conversation_session()
    print("🎤 [WAKE WORD DETECTED] - Conversation session started")
    print()
    
    # Test 1: General conversation flow
    print("📝 TEST 1: GENERAL CONVERSATION FLOW")
    print("-" * 40)
    
    conversation_tests = [
        "Hello Jarvis, how are you today?",
        "What's your name?", 
        "Can you tell me what time it is?",
        "That's great, thank you for helping me",
        "What did I just ask you about?"  # Test conversation memory
    ]
    
    for i, user_input in enumerate(conversation_tests, 1):
        print(f"👤 User: {user_input}")
        
        start_time = time.time()
        response = await integration.process_command(user_input)
        response_time = (time.time() - start_time) * 1000
        
        print(f"🤖 Jarvis: {response}")
        print(f"⏱️  Response time: {response_time:.1f}ms")
        print()
        
        # Small delay to simulate natural conversation
        await asyncio.sleep(0.5)
    
    print("=" * 60)
    print("📝 TEST 2: MEMORY AND RECALL FUNCTIONALITY")
    print("-" * 40)
    
    # Test 2: Remember functionality
    memory_tests = [
        "Remember that my favorite color is blue",
        "Please remember that I work as a software engineer", 
        "Remember that I live in San Francisco",
        "Also remember that I have a dog named Max",
        "Remember that I like to drink coffee in the morning"
    ]
    
    print("🧠 STORING MEMORIES:")
    for i, memory_command in enumerate(memory_tests, 1):
        print(f"👤 User: {memory_command}")
        
        start_time = time.time()
        response = await integration.process_command(memory_command)
        response_time = (time.time() - start_time) * 1000
        
        print(f"🤖 Jarvis: {response}")
        print(f"⏱️  Response time: {response_time:.1f}ms")
        print()
        
        await asyncio.sleep(0.3)
    
    print("-" * 40)
    print("🔍 TESTING RECALL:")
    
    # Test 3: Recall functionality
    recall_tests = [
        "What's my favorite color?",
        "What do you remember about my job?",
        "Where do I live?",
        "Tell me about my pet",
        "What do I like to drink in the morning?",
        "What do you know about me?"  # General recall
    ]
    
    for i, recall_query in enumerate(recall_tests, 1):
        print(f"👤 User: {recall_query}")
        
        start_time = time.time()
        response = await integration.process_command(recall_query)
        response_time = (time.time() - start_time) * 1000
        
        print(f"🤖 Jarvis: {response}")
        print(f"⏱️  Response time: {response_time:.1f}ms")
        print()
        
        await asyncio.sleep(0.3)
    
    print("=" * 60)
    print("📝 TEST 3: CONVERSATION CONTINUITY")
    print("-" * 40)
    
    # Test 4: Conversation continuity and context
    continuity_tests = [
        "Let's talk about programming",
        "What programming languages do you recommend?",
        "Which one of those is best for beginners?",  # Should reference previous response
        "Can you give me an example?",  # Should understand context
        "Thanks, that was helpful. Going back to what we discussed earlier, what was my job again?"  # Long-term memory + context
    ]
    
    for i, context_query in enumerate(continuity_tests, 1):
        print(f"👤 User: {context_query}")
        
        start_time = time.time()
        response = await integration.process_command(context_query)
        response_time = (time.time() - start_time) * 1000
        
        print(f"🤖 Jarvis: {response}")
        print(f"⏱️  Response time: {response_time:.1f}ms")
        print()
        
        await asyncio.sleep(0.5)
    
    # End conversation session
    session_summary = integration.end_conversation_session()
    
    print("=" * 60)
    print("📊 CONVERSATION SESSION SUMMARY")
    print("-" * 40)
    print(f"Queries processed: {session_summary.get('queries_processed', 'N/A')}")
    print(f"Average response time: {session_summary.get('avg_response_time_ms', 'N/A')}ms")
    print(f"Cache hits: {session_summary.get('cache_hits', 'N/A')}")
    print(f"Memory operations: {session_summary.get('memory_operations', 'N/A')}")
    print("=" * 60)
    
    print("✅ CONVERSATION TEST COMPLETE!")
    print("🎯 This demonstrates how a real user would interact with Jarvis:")
    print("   • Natural conversation flow")
    print("   • Memory storage and recall")
    print("   • Context awareness")
    print("   • Fast response times")
    print("   • Session management")

if __name__ == "__main__":
    asyncio.run(simulate_conversation())
