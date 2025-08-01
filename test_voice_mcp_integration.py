#!/usr/bin/env python3
"""
Test Voice Integration with MCP Tools.

This script simulates the exact voice command flow that Jarvis uses,
testing MCP tool integration in the voice assistant context.
"""

import asyncio
import sys
import logging
sys.path.append('jarvis')

from jarvis.config import get_config
from jarvis.core.agent import JarvisAgent
from jarvis.core.mcp_tool_integration import initialize_mcp_tools

# Set up logging
logging.basicConfig(level=logging.WARNING)  # Reduce noise
logger = logging.getLogger(__name__)


async def simulate_voice_command(agent, command):
    """Simulate a voice command exactly as Jarvis would process it."""
    try:
        print(f"🎤 Voice Command: '{command}'")
        
        # Process with shorter timeout for testing
        response = await asyncio.wait_for(
            agent.process_input(command),
            timeout=15.0  # 15 second timeout
        )
        
        if response and len(response.strip()) > 5:
            # Truncate long responses for readability
            display_response = response[:150] + "..." if len(response) > 150 else response
            print(f"🤖 Jarvis: {display_response}")
            return True, response
        else:
            print(f"❌ No meaningful response")
            return False, ""
            
    except asyncio.TimeoutError:
        print(f"⏰ Timeout - command took too long")
        return False, "timeout"
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False, str(e)


async def test_voice_mcp_integration():
    """Test voice integration with MCP tools."""
    print("🎤 TESTING VOICE INTEGRATION WITH MCP TOOLS")
    print("=" * 55)
    
    try:
        # Quick setup
        config = get_config()
        print("✅ Configuration loaded")
        
        # Initialize MCP tools
        print("🔧 Initializing MCP tools...")
        mcp_tools = await initialize_mcp_tools()
        print(f"✅ {len(mcp_tools)} MCP tools ready")
        
        # Initialize agent
        print("🤖 Initializing Jarvis agent...")
        agent = JarvisAgent(config.llm, config.agent)
        agent.initialize(tools=mcp_tools)
        print("✅ Agent ready with MCP tools")
        
        # Voice command tests (prioritized by importance)
        voice_tests = [
            # High priority - Time (most common voice command)
            ("What time is it?", "time"),
            ("Tell me the time", "time"),
            
            # High priority - Simple filesystem
            ("List my desktop files", "filesystem"),
            
            # Medium priority - General AI
            ("Hello Jarvis", "general"),
            ("How are you?", "general"),
            
            # Lower priority - Complex filesystem
            ("What files are in my Documents folder?", "filesystem"),
            ("Create a test directory", "filesystem"),
        ]
        
        print(f"\n🎯 Testing {len(voice_tests)} voice commands...")
        print("=" * 55)
        
        results = {"time": 0, "filesystem": 0, "general": 0, "total": 0}
        
        for i, (command, category) in enumerate(voice_tests, 1):
            print(f"\n📝 Test {i}/{len(voice_tests)} ({category.upper()})")
            print("-" * 40)
            
            success, response = await simulate_voice_command(agent, command)
            
            if success:
                results[category] += 1
                results["total"] += 1
                
                # Analyze response quality
                if category == "time":
                    if any(indicator in response.lower() for indicator in ['pm', 'am', ':', 'time is']):
                        print("✅ TIME TOOL: Working correctly")
                    else:
                        print("⚠️ TIME TOOL: Response may not be from time tool")
                
                elif category == "filesystem":
                    if any(indicator in response.lower() for indicator in ['file', 'directory', 'folder', '[dir]', '[file]']):
                        print("✅ FILESYSTEM TOOL: Working correctly")
                    else:
                        print("⚠️ FILESYSTEM TOOL: Response may not be from filesystem tool")
                
                else:  # general
                    print("✅ GENERAL AI: Working correctly")
            
            # Small delay between tests
            await asyncio.sleep(0.5)
        
        # Results summary
        total_tests = len(voice_tests)
        success_rate = (results["total"] / total_tests) * 100
        
        print("\n" + "=" * 55)
        print("🎉 VOICE INTEGRATION TEST COMPLETE!")
        print(f"\n📊 RESULTS:")
        print(f"  Overall Success: {results['total']}/{total_tests} ({success_rate:.1f}%)")
        print(f"  Time Commands: {results['time']}/2")
        print(f"  Filesystem Commands: {results['filesystem']}/3")
        print(f"  General AI Commands: {results['general']}/2")
        
        print(f"\n🔧 MCP STATUS:")
        print(f"  MCP Tools Available: {len(mcp_tools)}")
        print(f"  Time Tools: {len([t for t in mcp_tools if 'time' in t.name.lower()])}")
        print(f"  Filesystem Tools: {len([t for t in mcp_tools if 'filesystem' in t.name.lower()])}")
        
        # Assessment
        if success_rate >= 80:
            print(f"\n🌟 EXCELLENT: Voice + MCP integration working very well!")
            print(f"🎤 Ready for full voice assistant use!")
        elif success_rate >= 60:
            print(f"\n✅ GOOD: Voice + MCP integration working well")
            print(f"🎤 Ready for voice assistant use with minor issues")
        elif success_rate >= 40:
            print(f"\n⚠️ FAIR: Voice + MCP integration needs improvement")
            print(f"🔧 Some tools working, others need debugging")
        else:
            print(f"\n❌ POOR: Voice + MCP integration has major issues")
            print(f"🔧 Significant debugging needed")
        
        # Next steps
        print(f"\n🚀 NEXT STEPS:")
        if success_rate >= 60:
            print(f"  1. ✅ MCP integration is working well")
            print(f"  2. 🎤 Voice assistant is ready for use")
            print(f"  3. 🗣️ Say 'jarvis' then try these commands:")
            print(f"     • 'What time is it?'")
            print(f"     • 'List my files'")
            print(f"     • 'Hello, how are you?'")
        else:
            print(f"  1. 🔧 Debug failing MCP tools")
            print(f"  2. ⏰ Optimize tool execution timeouts")
            print(f"  3. 🧪 Run more targeted tests")
        
    except Exception as e:
        print(f"❌ Critical error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_voice_mcp_integration())
