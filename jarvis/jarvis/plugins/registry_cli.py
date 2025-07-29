#!/usr/bin/env python3
"""
Plugin Registry Management CLI

Command-line interface for managing and inspecting the enhanced plugin registry.
Provides tools for administrators and developers to monitor, analyze, and maintain
the plugin ecosystem.
"""

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
from tabulate import tabulate
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

try:
    from .enhanced_manager import EnhancedPluginManager
    from .registry import UnifiedPluginRegistry
    from .registry.relationship_mapper import RelationshipType
    REGISTRY_AVAILABLE = True
except ImportError:
    REGISTRY_AVAILABLE = False
    logger.error("Enhanced plugin registry not available")

class RegistryCLI:
    """Command-line interface for plugin registry management."""
    
    def __init__(self, registry_path: Optional[Path] = None):
        """
        Initialize the registry CLI.
        
        Args:
            registry_path: Optional path to registry storage
        """
        if not REGISTRY_AVAILABLE:
            raise RuntimeError("Enhanced plugin registry not available")
        
        self.registry_path = registry_path or Path("data/plugin_registry.json")
        self.plugin_manager = EnhancedPluginManager(
            enable_enhanced_features=True,
            registry_storage_path=self.registry_path
        )
    
    def list_plugins(self, show_details: bool = False) -> None:
        """
        List all registered plugins.
        
        Args:
            show_details: Whether to show detailed information
        """
        plugins = self.plugin_manager.get_loaded_plugins()
        
        if not plugins:
            print("No plugins registered.")
            return
        
        if show_details:
            self._show_detailed_plugin_list(plugins)
        else:
            self._show_simple_plugin_list(plugins)
    
    def show_plugin_info(self, plugin_name: str) -> None:
        """
        Show detailed information about a specific plugin.
        
        Args:
            plugin_name: Name of the plugin
        """
        if plugin_name not in self.plugin_manager.get_loaded_plugins():
            print(f"Plugin '{plugin_name}' not found.")
            return
        
        # Get enhanced metadata
        metadata = self.plugin_manager.get_enhanced_plugin_metadata(plugin_name)
        if not metadata:
            print(f"No enhanced metadata found for plugin '{plugin_name}'.")
            return
        
        # Display plugin information
        print(f"\n=== Plugin Information: {plugin_name} ===")
        print(f"Version: {metadata.version}")
        print(f"Author: {metadata.author}")
        print(f"Description: {metadata.description}")
        print(f"Capabilities: {', '.join(metadata.capabilities)}")
        print(f"Semantic Tags: {', '.join(metadata.semantic_tags)}")
        
        # Show performance profile
        if metadata.performance_profile:
            profile = metadata.performance_profile
            print(f"\nPerformance Profile:")
            print(f"  Average Execution Time: {profile.avg_execution_time:.3f}s")
            print(f"  Memory Usage: {profile.memory_usage_mb:.1f}MB")
            print(f"  Success Rate: {profile.success_rate:.1%}")
        
        # Show usage statistics
        if metadata.usage_statistics:
            stats = metadata.usage_statistics
            print(f"\nUsage Statistics:")
            print(f"  Total Executions: {stats.total_executions}")
            print(f"  Success Rate: {stats.success_rate:.1%}")
            print(f"  Average Rating: {stats.average_rating:.1f}/5.0")
            print(f"  Usage Frequency: {stats.usage_frequency:.2f} per day")
        
        # Show relationships
        relationships = self.plugin_manager.get_related_plugins(plugin_name)
        if relationships:
            print(f"\nRelated Plugins: {', '.join(relationships[:5])}")
    
    def show_relationships(self, plugin_name: Optional[str] = None) -> None:
        """
        Show plugin relationships.
        
        Args:
            plugin_name: Optional specific plugin name
        """
        if plugin_name:
            self._show_plugin_relationships(plugin_name)
        else:
            self._show_all_relationships()
    
    def show_analytics(self, plugin_name: Optional[str] = None) -> None:
        """
        Show analytics information.
        
        Args:
            plugin_name: Optional specific plugin name
        """
        if plugin_name:
            analytics = self.plugin_manager.get_plugin_analytics(plugin_name)
            self._display_plugin_analytics(plugin_name, analytics)
        else:
            self._show_system_analytics()
    
    def search_capabilities(self, capability: str) -> None:
        """
        Search for plugins by capability.
        
        Args:
            capability: Capability to search for
        """
        plugins = self.plugin_manager.find_plugins_by_capability(capability)
        
        if not plugins:
            print(f"No plugins found with capability '{capability}'.")
            return
        
        print(f"\nPlugins with capability '{capability}':")
        for plugin in plugins:
            print(f"  - {plugin}")
    
    def export_data(self, output_path: str, format_type: str = "json") -> None:
        """
        Export registry data.
        
        Args:
            output_path: Output file path
            format_type: Export format (json, csv)
        """
        export_path = Path(output_path)
        
        if format_type.lower() == "json":
            success = self.plugin_manager.export_enhanced_data(export_path)
            if success:
                print(f"Registry data exported to {export_path}")
            else:
                print("Failed to export registry data")
        else:
            print(f"Unsupported export format: {format_type}")
    
    def show_health_status(self, plugin_name: Optional[str] = None) -> None:
        """
        Show health status of plugins.
        
        Args:
            plugin_name: Optional specific plugin name
        """
        if plugin_name:
            health = self.plugin_manager.get_plugin_health_status(plugin_name)
            self._display_plugin_health(plugin_name, health)
        else:
            self._show_all_plugin_health()
    
    def show_statistics(self) -> None:
        """Show overall registry statistics."""
        stats = self.plugin_manager.get_registry_statistics()
        
        print("\n=== Registry Statistics ===")
        print(f"Total Plugins: {stats.get('total_plugins', 0)}")
        print(f"Active Plugins: {stats.get('active_plugins', 0)}")
        print(f"Enhanced Features: {'Enabled' if stats.get('enhanced_features_enabled', False) else 'Disabled'}")
        print(f"Registry Size: {stats.get('registry_size_mb', 0):.1f}MB")
        print(f"Total Relationships: {stats.get('total_relationships', 0)}")
        
        # Show ecosystem analysis
        ecosystem = self.plugin_manager.analyze_plugin_ecosystem()
        if 'error' not in ecosystem:
            print(f"\n=== Ecosystem Analysis ===")
            print(f"Relationship Density: {ecosystem.get('relationship_density', 0):.2%}")
            
            # Show top plugins
            if 'top_by_usage' in ecosystem:
                print(f"\nTop Plugins by Usage:")
                for plugin, score in ecosystem['top_by_usage'][:5]:
                    print(f"  {plugin}: {score:.2f}")
    
    def _show_simple_plugin_list(self, plugins: Dict[str, Any]) -> None:
        """Show simple plugin list."""
        print(f"\nRegistered Plugins ({len(plugins)}):")
        for plugin_name in sorted(plugins.keys()):
            print(f"  - {plugin_name}")
    
    def _show_detailed_plugin_list(self, plugins: Dict[str, Any]) -> None:
        """Show detailed plugin list."""
        table_data = []
        
        for plugin_name in sorted(plugins.keys()):
            metadata = self.plugin_manager.get_enhanced_plugin_metadata(plugin_name)
            if metadata:
                capabilities = ', '.join(list(metadata.capabilities)[:3])
                if len(metadata.capabilities) > 3:
                    capabilities += "..."
                
                success_rate = "N/A"
                if metadata.usage_statistics:
                    success_rate = f"{metadata.usage_statistics.success_rate:.1%}"
                
                table_data.append([
                    plugin_name,
                    metadata.version,
                    capabilities,
                    success_rate
                ])
        
        headers = ["Plugin", "Version", "Capabilities", "Success Rate"]
        print(f"\n{tabulate(table_data, headers=headers, tablefmt='grid')}")
    
    def _show_plugin_relationships(self, plugin_name: str) -> None:
        """Show relationships for a specific plugin."""
        if not hasattr(self.plugin_manager, 'unified_registry'):
            print("Enhanced features not available.")
            return
        
        relationships = self.plugin_manager.unified_registry.relationship_mapper.get_plugin_relationships(plugin_name)
        
        if not relationships:
            print(f"No relationships found for plugin '{plugin_name}'.")
            return
        
        print(f"\n=== Relationships for {plugin_name} ===")
        for rel_type, related_plugins in relationships.items():
            if related_plugins:
                print(f"\n{rel_type.value.title()}:")
                for related_plugin, strength in related_plugins[:5]:
                    print(f"  - {related_plugin} (strength: {strength:.2f})")
    
    def _show_all_relationships(self) -> None:
        """Show overview of all relationships."""
        if not hasattr(self.plugin_manager, 'unified_registry'):
            print("Enhanced features not available.")
            return
        
        total_relationships = self.plugin_manager.unified_registry.relationship_mapper.get_relationship_count()
        print(f"\nTotal Relationships: {total_relationships}")
        
        # Show relationship type distribution
        plugins = self.plugin_manager.get_loaded_plugins()
        type_counts = {rel_type: 0 for rel_type in RelationshipType}
        
        for plugin_name in plugins:
            relationships = self.plugin_manager.unified_registry.relationship_mapper.get_plugin_relationships(plugin_name)
            for rel_type, related_plugins in relationships.items():
                type_counts[rel_type] += len(related_plugins)
        
        print("\nRelationship Type Distribution:")
        for rel_type, count in type_counts.items():
            if count > 0:
                print(f"  {rel_type.value.title()}: {count}")
    
    def _display_plugin_analytics(self, plugin_name: str, analytics: Dict[str, Any]) -> None:
        """Display analytics for a specific plugin."""
        if 'error' in analytics:
            print(f"Analytics not available for '{plugin_name}': {analytics['error']}")
            return
        
        print(f"\n=== Analytics for {plugin_name} ===")
        
        if 'usage_stats' in analytics:
            stats = analytics['usage_stats']
            print(f"Usage Statistics:")
            print(f"  Total Executions: {stats.get('total_executions', 0)}")
            print(f"  Success Rate: {stats.get('success_rate', 0):.1%}")
            print(f"  Usage Frequency: {stats.get('usage_frequency', 0):.2f} per day")
        
        if 'performance' in analytics:
            perf = analytics['performance']
            print(f"\nPerformance Metrics:")
            print(f"  Average Execution Time: {perf.get('avg_execution_time', 0):.3f}s")
            print(f"  Memory Usage: {perf.get('memory_usage_mb', 0):.1f}MB")
        
        if 'recommendations' in analytics:
            recommendations = analytics['recommendations']
            if recommendations and recommendations != ["Plugin performance is optimal"]:
                print(f"\nRecommendations:")
                for rec in recommendations:
                    print(f"  - {rec}")
    
    def _show_system_analytics(self) -> None:
        """Show system-wide analytics."""
        summary = self.plugin_manager.get_plugin_analytics_summary()
        
        if 'error' in summary:
            print(f"System analytics not available: {summary['error']}")
            return
        
        print("\n=== System Analytics ===")
        print(f"Total Plugins: {summary.get('total_plugins', 0)}")
        print(f"Total Tools: {summary.get('total_tools', 0)}")
        
        # Show plugin health summary
        health_summary = summary.get('plugin_health_summary', {})
        if health_summary:
            print(f"\nPlugin Health Summary:")
            for status, count in health_summary.items():
                if count > 0:
                    print(f"  {status.title()}: {count}")
        
        # Show top plugins
        top_plugins = summary.get('top_plugins', {})
        if 'by_usage' in top_plugins and top_plugins['by_usage']:
            print(f"\nTop Plugins by Usage:")
            for plugin, score in top_plugins['by_usage'][:5]:
                print(f"  {plugin}: {score:.2f}")
    
    def _display_plugin_health(self, plugin_name: str, health: Dict[str, Any]) -> None:
        """Display health status for a specific plugin."""
        status = health.get('status', 'unknown')
        reason = health.get('reason', 'No reason provided')
        
        status_emoji = {
            'healthy': '✅',
            'warning': '⚠️',
            'critical': '❌',
            'error': '💥',
            'unknown': '❓'
        }
        
        print(f"\n{status_emoji.get(status, '❓')} {plugin_name}: {status.upper()}")
        print(f"  Reason: {reason}")
        
        if 'issues' in health:
            print(f"  Issues:")
            for issue in health['issues']:
                print(f"    - {issue}")
    
    def _show_all_plugin_health(self) -> None:
        """Show health status for all plugins."""
        plugins = self.plugin_manager.get_loaded_plugins()
        
        print(f"\n=== Plugin Health Status ===")
        
        health_counts = {'healthy': 0, 'warning': 0, 'critical': 0, 'error': 0}
        
        for plugin_name in sorted(plugins.keys()):
            health = self.plugin_manager.get_plugin_health_status(plugin_name)
            status = health.get('status', 'unknown')
            
            if status in health_counts:
                health_counts[status] += 1
            
            status_emoji = {
                'healthy': '✅',
                'warning': '⚠️',
                'critical': '❌',
                'error': '💥',
                'unknown': '❓'
            }
            
            print(f"  {status_emoji.get(status, '❓')} {plugin_name}: {status}")
        
        print(f"\nSummary:")
        for status, count in health_counts.items():
            if count > 0:
                print(f"  {status.title()}: {count}")

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Plugin Registry Management CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s list                          # List all plugins
  %(prog)s list --details               # List plugins with details
  %(prog)s info my_plugin               # Show plugin information
  %(prog)s relationships                # Show all relationships
  %(prog)s relationships my_plugin      # Show plugin relationships
  %(prog)s analytics                    # Show system analytics
  %(prog)s analytics my_plugin          # Show plugin analytics
  %(prog)s search file_operations       # Search by capability
  %(prog)s health                       # Show all plugin health
  %(prog)s health my_plugin             # Show plugin health
  %(prog)s export data.json             # Export registry data
  %(prog)s stats                        # Show registry statistics
        """
    )
    
    parser.add_argument(
        '--registry-path',
        type=Path,
        help='Path to registry storage file'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List registered plugins')
    list_parser.add_argument('--details', action='store_true', help='Show detailed information')
    
    # Info command
    info_parser = subparsers.add_parser('info', help='Show plugin information')
    info_parser.add_argument('plugin_name', help='Name of the plugin')
    
    # Relationships command
    rel_parser = subparsers.add_parser('relationships', help='Show plugin relationships')
    rel_parser.add_argument('plugin_name', nargs='?', help='Optional plugin name')
    
    # Analytics command
    analytics_parser = subparsers.add_parser('analytics', help='Show analytics')
    analytics_parser.add_argument('plugin_name', nargs='?', help='Optional plugin name')
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Search plugins by capability')
    search_parser.add_argument('capability', help='Capability to search for')
    
    # Export command
    export_parser = subparsers.add_parser('export', help='Export registry data')
    export_parser.add_argument('output_path', help='Output file path')
    export_parser.add_argument('--format', default='json', choices=['json'], help='Export format')
    
    # Health command
    health_parser = subparsers.add_parser('health', help='Show plugin health status')
    health_parser.add_argument('plugin_name', nargs='?', help='Optional plugin name')
    
    # Stats command
    subparsers.add_parser('stats', help='Show registry statistics')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        cli = RegistryCLI(args.registry_path)
        
        if args.command == 'list':
            cli.list_plugins(args.details)
        elif args.command == 'info':
            cli.show_plugin_info(args.plugin_name)
        elif args.command == 'relationships':
            cli.show_relationships(args.plugin_name)
        elif args.command == 'analytics':
            cli.show_analytics(args.plugin_name)
        elif args.command == 'search':
            cli.search_capabilities(args.capability)
        elif args.command == 'export':
            cli.export_data(args.output_path, args.format)
        elif args.command == 'health':
            cli.show_health_status(args.plugin_name)
        elif args.command == 'stats':
            cli.show_statistics()
        
    except Exception as e:
        logger.error(f"Command failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
