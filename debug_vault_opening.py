#!/usr/bin/env python3
"""
Debug why the vault isn't opening even though Jarvis recognizes the phrase.
"""

import sys
import time
import subprocess
import psutil
from pathlib import Path

# Add jarvis to path
sys.path.insert(0, str(Path(__file__).parent / "jarvis"))

def test_vault_tool_call():
    """Test calling the vault tool directly."""
    print("🔧 Testing Direct Vault Tool Call")
    print("=" * 60)
    
    try:
        from jarvis.tools.plugins.rag_ui_tool import open_rag_manager
        
        print("✅ Successfully imported open_rag_manager")
        
        # Call the tool directly
        print("🧪 Calling open_rag_manager()...")
        result = open_rag_manager.func()
        
        print(f"📋 Tool result: {result}")
        
        # Check if the result indicates success
        if "vault" in result.lower() and "desktop app" in result.lower():
            print("✅ Tool returned success message")
            return True
        else:
            print("❌ Tool returned unexpected message")
            return False
        
    except Exception as e:
        print(f"❌ Direct tool call failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_rag_app_file():
    """Check if the rag_app.py file exists where the tool expects it."""
    print("\n📁 Checking RAG App File Location")
    print("=" * 60)
    
    try:
        from jarvis.tools.plugins.rag_ui_tool import open_rag_manager
        
        # Get the expected path from the tool
        import os
        plugin_file = open_rag_manager.func.__code__.co_filename
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(plugin_file)))))
        rag_app_path = os.path.join(project_root, "rag_app.py")
        
        print(f"📍 Tool expects rag_app.py at: {rag_app_path}")
        print(f"   Exists: {'✅ Yes' if os.path.exists(rag_app_path) else '❌ No'}")
        
        if os.path.exists(rag_app_path):
            # Check file details
            stat = os.stat(rag_app_path)
            print(f"   Size: {stat.st_size} bytes")
            print(f"   Readable: {'✅ Yes' if os.access(rag_app_path, os.R_OK) else '❌ No'}")
            return True
        else:
            # Check if it exists elsewhere
            possible_locations = [
                Path(__file__).parent / "rag_app.py",
                Path(__file__).parent / "jarvis" / "rag_app.py",
            ]
            
            print("\n🔍 Checking alternative locations:")
            for location in possible_locations:
                exists = location.exists()
                print(f"   {location}: {'✅ Found' if exists else '❌ Not found'}")
                if exists:
                    print(f"      Size: {location.stat().st_size} bytes")
            
            return False
        
    except Exception as e:
        print(f"❌ File check failed: {e}")
        return False


def test_manual_rag_app_launch():
    """Test launching rag_app.py manually."""
    print("\n🚀 Testing Manual RAG App Launch")
    print("=" * 60)
    
    try:
        # Find rag_app.py
        possible_locations = [
            Path(__file__).parent / "rag_app.py",
            Path(__file__).parent / "jarvis" / "rag_app.py",
        ]
        
        rag_app_path = None
        for location in possible_locations:
            if location.exists():
                rag_app_path = location
                break
        
        if not rag_app_path:
            print("❌ rag_app.py not found in any expected location")
            return False
        
        print(f"📍 Found rag_app.py at: {rag_app_path}")
        
        # Try to launch it
        cmd = [sys.executable, str(rag_app_path), "--panel", "main"]
        
        print(f"🚀 Launching: {' '.join(cmd)}")
        
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait a moment
        time.sleep(3)
        
        if process.poll() is None:
            print("✅ RAG app is running!")
            
            # Clean up
            process.terminate()
            process.wait()
            return True
        else:
            stdout, stderr = process.communicate()
            print("❌ RAG app failed to start")
            print(f"STDOUT: {stdout}")
            print(f"STDERR: {stderr}")
            return False
        
    except Exception as e:
        print(f"❌ Manual launch test failed: {e}")
        return False


def check_vault_processes():
    """Check if any vault/RAG processes are running."""
    print("\n🔍 Checking for Vault/RAG Processes")
    print("=" * 60)
    
    try:
        vault_processes = []
        
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = proc.info['cmdline']
                if cmdline:
                    cmdline_str = ' '.join(cmdline)
                    if 'rag_app.py' in cmdline_str:
                        vault_processes.append({
                            'pid': proc.info['pid'],
                            'name': proc.info['name'],
                            'cmdline': cmdline_str
                        })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        if vault_processes:
            print(f"✅ Found {len(vault_processes)} vault process(es):")
            for proc in vault_processes:
                print(f"   PID {proc['pid']}: {proc['cmdline']}")
            return True
        else:
            print("❌ No vault processes found")
            return False
        
    except Exception as e:
        print(f"❌ Process check failed: {e}")
        return False


def test_webview_availability():
    """Test if webview is available for the desktop app."""
    print("\n🖥️ Testing WebView Availability")
    print("=" * 60)
    
    try:
        import webview
        print("✅ webview module imported successfully")
        
        # Test creating a window
        webview.create_window(
            title="Test",
            html="<h1>Test</h1>",
            width=100,
            height=100
        )
        print("✅ webview.create_window() works")
        
        # Clear test window
        webview.windows.clear()
        
        return True
        
    except ImportError:
        print("❌ webview module not available")
        return False
    except Exception as e:
        print(f"❌ webview test failed: {e}")
        return False


def provide_vault_fix():
    """Provide solutions for vault opening issues."""
    print("\n🔧 Vault Opening Fix")
    print("=" * 60)
    
    print("Based on the test results, here are potential fixes:")
    print()
    print("1. **Missing rag_app.py file:**")
    print("   • The vault tool can't find rag_app.py")
    print("   • Check if rag_app.py exists in the project root")
    print("   • May need to create or move the file")
    print()
    print("2. **File path issues:**")
    print("   • Tool looking in wrong location")
    print("   • Update tool's path calculation")
    print()
    print("3. **WebView issues:**")
    print("   • pywebview not working properly")
    print("   • Try: pip install --upgrade pywebview")
    print()
    print("4. **Process launch issues:**")
    print("   • App starts but dies immediately")
    print("   • Check rag_app.py for errors")
    print()
    print("🎯 Quick tests:")
    print("   1. python rag_app.py (if it exists)")
    print("   2. Check Jarvis logs for error messages")
    print("   3. Try restarting Jarvis completely")


def main():
    """Debug vault opening issues."""
    print("🏛️ Vault Opening Debug")
    print("=" * 60)
    print("Diagnosing why vault doesn't open despite recognition")
    print("=" * 60)
    
    tests = [
        ("Direct Tool Call", test_vault_tool_call),
        ("RAG App File Check", check_rag_app_file),
        ("WebView Availability", test_webview_availability),
        ("Manual RAG App Launch", test_manual_rag_app_launch),
        ("Vault Processes", check_vault_processes),
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
    print("🏛️ VAULT OPENING DEBUG RESULTS")
    print("=" * 60)
    
    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status}: {test_name}")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed < total:
        provide_vault_fix()
    else:
        print("\n🎉 All tests passed - vault should be working!")


if __name__ == "__main__":
    main()
