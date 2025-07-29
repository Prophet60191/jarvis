#!/bin/bash

# 🎯 JARVIS DESKTOP LAUNCHER - macOS Command Script
# ==================================================
# 
# This script launches Jarvis Voice Assistant from the desktop on macOS.
# It provides a clean, user-friendly startup experience with error handling.
#
# Usage: Double-click this file from Finder or run from Terminal
#

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# If we're running from desktop, navigate to the Jarvis application directory
if [[ "$SCRIPT_DIR" == *"/Desktop" ]]; then
    # Assume Jarvis is in the "Voice App" directory on desktop
    JARVIS_DIR="/Users/josed/Desktop/Voice App"
    if [ -d "$JARVIS_DIR" ]; then
        cd "$JARVIS_DIR"
        print_color $YELLOW "📁 Navigated to Jarvis application directory: $JARVIS_DIR"
    else
        print_color $RED "❌ Jarvis application directory not found at: $JARVIS_DIR"
        exit 1
    fi
else
    cd "$SCRIPT_DIR"
fi

# Function to print colored output
print_color() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Function to print header
print_header() {
    clear
    print_color $CYAN "╔══════════════════════════════════════════════════════════════════════╗"
    print_color $CYAN "║                                                                      ║"
    print_color $CYAN "║    🎯 JARVIS ENHANCED VOICE ASSISTANT - DESKTOP LAUNCHER             ║"
    print_color $CYAN "║                                                                      ║"
    print_color $CYAN "║    Your intelligent AI assistant with complete self-awareness,      ║"
    print_color $CYAN "║    real-time analytics, and comprehensive documentation support.     ║"
    print_color $CYAN "║                                                                      ║"
    print_color $CYAN "║    🧠 Self-Aware AI  📊 Analytics  🎤 Voice Control  📚 Help UI      ║"
    print_color $CYAN "║                                                                      ║"
    print_color $CYAN "╚══════════════════════════════════════════════════════════════════════╝"
    echo
    print_color $GREEN "🚀 Starting Jarvis Enhanced Voice Assistant..."
    echo "======================================================================"
}

# Function to check system requirements
check_requirements() {
    print_color $BLUE "🔍 Checking system requirements..."
    
    # Check if Python 3 is available
    if ! command -v python3 &> /dev/null; then
        print_color $RED "❌ Python 3 is not installed or not in PATH"
        print_color $YELLOW "💡 Please install Python 3.8+ from https://python.org"
        return 1
    fi
    
    # Check Python version
    python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    print_color $GREEN "✅ Python $python_version detected"
    
    # Check if we're in the right directory
    if [ ! -f "start_jarvis.py" ]; then
        print_color $RED "❌ start_jarvis.py not found in current directory"
        print_color $YELLOW "💡 Please ensure this script is in the Jarvis application directory"
        return 1
    fi
    
    print_color $GREEN "✅ Jarvis application files found"
    
    # Check if Desktop_Jarvis_Launcher.py exists
    if [ ! -f "Desktop_Jarvis_Launcher.py" ]; then
        print_color $RED "❌ Desktop_Jarvis_Launcher.py not found"
        print_color $YELLOW "💡 The Python launcher script is missing"
        return 1
    fi
    
    print_color $GREEN "✅ Desktop launcher script found"
    
    return 0
}

# Function to show startup progress
show_progress() {
    local message=$1
    local duration=${2:-2}
    
    print_color $YELLOW "⏳ $message"
    for i in $(seq 1 $duration); do
        sleep 1
        echo -n "."
    done
    echo
}

# Function to launch Jarvis
launch_jarvis() {
    print_color $BLUE "🎤 Launching Jarvis Voice Assistant..."
    echo
    
    # Launch the Python desktop launcher
    python3 Desktop_Jarvis_Launcher.py
    
    local exit_code=$?
    
    if [ $exit_code -eq 0 ]; then
        print_color $GREEN "✅ Jarvis shut down normally"
    else
        print_color $RED "❌ Jarvis exited with error code: $exit_code"
        show_troubleshooting
    fi
    
    return $exit_code
}

# Function to show troubleshooting information
show_troubleshooting() {
    echo
    print_color $YELLOW "🔧 TROUBLESHOOTING TIPS:"
    echo "========================================"
    print_color $CYAN "• Check microphone permissions in System Preferences > Security & Privacy"
    print_color $CYAN "• Ensure no other voice assistants (Siri, etc.) are interfering"
    print_color $CYAN "• Try running: python3 validate_implementation.py"
    print_color $CYAN "• Install dependencies: pip3 install -r requirements-enhanced.txt"
    print_color $CYAN "• Check logs in the data/ directory"
    print_color $CYAN "• For detailed help: python3 launch_user_help.py"
    print_color $CYAN "• Documentation: https://github.com/Prophet60191/jarvis"
    echo
}

# Function to handle cleanup on exit
cleanup() {
    echo
    print_color $PURPLE "🧹 Cleaning up..."
    # Kill any remaining Jarvis processes
    pkill -f "start_jarvis.py" 2>/dev/null || true
    pkill -f "Desktop_Jarvis_Launcher.py" 2>/dev/null || true
    print_color $GREEN "👋 Desktop launcher cleanup complete"
}

# Function to handle interruption
handle_interrupt() {
    echo
    print_color $YELLOW "🛑 Interrupt signal received"
    cleanup
    exit 0
}

# Main execution
main() {
    # Set up signal handlers
    trap handle_interrupt SIGINT SIGTERM
    
    # Show header
    print_header
    
    # Check requirements
    if ! check_requirements; then
        echo
        print_color $RED "❌ System requirements not met!"
        show_troubleshooting
        echo
        print_color $YELLOW "Press any key to exit..."
        read -n 1
        exit 1
    fi
    
    echo
    print_color $GREEN "✅ System validation complete!"
    
    # Show startup message
    echo
    print_color $PURPLE "🎯 JARVIS FEATURES:"
    print_color $CYAN "   • 🧠 Complete self-awareness of codebase"
    print_color $CYAN "   • 📊 Real-time analytics and performance monitoring"
    print_color $CYAN "   • 🎤 Advanced voice command processing"
    print_color $CYAN "   • 📚 Voice-controlled documentation interface"
    print_color $CYAN "   • 🔧 Comprehensive plugin system"
    print_color $CYAN "   • ⚡ Enhanced performance optimization"
    
    echo
    show_progress "Initializing Jarvis components" 3
    
    # Launch Jarvis
    if launch_jarvis; then
        print_color $GREEN "🎉 Jarvis session completed successfully!"
    else
        print_color $RED "❌ Jarvis encountered an error"
        echo
        print_color $YELLOW "Press any key to exit..."
        read -n 1
        exit 1
    fi
    
    # Cleanup
    cleanup
    
    echo
    print_color $GREEN "✅ Desktop launcher finished"
    echo
    print_color $YELLOW "Press any key to close this window..."
    read -n 1
}

# Run main function
main "$@"
