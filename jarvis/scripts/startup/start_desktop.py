#!/usr/bin/env python3
"""
Jarvis Desktop App Launcher

Easy launcher for the Jarvis Desktop Application with common presets.
This script provides quick access to different panels and configurations.

Usage:
    python start_desktop.py                    # Main dashboard
    python start_desktop.py settings          # Settings panel
    python start_desktop.py audio             # Audio configuration
"""

import sys
import argparse
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def main():
    """Main launcher function."""
    parser = argparse.ArgumentParser(
        description="Jarvis Desktop App Launcher",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Quick Launch Examples:
  python start_desktop.py                    # Main dashboard
  python start_desktop.py settings          # Settings panel
  python start_desktop.py audio             # Audio configuration
  python start_desktop.py llm               # LLM settings
  python start_desktop.py device            # Device information

Advanced Options:
  python start_desktop.py --port 3000       # Custom port
  python start_desktop.py --debug           # Debug mode
        """
    )
    
    parser.add_argument(
        "panel",
        nargs="?",
        choices=["main", "settings", "audio", "llm", "conversation", "logging", "general", "voice-profiles", "device"],
        default="main",
        help="Panel to display (default: main)"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=8080,
        help="Port for the web server (default: 8080)"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode"
    )
    
    args = parser.parse_args()
    
    # Import and run the desktop app
    try:
        from jarvis_app import JarvisDesktopApp
        
        print(f"🚀 Launching Jarvis Desktop App - {args.panel.title()} Panel")
        
        app = JarvisDesktopApp(
            panel=args.panel,
            port=args.port,
            debug=args.debug
        )
        
        return app.run()
        
    except ImportError as e:
        print(f"❌ Error importing desktop app: {e}")
        print("   Make sure pywebview is installed: pip install pywebview")
        return 1
    except Exception as e:
        print(f"❌ Error launching desktop app: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
