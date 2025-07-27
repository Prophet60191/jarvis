#!/usr/bin/env python3
"""
Test MCP system from startup script directory.
"""

import sys
import os
from pathlib import Path

# Add the jarvis package to the path
jarvis_dir = Path("/Users/josed/Desktop/Voice App/jarvis")
sys.path.insert(0, str(jarvis_dir))

def test_mcp_from_startup_dir():
    """Test MCP system from startup script directory."""
    print("🧪 Testing MCP from Startup Script Directory")
    print("=" * 60)
    
    print(f"📁 Current working directory: {os.getcwd()}")
    print(f"📁 Jarvis directory: {jarvis_dir}")
    print(f"🐍 Python path: {sys.path[:3]}")
    
    try:
        # Test MCP system import
        from jarvis.tools import start_mcp_system, get_mcp_tool_manager, get_langchain_tools
        print("✅ MCP imports successful")
        
        # Start MCP system
        print("🚀 Starting MCP system...")
        result = start_mcp_system()
        print(f"   Start result: {result}")
        
        # Get tool manager
        tool_manager = get_mcp_tool_manager()
        print(f"   Tool manager available: {tool_manager is not None}")
        
        if tool_manager:
            print(f"   MCP tool count: {tool_manager.get_tool_count()}")
        
        # Get all tools
        all_tools = get_langchain_tools()
        print(f"🛠️ Total tools available: {len(all_tools)}")
        
        print("📋 Available tools:")
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
    
    tool_count = test_mcp_from_startup_dir()
    print(f"\n🎯 Result: {tool_count} tools found")
    
    if tool_count >= 17:
        print("✅ MCP integration working correctly!")
    elif tool_count >= 8:
        print("⚠️ Only built-in tools found - MCP not working")
    else:
        print("❌ Major issue - very few tools found")
