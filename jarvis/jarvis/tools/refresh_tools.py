"""
Tool to manually refresh and list available tools.
"""

from .base import BaseTool, ToolResult
from typing import Dict, Any


class RefreshToolsTool(BaseTool):
    """Tool to refresh and list all available tools."""

    def __init__(self):
        super().__init__(
            name="refresh_tools",
            description="Refresh the tool list and show all available tools including MCP tools"
        )

    def get_parameters(self) -> Dict[str, Any]:
        """
        Get the parameters schema for this tool.

        Returns:
            Dict[str, Any]: Empty parameters schema since this tool takes no arguments
        """
        return {
            "type": "object",
            "properties": {},
            "required": []
        }
    
    def execute(self, **kwargs) -> ToolResult:
        """
        Refresh tools and return the current tool list.
        
        Returns:
            ToolResult with the list of available tools
        """
        try:
            # Import here to avoid circular imports
            from . import get_langchain_tools
            
            # Get all current tools
            all_tools = get_langchain_tools()
            
            # Create tool summary
            tool_list = []
            builtin_count = 0
            mcp_count = 0
            
            for i, tool in enumerate(all_tools, 1):
                tool_list.append(f"{i}. {tool.name}")
                if "Memory Storage_" in tool.name:
                    mcp_count += 1
                else:
                    builtin_count += 1
            
            summary = f"""🛠️ Tool Refresh Complete!

📊 Summary:
   • Total Tools: {len(all_tools)}
   • Built-in Tools: {builtin_count}
   • MCP Memory Tools: {mcp_count}

📋 Available Tools:
{chr(10).join(tool_list)}

✅ All tools are now available for use!"""
            
            return ToolResult(
                success=True,
                message=summary,
                data={
                    "total_tools": len(all_tools),
                    "builtin_tools": builtin_count,
                    "mcp_tools": mcp_count,
                    "tool_names": [tool.name for tool in all_tools]
                }
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                message=f"Failed to refresh tools: {str(e)}",
                data={"error": str(e)}
            )
