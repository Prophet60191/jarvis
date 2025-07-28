"""
Official MCP Integration for Jarvis Voice Assistant.

This module uses the official langchain-mcp-adapters library to properly
convert MCP tools to LangChain-compatible tools, resolving schema compatibility issues.
"""

import asyncio
import logging
import os
from typing import List, Optional, Dict, Any
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain_core.tools import BaseTool as LangChainBaseTool

logger = logging.getLogger(__name__)


class OfficialMCPManager:
    """
    Official MCP integration using langchain-mcp-adapters.
    
    This class manages MCP server connections and tool loading using the
    official LangChain MCP adapters library, which properly handles
    schema conversion and compatibility issues.
    """
    
    def __init__(self, server_configs: Dict[str, Dict[str, Any]]):
        """Initialize the official MCP manager with server configurations."""
        self.loop: Optional[asyncio.AbstractEventLoop] = None  # Reference to main event loop
        self.sessions: Dict[str, ClientSession] = {}
        self.clients: Dict[str, Any] = {}  # Store active client connections
        self.tools: List[LangChainBaseTool] = []
        self.server_configs = server_configs
        logger.info(f"OfficialMCPManager initialized with {len(self.server_configs)} server configurations.")

    
    async def start_servers(self) -> bool:
        """
        Start all MCP servers and load tools using official adapters.
        
        Returns:
            bool: True if at least one server started successfully
        """
        try:
            logger.info("🚀 Starting MCP servers with official adapters...")
            
            success_count = 0
            for server_name, config in self.server_configs.items():
                try:
                    await self._start_server(server_name, config)
                    success_count += 1
                    logger.info(f"✅ Started MCP server: {server_name}")
                except Exception as e:
                    logger.error(f"❌ Failed to start MCP server {server_name}: {e}")
            
            if success_count > 0:
                logger.info(f"🎉 Successfully started {success_count} MCP servers")
                return True
            else:
                logger.warning("⚠️ No MCP servers started successfully")
                return False
                
        except Exception as e:
            logger.error(f"❌ Failed to start MCP servers: {e}")
            return False
    
    async def _start_server(self, server_name: str, config: Dict[str, Any]) -> None:
        """Start a single MCP server and load its tools, keeping the connection alive."""
        try:
            # Create server parameters
            server_params = StdioServerParameters(
                command=config["command"],
                args=config["args"],
                env=config.get("env")
            )

            # Manually create and enter the client context to keep it open
            client = stdio_client(server_params)
            read, write = await client.__aenter__()

            # Manually create and enter the session context to keep it open
            session = ClientSession(read, write)
            await session.__aenter__()

            # Initialize the connection
            await session.initialize()

            # Load tools using the LIVE session
            server_tools = await load_mcp_tools(session)

            logger.info(f"📦 Loaded {len(server_tools)} tools from {server_name}")

            # Store the LIVE tools and connection objects for later use
            self.tools.extend(server_tools)
            self.clients[server_name] = client  # Store the active client
            self.sessions[server_name] = session  # Store the active session

        except Exception as e:
            logger.error(f"❌ Error starting server {server_name}: {e}")
            # If something fails, make sure to clean up
            if server_name in self.sessions:
                await self.sessions[server_name].__aexit__(None, None, None)
                del self.sessions[server_name]
            if server_name in self.clients:
                await self.clients[server_name].__aexit__(None, None, None)
                del self.clients[server_name]
            raise
    
    def get_tools(self) -> List[LangChainBaseTool]:
        """
        Get all loaded MCP tools as LangChain tools.
        
        Returns:
            List of LangChain-compatible tools
        """
        return self.tools.copy()
    
    def get_tool_count(self) -> int:
        """Get the number of available MCP tools."""
        return len(self.tools)
    
    def get_tool_names(self) -> List[str]:
        """Get the names of all available MCP tools."""
        return [tool.name for tool in self.tools]
    
    async def stop_servers(self) -> None:
        """Stop all MCP servers and clean up resources."""
        try:
            logger.info("🛑 Stopping MCP servers...")

            # Explicitly close all active sessions and clients in reverse order
            for server_name in list(self.sessions.keys()):
                session = self.sessions.pop(server_name)
                try:
                    await session.__aexit__(None, None, None)
                    logger.info(f"✅ Closed MCP session: {server_name}")
                except Exception as e:
                    logger.error(f"❌ Error closing session {server_name}: {e}")

            for server_name in list(self.clients.keys()):
                client = self.clients.pop(server_name)
                try:
                    await client.__aexit__(None, None, None)
                    logger.info(f"✅ Stopped MCP client: {server_name}")
                except Exception as e:
                    logger.error(f"❌ Error stopping client {server_name}: {e}")

            # Clear tool list
            self.tools.clear()

            logger.info("✅ All MCP servers stopped")

        except Exception as e:
            logger.error(f"❌ Error stopping MCP servers: {e}")


# Global instance
_official_mcp_manager: Optional[OfficialMCPManager] = None


def get_official_mcp_manager() -> Optional[OfficialMCPManager]:
    """Get the global official MCP manager instance."""
    return _official_mcp_manager


async def start_official_mcp_system(app_config: Any) -> bool:
    """
    Start the official MCP system using langchain-mcp-adapters.

    Args:
        app_config: Main application configuration object

    Returns:
        bool: True if system started successfully
    """
    global _official_mcp_manager

    try:
        if _official_mcp_manager is None:
            # Convert MCPServerConfig objects to dictionaries for the manager
            server_configs = {}
            if hasattr(app_config, 'mcp') and app_config.mcp.enabled:
                for server_name, server_config in app_config.mcp.servers.items():
                    if server_config.enabled:
                        server_configs[server_name] = {
                            "command": server_config.command,
                            "args": server_config.args,
                            "env": server_config.env,
                            "timeout": server_config.timeout
                        }

            _official_mcp_manager = OfficialMCPManager(server_configs)

        success = await _official_mcp_manager.start_servers()

        if success:
            tool_count = _official_mcp_manager.get_tool_count()
            logger.info(f"🎉 Official MCP system started with {tool_count} tools")
            return True
        else:
            logger.warning("⚠️ Official MCP system failed to start")
            return False

    except Exception as e:
        logger.error(f"❌ Failed to start official MCP system: {e}")
        return False


async def stop_official_mcp_system() -> None:
    """Stop the official MCP system."""
    global _official_mcp_manager
    
    if _official_mcp_manager:
        await _official_mcp_manager.stop_servers()
        _official_mcp_manager = None


async def get_official_mcp_tools() -> List[LangChainBaseTool]:
    """
    Get all MCP tools using the official adapters.
    
    Returns:
        List of LangChain-compatible tools
    """
    manager = get_official_mcp_manager()
    if manager:
        return manager.get_tools()
    return []
