#!/usr/bin/env python3
"""
Test the agent's ability to use tools directly
"""

import sys
from pathlib import Path

# Add jarvis to path
sys.path.insert(0, str(Path(__file__).parent / "jarvis"))

def test_agent_with_tools():
    """Test the agent's tool usage directly."""
    print("🤖 TESTING AGENT TOOL USAGE")
    print("=" * 50)
    
    try:
        from jarvis.config import get_config
        from jarvis.core.agent import JarvisAgent
        from jarvis.tools import get_langchain_tools
        
        # Load config
        config = get_config()
        print(f"✅ Config loaded")
        
        # Initialize agent
        agent = JarvisAgent(config.llm)
        tools = get_langchain_tools()
        agent.initialize(tools=tools)
        
        print(f"✅ Agent initialized with {len(tools)} tools")
        
        # List available tools
        available_tools = agent.get_available_tools()
        print(f"🛠️  Available tools: {len(available_tools)}")
        
        # Find time tool
        time_tools = [name for name in available_tools if 'time' in name.lower()]
        print(f"⏰ Time tools: {time_tools}")
        
        # Test direct query
        print(f"\n🧪 Testing time query...")
        try:
            response = agent.process_input("What time is it?")
            print(f"✅ Agent response: {response}")
            
            # Check if it used tools
            if "get_current_time" in response or "time" in response.lower():
                print("✅ Agent appears to have used time functionality")
            else:
                print("❌ Agent did not use time tool")
                
        except Exception as e:
            print(f"❌ Agent query failed: {e}")
            import traceback
            traceback.print_exc()
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing agent: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_tool_directly():
    """Test calling the time tool directly."""
    print(f"\n🔧 TESTING DIRECT TOOL CALL")
    print("=" * 40)
    
    try:
        from jarvis.tools import get_langchain_tools
        
        tools = get_langchain_tools()
        time_tool = None
        
        for tool in tools:
            if hasattr(tool, 'name') and 'time' in tool.name.lower():
                time_tool = tool
                break
        
        if time_tool:
            print(f"✅ Found time tool: {time_tool.name}")
            result = time_tool.invoke({})
            print(f"✅ Direct tool result: {result}")
            return True
        else:
            print("❌ Time tool not found")
            return False
            
    except Exception as e:
        print(f"❌ Direct tool test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function."""
    print("🎯 JARVIS AGENT TOOL USAGE TEST")
    print("=" * 60)
    
    # Test agent with tools
    agent_works = test_agent_with_tools()
    
    # Test direct tool call
    direct_works = test_tool_directly()
    
    print("\n📋 SUMMARY")
    print("=" * 30)
    print(f"Agent tool usage: {'✅ Working' if agent_works else '❌ Failed'}")
    print(f"Direct tool call: {'✅ Working' if direct_works else '❌ Failed'}")

if __name__ == "__main__":
    main()
