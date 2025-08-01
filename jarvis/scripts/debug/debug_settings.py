#!/usr/bin/env python3
"""
Debug Settings App Opening

This script helps debug why the settings app might not be opening.
"""

import sys
import os
import subprocess
import time
import requests
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def check_pywebview():
    """Check if pywebview is available."""
    try:
        import webview
        print("✅ pywebview is available")
        return True
    except ImportError:
        print("❌ pywebview is not available")
        print("   Install with: pip install pywebview")
        return False

def check_desktop_app_files():
    """Check if desktop app files exist."""
    files_to_check = [
        "jarvis_app.py",
        "ui/jarvis_ui.py"
    ]
    
    for file in files_to_check:
        if Path(file).exists():
            print(f"✅ {file} exists")
        else:
            print(f"❌ {file} missing")
            return False
    return True

def test_manual_launch():
    """Test launching the desktop app manually."""
    print("\n🧪 Testing manual desktop app launch...")
    
    try:
        # Launch desktop app
        process = subprocess.Popen(
            [sys.executable, "jarvis_app.py", "--panel", "settings"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        print("🚀 Desktop app launched, waiting for server...")
        
        # Wait for server to start
        for i in range(10):
            try:
                response = requests.get("http://localhost:8080/settings", timeout=2)
                if response.status_code == 200:
                    print("✅ Server is responding")
                    print("✅ Desktop app should be visible on screen")
                    
                    # Keep it running for a moment
                    print("⏳ Keeping app running for 5 seconds...")
                    time.sleep(5)
                    
                    # Clean shutdown
                    try:
                        requests.post("http://localhost:8080/api/shutdown", timeout=2)
                    except:
                        pass
                    
                    process.terminate()
                    process.wait(timeout=5)
                    print("✅ Desktop app closed cleanly")
                    return True
                    
            except requests.exceptions.RequestException:
                time.sleep(1)
        
        print("❌ Server did not respond within 10 seconds")
        process.terminate()
        return False
        
    except Exception as e:
        print(f"❌ Error launching desktop app: {e}")
        return False

def test_voice_command():
    """Test the voice command function directly."""
    print("\n🧪 Testing voice command function...")
    
    try:
        from tools.plugins.jarvis_ui_tool import open_jarvis_ui
        
        # Test the function
        result = open_jarvis_ui.invoke({"panel": "settings"})
        print(f"Voice command result: {result}")
        
        if "desktop app" in result.lower():
            print("✅ Voice command is configured for desktop app")
            return True
        else:
            print("⚠️  Voice command may not be using desktop app")
            return False
            
    except Exception as e:
        print(f"❌ Error testing voice command: {e}")
        return False

def check_processes():
    """Check for running Jarvis processes."""
    print("\n🔍 Checking for running Jarvis processes...")
    
    try:
        result = subprocess.run(
            ["ps", "aux"],
            capture_output=True,
            text=True
        )
        
        jarvis_processes = []
        for line in result.stdout.split('\n'):
            if 'jarvis' in line.lower() and ('python' in line or '.py' in line):
                jarvis_processes.append(line.strip())
        
        if jarvis_processes:
            print(f"Found {len(jarvis_processes)} Jarvis process(es):")
            for proc in jarvis_processes:
                print(f"  📋 {proc}")
        else:
            print("✅ No Jarvis processes currently running")
            
        return len(jarvis_processes)
        
    except Exception as e:
        print(f"❌ Error checking processes: {e}")
        return 0

def main():
    """Main debug function."""
    print("🔧 Jarvis Settings App Debug")
    print("=" * 50)
    
    # Run all checks
    checks = [
        ("pywebview availability", check_pywebview),
        ("Desktop app files", check_desktop_app_files),
        ("Voice command function", test_voice_command),
    ]
    
    print("🔍 Running preliminary checks...")
    for check_name, check_func in checks:
        print(f"\n{check_name}:")
        try:
            result = check_func()
            if not result:
                print(f"⚠️  Issue found with {check_name}")
        except Exception as e:
            print(f"❌ Error in {check_name}: {e}")
    
    # Check for running processes
    running_processes = check_processes()
    
    if running_processes > 0:
        print("\n⚠️  There are Jarvis processes running.")
        print("   This might prevent the settings app from opening.")
        print("   Try closing them first with: python close_ui.py")
    
    # Test manual launch
    print("\n" + "="*50)
    print("🧪 MANUAL LAUNCH TEST")
    print("This will launch the desktop app for 5 seconds...")
    input("Press Enter to continue (or Ctrl+C to skip): ")
    
    success = test_manual_launch()
    
    print("\n📊 Debug Summary:")
    if success:
        print("✅ Desktop app can be launched manually")
        print("✅ If voice command isn't working, try restarting Jarvis")
    else:
        print("❌ Desktop app failed to launch")
        print("   Check the error messages above for clues")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n🛑 Debug cancelled by user")
    except Exception as e:
        print(f"\n❌ Debug script error: {e}")
