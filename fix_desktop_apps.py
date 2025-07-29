#!/usr/bin/env python3
"""
Fix for desktop applications to handle proper shutdown and restart.
"""

import signal
import sys
import os
import threading
import time
from pathlib import Path

def create_shutdown_handler():
    """Create a proper shutdown handler for desktop applications."""
    
    shutdown_event = threading.Event()
    
    def signal_handler(signum, frame):
        """Handle shutdown signals gracefully."""
        print(f"\n🛑 Received signal {signum}, shutting down gracefully...")
        shutdown_event.set()
        
        # Give webview time to close
        time.sleep(1)
        
        # Force exit if needed
        sys.exit(0)
    
    # Register signal handlers
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    
    return shutdown_event

def patch_rag_app():
    """Patch the RAG app to handle shutdown properly."""
    print("🔧 PATCHING RAG APP FOR PROPER SHUTDOWN")
    print("=" * 60)
    
    rag_app_path = Path("rag_app.py")
    
    if not rag_app_path.exists():
        print("❌ rag_app.py not found")
        return False
    
    # Read the current content
    content = rag_app_path.read_text()
    
    # Check if already patched
    if "shutdown_event" in content:
        print("✅ RAG app already patched")
        return True
    
    # Add signal handling import
    if "import signal" not in content:
        content = content.replace(
            "import threading",
            "import threading\nimport signal"
        )
    
    # Add shutdown handler before webview.start()
    shutdown_patch = '''
        # Add proper shutdown handling
        shutdown_event = threading.Event()
        
        def signal_handler(signum, frame):
            print(f"\\n🛑 RAG app received signal {signum}, shutting down...")
            shutdown_event.set()
            try:
                webview.destroy()
            except:
                pass
            sys.exit(0)
        
        signal.signal(signal.SIGTERM, signal_handler)
        signal.signal(signal.SIGINT, signal_handler)
        
        # Start webview in a way that can be interrupted
        try:'''
    
    # Patch the webview.start() call
    content = content.replace(
        "            if self.debug:\n                webview.start(debug=True)\n            else:\n                webview.start()",
        shutdown_patch + "\n            if self.debug:\n                webview.start(debug=True)\n            else:\n                webview.start()\n        except KeyboardInterrupt:\n            print('\\n🛑 RAG app interrupted')\n            sys.exit(0)"
    )
    
    # Write the patched content
    rag_app_path.write_text(content)
    print("✅ RAG app patched successfully")
    return True

def patch_settings_app():
    """Patch the settings app to handle shutdown properly."""
    print("\n🔧 PATCHING SETTINGS APP FOR PROPER SHUTDOWN")
    print("=" * 60)
    
    settings_app_path = Path("jarvis/jarvis_settings_app.py")
    
    if not settings_app_path.exists():
        print("❌ jarvis_settings_app.py not found")
        return False
    
    # Read the current content
    content = settings_app_path.read_text()
    
    # Check if already patched
    if "shutdown_event" in content:
        print("✅ Settings app already patched")
        return True
    
    # Add signal handling import
    if "import signal" not in content:
        content = content.replace(
            "import threading",
            "import threading\nimport signal"
        )
    
    # Add shutdown handler before webview.start()
    shutdown_patch = '''
        # Add proper shutdown handling
        shutdown_event = threading.Event()
        
        def signal_handler(signum, frame):
            print(f"\\n🛑 Settings app received signal {signum}, shutting down...")
            shutdown_event.set()
            try:
                webview.destroy()
            except:
                pass
            sys.exit(0)
        
        signal.signal(signal.SIGTERM, signal_handler)
        signal.signal(signal.SIGINT, signal_handler)
        
        # Start webview in a way that can be interrupted
        try:'''
    
    # Patch the webview.start() call
    content = content.replace(
        "            if self.debug:\n                webview.start(debug=True)\n            else:\n                webview.start()",
        shutdown_patch + "\n            if self.debug:\n                webview.start(debug=True)\n            else:\n                webview.start()\n        except KeyboardInterrupt:\n            print('\\n🛑 Settings app interrupted')\n            sys.exit(0)"
    )
    
    # Write the patched content
    settings_app_path.write_text(content)
    print("✅ Settings app patched successfully")
    return True

def create_test_script():
    """Create a test script to verify the fixes work."""
    test_script = '''#!/usr/bin/env python3
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
    
    print("\\n🎯 TEST RESULTS:")
    print("=" * 30)
    print(f"RAG App: {'✅ PASS' if rag_success else '❌ FAIL'}")
    print(f"Settings App: {'✅ PASS' if settings_success else '❌ FAIL'}")
    
    if rag_success and settings_success:
        print("\\n🎉 All tests passed! Apps should now work properly.")
    else:
        print("\\n⚠️  Some tests failed. Manual testing may be needed.")

if __name__ == "__main__":
    main()
'''
    
    Path("test_app_shutdown.py").write_text(test_script)
    print("\n✅ Created test_app_shutdown.py")

def main():
    """Main function to apply all fixes."""
    print("🛠️ FIXING DESKTOP APPLICATION SHUTDOWN ISSUES")
    print("=" * 80)
    print("Applying proper signal handling and shutdown mechanisms...")
    print("=" * 80)
    
    # Apply patches
    rag_success = patch_rag_app()
    settings_success = patch_settings_app()
    
    # Create test script
    create_test_script()
    
    print("\n🎯 SUMMARY:")
    print("=" * 30)
    print(f"RAG App Patch: {'✅ SUCCESS' if rag_success else '❌ FAILED'}")
    print(f"Settings App Patch: {'✅ SUCCESS' if settings_success else '❌ FAILED'}")
    
    if rag_success and settings_success:
        print("\n🎉 FIXES APPLIED SUCCESSFULLY!")
        print("=" * 50)
        print("The desktop applications now have proper shutdown handling.")
        print("They should respond to SIGTERM signals and close cleanly.")
        print()
        print("🧪 To test the fixes:")
        print("  python test_app_shutdown.py")
        print()
        print("🚀 To test with Jarvis:")
        print("  1. Restart Jarvis")
        print("  2. Say 'Open vault' → Should work")
        print("  3. Say 'Close vault' → Should close properly")
        print("  4. Say 'Open vault' → Should work again!")
    else:
        print("\n❌ Some patches failed. Manual intervention needed.")

if __name__ == "__main__":
    main()
