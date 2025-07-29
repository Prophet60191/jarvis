#!/bin/bash

# Jarvis Voice Assistant Startup Script - Clean Version
# This script starts the Jarvis voice assistant with clean, professional output

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Jarvis project directory
JARVIS_DIR="/Users/josed/Desktop/Voice App/jarvis"

echo -e "${BLUE}Starting Jarvis Voice Assistant...${NC}"
echo -e "${CYAN}================================================${NC}"

# Check if Jarvis directory exists
if [ ! -d "$JARVIS_DIR" ]; then
    echo -e "${RED}Error: Jarvis directory not found at $JARVIS_DIR${NC}"
    echo -e "${YELLOW}Please check the path and try again.${NC}"
    read -p "Press any key to exit..."
    exit 1
fi

# Change to Jarvis directory
cd "$JARVIS_DIR"
echo -e "${GREEN}Changed to Jarvis directory${NC}"

# Check if Python virtual environment exists
if [ -d "venv" ]; then
    echo -e "${GREEN}Activating Python virtual environment...${NC}"
    source venv/bin/activate
elif [ -d ".venv" ]; then
    echo -e "${GREEN}Activating Python virtual environment...${NC}"
    source .venv/bin/activate
else
    echo -e "${YELLOW}No virtual environment found. Using system Python.${NC}"
fi

# Check if Ollama is running
echo -e "${BLUE}Checking Ollama status...${NC}"
if ! command -v ollama &> /dev/null; then
    echo -e "${RED}Ollama not found. Please install Ollama first.${NC}"
    echo -e "${CYAN}Visit: https://ollama.ai${NC}"
    read -p "Press any key to exit..."
    exit 1
fi

# Check if Ollama service is running
if ! pgrep -x "ollama" > /dev/null; then
    echo -e "${YELLOW}Ollama service not running. Starting Ollama...${NC}"
    ollama serve &
    sleep 3
fi

# Check if required model is available
echo -e "${BLUE}Checking for AI model...${NC}"
if ! ollama list | grep -q "qwen2.5:7b-instruct"; then
    echo -e "${YELLOW}Required model 'qwen2.5:7b-instruct' not found.${NC}"
    echo -e "${BLUE}Downloading model (this may take a few minutes)...${NC}"
    ollama pull qwen2.5:7b-instruct
fi

# Load environment variables from .env file
echo -e "${BLUE}Loading environment configuration...${NC}"
if [ -f ".env" ]; then
    # Export environment variables from .env file
    set -a  # automatically export all variables
    source .env
    set +a  # stop automatically exporting
    echo -e "${GREEN}Environment variables loaded${NC}"
else
    echo -e "${YELLOW}No .env file found${NC}"
fi

# Display clean system info
echo -e "${CYAN}================================================${NC}"
echo -e "${PURPLE}Jarvis System Ready${NC}"
echo -e "${GREEN}Model: qwen2.5:7b-instruct${NC}"
echo -e "${GREEN}Tools: MCP enabled${NC}"
echo -e "${GREEN}Voice: Coqui TTS${NC}"

echo -e "${CYAN}================================================${NC}"
echo -e "${GREEN}Starting Jarvis Voice Assistant...${NC}"
echo -e "${YELLOW}Say 'Jarvis' to wake up • Press Ctrl+C to stop${NC}"
echo -e "${CYAN}================================================${NC}"

# Start Jarvis with clean output
python -m jarvis.main

# Handle exit
echo -e "${BLUE}Jarvis has stopped.${NC}"
echo -e "${YELLOW}Thank you for using Jarvis Voice Assistant!${NC}"
read -p "Press any key to close this window..."
