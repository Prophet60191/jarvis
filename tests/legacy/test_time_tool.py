#!/usr/bin/env python3
"""
Test the time tool to ensure it's working properly.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_time_tool():
    """Test the get_current_time tool directly."""
    
    print("🕐 TESTING JARVIS TIME TOOL")
    print("=" * 30)
    
    try:
        # Import the time tool
        from jarvis.jarvis.tools.plugins.device_time_tool import get_current_time
        
        print("✅ Successfully imported get_current_time tool")
        
        # Test the tool (LangChain tools need to be invoked properly)
        print("🔍 Testing get_current_time.invoke()...")
        result = get_current_time.invoke({})
        
        print(f"📅 Result: {result}")
        
        if "Error" in result:
            print("❌ Time tool returned an error")
            return False
        else:
            print("✅ Time tool working correctly")
            return True
            
    except ImportError as e:
        print(f"❌ Failed to import time tool: {e}")
        return False
    except Exception as e:
        print(f"❌ Error testing time tool: {e}")
        return False

def test_tool_in_agent_context():
    """Test how the tool works in the agent context."""
    
    print("\n🤖 TESTING TIME TOOL IN AGENT CONTEXT")
    print("=" * 40)
    
    try:
        # Import agent components
        from jarvis.jarvis.core.agent import JarvisAgent
        from jarvis.jarvis.config import JarvisConfig
        
        print("✅ Successfully imported agent components")
        
        # Create config and agent
        config = JarvisConfig()
        agent = JarvisAgent(config)
        
        print("✅ Created agent instance")
        
        # Test with a time query
        test_queries = [
            "What time is it?",
            "Tell me the current time",
            "What's the time right now?"
        ]
        
        for query in test_queries:
            print(f"\n🔍 Testing query: '{query}'")
            try:
                # Process the query (with timeout)
                import signal
                
                def timeout_handler(signum, frame):
                    raise TimeoutError("Agent processing timed out")
                
                signal.signal(signal.SIGALRM, timeout_handler)
                signal.alarm(15)  # 15 second timeout
                
                response = agent.process_input(query)
                
                signal.alarm(0)  # Cancel timeout
                
                if response and response.strip():
                    print(f"✅ Agent response: {response}")
                else:
                    print("❌ Agent returned empty response")
                    
            except TimeoutError:
                print("⏰ Agent processing timed out (15s)")
            except Exception as e:
                print(f"❌ Error processing query: {e}")
                
    except ImportError as e:
        print(f"❌ Failed to import agent: {e}")
    except Exception as e:
        print(f"❌ Error in agent test: {e}")

def main():
    """Run all time tool tests."""
    
    print("🧪 JARVIS TIME TOOL DIAGNOSTIC")
    print("=" * 50)
    
    # Test 1: Direct tool test
    tool_works = test_time_tool()
    
    # Test 2: Agent context test (only if direct tool works)
    if tool_works:
        test_tool_in_agent_context()
    else:
        print("\n⚠️  Skipping agent test due to tool failure")
    
    print("\n🎯 DIAGNOSTIC COMPLETE")
    
    if tool_works:
        print("✅ Time tool is working - issue may be in agent processing")
        print("💡 Suggestions:")
        print("   • Check LLM model performance")
        print("   • Verify tool is being called by agent")
        print("   • Check for timeout issues in conversation flow")
    else:
        print("❌ Time tool has issues - needs fixing")

if __name__ == "__main__":
    main()
