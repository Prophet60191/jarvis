#!/bin/bash
# Jarvis Web UI Launcher for Unix/Linux/macOS
# Quick start shell script for the Jarvis Voice Assistant Web Configuration Interface

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Default values
PANEL="main"
PORT="8080"

# Function to display help
show_help() {
    echo
    echo "🤖 Jarvis Web UI Launcher"
    echo "========================"
    echo
    echo "Usage: $0 [panel] [options]"
    echo
    echo "Available panels:"
    echo "  main           Dashboard overview (default)"
    echo "  settings       Configuration overview"
    echo "  audio          Audio and TTS settings"
    echo "  llm            Language model configuration"
    echo "  conversation   Conversation flow settings"
    echo "  logging        Logging configuration"
    echo "  general        General application settings"
    echo "  voice-profiles Voice cloning management"
    echo "  device         Device and hardware information"
    echo
    echo "Options:"
    echo "  --port PORT    Use custom port (default: 8080)"
    echo "  --no-browser   Don't automatically open browser"
    echo "  --help, -h     Show this help message"
    echo
    echo "Examples:"
    echo "  $0                    # Launch main dashboard"
    echo "  $0 settings           # Launch settings overview"
    echo "  $0 audio              # Launch audio configuration"
    echo "  $0 main --port 3000   # Use custom port"
    echo
    echo "For advanced options, use:"
    echo "  python start_ui.py --help"
    echo
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --help|-h|help)
            show_help
            exit 0
            ;;
        --port)
            PORT="$2"
            shift 2
            ;;
        --no-browser)
            NO_BROWSER="--no-browser"
            shift
            ;;
        main|settings|audio|llm|conversation|logging|general|voice-profiles|device)
            PANEL="$1"
            shift
            ;;
        *)
            echo -e "${RED}❌ Unknown option: $1${NC}"
            echo "Use --help for usage information."
            exit 1
            ;;
    esac
done

echo
echo -e "${BLUE}🤖 Jarvis Web UI Launcher${NC}"
echo "========================"

# Check if Python is available
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo -e "${RED}❌ Python not found! Please install Python 3.8+ and add it to your PATH.${NC}"
    echo "   Download from: https://www.python.org/downloads/"
    exit 1
fi

# Use python3 if available, otherwise python
PYTHON_CMD="python3"
if ! command -v python3 &> /dev/null; then
    PYTHON_CMD="python"
fi

# Check if start_ui.py exists
if [[ ! -f "start_ui.py" ]]; then
    echo -e "${RED}❌ start_ui.py not found! Please run this from the Jarvis project directory.${NC}"
    exit 1
fi

echo -e "${GREEN}🚀 Starting Jarvis Web Interface...${NC}"
echo "   Panel: $PANEL"
echo "   Port: $PORT"
echo "   URL: http://localhost:$PORT"
echo

# Launch the UI
exec $PYTHON_CMD start_ui.py --panel "$PANEL" --port "$PORT" $NO_BROWSER
