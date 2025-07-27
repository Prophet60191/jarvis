#!/bin/bash
# Jarvis Voice Assistant Launcher Script

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
    echo -e "${BLUE}ℹ️${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "start_jarvis.py" ]; then
    print_error "Please run this script from the Voice App root directory"
    exit 1
fi

# Make sure Python startup script is executable
chmod +x start_jarvis.py

# Parse command line arguments
MODE="voice"
EXTRA_ARGS=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --mode)
            MODE="$2"
            shift 2
            ;;
        --debug)
            EXTRA_ARGS="$EXTRA_ARGS --debug"
            shift
            ;;
        --skip-checks)
            EXTRA_ARGS="$EXTRA_ARGS --skip-checks"
            shift
            ;;
        --skip-audio)
            EXTRA_ARGS="$EXTRA_ARGS --skip-audio"
            shift
            ;;
        --help|-h)
            echo "Jarvis Voice Assistant Launcher"
            echo ""
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --mode MODE        Startup mode: voice, ui, test (default: voice)"
            echo "  --debug           Enable debug logging"
            echo "  --skip-checks     Skip system requirement checks"
            echo "  --skip-audio      Skip audio diagnostics"
            echo "  --help, -h        Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                    # Start voice assistant"
            echo "  $0 --mode ui          # Start web UI only"
            echo "  $0 --mode test        # Run test mode"
            echo "  $0 --debug            # Start with debug logging"
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Header
echo "🤖 Jarvis Voice Assistant Launcher"
echo "=================================="

# Run the Python startup script
print_info "Starting Jarvis..."
python3 start_jarvis.py --mode "$MODE" $EXTRA_ARGS

exit_code=$?

if [ $exit_code -eq 0 ]; then
    print_status "Jarvis exited normally"
else
    print_error "Jarvis exited with error code $exit_code"
fi

exit $exit_code
