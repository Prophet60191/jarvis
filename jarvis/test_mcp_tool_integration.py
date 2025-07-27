#!/usr/bin/env python3
"""
Test script for MCP tool integration with Jarvis.

This script tests the integration between MCP tools and the Jarvis tool system.
"""

import logging
import sys
from pathlib import Path

# Add the jarvis module to the path
sys.path.insert(0, str(Path(__file__).parent))

from jarvis.tools import get_langchain_tools, start_mcp_system, stop_mcp_system, get_mcp_client
from jarvis.core.mcp_client import MCPServerConfig, MCPTransportType

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_mcp_tool_integration():
    """Test MCP tool integration with Jarvis tool system."""
    logger.info("Testing MCP tool integration...")
    
    try:
        # Start MCP system
        logger.info("Starting MCP system...")
        success = start_mcp_system()
        assert success, "Failed to start MCP system"
        logger.info("✓ MCP system started successfully")
        
        # Get initial tool count
        initial_tools = get_langchain_tools()
        initial_count = len(initial_tools)
        logger.info(f"✓ Initial tool count: {initial_count}")
        
        # Add a test MCP server (this won't actually connect, but will test the integration)
        mcp_client = get_mcp_client()
        test_config = MCPServerConfig(
            name="test-integration-server",
            transport=MCPTransportType.STDIO,
            command="echo",
            args=["test"],
            enabled=False  # Don't auto-connect
        )
        
        success = mcp_client.add_server(test_config)
        assert success, "Failed to add test server"
        logger.info("✓ Test server added successfully")
        
        # Verify server was added
        server_info = mcp_client.get_server_info("test-integration-server")
        assert server_info is not None, "Server info not found"
        assert server_info.name == "test-integration-server", "Server name mismatch"
        logger.info("✓ Server info retrieved correctly")
        
        # Get updated tool count (should be same since server is not connected)
        updated_tools = get_langchain_tools()
        updated_count = len(updated_tools)
        logger.info(f"✓ Updated tool count: {updated_count}")
        
        # Clean up - remove test server
        success = mcp_client.remove_server("test-integration-server")
        assert success, "Failed to remove test server"
        logger.info("✓ Test server removed successfully")
        
        # Stop MCP system
        logger.info("Stopping MCP system...")
        success = stop_mcp_system()
        assert success, "Failed to stop MCP system"
        logger.info("✓ MCP system stopped successfully")
        
        logger.info("✓ MCP tool integration test passed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ MCP tool integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_tool_system_without_mcp():
    """Test that the tool system works without MCP."""
    logger.info("Testing tool system without MCP...")
    
    try:
        # Get tools without starting MCP system
        tools = get_langchain_tools()
        logger.info(f"✓ Got {len(tools)} tools without MCP system")
        
        # Verify we have at least built-in and plugin tools
        assert len(tools) > 0, "No tools found"
        
        # Check tool names
        tool_names = [tool.name for tool in tools]
        logger.info(f"✓ Available tools: {tool_names}")
        
        # Should have at least video tool and some plugin tools
        assert any("video" in name.lower() for name in tool_names), "Video tool not found"
        
        logger.info("✓ Tool system works correctly without MCP")
        return True
        
    except Exception as e:
        logger.error(f"❌ Tool system test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all MCP tool integration tests."""
    logger.info("Starting MCP tool integration tests...")
    
    try:
        # Test tool system without MCP first
        if not test_tool_system_without_mcp():
            return False
        
        # Test MCP integration
        if not test_mcp_tool_integration():
            return False
        
        logger.info("🎉 All MCP tool integration tests passed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ MCP tool integration tests failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
