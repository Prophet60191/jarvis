"""
Plugin template generator for Jarvis.

This module provides utilities to generate plugin templates and boilerplate
code for new tools, following MCP standards and best practices.
"""

import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class PluginGenerator:
    """
    Generates plugin templates and boilerplate code for Jarvis tools.
    
    This class helps developers quickly create new plugins by generating
    standardized templates with proper structure and documentation.
    """
    
    def __init__(self, output_dir: Optional[str] = None):
        """
        Initialize the plugin generator.
        
        Args:
            output_dir: Directory where plugins will be generated
        """
        self.output_dir = Path(output_dir) if output_dir else Path.cwd() / "plugins"
        self.templates = self._load_templates()
    
    def _load_templates(self) -> Dict[str, str]:
        """Load plugin templates."""
        return {
            "basic_plugin": self._get_basic_plugin_template(),
            "tool_plugin": self._get_tool_plugin_template(),
            "advanced_plugin": self._get_advanced_plugin_template()
        }
    
    def generate_plugin(self, 
                       plugin_name: str,
                       plugin_type: str = "basic",
                       author: str = "Unknown",
                       description: str = "",
                       tools: Optional[list] = None) -> str:
        """
        Generate a new plugin from template.
        
        Args:
            plugin_name: Name of the plugin
            plugin_type: Type of plugin template (basic, tool, advanced)
            author: Plugin author name
            description: Plugin description
            tools: List of tool names to include
            
        Returns:
            str: Path to the generated plugin file
        """
        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate plugin content
        template_key = f"{plugin_type}_plugin"
        if template_key not in self.templates:
            raise ValueError(f"Unknown plugin type: {plugin_type}")
        
        template = self.templates[template_key]
        
        # Replace template variables
        content = template.format(
            plugin_name=plugin_name,
            plugin_class_name=self._to_class_name(plugin_name),
            author=author,
            description=description or f"A {plugin_type} plugin for Jarvis",
            date=datetime.now().strftime("%Y-%m-%d"),
            tools=tools or [],
            tool_methods=self._generate_tool_methods(tools or [])
        )
        
        # Write plugin file
        filename = f"{plugin_name.lower().replace(' ', '_')}.py"
        file_path = self.output_dir / filename
        
        with open(file_path, 'w') as f:
            f.write(content)
        
        logger.info(f"Generated plugin: {file_path}")
        return str(file_path)
    
    def _to_class_name(self, name: str) -> str:
        """Convert plugin name to class name."""
        return ''.join(word.capitalize() for word in name.replace('_', ' ').split())
    
    def _generate_tool_methods(self, tools: list) -> str:
        """Generate tool method implementations."""
        if not tools:
            return ""
        
        methods = []
        for tool in tools:
            method_name = tool.lower().replace(' ', '_')
            class_name = self._to_class_name(tool)
            
            method = f'''
    def _create_{method_name}_tool(self) -> BaseTool:
        """Create the {tool} tool."""
        @tool
        def {method_name}(query: str = "") -> str:
            """
            {tool} tool implementation.
            
            Args:
                query: Input query for the tool
                
            Returns:
                str: Tool result
            """
            # TODO: Implement {tool} functionality
            return f"Result from {tool}: {{query}}"
        
        return {method_name}
'''
            methods.append(method)
        
        return '\n'.join(methods)
    
    def _get_basic_plugin_template(self) -> str:
        """Get basic plugin template."""
        return '''"""
{plugin_name} Plugin for Jarvis Voice Assistant.

{description}

Author: {author}
Date: {date}
"""

import logging
from typing import List
from langchain_core.tools import BaseTool, tool

from jarvis.plugins.base import PluginBase, PluginMetadata

logger = logging.getLogger(__name__)


class {plugin_class_name}Plugin(PluginBase):
    """
    {plugin_name} plugin for Jarvis.
    
    {description}
    """
    
    def __init__(self):
        """Initialize the {plugin_name} plugin."""
        super().__init__()
        logger.info("Initialized {plugin_name} plugin")
    
    def get_metadata(self) -> PluginMetadata:
        """Get plugin metadata."""
        return PluginMetadata(
            name="{plugin_name}",
            version="1.0.0",
            description="{description}",
            author="{author}",
            dependencies=[],
            min_jarvis_version="1.0.0"
        )
    
    def get_tools(self) -> List[BaseTool]:
        """Get tools provided by this plugin."""
        tools = []
        
        # Add your tools here
        # Example:
        # tools.append(self._create_example_tool())
        
        return tools
    
    def _create_example_tool(self) -> BaseTool:
        """Create an example tool."""
        @tool
        def example_tool(query: str = "") -> str:
            """
            Example tool implementation.
            
            Args:
                query: Input query for the tool
                
            Returns:
                str: Tool result
            """
            return f"Example tool result: {{query}}"
        
        return example_tool


# Plugin class for automatic discovery
PLUGIN_CLASS = {plugin_class_name}Plugin

# Plugin metadata for discovery
PLUGIN_METADATA = {plugin_class_name}Plugin().get_metadata()
'''
    
    def _get_tool_plugin_template(self) -> str:
        """Get tool-focused plugin template."""
        return '''"""
{plugin_name} Plugin for Jarvis Voice Assistant.

{description}

Author: {author}
Date: {date}
"""

import logging
from typing import List, Dict, Any
from langchain_core.tools import BaseTool, tool

from jarvis.plugins.base import PluginBase, PluginMetadata

logger = logging.getLogger(__name__)


class {plugin_class_name}Plugin(PluginBase):
    """
    {plugin_name} plugin providing specialized tools for Jarvis.
    
    {description}
    """
    
    def __init__(self):
        """Initialize the {plugin_name} plugin."""
        super().__init__()
        self.config = {{}}
        logger.info("Initialized {plugin_name} plugin")
    
    def get_metadata(self) -> PluginMetadata:
        """Get plugin metadata."""
        return PluginMetadata(
            name="{plugin_name}",
            version="1.0.0",
            description="{description}",
            author="{author}",
            dependencies=[],
            min_jarvis_version="1.0.0",
            config_schema={{
                "type": "object",
                "properties": {{
                    "enabled": {{
                        "type": "boolean",
                        "default": True,
                        "description": "Enable/disable the plugin"
                    }}
                }}
            }}
        )
    
    def get_tools(self) -> List[BaseTool]:
        """Get tools provided by this plugin."""
        tools = []
        
        # Add plugin tools
        {tool_methods}
        
        return tools
    
    def configure(self, config: Dict[str, Any]) -> None:
        """Configure the plugin."""
        self.config.update(config)
        logger.info(f"Configured {plugin_name} plugin: {{config}}")


# Plugin class for automatic discovery
PLUGIN_CLASS = {plugin_class_name}Plugin

# Plugin metadata for discovery
PLUGIN_METADATA = {plugin_class_name}Plugin().get_metadata()
'''
    
    def _get_advanced_plugin_template(self) -> str:
        """Get advanced plugin template with full features."""
        return '''"""
{plugin_name} Plugin for Jarvis Voice Assistant.

{description}

Author: {author}
Date: {date}
"""

import logging
from typing import List, Dict, Any, Optional
from langchain_core.tools import BaseTool, tool

from jarvis.plugins.base import PluginBase, PluginMetadata

logger = logging.getLogger(__name__)


class {plugin_class_name}Plugin(PluginBase):
    """
    Advanced {plugin_name} plugin for Jarvis.
    
    {description}
    """
    
    def __init__(self):
        """Initialize the {plugin_name} plugin."""
        super().__init__()
        self.config = {{}}
        self.resources = {{}}
        logger.info("Initialized {plugin_name} plugin")
    
    def get_metadata(self) -> PluginMetadata:
        """Get plugin metadata."""
        return PluginMetadata(
            name="{plugin_name}",
            version="1.0.0",
            description="{description}",
            author="{author}",
            dependencies=[],
            min_jarvis_version="1.0.0",
            config_schema={{
                "type": "object",
                "properties": {{
                    "enabled": {{
                        "type": "boolean",
                        "default": True,
                        "description": "Enable/disable the plugin"
                    }},
                    "api_key": {{
                        "type": "string",
                        "description": "API key for external services"
                    }},
                    "timeout": {{
                        "type": "number",
                        "default": 30,
                        "description": "Request timeout in seconds"
                    }}
                }},
                "required": ["enabled"]
            }}
        )
    
    def initialize(self) -> None:
        """Initialize plugin resources."""
        super().initialize()
        
        # Initialize any resources needed by the plugin
        try:
            self._setup_resources()
            logger.info(f"{plugin_name} plugin resources initialized")
        except Exception as e:
            logger.error(f"Failed to initialize {plugin_name} plugin resources: {{e}}")
            raise
    
    def cleanup(self) -> None:
        """Clean up plugin resources."""
        try:
            self._cleanup_resources()
            logger.info(f"{plugin_name} plugin resources cleaned up")
        except Exception as e:
            logger.warning(f"Error cleaning up {plugin_name} plugin resources: {{e}}")
        
        super().cleanup()
    
    def _setup_resources(self) -> None:
        """Set up plugin-specific resources."""
        # TODO: Initialize any external connections, caches, etc.
        pass
    
    def _cleanup_resources(self) -> None:
        """Clean up plugin-specific resources."""
        # TODO: Close connections, clear caches, etc.
        self.resources.clear()
    
    def get_tools(self) -> List[BaseTool]:
        """Get tools provided by this plugin."""
        if not self.is_initialized():
            logger.warning(f"{plugin_name} plugin not initialized, returning empty tools list")
            return []
        
        tools = []
        
        # Add plugin tools
        {tool_methods}
        
        return tools
    
    def configure(self, config: Dict[str, Any]) -> None:
        """Configure the plugin."""
        self.config.update(config)
        
        # Validate configuration
        if not self._validate_config():
            raise ValueError(f"Invalid configuration for {plugin_name} plugin")
        
        logger.info(f"Configured {plugin_name} plugin")
    
    def _validate_config(self) -> bool:
        """Validate plugin configuration."""
        # TODO: Add configuration validation logic
        return True


# Plugin class for automatic discovery
PLUGIN_CLASS = {plugin_class_name}Plugin

# Plugin metadata for discovery
PLUGIN_METADATA = {plugin_class_name}Plugin().get_metadata()
'''


def generate_plugin_cli():
    """Command-line interface for plugin generation."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate Jarvis plugin templates")
    parser.add_argument("name", help="Plugin name")
    parser.add_argument("--type", choices=["basic", "tool", "advanced"], 
                       default="basic", help="Plugin template type")
    parser.add_argument("--author", default="Unknown", help="Plugin author")
    parser.add_argument("--description", default="", help="Plugin description")
    parser.add_argument("--output-dir", help="Output directory")
    parser.add_argument("--tools", nargs="*", help="Tool names to include")
    
    args = parser.parse_args()
    
    generator = PluginGenerator(args.output_dir)
    
    try:
        file_path = generator.generate_plugin(
            plugin_name=args.name,
            plugin_type=args.type,
            author=args.author,
            description=args.description,
            tools=args.tools
        )
        print(f"✅ Generated plugin: {file_path}")
    except Exception as e:
        print(f"❌ Error generating plugin: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(generate_plugin_cli())
