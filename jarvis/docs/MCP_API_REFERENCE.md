# MCP API Reference

## Overview

This document provides a comprehensive reference for the MCP (Model Context Protocol) integration API in Jarvis Voice Assistant.

## Core Classes

### MCPClientManager

Main class for managing MCP server connections and operations.

```python
from jarvis.core.mcp_client import MCPClientManager

# Initialize
client = MCPClientManager(config_file=Path("~/.jarvis/mcp_servers.json"))

# Start the client system
client.start()

# Add a server
config = MCPServerConfig(...)
success = client.add_server(config)

# Connect to server
await client.connect_server("server_name")

# Execute tool
result = await client.execute_tool("server:tool_name", param1="value1")

# Stop the client system
client.stop()
```

#### Methods

##### `start() -> None`
Starts the MCP client manager and background event loop.

##### `stop() -> None`
Stops the MCP client manager and cleans up resources.

##### `add_server(config: MCPServerConfig) -> bool`
Adds a new MCP server configuration.

**Parameters:**
- `config`: MCPServerConfig instance with server details

**Returns:** `True` if successful, `False` otherwise

##### `remove_server(server_name: str) -> bool`
Removes an MCP server configuration.

**Parameters:**
- `server_name`: Name of the server to remove

**Returns:** `True` if successful, `False` otherwise

##### `async connect_server(server_name: str) -> bool`
Connects to an MCP server.

**Parameters:**
- `server_name`: Name of the server to connect to

**Returns:** `True` if connection successful, `False` otherwise

##### `async disconnect_server(server_name: str) -> None`
Disconnects from an MCP server.

**Parameters:**
- `server_name`: Name of the server to disconnect from

##### `get_server_info(server_name: str) -> Optional[MCPServerInfo]`
Gets information about a specific server.

**Parameters:**
- `server_name`: Name of the server

**Returns:** MCPServerInfo instance or None if not found

##### `get_all_servers() -> Dict[str, MCPServerInfo]`
Gets information about all configured servers.

**Returns:** Dictionary mapping server names to MCPServerInfo instances

##### `get_all_tools() -> List[MCPTool]`
Gets all discovered tools from all servers.

**Returns:** List of MCPTool instances

##### `async execute_tool(tool_name: str, **kwargs) -> Dict[str, Any]`
Executes a tool on the appropriate MCP server.

**Parameters:**
- `tool_name`: Full tool name in format "server:tool"
- `**kwargs`: Tool parameters

**Returns:** Tool execution result dictionary

### MCPServerConfig

Configuration class for MCP servers.

```python
from jarvis.core.mcp_client import MCPServerConfig, MCPTransportType

# STDIO configuration
config = MCPServerConfig(
    name="github-server",
    transport=MCPTransportType.STDIO,
    command="npx",
    args=["-m", "@modelcontextprotocol/server-github"],
    env={"GITHUB_TOKEN": "your_token"},
    enabled=True
)

# HTTP/SSE configuration
config = MCPServerConfig(
    name="web-server",
    transport=MCPTransportType.SSE,
    url="https://api.example.com/mcp",
    headers={"Authorization": "Bearer token"},
    timeout=30,
    enabled=True
)
```

#### Fields

- `name: str` - Unique server name
- `transport: MCPTransportType` - Transport type (STDIO, SSE, WEBSOCKET)
- `enabled: bool` - Whether server is enabled (default: True)
- `command: Optional[str]` - Command for STDIO transport
- `args: List[str]` - Command arguments for STDIO transport
- `env: Dict[str, str]` - Environment variables for STDIO transport
- `cwd: Optional[str]` - Working directory for STDIO transport
- `url: Optional[str]` - URL for HTTP/WebSocket transports
- `headers: Dict[str, str]` - Headers for HTTP/WebSocket transports
- `timeout: int` - Connection timeout in seconds (default: 30)

#### Methods

##### `validate() -> None`
Validates the server configuration.

**Raises:** `ValueError` if configuration is invalid

### MCPTool

Represents a tool discovered from an MCP server.

```python
from jarvis.core.mcp_client import MCPTool

tool = MCPTool(
    name="list_repos",
    description="List GitHub repositories",
    server_name="github",
    parameters={"type": "object", "properties": {...}},
    enabled=True
)
```

#### Fields

- `name: str` - Tool name
- `description: str` - Tool description
- `server_name: str` - Name of the server providing this tool
- `parameters: Dict[str, Any]` - JSON schema for tool parameters
- `enabled: bool` - Whether tool is enabled (default: True)
- `metadata: Dict[str, Any]` - Additional tool metadata

### MCPToolManager

Manages MCP tools and their integration with Jarvis.

```python
from jarvis.core.mcp_tool_adapter import MCPToolManager

# Initialize with MCP client
tool_manager = MCPToolManager(mcp_client)

# Get LangChain-compatible tools
langchain_tools = tool_manager.get_langchain_tools()

# Enable/disable tools
tool_manager.enable_tool("server_tool_name")
tool_manager.disable_tool("server_tool_name")

# Refresh tools from servers
tool_manager.refresh_tools()
```

#### Methods

##### `get_langchain_tools() -> List[LangChainBaseTool]`
Gets all MCP tools as LangChain-compatible tools.

**Returns:** List of LangChain tool instances

##### `get_tool_by_name(tool_name: str) -> Optional[MCPLangChainTool]`
Gets a specific MCP tool by name.

**Parameters:**
- `tool_name`: Name of the tool to retrieve

**Returns:** MCPLangChainTool instance or None if not found

##### `enable_tool(tool_name: str) -> bool`
Enables a specific MCP tool.

**Parameters:**
- `tool_name`: Name of the tool to enable

**Returns:** `True` if successful, `False` otherwise

##### `disable_tool(tool_name: str) -> bool`
Disables a specific MCP tool.

**Parameters:**
- `tool_name`: Name of the tool to disable

**Returns:** `True` if successful, `False` otherwise

##### `refresh_tools() -> None`
Refreshes MCP tools from all connected servers.

##### `get_tool_count() -> int`
Gets the number of available MCP tools.

**Returns:** Number of available tools

## Configuration Management

### MCPConfigManager

Handles secure storage and retrieval of MCP server configurations.

```python
from jarvis.core.mcp_config import MCPConfigManager

# Initialize with password for encryption
config_manager = MCPConfigManager("your_password")

# Save configurations
configs = {"server1": config1, "server2": config2}
config_manager.save_servers(configs)

# Load configurations
loaded_configs = config_manager.load_servers()

# Backup and restore
config_manager.backup_config("backup.json")
config_manager.restore_config("backup.json")
```

#### Methods

##### `save_servers(servers: Dict[str, MCPServerConfig]) -> None`
Saves server configurations with encryption.

**Parameters:**
- `servers`: Dictionary mapping server names to configurations

##### `load_servers() -> Dict[str, MCPServerConfig]`
Loads server configurations with decryption.

**Returns:** Dictionary of server configurations

##### `backup_config(backup_path: str) -> None`
Creates a backup of the configuration file.

**Parameters:**
- `backup_path`: Path for backup file

##### `restore_config(backup_path: str) -> None`
Restores configuration from backup file.

**Parameters:**
- `backup_path`: Path to backup file

## Template System

### Server Templates

Pre-configured templates for popular MCP servers.

```python
from jarvis.core.mcp_templates import get_all_templates, get_template, create_config_from_template

# Get all available templates
templates = get_all_templates()

# Get specific template
github_template = get_template("github")

# Create configuration from template
config = create_config_from_template(
    "github", 
    custom_name="my-github",
    env={"GITHUB_TOKEN": "my_token"}
)
```

#### Available Templates

- `github` - GitHub Integration
- `filesystem` - File System Access
- `brave_search` - Brave Search
- `memory` - Memory Storage
- `sqlite` - SQLite Database
- `google_drive` - Google Drive
- `slack` - Slack Integration
- `postgres` - PostgreSQL Database
- `puppeteer` - Web Automation
- `everything` - Everything Search (Windows)

#### Functions

##### `get_all_templates() -> Dict[str, MCPServerTemplate]`
Gets all available server templates.

**Returns:** Dictionary mapping template names to MCPServerTemplate instances

##### `get_template(template_name: str) -> MCPServerTemplate`
Gets a specific server template.

**Parameters:**
- `template_name`: Name of the template

**Returns:** MCPServerTemplate instance or None if not found

##### `create_config_from_template(template_name: str, custom_name: str = None, **overrides) -> MCPServerConfig`
Creates a server configuration from a template.

**Parameters:**
- `template_name`: Name of the template to use
- `custom_name`: Custom name for the server (optional)
- `**overrides`: Configuration overrides

**Returns:** MCPServerConfig instance

## Integration Functions

### Tool System Integration

Functions for integrating MCP with the existing Jarvis tool system.

```python
from jarvis.tools import (
    get_langchain_tools,
    get_mcp_client,
    get_mcp_tool_manager,
    start_mcp_system,
    stop_mcp_system
)

# Get all tools (built-in + plugins + MCP)
all_tools = get_langchain_tools()

# Access MCP components
mcp_client = get_mcp_client()
mcp_tool_manager = get_mcp_tool_manager()

# Control MCP system
start_mcp_system()
stop_mcp_system()
```

#### Functions

##### `get_langchain_tools() -> List[LangChainBaseTool]`
Gets all available LangChain tools from built-in, plugins, and MCP servers.

**Returns:** Combined list of all tools

##### `get_mcp_client() -> MCPClientManager`
Gets the global MCP client manager instance.

**Returns:** MCPClientManager instance

##### `get_mcp_tool_manager() -> MCPToolManager`
Gets the global MCP tool manager instance.

**Returns:** MCPToolManager instance

##### `start_mcp_system() -> bool`
Starts the MCP client system.

**Returns:** `True` if successful, `False` otherwise

##### `stop_mcp_system() -> bool`
Stops the MCP client system.

**Returns:** `True` if successful, `False` otherwise

## HTTP API Endpoints

### Server Management

#### GET /api/mcp/servers
Gets information about all MCP servers.

**Response:**
```json
{
  "servers": {
    "server_name": {
      "config": {
        "name": "server_name",
        "transport": "stdio",
        "command": "npx",
        "args": ["-m", "@modelcontextprotocol/server-github"],
        "enabled": true
      },
      "status": "connected",
      "tools": [
        {
          "name": "list_repos",
          "description": "List repositories",
          "enabled": true
        }
      ],
      "last_error": null,
      "connected_at": 1640995200.0
    }
  }
}
```

#### POST /api/mcp/servers
Manages MCP servers (add, remove, test).

**Request Body:**
```json
{
  "action": "add|remove|test",
  "name": "server_name",
  "transport": "stdio|sse|websocket",
  "command": "npx",
  "args": ["-m", "@modelcontextprotocol/server-github"],
  "env": {"GITHUB_TOKEN": "token"},
  "url": "https://api.example.com/mcp",
  "headers": {"Authorization": "Bearer token"},
  "timeout": 30,
  "enabled": true
}
```

**Response:**
```json
{
  "success": true,
  "message": "Server added successfully"
}
```

### Tool Management

#### GET /api/mcp/tools
Gets information about all discovered MCP tools.

**Response:**
```json
{
  "tools": {
    "server:tool_name": {
      "name": "tool_name",
      "description": "Tool description",
      "server_name": "server",
      "enabled": true,
      "parameters": {
        "type": "object",
        "properties": {...}
      }
    }
  }
}
```

#### POST /api/mcp/tools/toggle
Enables or disables a specific tool.

**Request Body:**
```json
{
  "tool": "server:tool_name",
  "enabled": true
}
```

**Response:**
```json
{
  "success": true,
  "message": "Tool enabled"
}
```

### Connection Management

#### POST /api/mcp/connect
Connects to an MCP server.

**Request Body:**
```json
{
  "server": "server_name"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Connected to server_name"
}
```

#### POST /api/mcp/disconnect
Disconnects from an MCP server.

**Request Body:**
```json
{
  "server": "server_name"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Disconnected from server_name"
}
```

## Error Handling

### Exception Types

- `MCPError` - Base MCP exception
- `MCPConnectionError` - Connection-related errors
- `MCPConfigurationError` - Configuration validation errors
- `MCPToolExecutionError` - Tool execution errors

### Error Response Format

```json
{
  "success": false,
  "error": "Error message",
  "details": "Additional error details"
}
```

## Examples

### Complete Server Setup

```python
from jarvis.core.mcp_client import MCPClientManager, MCPServerConfig, MCPTransportType

# Initialize client
client = MCPClientManager()
client.start()

# Create server configuration
config = MCPServerConfig(
    name="github-integration",
    transport=MCPTransportType.STDIO,
    command="npx",
    args=["-m", "@modelcontextprotocol/server-github"],
    env={"GITHUB_TOKEN": "your_github_token"},
    enabled=True
)

# Add and connect server
client.add_server(config)
await client.connect_server("github-integration")

# Execute tool
result = await client.execute_tool(
    "github-integration:list_repos",
    owner="username"
)

print(result)
```

### Using Templates

```python
from jarvis.core.mcp_templates import create_config_from_template

# Create GitHub server from template
config = create_config_from_template(
    "github",
    custom_name="my-github-server",
    env={"GITHUB_TOKEN": "your_token_here"}
)

# Add to client
client.add_server(config)
```
