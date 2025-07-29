#!/usr/bin/env python3
"""
Debug the exact file path the tool is looking for.
"""

import sys
import os
from pathlib import Path

# Add jarvis to path
sys.path.insert(0, str(Path(__file__).parent / "jarvis"))

def debug_tool_path():
    """Debug exactly what path the tool is using."""
    print("🔍 Debugging Tool File Path")
    print("=" * 60)
    
    try:
        # Simulate exactly what the tool does
        from jarvis.tools.plugins.jarvis_ui_tool import open_jarvis_ui
        
        # Get the plugin file location
        plugin_file = open_jarvis_ui.func.__code__.co_filename
        print(f"📍 Plugin file: {plugin_file}")
        
        # Calculate the path like the tool does
        # Plugin is in jarvis/tools/plugins/, so go up 4 levels to get to project root
        jarvis_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(plugin_file))))
        print(f"📁 Calculated jarvis_dir: {jarvis_dir}")
        
        # Check what the tool is looking for
        desktop_script = os.path.join(jarvis_dir, "jarvis_settings_app.py")
        print(f"🎯 Looking for desktop script: {desktop_script}")
        print(f"   Exists: {'✅ Yes' if os.path.exists(desktop_script) else '❌ No'}")
        
        # Check what's actually in that directory
        if os.path.exists(jarvis_dir):
            print(f"\n📋 Contents of {jarvis_dir}:")
            for item in sorted(os.listdir(jarvis_dir)):
                if item.endswith('.py'):
                    print(f"   📄 {item}")
        
        # Check where our script actually is
        actual_script = Path(__file__).parent / "jarvis_settings_app.py"
        print(f"\n🎯 Our script is actually at: {actual_script}")
        print(f"   Exists: {'✅ Yes' if actual_script.exists() else '❌ No'}")
        
        # Check if they're the same
        if str(actual_script) == desktop_script:
            print("✅ Paths match!")
        else:
            print("❌ Paths don't match!")
            print(f"   Tool expects: {desktop_script}")
            print(f"   Script is at: {actual_script}")
        
        return desktop_script, str(actual_script)
        
    except Exception as e:
        print(f"❌ Path debug failed: {e}")
        import traceback
        traceback.print_exc()
        return None, None


def test_webview_import():
    """Test if webview import works in the tool context."""
    print("\n🖥️ Testing WebView Import")
    print("=" * 60)
    
    try:
        # Test webview import like the tool does
        import webview
        print("✅ webview imported successfully")
        
        # Check if we can create a window
        webview.create_window(
            title="Test",
            html="<h1>Test</h1>",
            width=100,
            height=100
        )
        print("✅ webview.create_window() works")
        
        # Clear windows
        webview.windows.clear()
        
        return True
        
    except ImportError as e:
        print(f"❌ webview import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ webview test failed: {e}")
        return False


def main():
    """Debug the tool path issue."""
    print("🔍 Tool Path Debug")
    print("=" * 60)
    print("Finding out why the tool can't find the desktop app")
    print("=" * 60)
    
    # Debug the path
    expected_path, actual_path = debug_tool_path()
    
    # Test webview
    webview_works = test_webview_import()
    
    print(f"\n{'='*60}")
    print("🔍 DIAGNOSIS")
    print("=" * 60)
    
    if expected_path and actual_path:
        if expected_path == actual_path:
            print("✅ File path is correct")
            if webview_works:
                print("✅ WebView works")
                print("🤔 The tool should be working...")
                print("   Maybe there's another issue in the tool logic")
            else:
                print("❌ WebView doesn't work")
                print("   This is why it falls back to web interface")
        else:
            print("❌ File path mismatch!")
            print("🔧 Solution: Move the script or update the tool path")
            print(f"   Move {actual_path}")
            print(f"   To   {expected_path}")
    else:
        print("❌ Couldn't determine paths")


if __name__ == "__main__":
    main()
