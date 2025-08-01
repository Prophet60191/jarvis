"""
MCP Client for Jarvis Voice Assistant.

This module provides the client implementation for connecting to MCP (Model Context Protocol) servers,
managing server connections, and integrating MCP tools with the Jarvis tool system.
"""

import json
import logging
import subprocess
import asyncio
import os
from typing import Dict, List, Optional, Any
from pathlib import Path

# Import shared types from config manager
from .mcp_config_manager import MCPServerConfig, MCPTransportType

logger = logging.getLogger(__name__)


class MCPServerConnection:
    """Manages connection to a single MCP server."""
    
    def __init__(self, config: MCPServerConfig):
        self.config = config
        self.process: Optional[subprocess.Popen] = None
        self.connected = False
        self.tools: List[Dict[str, Any]] = []
        self.resources: List[Dict[str, Any]] = []
    
    async def connect(self) -> bool:
        """Connect to the MCP server."""
        try:
            if self.config.transport == MCPTransportType.STDIO:
                return await self._connect_stdio()
            else:
                logger.warning(f"Transport type {self.config.transport} not yet implemented")
                return False

        except Exception as e:
            logger.error(f"Error connecting to MCP server {self.config.name}: {e}")
            return False
    
    async def _connect_stdio(self) -> bool:
        """Connect to MCP server using STDIO transport."""
        try:
            # Start the MCP server process
            env = dict(os.environ)
            if self.config.env:
                env.update(self.config.env)
            
            self.process = subprocess.Popen(
                [self.config.command] + self.config.args,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=env
            )
            
            # Send initialize request
            init_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "roots": {"listChanged": True},
                        "sampling": {}
                    },
                    "clientInfo": {
                        "name": "jarvis-voice-assistant",
                        "version": "1.0.0"
                    }
                }
            }
            
            # Send request
            request_json = json.dumps(init_request) + "\n"
            self.process.stdin.write(request_json)
            self.process.stdin.flush()
            
            # Read response with timeout
            try:
                response_line = await asyncio.wait_for(
                    asyncio.get_event_loop().run_in_executor(
                        None, self.process.stdout.readline
                    ),
                    timeout=self.config.timeout
                )
                
                if response_line:
                    response = json.loads(response_line.strip())
                    if "result" in response:
                        self.connected = True
                        logger.info(f"Successfully connected to MCP server: {self.config.name}")
                        
                        # Get available tools
                        await self._list_tools()
                        return True
                        
            except asyncio.TimeoutError:
                logger.error(f"Timeout connecting to MCP server: {self.config.name}")
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON response from MCP server {self.config.name}: {e}")
            
            return False
            
        except Exception as e:
            logger.error(f"Error in STDIO connection to {self.config.name}: {e}")
            return False
    
    async def _list_tools(self) -> None:
        """List available tools from the MCP server."""
        try:
            if not self.process or not self.connected:
                return
            
            # Send tools/list request
            tools_request = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/list",
                "params": {}
            }
            
            request_json = json.dumps(tools_request) + "\n"
            self.process.stdin.write(request_json)
            self.process.stdin.flush()
            
            # Read response
            response_line = await asyncio.wait_for(
                asyncio.get_event_loop().run_in_executor(
                    None, self.process.stdout.readline
                ),
                timeout=10
            )
            
            if response_line:
                response = json.loads(response_line.strip())
                if "result" in response and "tools" in response["result"]:
                    self.tools = response["result"]["tools"]
                    logger.info(f"Found {len(self.tools)} tools in MCP server: {self.config.name}")
                    
        except Exception as e:
            logger.error(f"Error listing tools from MCP server {self.config.name}: {e}")
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Call a tool on the MCP server."""
        try:
            if not self.process or not self.connected:
                logger.error(f"MCP server {self.config.name} not connected")
                return None
            
            # Send tools/call request
            call_request = {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": arguments
                }
            }
            
            request_json = json.dumps(call_request) + "\n"
            self.process.stdin.write(request_json)
            self.process.stdin.flush()
            
            # Read response
            response_line = await asyncio.wait_for(
                asyncio.get_event_loop().run_in_executor(
                    None, self.process.stdout.readline
                ),
                timeout=30
            )
            
            if response_line:
                response = json.loads(response_line.strip())
                if "result" in response:
                    return response["result"]
                elif "error" in response:
                    logger.error(f"MCP tool call error: {response['error']}")
                    return None
            
            return None
            
        except Exception as e:
            logger.error(f"Error calling tool {tool_name} on MCP server {self.config.name}: {e}")
            return None
    
    def disconnect(self) -> None:
        """Disconnect from the MCP server."""
        try:
            if self.process:
                self.process.terminate()
                try:
                    self.process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    self.process.kill()
                    self.process.wait()
                
                self.process = None
            
            self.connected = False
            self.tools = []
            self.resources = []
            
            logger.info(f"Disconnected from MCP server: {self.config.name}")
            
        except Exception as e:
            logger.error(f"Error disconnecting from MCP server {self.config.name}: {e}")


class MCPClient:
    """Main MCP client that manages multiple server connections."""
    
    def __init__(self):
        self.connections: Dict[str, MCPServerConnection] = {}
        self.config_manager = None
    
    def set_config_manager(self, config_manager):
        """Set the MCP configuration manager."""
        self.config_manager = config_manager
    
    async def connect_all_servers(self) -> Dict[str, bool]:
        """Connect to all enabled MCP servers."""
        results = {}
        
        if not self.config_manager:
            logger.error("No MCP configuration manager set")
            return results
        
        enabled_servers = self.config_manager.get_enabled_servers()
        
        for server_id, config in enabled_servers.items():
            try:
                connection = MCPServerConnection(config)
                success = await connection.connect()
                
                if success:
                    self.connections[server_id] = connection
                    results[server_id] = True
                    logger.info(f"Connected to MCP server: {config.name}")
                else:
                    results[server_id] = False
                    logger.warning(f"Failed to connect to MCP server: {config.name}")
                    
            except Exception as e:
                logger.error(f"Error connecting to MCP server {config.name}: {e}")
                results[server_id] = False
        
        return results
    
    def get_all_tools(self) -> List[Dict[str, Any]]:
        """Get all tools from all connected MCP servers."""
        all_tools = []
        
        for server_id, connection in self.connections.items():
            if connection.connected:
                for tool in connection.tools:
                    # Add server information to tool
                    tool_with_server = tool.copy()
                    tool_with_server["_mcp_server"] = server_id
                    tool_with_server["_mcp_server_name"] = connection.config.name
                    all_tools.append(tool_with_server)
        
        return all_tools
    
    async def call_tool(self, server_id: str, tool_name: str, arguments: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Call a tool on a specific MCP server."""
        if server_id not in self.connections:
            logger.error(f"MCP server {server_id} not connected")
            return None
        
        connection = self.connections[server_id]
        return await connection.call_tool(tool_name, arguments)
    
    def disconnect_all(self) -> None:
        """Disconnect from all MCP servers."""
        for connection in self.connections.values():
            connection.disconnect()
        
        self.connections.clear()
        logger.info("Disconnected from all MCP servers")
    
    def get_connection_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all MCP server connections."""
        status = {}
        
        for server_id, connection in self.connections.items():
            status[server_id] = {
                "name": connection.config.name,
                "connected": connection.connected,
                "tools_count": len(connection.tools),
                "transport": connection.config.transport.value
            }
        
        return status


# Global MCP client instance
_mcp_client = None


def get_mcp_client() -> MCPClient:
    """Get the global MCP client instance."""
    global _mcp_client
    if _mcp_client is None:
        _mcp_client = MCPClient()
    return _mcp_client
