"""
MCP Configuration Manager for Jarvis Voice Assistant.

This module manages MCP server configurations in a centralized, persistent way
without hardcoding servers into the application configuration.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)


class MCPTransportType(Enum):
    """MCP transport types."""
    STDIO = "stdio"
    HTTP = "http"
    WEBSOCKET = "websocket"


@dataclass
class MCPServerConfig:
    """Configuration for a single MCP server."""
    name: str
    description: str = ""
    transport: MCPTransportType = MCPTransportType.STDIO
    command: str = ""
    args: List[str] = None
    env: Dict[str, str] = None
    enabled: bool = True
    timeout: int = 30
    auto_start: bool = True
    created_at: str = ""
    last_modified: str = ""
    
    def __post_init__(self):
        if self.args is None:
            self.args = []
        if self.env is None:
            self.env = {}
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        self.last_modified = datetime.now().isoformat()


class MCPConfigManager:
    """Manages MCP server configurations in a centralized way."""
    
    def __init__(self, config_file: Path = None):
        """Initialize the MCP configuration manager."""
        if config_file is None:
            config_file = Path("data/mcp_servers.json")
        
        self.config_file = config_file
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        self._servers: Dict[str, MCPServerConfig] = {}
        self._load_config()
    
    def _load_config(self) -> None:
        """Load MCP server configurations from file."""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
                
                servers_data = data.get('servers', {})
                for server_id, server_config in servers_data.items():
                    # Convert transport string back to enum
                    if 'transport' in server_config:
                        server_config['transport'] = MCPTransportType(server_config['transport'])
                    
                    self._servers[server_id] = MCPServerConfig(**server_config)
                
                logger.info(f"Loaded {len(self._servers)} MCP server configurations")
            else:
                logger.info("No existing MCP configuration file found, starting with empty configuration")
                self._save_config()
                
        except Exception as e:
            logger.error(f"Error loading MCP configuration: {e}")
            self._servers = {}
    
    def _save_config(self) -> None:
        """Save MCP server configurations to file."""
        try:
            # Convert servers to serializable format
            servers_data = {}
            for server_id, server_config in self._servers.items():
                config_dict = asdict(server_config)
                # Convert enum to string for JSON serialization
                config_dict['transport'] = config_dict['transport'].value
                servers_data[server_id] = config_dict
            
            data = {
                "servers": servers_data,
                "metadata": {
                    "version": "1.0.0",
                    "last_updated": datetime.now().isoformat(),
                    "description": "MCP server configurations for Jarvis Voice Assistant",
                    "total_servers": len(self._servers),
                    "enabled_servers": len([s for s in self._servers.values() if s.enabled])
                }
            }
            
            with open(self.config_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"Saved {len(self._servers)} MCP server configurations")
            
        except Exception as e:
            logger.error(f"Error saving MCP configuration: {e}")
    
    def add_server(self, server_config: MCPServerConfig) -> bool:
        """Add a new MCP server configuration."""
        try:
            server_id = server_config.name.lower().replace(' ', '_').replace('-', '_')
            
            if server_id in self._servers:
                logger.warning(f"MCP server '{server_id}' already exists, updating configuration")
            
            self._servers[server_id] = server_config
            self._save_config()
            
            logger.info(f"Added MCP server: {server_config.name} ({server_id})")
            return True
            
        except Exception as e:
            logger.error(f"Error adding MCP server: {e}")
            return False
    
    def remove_server(self, server_id: str) -> bool:
        """Remove an MCP server configuration."""
        try:
            if server_id in self._servers:
                server_name = self._servers[server_id].name
                del self._servers[server_id]
                self._save_config()
                
                logger.info(f"Removed MCP server: {server_name} ({server_id})")
                return True
            else:
                logger.warning(f"MCP server '{server_id}' not found")
                return False
                
        except Exception as e:
            logger.error(f"Error removing MCP server: {e}")
            return False
    
    def get_server(self, server_id: str) -> Optional[MCPServerConfig]:
        """Get a specific MCP server configuration."""
        return self._servers.get(server_id)
    
    def get_all_servers(self) -> Dict[str, MCPServerConfig]:
        """Get all MCP server configurations."""
        return self._servers.copy()
    
    def get_enabled_servers(self) -> Dict[str, MCPServerConfig]:
        """Get only enabled MCP server configurations."""
        return {
            server_id: config 
            for server_id, config in self._servers.items() 
            if config.enabled
        }
    
    def enable_server(self, server_id: str) -> bool:
        """Enable an MCP server."""
        if server_id in self._servers:
            self._servers[server_id].enabled = True
            self._servers[server_id].last_modified = datetime.now().isoformat()
            self._save_config()
            logger.info(f"Enabled MCP server: {server_id}")
            return True
        return False
    
    def disable_server(self, server_id: str) -> bool:
        """Disable an MCP server."""
        if server_id in self._servers:
            self._servers[server_id].enabled = False
            self._servers[server_id].last_modified = datetime.now().isoformat()
            self._save_config()
            logger.info(f"Disabled MCP server: {server_id}")
            return True
        return False
    
    def update_server(self, server_id: str, updates: Dict[str, Any]) -> bool:
        """Update an MCP server configuration."""
        try:
            if server_id not in self._servers:
                logger.warning(f"MCP server '{server_id}' not found")
                return False
            
            server_config = self._servers[server_id]
            
            # Update allowed fields
            allowed_fields = ['description', 'command', 'args', 'env', 'enabled', 'timeout', 'auto_start']
            for field, value in updates.items():
                if field in allowed_fields:
                    setattr(server_config, field, value)
            
            server_config.last_modified = datetime.now().isoformat()
            self._save_config()
            
            logger.info(f"Updated MCP server: {server_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating MCP server: {e}")
            return False
    
    def get_server_count(self) -> Dict[str, int]:
        """Get server count statistics."""
        total = len(self._servers)
        enabled = len([s for s in self._servers.values() if s.enabled])
        disabled = total - enabled
        
        return {
            "total": total,
            "enabled": enabled,
            "disabled": disabled
        }


# Global MCP configuration manager instance
_mcp_config_manager = None


def get_mcp_config_manager() -> MCPConfigManager:
    """Get the global MCP configuration manager instance."""
    global _mcp_config_manager
    if _mcp_config_manager is None:
        _mcp_config_manager = MCPConfigManager()
    return _mcp_config_manager
