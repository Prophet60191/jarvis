#!/usr/bin/env python3
"""
Test basic conversation without memory tools to see if the integration works.
"""

import sys
import asyncio
import time
sys.path.append('jarvis')

async def test_basic_conversation():
    """Test basic conversation functionality."""
    
    print("💬 TESTING BASIC CONVERSATION")
    print("=" * 40)
    
    from jarvis.core.integration.optimized_integration import get_optimized_integration
    
    integration = get_optimized_integration()
    integration.start_conversation_session()
    
    # Test simple greetings and questions
    basic_tests = [
        "Hello",
        "How are you?",
        "What's your name?",
        "Thank you"
    ]
    
    for prompt in basic_tests:
        print(f"👤 User: {prompt}")
        
        start_time = time.time()
        response = await integration.process_command(prompt)
        response_time = (time.time() - start_time) * 1000
        
        print(f"🤖 Jarvis: {response}")
        print(f"⏱️  {response_time:.1f}ms")
        print()
        
        # Stop if response takes too long
        if response_time > 10000:  # 10 seconds
            print("⚠️  Response too slow, stopping test")
            break
    
    print("=" * 40)

if __name__ == "__main__":
    asyncio.run(test_basic_conversation())
