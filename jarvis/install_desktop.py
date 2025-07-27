#!/usr/bin/env python3
"""
Jarvis Desktop App Installer

This script installs the required dependencies for the Jarvis Desktop Application
and provides platform-specific setup instructions.
"""

import sys
import subprocess
import platform
import os
from pathlib import Path

def run_command(cmd, description=""):
    """Run a command and handle errors."""
    print(f"🔄 {description}")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} - Success")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - Failed")
        print(f"   Error: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ is required for the desktop app")
        print(f"   Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    
    print(f"✅ Python version {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def install_pywebview():
    """Install pywebview package."""
    print("\n📦 Installing pywebview...")
    
    # Try to install pywebview
    success = run_command(
        f"{sys.executable} -m pip install pywebview>=4.0.0",
        "Installing pywebview"
    )
    
    if not success:
        print("⚠️  Failed to install pywebview automatically")
        print("   Please install manually with: pip install pywebview")
        return False
    
    return True

def install_platform_dependencies():
    """Install platform-specific dependencies."""
    system = platform.system().lower()
    
    print(f"\n🖥️  Detected platform: {platform.system()}")
    
    if system == "darwin":  # macOS
        print("✅ macOS uses built-in WebKit - no additional dependencies needed")
        return True
        
    elif system == "windows":
        print("🔄 Windows detected - checking for Edge WebView2...")
        print("   If you encounter issues, install Edge WebView2 from:")
        print("   https://developer.microsoft.com/en-us/microsoft-edge/webview2/")
        
        # Optionally install pythonnet for better Windows integration
        print("\n🔄 Installing optional Windows dependencies...")
        run_command(
            f"{sys.executable} -m pip install pythonnet",
            "Installing pythonnet (optional Windows enhancement)"
        )
        return True
        
    elif system == "linux":
        print("🐧 Linux detected - checking for GTK dependencies...")
        
        # Check if we're on Ubuntu/Debian
        try:
            subprocess.run(["which", "apt"], check=True, capture_output=True)
            print("📦 Ubuntu/Debian detected - install GTK dependencies with:")
            print("   sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-3.0 gir1.2-webkit2-4.0")
        except subprocess.CalledProcessError:
            pass
        
        # Check if we're on Fedora/RHEL
        try:
            subprocess.run(["which", "dnf"], check=True, capture_output=True)
            print("📦 Fedora/RHEL detected - install GTK dependencies with:")
            print("   sudo dnf install python3-gobject gtk3-devel webkit2gtk3-devel")
        except subprocess.CalledProcessError:
            pass
        
        # Try to install PyGObject
        print("\n🔄 Installing optional Linux dependencies...")
        run_command(
            f"{sys.executable} -m pip install PyGObject",
            "Installing PyGObject (optional Linux enhancement)"
        )
        return True
    
    else:
        print(f"⚠️  Unknown platform: {system}")
        print("   pywebview should still work, but you may need platform-specific setup")
        return True

def test_installation():
    """Test if the installation was successful."""
    print("\n🧪 Testing installation...")
    
    try:
        import webview
        print("✅ pywebview imported successfully")
        
        # Test basic functionality
        try:
            print(f"   Version: {webview.__version__}")
        except AttributeError:
            print("   Version: Available (version info not accessible)")
        print("✅ Desktop app dependencies are ready!")
        return True
        
    except ImportError as e:
        print(f"❌ Failed to import pywebview: {e}")
        return False

def create_desktop_shortcut():
    """Create a desktop shortcut (optional)."""
    system = platform.system().lower()
    project_root = Path(__file__).parent
    
    if system == "darwin":  # macOS
        print("\n🔗 To create a macOS app bundle, you can use:")
        print("   py2app or create an Automator application")
        
    elif system == "windows":
        print("\n🔗 To create a Windows shortcut:")
        print(f"   Target: {sys.executable}")
        print(f"   Arguments: {project_root / 'jarvis_app.py'}")
        print(f"   Start in: {project_root}")
        
    elif system == "linux":
        desktop_file = f"""[Desktop Entry]
Name=Jarvis Control Panel
Comment=Jarvis Voice Assistant Desktop App
Exec={sys.executable} {project_root / 'jarvis_app.py'}
Icon={project_root / 'ui' / 'icon.png'}
Terminal=false
Type=Application
Categories=Utility;
"""
        print("\n🔗 To create a Linux desktop entry:")
        print("   Save this content to ~/.local/share/applications/jarvis.desktop:")
        print(desktop_file)

def main():
    """Main installer function."""
    print("🤖 Jarvis Desktop App Installer")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        return 1
    
    # Install pywebview
    if not install_pywebview():
        return 1
    
    # Install platform dependencies
    install_platform_dependencies()
    
    # Test installation
    if not test_installation():
        print("\n❌ Installation test failed")
        print("   Please check the error messages above and try manual installation")
        return 1
    
    # Offer to create shortcuts
    create_desktop_shortcut()
    
    print("\n🎉 Installation completed successfully!")
    print("\n🚀 You can now run the desktop app with:")
    print("   python jarvis_app.py")
    print("\n📚 For more options:")
    print("   python jarvis_app.py --help")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
