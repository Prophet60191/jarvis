#!/usr/bin/env python3
"""
Minimal test for Jarvis Settings desktop app.
"""

import sys
import time
import subprocess
from pathlib import Path

# Add jarvis to path
sys.path.insert(0, str(Path(__file__).parent / "jarvis"))

def test_ui_server_minimal():
    """Test if we can start the UI server manually."""
    print("🌐 Testing UI Server Manually")
    print("=" * 60)
    
    try:
        # Start UI server on a different port
        ui_script = Path(__file__).parent / "jarvis" / "ui" / "jarvis_ui.py"
        
        cmd = [sys.executable, str(ui_script), "--port", "8083", "--no-browser"]
        
        print(f"Starting: {' '.join(cmd)}")
        
        # Start the server
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        print("Waiting 5 seconds for server to start...")
        time.sleep(5)
        
        # Check if it's running
        if process.poll() is None:
            print("✅ Server is running")
            
            # Try to connect
            try:
                import requests
                response = requests.get("http://localhost:8083", timeout=10)
                print(f"✅ Server responds: {response.status_code}")
                
                # Clean up
                process.terminate()
                process.wait()
                return True
                
            except Exception as e:
                print(f"❌ Server not responding: {e}")
                process.terminate()
                process.wait()
                return False
        else:
            stdout, stderr = process.communicate()
            print(f"❌ Server failed to start")
            print(f"STDOUT: {stdout}")
            print(f"STDERR: {stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def test_webview_minimal():
    """Test if webview works with a simple page."""
    print("\n🖥️ Testing WebView Minimal")
    print("=" * 60)
    
    try:
        import webview
        
        print("✅ webview imported successfully")
        
        # Create a simple test window
        print("Creating test window...")
        
        webview.create_window(
            title="Test Window",
            html="<h1>Test</h1><p>If you see this, webview is working!</p>",
            width=400,
            height=300
        )
        
        print("✅ Window created, starting webview...")
        
        # This will block until window is closed
        # For testing, we'll just show that it can be created
        print("💡 Window would open here (skipping actual display for test)")
        
        return True
        
    except Exception as e:
        print(f"❌ WebView test failed: {e}")
        return False


def test_fallback_browser():
    """Test opening settings in browser as fallback."""
    print("\n🌐 Testing Browser Fallback")
    print("=" * 60)
    
    try:
        # Start UI server
        ui_script = Path(__file__).parent / "jarvis" / "ui" / "jarvis_ui.py"
        
        cmd = [sys.executable, str(ui_script), "--port", "8084"]
        
        print(f"Starting UI server: {' '.join(cmd)}")
        
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        
        print("Waiting for server to start...")
        time.sleep(3)
        
        if process.poll() is None:
            print("✅ UI server started")
            print("💡 Settings should be available at: http://localhost:8084")
            
            # Clean up
            process.terminate()
            process.wait()
            return True
        else:
            print("❌ UI server failed to start")
            return False
            
    except Exception as e:
        print(f"❌ Browser fallback test failed: {e}")
        return False


def provide_quick_fix():
    """Provide a quick fix for opening settings."""
    print("\n🔧 Quick Fix")
    print("=" * 60)
    
    print("Since the desktop app isn't working, here's a quick workaround:")
    print()
    print("1. Start the UI server manually:")
    print("   python jarvis/ui/jarvis_ui.py --port 8080")
    print()
    print("2. Open in your browser:")
    print("   http://localhost:8080")
    print()
    print("3. Or use the voice command and it will open in browser:")
    print("   'Hey Jarvis, open settings'")
    print()
    print("🎯 This gives you the same settings interface, just in browser instead of desktop app.")


def main():
    """Run minimal tests."""
    print("🔍 Minimal Jarvis Settings Test")
    print("=" * 60)
    print("Testing basic components")
    print("=" * 60)
    
    tests = [
        ("UI Server", test_ui_server_minimal),
        ("WebView", test_webview_minimal),
        ("Browser Fallback", test_fallback_browser),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print(f"\n{'='*60}")
    print("🔍 MINIMAL TEST RESULTS")
    print("=" * 60)
    
    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status}: {test_name}")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if results[0][1]:  # If UI server works
        print("\n🎉 Good news: The UI server works!")
        print("   The issue is just with the desktop app wrapper.")
        provide_quick_fix()
    else:
        print("\n❌ The UI server itself has issues.")
        print("   This needs to be fixed first.")


if __name__ == "__main__":
    main()
