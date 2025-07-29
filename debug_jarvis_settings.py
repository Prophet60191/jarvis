#!/usr/bin/env python3
"""
Debug script to diagnose Jarvis Settings opening issues.
"""

import sys
import os
import subprocess
import time
from pathlib import Path

# Add jarvis to path
sys.path.insert(0, str(Path(__file__).parent / "jarvis"))

def check_file_locations():
    """Check if all required files exist."""
    print("📁 Checking File Locations")
    print("=" * 60)
    
    files_to_check = [
        ("jarvis_settings_app.py", Path(__file__).parent / "jarvis_settings_app.py"),
        ("jarvis_ui.py", Path(__file__).parent / "jarvis" / "ui" / "jarvis_ui.py"),
        ("jarvis_ui_tool.py", Path(__file__).parent / "jarvis" / "jarvis" / "tools" / "plugins" / "jarvis_ui_tool.py"),
    ]
    
    all_exist = True
    
    for name, path in files_to_check:
        if path.exists():
            print(f"✅ {name}: {path}")
        else:
            print(f"❌ {name}: MISSING - {path}")
            all_exist = False
    
    return all_exist


def test_direct_launch():
    """Test launching the settings app directly."""
    print("\n🚀 Testing Direct Launch")
    print("=" * 60)
    
    try:
        app_script = Path(__file__).parent / "jarvis_settings_app.py"
        
        if not app_script.exists():
            print(f"❌ Settings app not found: {app_script}")
            return False
        
        print(f"Launching: {app_script}")
        
        # Test with verbose output
        cmd = [sys.executable, str(app_script), "--panel", "audio", "--debug"]
        
        print(f"Command: {' '.join(cmd)}")
        
        # Launch and capture output
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        print(f"Return code: {result.returncode}")
        print(f"STDOUT:\n{result.stdout}")
        print(f"STDERR:\n{result.stderr}")
        
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print("⏰ Process timed out (this might be normal for GUI apps)")
        return True
    except Exception as e:
        print(f"❌ Direct launch failed: {e}")
        return False


def test_tool_function():
    """Test the Jarvis UI tool function."""
    print("\n🔧 Testing Tool Function")
    print("=" * 60)
    
    try:
        from jarvis.tools.plugins.jarvis_ui_tool import open_jarvis_ui
        
        print("✅ Successfully imported open_jarvis_ui")
        
        # Test the function
        result = open_jarvis_ui.func("audio")
        print(f"Tool result: {result}")
        
        # Check if any processes were started
        time.sleep(2)
        
        import psutil
        ui_processes = []
        
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = proc.info['cmdline']
                if cmdline:
                    cmdline_str = ' '.join(cmdline)
                    if 'jarvis_settings_app.py' in cmdline_str:
                        ui_processes.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        if ui_processes:
            print(f"✅ Found {len(ui_processes)} settings app process(es)")
            for proc in ui_processes:
                print(f"   PID {proc['pid']}: {' '.join(proc['cmdline'])}")
        else:
            print("❌ No settings app processes found")
        
        return len(ui_processes) > 0
        
    except Exception as e:
        print(f"❌ Tool function test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_dependencies():
    """Check if all dependencies are available."""
    print("\n📦 Checking Dependencies")
    print("=" * 60)
    
    dependencies = [
        "webview",
        "requests", 
        "psutil"
    ]
    
    all_available = True
    
    for dep in dependencies:
        try:
            __import__(dep)
            print(f"✅ {dep}")
        except ImportError:
            print(f"❌ {dep} - MISSING")
            all_available = False
    
    return all_available


def check_ui_server():
    """Check if the UI server can start."""
    print("\n🌐 Testing UI Server")
    print("=" * 60)
    
    try:
        ui_script = Path(__file__).parent / "jarvis" / "ui" / "jarvis_ui.py"
        
        if not ui_script.exists():
            print(f"❌ UI script not found: {ui_script}")
            return False
        
        # Try to start the UI server
        cmd = [sys.executable, str(ui_script), "--port", "8081", "--no-browser"]
        
        print(f"Testing UI server: {' '.join(cmd)}")
        
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait a bit for server to start
        time.sleep(3)
        
        # Check if process is still running
        if process.poll() is None:
            print("✅ UI server started successfully")
            
            # Test if server responds
            try:
                import requests
                response = requests.get("http://localhost:8081", timeout=5)
                print(f"✅ Server responds with status: {response.status_code}")
                server_works = True
            except Exception as e:
                print(f"❌ Server not responding: {e}")
                server_works = False
            
            # Clean up
            process.terminate()
            process.wait()
            
            return server_works
        else:
            stdout, stderr = process.communicate()
            print(f"❌ UI server failed to start")
            print(f"STDOUT: {stdout}")
            print(f"STDERR: {stderr}")
            return False
        
    except Exception as e:
        print(f"❌ UI server test failed: {e}")
        return False


def provide_solutions():
    """Provide solutions based on test results."""
    print("\n💡 Solutions")
    print("=" * 60)
    
    print("🔧 Troubleshooting Steps:")
    print("1. Check if pywebview is installed:")
    print("   pip install pywebview")
    print()
    print("2. Try launching manually:")
    print("   python jarvis_settings_app.py --panel audio")
    print()
    print("3. Check if UI server works:")
    print("   python jarvis/ui/jarvis_ui.py --port 8080")
    print()
    print("4. Test the tool directly:")
    print("   python -c \"from jarvis.tools.plugins.jarvis_ui_tool import open_jarvis_ui; print(open_jarvis_ui.func('audio'))\"")
    print()
    print("5. Check for error messages in Jarvis logs")
    print()
    print("🎯 Common Issues:")
    print("• Missing pywebview dependency")
    print("• Port conflicts (8080 already in use)")
    print("• File path issues")
    print("• Permission problems")


def main():
    """Run comprehensive diagnostics."""
    print("🔍 Jarvis Settings Opening Diagnostics")
    print("=" * 60)
    print("Diagnosing why Jarvis settings won't open")
    print("=" * 60)
    
    tests = [
        ("File Locations", check_file_locations),
        ("Dependencies", check_dependencies),
        ("UI Server", check_ui_server),
        ("Tool Function", test_tool_function),
        ("Direct Launch", test_direct_launch),
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
    print("🔍 DIAGNOSTIC RESULTS")
    print("=" * 60)
    
    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status}: {test_name}")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed < total:
        provide_solutions()
    else:
        print("🎉 All diagnostics passed! Settings should be working.")


if __name__ == "__main__":
    main()
