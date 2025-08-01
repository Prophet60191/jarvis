#!/usr/bin/env python3
"""
Quick test to verify MCP system functionality.
"""

import sys
import os
import json
from pathlib import Path

# Add the jarvis package to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_mcp_system():
    """Test MCP system step by step."""
    print("🧪 Quick MCP System Test")
    print("=" * 50)
    
    # Step 1: Check if .jarvis directory exists
    jarvis_dir = Path.home() / ".jarvis"
    print(f"1. 📁 Jarvis directory: {jarvis_dir}")
    print(f"   Exists: {jarvis_dir.exists()}")
    
    # Step 2: Check MCP config file
    mcp_config = jarvis_dir / "mcp_servers.json"
    print(f"2. 📄 MCP config: {mcp_config}")
    print(f"   Exists: {mcp_config.exists()}")
    
    if mcp_config.exists():
        try:
            with open(mcp_config, 'r') as f:
                config = json.load(f)
            print(f"   Servers configured: {len(config.get('servers', {}))}")
            for name, server in config.get('mcpServers', {}).items():
                print(f"     - {name}: {server.get('enabled', False)}")
        except Exception as e:
            print(f"   Error reading config: {e}")
    
    # Step 3: Test MCP system import and initialization
    print("\n3. 🔧 Testing MCP System")
    try:
        from jarvis.tools import start_mcp_system, get_mcp_tool_manager
        print("   ✅ MCP imports successful")
        
        # Start MCP system
        print("   🚀 Starting MCP system...")
        result = start_mcp_system()
        print(f"   Start result: {result}")
        
        # Get tool manager
        tool_manager = get_mcp_tool_manager()
        print(f"   Tool manager available: {tool_manager is not None}")
        
        if tool_manager:
            print(f"   MCP tool count: {tool_manager.get_tool_count()}")
            
            # Get LangChain tools
            langchain_tools = tool_manager.get_langchain_tools()
            print(f"   LangChain tools: {len(langchain_tools)}")
            
            if langchain_tools:
                print("   Available MCP tools:")
                for tool in langchain_tools:
                    print(f"     - {tool.name}")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    # Step 4: Test overall tool system
    print("\n4. 🛠️ Testing Overall Tool System")
    try:
        from jarvis.tools import get_langchain_tools
        all_tools = get_langchain_tools()
        print(f"   Total tools available: {len(all_tools)}")
        print("   All tools:")
        for i, tool in enumerate(all_tools, 1):
            print(f"     {i}. {tool.name}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_mcp_system()
