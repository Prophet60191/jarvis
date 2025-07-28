"""
MCP Client Manager for Jarvis Voice Assistant.

This module provides the core MCP (Model Context Protocol) client functionality
for connecting to external MCP servers and managing dynamic tool discovery.
"""

import asyncio
import json
import logging
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
        if not self.connected or not self.process:
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
            while self.connected and self.process:
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
