# Open Interpreter MCP Server - Usage Guide

## 🎯 Overview

Open Interpreter is now integrated with Jarvis as an MCP (Model Context Protocol) server, providing powerful local code execution capabilities through voice commands.

## 🎤 Voice Commands

### Data Analysis
- "Execute code to analyze this CSV file and create a chart"
- "Analyze the data in sales.csv and show me trends"
- "Calculate the correlation between these columns"

### File Management
- "Execute code to organize my photos by date"
- "Create a backup script for my documents"
- "Check my disk usage and show largest folders"

### System Tasks
- "Perform system task to check running processes"
- "Execute code to monitor CPU usage"
- "Create a script to clean temporary files"

### Code Creation
- "Create a Python script to download images from URLs"
- "Generate a web scraper for this website"
- "Write a script to convert CSV to JSON"

## 🔧 Available MCP Tools

1. **execute_code** - General code execution for any programming task
2. **analyze_file** - Analyze files with code (CSV, JSON, text, etc.)
3. **create_script** - Generate scripts and programs on demand
4. **system_task** - System administration and maintenance tasks

## 🔒 Security Features

- **100% Local**: All code execution happens on your machine
- **Permission-Based**: Asks before running potentially dangerous code
- **Safe Mode**: Built-in safety checks for system operations
- **No Cloud**: Uses your local Ollama llama3.1:8b model

## 🚀 Getting Started

1. **Restart Jarvis** to load the new MCP server
2. **Try voice commands** like the examples above
3. **Check MCP status** in the Jarvis UI at http://localhost:8080/mcp

## 🔧 Troubleshooting

If tools don't appear:
1. Check that Ollama is running: `ollama serve`
2. Verify MCP server status in Jarvis UI
3. Check logs: `tail -f open_interpreter_mcp.log`
4. Restart Jarvis to reload MCP servers

## 📊 MCP vs Plugin Comparison

**MCP Server Advantages:**
- ✅ Dynamic loading without restart
- ✅ Better isolation and error handling
- ✅ Standardized protocol
- ✅ Real-time status monitoring
- ✅ Easy enable/disable through UI

**Integration Benefits:**
- Voice-activated code execution
- Seamless tool discovery
- Automatic error recovery
- Performance monitoring
- Configuration through UI
