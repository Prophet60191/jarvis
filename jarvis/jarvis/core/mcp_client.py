"""
MCP Client Manager for Jarvis Voice Assistant.

This module provides the core MCP (Model Context Protocol) client functionality
for connecting to external MCP servers and managing dynamic tool discovery.
"""

import asyncio
import json
import logging
import os
import subprocess
import threading
import time
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable, Union
from urllib.parse import urlparse

import aiohttp
import websockets
from langchain_core.tools import BaseTool

logger = logging.getLogger(__name__)


class MCPTransportType(Enum):
    """Supported MCP transport types."""
    STDIO = "stdio"
    SSE = "sse"
    WEBSOCKET = "websocket"


class MCPServerStatus(Enum):
    """MCP server connection status."""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"


@dataclass
class MCPServerConfig:
    """Configuration for an MCP server connection."""
    name: str
    transport: MCPTransportType
    enabled: bool = True
    
    # STDIO transport config
    command: Optional[str] = None
    args: List[str] = field(default_factory=list)
    env: Dict[str, str] = field(default_factory=dict)
    cwd: Optional[str] = None
    
    # HTTP/SSE transport config
    url: Optional[str] = None
    headers: Dict[str, str] = field(default_factory=dict)
    timeout: int = 30
    
    # WebSocket transport config
    # (uses url and headers from HTTP config)
    
    def validate(self) -> None:
        """Validate the server configuration."""
        if self.transport == MCPTransportType.STDIO:
            if not self.command:
                raise ValueError("STDIO transport requires command")
        elif self.transport in (MCPTransportType.SSE, MCPTransportType.WEBSOCKET):
            if not self.url:
                raise ValueError(f"{self.transport.value} transport requires URL")
            # Validate URL format
            parsed = urlparse(self.url)
            if not parsed.scheme or not parsed.netloc:
                raise ValueError(f"Invalid URL format: {self.url}")


@dataclass
class MCPTool:
    """Represents a tool discovered from an MCP server."""
    name: str
    description: str
    server_name: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    enabled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MCPServerInfo:
    """Information about a connected MCP server."""
    name: str
    config: MCPServerConfig
    status: MCPServerStatus
    tools: List[MCPTool] = field(default_factory=list)
    capabilities: Dict[str, Any] = field(default_factory=dict)
    last_error: Optional[str] = None
    connected_at: Optional[float] = None


class MCPTransport(ABC):
    """Abstract base class for MCP transport implementations."""
    
    def __init__(self, config: MCPServerConfig):
        self.config = config
        self.connected = False
        self.message_id = 0
        
    @abstractmethod
    async def connect(self) -> bool:
        """Connect to the MCP server."""
        pass
        
    @abstractmethod
    async def disconnect(self) -> None:
        """Disconnect from the MCP server."""
        pass
        
    @abstractmethod
    async def send_request(self, method: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Send a JSON-RPC request to the server."""
        pass
        
    def _create_request(self, method: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create a JSON-RPC 2.0 request."""
        self.message_id += 1
        request = {
            "jsonrpc": "2.0",
            "id": self.message_id,
            "method": method
        }
        if params:
            request["params"] = params
        return request


class STDIOTransport(MCPTransport):
    """STDIO transport for MCP communication."""
    
    def __init__(self, config: MCPServerConfig):
        super().__init__(config)
        self.process: Optional[subprocess.Popen] = None
        self.reader_task: Optional[asyncio.Task] = None
        self.pending_requests: Dict[int, asyncio.Future] = {}
        
    async def connect(self) -> bool:
        """Connect to the MCP server via STDIO."""
        try:
            # Build command with arguments
            cmd = [self.config.command] + self.config.args
            
            # Set up environment
            env = dict(os.environ)
            env.update(self.config.env)
            
            # Start the process
            self.process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env,
                cwd=self.config.cwd,
                text=True,
                bufsize=0
            )
            
            # Start reading responses
            self.reader_task = asyncio.create_task(self._read_responses())
            
            # Send initialize request
            init_response = await self.send_request("initialize", {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "roots": {"listChanged": True},
                    "sampling": {}
                },
                "clientInfo": {
                    "name": "jarvis-voice-assistant",
                    "version": "1.0.0"
                }
            })
            
            if "error" in init_response:
                logger.error(f"MCP initialization failed: {init_response['error']}")
                return False
                
            self.connected = True
            logger.info(f"Connected to MCP server: {self.config.name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to MCP server {self.config.name}: {e}")
            await self.disconnect()
            return False
    
    async def disconnect(self) -> None:
        """Disconnect from the MCP server."""
        self.connected = False
        
        if self.reader_task:
            self.reader_task.cancel()
            try:
                await self.reader_task
            except asyncio.CancelledError:
                pass
            
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait()
            except Exception as e:
                logger.warning(f"Error terminating MCP process: {e}")
            finally:
                self.process = None
                
        # Cancel pending requests
        for future in self.pending_requests.values():
            if not future.done():
                future.cancel()
        self.pending_requests.clear()
        
        logger.info(f"Disconnected from MCP server: {self.config.name}")
    
    async def send_request(self, method: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Send a JSON-RPC request via STDIO."""
        # Allow initialize request even when not connected yet
        if not self.process or (not self.connected and method != "initialize"):
            raise RuntimeError("Not connected to MCP server")
            
        request = self._create_request(method, params)
        request_id = request["id"]
        
        # Create future for response
        future = asyncio.Future()
        self.pending_requests[request_id] = future
        
        try:
            # Send request
            request_json = json.dumps(request) + "\n"
            self.process.stdin.write(request_json)
            self.process.stdin.flush()
            
            # Wait for response with timeout
            response = await asyncio.wait_for(future, timeout=self.config.timeout)
            return response
            
        except asyncio.TimeoutError:
            logger.error(f"MCP request timeout for method: {method}")
            return {"error": {"code": -32603, "message": "Request timeout"}}
        except Exception as e:
            logger.error(f"Error sending MCP request: {e}")
            return {"error": {"code": -32603, "message": str(e)}}
        finally:
            self.pending_requests.pop(request_id, None)
    
    async def _read_responses(self) -> None:
        """Read responses from the MCP server."""
        try:
            while self.process and self.process.poll() is None:
                line = await asyncio.get_event_loop().run_in_executor(
                    None, self.process.stdout.readline
                )
                
                if not line:
                    break
                    
                try:
                    response = json.loads(line.strip())
                    
                    # Handle response
                    if "id" in response:
                        request_id = response["id"]
                        if request_id in self.pending_requests:
                            future = self.pending_requests[request_id]
                            if not future.done():
                                future.set_result(response)
                    
                except json.JSONDecodeError as e:
                    logger.warning(f"Invalid JSON from MCP server: {e}")
                    
        except Exception as e:
            logger.error(f"Error reading MCP responses: {e}")
        finally:
            self.connected = False


class SSETransport(MCPTransport):
    """Server-Sent Events transport for MCP communication."""
    
    def __init__(self, config: MCPServerConfig):
        super().__init__(config)
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def connect(self) -> bool:
        """Connect to the MCP server via SSE."""
        try:
            self.session = aiohttp.ClientSession(
                headers=self.config.headers,
                timeout=aiohttp.ClientTimeout(total=self.config.timeout)
            )
            
            # Test connection with initialize request
            init_response = await self.send_request("initialize", {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "roots": {"listChanged": True},
                    "sampling": {}
                },
                "clientInfo": {
                    "name": "jarvis-voice-assistant",
                    "version": "1.0.0"
                }
            })
            
            if "error" in init_response:
                logger.error(f"MCP SSE initialization failed: {init_response['error']}")
                return False
                
            self.connected = True
            logger.info(f"Connected to MCP SSE server: {self.config.name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to MCP SSE server {self.config.name}: {e}")
            await self.disconnect()
            return False
    
    async def disconnect(self) -> None:
        """Disconnect from the MCP SSE server."""
        self.connected = False
        
        if self.session:
            await self.session.close()
            self.session = None
            
        logger.info(f"Disconnected from MCP SSE server: {self.config.name}")
    
    async def send_request(self, method: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Send a JSON-RPC request via SSE."""
        if not self.connected or not self.session:
            raise RuntimeError("Not connected to MCP SSE server")
            
        request = self._create_request(method, params)
        
        try:
            async with self.session.post(self.config.url, json=request) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    return {
                        "error": {
                            "code": -32603,
                            "message": f"HTTP {response.status}: {error_text}"
                        }
                    }
                    
        except Exception as e:
            logger.error(f"Error sending MCP SSE request: {e}")
            return {"error": {"code": -32603, "message": str(e)}}


class WebSocketTransport(MCPTransport):
    """WebSocket transport for MCP communication."""

    def __init__(self, config: MCPServerConfig):
        super().__init__(config)
        self.websocket: Optional[websockets.WebSocketServerProtocol] = None
        self.pending_requests: Dict[int, asyncio.Future] = {}
        self.reader_task: Optional[asyncio.Task] = None

    async def connect(self) -> bool:
        """Connect to the MCP server via WebSocket."""
        try:
            # Convert HTTP URL to WebSocket URL
            ws_url = self.config.url.replace("http://", "ws://").replace("https://", "wss://")

            # Connect to WebSocket
            self.websocket = await websockets.connect(
                ws_url,
                extra_headers=self.config.headers,
                timeout=self.config.timeout
            )

            # Start reading responses
            self.reader_task = asyncio.create_task(self._read_responses())

            # Send initialize request
            init_response = await self.send_request("initialize", {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "roots": {"listChanged": True},
                    "sampling": {}
                },
                "clientInfo": {
                    "name": "jarvis-voice-assistant",
                    "version": "1.0.0"
                }
            })

            if "error" in init_response:
                logger.error(f"MCP WebSocket initialization failed: {init_response['error']}")
                return False

            self.connected = True
            logger.info(f"Connected to MCP WebSocket server: {self.config.name}")
            return True

        except Exception as e:
            logger.error(f"Failed to connect to MCP WebSocket server {self.config.name}: {e}")
            await self.disconnect()
            return False

    async def disconnect(self) -> None:
        """Disconnect from the MCP WebSocket server."""
        self.connected = False

        if self.reader_task:
            self.reader_task.cancel()
            try:
                await self.reader_task
            except asyncio.CancelledError:
                pass

        if self.websocket:
            await self.websocket.close()
            self.websocket = None

        # Cancel pending requests
        for future in self.pending_requests.values():
            if not future.done():
                future.cancel()
        self.pending_requests.clear()

        logger.info(f"Disconnected from MCP WebSocket server: {self.config.name}")

    async def send_request(self, method: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Send a JSON-RPC request via WebSocket."""
        if not self.connected or not self.websocket:
            raise RuntimeError("Not connected to MCP WebSocket server")

        request = self._create_request(method, params)
        request_id = request["id"]

        # Create future for response
        future = asyncio.Future()
        self.pending_requests[request_id] = future

        try:
            # Send request
            await self.websocket.send(json.dumps(request))

            # Wait for response with timeout
            response = await asyncio.wait_for(future, timeout=self.config.timeout)
            return response

        except asyncio.TimeoutError:
            logger.error(f"MCP WebSocket request timeout for method: {method}")
            return {"error": {"code": -32603, "message": "Request timeout"}}
        except Exception as e:
            logger.error(f"Error sending MCP WebSocket request: {e}")
            return {"error": {"code": -32603, "message": str(e)}}
        finally:
            self.pending_requests.pop(request_id, None)

    async def _read_responses(self) -> None:
        """Read responses from the MCP WebSocket server."""
        try:
            async for message in self.websocket:
                try:
                    response = json.loads(message)

                    # Handle response
                    if "id" in response:
                        request_id = response["id"]
                        if request_id in self.pending_requests:
                            future = self.pending_requests[request_id]
                            if not future.done():
                                future.set_result(response)

                except json.JSONDecodeError as e:
                    logger.warning(f"Invalid JSON from MCP WebSocket server: {e}")

        except Exception as e:
            logger.error(f"Error reading MCP WebSocket responses: {e}")
        finally:
            self.connected = False


class MCPClientManager:
    """
    Main MCP client manager for Jarvis Voice Assistant.

    Manages connections to multiple MCP servers, tool discovery,
    and dynamic tool execution.
    """

    def __init__(self, config_file: Optional[Path] = None):
        """
        Initialize the MCP client manager.

        Args:
            config_file: Path to MCP configuration file
        """
        self.config_file = config_file or Path.home() / ".jarvis" / "mcp_servers.json"
        self.servers: Dict[str, MCPServerInfo] = {}
        self.transports: Dict[str, MCPTransport] = {}
        self.tools: Dict[str, MCPTool] = {}
        self.event_loop: Optional[asyncio.AbstractEventLoop] = None
        self.background_task: Optional[asyncio.Task] = None
        self._lock = threading.Lock()

        # Callbacks for UI updates
        self.on_server_status_changed: Optional[Callable[[str, MCPServerStatus], None]] = None
        self.on_tools_updated: Optional[Callable[[List[MCPTool]], None]] = None

    def start(self) -> None:
        """Start the MCP client manager."""
        if self.event_loop and not self.event_loop.is_closed():
            return

        # Create event loop for async operations
        self.event_loop = asyncio.new_event_loop()

        # Start background thread for async operations
        def run_event_loop():
            asyncio.set_event_loop(self.event_loop)
            self.event_loop.run_forever()

        thread = threading.Thread(target=run_event_loop, daemon=True)
        thread.start()

        # Load configuration and connect to servers
        self.load_configuration()

        logger.info("MCP Client Manager started")

    def stop(self) -> None:
        """Stop the MCP client manager."""
        if self.background_task:
            asyncio.run_coroutine_threadsafe(
                self._disconnect_all_servers(), self.event_loop
            )

        if self.event_loop and not self.event_loop.is_closed():
            self.event_loop.call_soon_threadsafe(self.event_loop.stop)

        logger.info("MCP Client Manager stopped")

    def load_configuration(self) -> None:
        """Load MCP server configurations from file."""
        if not self.config_file.exists():
            logger.info("No MCP configuration file found, creating default")
            self.save_configuration()
            return

        try:
            with open(self.config_file, 'r') as f:
                config_data = json.load(f)

            for server_name, server_config in config_data.get("mcpServers", {}).items():
                try:
                    # Convert config dict to MCPServerConfig
                    transport_type = MCPTransportType(server_config["transport"])
                    config = MCPServerConfig(
                        name=server_name,
                        transport=transport_type,
                        enabled=server_config.get("enabled", True),
                        command=server_config.get("command"),
                        args=server_config.get("args", []),
                        env=server_config.get("env", {}),
                        cwd=server_config.get("cwd"),
                        url=server_config.get("url"),
                        headers=server_config.get("headers", {}),
                        timeout=server_config.get("timeout", 30)
                    )

                    config.validate()

                    # Create server info
                    server_info = MCPServerInfo(
                        name=server_name,
                        config=config,
                        status=MCPServerStatus.DISCONNECTED
                    )

                    self.servers[server_name] = server_info

                    # Connect if enabled
                    if config.enabled:
                        asyncio.run_coroutine_threadsafe(
                            self.connect_server(server_name), self.event_loop
                        )

                except Exception as e:
                    logger.error(f"Error loading MCP server config '{server_name}': {e}")

        except Exception as e:
            logger.error(f"Error loading MCP configuration: {e}")

    def save_configuration(self) -> None:
        """Save MCP server configurations to file."""
        try:
            # Ensure directory exists
            self.config_file.parent.mkdir(parents=True, exist_ok=True)

            # Build configuration data
            config_data = {"mcpServers": {}}

            for server_name, server_info in self.servers.items():
                config = server_info.config
                server_config = {
                    "transport": config.transport.value,
                    "enabled": config.enabled
                }

                # Add transport-specific config
                if config.transport == MCPTransportType.STDIO:
                    server_config.update({
                        "command": config.command,
                        "args": config.args,
                        "env": config.env
                    })
                    if config.cwd:
                        server_config["cwd"] = config.cwd

                elif config.transport in (MCPTransportType.SSE, MCPTransportType.WEBSOCKET):
                    server_config.update({
                        "url": config.url,
                        "headers": config.headers,
                        "timeout": config.timeout
                    })

                config_data["mcpServers"][server_name] = server_config

            # Write to file
            with open(self.config_file, 'w') as f:
                json.dump(config_data, f, indent=2)

            logger.info(f"MCP configuration saved to {self.config_file}")

        except Exception as e:
            logger.error(f"Error saving MCP configuration: {e}")

    async def connect_server(self, server_name: str) -> bool:
        """
        Connect to an MCP server.

        Args:
            server_name: Name of the server to connect to

        Returns:
            True if connection successful, False otherwise
        """
        if server_name not in self.servers:
            logger.error(f"Unknown MCP server: {server_name}")
            return False

        server_info = self.servers[server_name]

        # Update status
        server_info.status = MCPServerStatus.CONNECTING
        self._notify_status_change(server_name, MCPServerStatus.CONNECTING)

        try:
            # Create transport
            transport = self._create_transport(server_info.config)

            # Connect
            if await transport.connect():
                self.transports[server_name] = transport
                server_info.status = MCPServerStatus.CONNECTED
                server_info.connected_at = time.time()
                server_info.last_error = None

                # Discover tools
                await self._discover_tools(server_name)

                self._notify_status_change(server_name, MCPServerStatus.CONNECTED)
                logger.info(f"Successfully connected to MCP server: {server_name}")
                return True
            else:
                server_info.status = MCPServerStatus.ERROR
                server_info.last_error = "Connection failed"
                self._notify_status_change(server_name, MCPServerStatus.ERROR)
                return False

        except Exception as e:
            server_info.status = MCPServerStatus.ERROR
            server_info.last_error = str(e)
            self._notify_status_change(server_name, MCPServerStatus.ERROR)
            logger.error(f"Error connecting to MCP server {server_name}: {e}")
            return False

    async def disconnect_server(self, server_name: str) -> None:
        """
        Disconnect from an MCP server.

        Args:
            server_name: Name of the server to disconnect from
        """
        if server_name not in self.servers:
            return

        server_info = self.servers[server_name]

        # Disconnect transport
        if server_name in self.transports:
            transport = self.transports[server_name]
            await transport.disconnect()
            del self.transports[server_name]

        # Update status
        server_info.status = MCPServerStatus.DISCONNECTED
        server_info.connected_at = None

        # Remove tools from this server
        tools_to_remove = [name for name, tool in self.tools.items()
                          if tool.server_name == server_name]
        for tool_name in tools_to_remove:
            del self.tools[tool_name]

        server_info.tools.clear()

        self._notify_status_change(server_name, MCPServerStatus.DISCONNECTED)
        self._notify_tools_updated()

        logger.info(f"Disconnected from MCP server: {server_name}")

    async def _disconnect_all_servers(self) -> None:
        """Disconnect from all MCP servers."""
        for server_name in list(self.servers.keys()):
            await self.disconnect_server(server_name)

    def _create_transport(self, config: MCPServerConfig) -> MCPTransport:
        """Create appropriate transport for server configuration."""
        if config.transport == MCPTransportType.STDIO:
            return STDIOTransport(config)
        elif config.transport == MCPTransportType.SSE:
            return SSETransport(config)
        elif config.transport == MCPTransportType.WEBSOCKET:
            return WebSocketTransport(config)
        else:
            raise ValueError(f"Unsupported transport type: {config.transport}")

    async def _discover_tools(self, server_name: str) -> None:
        """
        Discover tools from an MCP server.

        Args:
            server_name: Name of the server to discover tools from
        """
        if server_name not in self.transports:
            return

        transport = self.transports[server_name]
        server_info = self.servers[server_name]

        try:
            # Request tools list
            response = await transport.send_request("tools/list")

            if "error" in response:
                logger.error(f"Error discovering tools from {server_name}: {response['error']}")
                return

            # Process tools
            tools_data = response.get("result", {}).get("tools", [])
            discovered_tools = []

            for tool_data in tools_data:
                tool = MCPTool(
                    name=tool_data["name"],
                    description=tool_data.get("description", ""),
                    server_name=server_name,
                    parameters=tool_data.get("inputSchema", {}),
                    metadata=tool_data
                )

                discovered_tools.append(tool)
                self.tools[f"{server_name}:{tool.name}"] = tool

            server_info.tools = discovered_tools

            # Notify UI of tool updates
            self._notify_tools_updated()

            logger.info(f"Discovered {len(discovered_tools)} tools from {server_name}")

        except Exception as e:
            logger.error(f"Error discovering tools from {server_name}: {e}")

    async def execute_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """
        Execute a tool on the appropriate MCP server.

        Args:
            tool_name: Name of the tool to execute (format: server:tool)
            **kwargs: Tool parameters

        Returns:
            Tool execution result
        """
        if tool_name not in self.tools:
            return {"error": f"Tool not found: {tool_name}"}

        tool = self.tools[tool_name]
        server_name = tool.server_name

        if server_name not in self.transports:
            return {"error": f"Server not connected: {server_name}"}

        transport = self.transports[server_name]

        try:
            # Execute tool
            response = await transport.send_request("tools/call", {
                "name": tool.name,
                "arguments": kwargs
            })

            if "error" in response:
                logger.error(f"Tool execution error: {response['error']}")
                return response

            result = response.get("result", {})
            logger.info(f"Successfully executed tool: {tool_name}")
            return result

        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {e}")
            return {"error": str(e)}

    def _notify_status_change(self, server_name: str, status: MCPServerStatus) -> None:
        """Notify UI of server status change."""
        if self.on_server_status_changed:
            try:
                self.on_server_status_changed(server_name, status)
            except Exception as e:
                logger.error(f"Error in status change callback: {e}")

    def _notify_tools_updated(self) -> None:
        """Notify UI of tool updates."""
        if self.on_tools_updated:
            try:
                all_tools = list(self.tools.values())
                self.on_tools_updated(all_tools)
            except Exception as e:
                logger.error(f"Error in tools updated callback: {e}")

    # Synchronous wrapper methods for UI integration

    def add_server(self, config: MCPServerConfig) -> bool:
        """
        Add a new MCP server configuration.

        Args:
            config: Server configuration

        Returns:
            True if added successfully
        """
        try:
            config.validate()

            server_info = MCPServerInfo(
                name=config.name,
                config=config,
                status=MCPServerStatus.DISCONNECTED
            )

            self.servers[config.name] = server_info
            self.save_configuration()

            # Connect if enabled
            if config.enabled and self.event_loop:
                asyncio.run_coroutine_threadsafe(
                    self.connect_server(config.name), self.event_loop
                )

            logger.info(f"Added MCP server: {config.name}")
            return True

        except Exception as e:
            logger.error(f"Error adding MCP server: {e}")
            return False

    def remove_server(self, server_name: str) -> bool:
        """
        Remove an MCP server configuration.

        Args:
            server_name: Name of the server to remove

        Returns:
            True if removed successfully
        """
        if server_name not in self.servers:
            return False

        try:
            # Disconnect if connected
            if self.event_loop:
                asyncio.run_coroutine_threadsafe(
                    self.disconnect_server(server_name), self.event_loop
                )

            # Remove from configuration
            del self.servers[server_name]
            self.save_configuration()

            logger.info(f"Removed MCP server: {server_name}")
            return True

        except Exception as e:
            logger.error(f"Error removing MCP server: {e}")
            return False

    def get_server_info(self, server_name: str) -> Optional[MCPServerInfo]:
        """Get information about a specific server."""
        return self.servers.get(server_name)

    def get_all_servers(self) -> Dict[str, MCPServerInfo]:
        """Get information about all servers."""
        return self.servers.copy()

    def get_all_tools(self) -> List[MCPTool]:
        """Get all available tools from all servers."""
        return list(self.tools.values())

    def get_enabled_tools(self) -> List[MCPTool]:
        """Get all enabled tools from all servers."""
        return [tool for tool in self.tools.values() if tool.enabled]
