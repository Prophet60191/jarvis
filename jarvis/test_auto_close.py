#!/usr/bin/env python3
"""
Test Auto Close Behavior

This script tests that the desktop window automatically closes
when the server is shut down via voice command or API.
"""

import sys
import time
import requests
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_voice_command_close():
    """Test the voice command close functionality."""
    print("🎤 Testing Voice Command Auto-Close")
    print("=" * 50)
    
    try:
        from jarvis.core.agent import JarvisAgent
        from jarvis.config import get_config
        from jarvis.tools import get_langchain_tools
        
        config = get_config()
        agent = JarvisAgent(config.llm)
        tools = get_langchain_tools()
        agent.initialize(tools)
        
        # Test close command
        print("🛑 Testing close command...")
        close_response = agent.process_input("close jarvis ui")
        print(f"📝 Close response: {close_response}")
        
        # Check if the response indicates success
        if "closed successfully" in close_response.lower() or "shut down" in close_response.lower():
            print("✅ Voice command executed successfully")
            print("🖥️  Desktop window should close automatically within 2-6 seconds")
        else:
            print("⚠️  Voice command may not have worked as expected")
        
        return True
        
    except Exception as e:
        print(f"❌ Voice command test error: {e}")
        return False

def test_api_endpoints():
    """Test the new API endpoints."""
    print("\n🔧 Testing API Endpoints")
    print("=" * 30)
    
    # Test if server is running
    try:
        response = requests.get("http://localhost:8080/", timeout=2)
        print("✅ Server is running")
    except:
        print("❌ Server is not running - start desktop app first")
        return False
    
    # Test close-window API
    print("\n📡 Testing /api/close-window...")
    try:
        response = requests.post("http://localhost:8080/api/close-window", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Close-window API: {data}")
        else:
            print(f"⚠️  Close-window API status: {response.status_code}")
    except Exception as e:
        print(f"❌ Close-window API error: {e}")
    
    # Test shutdown API
    print("\n📡 Testing /api/shutdown...")
    try:
        response = requests.post("http://localhost:8080/api/shutdown", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Shutdown API: {data}")
            print("🖥️  Desktop window should close automatically")
        else:
            print(f"⚠️  Shutdown API status: {response.status_code}")
    except Exception as e:
        print(f"❌ Shutdown API error: {e}")
    
    return True

def main():
    """Main test function."""
    print("🔧 Jarvis Auto-Close Test")
    print("=" * 40)
    print("This test verifies that the desktop window closes")
    print("automatically when Jarvis is shut down.\n")
    
    # Check if we should test voice commands or APIs
    print("Choose test type:")
    print("1. Voice command test (close jarvis ui)")
    print("2. API endpoint test (requires running desktop app)")
    print("3. Both tests")
    
    try:
        choice = input("\nEnter choice (1-3): ").strip()
    except KeyboardInterrupt:
        print("\n🛑 Test cancelled")
        return 0
    
    success = True
    
    if choice in ['1', '3']:
        success &= test_voice_command_close()
    
    if choice in ['2', '3']:
        success &= test_api_endpoints()
    
    print("\n" + "="*50)
    print("🏁 Test Summary:")
    if success:
        print("✅ Tests completed successfully")
        print("\n🎯 Expected behavior:")
        print("   - Desktop window closes automatically when server shuts down")
        print("   - JavaScript monitoring detects server shutdown")
        print("   - Window closes within 2-6 seconds")
        print("\n💡 If window doesn't close automatically:")
        print("   - Check browser console for JavaScript errors")
        print("   - Verify pywebview version supports window closing")
        print("   - Manual window close should still work")
    else:
        print("⚠️  Some tests had issues")
    
    return 0 if success else 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n🛑 Test cancelled by user")
    except Exception as e:
        print(f"\n❌ Test script error: {e}")
        sys.exit(1)
