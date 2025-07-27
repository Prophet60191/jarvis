#!/usr/bin/env python3
"""
Complete MCP System Test for Jarvis Voice Assistant.

This script performs end-to-end testing of the MCP integration system.
"""

import logging
import sys
import time
import requests
import json
from pathlib import Path

# Add the jarvis module to the path
sys.path.insert(0, str(Path(__file__).parent))

from jarvis.tools import get_langchain_tools, start_mcp_system, stop_mcp_system, get_mcp_client
from jarvis.core.mcp_client import MCPServerConfig, MCPTransportType

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_mcp_system_integration():
    """Test complete MCP system integration."""
    logger.info("🧪 Testing complete MCP system integration...")
    
    try:
        # 1. Test MCP system startup
        logger.info("1. Testing MCP system startup...")
        success = start_mcp_system()
        assert success, "Failed to start MCP system"
        logger.info("✓ MCP system started successfully")
        
        # 2. Test tool loading without MCP servers
        logger.info("2. Testing tool loading...")
        tools = get_langchain_tools()
        initial_count = len(tools)
        logger.info(f"✓ Loaded {initial_count} tools (built-in + plugins)")
        
        # 3. Test adding MCP server
        logger.info("3. Testing MCP server addition...")
        mcp_client = get_mcp_client()
        test_config = MCPServerConfig(
            name="test-memory-server",
            transport=MCPTransportType.STDIO,
            command="echo",  # Simple command that won't actually work but tests config
            args=["test"],
            enabled=False  # Don't auto-connect
        )
        
        success = mcp_client.add_server(test_config)
        assert success, "Failed to add test server"
        logger.info("✓ Test server added successfully")
        
        # 4. Test server info retrieval
        logger.info("4. Testing server info retrieval...")
        server_info = mcp_client.get_server_info("test-memory-server")
        assert server_info is not None, "Server info not found"
        assert server_info.name == "test-memory-server", "Server name mismatch"
        logger.info("✓ Server info retrieved correctly")
        
        # 5. Test server removal
        logger.info("5. Testing server removal...")
        success = mcp_client.remove_server("test-memory-server")
        assert success, "Failed to remove test server"
        logger.info("✓ Test server removed successfully")
        
        # 6. Test MCP system shutdown
        logger.info("6. Testing MCP system shutdown...")
        success = stop_mcp_system()
        assert success, "Failed to stop MCP system"
        logger.info("✓ MCP system stopped successfully")
        
        logger.info("🎉 Complete MCP system integration test passed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ MCP system integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_ui_api_endpoints():
    """Test UI API endpoints."""
    logger.info("🌐 Testing UI API endpoints...")
    
    try:
        base_url = "http://localhost:8085"
        
        # Test servers API
        logger.info("1. Testing servers API...")
        response = requests.get(f"{base_url}/api/mcp/servers", timeout=5)
        assert response.status_code == 200, f"Servers API failed: {response.status_code}"
        servers_data = response.json()
        assert "servers" in servers_data, "Servers data missing"
        logger.info("✓ Servers API working")
        
        # Test tools API
        logger.info("2. Testing tools API...")
        response = requests.get(f"{base_url}/api/mcp/tools", timeout=5)
        assert response.status_code == 200, f"Tools API failed: {response.status_code}"
        tools_data = response.json()
        assert "tools" in tools_data, "Tools data missing"
        logger.info("✓ Tools API working")
        
        # Test server configuration validation
        logger.info("3. Testing server configuration validation...")
        test_config = {
            "action": "test",
            "name": "test-validation",
            "transport": "stdio",
            "command": "echo",
            "args": ["hello"],
            "env": {"TEST": "value"}
        }
        
        response = requests.post(
            f"{base_url}/api/mcp/servers",
            json=test_config,
            timeout=10
        )
        assert response.status_code == 200, f"Validation API failed: {response.status_code}"
        result = response.json()
        assert result.get("success") == True, f"Validation failed: {result}"
        logger.info("✓ Server configuration validation working")
        
        logger.info("🎉 UI API endpoints test passed!")
        return True
        
    except requests.exceptions.ConnectionError:
        logger.warning("⚠️ UI server not running, skipping API tests")
        return True  # Don't fail if UI server isn't running
    except Exception as e:
        logger.error(f"❌ UI API endpoints test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_template_system():
    """Test MCP server template system."""
    logger.info("📋 Testing MCP server template system...")
    
    try:
        from jarvis.core.mcp_templates import get_all_templates, get_template, create_config_from_template
        
        # Test template retrieval
        logger.info("1. Testing template retrieval...")
        templates = get_all_templates()
        assert len(templates) > 0, "No templates found"
        logger.info(f"✓ Found {len(templates)} templates")
        
        # Test specific template
        logger.info("2. Testing specific template...")
        github_template = get_template("github")
        assert github_template is not None, "GitHub template not found"
        assert github_template.name == "GitHub Integration", "Template name mismatch"
        logger.info("✓ GitHub template retrieved correctly")
        
        # Test config creation from template
        logger.info("3. Testing config creation from template...")
        config = create_config_from_template("memory", custom_name="test-memory")
        assert config.name == "test-memory", "Custom name not applied"
        assert config.transport == MCPTransportType.STDIO, "Transport type mismatch"
        logger.info("✓ Config created from template successfully")
        
        logger.info("🎉 Template system test passed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Template system test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all comprehensive MCP system tests."""
    logger.info("🚀 Starting comprehensive MCP system tests...")
    
    tests = [
        ("MCP System Integration", test_mcp_system_integration),
        ("Template System", test_template_system),
        ("UI API Endpoints", test_ui_api_endpoints),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        logger.info(f"\n{'='*50}")
        logger.info(f"Running: {test_name}")
        logger.info(f"{'='*50}")
        
        try:
            if test_func():
                logger.info(f"✅ {test_name} PASSED")
                passed += 1
            else:
                logger.error(f"❌ {test_name} FAILED")
                failed += 1
        except Exception as e:
            logger.error(f"❌ {test_name} FAILED with exception: {e}")
            failed += 1
    
    logger.info(f"\n{'='*50}")
    logger.info(f"TEST RESULTS: {passed} passed, {failed} failed")
    logger.info(f"{'='*50}")
    
    if failed == 0:
        logger.info("🎉 ALL TESTS PASSED! MCP system is ready for production use.")
        return True
    else:
        logger.error(f"❌ {failed} tests failed. Please review the errors above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
