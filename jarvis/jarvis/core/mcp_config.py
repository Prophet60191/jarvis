"""
MCP Configuration Management for Jarvis Voice Assistant.

This module provides secure configuration storage and management for MCP servers,
including encryption for sensitive data like API keys and tokens.
"""

import base64
import json
import logging
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from .mcp_client import MCPServerConfig, MCPTransportType

logger = logging.getLogger(__name__)


@dataclass
class MCPConfigurationData:
    """Complete MCP configuration data structure."""
    servers: Dict[str, MCPServerConfig]
    version: str = "1.0"
    encrypted_fields: List[str] = None
    
    def __post_init__(self):
        if self.encrypted_fields is None:
            self.encrypted_fields = []


class MCPConfigurationManager:
    """
    Manages MCP server configurations with encryption for sensitive data.
    
    Provides secure storage and retrieval of MCP server configurations,
    automatically encrypting sensitive fields like API keys and tokens.
    """
    
    # Fields that should be encrypted
    SENSITIVE_FIELDS = {
        'env',  # Environment variables (may contain API keys)
        'headers',  # HTTP headers (may contain auth tokens)
    }
    
    def __init__(self, config_file: Optional[Path] = None, password: Optional[str] = None):
        """
        Initialize the MCP configuration manager.
        
        Args:
            config_file: Path to configuration file
            password: Password for encryption (auto-generated if None)
        """
        self.config_file = config_file or Path.home() / ".jarvis" / "mcp_config.json"
        self.key_file = self.config_file.parent / ".mcp_key"
        self.password = password
        self._cipher: Optional[Fernet] = None
        
        # Ensure config directory exists
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize encryption
        self._init_encryption()
    
    def _init_encryption(self) -> None:
        """Initialize encryption cipher."""
        try:
            # Get or create encryption key
            if self.key_file.exists():
                # Load existing key
                with open(self.key_file, 'rb') as f:
                    key_data = f.read()
                    
                # Derive key from password if provided
                if self.password:
                    kdf = PBKDF2HMAC(
                        algorithm=hashes.SHA256(),
                        length=32,
                        salt=key_data[:16],  # First 16 bytes as salt
                        iterations=100000,
                    )
                    key = base64.urlsafe_b64encode(kdf.derive(self.password.encode()))
                else:
                    key = key_data[16:]  # Skip salt, use key
                    
            else:
                # Generate new key
                if self.password:
                    # Use password-based key derivation
                    salt = os.urandom(16)
                    kdf = PBKDF2HMAC(
                        algorithm=hashes.SHA256(),
                        length=32,
                        salt=salt,
                        iterations=100000,
                    )
                    key = base64.urlsafe_b64encode(kdf.derive(self.password.encode()))
                    
                    # Save salt + key
                    with open(self.key_file, 'wb') as f:
                        f.write(salt + base64.urlsafe_b64decode(key))
                else:
                    # Generate random key
                    key = Fernet.generate_key()
                    salt = os.urandom(16)
                    
                    # Save salt + key
                    with open(self.key_file, 'wb') as f:
                        f.write(salt + base64.urlsafe_b64decode(key))
                
                # Set restrictive permissions
                os.chmod(self.key_file, 0o600)
                
            self._cipher = Fernet(key)
            logger.info("MCP configuration encryption initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize MCP configuration encryption: {e}")
            # Fall back to no encryption
            self._cipher = None
    
    def _encrypt_value(self, value: Any) -> str:
        """Encrypt a value if cipher is available."""
        if not self._cipher:
            return value
            
        try:
            if isinstance(value, dict):
                value_str = json.dumps(value)
            else:
                value_str = str(value)
                
            encrypted = self._cipher.encrypt(value_str.encode())
            return base64.urlsafe_b64encode(encrypted).decode()
            
        except Exception as e:
            logger.warning(f"Failed to encrypt value: {e}")
            return value
    
    def _decrypt_value(self, encrypted_value: str) -> Any:
        """Decrypt a value if cipher is available."""
        if not self._cipher:
            return encrypted_value
            
        try:
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_value.encode())
            decrypted = self._cipher.decrypt(encrypted_bytes)
            value_str = decrypted.decode()
            
            # Try to parse as JSON first
            try:
                return json.loads(value_str)
            except json.JSONDecodeError:
                return value_str
                
        except Exception as e:
            logger.warning(f"Failed to decrypt value: {e}")
            return encrypted_value
    
    def _encrypt_server_config(self, config: MCPServerConfig) -> Dict[str, Any]:
        """Encrypt sensitive fields in server configuration."""
        config_dict = asdict(config)

        # Convert enum to string for JSON serialization
        if 'transport' in config_dict:
            config_dict['transport'] = config_dict['transport'].value

        encrypted_fields = []
        
        for field_name in self.SENSITIVE_FIELDS:
            if field_name in config_dict and config_dict[field_name]:
                # Only encrypt non-empty values
                if (isinstance(config_dict[field_name], dict) and config_dict[field_name]) or \
                   (isinstance(config_dict[field_name], str) and config_dict[field_name].strip()):
                    config_dict[field_name] = self._encrypt_value(config_dict[field_name])
                    encrypted_fields.append(field_name)
        
        config_dict['_encrypted_fields'] = encrypted_fields
        return config_dict
    
    def _decrypt_server_config(self, config_dict: Dict[str, Any]) -> MCPServerConfig:
        """Decrypt sensitive fields in server configuration."""
        encrypted_fields = config_dict.pop('_encrypted_fields', [])
        
        for field_name in encrypted_fields:
            if field_name in config_dict:
                config_dict[field_name] = self._decrypt_value(config_dict[field_name])
        
        # Convert transport string to enum
        if 'transport' in config_dict:
            config_dict['transport'] = MCPTransportType(config_dict['transport'])
        
        return MCPServerConfig(**config_dict)
    
    def load_configuration(self) -> Dict[str, MCPServerConfig]:
        """
        Load MCP server configurations from file.
        
        Returns:
            Dictionary of server configurations
        """
        if not self.config_file.exists():
            logger.info("No MCP configuration file found")
            return {}
        
        try:
            with open(self.config_file, 'r') as f:
                data = json.load(f)
            
            servers = {}
            for server_name, server_data in data.get('servers', {}).items():
                try:
                    config = self._decrypt_server_config(server_data)
                    servers[server_name] = config
                except Exception as e:
                    logger.error(f"Error loading server config '{server_name}': {e}")
            
            logger.info(f"Loaded {len(servers)} MCP server configurations")
            return servers
            
        except Exception as e:
            logger.error(f"Error loading MCP configuration: {e}")
            return {}
    
    def save_configuration(self, servers: Dict[str, MCPServerConfig]) -> bool:
        """
        Save MCP server configurations to file.
        
        Args:
            servers: Dictionary of server configurations
            
        Returns:
            True if saved successfully
        """
        try:
            # Prepare data for saving
            config_data = {
                'version': '1.0',
                'servers': {}
            }
            
            for server_name, config in servers.items():
                config_data['servers'][server_name] = self._encrypt_server_config(config)
            
            # Write to temporary file first
            temp_file = self.config_file.with_suffix('.tmp')
            with open(temp_file, 'w') as f:
                json.dump(config_data, f, indent=2)
            
            # Atomic move to final location
            temp_file.replace(self.config_file)
            
            # Set restrictive permissions
            os.chmod(self.config_file, 0o600)
            
            logger.info(f"Saved {len(servers)} MCP server configurations")
            return True
            
        except Exception as e:
            logger.error(f"Error saving MCP configuration: {e}")
            return False
    
    def add_server(self, config: MCPServerConfig) -> bool:
        """
        Add a new server configuration.
        
        Args:
            config: Server configuration to add
            
        Returns:
            True if added successfully
        """
        try:
            # Load existing configurations
            servers = self.load_configuration()
            
            # Add new server
            servers[config.name] = config
            
            # Save updated configurations
            return self.save_configuration(servers)
            
        except Exception as e:
            logger.error(f"Error adding server configuration: {e}")
            return False
    
    def remove_server(self, server_name: str) -> bool:
        """
        Remove a server configuration.
        
        Args:
            server_name: Name of server to remove
            
        Returns:
            True if removed successfully
        """
        try:
            # Load existing configurations
            servers = self.load_configuration()
            
            if server_name not in servers:
                logger.warning(f"Server '{server_name}' not found in configuration")
                return False
            
            # Remove server
            del servers[server_name]
            
            # Save updated configurations
            return self.save_configuration(servers)
            
        except Exception as e:
            logger.error(f"Error removing server configuration: {e}")
            return False
    
    def update_server(self, config: MCPServerConfig) -> bool:
        """
        Update an existing server configuration.
        
        Args:
            config: Updated server configuration
            
        Returns:
            True if updated successfully
        """
        try:
            # Load existing configurations
            servers = self.load_configuration()
            
            # Update server
            servers[config.name] = config
            
            # Save updated configurations
            return self.save_configuration(servers)
            
        except Exception as e:
            logger.error(f"Error updating server configuration: {e}")
            return False
    
    def get_server(self, server_name: str) -> Optional[MCPServerConfig]:
        """
        Get a specific server configuration.
        
        Args:
            server_name: Name of server to retrieve
            
        Returns:
            Server configuration or None if not found
        """
        servers = self.load_configuration()
        return servers.get(server_name)
    
    def list_servers(self) -> List[str]:
        """
        List all configured server names.
        
        Returns:
            List of server names
        """
        servers = self.load_configuration()
        return list(servers.keys())
    
    def backup_configuration(self, backup_path: Path) -> bool:
        """
        Create a backup of the configuration.
        
        Args:
            backup_path: Path for backup file
            
        Returns:
            True if backup created successfully
        """
        try:
            if self.config_file.exists():
                backup_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Copy configuration file
                with open(self.config_file, 'rb') as src, open(backup_path, 'wb') as dst:
                    dst.write(src.read())
                
                logger.info(f"Configuration backed up to {backup_path}")
                return True
            else:
                logger.warning("No configuration file to backup")
                return False
                
        except Exception as e:
            logger.error(f"Error creating configuration backup: {e}")
            return False
    
    def restore_configuration(self, backup_path: Path) -> bool:
        """
        Restore configuration from backup.
        
        Args:
            backup_path: Path to backup file
            
        Returns:
            True if restored successfully
        """
        try:
            if not backup_path.exists():
                logger.error(f"Backup file not found: {backup_path}")
                return False
            
            # Copy backup to configuration file
            with open(backup_path, 'rb') as src, open(self.config_file, 'wb') as dst:
                dst.write(src.read())
            
            # Set permissions
            os.chmod(self.config_file, 0o600)
            
            logger.info(f"Configuration restored from {backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error restoring configuration: {e}")
            return False
