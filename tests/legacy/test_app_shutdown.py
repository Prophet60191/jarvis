#!/usr/bin/env python3
"""
Test script to verify desktop app shutdown fixes.
"""

import subprocess
import time
import signal
import os

def test_app_lifecycle(app_name, script_path):
    """Test that an app can be started and stopped properly."""
    print(f"🧪 Testing {app_name} lifecycle...")
    
    # Start the app
    print(f"  Starting {app_name}...")
    proc = subprocess.Popen([
        "python", script_path, "--panel", "main"
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Give it time to start
    time.sleep(3)
    
    # Check if it's running
    if proc.poll() is None:
        print(f"  ✅ {app_name} started successfully (PID: {proc.pid})")
        
        # Try to terminate gracefully
        print(f"  Sending SIGTERM to {app_name}...")
        proc.terminate()
        
        # Wait for graceful shutdown
        try:
            proc.wait(timeout=5)
            print(f"  ✅ {app_name} shut down gracefully")
            return True
        except subprocess.TimeoutExpired:
            print(f"  ⚠️  {app_name} didn't shut down gracefully, force killing...")
            proc.kill()
            proc.wait()
            return False
    else:
        print(f"  ❌ {app_name} failed to start")
        return False

def main():
    """Test both apps."""
    print("🧪 TESTING DESKTOP APP SHUTDOWN FIXES")
    print("=" * 60)
    
    # Test RAG app
    rag_success = test_app_lifecycle("RAG App", "rag_app.py")
    
    # Test Settings app  
    settings_success = test_app_lifecycle("Settings App", "jarvis/jarvis_settings_app.py")
    
    print("\n🎯 TEST RESULTS:")
    print("=" * 30)
    print(f"RAG App: {'✅ PASS' if rag_success else '❌ FAIL'}")
    print(f"Settings App: {'✅ PASS' if settings_success else '❌ FAIL'}")
    
    if rag_success and settings_success:
        print("\n🎉 All tests passed! Apps should now work properly.")
    else:
        print("\n⚠️  Some tests failed. Manual testing may be needed.")

if __name__ == "__main__":
    main()
