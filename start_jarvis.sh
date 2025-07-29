#!/bin/bash
# Jarvis Voice Assistant Startup Script (macOS/Linux)
# 
# This script provides an easy way to start Jarvis with proper environment setup.
# 
# Usage:
#   chmod +x start_jarvis.sh
#   ./start_jarvis.sh

# Configuration
JARVIS_PROJECT_PATH="$HOME/Desktop/Voice App"
JARVIS_MAIN_SCRIPT="jarvis_app.py"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠️${NC} $1"
}

print_error() {
    echo -e "${RED}❌${NC} $1"
}

print_info() {
    echo -e "${BLUE}🔍${NC} $1"
}

# Print banner
echo "================================================================================"
echo "🎤 JARVIS VOICE ASSISTANT LAUNCHER"
echo "================================================================================"
echo "Project Path: $JARVIS_PROJECT_PATH"
echo "Main Script: $JARVIS_MAIN_SCRIPT"
echo "Shell: $SHELL"
echo "================================================================================"

# Check if project directory exists
if [ ! -d "$JARVIS_PROJECT_PATH" ]; then
    print_error "Project directory not found: $JARVIS_PROJECT_PATH"
    print_error "Please update JARVIS_PROJECT_PATH in this script"
    exit 1
fi
print_status "Project directory found"

# Check if main script exists
if [ ! -f "$JARVIS_PROJECT_PATH/$JARVIS_MAIN_SCRIPT" ]; then
    print_error "Main script not found: $JARVIS_PROJECT_PATH/$JARVIS_MAIN_SCRIPT"
    exit 1
fi
print_status "Main script found"

# Check Python version
python_version=$(python3 --version 2>/dev/null | cut -d' ' -f2)
if [ -z "$python_version" ]; then
    print_error "Python 3 not found. Please install Python 3.8+"
    exit 1
fi
print_status "Python version: $python_version"

# Check for virtual environment
if [ -n "$VIRTUAL_ENV" ]; then
    print_status "Virtual environment: $VIRTUAL_ENV"
else
    print_warning "No virtual environment detected (recommended but not required)"
fi

# Change to project directory
cd "$JARVIS_PROJECT_PATH" || {
    print_error "Failed to change to project directory"
    exit 1
}

print_info "Changed to project directory: $(pwd)"

# Function to handle cleanup on exit
cleanup() {
    echo ""
    print_info "Shutting down Jarvis..."
    # Kill any remaining Jarvis processes
    pkill -f "$JARVIS_MAIN_SCRIPT" 2>/dev/null
    print_status "Jarvis shutdown complete"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Start Jarvis
echo ""
print_info "Starting Jarvis..."
echo "================================================================================"
echo "🎤 Jarvis is starting up..."
echo "================================================================================"
echo "Voice commands available:"
echo "• 'Open vault' - Open the knowledge vault"
echo "• 'Open settings' - Open Jarvis settings"
echo "• 'Close vault' - Close the vault"
echo "• 'Close settings' - Close settings"
echo "• And many more..."
echo "================================================================================"
echo "Press Ctrl+C to stop Jarvis"
echo "================================================================================"

# Launch Jarvis
python3 "$JARVIS_MAIN_SCRIPT"

# If we get here, Jarvis has exited
echo ""
print_info "Jarvis has stopped"
cleanup
