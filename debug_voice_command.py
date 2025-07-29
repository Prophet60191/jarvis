#!/usr/bin/env python3
"""
Debug script to test the voice command "open settings" flow.
"""

import sys
import time
import subprocess
import psutil
from pathlib import Path

# Add jarvis to path
sys.path.insert(0, str(Path(__file__).parent / "jarvis"))

def test_tool_import():
    """Test if the tool can be imported and called."""
    print("🔧 Testing Tool Import and Call")
    print("=" * 60)
    
    try:
        from jarvis.tools.plugins.jarvis_ui_tool import open_jarvis_ui
        
        print("✅ Successfully imported open_jarvis_ui")
        
        # Test calling the tool function directly
        print("🧪 Calling open_jarvis_ui('audio')...")
        result = open_jarvis_ui.func('audio')
        
        print(f"📋 Tool result: {result}")
        
        return True
        
    except Exception as e:
        print(f"❌ Tool import/call failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_processes_after_tool_call():
    """Check what processes are running after tool call."""
    print("\n🔍 Checking Processes After Tool Call")
    print("=" * 60)
    
    try:
        # Call the tool
        from jarvis.tools.plugins.jarvis_ui_tool import open_jarvis_ui
        result = open_jarvis_ui.func('audio')
        print(f"Tool result: {result}")
        
        # Wait a moment for processes to start
        print("⏳ Waiting 3 seconds for processes to start...")
        time.sleep(3)
        
        # Check for relevant processes
        relevant_processes = []
        
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = proc.info['cmdline']
                if cmdline:
                    cmdline_str = ' '.join(cmdline)
                    
                    # Look for our processes
                    if any(keyword in cmdline_str for keyword in [
                        'jarvis_settings_app.py',
                        'jarvis_ui.py',
                        'jarvis_app.py'
                    ]):
                        relevant_processes.append({
                            'pid': proc.info['pid'],
                            'name': proc.info['name'],
                            'cmdline': cmdline_str
                        })
                        
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        if relevant_processes:
            print(f"✅ Found {len(relevant_processes)} relevant process(es):")
            for proc in relevant_processes:
                print(f"   PID {proc['pid']}: {proc['cmdline']}")
        else:
            print("❌ No relevant processes found")
            
        return len(relevant_processes) > 0
        
    except Exception as e:
        print(f"❌ Process check failed: {e}")
        return False


def test_file_paths():
    """Test if the tool is looking for the right files."""
    print("\n📁 Testing File Paths")
    print("=" * 60)
    
    try:
        # Check what the tool is actually looking for
        from jarvis.tools.plugins.jarvis_ui_tool import open_jarvis_ui
        
        # Look at the tool source to see what file it's trying to launch
        import inspect
        source = inspect.getsource(open_jarvis_ui.func)
        
        print("🔍 Tool source code snippet:")
        lines = source.split('\n')
        for i, line in enumerate(lines):
            if 'jarvis_settings_app.py' in line or 'desktop_script' in line:
                print(f"   Line {i+1}: {line.strip()}")
        
        # Check if the file exists where the tool expects it
        current_dir = Path(__file__).parent
        expected_path = current_dir / "jarvis_settings_app.py"
        
        print(f"\n📍 Expected file location: {expected_path}")
        print(f"   Exists: {'✅ Yes' if expected_path.exists() else '❌ No'}")
        
        if expected_path.exists():
            print(f"   Size: {expected_path.stat().st_size} bytes")
            print(f"   Executable: {'✅ Yes' if expected_path.stat().st_mode & 0o111 else '❌ No'}")
        
        return expected_path.exists()
        
    except Exception as e:
        print(f"❌ File path test failed: {e}")
        return False


def test_manual_subprocess():
    """Test launching the app manually with subprocess like the tool does."""
    print("\n🚀 Testing Manual Subprocess Launch")
    print("=" * 60)
    
    try:
        desktop_script = Path(__file__).parent / "jarvis_settings_app.py"
        
        if not desktop_script.exists():
            print(f"❌ Script not found: {desktop_script}")
            return False
        
        # Launch exactly like the tool does
        cmd = [sys.executable, str(desktop_script), "--panel", "audio"]
        
        print(f"🚀 Launching: {' '.join(cmd)}")
        
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True
        )
        
        print(f"📋 Process started with PID: {process.pid}")
        
        # Wait a moment
        time.sleep(2)
        
        # Check if process is still running
        if process.poll() is None:
            print("✅ Process is still running")
            
            # Let it run for a few more seconds
            time.sleep(3)
            
            if process.poll() is None:
                print("✅ Process stable after 5 seconds")
                
                # Clean up
                process.terminate()
                process.wait()
                return True
            else:
                print("❌ Process died after 5 seconds")
                return False
        else:
            print("❌ Process died immediately")
            return False
        
    except Exception as e:
        print(f"❌ Manual subprocess test failed: {e}")
        return False


def check_webview_availability():
    """Check if webview is properly available."""
    print("\n🖥️ Checking WebView Availability")
    print("=" * 60)
    
    try:
        import webview
        print("✅ webview module imported successfully")
        
        # Check webview version
        if hasattr(webview, '__version__'):
            print(f"📋 webview version: {webview.__version__}")
        
        # Try to create a simple window (but don't show it)
        try:
            webview.create_window(
                title="Test",
                html="<h1>Test</h1>",
                width=100,
                height=100
            )
            print("✅ webview.create_window() works")
            
            # Clear the window
            webview.windows.clear()
            
            return True
            
        except Exception as e:
            print(f"❌ webview.create_window() failed: {e}")
            return False
        
    except ImportError:
        print("❌ webview module not available")
        return False
    except Exception as e:
        print(f"❌ webview check failed: {e}")
        return False


def provide_diagnosis():
    """Provide diagnosis based on test results."""
    print("\n🔍 Diagnosis and Solutions")
    print("=" * 60)
    
    print("Based on the test results above:")
    print()
    print("🎯 If tool import works but no processes start:")
    print("   • The tool function runs but subprocess.Popen fails silently")
    print("   • Try running with visible output to see errors")
    print()
    print("🎯 If file paths are wrong:")
    print("   • The tool is looking in the wrong location")
    print("   • Need to update the tool's file path logic")
    print()
    print("🎯 If manual subprocess works but tool doesn't:")
    print("   • Issue with how the tool calls subprocess.Popen")
    print("   • May need to adjust the tool's launch method")
    print()
    print("🎯 If webview isn't available:")
    print("   • Need to install or fix pywebview")
    print("   • pip install pywebview")
    print()
    print("🔧 Quick test commands:")
    print("   1. python jarvis_settings_app.py --panel audio")
    print("   2. python -c \"from jarvis.tools.plugins.jarvis_ui_tool import open_jarvis_ui; open_jarvis_ui.func('audio')\"")


def main():
    """Run comprehensive voice command debugging."""
    print("🎤 Voice Command 'Open Settings' Debug")
    print("=" * 60)
    print("Testing why 'Hey Jarvis, open settings' doesn't work")
    print("=" * 60)
    
    tests = [
        ("Tool Import", test_tool_import),
        ("File Paths", test_file_paths),
        ("WebView Availability", check_webview_availability),
        ("Manual Subprocess", test_manual_subprocess),
        ("Process Check", check_processes_after_tool_call),
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
    print("🔍 VOICE COMMAND DEBUG RESULTS")
    print("=" * 60)
    
    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status}: {test_name}")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    provide_diagnosis()


if __name__ == "__main__":
    main()
