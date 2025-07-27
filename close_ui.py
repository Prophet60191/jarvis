#!/usr/bin/env python3
"""
Jarvis UI Shutdown Utility

Command-line utility to close and shut down the Jarvis Web UI server.
This script provides a simple way to gracefully or forcefully terminate
the web interface server.

Usage:
    python close_ui.py                    # Close UI on default port 8080
    python close_ui.py --port 3000       # Close UI on custom port
    python close_ui.py --force           # Force close if graceful shutdown fails
"""

import argparse
import sys
import os
import requests
import subprocess
import time
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def shutdown_via_api(port: int) -> bool:
    """
    Attempt to shutdown the UI server via API call.
    
    Args:
        port: Port number of the UI server
        
    Returns:
        True if shutdown was successful, False otherwise
    """
    try:
        url = f"http://localhost:{port}/api/shutdown"
        print(f"🌐 Sending shutdown request to {url}...")
        
        # Make the shutdown request with a short timeout
        response = requests.post(url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print("✅ UI server acknowledged shutdown request")
                
                # Wait a moment for the server to actually shut down
                print("⏳ Waiting for server to shut down...")
                time.sleep(2)
                
                # Verify the server is actually down
                try:
                    requests.get(f"http://localhost:{port}/", timeout=2)
                    # If we get here, server is still running
                    print("⚠️  Server is still responding after shutdown request")
                    return False
                except requests.exceptions.RequestException:
                    # Server is down, which is what we want
                    print("✅ Server has been shut down successfully")
                    return True
                    
        else:
            print(f"❌ Server returned status code {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Could not connect to UI server on port {port}: {e}")
        return False
    except Exception as e:
        print(f"❌ Error during API shutdown: {e}")
        return False

def shutdown_via_process(port: int) -> bool:
    """
    Attempt to shutdown the UI server by killing the process.
    
    Args:
        port: Port number of the UI server
        
    Returns:
        True if process was terminated, False otherwise
    """
    try:
        print(f"🔍 Looking for processes using port {port}...")
        
        # Find processes using the port
        result = subprocess.run(
            ["lsof", "-ti", f":{port}"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0 and result.stdout.strip():
            pids = result.stdout.strip().split('\n')
            print(f"📋 Found {len(pids)} process(es) using port {port}")
            
            for pid in pids:
                if pid.strip():
                    try:
                        print(f"🔄 Terminating process {pid}...")
                        
                        # Try to kill the process gracefully first
                        subprocess.run(["kill", pid.strip()], timeout=5)
                        
                        # Wait a moment
                        time.sleep(2)
                        
                        # Check if process is still running
                        check_result = subprocess.run(
                            ["kill", "-0", pid.strip()],
                            capture_output=True,
                            timeout=2
                        )
                        
                        if check_result.returncode != 0:
                            # Process is gone
                            print(f"✅ Process {pid} terminated successfully")
                            return True
                        else:
                            # Process still running, force kill
                            print(f"💀 Force killing process {pid}...")
                            subprocess.run(["kill", "-9", pid.strip()], timeout=5)
                            print(f"✅ Process {pid} force killed")
                            return True
                            
                    except subprocess.TimeoutExpired:
                        print(f"⏰ Timeout while trying to kill process {pid}")
                    except Exception as e:
                        print(f"❌ Error killing process {pid}: {e}")
            
            return False
        else:
            print(f"ℹ️  No processes found using port {port}")
            return False
            
    except subprocess.TimeoutExpired:
        print("⏰ Timeout while searching for processes")
        return False
    except FileNotFoundError:
        print("❌ lsof command not found, cannot force close via process")
        print("   This feature requires Unix/Linux/macOS with lsof installed")
        return False
    except Exception as e:
        print(f"❌ Error during process shutdown: {e}")
        return False

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Close Jarvis Web UI Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python close_ui.py                    # Close UI on default port 8080
  python close_ui.py --port 3000       # Close UI on custom port
  python close_ui.py --force           # Force close if graceful shutdown fails
  python close_ui.py --port 8080 --force  # Close on port 8080 with force option

The script will first try to gracefully shutdown the server via API.
If that fails and --force is specified, it will attempt to kill the process.
        """
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=8080,
        help="Port number of the UI server to close (default: 8080)"
    )
    
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force close the UI server if API shutdown fails"
    )
    
    args = parser.parse_args()
    
    print("🤖 Jarvis UI Shutdown Utility")
    print("=" * 40)
    print(f"Target: http://localhost:{args.port}")
    print(f"Force mode: {'Enabled' if args.force else 'Disabled'}")
    print()
    
    # First, try graceful shutdown via API
    print("🔄 Attempting graceful shutdown via API...")
    api_success = shutdown_via_api(args.port)
    
    if api_success:
        print()
        print("🎉 Jarvis UI server has been shut down gracefully!")
        return 0
    
    # If API shutdown failed and force is requested, try process termination
    if args.force:
        print()
        print("🔄 Graceful shutdown failed, attempting force shutdown...")
        process_success = shutdown_via_process(args.port)
        
        if process_success:
            print()
            print("🎉 Jarvis UI server has been forcefully terminated!")
            return 0
        else:
            print()
            print("❌ Could not terminate the UI server process")
            return 1
    else:
        print()
        print("❌ Could not shut down Jarvis UI server gracefully")
        print("💡 Try using --force to attempt process termination")
        print("💡 Check if the server is running on a different port")
        return 1

if __name__ == "__main__":
    sys.exit(main())
