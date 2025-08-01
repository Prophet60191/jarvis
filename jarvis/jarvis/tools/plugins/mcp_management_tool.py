"""
MCP Management Tool Plugin for Jarvis Voice Assistant.

This plugin provides voice commands for managing MCP (Model Context Protocol) servers,
allowing users to add, remove, enable, disable, and list MCP servers through voice commands.
"""

import logging
import sys
from pathlib import Path
from typing import List, Dict, Any
from langchain_core.tools import tool

# Add the correct path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))
from plugins.base import PluginBase, PluginMetadata

# Import MCP configuration manager
try:
    from jarvis.core.mcp_config_manager import get_mcp_config_manager, MCPServerConfig, MCPTransportType
    from jarvis.core.mcp_templates import MCP_SERVER_TEMPLATES
    MCP_AVAILABLE = True
except ImportError as e:
    try:
        # Fallback for relative imports
        from core.mcp_config_manager import get_mcp_config_manager, MCPServerConfig, MCPTransportType
        from core.mcp_templates import MCP_SERVER_TEMPLATES
        MCP_AVAILABLE = True
    except ImportError as e2:
        MCP_AVAILABLE = False
        MCP_ERROR = f"MCP imports failed: {e}, {e2}"

logger = logging.getLogger(__name__)


@tool
def add_mcp_server_from_template(template_name: str, custom_args: str = "") -> str:
    """
    Add an MCP server using a predefined template.
    
    Use this when user asks to:
    - "Add filesystem MCP server"
    - "Connect to GitHub MCP"
    - "Set up file system access"
    - "Add memory storage MCP"
    - "Connect web search MCP"
    
    Args:
        template_name: Name of the template (filesystem, github, brave_search, memory, etc.)
        custom_args: Optional custom arguments or environment variables
    
    Returns:
        Status message about adding the MCP server
    """
    if not MCP_AVAILABLE:
        return f"MCP system is not available: {MCP_ERROR}"
    
    try:
        mcp_manager = get_mcp_config_manager()
        
        # Normalize template name
        template_key = template_name.lower().replace(' ', '_').replace('-', '_')
        
        # Map common variations
        template_mapping = {
            'file': 'filesystem',
            'files': 'filesystem',
            'file_system': 'filesystem',
            'filesystem': 'filesystem',
            'github': 'github',
            'git': 'github',
            'search': 'brave_search',
            'web_search': 'brave_search',
            'brave': 'brave_search',
            'memory': 'memory',
            'storage': 'memory',
            'database': 'sqlite',
            'db': 'sqlite'
        }
        
        template_key = template_mapping.get(template_key, template_key)
        
        if template_key not in MCP_SERVER_TEMPLATES:
            available = ", ".join(MCP_SERVER_TEMPLATES.keys())
            return f"Template '{template_name}' not found. Available templates: {available}"
        
        template = MCP_SERVER_TEMPLATES[template_key]
        server_config = template.config
        
        # Apply custom arguments if provided
        if custom_args:
            # Simple parsing for custom arguments
            if "=" in custom_args:
                # Environment variable format: KEY=value
                key, value = custom_args.split("=", 1)
                if not server_config.env:
                    server_config.env = {}
                server_config.env[key.strip()] = value.strip()
            else:
                # Additional command argument
                server_config.args.append(custom_args.strip())
        
        # Add the server
        success = mcp_manager.add_server(server_config)
        
        if success:
            setup_info = ""
            if template.required_env_vars:
                setup_info = f"\n\nSetup required:\n{template.setup_instructions}"
            
            return f"✅ Successfully added MCP server '{template.name}' ({template_key}). {setup_info}"
        else:
            return f"❌ Failed to add MCP server '{template.name}'"
            
    except Exception as e:
        logger.error(f"Error adding MCP server from template: {e}")
        return f"Error adding MCP server: {str(e)}"


@tool
def list_mcp_servers() -> str:
    """
    List all configured MCP servers and their status.
    
    Use this when user asks to:
    - "List MCP servers"
    - "Show MCP status"
    - "What MCP servers are connected?"
    - "Show all MCP connections"
    
    Returns:
        List of all MCP servers with their status
    """
    if not MCP_AVAILABLE:
        return f"MCP system is not available: {MCP_ERROR}"
    
    try:
        mcp_manager = get_mcp_config_manager()
        servers = mcp_manager.get_all_servers()
        
        if not servers:
            return "📋 **No MCP servers configured**\n\n🚀 **Get Started:**\n• Say: 'Add filesystem MCP server' for file access\n• Say: 'Add GitHub MCP server' for repository management\n• Say: 'Add custom MCP server' for any MCP from mcpservers.org\n• Or open MCP settings in the UI to browse templates"

        server_list = []
        stats = mcp_manager.get_server_count()
        enabled_count = stats['enabled']
        total_count = stats['total']

        server_list.append(f"📋 **MCP Servers Status** ({total_count} total, {enabled_count} active)")
        server_list.append("=" * 60)
        server_list.append("")

        for server_id, config in servers.items():
            if config.enabled:
                status_emoji = "🟢"
                status_text = "Active"
            else:
                status_emoji = "🔴"
                status_text = "Disabled"

            server_list.append(f"{status_emoji} **{config.name}**")
            server_list.append(f"   📍 Status: {status_text}")
            server_list.append(f"   🔧 Command: `{config.command} {' '.join(config.args)}`")

            if config.description:
                server_list.append(f"   📝 Description: {config.description}")

            if config.env:
                env_count = len(config.env)
                has_secrets = any('token' in k.lower() or 'key' in k.lower() for k in config.env.keys())
                secret_indicator = " (includes API keys)" if has_secrets else ""
                server_list.append(f"   🔐 Environment: {env_count} variables{secret_indicator}")

            server_list.append(f"   ⏱️  Timeout: {config.timeout}s")
            server_list.append(f"   💬 Commands: 'Enable {config.name} MCP' | 'Edit {config.name} MCP' | 'Remove {config.name} MCP'")
            server_list.append("")

        # Add summary and tips
        server_list.append("📊 **Summary:**")
        if enabled_count == 0:
            server_list.append("💡 **Tip:** Enable servers with 'Enable [server name] MCP' to start using their tools!")
        elif enabled_count < total_count:
            server_list.append(f"💡 **Tip:** You have {total_count - enabled_count} disabled servers. Enable them to access more tools!")
        else:
            server_list.append("✨ **All servers are active!** You can now use their tools through voice commands.")

        return "\n".join(server_list)
        
    except Exception as e:
        logger.error(f"Error listing MCP servers: {e}")
        return f"Error listing MCP servers: {str(e)}"


@tool
def enable_mcp_server(server_name: str) -> str:
    """
    Enable an MCP server.
    
    Use this when user asks to:
    - "Enable filesystem MCP"
    - "Turn on GitHub MCP server"
    - "Activate memory storage"
    
    Args:
        server_name: Name or ID of the server to enable
    
    Returns:
        Status message about enabling the server
    """
    if not MCP_AVAILABLE:
        return f"MCP system is not available: {MCP_ERROR}"
    
    try:
        mcp_manager = get_mcp_config_manager()
        
        # Try to find server by name or ID
        server_id = server_name.lower().replace(' ', '_').replace('-', '_')
        servers = mcp_manager.get_all_servers()
        
        # Check if server exists
        if server_id not in servers:
            # Try to find by name
            for sid, config in servers.items():
                if config.name.lower() == server_name.lower():
                    server_id = sid
                    break
            else:
                available = ", ".join([config.name for config in servers.values()])
                return f"MCP server '{server_name}' not found. Available servers: {available}"
        
        success = mcp_manager.enable_server(server_id)
        
        if success:
            server_config = servers[server_id]
            return f"✅ Enabled MCP server '{server_config.name}' ({server_id})"
        else:
            return f"❌ Failed to enable MCP server '{server_name}'"
            
    except Exception as e:
        logger.error(f"Error enabling MCP server: {e}")
        return f"Error enabling MCP server: {str(e)}"


@tool
def disable_mcp_server(server_name: str) -> str:
    """
    Disable an MCP server.
    
    Use this when user asks to:
    - "Disable filesystem MCP"
    - "Turn off GitHub MCP server"
    - "Deactivate memory storage"
    
    Args:
        server_name: Name or ID of the server to disable
    
    Returns:
        Status message about disabling the server
    """
    if not MCP_AVAILABLE:
        return f"MCP system is not available: {MCP_ERROR}"
    
    try:
        mcp_manager = get_mcp_config_manager()
        
        # Try to find server by name or ID
        server_id = server_name.lower().replace(' ', '_').replace('-', '_')
        servers = mcp_manager.get_all_servers()
        
        # Check if server exists
        if server_id not in servers:
            # Try to find by name
            for sid, config in servers.items():
                if config.name.lower() == server_name.lower():
                    server_id = sid
                    break
            else:
                available = ", ".join([config.name for config in servers.values()])
                return f"MCP server '{server_name}' not found. Available servers: {available}"
        
        success = mcp_manager.disable_server(server_id)
        
        if success:
            server_config = servers[server_id]
            return f"✅ Disabled MCP server '{server_config.name}' ({server_id})"
        else:
            return f"❌ Failed to disable MCP server '{server_name}'"
            
    except Exception as e:
        logger.error(f"Error disabling MCP server: {e}")
        return f"Error disabling MCP server: {str(e)}"


@tool
def edit_mcp_server(server_name: str, field: str, new_value: str) -> str:
    """
    Edit an MCP server configuration field.

    Use this when user asks to:
    - "Edit filesystem MCP command"
    - "Change GitHub MCP environment variable"
    - "Update memory storage MCP arguments"
    - "Modify browser MCP timeout"

    Args:
        server_name: Name or ID of the server to edit
        field: Field to edit (command, args, env, timeout, description)
        new_value: New value for the field

    Returns:
        Status message about editing the server
    """
    if not MCP_AVAILABLE:
        return f"MCP system is not available: {MCP_ERROR}"

    try:
        mcp_manager = get_mcp_config_manager()

        # Try to find server by name or ID
        server_id = server_name.lower().replace(' ', '_').replace('-', '_')
        servers = mcp_manager.get_all_servers()

        # Check if server exists
        if server_id not in servers:
            # Try to find by name
            for sid, config in servers.items():
                if config.name.lower() == server_name.lower():
                    server_id = sid
                    break
            else:
                available = ", ".join([config.name for config in servers.values()])
                return f"MCP server '{server_name}' not found. Available servers: {available}"

        # Validate field
        allowed_fields = ['command', 'args', 'env', 'timeout', 'description']
        if field not in allowed_fields:
            return f"Cannot edit field '{field}'. Allowed fields: {', '.join(allowed_fields)}"

        # Prepare update
        updates = {}
        if field == 'args':
            # Parse args as list
            updates[field] = new_value.split() if new_value else []
        elif field == 'env':
            # Parse env as key=value
            if '=' in new_value:
                key, value = new_value.split('=', 1)
                server_config = servers[server_id]
                env = server_config.env or {}
                env[key] = value
                updates[field] = env
            else:
                return f"Environment variable must be in format 'KEY=VALUE'"
        elif field == 'timeout':
            # Parse timeout as integer
            try:
                updates[field] = int(new_value)
            except ValueError:
                return f"Timeout must be a number (seconds)"
        else:
            updates[field] = new_value

        success = mcp_manager.update_server(server_id, updates)

        if success:
            server_config = servers[server_id]
            return f"✅ Updated {field} for MCP server '{server_config.name}' ({server_id})"
        else:
            return f"❌ Failed to update MCP server '{server_name}'"

    except Exception as e:
        logger.error(f"Error editing MCP server: {e}")
        return f"Error editing MCP server: {str(e)}"


@tool
def remove_mcp_server(server_name: str) -> str:
    """
    Remove an MCP server configuration.
    
    Use this when user asks to:
    - "Remove filesystem MCP"
    - "Delete GitHub MCP server"
    - "Uninstall memory storage MCP"
    
    Args:
        server_name: Name or ID of the server to remove
    
    Returns:
        Status message about removing the server
    """
    if not MCP_AVAILABLE:
        return f"MCP system is not available: {MCP_ERROR}"
    
    try:
        mcp_manager = get_mcp_config_manager()
        
        # Try to find server by name or ID
        server_id = server_name.lower().replace(' ', '_').replace('-', '_')
        servers = mcp_manager.get_all_servers()
        
        # Check if server exists
        if server_id not in servers:
            # Try to find by name
            for sid, config in servers.items():
                if config.name.lower() == server_name.lower():
                    server_id = sid
                    break
            else:
                available = ", ".join([config.name for config in servers.values()])
                return f"MCP server '{server_name}' not found. Available servers: {available}"
        
        server_config = servers[server_id]
        success = mcp_manager.remove_server(server_id)
        
        if success:
            return f"✅ Removed MCP server '{server_config.name}' ({server_id})"
        else:
            return f"❌ Failed to remove MCP server '{server_name}'"
            
    except Exception as e:
        logger.error(f"Error removing MCP server: {e}")
        return f"Error removing MCP server: {str(e)}"


@tool
def open_tools_and_plugins_page() -> str:
    """
    Open the Tools & Plugins management page in the UI.

    Use this when user asks to:
    - "Open tools page"
    - "Show plugins"
    - "Manage tools and plugins"
    - "Open plugin manager"
    - "Show Jarvis tools"

    Returns:
        Status message about opening the page
    """
    try:
        import webbrowser
        import time

        # Try to open the tools page
        url = "http://localhost:8083/tools"
        webbrowser.open(url)

        return "✅ **Tools & Plugins page opened!**\n\n🔧 **What you can do:**\n• View all current Jarvis plugins\n• Add custom plugins with voice commands\n• Edit existing plugin configurations\n• Delete plugins you no longer need\n\n💬 **Voice tip:** Say 'Add custom plugin' to create new tools!"

    except Exception as e:
        logger.error(f"Error opening tools page: {e}")
        return f"❌ Error opening Tools & Plugins page: {str(e)}\n\n🔧 **Alternative:** You can manually navigate to the Tools & Plugins section in the Jarvis UI settings."


class MCPManagementPlugin(PluginBase):
    """Plugin class for MCP management tools."""
    
    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="MCP Management",
            version="1.0.0",
            description="Voice commands for managing MCP servers",
            author="Jarvis Assistant",
            tags=["mcp", "management", "servers", "voice"]
        )
    
    def get_tools(self) -> List:
        return [
            add_mcp_server_from_template,
            list_mcp_servers,
            enable_mcp_server,
            disable_mcp_server,
            edit_mcp_server,
            remove_mcp_server
        ]


# Create plugin instance for automatic discovery
plugin = MCPManagementPlugin()

# Export tools for direct import
__all__ = [
    "add_mcp_server_from_template",
    "list_mcp_servers", 
    "enable_mcp_server",
    "disable_mcp_server",
    "remove_mcp_server",
    "plugin"
]
