"""
MCP Tool Adapter for Jarvis Voice Assistant.

This module provides integration between MCP tools and the Jarvis tool system,
converting MCP tools to LangChain-compatible tools for use in conversations.
"""

import asyncio
import json
import logging
import concurrent.futures
from typing import Any, Dict, List, Optional, Callable
from langchain_core.tools import BaseTool as LangChainBaseTool, tool
from pydantic import BaseModel, Field

from .mcp_client import MCPClientManager, MCPTool

logger = logging.getLogger(__name__)


class MCPToolInput(BaseModel):
    """Input schema for MCP tools."""
    # Dynamic fields will be added based on MCP tool parameters
    pass


class MCPLangChainTool(LangChainBaseTool):
    """
    LangChain tool wrapper for MCP tools.

    This class adapts MCP tools to work with LangChain's agent system,
    handling async execution and parameter validation.
    """

    name: str = Field(description="Tool name")
    description: str = Field(description="Tool description")
    mcp_tool: MCPTool = Field(description="Underlying MCP tool")
    mcp_client: MCPClientManager = Field(description="MCP client manager")

    # Explicitly set this to support synchronous execution
    coroutine: Optional[Any] = None

    class Config:
        arbitrary_types_allowed = True
    
    def __init__(self, mcp_tool: MCPTool, mcp_client: MCPClientManager, **kwargs):
        """
        Initialize the MCP LangChain tool.
        
        Args:
            mcp_tool: The MCP tool to wrap
            mcp_client: MCP client manager for tool execution
            **kwargs: Additional arguments
        """
        # Create dynamic input schema based on MCP tool parameters
        input_schema = self._create_input_schema(mcp_tool)
        
        super().__init__(
            name=f"{mcp_tool.server_name}_{mcp_tool.name}",
            description=mcp_tool.description or f"Tool from {mcp_tool.server_name}",
            mcp_tool=mcp_tool,
            mcp_client=mcp_client,
            args_schema=input_schema,
            **kwargs
        )
    
    def _create_input_schema(self, mcp_tool: MCPTool) -> type:
        """
        Create a simple input schema that accepts any parameters.

        Args:
            mcp_tool: MCP tool to create schema for

        Returns:
            Pydantic model class for input validation
        """
        # Create a simple schema that accepts any keyword arguments
        # This avoids complex dynamic field creation that causes Pydantic issues

        class DynamicMCPInput(BaseModel):
            """Dynamic input schema for MCP tools."""

            class Config:
                extra = "allow"  # Allow any additional fields
                arbitrary_types_allowed = True

            def __init__(self, **data):
                # Accept any keyword arguments
                super().__init__(**data)

        # Set a unique name for the class
        model_name = f"{mcp_tool.name.replace('-', '_').replace(' ', '_')}Input"
        DynamicMCPInput.__name__ = model_name
        DynamicMCPInput.__qualname__ = model_name

        return DynamicMCPInput
    
    def _map_json_type_to_python(self, json_type: str) -> type:
        """
        Map JSON schema types to Python types.
        
        Args:
            json_type: JSON schema type string
            
        Returns:
            Python type
        """
        type_mapping = {
            "string": str,
            "integer": int,
            "number": float,
            "boolean": bool,
            "array": List[Any],
            "object": Dict[str, Any]
        }
        return type_mapping.get(json_type, str)
    
    def _run(self, **kwargs: Any) -> str:
        """
        Execute the MCP tool synchronously.

        Args:
            **kwargs: Tool parameters

        Returns:
            Tool execution result as string
        """
        try:
            logger.info(f"🔍 MCP TOOL DEBUG: _run called for tool '{self.name}' with args: {kwargs}")

            # Create a new event loop for synchronous execution
            try:
                # Try to get the current event loop
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    logger.info(f"🔍 MCP TOOL DEBUG: Event loop is running, using thread executor")
                    # If we're already in an event loop, run in a new thread
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        future = executor.submit(self._run_in_new_loop, **kwargs)
                        result = future.result(timeout=30)  # 30 second timeout
                else:
                    logger.info(f"🔍 MCP TOOL DEBUG: Event loop not running, using run_until_complete")
                    # Run directly in the existing loop
                    result = loop.run_until_complete(self._run_async(**kwargs))
            except RuntimeError as e:
                logger.info(f"🔍 MCP TOOL DEBUG: RuntimeError ({e}), creating new event loop")
                # No event loop exists, create a new one
                result = asyncio.run(self._run_async(**kwargs))

            logger.info(f"🔍 MCP TOOL DEBUG: Tool '{self.name}' execution successful, result: '{result[:200]}{'...' if len(result) > 200 else ''}'")
            return result

        except Exception as e:
            error_msg = f"Error executing MCP tool {self.name}: {str(e)}"
            logger.error(f"🔍 MCP TOOL DEBUG: Tool '{self.name}' execution failed: {error_msg}")
            logger.error(f"🔍 MCP TOOL DEBUG: Full exception: {e}", exc_info=True)
            return error_msg

    def _run_in_new_loop(self, **kwargs: Any) -> str:
        """Run the async method in a new event loop."""
        return asyncio.run(self._run_async(**kwargs))
    
    async def _run_async(self, **kwargs: Any) -> str:
        """
        Execute the MCP tool asynchronously.
        
        Args:
            **kwargs: Tool parameters
            
        Returns:
            Tool execution result as string
        """
        try:
            logger.info(f"🔍 MCP TOOL DEBUG: _run_async called for tool '{self.name}' with args: {kwargs}")

            # Execute the tool via MCP client
            tool_name = f"{self.mcp_tool.server_name}:{self.mcp_tool.name}"
            logger.info(f"🔍 MCP TOOL DEBUG: Calling MCP client for tool '{tool_name}'")

            # Check if MCP client is still connected
            if not hasattr(self.mcp_client, 'transports') or not self.mcp_client.transports:
                logger.error(f"🔍 MCP TOOL DEBUG: MCP client has no active transports")
                return "Error: MCP client connection lost"

            server_name = self.mcp_tool.server_name
            if server_name not in self.mcp_client.transports:
                logger.error(f"🔍 MCP TOOL DEBUG: Server '{server_name}' not in transports")
                return f"Error: Server {server_name} not connected"

            logger.info(f"🔍 MCP TOOL DEBUG: Server '{server_name}' transport found, executing tool")
            result = await self.mcp_client.execute_tool(tool_name, **kwargs)
            logger.info(f"🔍 MCP TOOL DEBUG: MCP client returned result type: {type(result)}")
            logger.info(f"🔍 MCP TOOL DEBUG: MCP client result: {result}")

            if "error" in result:
                error_result = f"Error: {result['error']}"
                logger.error(f"🔍 MCP TOOL DEBUG: Tool returned error: {error_result}")
                return error_result

            # Format result as string
            if isinstance(result, dict):
                # Try to extract meaningful content
                if "content" in result:
                    formatted_result = str(result["content"])
                    logger.info(f"🔍 MCP TOOL DEBUG: Extracted 'content': {formatted_result[:200]}{'...' if len(formatted_result) > 200 else ''}")
                    return formatted_result
                elif "text" in result:
                    formatted_result = str(result["text"])
                    logger.info(f"🔍 MCP TOOL DEBUG: Extracted 'text': {formatted_result[:200]}{'...' if len(formatted_result) > 200 else ''}")
                    return formatted_result
                elif "result" in result:
                    formatted_result = str(result["result"])
                    logger.info(f"🔍 MCP TOOL DEBUG: Extracted 'result': {formatted_result[:200]}{'...' if len(formatted_result) > 200 else ''}")
                    return formatted_result
                else:
                    formatted_result = json.dumps(result, indent=2)
                    logger.info(f"🔍 MCP TOOL DEBUG: Formatted as JSON: {formatted_result[:200]}{'...' if len(formatted_result) > 200 else ''}")
                    return formatted_result
            else:
                formatted_result = str(result)
                logger.info(f"🔍 MCP TOOL DEBUG: Formatted as string: {formatted_result[:200]}{'...' if len(formatted_result) > 200 else ''}")
                return formatted_result

        except Exception as e:
            error_msg = f"Error executing MCP tool: {str(e)}"
            logger.error(f"🔍 MCP TOOL DEBUG: _run_async failed for tool '{self.name}': {error_msg}")
            logger.error(f"🔍 MCP TOOL DEBUG: Full exception: {e}", exc_info=True)
            return error_msg


class MCPToolManager:
    """
    Manages MCP tools and their integration with Jarvis.
    
    This class handles the lifecycle of MCP tools, converting them to
    LangChain-compatible tools and managing their availability.
    """
    
    def __init__(self, mcp_client: MCPClientManager):
        """
        Initialize the MCP tool manager.

        Args:
            mcp_client: MCP client manager instance
        """
        self.mcp_client = mcp_client
        self.langchain_tools: Dict[str, MCPLangChainTool] = {}
        self.tool_update_callbacks = []  # Callbacks to notify when tools change

        # Set up callbacks for tool updates
        self.mcp_client.on_tools_updated = self._on_tools_updated

        logger.info("MCP Tool Manager initialized")
    
    def _on_tools_updated(self, mcp_tools: List[MCPTool]) -> None:
        """
        Handle MCP tool updates.
        
        Args:
            mcp_tools: Updated list of MCP tools
        """
        try:
            # Clear existing tools
            self.langchain_tools.clear()
            
            # Convert MCP tools to LangChain tools
            for mcp_tool in mcp_tools:
                if mcp_tool.enabled:
                    try:
                        langchain_tool = MCPLangChainTool(mcp_tool, self.mcp_client)
                        self.langchain_tools[langchain_tool.name] = langchain_tool
                        logger.debug(f"Converted MCP tool to LangChain: {langchain_tool.name}")
                    except Exception as e:
                        logger.error(f"Failed to convert MCP tool {mcp_tool.name}: {e}")
            
            logger.info(f"✅ Updated MCP tools: {len(self.langchain_tools)} tools available")

            # Log tool names for debugging
            if self.langchain_tools:
                tool_names = [tool.name for tool in self.langchain_tools.values()]
                logger.debug(f"   Available MCP tools: {', '.join(tool_names)}")

            # Notify callbacks about tool updates
            self._notify_tool_update_callbacks()

        except Exception as e:
            logger.error(f"Error updating MCP tools: {e}")
    
    def get_langchain_tools(self) -> List[LangChainBaseTool]:
        """
        Get all MCP tools as LangChain-compatible tools.
        
        Returns:
            List of LangChain tools
        """
        return list(self.langchain_tools.values())
    
    def get_tool_by_name(self, tool_name: str) -> Optional[MCPLangChainTool]:
        """
        Get a specific MCP tool by name.
        
        Args:
            tool_name: Name of the tool to retrieve
            
        Returns:
            MCP LangChain tool or None if not found
        """
        return self.langchain_tools.get(tool_name)
    
    def refresh_tools(self) -> None:
        """Refresh MCP tools from all connected servers."""
        try:
            # Trigger tool discovery on all connected servers
            for server_name in self.mcp_client.get_all_servers():
                server_info = self.mcp_client.get_server_info(server_name)
                if server_info and server_info.status.value == "connected":
                    # Reconnect to refresh tools
                    if self.mcp_client.event_loop:
                        asyncio.run_coroutine_threadsafe(
                            self.mcp_client._discover_tools(server_name),
                            self.mcp_client.event_loop
                        )
            
            logger.info("Refreshed MCP tools from all servers")
            
        except Exception as e:
            logger.error(f"Error refreshing MCP tools: {e}")
    
    def get_tool_count(self) -> int:
        """
        Get the number of available MCP tools.

        Returns:
            Number of available tools
        """
        return len(self.langchain_tools)

    def add_tool_update_callback(self, callback: Callable[[], None]) -> None:
        """
        Add a callback to be notified when MCP tools are updated.

        Args:
            callback: Function to call when tools are updated
        """
        self.tool_update_callbacks.append(callback)
        logger.debug("Added tool update callback")

    def _notify_tool_update_callbacks(self) -> None:
        """Notify all registered callbacks about tool updates."""
        logger.info(f"🔄 Notifying {len(self.tool_update_callbacks)} callbacks about MCP tool updates")
        for callback in self.tool_update_callbacks:
            try:
                callback()
                logger.debug("✅ Tool update callback executed successfully")
            except Exception as e:
                logger.error(f"❌ Error in tool update callback: {e}")
    
    def get_server_tool_count(self, server_name: str) -> int:
        """
        Get the number of tools from a specific server.
        
        Args:
            server_name: Name of the MCP server
            
        Returns:
            Number of tools from the server
        """
        count = 0
        for tool in self.langchain_tools.values():
            if tool.mcp_tool.server_name == server_name:
                count += 1
        return count
    
    def is_tool_enabled(self, tool_name: str) -> bool:
        """
        Check if a tool is enabled.
        
        Args:
            tool_name: Name of the tool to check
            
        Returns:
            True if tool is enabled, False otherwise
        """
        tool = self.langchain_tools.get(tool_name)
        return tool is not None and tool.mcp_tool.enabled
    
    def enable_tool(self, tool_name: str) -> bool:
        """
        Enable a specific MCP tool.
        
        Args:
            tool_name: Name of the tool to enable
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Find the MCP tool and enable it
            for mcp_tool in self.mcp_client.get_all_tools():
                if f"{mcp_tool.server_name}_{mcp_tool.name}" == tool_name:
                    mcp_tool.enabled = True
                    # Recreate LangChain tool
                    langchain_tool = MCPLangChainTool(mcp_tool, self.mcp_client)
                    self.langchain_tools[tool_name] = langchain_tool
                    logger.info(f"Enabled MCP tool: {tool_name}")
                    return True
            
            logger.warning(f"MCP tool not found: {tool_name}")
            return False
            
        except Exception as e:
            logger.error(f"Error enabling MCP tool {tool_name}: {e}")
            return False
    
    def disable_tool(self, tool_name: str) -> bool:
        """
        Disable a specific MCP tool.
        
        Args:
            tool_name: Name of the tool to disable
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Find the MCP tool and disable it
            for mcp_tool in self.mcp_client.get_all_tools():
                if f"{mcp_tool.server_name}_{mcp_tool.name}" == tool_name:
                    mcp_tool.enabled = False
                    # Remove from LangChain tools
                    if tool_name in self.langchain_tools:
                        del self.langchain_tools[tool_name]
                    logger.info(f"Disabled MCP tool: {tool_name}")
                    return True
            
            logger.warning(f"MCP tool not found: {tool_name}")
            return False
            
        except Exception as e:
            logger.error(f"Error disabling MCP tool {tool_name}: {e}")
            return False
