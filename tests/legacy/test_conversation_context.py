#!/usr/bin/env python3
"""
Test conversation context and flow - does Jarvis remember what we talked about
in the same conversation session?
"""

import sys
import asyncio
import time
sys.path.append('jarvis')

async def test_conversation_context():
    """Test if Jarvis maintains conversation context between prompts."""
    
    print("🧠 TESTING CONVERSATION CONTEXT & FLOW")
    print("=" * 50)
    print("Testing: Does Jarvis remember what we just talked about?")
    print("=" * 50)
    
    from jarvis.core.integration.optimized_integration import get_optimized_integration
    
    integration = get_optimized_integration()
    integration.start_conversation_session()
    
    print("✅ Starting conversation session...")
    print()
    
    # Test 1: Basic conversation flow
    print("📝 TEST 1: BASIC CONVERSATION FLOW")
    print("-" * 30)
    
    conversation_flow = [
        "Let's talk about programming languages",
        "What are the benefits of Python?",
        "Which benefit did you mention first?",  # Should reference previous response
        "Can you give me an example of that?",   # Should understand "that" refers to the first benefit
    ]
    
    for i, prompt in enumerate(conversation_flow, 1):
        print(f"👤 User: {prompt}")
        
        start_time = time.time()
        response = await integration.process_command(prompt)
        response_time = (time.time() - start_time) * 1000
        
        print(f"🤖 Jarvis: {response}")
        print(f"⏱️  {response_time:.1f}ms")
        print()
        
        await asyncio.sleep(0.5)
    
    print("=" * 50)
    print("📝 TEST 2: TOPIC SWITCHING & RECALL")
    print("-" * 30)
    
    topic_switching = [
        "Now let's switch topics. Tell me about machine learning",
        "What's the difference between supervised and unsupervised learning?",
        "Going back to our earlier conversation, what programming language were we discussing?",  # Should recall Python
        "And what was the first benefit of that language you mentioned?",  # Should recall first Python benefit
    ]
    
    for i, prompt in enumerate(topic_switching, 1):
        print(f"👤 User: {prompt}")
        
        start_time = time.time()
        response = await integration.process_command(prompt)
        response_time = (time.time() - start_time) * 1000
        
        print(f"🤖 Jarvis: {response}")
        print(f"⏱️  {response_time:.1f}ms")
        print()
        
        await asyncio.sleep(0.5)
    
    print("=" * 50)
    print("📝 TEST 3: PRONOUN RESOLUTION")
    print("-" * 30)
    
    pronoun_tests = [
        "I'm working on a web application",
        "It uses React for the frontend",
        "What are some good practices for it?",  # "it" should refer to React
        "How does that compare to Vue?",         # "that" should refer to React practices
    ]
    
    for i, prompt in enumerate(pronoun_tests, 1):
        print(f"👤 User: {prompt}")
        
        start_time = time.time()
        response = await integration.process_command(prompt)
        response_time = (time.time() - start_time) * 1000
        
        print(f"🤖 Jarvis: {response}")
        print(f"⏱️  {response_time:.1f}ms")
        print()
        
        await asyncio.sleep(0.5)
    
    # End session and get summary
    session_summary = integration.end_conversation_session()
    
    print("=" * 50)
    print("📊 CONVERSATION CONTEXT TEST RESULTS")
    print("-" * 30)
    print(f"✅ Total conversation turns: {len(conversation_flow) + len(topic_switching) + len(pronoun_tests)}")
    print(f"📈 Session summary: {session_summary}")
    print()
    
    print("🎯 WHAT TO LOOK FOR:")
    print("-" * 30)
    print("✅ Does Jarvis reference previous responses?")
    print("✅ Can it recall earlier topics when asked?")
    print("✅ Does it understand pronouns like 'it', 'that', 'which'?")
    print("✅ Does conversation flow naturally?")
    print()
    
    print("🧠 CONVERSATION CONTEXT TEST COMPLETE!")
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(test_conversation_context())
