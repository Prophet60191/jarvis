#!/usr/bin/env python3
"""
User Help UI Launcher

Launches the Jarvis User Help interface for testing and demonstration.
"""

import sys
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def main():
    """Launch the User Help UI."""
    print("🚀 Launching Jarvis User Help Interface...")
    print("=" * 50)
    
    try:
        # Check dependencies
        try:
            import PyQt6
            print("✅ PyQt6 found")
        except ImportError:
            print("❌ PyQt6 not found - installing...")
            import subprocess
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", "PyQt6"])
                print("✅ PyQt6 installed successfully")
            except subprocess.CalledProcessError:
                print("❌ Failed to install PyQt6")
                print("   Please install manually: pip install PyQt6")
                return False
        
        # Launch the help UI
        from jarvis.jarvis.ui.user_help_ui import main as help_main
        print("✅ Starting User Help UI...")
        help_main()
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   Make sure all dependencies are installed")
        return False
    except Exception as e:
        print(f"❌ Error launching User Help: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
