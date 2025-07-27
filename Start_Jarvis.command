#!/bin/bash

# Jarvis Voice Assistant Startup Script
# This script starts the Jarvis voice assistant with proper environment setup

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

echo -e "${BLUE}🤖 Starting Jarvis Voice Assistant...${NC}"
echo -e "${CYAN}================================================${NC}"

# Check if Jarvis directory exists
if [ ! -d "$JARVIS_DIR" ]; then
    echo -e "${RED}❌ Error: Jarvis directory not found at $JARVIS_DIR${NC}"
    echo -e "${YELLOW}Please check the path and try again.${NC}"
    read -p "Press any key to exit..."
    exit 1
fi

# Change to Jarvis directory
cd "$JARVIS_DIR"
echo -e "${GREEN}📁 Changed to Jarvis directory: $JARVIS_DIR${NC}"

# Check if Python virtual environment exists
if [ -d "venv" ]; then
    echo -e "${GREEN}🐍 Activating Python virtual environment...${NC}"
    source venv/bin/activate
elif [ -d ".venv" ]; then
    echo -e "${GREEN}🐍 Activating Python virtual environment...${NC}"
    source .venv/bin/activate
else
    echo -e "${YELLOW}⚠️  No virtual environment found. Using system Python.${NC}"
fi

# Check if Ollama is running
echo -e "${BLUE}🔍 Checking Ollama status...${NC}"
if ! command -v ollama &> /dev/null; then
    echo -e "${RED}❌ Ollama not found. Please install Ollama first.${NC}"
    echo -e "${CYAN}Visit: https://ollama.ai${NC}"
    read -p "Press any key to exit..."
    exit 1
fi

# Check if Ollama service is running
if ! pgrep -x "ollama" > /dev/null; then
    echo -e "${YELLOW}⚠️  Ollama service not running. Starting Ollama...${NC}"
    ollama serve &
    sleep 3
fi

# Check if required model is available
echo -e "${BLUE}🔍 Checking for AI model...${NC}"
if ! ollama list | grep -q "llama3.1:8b"; then
    echo -e "${YELLOW}⚠️  Required model 'llama3.1:8b' not found.${NC}"
    echo -e "${BLUE}📥 Downloading model (this may take a few minutes)...${NC}"
    ollama pull llama3.1:8b
fi

# Check Python dependencies
echo -e "${BLUE}🔍 Checking Python dependencies...${NC}"
if [ -f "requirements.txt" ]; then
    python -c "
import pkg_resources
import sys

try:
    with open('requirements.txt', 'r') as f:
        requirements = f.read().splitlines()
    
    for requirement in requirements:
        if requirement.strip() and not requirement.startswith('#'):
            try:
                pkg_resources.require(requirement.strip())
            except:
                print(f'Missing: {requirement.strip()}')
                sys.exit(1)
    print('All dependencies satisfied')
except Exception as e:
    print(f'Error checking dependencies: {e}')
    sys.exit(1)
"
    
    if [ $? -ne 0 ]; then
        echo -e "${YELLOW}⚠️  Installing missing dependencies...${NC}"
        pip install -r requirements.txt
    fi
else
    echo -e "${YELLOW}⚠️  requirements.txt not found${NC}"
fi

# Display system info
echo -e "${CYAN}================================================${NC}"
echo -e "${PURPLE}🎯 Jarvis System Information:${NC}"
echo -e "${GREEN}📍 Location: $JARVIS_DIR${NC}"
echo -e "${GREEN}🐍 Python: $(python --version)${NC}"
echo -e "${GREEN}🤖 Ollama: $(ollama --version 2>/dev/null || echo 'Version check failed')${NC}"
echo -e "${GREEN}🧠 AI Model: llama3.1:8b (Single Model)${NC}"

echo -e "${CYAN}================================================${NC}"
echo -e "${GREEN}🚀 Starting Jarvis Voice Assistant...${NC}"
echo -e "${YELLOW}💡 Say 'Jarvis' to wake up the assistant${NC}"
echo -e "${YELLOW}💡 Press Ctrl+C to stop Jarvis${NC}"
echo -e "${CYAN}================================================${NC}"

# Pre-check MCP system
echo -e "${BLUE}🔧 Checking MCP system...${NC}"
python -c "
import sys
import os
import time
sys.path.insert(0, os.getcwd())

try:
    from jarvis.tools import start_mcp_system, get_mcp_tool_manager
    print('🚀 Starting MCP system...')
    result = start_mcp_system()
    print(f'MCP start result: {result}')

    # Give MCP time to connect
    print('⏳ Waiting for MCP connections...')
    time.sleep(5)

    tool_manager = get_mcp_tool_manager()
    if tool_manager:
        tool_count = tool_manager.get_tool_count()
        print(f'✅ MCP tools available: {tool_count}')
        if tool_count > 0:
            print('🎉 MCP system ready!')
        else:
            print('⚠️ MCP started but no tools discovered')
    else:
        print('❌ MCP tool manager not available')

except Exception as e:
    print(f'❌ MCP check failed: {e}')
"

echo -e "${CYAN}================================================${NC}"

# Start Jarvis with MCP pre-initialized
echo -e "${GREEN}🚀 Starting Jarvis Voice Assistant with MCP...${NC}"
python -m jarvis.main

# Handle exit
echo -e "${BLUE}👋 Jarvis has stopped.${NC}"
echo -e "${YELLOW}Thank you for using Jarvis Voice Assistant!${NC}"
read -p "Press any key to close this window..."
