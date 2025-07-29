#!/usr/bin/env python3
"""
🖥️ JARVIS DESKTOP LAUNCHER

Enhanced desktop launcher for Jarvis Voice Assistant with GUI progress indicator
and comprehensive system management.

This launcher provides:
- Visual startup progress
- System validation
- Error handling with user-friendly messages
- Desktop integration
- Graceful shutdown management
"""

import os
import sys
import time
import subprocess
import signal
import threading
from pathlib import Path
from typing import Optional

# Determine the correct project root
script_location = Path(__file__).parent

# If running from desktop, navigate to the actual Jarvis directory
if "Desktop" in str(script_location):
    # Assume Jarvis is in the "Voice App" directory on desktop
    project_root = Path("/Users/josed/Desktop/Voice App")
    if not project_root.exists():
        print("❌ Jarvis application directory not found!")
        print(f"Expected location: {project_root}")
        sys.exit(1)
else:
    project_root = script_location

# Add project root to path
sys.path.insert(0, str(project_root))

# Change to project directory
os.chdir(project_root)

class DesktopJarvisLauncher:
    """
    Desktop-optimized launcher for Jarvis Voice Assistant.
    
    Features:
    - Clean console interface optimized for desktop use
    - Visual progress indicators
    - Comprehensive error handling
    - System validation and troubleshooting
    - Graceful shutdown with cleanup
    """
    
    def __init__(self):
        self.jarvis_process: Optional[subprocess.Popen] = None
        self.is_running = False
        self.startup_errors = []
        
    def clear_screen(self):
        """Clear the console screen."""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_header(self):
        """Display the desktop launcher header."""
        self.clear_screen()
        header = """
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║    🎯 JARVIS ENHANCED VOICE ASSISTANT - DESKTOP LAUNCHER             ║
║                                                                      ║
║    Your intelligent AI assistant with complete self-awareness,      ║
║    real-time analytics, and comprehensive documentation support.     ║
║                                                                      ║
║    🧠 Self-Aware AI  📊 Analytics  🎤 Voice Control  📚 Help UI      ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
        """
        print(header)
        print("🚀 Initializing Jarvis Enhanced Voice Assistant...")
        print("=" * 70)
    
    def show_progress(self, message: str, duration: float = 1.0):
        """Show a progress message with animation."""
        print(f"⏳ {message}", end="", flush=True)
        for i in range(int(duration * 4)):
            time.sleep(0.25)
            print(".", end="", flush=True)
        print(" ✅")
    
    def validate_environment(self) -> bool:
        """Comprehensive environment validation."""
        print("\n🔍 SYSTEM VALIDATION")
        print("-" * 30)
        
        # Python version check
        if sys.version_info < (3, 8):
            print(f"❌ Python 3.8+ required. Current: {sys.version.split()[0]}")
            self.startup_errors.append("Python version too old")
            return False
        print(f"✅ Python {sys.version.split()[0]} - Compatible")
        
        # Directory structure check
        essential_files = [
            "start_jarvis.py",
            "jarvis/jarvis/core/",
            "jarvis/jarvis/tools/",
            "data/"
        ]
        
        for file_path in essential_files:
            full_path = project_root / file_path
            if not full_path.exists():
                print(f"❌ Missing: {file_path}")
                self.startup_errors.append(f"Missing file/directory: {file_path}")
                return False
        print("✅ Directory structure - Valid")
        
        # Dependency check
        critical_deps = [
            ("speech_recognition", "Voice input"),
            ("pyttsx3", "Voice output"),
        ]
        
        optional_deps = [
            ("PyQt6", "GUI interfaces"),
            ("chromadb", "RAG memory system"),
            ("psutil", "System monitoring")
        ]
        
        for dep, description in critical_deps:
            try:
                __import__(dep)
                print(f"✅ {dep} - {description}")
            except ImportError:
                print(f"❌ {dep} - {description} (CRITICAL)")
                self.startup_errors.append(f"Missing critical dependency: {dep}")
                return False
        
        for dep, description in optional_deps:
            try:
                __import__(dep)
                print(f"✅ {dep} - {description}")
            except ImportError:
                print(f"⚠️  {dep} - {description} (Optional - some features may be limited)")
        
        # Data directory setup
        data_dir = project_root / "data"
        if not data_dir.exists():
            print("📁 Creating data directory...")
            data_dir.mkdir(exist_ok=True)
        print("✅ Data directory - Ready")
        
        return True
    
    def setup_signal_handlers(self):
        """Setup graceful shutdown handlers."""
        def shutdown_handler(signum, frame):
            print(f"\n🛑 Shutdown signal received ({signum})")
            self.graceful_shutdown()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, shutdown_handler)
        signal.signal(signal.SIGTERM, shutdown_handler)
    
    def start_jarvis_process(self) -> bool:
        """Start the main Jarvis application."""
        print("\n🎤 STARTING JARVIS")
        print("-" * 20)
        
        try:
            print("⏳ Launching Jarvis core system...")
            
            # Start Jarvis with proper environment
            env = os.environ.copy()
            env['PYTHONPATH'] = str(project_root)
            
            self.jarvis_process = subprocess.Popen(
                [sys.executable, "start_jarvis.py"],
                cwd=project_root,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                bufsize=1
            )
            
            # Wait for startup
            time.sleep(3)
            
            # Check if process is running
            if self.jarvis_process.poll() is None:
                self.is_running = True
                print("✅ Jarvis core system started successfully!")
                return True
            else:
                # Process failed
                stdout, stderr = self.jarvis_process.communicate()
                print("❌ Jarvis failed to start")
                if stderr:
                    print(f"Error: {stderr[:200]}...")
                self.startup_errors.append("Jarvis process failed to start")
                return False
                
        except Exception as e:
            print(f"❌ Exception starting Jarvis: {e}")
            self.startup_errors.append(f"Startup exception: {e}")
            return False
    
    def show_running_status(self):
        """Display running status and available features."""
        print("\n🎉 JARVIS IS NOW RUNNING!")
        print("=" * 40)
        print("🎤 Voice Commands Available:")
        print("   • 'Hey Jarvis' - Start conversation")
        print("   • 'Hey Jarvis, open user help' - Access documentation")
        print("   • 'Hey Jarvis, open settings' - Configure system")
        print("   • 'Hey Jarvis, show analytics' - View usage data")
        print("   • 'Hey Jarvis, what can you do?' - List capabilities")
        print()
        print("🖥️  Desktop Features:")
        print("   • Analytics Dashboard: python launch_analytics_dashboard.py")
        print("   • User Help Interface: python launch_user_help.py")
        print("   • Settings Interface: python jarvis_settings_app.py")
        print()
        print("🧠 Enhanced Capabilities:")
        print("   • Complete self-awareness of codebase")
        print("   • Real-time performance monitoring")
        print("   • Comprehensive plugin system")
        print("   • Advanced RAG memory system")
        print()
        print("🛑 To stop Jarvis: Press Ctrl+C or close this window")
        print("=" * 40)
    
    def monitor_process(self):
        """Monitor the Jarvis process."""
        try:
            while self.is_running and self.jarvis_process and self.jarvis_process.poll() is None:
                time.sleep(1)
            
            # Process ended
            if self.jarvis_process and self.jarvis_process.poll() is not None:
                return_code = self.jarvis_process.returncode
                if return_code != 0:
                    print(f"\n⚠️  Jarvis process ended unexpectedly (code: {return_code})")
                    stdout, stderr = self.jarvis_process.communicate()
                    if stderr:
                        print(f"Error output: {stderr[:300]}...")
                else:
                    print("\n✅ Jarvis shut down normally")
                    
        except KeyboardInterrupt:
            print("\n🛑 Shutdown requested")
            self.graceful_shutdown()
    
    def graceful_shutdown(self):
        """Perform graceful shutdown."""
        print("\n🔄 Shutting down Jarvis...")
        self.is_running = False
        
        if self.jarvis_process and self.jarvis_process.poll() is None:
            try:
                # Graceful termination
                self.jarvis_process.terminate()
                
                # Wait for graceful shutdown
                try:
                    self.jarvis_process.wait(timeout=10)
                    print("✅ Jarvis shut down gracefully")
                except subprocess.TimeoutExpired:
                    print("⚠️  Force terminating Jarvis...")
                    self.jarvis_process.kill()
                    self.jarvis_process.wait()
                    print("✅ Jarvis terminated")
                    
            except Exception as e:
                print(f"⚠️  Shutdown error: {e}")
        
        print("👋 Desktop launcher shutdown complete")
    
    def show_error_help(self):
        """Show troubleshooting help for errors."""
        if not self.startup_errors:
            return
            
        print("\n🔧 TROUBLESHOOTING")
        print("=" * 30)
        print("Startup errors detected:")
        for error in self.startup_errors:
            print(f"  • {error}")
        
        print("\n💡 Suggested Solutions:")
        print("  1. Install missing dependencies:")
        print("     pip install -r requirements-enhanced.txt")
        print("  2. Run system validation:")
        print("     python validate_implementation.py")
        print("  3. Check audio permissions in system settings")
        print("  4. Try running from terminal for detailed error messages")
        print("  5. Check documentation: python launch_user_help.py")
        print("\n📞 For more help:")
        print("  • GitHub: https://github.com/Prophet60191/jarvis")
        print("  • Documentation: See USER_GUIDE.md")
    
    def run(self):
        """Main launcher execution."""
        try:
            # Initialize
            self.print_header()
            self.setup_signal_handlers()
            
            # Validate environment
            if not self.validate_environment():
                print("\n❌ SYSTEM VALIDATION FAILED")
                self.show_error_help()
                input("\nPress Enter to exit...")
                return False
            
            print("\n✅ System validation complete!")
            
            # Start Jarvis
            if not self.start_jarvis_process():
                print("\n❌ FAILED TO START JARVIS")
                self.show_error_help()
                input("\nPress Enter to exit...")
                return False
            
            # Show status and monitor
            self.show_running_status()
            self.monitor_process()
            
            return True
            
        except KeyboardInterrupt:
            print("\n🛑 Startup interrupted")
            return False
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
            self.show_error_help()
            input("\nPress Enter to exit...")
            return False
        finally:
            self.graceful_shutdown()

def main():
    """Main entry point for desktop launcher."""
    launcher = DesktopJarvisLauncher()
    success = launcher.run()
    
    if not success:
        print("\n❌ Jarvis failed to start properly")
        input("Press Enter to exit...")
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
