#!/bin/bash

# RAG Management Desktop App Launcher (Unix/Linux/macOS)
# 
# Native desktop application for RAG document and memory management.

# Color codes for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to display help
show_help() {
    echo
    echo "🧠 RAG Management Desktop App Launcher"
    echo "======================================"
    echo
    echo "Usage: $0 [panel] [options]"
    echo
    echo "Available panels:"
    echo "  main           Main dashboard (default)"
    echo "  upload         Document upload interface"
    echo "  documents      Document library management"
    echo "  memory         Memory and conversation management"
    echo "  settings       RAG configuration settings"
    echo
    echo "Options:"
    echo "  --debug        Enable debug mode"
    echo "  --help, -h     Show this help message"
    echo
    echo "Examples:"
    echo "  $0                        # Launch main dashboard"
    echo "  $0 upload                 # Launch upload interface"
    echo "  $0 documents              # Launch document library"
    echo "  $0 memory                 # Launch memory management"
    echo "  $0 settings               # Launch RAG settings"
    echo
    echo "Voice Commands:"
    echo "  'Jarvis, open RAG manager'     # Open main dashboard"
    echo "  'Jarvis, open document manager' # Open upload interface"
    echo "  'Jarvis, close RAG manager'    # Close the application"
    echo
}

# Default values
PANEL="main"
DEBUG_FLAG=""

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        main|upload|documents|memory|settings)
            PANEL="$1"
            shift
            ;;
        --debug)
            DEBUG_FLAG="--debug"
            shift
            ;;
        --help|-h|help)
            show_help
            exit 0
            ;;
        *)
            echo -e "${RED}❌ Unknown option: $1${NC}"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Use python3 if available, otherwise python
PYTHON_CMD="python3"
if ! command -v python3 &> /dev/null; then
    PYTHON_CMD="python"
fi

# Check if start_rag_manager.py exists
if [[ ! -f "start_rag_manager.py" ]]; then
    echo -e "${RED}❌ start_rag_manager.py not found! Please run this from the Jarvis project directory.${NC}"
    exit 1
fi

echo -e "${GREEN}🧠 Starting RAG Management Desktop App...${NC}"
echo "   Panel: $PANEL"
echo

# Launch the desktop app
exec $PYTHON_CMD start_rag_manager.py "$PANEL" $DEBUG_FLAG
