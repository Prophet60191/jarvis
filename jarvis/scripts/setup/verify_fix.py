#!/usr/bin/env python3
"""
Verify Plugin Fix

This script verifies that the duplicate plugin issue has been resolved
and that voice commands now only open the desktop app.
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def check_plugin_files():
    """Check how many jarvis_ui_tool.py files exist."""
    print("🔍 Checking for jarvis_ui_tool.py files...")
    
    plugin_files = list(Path(".").rglob("jarvis_ui_tool.py"))
    
    print(f"Found {len(plugin_files)} jarvis_ui_tool.py file(s):")
    for file in plugin_files:
        print(f"  📄 {file}")
    
    if len(plugin_files) == 1:
        print("✅ GOOD: Only one plugin file found (no duplicates)")
        return True
    elif len(plugin_files) == 0:
        print("❌ ERROR: No plugin files found")
        return False
    else:
        print(f"⚠️  WARNING: {len(plugin_files)} plugin files found (duplicates may cause issues)")
        return False

def check_plugin_content():
    """Check if the remaining plugin has desktop app logic."""
    print("\n🔍 Checking plugin content...")
    
    plugin_file = Path("tools/plugins/jarvis_ui_tool.py")
    if not plugin_file.exists():
        print("❌ ERROR: Main plugin file not found")
        return False
    
    content = plugin_file.read_text()
    
    # Check for desktop app logic
    if "jarvis_app.py" in content and "desktop app" in content.lower():
        print("✅ GOOD: Plugin contains desktop app logic")
    else:
        print("❌ ERROR: Plugin missing desktop app logic")
        return False
    
    # Check for fallback logic
    if "fallback to web interface" in content.lower():
        print("✅ GOOD: Plugin has web interface fallback")
    else:
        print("⚠️  WARNING: Plugin may not have web interface fallback")
    
    return True

def test_plugin_import():
    """Test if the plugin can be imported correctly."""
    print("\n🔍 Testing plugin import...")
    
    try:
        from tools.plugins.jarvis_ui_tool import open_jarvis_ui, close_jarvis_ui
        print("✅ GOOD: Plugin imports successfully")
        
        # Test function signatures
        if hasattr(open_jarvis_ui, 'invoke'):
            print("✅ GOOD: open_jarvis_ui is a LangChain tool")
        else:
            print("⚠️  WARNING: open_jarvis_ui may not be a proper LangChain tool")
        
        if hasattr(close_jarvis_ui, 'invoke'):
            print("✅ GOOD: close_jarvis_ui is a LangChain tool")
        else:
            print("⚠️  WARNING: close_jarvis_ui may not be a proper LangChain tool")
        
        return True
        
    except ImportError as e:
        print(f"❌ ERROR: Cannot import plugin: {e}")
        return False
    except Exception as e:
        print(f"❌ ERROR: Plugin import failed: {e}")
        return False

def check_desktop_app_files():
    """Check if desktop app files exist."""
    print("\n🔍 Checking desktop app files...")
    
    required_files = [
        "jarvis_app.py",
        "start_desktop.py",
        "install_desktop.py"
    ]
    
    all_exist = True
    for file in required_files:
        if Path(file).exists():
            print(f"✅ {file} exists")
        else:
            print(f"❌ {file} missing")
            all_exist = False
    
    return all_exist

def main():
    """Main verification function."""
    print("🔧 Jarvis Plugin Fix Verification")
    print("=" * 50)
    print("Checking if the duplicate plugin issue has been resolved...")
    print()
    
    # Run all checks
    checks = [
        ("Plugin Files", check_plugin_files),
        ("Plugin Content", check_plugin_content),
        ("Plugin Import", test_plugin_import),
        ("Desktop App Files", check_desktop_app_files)
    ]
    
    results = []
    for check_name, check_func in checks:
        try:
            result = check_func()
            results.append((check_name, result))
        except Exception as e:
            print(f"❌ ERROR in {check_name}: {e}")
            results.append((check_name, False))
    
    # Summary
    print("\n📊 Verification Summary:")
    print("=" * 30)
    
    passed = 0
    for check_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{check_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{len(results)} checks passed")
    
    if passed == len(results):
        print("\n🎉 SUCCESS: All checks passed!")
        print("The duplicate plugin issue has been resolved.")
        print("Voice commands should now only open the desktop app.")
    else:
        print(f"\n⚠️  WARNING: {len(results) - passed} check(s) failed.")
        print("There may still be issues with the plugin configuration.")
    
    return 0 if passed == len(results) else 1

if __name__ == "__main__":
    sys.exit(main())
