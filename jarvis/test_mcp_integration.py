#!/usr/bin/env python3
"""
Test script for MCP integration functionality.

This script tests the core MCP client components and configuration management
to ensure everything works correctly before full integration.
"""

import asyncio
import json
import logging
import sys
import tempfile
from pathlib import Path

# Add the jarvis module to the path
sys.path.insert(0, str(Path(__file__).parent))

from jarvis.core.mcp_client import (
    MCPClientManager, 
    MCPServerConfig, 
    MCPTransportType,
    MCPServerStatus
)
from jarvis.core.mcp_config import MCPConfigurationManager

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_mcp_configuration():
    """Test MCP configuration management."""
    logger.info("Testing MCP configuration management...")
    
    # Create temporary config file
    with tempfile.TemporaryDirectory() as temp_dir:
        config_file = Path(temp_dir) / "test_mcp_config.json"
        
        # Initialize configuration manager
        config_manager = MCPConfigurationManager(config_file)
        
        # Test adding a server configuration
        test_config = MCPServerConfig(
            name="test-server",
            transport=MCPTransportType.STDIO,
            command="echo",
            args=["hello"],
            env={"TEST_VAR": "test_value"},
            enabled=True
        )
        
        # Add server
        success = config_manager.add_server(test_config)
        assert success, "Failed to add server configuration"
        logger.info("✓ Server configuration added successfully")
        
        # Load configurations
        servers = config_manager.load_configuration()
        assert "test-server" in servers, "Server not found in loaded configuration"
        
        loaded_config = servers["test-server"]
        assert loaded_config.name == "test-server", "Server name mismatch"
        assert loaded_config.transport == MCPTransportType.STDIO, "Transport type mismatch"
        assert loaded_config.command == "echo", "Command mismatch"
        assert loaded_config.args == ["hello"], "Args mismatch"
        assert loaded_config.env == {"TEST_VAR": "test_value"}, "Environment variables mismatch"
        logger.info("✓ Server configuration loaded correctly")
        
        # Test updating server
        test_config.enabled = False
        success = config_manager.update_server(test_config)
        assert success, "Failed to update server configuration"
        
        # Verify update
        servers = config_manager.load_configuration()
        assert not servers["test-server"].enabled, "Server update failed"
        logger.info("✓ Server configuration updated successfully")
        
        # Test removing server
        success = config_manager.remove_server("test-server")
        assert success, "Failed to remove server configuration"
        
        # Verify removal
        servers = config_manager.load_configuration()
        assert "test-server" not in servers, "Server not removed"
        logger.info("✓ Server configuration removed successfully")
        
        logger.info("✓ MCP configuration management tests passed!")


def test_mcp_client_manager():
    """Test MCP client manager basic functionality."""
    logger.info("Testing MCP client manager...")
    
    # Create temporary config file
    with tempfile.TemporaryDirectory() as temp_dir:
        config_file = Path(temp_dir) / "test_mcp_client.json"
        
        # Initialize client manager
        client_manager = MCPClientManager(config_file)
        
        # Test adding a server
        test_config = MCPServerConfig(
            name="test-echo-server",
            transport=MCPTransportType.STDIO,
            command="echo",
            args=["test"],
            enabled=False  # Don't auto-connect for this test
        )
        
        success = client_manager.add_server(test_config)
        assert success, "Failed to add server to client manager"
        logger.info("✓ Server added to client manager")
        
        # Test getting server info
        server_info = client_manager.get_server_info("test-echo-server")
        assert server_info is not None, "Server info not found"
        assert server_info.name == "test-echo-server", "Server name mismatch"
        assert server_info.status == MCPServerStatus.DISCONNECTED, "Server should be disconnected"
        logger.info("✓ Server info retrieved correctly")
        
        # Test getting all servers
        all_servers = client_manager.get_all_servers()
        assert "test-echo-server" in all_servers, "Server not in all servers list"
        logger.info("✓ All servers retrieved correctly")
        
        # Test removing server
        success = client_manager.remove_server("test-echo-server")
        assert success, "Failed to remove server from client manager"
        
        # Verify removal
        server_info = client_manager.get_server_info("test-echo-server")
        assert server_info is None, "Server not removed from client manager"
        logger.info("✓ Server removed from client manager")
        
        logger.info("✓ MCP client manager tests passed!")


def test_mcp_server_config_validation():
    """Test MCP server configuration validation."""
    logger.info("Testing MCP server configuration validation...")
    
    # Test valid STDIO configuration
    stdio_config = MCPServerConfig(
        name="stdio-server",
        transport=MCPTransportType.STDIO,
        command="python",
        args=["-m", "test_server"]
    )
    
    try:
        stdio_config.validate()
        logger.info("✓ Valid STDIO configuration passed validation")
    except Exception as e:
        assert False, f"Valid STDIO configuration failed validation: {e}"
    
    # Test invalid STDIO configuration (missing command)
    invalid_stdio_config = MCPServerConfig(
        name="invalid-stdio",
        transport=MCPTransportType.STDIO
    )
    
    try:
        invalid_stdio_config.validate()
        assert False, "Invalid STDIO configuration should have failed validation"
    except ValueError:
        logger.info("✓ Invalid STDIO configuration correctly failed validation")
    
    # Test valid SSE configuration
    sse_config = MCPServerConfig(
        name="sse-server",
        transport=MCPTransportType.SSE,
        url="https://api.example.com/mcp"
    )
    
    try:
        sse_config.validate()
        logger.info("✓ Valid SSE configuration passed validation")
    except Exception as e:
        assert False, f"Valid SSE configuration failed validation: {e}"
    
    # Test invalid SSE configuration (missing URL)
    invalid_sse_config = MCPServerConfig(
        name="invalid-sse",
        transport=MCPTransportType.SSE
    )
    
    try:
        invalid_sse_config.validate()
        assert False, "Invalid SSE configuration should have failed validation"
    except ValueError:
        logger.info("✓ Invalid SSE configuration correctly failed validation")
    
    # Test invalid URL format
    invalid_url_config = MCPServerConfig(
        name="invalid-url",
        transport=MCPTransportType.SSE,
        url="not-a-valid-url"
    )
    
    try:
        invalid_url_config.validate()
        assert False, "Invalid URL configuration should have failed validation"
    except ValueError:
        logger.info("✓ Invalid URL configuration correctly failed validation")
    
    logger.info("✓ MCP server configuration validation tests passed!")


def test_encryption():
    """Test configuration encryption functionality."""
    logger.info("Testing configuration encryption...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        config_file = Path(temp_dir) / "test_encryption.json"
        
        # Test with password
        config_manager = MCPConfigurationManager(config_file, password="test_password")
        
        # Create config with sensitive data
        test_config = MCPServerConfig(
            name="secure-server",
            transport=MCPTransportType.SSE,
            url="https://api.example.com/mcp",
            headers={"Authorization": "Bearer secret_token"},
            env={"API_KEY": "super_secret_key"}
        )
        
        # Add and save
        success = config_manager.add_server(test_config)
        assert success, "Failed to add server with encryption"
        
        # Read raw file to verify encryption
        with open(config_file, 'r') as f:
            raw_data = json.load(f)
        
        server_data = raw_data['servers']['secure-server']
        
        # Check that sensitive fields are encrypted (should not contain original values)
        assert "secret_token" not in json.dumps(server_data), "Authorization header not encrypted"
        assert "super_secret_key" not in json.dumps(server_data), "API key not encrypted"
        logger.info("✓ Sensitive data encrypted in storage")
        
        # Load and verify decryption
        servers = config_manager.load_configuration()
        loaded_config = servers["secure-server"]
        
        assert loaded_config.headers["Authorization"] == "Bearer secret_token", "Authorization header not decrypted correctly"
        assert loaded_config.env["API_KEY"] == "super_secret_key", "API key not decrypted correctly"
        logger.info("✓ Sensitive data decrypted correctly")
        
        logger.info("✓ Configuration encryption tests passed!")


def main():
    """Run all MCP integration tests."""
    logger.info("Starting MCP integration tests...")
    
    try:
        test_mcp_server_config_validation()
        test_mcp_configuration()
        test_mcp_client_manager()
        test_encryption()
        
        logger.info("🎉 All MCP integration tests passed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ MCP integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
