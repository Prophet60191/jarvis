#!/usr/bin/env python3
"""
Test plugin discovery system to see what's happening with tool detection
"""

import sys
from pathlib import Path

# Add jarvis to path
sys.path.insert(0, str(Path(__file__).parent / "jarvis"))

def test_plugin_discovery():
    """Test the plugin discovery system."""
    print("🔍 TESTING PLUGIN DISCOVERY SYSTEM")
    print("=" * 60)
    
    try:
        from jarvis.plugins.discovery import PluginDiscovery
        from jarvis.plugins.manager import PluginManager
        
        # Test discovery
        discovery = PluginDiscovery()
        print(f"📁 Plugin directories: {discovery.plugin_directories}")
        
        # Discover plugins
        discovered = discovery.discover_plugins()
        print(f"🔍 Discovered {len(discovered)} plugins:")
        
        for plugin_name, plugin_info in discovered.items():
            print(f"\n📦 Plugin: {plugin_name}")
            print(f"   Method: {plugin_info.get('discovery_method', 'unknown')}")
            print(f"   File: {plugin_info.get('file_path', 'unknown')}")
            
            if 'tools' in plugin_info:
                tools = plugin_info['tools']
                print(f"   Tools: {len(tools)}")
                for tool in tools[:3]:  # Show first 3 tools
                    if hasattr(tool, 'name'):
                        print(f"     - {tool.name}: {getattr(tool, 'description', 'No description')[:50]}...")
            
            if 'plugin_class' in plugin_info:
                print(f"   Plugin Class: {plugin_info['plugin_class']}")
        
        # Test manager
        print(f"\n🔧 TESTING PLUGIN MANAGER")
        print("=" * 40)
        
        manager = PluginManager(auto_discover=True)
        all_tools = manager.get_all_tools()
        
        print(f"🛠️  Total tools loaded: {len(all_tools)}")
        
        # Look for time tool specifically
        time_tools = [tool for tool in all_tools if 'time' in tool.name.lower()]
        print(f"⏰ Time-related tools: {len(time_tools)}")
        for tool in time_tools:
            print(f"   - {tool.name}: {tool.description[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing plugin discovery: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_direct_tool_import():
    """Test direct import of a specific tool."""
    print(f"\n🧪 TESTING DIRECT TOOL IMPORT")
    print("=" * 40)
    
    try:
        # Try to import the device time tool directly
        from jarvis.tools.plugins.device_time_tool import get_current_time
        
        print("✅ Successfully imported get_current_time")
        print(f"   Name: {get_current_time.name}")
        print(f"   Description: {get_current_time.description[:100]}...")
        print(f"   Has func: {hasattr(get_current_time, 'func')}")
        print(f"   Callable func: {callable(getattr(get_current_time, 'func', None))}")
        
        return True
        
    except Exception as e:
        print(f"❌ Direct import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function."""
    print("🎯 JARVIS PLUGIN DISCOVERY DIAGNOSTIC")
    print("=" * 70)
    
    # Test discovery system
    discovery_works = test_plugin_discovery()
    
    # Test direct import
    direct_import_works = test_direct_tool_import()
    
    print("\n📋 SUMMARY")
    print("=" * 30)
    print(f"Plugin discovery: {'✅ Working' if discovery_works else '❌ Failed'}")
    print(f"Direct import: {'✅ Working' if direct_import_works else '❌ Failed'}")

if __name__ == "__main__":
    main()
