#!/usr/bin/env python3
"""
Quick test of conversation context with the fixed persistent agent.
"""

import sys
import asyncio
import time
sys.path.append('jarvis')

async def test_context_quick():
    """Quick test of conversation context."""
    
    print("🧠 QUICK CONVERSATION CONTEXT TEST")
    print("=" * 40)
    
    from jarvis.core.integration.optimized_integration import get_optimized_integration
    
    integration = get_optimized_integration()
    integration.start_conversation_session()
    
    print(f"✅ Persistent agent created: {integration.persistent_agent is not None}")
    print()
    
    # Simple context test
    context_test = [
        "Let's talk about Python programming",
        "What are the main benefits of Python?",
        "Which benefit did you mention first?",  # Should reference previous response
        "Can you give me an example of that first benefit?",  # Should understand context
    ]
    
    for i, prompt in enumerate(context_test, 1):
        print(f"👤 User: {prompt}")
        
        start_time = time.time()
        response = await integration.process_command(prompt)
        response_time = (time.time() - start_time) * 1000
        
        print(f"🤖 Jarvis: {response}")
        print(f"⏱️  {response_time:.1f}ms")
        print()
        
        if i == 2:  # After the "which benefit first" question
            if "don't have" in response.lower() or "don't recall" in response.lower():
                print("❌ CONTEXT FAILURE: Jarvis doesn't remember previous response")
            else:
                print("✅ CONTEXT SUCCESS: Jarvis referenced previous response")
            print()
    
    print("🎯 CONTEXT TEST COMPLETE!")
    print("=" * 40)

if __name__ == "__main__":
    asyncio.run(test_context_quick())
