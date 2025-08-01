#!/usr/bin/env python3
"""
MCP Time Server for Jarvis Voice Assistant.

This is an external MCP server that provides time-related tools.
It runs as a separate process and communicates with Jarvis via MCP protocol.
"""

import json
import sys
import asyncio
from datetime import datetime
from typing import Dict, Any, List


class MCPTimeServer:
    """MCP server providing time-related tools."""
    
    def __init__(self):
        self.tools = [
            {
                "name": "get_current_time",
                "description": "Get the current time in 12-hour format",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "get_current_date",
                "description": "Get the current date",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "get_datetime_info",
                "description": "Get detailed date and time information",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "format": {
                            "type": "string",
                            "description": "Optional format string for datetime",
                            "default": "%I:%M %p on %A, %B %d, %Y"
                        }
                    },
                    "required": []
                }
            }
        ]
    
    def get_current_time(self, arguments: Dict[str, Any]) -> str:
        """Get current time in 12-hour format."""
        now = datetime.now()
        return now.strftime("%I:%M %p").lstrip('0')
    
    def get_current_date(self, arguments: Dict[str, Any]) -> str:
        """Get current date."""
        now = datetime.now()
        return now.strftime("%A, %B %d, %Y")
    
    def get_datetime_info(self, arguments: Dict[str, Any]) -> str:
        """Get detailed date and time information."""
        now = datetime.now()
        format_str = arguments.get("format", "%I:%M %p on %A, %B %d, %Y")
        try:
            return now.strftime(format_str).lstrip('0')
        except ValueError:
            # Fallback to default format if custom format is invalid
            return now.strftime("%I:%M %p on %A, %B %d, %Y").lstrip('0')
    
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming MCP requests."""
        method = request.get("method")
        params = request.get("params", {})
        request_id = request.get("id")
        
        try:
            if method == "initialize":
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {
                            "tools": {"listChanged": True}
                        },
                        "serverInfo": {
                            "name": "jarvis-time-server",
                            "version": "1.0.0"
                        }
                    }
                }
            
            elif method == "tools/list":
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "tools": self.tools
                    }
                }
            
            elif method == "tools/call":
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                
                if tool_name == "get_current_time":
                    result = self.get_current_time(arguments)
                elif tool_name == "get_current_date":
                    result = self.get_current_date(arguments)
                elif tool_name == "get_datetime_info":
                    result = self.get_datetime_info(arguments)
                else:
                    return {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "error": {
                            "code": -32601,
                            "message": f"Unknown tool: {tool_name}"
                        }
                    }
                
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": result
                            }
                        ]
                    }
                }
            
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32601,
                        "message": f"Unknown method: {method}"
                    }
                }
        
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }
    
    async def run(self):
        """Run the MCP server."""
        print("🕐 Jarvis Time Server starting...", file=sys.stderr)
        
        while True:
            try:
                # Read request from stdin
                line = await asyncio.get_event_loop().run_in_executor(
                    None, sys.stdin.readline
                )
                
                if not line:
                    break
                
                # Parse JSON request
                try:
                    request = json.loads(line.strip())
                except json.JSONDecodeError:
                    continue
                
                # Handle request
                response = await self.handle_request(request)
                
                # Send response to stdout
                print(json.dumps(response), flush=True)
                
            except Exception as e:
                print(f"❌ Error in time server: {e}", file=sys.stderr)
                break
        
        print("🕐 Jarvis Time Server shutting down...", file=sys.stderr)


async def main():
    """Main entry point."""
    server = MCPTimeServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
