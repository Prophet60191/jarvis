#!/usr/bin/env python3
"""
RAG Management Desktop App Launcher

Quick launcher for the RAG Management native desktop application.
Provides document upload, memory management, and RAG configuration.

Usage:
    python start_rag_manager.py                    # Main dashboard
    python start_rag_manager.py upload             # Upload panel
    python start_rag_manager.py documents          # Document library
    python start_rag_manager.py memory             # Memory management
    python start_rag_manager.py settings           # RAG settings
"""

import sys
import argparse
from pathlib import Path

def main():
    """Main launcher function."""
    parser = argparse.ArgumentParser(
        description="RAG Management Desktop App Launcher",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python start_rag_manager.py                    # Main dashboard
  python start_rag_manager.py upload             # Upload interface
  python start_rag_manager.py documents          # Document library
  python start_rag_manager.py memory             # Memory management
  python start_rag_manager.py settings           # RAG settings

Voice Commands:
  "Jarvis, open RAG manager"                     # Opens main dashboard
  "Jarvis, open document manager"                # Opens upload interface
  "Jarvis, close RAG manager"                    # Closes the app
        """
    )
    
    parser.add_argument(
        "panel",
        nargs="?",
        default="main",
        choices=["main", "upload", "documents", "memory", "settings"],
        help="Panel to open (default: main)"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode"
    )
    
    args = parser.parse_args()
    
    # Import and run the RAG desktop app
    try:
        from rag_app import RAGDesktopApp
        
        print(f"🧠 Launching RAG Management Desktop App - {args.panel.title()} Panel")
        
        app = RAGDesktopApp(panel=args.panel, debug=args.debug)
        return app.run()
        
    except ImportError as e:
        print(f"❌ Error importing RAG desktop app: {e}")
        print("   Make sure pywebview is installed: pip install pywebview")
        return 1
    except Exception as e:
        print(f"❌ Error launching RAG desktop app: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
