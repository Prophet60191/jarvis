#!/usr/bin/env python3
"""
Jarvis Voice Assistant Startup Script

This script provides a user-friendly way to start Jarvis with proper
error handling, permission checking, and diagnostic information.
"""

import sys
import os
import subprocess
from pathlib import Path
import argparse

def print_header():
    """Print the Jarvis startup header."""
    print("🤖 Jarvis Voice Assistant")
    print("=" * 50)
    print("Privacy-first AI voice assistant with local processing")
    print()

def check_requirements():
    """Check if all requirements are met."""
    print("🔍 Checking system requirements...")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required. Current version:", sys.version)
        return False
    print(f"✅ Python {sys.version.split()[0]}")
    
    # Check if we're in the right directory
    if not Path("jarvis/jarvis/main.py").exists():
        print("❌ Please run this script from the Voice App root directory")
        print("   Expected structure: Voice App/jarvis/jarvis/main.py")
        return False
    print("✅ Directory structure correct")
    
    # Check if package is installed
    try:
        import jarvis
        print("✅ Jarvis package installed")
    except ImportError:
        print("❌ Jarvis package not installed")
        print("   Run: pip install -e jarvis/")
        return False
    
    # Check Ollama
    try:
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Ollama running")
            
            # Check for required model
            if "qwen2.5:7b-instruct" in result.stdout:
                print("✅ qwen2.5:7b-instruct model available")
            else:
                print("⚠️  qwen2.5:7b-instruct model not found")
                print("   Run: ollama pull qwen2.5:7b-instruct")
        else:
            print("❌ Ollama not running")
            print("   Start Ollama first")
            return False
    except FileNotFoundError:
        print("❌ Ollama not installed")
        print("   Install from: https://ollama.ai")
        return False
    
    return True

def run_audio_diagnostics():
    """Run audio system diagnostics."""
    print("\n🎤 Running audio diagnostics...")
    
    try:
        result = subprocess.run([
            sys.executable, "jarvis/diagnose_audio.py"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Audio system working correctly")
            return True
        else:
            print("❌ Audio system issues detected:")
            print(result.stdout)
            if result.stderr:
                print("Errors:", result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Error running audio diagnostics: {e}")
        return False

def check_permissions():
    """Check microphone permissions on macOS."""
    if sys.platform != "darwin":
        return True

    print("\n🔐 Checking microphone permissions...")

    try:
        # Import here to avoid issues if jarvis isn't installed
        import jarvis.audio.microphone

        if jarvis.audio.microphone.MicrophoneManager.check_microphone_permissions():
            print("✅ Microphone permissions granted")
            return True
        else:
            print("❌ Microphone permissions required")
            print("\n🔧 To fix this:")
            print("1. Open System Preferences > Security & Privacy > Privacy")
            print("2. Select 'Microphone' from the left sidebar")
            print("3. Check the box next to your terminal/IDE application")
            print("4. Restart your terminal/IDE and try again")
            return False

    except Exception as e:
        print(f"⚠️  Could not check permissions: {e}")
        return True  # Continue anyway

def start_jarvis(mode="voice", debug=False):
    """Start Jarvis in the specified mode."""
    print(f"\n🚀 Starting Jarvis in {mode} mode...")
    
    try:
        if mode == "voice":
            # Start full voice assistant
            os.chdir("jarvis")
            if debug:
                subprocess.run([sys.executable, "-m", "jarvis.main", "--debug"])
            else:
                subprocess.run([sys.executable, "-m", "jarvis.main"])
                
        elif mode == "ui":
            # Start web UI only
            subprocess.run([sys.executable, "jarvis_app.py"])
            
        elif mode == "test":
            # Run test mode
            subprocess.run([sys.executable, "test_jarvis_core.py"])
            
    except KeyboardInterrupt:
        print("\n👋 Jarvis stopped by user")
    except Exception as e:
        print(f"❌ Error starting Jarvis: {e}")
        return False
    
    return True

def main():
    """Main startup function."""
    parser = argparse.ArgumentParser(
        description="Start Jarvis Voice Assistant",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python start_jarvis.py                    # Start voice assistant
  python start_jarvis.py --mode ui          # Start web UI only
  python start_jarvis.py --mode test        # Run test mode
  python start_jarvis.py --debug            # Start with debug logging
  python start_jarvis.py --skip-checks      # Skip system checks
        """
    )
    
    parser.add_argument(
        "--mode",
        choices=["voice", "ui", "test"],
        default="voice",
        help="Startup mode (default: voice)"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    
    parser.add_argument(
        "--skip-checks",
        action="store_true",
        help="Skip system requirement checks"
    )
    
    parser.add_argument(
        "--skip-audio",
        action="store_true",
        help="Skip audio diagnostics"
    )
    
    args = parser.parse_args()
    
    print_header()
    
    # Run system checks unless skipped
    if not args.skip_checks:
        if not check_requirements():
            print("\n❌ System requirements not met. Please fix the issues above.")
            return 1
        
        if not check_permissions():
            print("\n❌ Permission issues detected. Please fix the issues above.")
            return 1
    
    # Run audio diagnostics unless skipped or in UI mode
    if not args.skip_audio and args.mode != "ui":
        if not run_audio_diagnostics():
            print("\n⚠️  Audio issues detected. Jarvis may not work properly.")
            response = input("Continue anyway? (y/N): ").strip().lower()
            if response not in ['y', 'yes']:
                return 1
    
    # Start Jarvis
    success = start_jarvis(args.mode, args.debug)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
