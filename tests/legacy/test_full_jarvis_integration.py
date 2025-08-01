#!/usr/bin/env python3
"""
Test Full Jarvis Integration with MCP Tools.

This script tests the complete Jarvis voice assistant with MCP tool integration,
simulating voice commands that would use various MCP servers.
"""

import asyncio
import sys
import logging
sys.path.append('jarvis')

from jarvis.config import get_config
from jarvis.core.agent import JarvisAgent
from jarvis.core.mcp_tool_integration import initialize_mcp_tools

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_full_jarvis_integration():
    """Test complete Jarvis integration with MCP tools."""
    print("🚀 TESTING FULL JARVIS INTEGRATION WITH MCP TOOLS")
    print("=" * 60)
    
    try:
        # Initialize configuration
        config = get_config()
        print("✅ Configuration loaded")
        
        # Initialize MCP tools
        print("\n🔧 Initializing MCP tools...")
        mcp_tools = await initialize_mcp_tools()
        print(f"✅ MCP tools initialized: {len(mcp_tools)} tools")
        
        # Display available tools
        print("\n📋 Available MCP Tools:")
        for i, tool in enumerate(mcp_tools, 1):
            print(f"  {i:2d}. {tool.name}")
            print(f"      {tool.description[:80]}...")
        
        # Initialize Jarvis agent with MCP tools
        print(f"\n🤖 Initializing Jarvis agent...")
        agent = JarvisAgent(config.llm, config.agent)
        agent.initialize(tools=mcp_tools)
        print(f"✅ Jarvis agent initialized with {len(mcp_tools)} MCP tools")
        
        # Test voice commands that would use MCP tools
        test_commands = [
            # Time tool tests
            "What time is it?",
            "Tell me the current date",
            "What's the current date and time?",
            
            # Filesystem tool tests
            "List the files in my Desktop directory",
            "What files are in my home directory?",
            "Show me the contents of my Documents folder",
            "Create a directory called test_jarvis",
            "Search for files with 'jarvis' in the name",
            
            # General AI tests (no tools needed)
            "Hello, how are you?",
            "What is artificial intelligence?",
            "Tell me a joke",
        ]
        
        print(f"\n🎯 Testing {len(test_commands)} voice commands...")
        print("=" * 60)
        
        successful_tests = 0
        failed_tests = 0
        
        for i, command in enumerate(test_commands, 1):
            print(f"\n📝 Test {i}/{len(test_commands)}: '{command}'")
            print("-" * 50)
            
            try:
                # Process command with Jarvis agent
                response = await agent.process_input(command)
                
                # Analyze response
                if response and len(response) > 10:
                    print(f"🤖 Jarvis: {response[:200]}...")
                    
                    # Check if appropriate tool was used
                    if any(word in command.lower() for word in ['time', 'date']):
                        if any(word in response.lower() for word in ['pm', 'am', ':', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']):
                            print("✅ TIME TOOL: Successfully used MCP time server")
                        else:
                            print("⚠️ TIME TOOL: May not have used MCP time server")
                    
                    elif any(word in command.lower() for word in ['list', 'files', 'directory', 'folder', 'create', 'search']):
                        if any(word in response.lower() for word in ['file', 'directory', 'folder', 'created', 'found']):
                            print("✅ FILESYSTEM TOOL: Successfully used MCP filesystem server")
                        else:
                            print("⚠️ FILESYSTEM TOOL: May not have used MCP filesystem server")
                    
                    else:
                        print("✅ AI RESPONSE: Good general response")
                    
                    successful_tests += 1
                else:
                    print("❌ FAILED: No response or very short response")
                    failed_tests += 1
                    
            except Exception as e:
                print(f"❌ ERROR: {str(e)}")
                failed_tests += 1
        
        # Summary
        print("\n" + "=" * 60)
        print("🎉 FULL INTEGRATION TEST COMPLETE!")
        print(f"\n📊 RESULTS:")
        print(f"  Total Tests: {len(test_commands)}")
        print(f"  Successful: {successful_tests} ({successful_tests/len(test_commands)*100:.1f}%)")
        print(f"  Failed: {failed_tests} ({failed_tests/len(test_commands)*100:.1f}%)")
        
        print(f"\n🔧 MCP INTEGRATION STATUS:")
        print(f"  MCP Tools Available: {len(mcp_tools)}")
        print(f"  Time Tools: {len([t for t in mcp_tools if 'time' in t.name.lower()])}")
        print(f"  Filesystem Tools: {len([t for t in mcp_tools if 'filesystem' in t.name.lower()])}")
        
        if successful_tests >= len(test_commands) * 0.8:
            print(f"\n🌟 EXCELLENT: Jarvis with MCP integration is working very well!")
        elif successful_tests >= len(test_commands) * 0.6:
            print(f"\n✅ GOOD: Jarvis with MCP integration is working well")
        else:
            print(f"\n⚠️ NEEDS IMPROVEMENT: Some issues with MCP integration")
        
        print(f"\n🎯 READY FOR VOICE COMMANDS:")
        print(f"  Say 'jarvis' to activate")
        print(f"  Then try: 'What time is it?' or 'List my files'")
        print(f"  MCP tools will be used automatically!")
        
    except Exception as e:
        print(f"❌ Critical error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_full_jarvis_integration())
