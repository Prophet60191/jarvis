# Jarvis Voice Assistant

A 100% local, privacy-focused voice-activated AI assistant inspired by Tony Stark's Jarvis. Built with Python and powered by local AI models with zero external API calls. Features advanced speech recognition, natural conversation flow, complete offline operation, and a **modern web-based configuration interface**.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Privacy](https://img.shields.io/badge/privacy-100%25%20local-green.svg)](https://github.com/Prophet60191/jarvis)
[![Apple Silicon](https://img.shields.io/badge/Apple%20Silicon-optimized-blue.svg)](https://github.com/Prophet60191/jarvis)
[![Web UI](https://img.shields.io/badge/Web%20UI-included-brightgreen.svg)](https://github.com/Prophet60191/jarvis)

## Features

### 100% Local & Private
- **Zero External APIs**: No data sent to Google, OpenAI, or any external services
- **Complete Offline Operation**: Works without internet connection
- **Apple Silicon Optimized**: Native performance on M1/M2/M3 Macs
- **Privacy First**: All processing happens on your device

### Advanced Voice Interaction
- **Local Speech Recognition**: Powered by OpenAI Whisper (Faster-Whisper)
- **Apple System TTS**: High-quality native voice synthesis
- **Wake Word Detection**: Customizable wake word with confidence scoring
- **Auto-Listen Feature**: 5-second follow-up window for natural conversation
- **Voice Activity Detection**: Smart noise filtering and speech detection

### Local AI Integration
- **Local LLM**: Powered by Ollama with llama3.1:8b for optimal tool calling
- **Reliable Tool Calling**: Advanced function calling with real-time data retrieval
- **MCP Tool System**: Model Context Protocol for extensible tool architecture
- **LangChain Integration**: Seamless tool integration with automatic discovery
- **Context Awareness**: Maintains conversation context and history
- **Natural Conversation**: Seamless follow-up questions without repeating wake word

### Professional Architecture
- **Modular Design**: Clean separation of concerns with dependency injection
- **Configuration Management**: Environment-based configuration with validation
- **Error Handling**: Comprehensive exception hierarchy with detailed logging
- **Testing**: Full test suite with unit and integration tests
- **Documentation**: Comprehensive documentation and examples

### MCP Plugin System
- **Extensible Tool Architecture**: Add new tools without modifying core code
- **Automatic Discovery**: Plugins are found and loaded automatically
- **Template Generation**: Quick plugin creation with built-in templates
- **CLI Management**: Easy plugin management with `manage_plugins.py`

### Built-in Tools
- **Time Tool**: Get current time in 12-hour format (optimized for natural conversation)
- **Video Tool**: Video content creation advice with platform-specific tips
- **UI Control Tools**: Voice-activated web interface management
- **Plugin-Ready**: Add unlimited custom tools via the MCP system

### Modern Web Interface 🌐
- **Professional Web UI**: Modern dark-themed configuration interface
- **Real-time Configuration**: Change settings without restarting Jarvis
- **Sidebar Navigation**: Organized settings with intuitive navigation
- **Voice-Activated UI**: Open configuration pages with voice commands
- **Dynamic Updates**: All components respond to configuration changes instantly
- **Mobile Responsive**: Works on desktop, tablet, and mobile devices
- **Export/Import**: Backup and restore configuration settings

### Technology Stack
- **Speech Recognition**: Faster-Whisper (OpenAI Whisper optimized)
- **Text-to-Speech**: Apple System Voices (macOS native) with enhanced fallback
- **AI Model**: Ollama (llama3.1:8b - optimized for tool calling and natural language)
- **Audio Processing**: PyAudio, speech_recognition
- **Framework**: LangChain for tool integration with MCP plugin system
- **Web Interface**: Built-in HTTP server with modern UI
- **Platform**: Optimized for Apple Silicon (M1/M2/M3)

## Quick Start

### Prerequisites
- **Python 3.8+** (3.9+ recommended for Apple Silicon)
- **macOS** (optimized for Apple Silicon M1/M2/M3)
- **Microphone and speakers/headphones**
- **[Ollama](https://ollama.ai)** installed locally

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/Prophet60191/jarvis.git
cd jarvis
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
# Install Faster-Whisper for local speech recognition
pip install faster-whisper
```

3. **Install and configure Ollama:**
```bash
# Install Ollama (see https://ollama.ai for your platform)
# Pull the recommended model (optimized for tool calling)
ollama pull llama3.1:8b
```

4. **Configure Jarvis (optional):**
```bash
cp .env.example .env
# Edit .env with your preferred settings
```

5. **Run Jarvis:**
```bash
# Use the enhanced startup script (recommended)
python start_jarvis.py

# Or run directly
python -m jarvis.main
```

6. **Access the Configuration Interface (Optional):**

   **🖥️ Native Desktop App (Recommended):**
```bash
# Install desktop dependencies (one-time)
python install_desktop.py

# Launch native desktop application
python start_desktop.py              # Main dashboard
python start_desktop.py settings     # Settings panel
```

   **🌐 Web Interface (Browser-based):**
```bash
# Easy launcher
python start_ui.py                    # Main dashboard
python start_ui.py --panel settings  # Settings overview

# Or use platform-specific scripts
./start_ui.sh settings               # Unix/Linux/macOS
start_ui.bat settings               # Windows
```
   - **Desktop App**: Native window, no browser required
   - **Web Interface**: Opens http://localhost:8080 in your browser
   - Configure all Jarvis settings through the modern interface
   - Changes take effect immediately without restarting Jarvis

7. **Start talking:**
   - Say "Jarvis" clearly
   - Wait for the acknowledgment
   - Ask your question or give a command
   - **New**: Ask follow-up questions immediately (no need to say "Jarvis" again!)
   - **Voice UI Control**: Say "Jarvis, open settings" to launch the web interface
   - Press Ctrl+C to exit

## Usage Examples

### Natural Conversation Flow
```
You: "Jarvis"
Jarvis: "Yes sir?"
You: "What time is it?"
Jarvis: "I've checked the current time for you. It's currently 2:30 PM."
[Auto-listening for 5 seconds...]
You: "What about the weather?" (no need to say "Jarvis" again!)
Jarvis: "I don't have a weather tool available, but you can add one using the MCP plugin system."
```

### Video Content Advice
```
You: "Jarvis"
Jarvis: "Yes sir?"
You: "Give me video content advice for today"
Jarvis: "For Monday video content: Monday Motivation videos perform well..."
```

### Voice-Controlled Web Interface
```
You: "Jarvis"
Jarvis: "Yes sir?"
You: "Open settings"
Jarvis: "Opening Jarvis Settings Panel. The UI should appear on your screen shortly."
[Web browser opens to http://localhost:8080/settings]

You: "Open audio config"
Jarvis: "Opening Jarvis Audio Configuration. The UI should appear on your screen shortly."
[Web browser opens to http://localhost:8080/audio]
```

## Web Configuration Interface

Jarvis features a **modern, professional web interface** for complete configuration management:

### 🎨 **Modern Design**
- **Dark Theme**: Professional dark UI with glass-morphism effects
- **Sidebar Navigation**: Organized sections for easy access
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Real-time Updates**: Changes apply immediately without restart

### ⚙️ **Configuration Pages**
- **Dashboard** (`/`) - System overview and quick access
- **Settings Overview** (`/settings`) - Central configuration hub
- **Audio Configuration** (`/audio`) - Microphone, TTS, and Coqui settings
- **LLM Configuration** (`/llm`) - Language model parameters
- **Conversation Settings** (`/conversation`) - Wake word and flow settings
- **Logging Configuration** (`/logging`) - Log levels and output settings
- **Voice Profiles** (`/voice-profiles`) - Voice cloning management
- **Device Information** (`/device`) - Hardware and system details

### 🚀 **Quick Start Options**

#### 🖥️ **Native Desktop App (Recommended)**
```bash
# Install desktop app dependencies
python install_desktop.py

# Launch native desktop application
python start_desktop.py              # Main dashboard
python start_desktop.py settings     # Settings panel
python start_desktop.py audio        # Audio configuration

# Platform-specific launchers
./start_desktop.sh settings          # Unix/Linux/macOS
start_desktop.bat audio             # Windows
```

#### 🌐 **Web Interface (Browser-based)**
```bash
# Cross-platform Python launcher
python start_ui.py                    # Main dashboard
python start_ui.py --panel settings  # Settings overview
python start_ui.py --panel audio     # Audio configuration

# Unix/Linux/macOS shell script
./start_ui.sh                         # Main dashboard
./start_ui.sh settings               # Settings overview
./start_ui.sh audio                  # Audio configuration

# Windows batch file
start_ui.bat                         # Main dashboard
start_ui.bat settings               # Settings overview
start_ui.bat audio                  # Audio configuration
```

#### Direct Launch Commands
```bash
# Launch main dashboard
python ui/jarvis_ui.py --panel main --port 8080

# Launch specific configuration page
python ui/jarvis_ui.py --panel audio --port 8080
python ui/jarvis_ui.py --panel settings --port 8080

# Access via browser
open http://localhost:8080
```

## 🖥️ **Native Desktop Application**

Jarvis includes a **native desktop application** that provides a professional desktop experience without requiring a browser:

### **Features**
- **Native Window**: True desktop app with system integration
- **No Browser Required**: Embedded web view, no external browser needed
- **All UI Features**: Complete access to all Jarvis configuration panels
- **Cross-Platform**: Works on Windows, macOS, and Linux
- **Easy Installation**: One-command setup with automatic dependencies

### **Installation**
```bash
# Install desktop app dependencies
python install_desktop.py

# Or install manually
pip install pywebview
```

### **Usage**
```bash
# Launch desktop app
python start_desktop.py              # Main dashboard
python start_desktop.py settings     # Settings panel
python start_desktop.py audio        # Audio configuration
python start_desktop.py llm          # LLM settings

# Platform-specific shortcuts
./start_desktop.sh settings          # Unix/Linux/macOS
start_desktop.bat audio             # Windows
```

### 🎤 **Voice Commands for UI**
- **"Jarvis, open settings"** - Main configuration overview
- **"Jarvis, open audio config"** - Audio configuration page
- **"Jarvis, open LLM config"** - Language model settings
- **"Jarvis, open device info"** - Device information page
- **"Jarvis, close UI"** - Shutdown the web interface server

### 🔄 **Real-time Configuration**
- **Instant Updates**: All changes take effect immediately
- **No Restart Required**: Components update automatically
- **Live Validation**: Real-time error checking and feedback
- **Export/Import**: Backup and restore configurations

## MCP Plugin System

Jarvis features a revolutionary **Model Context Protocol (MCP)** system that allows unlimited extensibility without modifying core code:

### How It Works
1. **Automatic Discovery**: Plugins are automatically found in `jarvis/tools/plugins/`
2. **Template Generation**: Create new plugins instantly with built-in templates
3. **Zero Configuration**: Plugins are loaded automatically on startup
4. **CLI Management**: Manage plugins with simple command-line tools

### Quick Plugin Creation
```bash
# Generate a new plugin
python manage_plugins.py generate weather_tool --type tool --author "Your Name"

# List all plugins
python manage_plugins.py list --details

# Load a specific plugin
python manage_plugins.py load WeatherTool
```

### Plugin Example
```python
@tool
def weather_tool(city: str) -> str:
    """Get weather information for a city."""
    return f"Weather in {city}: Sunny, 72°F"

class WeatherPlugin(PluginBase):
    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="WeatherTool",
            version="1.0.0",
            description="Weather information tool",
            author="Your Name"
        )

    def get_tools(self):
        return [weather_tool]
```

### Benefits
- **Infinite Extensibility**: Add any functionality you can imagine
- **No Core Changes**: Main codebase remains untouched
- **Professional Architecture**: Following industry standards
- **Developer Friendly**: Templates, CLI tools, and comprehensive docs

## Privacy & Local Operation

Jarvis is designed with **privacy first** principles:

### What Stays Local
- **All voice data**: Speech recognition happens on your device using Whisper
- **All AI processing**: LLM runs locally via Ollama
- **All conversations**: No conversation data leaves your machine
- **All audio**: TTS uses Apple's system voices (local)

### What's NOT Sent Externally
- No audio sent to Google, OpenAI, or any cloud service
- No conversation logs uploaded anywhere
- No telemetry or analytics data collected
- No internet connection required after initial setup

### Security Benefits
- **Complete offline operation** after setup
- **No API keys required** for speech or AI
- **No data breaches possible** - everything stays on your device
- **Corporate/sensitive environment friendly**

## Configuration

Jarvis offers **two ways** to configure settings:

### 🌐 **Web Interface (Recommended)**
Use the modern web interface for easy configuration:
```bash
# Launch configuration interface
python ui/jarvis_ui.py --panel settings --port 8080
# Open http://localhost:8080 in your browser
```

**Benefits:**
- **Visual Interface**: Easy-to-use forms with validation
- **Real-time Updates**: Changes apply immediately
- **No File Editing**: Point-and-click configuration
- **Voice Control**: Open with "Jarvis, open settings"

### 📝 **Manual Configuration**
Alternatively, use environment variables by copying `.env.example` to `.env` and customizing:

### Speech Recognition Settings (Whisper)
```bash
JARVIS_WHISPER_MODEL_SIZE="base"      # Model: tiny, base, small, medium, large
JARVIS_WHISPER_DEVICE="cpu"           # Device: cpu (recommended for Apple Silicon)
JARVIS_WHISPER_LANGUAGE="en"          # Language: en, es, fr, etc. or "auto"
JARVIS_WHISPER_COMPUTE_TYPE="float32" # Precision: float32 (recommended)
```

### Audio Settings
```bash
JARVIS_MIC_INDEX=2                    # Microphone index
JARVIS_ENERGY_THRESHOLD=100           # Voice detection sensitivity
JARVIS_TTS_RATE=180                   # Speech rate (words per minute)
JARVIS_TTS_VOLUME=0.9                 # TTS volume (0.0-1.0)
JARVIS_TTS_VOICE="Daniel"             # Apple voice name
```

### Conversation Settings
```bash
JARVIS_WAKE_WORD="jarvis"             # Wake word
JARVIS_CONVERSATION_TIMEOUT=30        # Conversation timeout (seconds)
JARVIS_MAX_RETRIES=3                  # Max retry attempts
```

### AI Model Settings
```bash
JARVIS_MODEL="llama3.1:8b"            # Ollama model name (optimized for tool calling)
JARVIS_TEMPERATURE=0.7                # Response creativity (0.0-2.0)
JARVIS_VERBOSE=false                  # Verbose AI output
```

## Architecture

Jarvis follows a modular architecture with clear separation of concerns:

```
jarvis/
├── audio/           # Audio management (microphone, TTS, processing)
├── core/            # Core business logic (agent, speech, conversation)
├── plugins/         # MCP system (base, discovery, manager, generator, CLI)
├── tools/           # Tool system (base classes, registry, implementations)
│   └── plugins/     # Plugin storage directory
├── ui/              # Web-based configuration interface
│   └── jarvis_ui.py # Modern web UI server and interface
├── utils/           # Utilities (logging, decorators, helpers)
├── config.py        # Configuration management with dynamic reload
├── exceptions.py    # Custom exception hierarchy
├── main.py          # Application entry point
└── manage_plugins.py # Plugin management CLI
```

### Key Components

- **SpeechManager**: Coordinates speech recognition and TTS with dynamic configuration
- **JarvisAgent**: Manages LLM interaction and tool execution
- **ConversationManager**: Handles conversation flow and state
- **WakeWordDetector**: Detects wake words with confidence scoring
- **PluginManager**: MCP system for automatic tool discovery and loading
- **ToolRegistry**: Manages available tools and their execution
- **JarvisUI**: Modern web interface for configuration and monitoring
- **ConfigurationManager**: Dynamic configuration with real-time updates

## Development

### Running Tests
```bash
# Run all tests
python tests/run_tests.py

# Run with coverage
python tests/run_tests.py --coverage

# Run specific test types
python tests/run_tests.py --unit
python tests/run_tests.py --integration
```

### MCP Plugin System

Jarvis features a powerful Model Context Protocol (MCP) system for adding tools without modifying core code:

#### 1. Generate a Plugin Template
```bash
# Create a new tool plugin
python manage_plugins.py generate my_tool --type tool --author "Your Name"
```

#### 2. Implement Your Tool
```python
from langchain_core.tools import tool
from jarvis.plugins.base import PluginBase, PluginMetadata

@tool
def my_awesome_tool(query: str) -> str:
    """My custom tool implementation."""
    return f"Processed: {query}"

class MyToolPlugin(PluginBase):
    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="MyTool",
            version="1.0.0",
            description="My awesome tool",
            author="Your Name"
        )

    def get_tools(self):
        return [my_awesome_tool]

# Plugin discovery
PLUGIN_CLASS = MyToolPlugin
PLUGIN_METADATA = MyToolPlugin().get_metadata()
```

#### 3. Automatic Integration
```bash
# List discovered plugins
python manage_plugins.py list

# Load your plugin
python manage_plugins.py load MyTool

# Your tool is now available in Jarvis!
```

#### Key Benefits
- **Zero Core Changes**: Add tools without touching main codebase
- **Automatic Discovery**: Plugins are found and loaded automatically
- **Template Generation**: Quick start with built-in templates
- **CLI Management**: Easy plugin management and testing

### Web Interface Development

The Jarvis Web UI is built with modern web technologies and can be extended:

#### Starting the Web Interface
```bash
# Main dashboard
python ui/jarvis_ui.py --panel main --port 8080

# Specific configuration pages
python ui/jarvis_ui.py --panel settings --port 8080
python ui/jarvis_ui.py --panel audio --port 8080
python ui/jarvis_ui.py --panel llm --port 8080

# Custom port
python ui/jarvis_ui.py --panel main --port 3000
```

#### Available Panels
- `main` - Dashboard overview
- `settings` - Configuration overview
- `audio` - Audio and TTS settings
- `llm` - Language model configuration
- `conversation` - Conversation flow settings
- `logging` - Logging configuration
- `general` - General application settings
- `voice-profiles` - Voice cloning management
- `device` - Device and hardware information

#### API Endpoints
- `GET /api/config` - Retrieve current configuration
- `POST /api/config` - Update configuration settings
- `POST /api/config/reload` - Trigger configuration reload
- `GET /api/device-info` - Device and hardware information
- `GET /api/voice-profiles` - Voice profile management

#### Features
- **Real-time Configuration**: Changes apply immediately without restart
- **Voice Integration**: All pages accessible via voice commands
- **Mobile Responsive**: Works on all device sizes
- **Dark Theme**: Professional appearance with glass-morphism effects
- **Export/Import**: Configuration backup and restore

## Documentation

📚 **[Complete Documentation Index](docs/README.md)** - Start here for all documentation

### 🚀 **Quick Start**
- **[Installation Guide](docs/installation.md)** - Get Jarvis running
- **[Developer Quick Start](docs/DEVELOPER_QUICK_START.md)** - For developers
- **[Troubleshooting Guide](docs/TROUBLESHOOTING.md)** - Solve common issues

### 🏗️ **Architecture & Development**
- **[Architecture Overview](docs/ARCHITECTURE.md)** - System design and components
- **[API Documentation](docs/API_DOCUMENTATION.md)** - Complete API reference
- **[MCP System Overview](docs/MCP_SYSTEM_OVERVIEW.md)** - Plugin architecture

### 🛠️ **Tool Development**
- **[Tool Development Guide](docs/TOOL_DEVELOPMENT_GUIDE.md)** - Create custom tools
- **[Tool Quick Reference](docs/TOOL_QUICK_REFERENCE.md)** - Quick development reference
- **[Developer Critical Notes](docs/DEVELOPER_CRITICAL_NOTES.md)** - Must-read for developers

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## Requirements

### System Requirements
- **Operating System**: macOS, Linux (Windows support in development)
- **Python**: 3.8 or higher
- **Memory**: 4GB RAM minimum, 8GB recommended

### Hardware Requirements
- **Microphone**: Any USB or built-in microphone
- **Speakers/Headphones**: For audio output
- **Internet**: Required for initial setup and model downloads

## Troubleshooting

### Common Issues

**Microphone not detected:**
```bash
# List available microphones
python -c "import speech_recognition as sr; print(sr.Microphone.list_microphone_names())"
```

**Ollama connection issues:**
```bash
# Check if Ollama is running
ollama list
```

**Speech recognition not working:**
- Check microphone permissions
- Adjust `JARVIS_ENERGY_THRESHOLD` in configuration
- Test microphone with system settings

**Web UI not accessible:**
```bash
# Check if UI is running
curl http://localhost:8080/api/config

# Try different port
python ui/jarvis_ui.py --panel main --port 3000

# Check for port conflicts
lsof -i :8080
```

**Configuration changes not applying:**
- Use the "Reload Configuration" button in the web interface
- Check the browser console for JavaScript errors
- Verify .env file permissions and format

**Shutting down the Web UI:**
```bash
# Graceful shutdown via command line
python close_ui.py

# Force shutdown if needed
python close_ui.py --force

# Shutdown specific port
python close_ui.py --port 3000

# Via web interface - click "Shutdown UI" button in settings
# Via voice command - "Jarvis, close UI"
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Inspired by Tony Stark's Jarvis from the Marvel Cinematic Universe
- Built with [Ollama](https://ollama.ai) for local LLM inference
- Uses [LangChain](https://langchain.com) for AI tool integration
- Speech recognition powered by OpenAI Whisper (Faster-Whisper implementation)
- Text-to-speech using Apple's native system voices

"Sometimes you gotta run before you can walk." - Tony Stark