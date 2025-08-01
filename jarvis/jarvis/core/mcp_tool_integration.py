"""
MCP Tool Integration for Jarvis Voice Assistant.

This module integrates MCP servers as LangChain tools, allowing Jarvis to use
external MCP servers seamlessly through the agent system.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

from .mcp_client import get_mcp_client, MCPClient
from .mcp_config_manager import get_mcp_config_manager

logger = logging.getLogger(__name__)


class MCPToolInput(BaseModel):
    """Input schema for MCP tools."""
    arguments: Dict[str, Any] = Field(default_factory=dict, description="Arguments to pass to the MCP tool")


class MCPTool(BaseTool):
    """LangChain tool wrapper for MCP server tools."""
    
    name: str
    description: str
    server_id: str
    tool_name: str
    mcp_client: MCPClient
    args_schema: type[BaseModel] = MCPToolInput
    
    def __init__(self, server_id: str, tool_name: str, tool_info: Dict[str, Any], mcp_client: MCPClient):
        """Initialize MCP tool wrapper."""
        super().__init__(
            name=f"mcp_{server_id}_{tool_name}",
            description=tool_info.get("description", f"MCP tool: {tool_name}"),
            server_id=server_id,
            tool_name=tool_name,
            mcp_client=mcp_client
        )
    
    def _run(self, arguments: Dict[str, Any] = None) -> str:
        """Run the MCP tool synchronously."""
        if arguments is None:
            arguments = {}

        try:
            # Check if we're already in an event loop
            try:
                loop = asyncio.get_running_loop()
                # We're in an event loop, use asyncio.create_task or run in thread
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(self._run_in_new_loop, arguments)
                    result = future.result(timeout=30)
                    return result
            except RuntimeError:
                # No event loop running, safe to create one
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    result = loop.run_until_complete(self._arun(arguments))
                    return result
                finally:
                    loop.close()
        except Exception as e:
            logger.error(f"Error running MCP tool {self.name}: {e}")
            return f"Error: {str(e)}"

    def _run_in_new_loop(self, arguments: Dict[str, Any]) -> str:
        """Run the async method in a new event loop (for thread execution)."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(self._arun(arguments))
            return result
        finally:
            loop.close()
    
    async def _arun(self, arguments: Dict[str, Any] = None) -> str:
        """Run the MCP tool asynchronously."""
        if arguments is None:
            arguments = {}
        
        try:
            result = await self.mcp_client.call_tool(self.server_id, self.tool_name, arguments)
            
            if result is None:
                return f"No response from MCP tool {self.tool_name}"
            
            # Extract text content from MCP response
            if "content" in result:
                content_items = result["content"]
                if isinstance(content_items, list) and len(content_items) > 0:
                    first_item = content_items[0]
                    if isinstance(first_item, dict) and "text" in first_item:
                        return first_item["text"]
            
            # Fallback: return string representation
            return str(result)
            
        except Exception as e:
            logger.error(f"Error running MCP tool {self.name}: {e}")
            return f"Error: {str(e)}"


class MCPToolManager:
    """Manages MCP tools and their integration with Jarvis."""
    
    def __init__(self):
        self.mcp_client = get_mcp_client()
        self.config_manager = get_mcp_config_manager()
        self.mcp_tools: List[MCPTool] = []
        self._initialized = False
    
    async def initialize(self) -> bool:
        """Initialize MCP tool manager and connect to servers."""
        try:
            logger.info("Initializing MCP tool manager...")
            
            # Set config manager for MCP client
            self.mcp_client.set_config_manager(self.config_manager)
            
            # Connect to all enabled MCP servers
            connection_results = await self.mcp_client.connect_all_servers()
            
            successful_connections = sum(1 for success in connection_results.values() if success)
            total_servers = len(connection_results)
            
            logger.info(f"Connected to {successful_connections}/{total_servers} MCP servers")
            
            # Load tools from connected servers
            await self._load_mcp_tools()
            
            self._initialized = True
            return successful_connections > 0
            
        except Exception as e:
            logger.error(f"Error initializing MCP tool manager: {e}")
            return False
    
    async def _load_mcp_tools(self) -> None:
        """Load tools from all connected MCP servers."""
        try:
            self.mcp_tools.clear()
            
            # Get all tools from connected servers
            all_tools = self.mcp_client.get_all_tools()
            
            for tool_info in all_tools:
                try:
                    server_id = tool_info.get("_mcp_server")
                    tool_name = tool_info.get("name")
                    
                    if not server_id or not tool_name:
                        logger.warning(f"Invalid tool info: {tool_info}")
                        continue
                    
                    # Create LangChain tool wrapper
                    mcp_tool = MCPTool(
                        server_id=server_id,
                        tool_name=tool_name,
                        tool_info=tool_info,
                        mcp_client=self.mcp_client
                    )
                    
                    self.mcp_tools.append(mcp_tool)
                    logger.info(f"Loaded MCP tool: {mcp_tool.name}")
                    
                except Exception as e:
                    logger.error(f"Error creating MCP tool wrapper: {e}")
            
            logger.info(f"Loaded {len(self.mcp_tools)} MCP tools total")
            
        except Exception as e:
            logger.error(f"Error loading MCP tools: {e}")
    
    def get_langchain_tools(self) -> List[BaseTool]:
        """Get all MCP tools as LangChain tools."""
        return self.mcp_tools.copy()
    
    async def refresh_tools(self) -> bool:
        """Refresh tools from MCP servers."""
        try:
            logger.info("Refreshing MCP tools...")
            await self._load_mcp_tools()
            return True
        except Exception as e:
            logger.error(f"Error refreshing MCP tools: {e}")
            return False
    
    def get_tool_by_name(self, tool_name: str) -> Optional[MCPTool]:
        """Get an MCP tool by name."""
        for tool in self.mcp_tools:
            if tool.name == tool_name:
                return tool
        return None
    
    def get_tools_by_server(self, server_id: str) -> List[MCPTool]:
        """Get all tools from a specific MCP server."""
        return [tool for tool in self.mcp_tools if tool.server_id == server_id]
    
    def get_server_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all MCP servers."""
        return self.mcp_client.get_connection_status()
    
    async def add_server_and_refresh(self, server_config) -> bool:
        """Add a new MCP server and refresh tools."""
        try:
            # Add server to config
            success = self.config_manager.add_server(server_config)
            if not success:
                return False
            
            # Reconnect to all servers (including new one)
            connection_results = await self.mcp_client.connect_all_servers()
            
            # Refresh tools
            await self._load_mcp_tools()
            
            return True
            
        except Exception as e:
            logger.error(f"Error adding server and refreshing tools: {e}")
            return False
    
    def is_initialized(self) -> bool:
        """Check if MCP tool manager is initialized."""
        return self._initialized
    
    def cleanup(self) -> None:
        """Clean up MCP tool manager."""
        logger.info("Cleaning up MCP tool manager...")
        self.mcp_client.disconnect_all()
        self.mcp_tools.clear()
        self._initialized = False


# Global MCP tool manager instance
_mcp_tool_manager = None


def get_mcp_tool_manager() -> MCPToolManager:
    """Get the global MCP tool manager instance."""
    global _mcp_tool_manager
    if _mcp_tool_manager is None:
        _mcp_tool_manager = MCPToolManager()
    return _mcp_tool_manager


async def initialize_mcp_tools() -> List[BaseTool]:
    """Initialize MCP tools and return them as LangChain tools."""
    try:
        mcp_manager = get_mcp_tool_manager()
        success = await mcp_manager.initialize()
        
        if success:
            tools = mcp_manager.get_langchain_tools()
            logger.info(f"Successfully initialized {len(tools)} MCP tools")
            return tools
        else:
            logger.warning("No MCP servers connected, returning empty tool list")
            return []
            
    except Exception as e:
        logger.error(f"Error initializing MCP tools: {e}")
        return []
