#!/usr/bin/env python3
"""
Test the time tool availability and functionality
"""

import sys
from pathlib import Path

# Add jarvis to path
sys.path.insert(0, str(Path(__file__).parent / "jarvis"))

def test_time_tool():
    """Test if the time tool is available and working."""
    print("🕐 TESTING TIME TOOL AVAILABILITY")
    print("=" * 50)
    
    try:
        # Test 1: Check if tool is in the registry
        from jarvis.tools import get_langchain_tools
        tools = get_langchain_tools()
        
        print(f"📊 Total tools loaded: {len(tools)}")
        
        # Find the time tool
        time_tool = None
        for tool in tools:
            if hasattr(tool, 'name') and 'time' in tool.name.lower():
                time_tool = tool
                print(f"✅ Found time tool: {tool.name}")
                print(f"   Description: {tool.description}")
                break
        
        if not time_tool:
            print("❌ No time tool found!")
            print("Available tools:")
            for tool in tools[:10]:  # Show first 10 tools
                if hasattr(tool, 'name'):
                    print(f"   - {tool.name}")
            return False
        
        # Test 2: Try to invoke the tool
        print(f"\n🧪 Testing tool invocation...")
        try:
            result = time_tool.invoke({})
            print(f"✅ Tool result: {result}")
            return True
        except Exception as e:
            print(f"❌ Tool invocation failed: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing time tool: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_direct_import():
    """Test direct import of the time tool."""
    print("\n🔧 TESTING DIRECT TOOL IMPORT")
    print("=" * 50)
    
    try:
        # Try to import the tool directly
        from jarvis.tools.plugins.device_time_tool import get_current_time
        
        print("✅ Successfully imported get_current_time")
        
        # Test the tool directly
        result = get_current_time()
        print(f"✅ Direct tool result: {result}")
        return True
        
    except Exception as e:
        print(f"❌ Direct import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function."""
    print("🎯 JARVIS TIME TOOL DIAGNOSTIC")
    print("=" * 60)
    
    # Test through the tool system
    tool_system_works = test_time_tool()
    
    # Test direct import
    direct_import_works = test_direct_import()
    
    print("\n📋 SUMMARY")
    print("=" * 30)
    print(f"Tool system: {'✅ Working' if tool_system_works else '❌ Failed'}")
    print(f"Direct import: {'✅ Working' if direct_import_works else '❌ Failed'}")
    
    if tool_system_works:
        print("\n💡 The time tool is available and should work with Jarvis!")
    else:
        print("\n⚠️  The time tool has issues that need to be resolved.")

if __name__ == "__main__":
    main()
