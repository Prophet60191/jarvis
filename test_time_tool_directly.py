#!/usr/bin/env python3
"""
Test Time Tool Directly

Test if the time tool works properly when called directly.
"""

import sys
from pathlib import Path

# Add jarvis to path
sys.path.insert(0, str(Path(__file__).parent / "jarvis"))

def test_time_tool():
    """Test the time tool directly."""
    print("🕐 TESTING TIME TOOL DIRECTLY")
    print("=" * 40)
    
    try:
        from jarvis.tools.time_tool import get_current_time
        
        print("⏰ Calling get_current_time()...")
        result = get_current_time()
        print(f"✅ Time tool result: {result}")
        
        return result
        
    except Exception as e:
        print(f"❌ Time tool failed: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_tools_list():
    """Check what tools are available."""
    print("\n🔧 CHECKING AVAILABLE TOOLS")
    print("=" * 40)
    
    try:
        from jarvis.tools import get_langchain_tools
        
        tools = get_langchain_tools()
        print(f"✅ Found {len(tools)} tools:")
        
        for i, tool in enumerate(tools):
            tool_name = getattr(tool, 'name', 'Unknown')
            tool_desc = getattr(tool, 'description', 'No description')
            print(f"  {i+1:2d}. {tool_name}: {tool_desc[:60]}...")
            
            # Look for time-related tools
            if 'time' in tool_name.lower() or 'time' in tool_desc.lower():
                print(f"      ⏰ TIME TOOL FOUND!")
        
        return tools
        
    except Exception as e:
        print(f"❌ Tools list failed: {e}")
        import traceback
        traceback.print_exc()
        return []


def test_simple_agent_without_rag():
    """Test agent with a simple query that should use time tool."""
    print("\n🧠 TESTING AGENT WITH TIME QUERY")
    print("=" * 40)
    
    try:
        from jarvis.config import get_config
        from jarvis.core.agent import JarvisAgent
        from jarvis.tools import get_langchain_tools
        import asyncio
        
        config = get_config()
        
        # Initialize agent
        print("🧠 Initializing agent...")
        agent = JarvisAgent(config.llm, config.agent)
        tools = get_langchain_tools()
        agent.initialize(tools=tools)
        print(f"✅ Agent initialized with {len(tools)} tools")
        
        # Test with a very clear time query
        queries = [
            "What time is it right now?",
            "Tell me the current time",
            "What's the time?",
            "Current time please"
        ]
        
        for query in queries:
            print(f"\n🧪 Testing: '{query}'")
            try:
                start_time = time.time()
                response = asyncio.run(agent.process_input(query))
                end_time = time.time()
                duration = end_time - start_time
                
                print(f"✅ Response in {duration:.2f}s: {response}")
                
                # Check if it's a reasonable time response
                if any(word in response.lower() for word in ['time', 'clock', ':', 'am', 'pm', 'hour', 'minute']):
                    print("🎉 GOOD RESPONSE - Contains time information!")
                    return response
                else:
                    print("❌ BAD RESPONSE - Doesn't seem to be about time")
                    
            except Exception as e:
                print(f"❌ Query failed: {e}")
        
        return None
        
    except Exception as e:
        print(f"❌ Agent test failed: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """Run time tool diagnostics."""
    print("🕐 TIME TOOL DIAGNOSTIC")
    print("=" * 50)
    print("Testing why 'What time is it?' isn't working properly...")
    print()
    
    # Test 1: Time tool directly
    time_result = test_time_tool()
    
    # Test 2: Check available tools
    tools = test_tools_list()
    
    # Test 3: Agent with time query
    agent_result = test_simple_agent_without_rag()
    
    # Summary
    print("\n📊 TIME TOOL DIAGNOSTIC SUMMARY")
    print("=" * 40)
    print(f"Direct Time Tool: {'✅ WORKS' if time_result else '❌ FAILS'}")
    print(f"Tools Available: {'✅ FOUND' if tools else '❌ MISSING'}")
    print(f"Agent Time Query: {'✅ WORKS' if agent_result else '❌ FAILS'}")
    
    if time_result and tools and agent_result:
        print("\n🎉 TIME FUNCTIONALITY WORKING!")
        print("The issue might be with tool selection or RAG interference.")
    else:
        print("\n❌ TIME FUNCTIONALITY ISSUES:")
        if not time_result:
            print("  • Time tool not working directly")
        if not tools:
            print("  • Tools not loading properly")
        if not agent_result:
            print("  • Agent not using time tool correctly")


if __name__ == "__main__":
    import time
    main()
