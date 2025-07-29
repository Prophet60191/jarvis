#!/usr/bin/env python3
"""
Jarvis Settings Desktop Application

Native desktop app for Jarvis configuration using pywebview.
This creates a native window that displays the Jarvis settings interface
without requiring a separate browser.

Usage:
    python jarvis_settings_app.py
    python jarvis_settings_app.py --panel audio
    python jarvis_settings_app.py --panel llm
"""

import sys
import os
import argparse
import logging
import threading
import signal
import time
from pathlib import Path

# Add jarvis to path (we're in jarvis/ directory, so parent is project root)
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "jarvis"))

# Check for pywebview availability
try:
    import webview
    WEBVIEW_AVAILABLE = True
except ImportError:
    WEBVIEW_AVAILABLE = False

logger = logging.getLogger(__name__)


class JarvisSettingsApp:
    """Native desktop application for Jarvis Settings."""

    def __init__(self, panel: str = "main", debug: bool = False):
        """
        Initialize the Jarvis Settings desktop application.

        Args:
            panel: Initial panel to display
            debug: Enable debug mode
        """
        self.panel = panel
        self.debug = debug
        self.ui_server = None
        self.ui_port = None
        
    def find_available_port(self, start_port: int = 8080) -> int:
        """Find an available port starting from the given port."""
        import socket
        
        for port in range(start_port, start_port + 100):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('localhost', port))
                    return port
            except OSError:
                continue
        
        raise RuntimeError("No available ports found")
    
    def start_ui_server(self) -> bool:
        """Start the Jarvis UI server in the background."""
        try:
            import subprocess

            # Find available port
            self.ui_port = self.find_available_port()

            # Start the UI server
            ui_script = project_root / "jarvis" / "ui" / "jarvis_ui.py"

            if not ui_script.exists():
                print(f"❌ UI script not found: {ui_script}")
                return False

            cmd = [
                sys.executable,
                str(ui_script),
                "--port", str(self.ui_port),
                "--no-browser"  # Don't auto-open browser
            ]

            print(f"🚀 Starting UI server on port {self.ui_port}")

            self.ui_server = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                start_new_session=True
            )

            # Wait longer for server to start
            print("⏳ Waiting for server to start...")
            time.sleep(5)

            # Check if server is running
            if self.ui_server.poll() is None:
                # Test if server responds
                try:
                    import requests
                    response = requests.get(f"http://localhost:{self.ui_port}", timeout=10)
                    if response.status_code == 200:
                        print(f"✅ UI server started successfully on port {self.ui_port}")
                        return True
                    else:
                        print(f"❌ Server not responding properly: {response.status_code}")
                        return False
                except Exception as e:
                    print(f"❌ Server not responding: {e}")
                    return False
            else:
                stdout, stderr = self.ui_server.communicate()
                print(f"❌ UI server failed to start")
                print(f"STDOUT: {stdout.decode()}")
                print(f"STDERR: {stderr.decode()}")
                return False

        except Exception as e:
            print(f"❌ Failed to start UI server: {e}")
            return False
    
    def stop_ui_server(self):
        """Stop the UI server."""
        if self.ui_server:
            try:
                self.ui_server.terminate()
                self.ui_server.wait(timeout=5)
                logger.info("UI server stopped")
            except Exception as e:
                logger.warning(f"Error stopping UI server: {e}")
                try:
                    self.ui_server.kill()
                except:
                    pass
    
    def get_ui_url(self) -> str:
        """Get the UI URL with the appropriate panel."""
        base_url = f"http://localhost:{self.ui_port}"
        
        # Map panels to URL fragments
        panel_urls = {
            "main": "",
            "settings": "",
            "audio": "#audio",
            "llm": "#llm", 
            "conversation": "#conversation",
            "logging": "#logging",
            "general": "#general",
            "voice-profiles": "#voice-profiles",
            "device": "#device",
            "mcp": "#mcp",
            "rag": "#rag"
        }
        
        fragment = panel_urls.get(self.panel, "")
        return f"{base_url}{fragment}"
    
    def create_native_window(self) -> bool:
        """Create the native desktop window."""
        try:
            if not WEBVIEW_AVAILABLE:
                print("❌ pywebview not available")
                return False

            # Start the UI server first
            print("🌐 Starting UI server...")
            if not self.start_ui_server():
                print("❌ Failed to start UI server")
                return False

            url = self.get_ui_url()

            # Panel display names
            panel_names = {
                "main": "Dashboard",
                "settings": "Settings Overview",
                "audio": "Audio Configuration",
                "llm": "Language Model Settings",
                "conversation": "Conversation Settings",
                "logging": "Logging Configuration",
                "general": "General Settings",
                "voice-profiles": "Voice Profiles",
                "device": "Device Information",
                "mcp": "MCP Tools",
                "rag": "RAG Configuration"
            }

            panel_name = panel_names.get(self.panel, self.panel.title())
            window_title = f"Jarvis Settings - {panel_name}"

            print(f"🖥️ Creating native window: {window_title}")
            print(f"📍 URL: {url}")

            # Create the native window
            webview.create_window(
                title=window_title,
                url=url,
                width=1200,
                height=800,
                min_size=(800, 600),
                resizable=True,
                shadow=True,
                on_top=False
            )

            # Set up window close handler
            def on_window_closed():
                print("🔒 Settings window closed")
                self.stop_ui_server()

            if webview.windows:
                webview.windows[0].events.closed += on_window_closed

            print(f"✅ Native window created successfully")

            return True

        except Exception as e:
            print(f"❌ Failed to create native window: {e}")
            import traceback
            traceback.print_exc()
            self.stop_ui_server()
            return False
    
    def run(self):
        """Run the Jarvis Settings desktop application."""
        if not WEBVIEW_AVAILABLE:
            print("❌ pywebview is required for the desktop app")
            print("   Install with: pip install pywebview")
            return 1
        
        try:
            print(f"⚙️  Starting Jarvis Settings Desktop App - {self.panel.title()} Panel")
            
            # Create and show the native window
            if self.create_native_window():
                if self.debug:
                    webview.start(debug=True)
                else:
                    webview.start()
                return 0
            else:
                print("❌ Failed to create native window")
                return 1
                
        except KeyboardInterrupt:
            print("\n🛑 Jarvis Settings app stopped by user")
            self.stop_ui_server()
            return 0
        except Exception as e:
            logger.error(f"Error running Jarvis Settings app: {e}")
            print(f"❌ Error: {e}")
            self.stop_ui_server()
            return 1


def main():
    """Main entry point for the Jarvis Settings desktop app."""
    parser = argparse.ArgumentParser(description="Jarvis Settings Desktop Application")
    parser.add_argument(
        "--panel",
        default="main",
        choices=["main", "settings", "audio", "llm", "conversation", "logging", "general", "voice-profiles", "device", "mcp", "rag"],
        help="Initial panel to display"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode"
    )

    args = parser.parse_args()

    try:
        app = JarvisSettingsApp(panel=args.panel, debug=args.debug)
        return app.run()
    except Exception as e:
        logger.error(f"Failed to start Jarvis Settings app: {e}")
        print(f"Error: Failed to start Jarvis Settings app: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
