"""
Command-line interface for Jarvis plugin management.

This module provides CLI commands for managing plugins, including listing,
enabling, disabling, and generating new plugins.
"""

import argparse
import logging
import sys
from typing import List, Optional
from pathlib import Path

from .manager import PluginManager
from .generator import PluginGenerator
from .discovery import PluginDiscovery

logger = logging.getLogger(__name__)


class PluginCLI:
    """
    Command-line interface for plugin management.
    
    Provides commands for discovering, managing, and generating plugins.
    """
    
    def __init__(self):
        """Initialize the plugin CLI."""
        self.plugin_manager = PluginManager(auto_discover=False)
        # Set default output directory to jarvis/tools/plugins
        jarvis_dir = Path(__file__).parent.parent
        default_output_dir = jarvis_dir / "tools" / "plugins"
        self.generator = PluginGenerator(output_dir=str(default_output_dir))
    
    def list_plugins(self, show_details: bool = False) -> None:
        """
        List all discovered plugins.
        
        Args:
            show_details: Whether to show detailed plugin information
        """
        print("🔍 Discovering plugins...")
        discovered = self.plugin_manager.discovery.discover_plugins()
        
        if not discovered:
            print("❌ No plugins found")
            return
        
        print(f"📦 Found {len(discovered)} plugins:")
        print()
        
        for plugin_name, plugin_info in discovered.items():
            metadata = plugin_info.get("metadata")
            if metadata:
                status = "✅ Loaded" if plugin_name in self.plugin_manager.get_loaded_plugin_names() else "⏸️  Available"
                print(f"{status} {plugin_name} v{metadata.version}")
                
                if show_details:
                    print(f"    📝 {metadata.description}")
                    print(f"    👤 Author: {metadata.author}")
                    print(f"    📁 File: {plugin_info.get('file_path', 'Unknown')}")
                    print(f"    🔧 Method: {plugin_info.get('discovery_method', 'Unknown')}")
                    
                    if hasattr(metadata, 'tools') and metadata.tools:
                        print(f"    🛠️  Tools: {len(metadata.tools)}")
                    
                    print()
    
    def load_plugin(self, plugin_name: str) -> None:
        """
        Load a specific plugin.
        
        Args:
            plugin_name: Name of the plugin to load
        """
        print(f"🔄 Loading plugin: {plugin_name}")
        
        # Discover plugins first
        self.plugin_manager.discovery.discover_plugins()
        
        plugin_info = self.plugin_manager.discovery.get_plugin_info(plugin_name)
        if not plugin_info:
            print(f"❌ Plugin '{plugin_name}' not found")
            return
        
        success = self.plugin_manager.load_plugin_from_info(plugin_info)
        if success:
            tools = self.plugin_manager.get_plugin_tools(plugin_name)
            print(f"✅ Successfully loaded plugin '{plugin_name}' with {len(tools)} tools")
        else:
            print(f"❌ Failed to load plugin '{plugin_name}'")
    
    def unload_plugin(self, plugin_name: str) -> None:
        """
        Unload a specific plugin.
        
        Args:
            plugin_name: Name of the plugin to unload
        """
        print(f"🔄 Unloading plugin: {plugin_name}")
        
        success = self.plugin_manager.unload_plugin(plugin_name)
        if success:
            print(f"✅ Successfully unloaded plugin '{plugin_name}'")
        else:
            print(f"❌ Failed to unload plugin '{plugin_name}'")
    
    def reload_plugin(self, plugin_name: str) -> None:
        """
        Reload a specific plugin.
        
        Args:
            plugin_name: Name of the plugin to reload
        """
        print(f"🔄 Reloading plugin: {plugin_name}")
        
        success = self.plugin_manager.reload_plugin(plugin_name)
        if success:
            tools = self.plugin_manager.get_plugin_tools(plugin_name)
            print(f"✅ Successfully reloaded plugin '{plugin_name}' with {len(tools)} tools")
        else:
            print(f"❌ Failed to reload plugin '{plugin_name}'")
    
    def enable_plugin(self, plugin_name: str) -> None:
        """
        Enable a disabled plugin.
        
        Args:
            plugin_name: Name of the plugin to enable
        """
        print(f"🔄 Enabling plugin: {plugin_name}")
        
        success = self.plugin_manager.enable_plugin(plugin_name)
        if success:
            print(f"✅ Successfully enabled plugin '{plugin_name}'")
        else:
            print(f"❌ Failed to enable plugin '{plugin_name}'")
    
    def disable_plugin(self, plugin_name: str) -> None:
        """
        Disable a plugin.
        
        Args:
            plugin_name: Name of the plugin to disable
        """
        print(f"🔄 Disabling plugin: {plugin_name}")
        
        self.plugin_manager.disable_plugin(plugin_name)
        print(f"✅ Successfully disabled plugin '{plugin_name}'")
    
    def generate_plugin(self, 
                       name: str,
                       plugin_type: str = "basic",
                       author: str = "Unknown",
                       description: str = "",
                       tools: Optional[List[str]] = None,
                       output_dir: Optional[str] = None) -> None:
        """
        Generate a new plugin from template.
        
        Args:
            name: Plugin name
            plugin_type: Type of plugin template
            author: Plugin author
            description: Plugin description
            tools: List of tool names
            output_dir: Output directory
        """
        print(f"🔧 Generating {plugin_type} plugin: {name}")
        
        if output_dir:
            self.generator.output_dir = Path(output_dir)
        
        try:
            file_path = self.generator.generate_plugin(
                plugin_name=name,
                plugin_type=plugin_type,
                author=author,
                description=description,
                tools=tools or []
            )
            print(f"✅ Generated plugin: {file_path}")
            print(f"💡 Edit the file to implement your plugin functionality")
            
        except Exception as e:
            print(f"❌ Error generating plugin: {e}")
    
    def show_plugin_info(self, plugin_name: str) -> None:
        """
        Show detailed information about a plugin.
        
        Args:
            plugin_name: Name of the plugin
        """
        # Discover plugins first
        self.plugin_manager.discovery.discover_plugins()
        
        plugin_info = self.plugin_manager.discovery.get_plugin_info(plugin_name)
        if not plugin_info:
            print(f"❌ Plugin '{plugin_name}' not found")
            return
        
        metadata = plugin_info.get("metadata")
        if not metadata:
            print(f"❌ No metadata found for plugin '{plugin_name}'")
            return
        
        print(f"📦 Plugin Information: {plugin_name}")
        print("=" * 50)
        print(f"Name: {metadata.name}")
        print(f"Version: {metadata.version}")
        print(f"Description: {metadata.description}")
        print(f"Author: {metadata.author}")
        print(f"File: {plugin_info.get('file_path', 'Unknown')}")
        print(f"Discovery Method: {plugin_info.get('discovery_method', 'Unknown')}")
        
        if metadata.dependencies:
            print(f"Dependencies: {', '.join(metadata.dependencies)}")
        
        if metadata.min_jarvis_version:
            print(f"Min Jarvis Version: {metadata.min_jarvis_version}")
        
        # Show tools
        if plugin_name in self.plugin_manager.get_loaded_plugin_names():
            tools = self.plugin_manager.get_plugin_tools(plugin_name)
            print(f"Tools: {len(tools)}")
            for tool in tools:
                print(f"  - {tool.name}: {tool.description}")
        else:
            print("Tools: Plugin not loaded")
        
        print(f"Status: {'✅ Loaded' if plugin_name in self.plugin_manager.get_loaded_plugin_names() else '⏸️  Available'}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="Jarvis Plugin Management CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List all plugins")
    list_parser.add_argument("--details", action="store_true", help="Show detailed information")
    
    # Load command
    load_parser = subparsers.add_parser("load", help="Load a plugin")
    load_parser.add_argument("name", help="Plugin name")
    
    # Unload command
    unload_parser = subparsers.add_parser("unload", help="Unload a plugin")
    unload_parser.add_argument("name", help="Plugin name")
    
    # Reload command
    reload_parser = subparsers.add_parser("reload", help="Reload a plugin")
    reload_parser.add_argument("name", help="Plugin name")
    
    # Enable command
    enable_parser = subparsers.add_parser("enable", help="Enable a plugin")
    enable_parser.add_argument("name", help="Plugin name")
    
    # Disable command
    disable_parser = subparsers.add_parser("disable", help="Disable a plugin")
    disable_parser.add_argument("name", help="Plugin name")
    
    # Info command
    info_parser = subparsers.add_parser("info", help="Show plugin information")
    info_parser.add_argument("name", help="Plugin name")
    
    # Generate command
    generate_parser = subparsers.add_parser("generate", help="Generate a new plugin")
    generate_parser.add_argument("name", help="Plugin name")
    generate_parser.add_argument("--type", choices=["basic", "tool", "advanced"], 
                                default="basic", help="Plugin template type")
    generate_parser.add_argument("--author", default="Unknown", help="Plugin author")
    generate_parser.add_argument("--description", default="", help="Plugin description")
    generate_parser.add_argument("--tools", nargs="*", help="Tool names to include")
    generate_parser.add_argument("--output-dir", help="Output directory")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    cli = PluginCLI()
    
    try:
        if args.command == "list":
            cli.list_plugins(show_details=args.details)
        elif args.command == "load":
            cli.load_plugin(args.name)
        elif args.command == "unload":
            cli.unload_plugin(args.name)
        elif args.command == "reload":
            cli.reload_plugin(args.name)
        elif args.command == "enable":
            cli.enable_plugin(args.name)
        elif args.command == "disable":
            cli.disable_plugin(args.name)
        elif args.command == "info":
            cli.show_plugin_info(args.name)
        elif args.command == "generate":
            cli.generate_plugin(
                name=args.name,
                plugin_type=args.type,
                author=args.author,
                description=args.description,
                tools=args.tools,
                output_dir=args.output_dir
            )
        
        return 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
