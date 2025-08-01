#!/usr/bin/env python3
"""
Test the settings app path resolution.
"""

import os
import sys
from pathlib import Path

# Add jarvis to path
sys.path.insert(0, str(Path(__file__).parent / "jarvis"))

def test_settings_path():
    """Test if we can find the settings app correctly."""
    print("🔍 TESTING SETTINGS APP PATH RESOLUTION")
    print("=" * 60)
    
    # Simulate the path calculation from the plugin
    plugin_file = "jarvis/jarvis/tools/plugins/jarvis_ui_tool.py"
    
    print(f"Plugin file: {plugin_file}")
    
    # Method 1: Current approach in the tool
    plugin_dir = os.path.dirname(plugin_file)  # jarvis/jarvis/tools/plugins/
    jarvis_tools_dir = os.path.dirname(plugin_dir)  # jarvis/jarvis/tools/
    jarvis_main_dir = os.path.dirname(jarvis_tools_dir)  # jarvis/jarvis/
    desktop_script = os.path.join(jarvis_main_dir, "jarvis_settings_app.py")
    
    print(f"\nMethod 1 (current):")
    print(f"  Plugin dir: {plugin_dir}")
    print(f"  Tools dir: {jarvis_tools_dir}")
    print(f"  Main dir: {jarvis_main_dir}")
    print(f"  Settings script: {desktop_script}")
    print(f"  Exists: {os.path.exists(desktop_script)}")
    
    # Method 2: Absolute path approach
    current_dir = os.path.dirname(os.path.abspath(__file__))
    settings_script_abs = os.path.join(current_dir, "jarvis", "jarvis_settings_app.py")
    
    print(f"\nMethod 2 (absolute):")
    print(f"  Current dir: {current_dir}")
    print(f"  Settings script: {settings_script_abs}")
    print(f"  Exists: {os.path.exists(settings_script_abs)}")
    
    # Method 3: Find it directly
    for root, dirs, files in os.walk("."):
        if "jarvis_settings_app.py" in files:
            found_path = os.path.join(root, "jarvis_settings_app.py")
            print(f"\nMethod 3 (search):")
            print(f"  Found at: {found_path}")
            print(f"  Absolute: {os.path.abspath(found_path)}")
            break
    
    # Test the vault path too for comparison
    vault_script = "rag_app.py"
    print(f"\nVault script (for comparison):")
    print(f"  Path: {vault_script}")
    print(f"  Exists: {os.path.exists(vault_script)}")


def test_import_from_plugin():
    """Test importing the tool to see what path it actually uses."""
    print("\n🧪 TESTING ACTUAL TOOL IMPORT")
    print("=" * 60)
    
    try:
        from jarvis.tools.plugins.jarvis_ui_tool import open_jarvis_ui
        print("✅ Successfully imported open_jarvis_ui tool")
        
        # Try to call it to see what happens
        print("\n📝 Tool description:")
        print(f"Name: {open_jarvis_ui.name}")
        print(f"Description: {open_jarvis_ui.description[:100]}...")
        
    except Exception as e:
        print(f"❌ Failed to import tool: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Main test function."""
    test_settings_path()
    test_import_from_plugin()
    
    print("\n🎯 RECOMMENDATIONS:")
    print("=" * 60)
    print("Based on the path tests above, the settings tool should use")
    print("the path that shows 'Exists: True' for jarvis_settings_app.py")


if __name__ == "__main__":
    main()
