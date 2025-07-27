#!/bin/bash
# Jarvis Desktop App Launcher Script for Unix/Linux/macOS
# 
# This script provides an easy way to launch the Jarvis Desktop Application
# with different panels and configurations.
#
# Usage:
#   ./start_desktop.sh                    # Main dashboard
#   ./start_desktop.sh settings          # Settings panel
#   ./start_desktop.sh audio             # Audio configuration

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}🤖 $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Default values
PANEL="${1:-main}"
PORT="${2:-8080}"
DEBUG_FLAG=""

# Parse additional arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --port)
            PORT="$2"
            shift 2
            ;;
        --debug)
            DEBUG_FLAG="--debug"
            shift
            ;;
        --help|-h)
            echo "Jarvis Desktop App Launcher"
            echo ""
            echo "Usage: $0 [panel] [options]"
            echo ""
            echo "Panels:"
            echo "  main          Main dashboard (default)"
            echo "  settings      Settings overview"
            echo "  audio         Audio configuration"
            echo "  llm           LLM settings"
            echo "  conversation  Conversation settings"
            echo "  logging       Logging configuration"
            echo "  general       General settings"
            echo "  voice-profiles Voice profile management"
            echo "  device        Device information"
            echo ""
            echo "Options:"
            echo "  --port PORT   Custom port (default: 8080)"
            echo "  --debug       Enable debug mode"
            echo "  --help        Show this help"
            echo ""
            echo "Examples:"
            echo "  $0                        # Main dashboard"
            echo "  $0 settings              # Settings panel"
            echo "  $0 audio --port 3000     # Audio config on port 3000"
            echo "  $0 llm --debug           # LLM settings with debug"
            exit 0
            ;;
        *)
            # If it's not a flag, treat it as panel name
            if [[ ! "$1" =~ ^-- ]]; then
                PANEL="$1"
            fi
            shift
            ;;
    esac
done

# Validate panel
VALID_PANELS=("main" "settings" "audio" "llm" "conversation" "logging" "general" "voice-profiles" "device")
if [[ ! " ${VALID_PANELS[@]} " =~ " ${PANEL} " ]]; then
    print_error "Invalid panel: $PANEL"
    echo "Valid panels: ${VALID_PANELS[*]}"
    exit 1
fi

print_status "Starting Jarvis Desktop Application"
echo "Panel: $PANEL"
echo "Port: $PORT"
if [[ -n "$DEBUG_FLAG" ]]; then
    echo "Debug: Enabled"
fi
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    print_error "Python is not installed or not in PATH"
    exit 1
fi

# Use python3 if available, otherwise python
PYTHON_CMD="python3"
if ! command -v python3 &> /dev/null; then
    PYTHON_CMD="python"
fi

# Check if pywebview is installed
print_status "Checking dependencies..."
if ! $PYTHON_CMD -c "import webview" 2>/dev/null; then
    print_warning "pywebview is not installed"
    echo "Installing pywebview..."
    if $PYTHON_CMD -m pip install pywebview; then
        print_success "pywebview installed successfully"
    else
        print_error "Failed to install pywebview"
        echo "Please install manually: pip install pywebview"
        exit 1
    fi
else
    print_success "pywebview is available"
fi

# Change to script directory
cd "$SCRIPT_DIR" || {
    print_error "Could not change to script directory: $SCRIPT_DIR"
    exit 1
}

# Launch the desktop app
print_status "Launching Jarvis Desktop App..."
exec $PYTHON_CMD jarvis_app.py --panel "$PANEL" --port "$PORT" $DEBUG_FLAG
