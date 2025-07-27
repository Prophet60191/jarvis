#!/usr/bin/env python3
"""
Jarvis Web UI Launcher

Quick start script for the Jarvis Voice Assistant Web Configuration Interface.
This script provides an easy way to launch the modern web interface for
configuring and monitoring your Jarvis Voice Assistant.

Usage:
    python start_ui.py                    # Launch main dashboard
    python start_ui.py --panel settings  # Launch settings overview
    python start_ui.py --panel audio     # Launch audio configuration
    python start_ui.py --port 3000       # Use custom port
"""

import argparse
import sys
import os
import subprocess
import webbrowser
import time
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def check_dependencies():
    """Check if required dependencies are available."""
    try:
        import jarvis
        return True
    except ImportError:
        print("❌ Jarvis package not found. Please install dependencies:")
        print("   pip install -r requirements.txt")
        return False

def get_available_panels():
    """Get list of available UI panels."""
    return [
        "main",           # Dashboard overview
        "settings",       # Configuration overview
        "audio",          # Audio and TTS settings
        "llm",            # Language model configuration
        "conversation",   # Conversation flow settings
        "logging",        # Logging configuration
        "general",        # General application settings
        "voice-profiles", # Voice cloning management
        "device"          # Device and hardware information
    ]

def launch_ui(panel="main", port=8080, auto_open=True):
    """Launch the Jarvis Web UI."""
    
    print("🚀 Starting Jarvis Web Configuration Interface...")
    print(f"   Panel: {panel}")
    print(f"   Port: {port}")
    print(f"   URL: http://localhost:{port}")
    
    # Construct the command
    ui_script = project_root / "ui" / "jarvis_ui.py"
    
    if not ui_script.exists():
        print(f"❌ UI script not found: {ui_script}")
        print("   Please ensure you're running this from the Jarvis project root.")
        return False
    
    cmd = [
        sys.executable,
        str(ui_script),
        "--panel", panel,
        "--port", str(port)
    ]
    
    try:
        # Launch the UI server
        print("🌐 Launching web server...")
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Give the server a moment to start
        time.sleep(2)
        
        # Check if the process is still running
        if process.poll() is None:
            print("✅ Web server started successfully!")
            
            if auto_open:
                url = f"http://localhost:{port}"
                print(f"🌍 Opening {url} in your default browser...")
                webbrowser.open(url)
            
            print("\n" + "="*60)
            print("🎉 Jarvis Web Interface is now running!")
            print("="*60)
            print(f"📱 Access URL: http://localhost:{port}")
            print(f"⚙️  Current Panel: {panel}")
            print("\n🎤 Voice Commands:")
            print("   • 'Jarvis, open settings' - Configuration overview")
            print("   • 'Jarvis, open audio config' - Audio settings")
            print("   • 'Jarvis, open LLM config' - Language model settings")
            print("   • 'Jarvis, open device info' - Device information")
            print("\n🔧 Available Panels:")
            for p in get_available_panels():
                print(f"   • {p}")
            print("\n⏹️  Press Ctrl+C to stop the server")
            print("="*60)
            
            # Wait for the process to complete or be interrupted
            try:
                process.wait()
            except KeyboardInterrupt:
                print("\n🛑 Stopping web server...")
                process.terminate()
                process.wait()
                print("✅ Web server stopped.")
            
            return True
        else:
            # Process failed to start
            stdout, stderr = process.communicate()
            print("❌ Failed to start web server!")
            if stderr:
                print(f"Error: {stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error launching UI: {e}")
        return False

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Launch Jarvis Web Configuration Interface",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python start_ui.py                    # Launch main dashboard
  python start_ui.py --panel settings  # Launch settings overview
  python start_ui.py --panel audio     # Launch audio configuration
  python start_ui.py --port 3000       # Use custom port
  python start_ui.py --no-browser      # Don't auto-open browser

Available Panels:
  main           Dashboard overview
  settings       Configuration overview
  audio          Audio and TTS settings
  llm            Language model configuration
  conversation   Conversation flow settings
  logging        Logging configuration
  general        General application settings
  voice-profiles Voice cloning management
  device         Device and hardware information
        """
    )
    
    parser.add_argument(
        "--panel",
        choices=get_available_panels(),
        default="main",
        help="UI panel to launch (default: main)"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=8080,
        help="Port to run the web server on (default: 8080)"
    )
    
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Don't automatically open the browser"
    )
    
    args = parser.parse_args()
    
    print("🤖 Jarvis Web UI Launcher")
    print("=" * 40)
    
    # Check dependencies
    if not check_dependencies():
        return 1
    
    # Launch the UI
    success = launch_ui(
        panel=args.panel,
        port=args.port,
        auto_open=not args.no_browser
    )
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
