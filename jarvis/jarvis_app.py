#!/usr/bin/env python3
"""
Jarvis Desktop Application

Native desktop app for Jarvis Voice Assistant using webview.
This creates a native window that displays the Jarvis web interface
without requiring a separate browser.

Usage:
    python jarvis_app.py
    python jarvis_app.py --port 8080
    python jarvis_app.py --panel settings
"""

import argparse
import sys
import os
import threading
import time
import logging
import webbrowser
import requests
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    import webview
    WEBVIEW_AVAILABLE = True
except ImportError:
    WEBVIEW_AVAILABLE = False
    print("⚠️  webview not installed. Install with: pip install pywebview")

logger = logging.getLogger(__name__)


class JarvisDesktopApp:
    """Native desktop application for Jarvis Voice Assistant."""
    
    def __init__(self, panel: str = "main", port: int = 8080, debug: bool = False):
        """
        Initialize the Jarvis desktop application.
        
        Args:
            panel: Initial panel to display
            port: Port for the web server
            debug: Enable debug mode
        """
        self.panel = panel
        self.port = port
        self.debug = debug
        self.web_server = None
        self.server_thread = None
        self.monitor_thread = None
        self.should_monitor = True
        
    def start_web_server(self):
        """Start the Jarvis web server in a background thread."""
        try:
            from ui.jarvis_ui import JarvisUI
            
            # Create and start the web server (without opening browser)
            self.web_server = JarvisUI(initial_panel=self.panel, port=self.port, open_browser=False)

            # Start server without opening browser
            logger.info(f"Starting Jarvis web server on port {self.port}")
            self.web_server.start_server()
            
        except Exception as e:
            logger.error(f"Error starting web server: {e}")
            raise
    
    def stop_web_server(self):
        """Stop the web server."""
        try:
            if self.web_server and hasattr(self.web_server, 'server'):
                logger.info("Stopping Jarvis web server...")
                if hasattr(self.web_server, 'stop_server'):
                    self.web_server.stop_server()
                elif hasattr(self.web_server.server, 'shutdown'):
                    self.web_server.server.shutdown()
                    self.web_server.server.server_close()
                logger.info("Web server stopped successfully")
            else:
                logger.debug("No web server to stop")
        except Exception as e:
            logger.error(f"Error stopping web server: {e}")
            # Force stop if graceful shutdown fails
            try:
                import os
                import signal
                os.kill(os.getpid(), signal.SIGTERM)
            except:
                pass
    
    def create_native_window(self):
        """Create the native desktop window."""
        if not WEBVIEW_AVAILABLE:
            print("❌ Cannot create native window: pywebview not installed")
            print("   Install with: pip install pywebview")
            print("   Falling back to browser mode...")
            
            # Fallback to browser
            url = f"http://localhost:{self.port}/{self.panel}"
            webbrowser.open(url)
            return False
        
        # Wait for web server to start
        max_wait = 10
        for i in range(max_wait):
            try:
                import requests
                response = requests.get(f"http://localhost:{self.port}/", timeout=1)
                if response.status_code == 200:
                    break
            except:
                time.sleep(1)
        else:
            print("❌ Web server failed to start within 10 seconds")
            return False
        
        # Create native window
        url = f"http://localhost:{self.port}/{self.panel}"
        
        # Window configuration (using only basic supported parameters)
        window_config = {
            'title': 'Jarvis Control Panel',
            'url': url,
            'width': 1200,
            'height': 800,
            'min_size': (800, 600),
            'resizable': True
        }
        
        logger.info(f"Creating native window for {url}")
        
        # Create window
        window = webview.create_window(**window_config)

        # Start server monitoring to auto-close window when server shuts down
        self.start_server_monitor()

        # Start the webview (this blocks until window is closed)
        try:
            webview.start(debug=self.debug)
        except TypeError:
            # Fallback for older webview versions that don't support debug parameter
            webview.start()

        # This code runs when the window is closed
        logger.info("Desktop window closed, stopping web server...")
        self.stop_server_monitor()
        self.stop_web_server()
        
        return True

    def start_server_monitor(self):
        """Start monitoring the server and close window when server shuts down."""
        def monitor_server():
            consecutive_failures = 0
            max_failures = 3

            logger.info("Starting server monitoring for auto-close...")

            while self.should_monitor:
                try:
                    # Check if server is still running
                    response = requests.get(f"http://localhost:{self.port}/", timeout=2)
                    if response.status_code == 200:
                        consecutive_failures = 0
                    else:
                        consecutive_failures += 1
                except requests.exceptions.RequestException:
                    consecutive_failures += 1

                # If server is down for multiple checks, close the window
                if consecutive_failures >= max_failures:
                    logger.info("Server appears to be down, closing desktop window...")
                    try:
                        # Close all webview windows
                        webview.windows[0].destroy()
                    except Exception as e:
                        logger.debug(f"Error closing webview window: {e}")
                    break

                time.sleep(2)  # Check every 2 seconds

            logger.info("Server monitoring stopped")

        self.monitor_thread = threading.Thread(target=monitor_server, daemon=True)
        self.monitor_thread.start()

    def stop_server_monitor(self):
        """Stop the server monitoring."""
        self.should_monitor = False
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=1)

    def run(self):
        """Run the Jarvis desktop application."""
        print("🤖 Starting Jarvis Desktop Application")
        print("=" * 50)
        print(f"Panel: {self.panel}")
        print(f"Port: {self.port}")
        print(f"Debug: {self.debug}")
        print()
        
        try:
            # Start web server in background thread
            print("🌐 Starting web server...")
            self.server_thread = threading.Thread(
                target=self.start_web_server,
                daemon=True
            )
            self.server_thread.start()
            
            # Give server time to start
            time.sleep(2)
            
            # Create native window
            print("🖥️  Creating native window...")
            success = self.create_native_window()
            
            if not success:
                print("⚠️  Native window creation failed, keeping server running...")
                print(f"   Access via browser: http://localhost:{self.port}")
                
                # Keep server running
                try:
                    while True:
                        time.sleep(1)
                except KeyboardInterrupt:
                    print("\n🛑 Shutting down...")
            
        except KeyboardInterrupt:
            print("\n🛑 Shutting down...")
        except Exception as e:
            print(f"❌ Error: {e}")
            return 1
        finally:
            self.stop_server_monitor()
            self.stop_web_server()
        
        return 0


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Jarvis Desktop Application",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python jarvis_app.py                    # Launch main dashboard
  python jarvis_app.py --panel settings  # Launch settings panel
  python jarvis_app.py --port 3000       # Use custom port
  python jarvis_app.py --debug           # Enable debug mode

Requirements:
  pip install pywebview

The app creates a native desktop window displaying the Jarvis web interface.
If pywebview is not available, it falls back to opening in the default browser.
        """
    )
    
    parser.add_argument(
        "--panel",
        choices=["main", "settings", "audio", "llm", "conversation", "logging", "general", "voice-profiles", "device"],
        default="main",
        help="Initial panel to display (default: main)"
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
    
    # Configure logging
    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create and run the app
    app = JarvisDesktopApp(
        panel=args.panel,
        port=args.port,
        debug=args.debug
    )
    
    return app.run()


if __name__ == "__main__":
    sys.exit(main())
