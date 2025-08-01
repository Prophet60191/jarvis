#!/usr/bin/env python3
"""
Specific test of Jarvis memory functionality to see if remember/recall is working.
"""

import sys
import asyncio
import time
sys.path.append('jarvis')

async def test_memory_functionality():
    """Test memory functionality specifically."""
    
    print("🧠 TESTING JARVIS MEMORY FUNCTIONALITY")
    print("=" * 50)
    
    from jarvis.core.integration.optimized_integration import get_optimized_integration
    
    integration = get_optimized_integration()
    integration.start_conversation_session()
    
    # Test simple memory storage
    print("📝 STORING A SIMPLE FACT:")
    print("-" * 30)
    
    memory_prompt = "Remember that my name is John"
    print(f"👤 User: {memory_prompt}")
    
    response = await integration.process_command(memory_prompt)
    print(f"🤖 Jarvis: {response}")
    print()
    
    # Test simple memory recall
    print("🔍 RECALLING THE FACT:")
    print("-" * 30)
    
    recall_prompt = "What is my name?"
    print(f"👤 User: {recall_prompt}")
    
    response = await integration.process_command(recall_prompt)
    print(f"🤖 Jarvis: {response}")
    print()
    
    # Test if we can see what tools are being used
    print("🔧 CHECKING AVAILABLE MEMORY TOOLS:")
    print("-" * 30)
    
    # Let's check what tools are actually available
    try:
        from jarvis.tools import plugin_manager
        tools = plugin_manager.get_all_tools()
        memory_tools = [tool for tool in tools if 'remember' in tool.name.lower() or 'search' in tool.name.lower()]
        
        print(f"Found {len(memory_tools)} memory-related tools:")
        for tool in memory_tools:
            print(f"  • {tool.name}: {tool.description[:60]}...")
        print()
        
        # Test calling a memory tool directly
        if memory_tools:
            print("🧪 TESTING MEMORY TOOL DIRECTLY:")
            print("-" * 30)
            
            remember_tool = None
            for tool in memory_tools:
                if 'remember' in tool.name.lower() and 'fact' in tool.name.lower():
                    remember_tool = tool
                    break
            
            if remember_tool:
                print(f"Testing tool: {remember_tool.name}")
                try:
                    # Try to use the remember tool directly
                    result = remember_tool._run({"fact": "My favorite food is pizza"})
                    print(f"Direct tool result: {result}")
                except Exception as e:
                    print(f"Tool error: {e}")
            
            # Test search tool
            search_tool = None
            for tool in memory_tools:
                if 'search' in tool.name.lower():
                    search_tool = tool
                    break
            
            if search_tool:
                print(f"Testing search tool: {search_tool.name}")
                try:
                    result = search_tool._run({"query": "name"})
                    print(f"Search result: {result}")
                except Exception as e:
                    print(f"Search error: {e}")
        
    except Exception as e:
        print(f"Error checking tools: {e}")
    
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(test_memory_functionality())
