#!/usr/bin/env python3
"""
Test Window Close Behavior

This script tests whether manually closing the desktop app window
properly shuts down the web server.
"""

import sys
import time
import requests
import subprocess
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def check_server_running(port=8080):
    """Check if the web server is running on the specified port."""
    try:
        response = requests.get(f"http://localhost:{port}/", timeout=2)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

def test_window_close_behavior():
    """Test the window close behavior."""
    print("🧪 Testing Desktop App Window Close Behavior")
    print("=" * 60)
    
    # Start the desktop app
    print("🚀 Starting desktop app...")
    process = subprocess.Popen(
        [sys.executable, "jarvis_app.py", "--panel", "main"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait for server to start
    print("⏳ Waiting for server to start...")
    for i in range(10):
        if check_server_running():
            print("✅ Server is running")
            break
        time.sleep(1)
    else:
        print("❌ Server failed to start within 10 seconds")
        process.terminate()
        return False
    
    print("\n📋 Instructions:")
    print("1. A desktop window should have opened")
    print("2. Please MANUALLY CLOSE the window (click the X button)")
    print("3. This test will check if the server shuts down properly")
    print("\n⏳ Waiting for you to close the window...")
    
    # Wait for the process to finish (when window is closed)
    try:
        process.wait(timeout=60)  # Wait up to 60 seconds
        print("✅ Desktop app process has ended")
    except subprocess.TimeoutExpired:
        print("⏰ Timeout waiting for window to close")
        process.terminate()
        return False
    
    # Check if server is still running
    print("🔍 Checking if web server stopped...")
    time.sleep(2)  # Give it a moment to shut down
    
    if check_server_running():
        print("❌ FAIL: Web server is still running after window close")
        print("   This means the server didn't shut down properly")
        
        # Try to stop it manually
        try:
            requests.post("http://localhost:8080/api/shutdown", timeout=5)
        except:
            pass
        
        return False
    else:
        print("✅ SUCCESS: Web server stopped when window was closed")
        return True

def main():
    """Main test function."""
    print("🤖 Jarvis Desktop App Window Close Test")
    print("This test verifies that closing the window shuts down the app")
    print()
    
    success = test_window_close_behavior()
    
    print("\n📊 Test Result:")
    if success:
        print("✅ PASS: Window close properly shuts down the app")
        print("   Users can safely close the window to exit the app")
    else:
        print("❌ FAIL: Window close doesn't shut down the app properly")
        print("   The web server may continue running in the background")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
