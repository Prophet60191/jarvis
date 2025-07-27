#!/usr/bin/env python3
"""
Test if the LLM can see and use tools.
"""

import sys
import os
from pathlib import Path

# Add the jarvis package to the path
jarvis_dir = Path("/Users/josed/Desktop/Voice App/jarvis")
sys.path.insert(0, str(jarvis_dir))

def test_llm_tools():
    """Test if the LLM can see and use tools."""
    print("🧪 Testing LLM Tool Recognition")
    print("=" * 50)
    
    try:
        # Import Jarvis components
        from jarvis.tools import get_langchain_tools
        from jarvis.config import JarvisConfig
        from jarvis.core.agent import JarvisAgent
        
        print("✅ Imports successful")
        
        # Get all available tools
        all_tools = get_langchain_tools()
        print(f"🛠️ Total tools available: {len(all_tools)}")
        
        print("📋 Available tools:")
        for i, tool in enumerate(all_tools, 1):
            print(f"   {i}. {tool.name} - {tool.description}")
        
        # Create agent with tools
        config = JarvisConfig()
        agent = JarvisAgent(config.llm)
        
        print(f"\n🤖 Initializing agent with {len(all_tools)} tools...")
        agent.initialize(tools=all_tools)
        
        if agent.is_initialized():
            print("✅ Agent initialized successfully")
            
            # Check agent's tool count
            agent_tools = agent.get_available_tools()
            print(f"🔍 Agent reports {len(agent_tools)} tools:")
            for tool_name in agent_tools:
                print(f"   - {tool_name}")
            
            # Test a simple tool query
            print("\n🧪 Testing tool recognition...")
            try:
                # Test with a simple question about tools
                response = agent.process_input("List all the tools you have access to")
                print(f"📝 Agent response: {response}")
                
                # Check if response mentions tools
                if "tool" in response.lower() or any(tool_name.lower() in response.lower() for tool_name in agent_tools):
                    print("✅ Agent recognizes tools!")
                    return True
                else:
                    print("❌ Agent doesn't seem to recognize tools")
                    return False
                    
            except Exception as e:
                print(f"❌ Error testing agent: {e}")
                return False
        else:
            print("❌ Agent failed to initialize")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_llm_tools()
    print(f"\n🎯 LLM Tool Test: {'✅ PASS' if success else '❌ FAIL'}")
