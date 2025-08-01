#!/usr/bin/env python3
import os
import sys
import uuid
import asyncio
from jarvis.core.orchestration.enhanced_orchestrator import EnhancedJarvisOrchestrator
from jarvis.core.orchestration.orchestrator import SystemOrchestrator
from jarvis.core.context.context_manager import ContextManager
from jarvis.core.context.context import Context

async def test_browser_hello():
    # Initialize orchestrator with context
    context_manager = ContextManager()
    base_orchestrator = SystemOrchestrator(context_manager)
    orchestrator = EnhancedJarvisOrchestrator(base_orchestrator)
    context = Context(session_id=str(uuid.uuid4()))

    # Send prompt to Jarvis
    prompt = "Jarvis can you make me a browser ui that says hello world"
    print("\n💬 Sending prompt to Jarvis:")
    print(prompt)
    
    # Let Jarvis handle everything
    result = await orchestrator.orchestrate_intelligent_workflow(prompt, context)
    print("\n🤖 Response from Jarvis:")
    print(result)

if __name__ == "__main__":
    asyncio.run(test_browser_hello())
