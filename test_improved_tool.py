#!/usr/bin/env python3
"""
Test the improved Jarvis UI tool.
"""

import sys
import time
from pathlib import Path

# Add jarvis to path
sys.path.insert(0, str(Path(__file__).parent / "jarvis"))

def test_improved_tool():
    """Test the improved tool with better error handling."""
    print("🔧 Testing Improved Jarvis UI Tool")
    print("=" * 60)
    
    try:
        from jarvis.tools.plugins.jarvis_ui_tool import open_jarvis_ui
        
        print("✅ Successfully imported open_jarvis_ui")
        
        # Test calling the tool function
        print("🧪 Calling open_jarvis_ui('audio')...")
        result = open_jarvis_ui.func('audio')
        
        print(f"📋 Tool result: {result}")
        
        # Check if it mentions "native desktop app" (success) or "web interface" (fallback)
        if "native desktop app" in result:
            print("✅ Desktop app launched successfully!")
            return True
        elif "web interface" in result:
            print("⚠️  Fell back to web interface")
            return False
        else:
            print("❓ Unclear result")
            return False
        
    except Exception as e:
        print(f"❌ Tool test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_logs():
    """Check what the logs say about the launch attempt."""
    print("\n📋 Checking Logs")
    print("=" * 60)
    
    try:
        import logging
        
        # Set up logging to capture what the tool is doing
        logging.basicConfig(level=logging.DEBUG)
        
        from jarvis.tools.plugins.jarvis_ui_tool import open_jarvis_ui
        
        print("🧪 Calling tool with logging enabled...")
        result = open_jarvis_ui.func('audio')
        
        print(f"📋 Result: {result}")
        
        return True
        
    except Exception as e:
        print(f"❌ Log check failed: {e}")
        return False


def main():
    """Test the improved tool."""
    print("🔧 Improved Jarvis UI Tool Test")
    print("=" * 60)
    print("Testing the tool with better error handling")
    print("=" * 60)
    
    # Test the improved tool
    success = test_improved_tool()
    
    if success:
        print("\n🎉 Desktop app is working!")
        print("   Try the voice command: 'Hey Jarvis, open settings'")
    else:
        print("\n⚠️  Desktop app isn't working, but web interface should be available")
        print("   The tool will fall back to web interface")
        print("   Check the logs for more details")
    
    # Also test with logging
    check_logs()


if __name__ == "__main__":
    main()
