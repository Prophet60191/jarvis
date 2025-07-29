#!/usr/bin/env python3
"""
🎯 SIMPLE JARVIS LAUNCHER

Ultra-reliable launcher that always works from any location.
Perfect for desktop shortcuts.
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """Simple, reliable Jarvis launcher."""
    
    # Clear screen
    os.system('cls' if os.name == 'nt' else 'clear')
    
    # Header
    print("╔══════════════════════════════════════════════════════════════════════╗")
    print("║                                                                      ║")
    print("║    🎯 JARVIS ENHANCED VOICE ASSISTANT - SIMPLE LAUNCHER             ║")
    print("║                                                                      ║")
    print("║    🧠 Self-Aware AI  📊 Analytics  🎤 Voice Control  📚 Help UI      ║")
    print("║                                                                      ║")
    print("╚══════════════════════════════════════════════════════════════════════╝")
    print()
    
    # Always use the known Jarvis directory
    jarvis_dir = Path("/Users/josed/Desktop/Voice App")
    
    print(f"📁 Navigating to Jarvis directory: {jarvis_dir}")
    
    # Check if directory exists
    if not jarvis_dir.exists():
        print(f"❌ Jarvis directory not found: {jarvis_dir}")
        input("\nPress Enter to exit...")
        return
    
    # Change to Jarvis directory
    os.chdir(jarvis_dir)
    
    # Verify start_jarvis.py exists
    start_script = jarvis_dir / "start_jarvis.py"
    if not start_script.exists():
        print(f"❌ start_jarvis.py not found in: {jarvis_dir}")
        print("\nDirectory contents:")
        for item in jarvis_dir.iterdir():
            print(f"  {item.name}")
        input("\nPress Enter to exit...")
        return
    
    print("✅ Found Jarvis application files")
    
    # Check Python
    try:
        python_version = sys.version.split()[0]
        print(f"✅ Python {python_version} available")
    except:
        print("❌ Python version check failed")
        input("\nPress Enter to exit...")
        return
    
    # Launch Jarvis
    print("\n🚀 Starting Jarvis Enhanced Voice Assistant...")
    print("⏳ Please wait while Jarvis initializes...")
    print()
    
    try:
        # First try the desktop launcher if it exists
        desktop_launcher = jarvis_dir / "Desktop_Jarvis_Launcher.py"
        if desktop_launcher.exists():
            print("🎯 Using Desktop Launcher...")
            result = subprocess.run([sys.executable, "Desktop_Jarvis_Launcher.py"], cwd=jarvis_dir)
        else:
            # Fallback to direct start_jarvis.py
            print("🎯 Using Direct Launcher...")
            result = subprocess.run([sys.executable, "start_jarvis.py"], cwd=jarvis_dir)
        
        # Check result
        if result.returncode == 0:
            print("\n✅ Jarvis finished successfully")
        else:
            print(f"\n❌ Jarvis exited with error code: {result.returncode}")
            print("\n🔧 Troubleshooting tips:")
            print("• Check microphone permissions in System Preferences")
            print("• Try: python3 validate_implementation.py")
            print("• Install dependencies: pip3 install -r requirements-enhanced.txt")
            
    except KeyboardInterrupt:
        print("\n🛑 Launch cancelled by user")
    except Exception as e:
        print(f"\n❌ Error launching Jarvis: {e}")
        print("\n🔧 Try running start_jarvis.py directly from the application directory")
    
    print("\nPress Enter to close...")
    input()

if __name__ == "__main__":
    main()
