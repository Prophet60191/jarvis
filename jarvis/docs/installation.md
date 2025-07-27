# Installation Guide

This guide will walk you through installing and setting up Jarvis Voice Assistant on your system.

## System Requirements

### Operating System
- **macOS**: 10.14 (Mojave) or later
- **Linux**: Ubuntu 18.04+, Debian 10+, CentOS 7+, or equivalent
- **Windows**: Windows 10/11 (experimental support)

### Hardware Requirements
- **CPU**: Modern multi-core processor (Intel i5/AMD Ryzen 5 or better recommended)
- **RAM**: 4GB minimum, 8GB recommended (16GB for larger models)
- **Storage**: 5GB free space (more for additional models)
- **Microphone**: Built-in or USB microphone
- **Speakers/Headphones**: For audio output

### Software Requirements
- **Python**: 3.8 or higher
- **Ollama**: Latest version
- **Git**: For cloning the repository

## Step-by-Step Installation

### 1. Install Python

#### macOS
```bash
# Using Homebrew (recommended)
brew install python@3.11

# Or download from python.org
# https://www.python.org/downloads/macos/
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install python3.11 python3.11-pip python3.11-venv python3.11-dev
```

#### Linux (CentOS/RHEL)
```bash
sudo yum install python3.11 python3.11-pip python3.11-devel
```

### 2. Install Ollama

#### macOS
```bash
# Download and install from https://ollama.ai
# Or using Homebrew
brew install ollama
```

#### Linux
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

#### Windows
Download the installer from [https://ollama.ai](https://ollama.ai)

### 3. Install System Dependencies

#### macOS
```bash
# Install audio dependencies
brew install portaudio

# Install development tools if needed
xcode-select --install
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt install portaudio19-dev python3-pyaudio espeak espeak-data libespeak1 libespeak-dev
```

#### Linux (CentOS/RHEL)
```bash
sudo yum install portaudio-devel espeak espeak-devel
```

### 4. Clone the Repository

```bash
git clone https://github.com/your-username/jarvis-assistant.git
cd jarvis-assistant
```

### 5. Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv jarvis-env

# Activate virtual environment
# On macOS/Linux:
source jarvis-env/bin/activate

# On Windows:
# jarvis-env\Scripts\activate
```

### 6. Install Python Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install requirements
pip install -r requirements.txt
```

### 7. Configure Ollama

```bash
# Start Ollama service
ollama serve &

# Pull a model (choose based on your hardware)
# For low-end systems:
ollama pull qwen2.5:1.5b

# For mid-range systems:
ollama pull qwen2.5:7b

# For high-end systems:
ollama pull qwen2.5:14b

# Verify installation
ollama list
```

### 8. Configure Jarvis

```bash
# Copy configuration template
cp .env.example .env

# Edit configuration (optional)
nano .env  # or your preferred editor
```

### 9. Test Installation

```bash
# Run component tests
python tests/run_tests.py --unit

# Test microphone
python -c "
import speech_recognition as sr
print('Available microphones:')
for i, name in enumerate(sr.Microphone.list_microphone_names()):
    print(f'{i}: {name}')
"

# Test Ollama connection
python -c "
import ollama
try:
    response = ollama.chat(model='qwen2.5:1.5b', messages=[{'role': 'user', 'content': 'Hello'}])
    print('Ollama test successful!')
except Exception as e:
    print(f'Ollama test failed: {e}')
"
```

### 10. Run Jarvis

```bash
python -m jarvis.main
```

## Troubleshooting Installation Issues

### Python Installation Issues

**Issue**: `python3` command not found
```bash
# On macOS, try:
python3.11 -m venv jarvis-env

# Or add Python to PATH
export PATH="/usr/local/bin:$PATH"
```

**Issue**: Permission denied when installing packages
```bash
# Use virtual environment (recommended)
python3 -m venv jarvis-env
source jarvis-env/bin/activate
pip install -r requirements.txt

# Or install with --user flag
pip install --user -r requirements.txt
```

### Audio Dependencies Issues

**Issue**: PyAudio installation fails on macOS
```bash
# Install portaudio first
brew install portaudio

# Then install PyAudio
pip install pyaudio
```

**Issue**: PyAudio installation fails on Linux
```bash
# Install development headers
sudo apt install portaudio19-dev python3-dev

# Then install PyAudio
pip install pyaudio
```

### Ollama Issues

**Issue**: Ollama service not starting
```bash
# Check if Ollama is installed
which ollama

# Start Ollama manually
ollama serve

# Check Ollama status
curl http://localhost:11434/api/tags
```

**Issue**: Model download fails
```bash
# Check internet connection
ping ollama.ai

# Try downloading with verbose output
ollama pull qwen2.5:1.5b --verbose

# Check available disk space
df -h
```

### Microphone Issues

**Issue**: Microphone not detected
```bash
# List available microphones
python -c "
import speech_recognition as sr
mics = sr.Microphone.list_microphone_names()
for i, name in enumerate(mics):
    print(f'{i}: {name}')
"

# Test microphone access
python -c "
import speech_recognition as sr
r = sr.Recognizer()
with sr.Microphone() as source:
    print('Microphone test successful!')
"
```

**Issue**: Permission denied for microphone
- **macOS**: Go to System Preferences > Security & Privacy > Privacy > Microphone
- **Linux**: Check PulseAudio/ALSA configuration
- **Windows**: Check Windows privacy settings

### Memory Issues

**Issue**: Out of memory when running models
```bash
# Use a smaller model
ollama pull qwen2.5:1.5b

# Monitor memory usage
htop  # or top on macOS
```

**Issue**: Slow performance
```bash
# Check system resources
python -c "
import psutil
print(f'CPU cores: {psutil.cpu_count()}')
print(f'RAM: {psutil.virtual_memory().total / 1024**3:.1f}GB')
print(f'Available RAM: {psutil.virtual_memory().available / 1024**3:.1f}GB')
"
```

## Post-Installation Configuration

### Microphone Setup

1. **Find your microphone index:**
```bash
python -c "
import speech_recognition as sr
for i, name in enumerate(sr.Microphone.list_microphone_names()):
    print(f'{i}: {name}')
"
```

2. **Update configuration:**
```bash
# Edit .env file
JARVIS_MIC_INDEX=2  # Use the correct index
JARVIS_MIC_NAME="Your Microphone Name"
```

### Voice Selection

1. **List available voices:**
```bash
python -c "
import pyttsx3
engine = pyttsx3.init()
voices = engine.getProperty('voices')
for i, voice in enumerate(voices):
    print(f'{i}: {voice.name} ({voice.id})')
"
```

2. **Update configuration:**
```bash
# Edit .env file
JARVIS_TTS_VOICE="preferred_voice_name"
```

### Model Configuration

Jarvis uses **llama3.1:8b** as the default model for optimal tool calling, natural language, and code capabilities.

```bash
# Download the recommended model
ollama pull llama3.1:8b

# Verify the model is available
ollama list
```

**Why llama3.1:8b?**
- **Excellent function/tool calling capabilities** - Reliably calls tools instead of generating placeholder text
- **Strong natural language understanding** - Natural conversation flow
- **Good code generation and analysis** - Handles technical queries well
- **Balanced performance and resource usage** - Fast enough for real-time conversation
- **Proven reliability** - Extensively tested with Jarvis tool system

**Hardware Requirements for llama3.1:8b:**
- **Minimum**: 8GB RAM
- **Recommended**: 16GB RAM for optimal performance
- **Storage**: ~5GB for the model

## Verification

After installation, verify everything works:

```bash
# Run full test suite
python tests/run_tests.py --all

# Start Jarvis
python -m jarvis.main

# Test basic interaction:
# 1. Say your wake word ("Jarvis" by default)
# 2. Wait for acknowledgment
# 3. Ask "What time is it?"
# 4. Verify you get a response
```

## Next Steps

- Learn about [Tool Development](TOOL_DEVELOPMENT_GUIDE.md) to add custom functionality with MCP plugins
- Read the [Plugin Development Guide](plugin_development_guide.md) for creating plugins
- Check the [MCP System Overview](MCP_SYSTEM_OVERVIEW.md) to understand the plugin architecture
- Use `python manage_plugins.py --help` to explore the plugin system

## Plugin System

Jarvis now includes a powerful MCP (Model Context Protocol) plugin system:

```bash
# Generate a new tool plugin
python manage_plugins.py generate my_tool --type tool --author "Your Name"

# List available plugins
python manage_plugins.py list

# Load a plugin
python manage_plugins.py load MyTool
```

Plugins are automatically discovered and loaded, making it easy to extend Jarvis without modifying core code.

## Getting Help

If you encounter issues not covered here:

1. Check the [Troubleshooting Guide](troubleshooting.md)
2. Search [GitHub Issues](https://github.com/your-username/jarvis-assistant/issues)
3. Create a new issue with detailed information about your system and the problem
