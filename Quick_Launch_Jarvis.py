#!/usr/bin/env python3
"""
🚀 QUICK LAUNCH JARVIS

Simple, fast launcher for Jarvis Voice Assistant.
Perfect for desktop shortcuts and quick access.
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """Quick launch Jarvis with minimal setup."""

    # Determine the correct application directory
    script_location = Path(__file__).parent

    # If running from desktop, navigate to the actual Jarvis directory
    if "Desktop" in str(script_location):
        app_dir = Path("/Users/josed/Desktop/Voice App")
        if not app_dir.exists():
            print("❌ Jarvis application directory not found!")
            print(f"Expected location: {app_dir}")
            return
    else:
        app_dir = script_location
    
    # Print quick header
    print("🎯 JARVIS QUICK LAUNCHER")
    print("=" * 30)
    print("🚀 Starting Jarvis...")
    
    # Change to app directory
    os.chdir(app_dir)
    
    # Launch the desktop launcher
    try:
        result = subprocess.run([
            sys.executable, 
            "Desktop_Jarvis_Launcher.py"
        ], cwd=app_dir)
        
        if result.returncode == 0:
            print("✅ Jarvis finished successfully")
        else:
            print(f"⚠️  Jarvis exited with code: {result.returncode}")
            
    except KeyboardInterrupt:
        print("\n🛑 Launch cancelled by user")
    except Exception as e:
        print(f"❌ Error launching Jarvis: {e}")
        print("💡 Try running Desktop_Jarvis_Launcher.py directly")

if __name__ == "__main__":
    main()
