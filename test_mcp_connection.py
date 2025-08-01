#!/usr/bin/env python3
"""
Test MCP connection directly to debug issues.
"""

import asyncio
import sys
sys.path.append('jarvis')

from jarvis.core.mcp_config_manager import get_mcp_config_manager
from jarvis.core.mcp_client import get_mcp_client

async def test_mcp_connection():
    """Test MCP connection directly."""
    print("🔧 Testing MCP Connection...")
    
    try:
        # Get MCP manager and client
        config_manager = get_mcp_config_manager()
        mcp_client = get_mcp_client()
        mcp_client.set_config_manager(config_manager)
        
        # Get servers
        servers = config_manager.get_all_servers()
        print(f"📊 Found {len(servers)} configured servers:")
        
        for server_id, config in servers.items():
            print(f"  • {config.name} ({server_id})")
            print(f"    Command: {config.command} {' '.join(config.args)}")
            print(f"    Enabled: {config.enabled}")
        
        # Try to connect
        print("\n🔌 Attempting to connect to servers...")
        connection_results = await mcp_client.connect_all_servers()
        
        print(f"📊 Connection Results:")
        for server_id, success in connection_results.items():
            status = "✅ Success" if success else "❌ Failed"
            print(f"  • {server_id}: {status}")
        
        # Get connection status
        status = mcp_client.get_connection_status()
        print(f"\n📊 Connection Status:")
        for server_id, info in status.items():
            print(f"  • {info['name']}: {'✅ Connected' if info['connected'] else '❌ Disconnected'}")
            print(f"    Tools: {info['tools_count']}")
        
        # Get all tools
        all_tools = mcp_client.get_all_tools()
        print(f"\n🔧 Available Tools: {len(all_tools)}")
        for tool in all_tools:
            print(f"  • {tool.get('name', 'Unknown')} - {tool.get('description', 'No description')}")
        
        # Test a tool call if available
        if all_tools:
            print(f"\n🧪 Testing tool call...")
            first_tool = all_tools[0]
            server_id = first_tool.get('_mcp_server')
            tool_name = first_tool.get('name')
            
            if server_id and tool_name:
                result = await mcp_client.call_tool(server_id, tool_name, {})
                print(f"🎯 Tool result: {result}")
        
        # Cleanup
        mcp_client.disconnect_all()
        print("\n✅ Test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during MCP test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_mcp_connection())
