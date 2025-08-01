#!/usr/bin/env python3
"""
Debug script to check if the professional app builder plugin is being loaded correctly.
"""

import sys
import os
from pathlib import Path

# Add the jarvis package to Python path
project_root = Path(__file__).parent
jarvis_path = project_root / "jarvis"
sys.path.insert(0, str(jarvis_path))

def debug_plugin_discovery():
    """Debug the plugin discovery system."""
    print("🔍 Debugging Plugin Discovery System")
    print("=" * 50)
    
    try:
        from jarvis.plugins.discovery import PluginDiscovery
        from jarvis.plugins.manager import PluginManager
        
        # Create plugin discovery instance
        discovery = PluginDiscovery()
        
        # Discover all plugins
        discovered = discovery.discover_plugins()
        
        print(f"📦 Discovered {len(discovered)} plugins:")
        for name, info in discovered.items():
            print(f"   - {name}: {info.get('discovery_method', 'unknown')}")
            if 'professional' in name.lower() or 'app' in name.lower():
                print(f"     🎯 APP BUILDER PLUGIN FOUND: {name}")
                print(f"        Method: {info.get('discovery_method')}")
                print(f"        File: {info.get('file_path')}")
        
        # Check specifically for professional app builder
        if "ProfessionalAppBuilder" in discovered:
            print("\n✅ Professional App Builder plugin discovered!")
            plugin_info = discovered["ProfessionalAppBuilder"]
            print(f"   Discovery method: {plugin_info.get('discovery_method')}")
            print(f"   File path: {plugin_info.get('file_path')}")
            print(f"   Has plugin class: {'plugin_class' in plugin_info}")
        else:
            print("\n❌ Professional App Builder plugin NOT discovered!")
            
        return discovered
        
    except Exception as e:
        print(f"❌ Error in plugin discovery: {e}")
        import traceback
        traceback.print_exc()
        return {}

def debug_plugin_loading():
    """Debug the plugin loading system."""
    print("\n🔧 Debugging Plugin Loading System")
    print("=" * 50)
    
    try:
        from jarvis.plugins.manager import PluginManager
        
        # Create plugin manager
        manager = PluginManager(auto_discover=True)
        
        # Get loaded plugins
        loaded_plugins = manager.get_loaded_plugins()
        print(f"📦 Loaded {len(loaded_plugins)} plugins:")
        for name in loaded_plugins:
            print(f"   - {name}")
            if 'professional' in name.lower() or 'app' in name.lower():
                print(f"     🎯 APP BUILDER PLUGIN LOADED: {name}")
        
        # Get all tools
        all_tools = manager.get_all_tools()
        print(f"\n🔧 Total tools available: {len(all_tools)}")
        
        # Look for app builder tools
        app_builder_tools = []
        for tool in all_tools:
            tool_name = getattr(tool, 'name', str(tool))
            tool_desc = getattr(tool, 'description', '')
            
            if any(keyword in tool_name.lower() for keyword in ['app', 'build', 'professional']):
                app_builder_tools.append((tool_name, tool_desc))
                print(f"   🎯 APP BUILDER TOOL: {tool_name}")
                print(f"      Description: {tool_desc[:100]}...")
        
        if not app_builder_tools:
            print("   ❌ No app builder tools found!")
        
        return manager, all_tools
        
    except Exception as e:
        print(f"❌ Error in plugin loading: {e}")
        import traceback
        traceback.print_exc()
        return None, []

def debug_tool_integration():
    """Debug the tool integration with Jarvis main system."""
    print("\n🔗 Debugging Tool Integration")
    print("=" * 50)
    
    try:
        from jarvis.tools import get_langchain_tools
        
        # Get all tools that would be available to Jarvis
        jarvis_tools = get_langchain_tools()
        print(f"🤖 Jarvis has access to {len(jarvis_tools)} tools:")
        
        # Look for app builder tools
        app_builder_tools = []
        for tool in jarvis_tools:
            tool_name = getattr(tool, 'name', str(tool))
            tool_desc = getattr(tool, 'description', '')
            
            if any(keyword in tool_name.lower() for keyword in ['app', 'build', 'professional']):
                app_builder_tools.append((tool_name, tool_desc))
                print(f"   🎯 APP BUILDER TOOL AVAILABLE: {tool_name}")
                print(f"      Description: {tool_desc[:100]}...")
        
        if not app_builder_tools:
            print("   ❌ No app builder tools available to Jarvis!")
            print("   📝 Available tools:")
            for i, tool in enumerate(jarvis_tools[:10]):  # Show first 10
                tool_name = getattr(tool, 'name', str(tool))
                print(f"      {i+1}. {tool_name}")
            if len(jarvis_tools) > 10:
                print(f"      ... and {len(jarvis_tools) - 10} more")
        
        return jarvis_tools
        
    except Exception as e:
        print(f"❌ Error in tool integration: {e}")
        import traceback
        traceback.print_exc()
        return []

def test_direct_tool_import():
    """Test importing the app builder tool directly."""
    print("\n🧪 Testing Direct Tool Import")
    print("=" * 50)
    
    try:
        from jarvis.tools.plugins.professional_app_builder import build_professional_application
        print("✅ Successfully imported build_professional_application")
        
        # Check tool properties
        print(f"   Name: {getattr(build_professional_application, 'name', 'Unknown')}")
        print(f"   Description: {getattr(build_professional_application, 'description', 'No description')[:100]}...")
        
        # Try to get the plugin class
        from jarvis.tools.plugins.professional_app_builder import ProfessionalAppBuilderPlugin
        print("✅ Successfully imported ProfessionalAppBuilderPlugin")
        
        # Create instance and get tools
        plugin = ProfessionalAppBuilderPlugin()
        tools = plugin.get_tools()
        print(f"   Plugin provides {len(tools)} tools:")
        for tool in tools:
            tool_name = getattr(tool, 'name', str(tool))
            print(f"      - {tool_name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error importing app builder tools: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_plugin_file():
    """Check if the plugin file has the required exports."""
    print("\n📄 Checking Plugin File Structure")
    print("=" * 50)
    
    plugin_file = jarvis_path / "jarvis" / "tools" / "plugins" / "professional_app_builder.py"
    
    if not plugin_file.exists():
        print(f"❌ Plugin file not found: {plugin_file}")
        return False
    
    print(f"✅ Plugin file exists: {plugin_file}")
    
    # Read the file and check for required exports
    try:
        with open(plugin_file, 'r') as f:
            content = f.read()
        
        required_items = [
            "PLUGIN_CLASS",
            "PLUGIN_METADATA", 
            "ProfessionalAppBuilderPlugin",
            "build_professional_application"
        ]
        
        for item in required_items:
            if item in content:
                print(f"   ✅ Found: {item}")
            else:
                print(f"   ❌ Missing: {item}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error reading plugin file: {e}")
        return False

def main():
    """Run all debug checks."""
    print("🚀 Debugging Jarvis App Builder Integration")
    print("=" * 60)
    
    # Run all debug checks
    discovered = debug_plugin_discovery()
    manager, tools = debug_plugin_loading()
    jarvis_tools = debug_tool_integration()
    direct_import = test_direct_tool_import()
    file_check = check_plugin_file()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 DEBUG SUMMARY")
    print("=" * 60)
    
    issues = []
    
    if "ProfessionalAppBuilder" not in discovered:
        issues.append("Plugin not discovered by discovery system")
    
    if manager and "ProfessionalAppBuilder" not in manager.get_loaded_plugins():
        issues.append("Plugin not loaded by plugin manager")
    
    app_builder_in_jarvis = any(
        'app' in getattr(tool, 'name', '').lower() and 'build' in getattr(tool, 'name', '').lower()
        for tool in jarvis_tools
    )
    if not app_builder_in_jarvis:
        issues.append("App builder tools not available to Jarvis")
    
    if not direct_import:
        issues.append("Cannot import app builder tools directly")
    
    if not file_check:
        issues.append("Plugin file structure issues")
    
    if issues:
        print("❌ ISSUES FOUND:")
        for i, issue in enumerate(issues, 1):
            print(f"   {i}. {issue}")
        
        print("\n💡 RECOMMENDED FIXES:")
        print("   1. Check plugin file exports (PLUGIN_CLASS, PLUGIN_METADATA)")
        print("   2. Verify plugin inheritance from PluginBase")
        print("   3. Ensure plugin directory is in discovery path")
        print("   4. Check for import errors in plugin file")
    else:
        print("✅ All checks passed! App builder should be accessible to Jarvis.")
    
    return len(issues) == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
