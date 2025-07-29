#!/usr/bin/env python3
"""
Test launching the desktop app exactly like the tool does.
"""

import sys
import subprocess
import time
from pathlib import Path

def test_tool_style_launch():
    """Test launching exactly like the tool does."""
    print("🚀 Testing Tool-Style Launch")
    print("=" * 60)
    
    try:
        desktop_script = Path(__file__).parent / "jarvis_settings_app.py"
        
        if not desktop_script.exists():
            print(f"❌ Script not found: {desktop_script}")
            return False
        
        print(f"📍 Script location: {desktop_script}")
        
        # Launch exactly like the improved tool does
        cmd = [sys.executable, str(desktop_script), "--panel", "audio"]
        
        print(f"🚀 Command: {' '.join(cmd)}")
        
        # Launch with visible output for debugging (like the improved tool)
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            start_new_session=True,
            text=True
        )
        
        print(f"📋 Process started with PID: {process.pid}")
        
        # Wait 1 second like the tool does
        print("⏳ Waiting 1 second...")
        time.sleep(1)
        
        if process.poll() is None:
            print("✅ Process is still running after 1 second")
            
            # Let it run a bit longer to see if it's stable
            print("⏳ Waiting 3 more seconds...")
            time.sleep(3)
            
            if process.poll() is None:
                print("✅ Process is stable after 4 seconds total")
                print("🎉 Desktop app launched successfully!")
                
                # Clean up
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                
                return True
            else:
                stdout, stderr = process.communicate()
                print("❌ Process died after 4 seconds")
                print(f"STDOUT: {stdout}")
                print(f"STDERR: {stderr}")
                return False
        else:
            # Process died immediately
            stdout, stderr = process.communicate()
            print("❌ Process died immediately")
            print(f"STDOUT: {stdout}")
            print(f"STDERR: {stderr}")
            return False
        
    except Exception as e:
        print(f"❌ Tool-style launch failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_background_launch():
    """Test launching in background like the original tool."""
    print("\n🌙 Testing Background Launch")
    print("=" * 60)
    
    try:
        desktop_script = Path(__file__).parent / "jarvis_settings_app.py"
        
        cmd = [sys.executable, str(desktop_script), "--panel", "audio"]
        
        print(f"🚀 Background command: {' '.join(cmd)}")
        
        # Launch like the original tool (completely in background)
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True
        )
        
        print(f"📋 Background process started with PID: {process.pid}")
        
        # Wait and check
        time.sleep(2)
        
        if process.poll() is None:
            print("✅ Background process is running")
            
            # Check if we can see it in process list
            import psutil
            try:
                proc = psutil.Process(process.pid)
                print(f"✅ Process found in system: {proc.name()}")
                
                # Clean up
                process.terminate()
                process.wait()
                
                return True
            except psutil.NoSuchProcess:
                print("❌ Process not found in system")
                return False
        else:
            print("❌ Background process died")
            return False
        
    except Exception as e:
        print(f"❌ Background launch failed: {e}")
        return False


def test_environment_differences():
    """Test if there are environment differences."""
    print("\n🌍 Testing Environment Differences")
    print("=" * 60)
    
    try:
        import os
        
        print("📋 Current environment:")
        print(f"   Python: {sys.executable}")
        print(f"   Working dir: {os.getcwd()}")
        print(f"   PATH: {os.environ.get('PATH', 'Not set')[:100]}...")
        
        # Check if DISPLAY is set (important for GUI apps)
        display = os.environ.get('DISPLAY')
        print(f"   DISPLAY: {display if display else 'Not set'}")
        
        # Check if we're in a GUI environment
        try:
            import tkinter
            root = tkinter.Tk()
            root.withdraw()  # Hide the window
            root.destroy()
            print("✅ GUI environment available (tkinter works)")
        except Exception as e:
            print(f"❌ GUI environment issue: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Environment check failed: {e}")
        return False


def main():
    """Test different launch methods."""
    print("🧪 Desktop App Launch Method Test")
    print("=" * 60)
    print("Testing why the tool launch fails but direct launch works")
    print("=" * 60)
    
    tests = [
        ("Environment Check", test_environment_differences),
        ("Tool-Style Launch", test_tool_style_launch),
        ("Background Launch", test_background_launch),
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
    print("🧪 LAUNCH METHOD TEST RESULTS")
    print("=" * 60)
    
    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status}: {test_name}")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if results[1][1]:  # Tool-style launch works
        print("\n🎉 Tool-style launch works!")
        print("   The issue might be in the tool's error detection logic")
    elif results[2][1]:  # Background launch works
        print("\n🎯 Background launch works!")
        print("   The issue is that the tool expects immediate success")
    else:
        print("\n❌ Both launch methods fail")
        print("   There's a deeper issue with the desktop app")


if __name__ == "__main__":
    main()
