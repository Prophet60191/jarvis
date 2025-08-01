#!/usr/bin/env python3
"""
Jarvis Voice Assistant Startup Script

This script provides an easy way to start your Jarvis voice assistant
with proper environment setup and configuration checks.

Usage:
    python Start_Jarvis.py
    
Or make it executable and run directly:
    chmod +x Start_Jarvis.py
    ./Start_Jarvis.py
"""

import os
import sys
import subprocess
import time
import signal
from pathlib import Path

# Configuration
JARVIS_PROJECT_PATH = Path.home() / "Desktop" / "Voice App"
JARVIS_MAIN_SCRIPT = "jarvis_app.py"
PYTHON_EXECUTABLE = sys.executable

class JarvisLauncher:
    """Jarvis application launcher with environment checks and setup."""
    
    def __init__(self):
        self.jarvis_process = None
        self.project_path = JARVIS_PROJECT_PATH
        self.main_script = self.project_path / JARVIS_MAIN_SCRIPT
        
    def print_banner(self):
        """Print the startup banner."""
        print("=" * 80)
        print("🎤 JARVIS VOICE ASSISTANT LAUNCHER")
        print("=" * 80)
        print(f"Project Path: {self.project_path}")
        print(f"Main Script: {self.main_script}")
        print(f"Python: {PYTHON_EXECUTABLE}")
        print("=" * 80)
    
    def check_environment(self):
        """Check if the environment is properly set up."""
        print("🔍 CHECKING ENVIRONMENT...")
        print("-" * 40)
        
        # Check if project directory exists
        if not self.project_path.exists():
            print(f"❌ Project directory not found: {self.project_path}")
            print("   Please update JARVIS_PROJECT_PATH in this script")
            return False
        print(f"✅ Project directory found: {self.project_path}")
        
        # Check if main script exists
        if not self.main_script.exists():
            print(f"❌ Main script not found: {self.main_script}")
            return False
        print(f"✅ Main script found: {self.main_script}")
        
        # Check Python version
        python_version = sys.version_info
        if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
            print(f"❌ Python 3.8+ required, found: {python_version.major}.{python_version.minor}")
            return False
        print(f"✅ Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
        
        # Check for virtual environment (optional but recommended)
        if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
            print("✅ Virtual environment detected")
        else:
            print("⚠️  No virtual environment detected (recommended but not required)")
        
        return True
    
    def check_dependencies(self):
        """Check if key dependencies are available."""
        print("\n🔍 CHECKING KEY DEPENDENCIES...")
        print("-" * 40)
        
        required_packages = [
            "langchain",
            "openai", 
            "pyaudio",
            "speech_recognition",
            "pyttsx3",
            "webview",
            "psutil"
        ]
        
        missing_packages = []
        
        for package in required_packages:
            try:
                __import__(package)
                print(f"✅ {package}")
            except ImportError:
                print(f"❌ {package} (missing)")
                missing_packages.append(package)
        
        if missing_packages:
            print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
            print("   Install with: pip install " + " ".join(missing_packages))
            
            response = input("\nContinue anyway? (y/N): ").strip().lower()
            return response == 'y'
        
        return True
    
    def setup_signal_handlers(self):
        """Set up signal handlers for graceful shutdown."""
        def signal_handler(signum, frame):
            print(f"\n🛑 Received signal {signum}, shutting down Jarvis...")
            self.shutdown()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    def start_jarvis(self):
        """Start the Jarvis application."""
        print("\n🚀 STARTING JARVIS...")
        print("-" * 40)
        
        try:
            # Change to project directory
            os.chdir(self.project_path)
            
            # Start Jarvis
            cmd = [PYTHON_EXECUTABLE, str(self.main_script)]
            print(f"Executing: {' '.join(cmd)}")
            print(f"Working directory: {os.getcwd()}")
            
            self.jarvis_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            print(f"✅ Jarvis started (PID: {self.jarvis_process.pid})")
            print("\n🎤 Jarvis is now running!")
            print("=" * 80)
            print("Voice commands available:")
            print("• 'Open vault' - Open the knowledge vault")
            print("• 'Open settings' - Open Jarvis settings")
            print("• 'Close vault' - Close the vault")
            print("• 'Close settings' - Close settings")
            print("• And many more...")
            print("=" * 80)
            print("Press Ctrl+C to stop Jarvis")
            print("=" * 80)
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to start Jarvis: {e}")
            return False
    
    def monitor_jarvis(self):
        """Monitor the Jarvis process and handle output."""
        try:
            while True:
                if self.jarvis_process.poll() is not None:
                    # Process has terminated
                    return_code = self.jarvis_process.returncode
                    print(f"\n🛑 Jarvis process terminated with code: {return_code}")
                    break
                
                # Read output line by line
                try:
                    line = self.jarvis_process.stdout.readline()
                    if line:
                        print(line.rstrip())
                except:
                    pass
                
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            print("\n🛑 Keyboard interrupt received")
        except Exception as e:
            print(f"\n❌ Error monitoring Jarvis: {e}")
    
    def shutdown(self):
        """Gracefully shutdown Jarvis."""
        if self.jarvis_process and self.jarvis_process.poll() is None:
            print("🛑 Shutting down Jarvis...")
            
            # Try graceful termination first
            self.jarvis_process.terminate()
            
            try:
                self.jarvis_process.wait(timeout=10)
                print("✅ Jarvis shut down gracefully")
            except subprocess.TimeoutExpired:
                print("⚠️  Graceful shutdown timed out, force killing...")
                self.jarvis_process.kill()
                self.jarvis_process.wait()
                print("✅ Jarvis force killed")
    
    def run(self):
        """Main run method."""
        self.print_banner()
        
        # Environment checks
        if not self.check_environment():
            print("\n❌ Environment check failed. Please fix the issues above.")
            return 1
        
        if not self.check_dependencies():
            print("\n❌ Dependency check failed.")
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
        
        return 0


def main():
    """Main entry point."""
    launcher = JarvisLauncher()
    return launcher.run()


if __name__ == "__main__":
    sys.exit(main())
