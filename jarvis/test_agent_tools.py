#!/usr/bin/env python3
"""
Test Agent Tool Integration

This script tests whether the LLM agent can properly access and use
the open_jarvis_ui tool when processing voice commands.
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_tool_availability():
    """Test if the open_jarvis_ui tool is available to the agent."""
    print("🔍 Testing tool availability...")
    
    try:
        from jarvis.tools import get_langchain_tools
        
        tools = get_langchain_tools()
        print(f"Found {len(tools)} total tools")
        
        # Look for the UI tool
        ui_tools = [tool for tool in tools if 'jarvis_ui' in tool.name.lower() or 'open' in tool.name.lower()]
        
        if ui_tools:
            print("✅ Found UI-related tools:")
            for tool in ui_tools:
                print(f"  📋 {tool.name}: {tool.description[:100]}...")
            return True
        else:
            print("❌ No UI-related tools found")
            return False
            
    except Exception as e:
        print(f"❌ Error checking tools: {e}")
        return False

def test_agent_initialization():
    """Test if the agent can be initialized with tools."""
    print("\n🔍 Testing agent initialization...")
    
    try:
        from jarvis.core.agent import JarvisAgent
        from jarvis.config import get_config
        from jarvis.tools import get_langchain_tools

        config = get_config()
        agent = JarvisAgent(config.llm)

        # Get tools
        tools = get_langchain_tools()

        # Initialize agent with tools
        agent.initialize(tools)
        
        if agent.is_initialized():
            print("✅ Agent initialized successfully")
            print(f"Agent has {len(agent.tools)} tools available")
            return agent
        else:
            print("❌ Agent failed to initialize")
            return None
            
    except Exception as e:
        print(f"❌ Error initializing agent: {e}")
        return None

def test_agent_response(agent, test_phrases):
    """Test agent responses to various phrases."""
    print("\n🧪 Testing agent responses...")
    
    for phrase in test_phrases:
        print(f"\n📝 Testing phrase: '{phrase}'")
        try:
            response = agent.process_input(phrase)
            print(f"🤖 Response: {response[:200]}{'...' if len(response) > 200 else ''}")
            
            # Check if response indicates tool usage
            if any(keyword in response.lower() for keyword in ['opening', 'jarvis', 'desktop', 'settings', 'ui']):
                print("✅ Response suggests tool was used")
            else:
                print("⚠️  Response doesn't clearly indicate tool usage")
                
        except Exception as e:
            print(f"❌ Error processing phrase: {e}")

def main():
    """Main test function."""
    print("🧪 Jarvis Agent Tool Integration Test")
    print("=" * 60)
    
    # Test 1: Tool availability
    tools_available = test_tool_availability()
    
    if not tools_available:
        print("\n❌ Tools not available - cannot proceed with agent tests")
        return 1
    
    # Test 2: Agent initialization
    agent = test_agent_initialization()
    
    if not agent:
        print("\n❌ Agent initialization failed - cannot test responses")
        return 1
    
    # Test 3: Agent responses to various phrases
    test_phrases = [
        "open settings",
        "show settings",
        "open jarvis settings",
        "open configuration",
        "I want to configure jarvis",
        "show me the settings",
        "open the config",
        "access jarvis preferences"
    ]
    
    test_agent_response(agent, test_phrases)
    
    print("\n📊 Test Summary:")
    print("✅ Tools are available to the agent")
    print("✅ Agent initializes successfully")
    print("⚠️  Check the responses above to see if the tool is being triggered")
    print("\nIf the tool isn't being triggered consistently, the LLM may need")
    print("more specific prompting or the tool description may need improvement.")
    
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n🛑 Test cancelled by user")
    except Exception as e:
        print(f"\n❌ Test script error: {e}")
        sys.exit(1)
