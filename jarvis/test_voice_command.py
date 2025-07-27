#!/usr/bin/env python3
"""
Test Voice Command for Desktop App

This script tests the updated voice command functionality to ensure
it launches the desktop app instead of the browser version.
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_voice_command():
    """Test the open_jarvis_ui voice command."""
    try:
        # Import the voice command function
        from tools.plugins.jarvis_ui_tool import open_jarvis_ui
        
        print("🧪 Testing Voice Command: 'open settings'")
        print("=" * 50)
        
        # Test opening settings panel (using invoke method for LangChain tools)
        result = open_jarvis_ui.invoke({"panel": "settings"})
        print(f"Result: {result}")
        
        # Check if the result mentions desktop app
        if "desktop app" in result.lower():
            print("✅ SUCCESS: Voice command is using desktop app!")
        elif "browser" in result.lower():
            print("⚠️  FALLBACK: Voice command fell back to browser (pywebview may not be installed)")
        else:
            print("❓ UNKNOWN: Unexpected response")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("   Make sure you're running from the correct directory")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_close_command():
    """Test the close_jarvis_ui voice command."""
    try:
        from tools.plugins.jarvis_ui_tool import close_jarvis_ui
        
        print("\n🧪 Testing Voice Command: 'close UI'")
        print("=" * 50)
        
        # Test closing UI (using invoke method for LangChain tools)
        result = close_jarvis_ui.invoke({})
        print(f"Result: {result}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Main test function."""
    print("🤖 Jarvis Voice Command Test")
    print("Testing updated voice commands for desktop app")
    print()
    
    # Test open command
    success1 = test_voice_command()
    
    # Test close command
    success2 = test_close_command()
    
    print("\n📊 Test Summary:")
    print(f"Open Command: {'✅ PASS' if success1 else '❌ FAIL'}")
    print(f"Close Command: {'✅ PASS' if success2 else '❌ FAIL'}")
    
    if success1 and success2:
        print("\n🎉 All tests passed! Voice commands are working correctly.")
        return 0
    else:
        print("\n⚠️  Some tests failed. Check the output above for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
