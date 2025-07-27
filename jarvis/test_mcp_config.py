#!/usr/bin/env python3
"""
Test MCP configuration and connection.
"""

import os
import json
from pathlib import Path

def test_mcp_config():
    """Test MCP configuration."""
    print("🧪 Testing MCP Configuration")
    print("=" * 50)
    
    # Check if .jarvis directory exists
    jarvis_dir = Path.home() / ".jarvis"
    print(f"📁 Jarvis directory: {jarvis_dir}")
    print(f"   Exists: {jarvis_dir.exists()}")
    
    if jarvis_dir.exists():
        print(f"   Contents: {list(jarvis_dir.iterdir())}")
    
    # Check MCP config file
    mcp_config_file = jarvis_dir / "mcp_servers.json"
    print(f"📄 MCP config file: {mcp_config_file}")
    print(f"   Exists: {mcp_config_file.exists()}")
    
    if mcp_config_file.exists():
        try:
            with open(mcp_config_file, 'r') as f:
                config = json.load(f)
            print(f"   Content: {json.dumps(config, indent=2)}")
        except Exception as e:
            print(f"   Error reading: {e}")
    
    # Test MCP system import
    print("\n🔧 Testing MCP System Import")
    try:
        from jarvis.tools import start_mcp_system, get_mcp_tool_manager
        print("✅ MCP system imports successful")
        
        # Test MCP system start
        print("\n🚀 Testing MCP System Start")
        result = start_mcp_system()
        print(f"   Start result: {result}")
        
        # Test tool manager
        print("\n🛠️ Testing MCP Tool Manager")
        tool_manager = get_mcp_tool_manager()
        print(f"   Tool manager: {tool_manager}")
        
        if tool_manager:
            print(f"   Tool count: {tool_manager.get_tool_count()}")
            tools = tool_manager.get_langchain_tools()
            print(f"   Available tools: {[tool.name for tool in tools]}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_mcp_config()
