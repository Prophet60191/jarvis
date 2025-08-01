#!/usr/bin/env python3
"""
Test the corrected settings app path.
"""

import os

def test_corrected_path():
    """Test the corrected path calculation."""
    print("🔍 TESTING CORRECTED SETTINGS PATH")
    print("=" * 50)
    
    # Simulate the corrected path calculation
    plugin_file = "jarvis/jarvis/tools/plugins/jarvis_ui_tool.py"
    
    plugin_dir = os.path.dirname(plugin_file)  # jarvis/jarvis/tools/plugins/
    jarvis_tools_dir = os.path.dirname(plugin_dir)  # jarvis/jarvis/tools/
    jarvis_inner_dir = os.path.dirname(jarvis_tools_dir)  # jarvis/jarvis/
    project_root = os.path.dirname(jarvis_inner_dir)  # project root
    
    desktop_script = os.path.join(project_root, "jarvis", "jarvis_settings_app.py")
    
    print(f"Plugin file: {plugin_file}")
    print(f"Plugin dir: {plugin_dir}")
    print(f"Tools dir: {jarvis_tools_dir}")
    print(f"Inner dir: {jarvis_inner_dir}")
    print(f"Project root: {project_root}")
    print(f"Settings script: {desktop_script}")
    print(f"Exists: {os.path.exists(desktop_script)}")
    
    if os.path.exists(desktop_script):
        print("✅ CORRECT PATH FOUND!")
    else:
        print("❌ Path still incorrect")

def main():
    test_corrected_path()

if __name__ == "__main__":
    main()
