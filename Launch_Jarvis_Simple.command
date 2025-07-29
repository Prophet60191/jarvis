#!/bin/bash

# 🎯 JARVIS SIMPLE DESKTOP LAUNCHER
# =================================
# 
# Simple, reliable launcher for Jarvis Voice Assistant
# This script always navigates to the correct directory
#

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to print colored output
print_color() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Clear screen and show header
clear
print_color $CYAN "╔══════════════════════════════════════════════════════════════════════╗"
print_color $CYAN "║                                                                      ║"
print_color $CYAN "║    🎯 JARVIS ENHANCED VOICE ASSISTANT - SIMPLE LAUNCHER             ║"
print_color $CYAN "║                                                                      ║"
print_color $CYAN "║    🧠 Self-Aware AI  📊 Analytics  🎤 Voice Control  📚 Help UI      ║"
print_color $CYAN "║                                                                      ║"
print_color $CYAN "╚══════════════════════════════════════════════════════════════════════╝"
echo

# Navigate to the Jarvis application directory
JARVIS_DIR="/Users/josed/Desktop/Voice App"

print_color $BLUE "📁 Navigating to Jarvis directory: $JARVIS_DIR"

if [ ! -d "$JARVIS_DIR" ]; then
    print_color $RED "❌ Jarvis directory not found: $JARVIS_DIR"
    echo
    print_color $YELLOW "Press any key to exit..."
    read -n 1
    exit 1
fi

cd "$JARVIS_DIR"

# Verify we're in the right place
if [ ! -f "start_jarvis.py" ]; then
    print_color $RED "❌ start_jarvis.py not found in: $(pwd)"
    echo
    print_color $YELLOW "Directory contents:"
    ls -la
    echo
    print_color $YELLOW "Press any key to exit..."
    read -n 1
    exit 1
fi

print_color $GREEN "✅ Found Jarvis application files"

# Check Python
if ! command -v python3 &> /dev/null; then
    print_color $RED "❌ Python 3 not found"
    echo
    print_color $YELLOW "Press any key to exit..."
    read -n 1
    exit 1
fi

print_color $GREEN "✅ Python 3 available"

# Launch Jarvis
echo
print_color $BLUE "🚀 Starting Jarvis Enhanced Voice Assistant..."
print_color $YELLOW "⏳ Please wait while Jarvis initializes..."
echo

# Run the Python desktop launcher
python3 Desktop_Jarvis_Launcher.py

# Check exit status
exit_code=$?

echo
if [ $exit_code -eq 0 ]; then
    print_color $GREEN "✅ Jarvis finished successfully"
else
    print_color $RED "❌ Jarvis exited with error code: $exit_code"
    echo
    print_color $YELLOW "🔧 Troubleshooting tips:"
    print_color $CYAN "• Check microphone permissions in System Preferences"
    print_color $CYAN "• Try: python3 validate_implementation.py"
    print_color $CYAN "• Install dependencies: pip3 install -r requirements-enhanced.txt"
fi

echo
print_color $YELLOW "Press any key to close..."
read -n 1
