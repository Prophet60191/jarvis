#!/usr/bin/env python3
"""
Debug script for RAG Management UI consistency issues.
"""

import sys
import time
import subprocess
import psutil
from pathlib import Path

# Add jarvis to path
sys.path.insert(0, str(Path(__file__).parent / "jarvis"))

def test_rag_tool_import():
    """Test if the RAG tool can be imported."""
    print("🔧 Testing RAG Tool Import")
    print("=" * 60)
    
    try:
        from jarvis.tools.plugins.rag_tool import open_rag_manager
        
        print("✅ Successfully imported open_rag_manager")
        
        # Check the tool function
        print(f"📋 Tool function: {open_rag_manager.func}")
        print(f"📋 Tool description: {open_rag_manager.description[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ RAG tool import failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_rag_app_file():
    """Test if the RAG app file exists and is accessible."""
    print("\n📁 Testing RAG App File")
    print("=" * 60)
    
    try:
        # Check where the RAG tool expects the app to be
        from jarvis.tools.plugins.rag_tool import open_rag_manager
        
        # Get the plugin file location to calculate expected path
        import os
        plugin_file = open_rag_manager.func.__code__.co_filename
        jarvis_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(plugin_file))))
        rag_app_path = os.path.join(jarvis_dir, "rag_app.py")
        
        print(f"📍 Expected RAG app location: {rag_app_path}")
        print(f"   Exists: {'✅ Yes' if os.path.exists(rag_app_path) else '❌ No'}")
        
        if os.path.exists(rag_app_path):
            # Check file size and permissions
            stat = os.stat(rag_app_path)
            print(f"   Size: {stat.st_size} bytes")
            print(f"   Readable: {'✅ Yes' if os.access(rag_app_path, os.R_OK) else '❌ No'}")
            print(f"   Executable: {'✅ Yes' if stat.st_mode & 0o111 else '❌ No'}")
            
            return True
        else:
            print("❌ RAG app file not found")
            return False
        
    except Exception as e:
        print(f"❌ RAG app file check failed: {e}")
        return False


def test_multiple_rag_launches():
    """Test launching RAG UI multiple times to check consistency."""
    print("\n🔄 Testing Multiple RAG Launches")
    print("=" * 60)
    
    try:
        from jarvis.tools.plugins.rag_tool import open_rag_manager
        
        success_count = 0
        total_attempts = 5
        
        for i in range(1, total_attempts + 1):
            print(f"\n🧪 Attempt {i}/{total_attempts}:")
            
            try:
                # Call the RAG tool
                result = open_rag_manager.func()
                print(f"   Result: {result}")
                
                # Wait a moment
                time.sleep(2)
                
                # Check if RAG processes are running
                rag_processes = []
                for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                    try:
                        cmdline = proc.info['cmdline']
                        if cmdline and 'rag_app.py' in ' '.join(cmdline):
                            rag_processes.append(proc.info['pid'])
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
                
                if rag_processes:
                    print(f"   ✅ Found RAG process(es): {rag_processes}")
                    success_count += 1
                    
                    # Clean up processes for next test
                    for pid in rag_processes:
                        try:
                            proc = psutil.Process(pid)
                            proc.terminate()
                        except:
                            pass
                else:
                    print(f"   ❌ No RAG processes found")
                
                # Wait between attempts
                if i < total_attempts:
                    time.sleep(1)
                
            except Exception as e:
                print(f"   ❌ Launch failed: {e}")
        
        print(f"\n📊 Results: {success_count}/{total_attempts} successful launches")
        
        if success_count == total_attempts:
            print("✅ RAG UI launches consistently")
            return True
        elif success_count > 0:
            print("⚠️  RAG UI launches inconsistently")
            return False
        else:
            print("❌ RAG UI never launches")
            return False
        
    except Exception as e:
        print(f"❌ Multiple launch test failed: {e}")
        return False


def test_rag_dependencies():
    """Test if RAG dependencies are available."""
    print("\n📦 Testing RAG Dependencies")
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
    
    # Test webview specifically
    try:
        import webview
        
        # Try creating a test window
        webview.create_window(
            title="Test",
            html="<h1>Test</h1>",
            width=100,
            height=100
        )
        print("✅ webview.create_window() works")
        
        # Clear test window
        webview.windows.clear()
        
    except Exception as e:
        print(f"❌ webview functionality issue: {e}")
        all_available = False
    
    return all_available


def check_port_conflicts():
    """Check for port conflicts that might affect RAG UI."""
    print("\n🌐 Checking Port Conflicts")
    print("=" * 60)
    
    try:
        import socket
        
        # Check common ports that RAG might use
        ports_to_check = [8080, 8081, 8082, 8083, 8084, 8085]
        
        for port in ports_to_check:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('localhost', port))
                    print(f"✅ Port {port}: Available")
            except OSError:
                print(f"❌ Port {port}: In use")
        
        return True
        
    except Exception as e:
        print(f"❌ Port check failed: {e}")
        return False


def provide_rag_solutions():
    """Provide solutions for RAG UI consistency issues."""
    print("\n💡 RAG UI Consistency Solutions")
    print("=" * 60)
    
    print("🔧 Common fixes for inconsistent RAG UI:")
    print()
    print("1. **Process Cleanup**:")
    print("   • Kill any stuck RAG processes")
    print("   • pkill -f rag_app.py")
    print()
    print("2. **Port Issues**:")
    print("   • RAG UI might be trying to use busy ports")
    print("   • Restart Jarvis to clear port usage")
    print()
    print("3. **File Permissions**:")
    print("   • Make sure rag_app.py is executable")
    print("   • chmod +x rag_app.py")
    print()
    print("4. **WebView Issues**:")
    print("   • macOS might be blocking GUI apps")
    print("   • Try running from terminal directly")
    print()
    print("5. **Timing Issues**:")
    print("   • RAG UI might need more time to start")
    print("   • Wait 3-5 seconds between attempts")
    print()
    print("🎯 Quick test:")
    print("   python rag_app.py")


def main():
    """Run comprehensive RAG UI diagnostics."""
    print("🔍 RAG Management UI Consistency Diagnostics")
    print("=" * 60)
    print("Diagnosing why RAG UI doesn't open consistently")
    print("=" * 60)
    
    tests = [
        ("RAG Tool Import", test_rag_tool_import),
        ("RAG App File", test_rag_app_file),
        ("RAG Dependencies", test_rag_dependencies),
        ("Port Conflicts", check_port_conflicts),
        ("Multiple Launches", test_multiple_rag_launches),
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
    print("🔍 RAG UI DIAGNOSTIC RESULTS")
    print("=" * 60)
    
    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status}: {test_name}")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed < total:
        provide_rag_solutions()
    else:
        print("\n🎉 All tests passed - RAG UI should be working consistently!")
        print("   If you're still having issues, try restarting Jarvis")


if __name__ == "__main__":
    main()
