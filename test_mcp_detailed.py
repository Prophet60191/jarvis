#!/usr/bin/env python3
"""
Detailed MCP system test with timing and logging.
"""

import sys
import os
import time
import asyncio
from pathlib import Path

# Add the jarvis package to the path
jarvis_dir = Path("/Users/josed/Desktop/Voice App/jarvis")
sys.path.insert(0, str(jarvis_dir))

def test_mcp_detailed():
    """Test MCP system with detailed timing and logging."""
    print("🧪 Detailed MCP System Test")
    print("=" * 60)
    
    print(f"📁 Current working directory: {os.getcwd()}")
    print(f"📁 Jarvis directory: {jarvis_dir}")
    
    try:
        # Import MCP system
        from jarvis.tools import start_mcp_system, get_mcp_tool_manager, get_langchain_tools
        print("✅ MCP imports successful")
        
        # Start MCP system
        print("🚀 Starting MCP system...")
        start_time = time.time()
        result = start_mcp_system()
        print(f"   Start result: {result} (took {time.time() - start_time:.2f}s)")
        
        # Get tool manager
        tool_manager = get_mcp_tool_manager()
        print(f"   Tool manager available: {tool_manager is not None}")
        
        if tool_manager:
            # Check initial tool count
            initial_count = tool_manager.get_tool_count()
            print(f"   Initial MCP tool count: {initial_count}")
            
            # Wait for connections with periodic checks
            print("⏳ Waiting for MCP connections...")
            for i in range(10):  # Wait up to 10 seconds
                time.sleep(1)
                current_count = tool_manager.get_tool_count()
                print(f"   After {i+1}s: {current_count} MCP tools")
                
                if current_count > 0:
                    print(f"🎉 MCP tools discovered after {i+1} seconds!")
                    break
            
            # Final check
            final_count = tool_manager.get_tool_count()
            print(f"   Final MCP tool count: {final_count}")
            
            if final_count > 0:
                # Get MCP tools
                mcp_tools = tool_manager.get_langchain_tools()
                print(f"📋 MCP Tools ({len(mcp_tools)}):")
                for tool in mcp_tools:
                    print(f"   - {tool.name}")
        
        # Get all tools
        all_tools = get_langchain_tools()
        print(f"\n🛠️ Total tools available: {len(all_tools)}")
        
        print("📋 All available tools:")
        for i, tool in enumerate(all_tools, 1):
            print(f"   {i}. {tool.name}")
            
        return len(all_tools)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 0

if __name__ == "__main__":
    # Change to jarvis directory (like startup script does)
    os.chdir(jarvis_dir)
    print(f"📁 Changed to: {os.getcwd()}")
    
    tool_count = test_mcp_detailed()
    print(f"\n🎯 Final Result: {tool_count} tools found")
    
    if tool_count >= 17:
        print("✅ MCP integration working correctly!")
    elif tool_count >= 8:
        print("⚠️ Only built-in tools found - MCP servers not connecting")
    else:
        print("❌ Major issue - very few tools found")
