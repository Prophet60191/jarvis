#!/usr/bin/env python3
"""
Simple test to verify window close behavior
"""

import sys
import time
import requests
import threading
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def check_server():
    """Check if server is running."""
    try:
        response = requests.get("http://localhost:8080/", timeout=2)
        return response.status_code == 200
    except:
        return False

def monitor_server():
    """Monitor server status."""
    print("🔍 Monitoring server status...")
    while True:
        if check_server():
            print("📡 Server is running")
        else:
            print("🔴 Server is not running")
            break
        time.sleep(2)

def main():
    """Test the desktop app."""
    print("🧪 Testing Desktop App Window Close")
    print("=" * 40)
    
    # Start monitoring in background
    monitor_thread = threading.Thread(target=monitor_server, daemon=True)
    monitor_thread.start()
    
    # Import and run desktop app
    try:
        from jarvis_app import JarvisDesktopApp
        
        print("🚀 Starting desktop app...")
        print("📋 Please close the window manually to test shutdown")
        
        app = JarvisDesktopApp(panel="main", port=8080)
        app.run()  # This blocks until window is closed
        
        print("✅ Desktop app has exited")
        
        # Check if server stopped
        time.sleep(1)
        if check_server():
            print("❌ Server is still running")
        else:
            print("✅ Server stopped correctly")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
