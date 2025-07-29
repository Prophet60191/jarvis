#!/usr/bin/env python3
"""
AppManager Debug Tool

This tool helps diagnose why the AppManager isn't properly terminating processes.
It will test the complete lifecycle and identify specific failure points.

Usage:
    python debug_app_manager.py
"""

import sys
import os
import time
import subprocess
import signal
import logging
from pathlib import Path

# Add jarvis to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "jarvis"))

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_basic_subprocess():
    """Test basic subprocess creation and termination."""
    print("\n🧪 Testing Basic Subprocess Management")
    print("=" * 50)
    
    try:
        # Create a simple long-running process
        test_script = """
import time
import signal
import sys

def signal_handler(signum, frame):
    print(f"Received signal {signum}, exiting...")
    sys.exit(0)

signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

print("Test process started, PID:", os.getpid())
try:
    while True:
        time.sleep(1)
        print("Test process running...")
except KeyboardInterrupt:
    print("Test process interrupted")
    sys.exit(0)
"""
        
        # Write test script
        test_file = Path("test_process.py")
        test_file.write_text(test_script)
        
        print(f"📝 Created test script: {test_file.absolute()}")
        
        # Start process
        print("🚀 Starting test process...")
        process = subprocess.Popen([
            sys.executable, str(test_file)
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        print(f"✅ Process started with PID: {process.pid}")
        
        # Let it run for a moment
        time.sleep(2)
        
        # Check if it's running
        if process.poll() is None:
            print("✅ Process is running")
        else:
            print("❌ Process died immediately")
            return False
        
        # Try to terminate gracefully
        print("🛑 Attempting graceful termination...")
        process.terminate()
        
        try:
            process.wait(timeout=5)
            print("✅ Process terminated gracefully")
            success = True
        except subprocess.TimeoutExpired:
            print("⚠️  Graceful termination timed out, force killing...")
            process.kill()
            process.wait()
            print("✅ Process force killed")
            success = False
        
        # Cleanup
        test_file.unlink()
        return success
        
    except Exception as e:
        print(f"❌ Error in basic subprocess test: {e}")
        return False

def test_app_manager():
    """Test the actual AppManager implementation."""
    print("\n🧪 Testing AppManager Implementation")
    print("=" * 50)
    
    try:
        from jarvis.utils.app_manager import get_app_manager
        
        app_manager = get_app_manager()
        if not app_manager:
            print("❌ AppManager not available")
            return False
        
        print("✅ AppManager instance obtained")
        
        # Create a test app script
        test_script = """
import time
import sys
import os
import signal

def signal_handler(signum, frame):
    print(f"AppManager test process received signal {signum}")
    sys.exit(0)

signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

print(f"AppManager test process started, PID: {os.getpid()}")
sys.stdout.flush()

try:
    for i in range(60):  # Run for up to 60 seconds
        time.sleep(1)
        if i % 5 == 0:
            print(f"AppManager test process alive: {i}s")
            sys.stdout.flush()
except KeyboardInterrupt:
    print("AppManager test process interrupted")
    sys.exit(0)
"""
        
        test_file = Path("appmanager_test.py")
        test_file.write_text(test_script)
        
        print(f"📝 Created AppManager test script: {test_file.absolute()}")
        
        # Register the app (fix: no description parameter)
        app_name = "debug_test_app"
        success = app_manager.register_app(
            name=app_name,
            script_path=str(test_file.absolute())
        )

        if not success:
            print("❌ Failed to register app")
            test_file.unlink()
            return False
        print(f"✅ Registered app: {app_name}")
        
        # Check initial status
        status = app_manager.get_app_status(app_name)
        print(f"📊 Initial status: {status}")
        
        # Start the app
        print("🚀 Starting app via AppManager...")
        if app_manager.start_app(app_name):
            print("✅ App started successfully")
        else:
            print("❌ Failed to start app")
            test_file.unlink()
            return False
        
        # Check if it's running
        time.sleep(2)
        if app_manager.is_app_running(app_name):
            print("✅ App is running according to AppManager")
        else:
            print("❌ App not running according to AppManager")
            test_file.unlink()
            return False
        
        # Get detailed status
        status = app_manager.get_app_status(app_name)
        print(f"📊 Running status: {status}")
        
        # Try to stop the app
        print("🛑 Stopping app via AppManager...")
        if app_manager.stop_app(app_name):
            print("✅ App stopped successfully")
            success = True
        else:
            print("❌ Failed to stop app")
            success = False
        
        # Verify it's actually stopped
        time.sleep(1)
        if app_manager.is_app_running(app_name):
            print("❌ App still running after stop command!")
            success = False
        else:
            print("✅ App confirmed stopped")
        
        # Check for zombie processes
        if PSUTIL_AVAILABLE:
            print("🔍 Checking for zombie processes...")
            found_zombies = False
            for proc in psutil.process_iter(['pid', 'name', 'status', 'cmdline']):
                try:
                    if proc.info['cmdline'] and 'appmanager_test.py' in ' '.join(proc.info['cmdline']):
                        print(f"⚠️  Found process: PID {proc.info['pid']}, Status: {proc.info['status']}")
                        if proc.info['status'] == psutil.STATUS_ZOMBIE:
                            print("❌ Found zombie process!")
                            found_zombies = True
                        else:
                            print("❌ Process still alive!")
                            try:
                                proc.terminate()
                                proc.wait(timeout=3)
                            except:
                                proc.kill()
                            found_zombies = True
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            if not found_zombies:
                print("✅ No zombie or lingering processes found")
        
        # Cleanup
        test_file.unlink()
        return success
        
    except Exception as e:
        print(f"❌ Error in AppManager test: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_voice_command_integration():
    """Test how voice commands interact with AppManager."""
    print("\n🧪 Testing Voice Command Integration")
    print("=" * 50)
    
    try:
        # Test the actual voice command tools
        from jarvis.tools.plugins.jarvis_ui_tool import open_jarvis_ui, close_jarvis_ui
        
        print("✅ Voice command tools imported successfully")
        
        # Test opening (this should register and start an app)
        print("🎤 Testing 'open settings' command...")
        result = open_jarvis_ui.invoke({"panel": "settings"})
        print(f"📝 Open result: {result}")
        
        # Wait a moment
        time.sleep(3)
        
        # Check if anything is actually running
        if PSUTIL_AVAILABLE:
            print("🔍 Checking for running UI processes...")
            found_processes = []
            ui_scripts = ['jarvis_settings_app.py', 'jarvis_ui.py']
            
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    cmdline = proc.info['cmdline']
                    if cmdline:
                        cmdline_str = ' '.join(cmdline)
                        for script in ui_scripts:
                            if script in cmdline_str:
                                found_processes.append({
                                    'pid': proc.info['pid'],
                                    'cmdline': cmdline_str
                                })
                                break
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            if found_processes:
                print(f"✅ Found {len(found_processes)} UI processes:")
                for proc in found_processes:
                    print(f"   PID {proc['pid']}: {proc['cmdline']}")
            else:
                print("⚠️  No UI processes found")
        
        # Test closing
        print("🎤 Testing 'close settings' command...")
        result = close_jarvis_ui.invoke({})
        print(f"📝 Close result: {result}")
        
        # Wait and check again
        time.sleep(3)
        
        if PSUTIL_AVAILABLE:
            print("🔍 Checking if processes were actually terminated...")
            remaining_processes = []
            
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    cmdline = proc.info['cmdline']
                    if cmdline:
                        cmdline_str = ' '.join(cmdline)
                        for script in ui_scripts:
                            if script in cmdline_str:
                                remaining_processes.append({
                                    'pid': proc.info['pid'],
                                    'cmdline': cmdline_str
                                })
                                break
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            if remaining_processes:
                print(f"❌ Found {len(remaining_processes)} processes still running:")
                for proc in remaining_processes:
                    print(f"   PID {proc['pid']}: {proc['cmdline']}")
                return False
            else:
                print("✅ All UI processes properly terminated")
                return True
        
        return True
        
    except Exception as e:
        print(f"❌ Error in voice command test: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all debug tests."""
    print("🔧 AppManager Debug Tool")
    print("=" * 60)
    print("This tool will test the AppManager and identify termination issues.")
    print()
    
    if not PSUTIL_AVAILABLE:
        print("⚠️  psutil not available - some tests will be limited")
        print("   Install with: pip install psutil")
        print()
    
    results = {}
    
    # Test 1: Basic subprocess management
    results['basic_subprocess'] = test_basic_subprocess()
    
    # Test 2: AppManager implementation
    results['app_manager'] = test_app_manager()
    
    # Test 3: Voice command integration
    results['voice_commands'] = test_voice_command_integration()
    
    # Summary
    print("\n📊 Debug Results Summary")
    print("=" * 50)
    
    for test_name, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{test_name:20} {status}")
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    
    print(f"\nOverall: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 All tests passed! AppManager appears to be working correctly.")
    else:
        print("🔍 Issues found. Check the detailed output above for specific problems.")
        
        # Provide specific recommendations
        print("\n💡 Recommendations:")
        if not results.get('basic_subprocess'):
            print("- Basic subprocess management is failing")
            print("- Check Python subprocess module and signal handling")
        
        if not results.get('app_manager'):
            print("- AppManager implementation has issues")
            print("- Check process group creation and termination logic")
        
        if not results.get('voice_commands'):
            print("- Voice command integration is not working properly")
            print("- Check app registration and voice command tool implementation")

if __name__ == "__main__":
    main()
