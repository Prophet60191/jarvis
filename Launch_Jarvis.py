#!/usr/bin/env python3
"""
🎤 JARVIS VOICE ASSISTANT - COMPREHENSIVE LAUNCHER
==================================================

This is the ultimate startup script for your Jarvis Voice Assistant.
It includes environment checks, dependency verification, and easy launching.

Features:
- Environment validation
- Dependency checking
- Graceful shutdown handling
- Real-time output monitoring
- Error diagnostics
- Desktop application management

Usage:
    python Launch_Jarvis.py
    
Or make it executable:
    chmod +x Launch_Jarvis.py
    ./Launch_Jarvis.py
"""

import os
import sys
import subprocess
import time
import signal
import threading
from pathlib import Path
from datetime import datetime

# Configuration
JARVIS_PROJECT_PATH = Path.home() / "Desktop" / "Voice App"
JARVIS_MAIN_SCRIPT = "jarvis_app.py"
PYTHON_EXECUTABLE = sys.executable

class Colors:
    """ANSI color codes for terminal output."""
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    PURPLE = '\033[0;35m'
    CYAN = '\033[0;36m'
    WHITE = '\033[1;37m'
    BOLD = '\033[1m'
    NC = '\033[0m'  # No Color

class JarvisLauncher:
    """Comprehensive Jarvis application launcher."""
    
    def __init__(self):
        self.jarvis_process = None
        self.project_path = JARVIS_PROJECT_PATH
        self.main_script = self.project_path / JARVIS_MAIN_SCRIPT
        self.start_time = None
        
    def print_banner(self):
        """Print the startup banner."""
        print(f"{Colors.CYAN}{'=' * 80}{Colors.NC}")
        print(f"{Colors.BOLD}{Colors.WHITE}🎤 JARVIS VOICE ASSISTANT LAUNCHER{Colors.NC}")
        print(f"{Colors.CYAN}{'=' * 80}{Colors.NC}")
        print(f"{Colors.BLUE}🏠 Project Path:{Colors.NC} {self.project_path}")
        print(f"{Colors.BLUE}📄 Main Script:{Colors.NC} {self.main_script}")
        print(f"{Colors.BLUE}🐍 Python:{Colors.NC} {PYTHON_EXECUTABLE}")
        print(f"{Colors.BLUE}⏰ Launch Time:{Colors.NC} {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{Colors.CYAN}{'=' * 80}{Colors.NC}")
    
    def print_status(self, message, status="info"):
        """Print colored status messages."""
        icons = {
            "success": f"{Colors.GREEN}✅{Colors.NC}",
            "error": f"{Colors.RED}❌{Colors.NC}",
            "warning": f"{Colors.YELLOW}⚠️{Colors.NC}",
            "info": f"{Colors.BLUE}🔍{Colors.NC}",
            "rocket": f"{Colors.PURPLE}🚀{Colors.NC}"
        }
        icon = icons.get(status, icons["info"])
        print(f"{icon} {message}")
    
    def check_environment(self):
        """Check if the environment is properly set up."""
        print(f"\n{Colors.BOLD}🔍 ENVIRONMENT CHECK{Colors.NC}")
        print("-" * 40)
        
        # Check if project directory exists
        if not self.project_path.exists():
            self.print_status(f"Project directory not found: {self.project_path}", "error")
            self.print_status("Please update JARVIS_PROJECT_PATH in this script", "error")
            return False
        self.print_status(f"Project directory found: {self.project_path}", "success")
        
        # Check if main script exists
        if not self.main_script.exists():
            self.print_status(f"Main script not found: {self.main_script}", "error")
            return False
        self.print_status(f"Main script found: {self.main_script.name}", "success")
        
        # Check Python version
        python_version = sys.version_info
        if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
            self.print_status(f"Python 3.8+ required, found: {python_version.major}.{python_version.minor}", "error")
            return False
        self.print_status(f"Python version: {python_version.major}.{python_version.minor}.{python_version.micro}", "success")
        
        # Check for virtual environment
        if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
            self.print_status("Virtual environment detected", "success")
        else:
            self.print_status("No virtual environment detected (recommended but not required)", "warning")
        
        return True
    
    def check_dependencies(self):
        """Check if key dependencies are available."""
        print(f"\n{Colors.BOLD}🔍 DEPENDENCY CHECK{Colors.NC}")
        print("-" * 40)
        
        critical_packages = ["langchain", "openai", "pyaudio", "speech_recognition"]
        optional_packages = ["pyttsx3", "webview", "psutil", "requests"]
        
        missing_critical = []
        missing_optional = []
        
        # Check critical packages
        for package in critical_packages:
            try:
                __import__(package)
                self.print_status(f"{package} (critical)", "success")
            except ImportError:
                self.print_status(f"{package} (critical) - MISSING", "error")
                missing_critical.append(package)
        
        # Check optional packages
        for package in optional_packages:
            try:
                __import__(package)
                self.print_status(f"{package} (optional)", "success")
            except ImportError:
                self.print_status(f"{package} (optional) - missing", "warning")
                missing_optional.append(package)
        
        if missing_critical:
            print(f"\n{Colors.RED}❌ CRITICAL PACKAGES MISSING:{Colors.NC}")
            print(f"   Install with: pip install {' '.join(missing_critical)}")
            return False
        
        if missing_optional:
            print(f"\n{Colors.YELLOW}⚠️  OPTIONAL PACKAGES MISSING:{Colors.NC}")
            print(f"   Install with: pip install {' '.join(missing_optional)}")
            print("   Jarvis will work but some features may be limited.")
        
        return True
    
    def setup_signal_handlers(self):
        """Set up signal handlers for graceful shutdown."""
        def signal_handler(signum, frame):
            print(f"\n{Colors.YELLOW}🛑 Received signal {signum}, shutting down Jarvis...{Colors.NC}")
            self.shutdown()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    def start_jarvis(self):
        """Start the Jarvis application."""
        print(f"\n{Colors.BOLD}🚀 STARTING JARVIS{Colors.NC}")
        print("-" * 40)
        
        try:
            # Change to project directory
            os.chdir(self.project_path)
            self.print_status(f"Changed to directory: {os.getcwd()}", "info")
            
            # Start Jarvis
            cmd = [PYTHON_EXECUTABLE, str(self.main_script)]
            self.print_status(f"Executing: {' '.join(cmd)}", "info")
            
            self.jarvis_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            self.start_time = time.time()
            self.print_status(f"Jarvis started (PID: {self.jarvis_process.pid})", "success")
            
            # Print usage information
            self.print_usage_info()
            
            return True
            
        except Exception as e:
            self.print_status(f"Failed to start Jarvis: {e}", "error")
            return False
    
    def print_usage_info(self):
        """Print usage information."""
        print(f"\n{Colors.BOLD}{Colors.GREEN}🎤 JARVIS IS NOW RUNNING!{Colors.NC}")
        print(f"{Colors.CYAN}{'=' * 80}{Colors.NC}")
        print(f"{Colors.BOLD}Voice Commands Available:{Colors.NC}")
        print(f"  {Colors.GREEN}•{Colors.NC} 'Open vault' - Open the knowledge vault")
        print(f"  {Colors.GREEN}•{Colors.NC} 'Open settings' - Open Jarvis settings")
        print(f"  {Colors.GREEN}•{Colors.NC} 'Close vault' - Close the vault")
        print(f"  {Colors.GREEN}•{Colors.NC} 'Close settings' - Close settings")
        print(f"  {Colors.GREEN}•{Colors.NC} 'What's the weather?' - Get weather info")
        print(f"  {Colors.GREEN}•{Colors.NC} 'What time is it?' - Get current time")
        print(f"  {Colors.GREEN}•{Colors.NC} And many more...")
        print(f"{Colors.CYAN}{'=' * 80}{Colors.NC}")
        print(f"{Colors.YELLOW}Press Ctrl+C to stop Jarvis{Colors.NC}")
        print(f"{Colors.CYAN}{'=' * 80}{Colors.NC}")
    
    def monitor_jarvis(self):
        """Monitor the Jarvis process and handle output."""
        try:
            while True:
                if self.jarvis_process.poll() is not None:
                    # Process has terminated
                    return_code = self.jarvis_process.returncode
                    runtime = time.time() - self.start_time if self.start_time else 0
                    print(f"\n{Colors.RED}🛑 Jarvis process terminated{Colors.NC}")
                    print(f"   Return code: {return_code}")
                    print(f"   Runtime: {runtime:.1f} seconds")
                    break
                
                # Read output line by line
                try:
                    line = self.jarvis_process.stdout.readline()
                    if line:
                        # Add timestamp to output
                        timestamp = datetime.now().strftime('%H:%M:%S')
                        print(f"{Colors.CYAN}[{timestamp}]{Colors.NC} {line.rstrip()}")
                except:
                    pass
                
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}🛑 Keyboard interrupt received{Colors.NC}")
        except Exception as e:
            print(f"\n{Colors.RED}❌ Error monitoring Jarvis: {e}{Colors.NC}")
    
    def shutdown(self):
        """Gracefully shutdown Jarvis."""
        if self.jarvis_process and self.jarvis_process.poll() is None:
            print(f"{Colors.YELLOW}🛑 Shutting down Jarvis...{Colors.NC}")
            
            # Try graceful termination first
            self.jarvis_process.terminate()
            
            try:
                self.jarvis_process.wait(timeout=10)
                self.print_status("Jarvis shut down gracefully", "success")
            except subprocess.TimeoutExpired:
                self.print_status("Graceful shutdown timed out, force killing...", "warning")
                self.jarvis_process.kill()
                self.jarvis_process.wait()
                self.print_status("Jarvis force killed", "success")
    
    def run(self):
        """Main run method."""
        self.print_banner()
        
        # Environment checks
        if not self.check_environment():
            print(f"\n{Colors.RED}❌ Environment check failed. Please fix the issues above.{Colors.NC}")
            return 1
        
        if not self.check_dependencies():
            print(f"\n{Colors.RED}❌ Dependency check failed.{Colors.NC}")
            return 1
        
        # Setup signal handlers
        self.setup_signal_handlers()
        
        # Start Jarvis
        if not self.start_jarvis():
            return 1
        
        # Monitor Jarvis
        try:
            self.monitor_jarvis()
        finally:
            self.shutdown()
        
        print(f"\n{Colors.GREEN}✅ Jarvis launcher finished.{Colors.NC}")
        return 0


def main():
    """Main entry point."""
    launcher = JarvisLauncher()
    return launcher.run()


if __name__ == "__main__":
    sys.exit(main())
