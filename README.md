# Jarvis Voice Assistant

A sophisticated AI-powered voice assistant with extensible tool integration, web-based control panel, and Model Context Protocol (MCP) support.

## 🚧 Current Status

**Latest Update**: July 28, 2025 - RAG Memory System & Plugin Architecture Complete

### ✅ Recently Completed
- **RAG Memory System**: ChromaDB-based dual memory with semantic search and persistent storage
- **Plugin Architecture**: Zero built-in tools - everything is plugin-based for maximum flexibility
- **Memory Migration**: Replaced 9 MCP memory tools with 2 simple RAG tools (remember_fact, search_long_term_memory)
- **Enhanced UX**: PII protection, contextual messages, and improved user guidance
- **Clean Architecture**: Dynamic tool loading with hot-swappable plugins

### ⚠️ Known Issues
- **Model Configuration**: Tool calling quality inconsistent due to model switching issues
- **Response Format**: Some tool responses return JSON instead of natural language
- **See**: [`jarvis/docs/MODEL_CONFIGURATION_ISSUE.md`](jarvis/docs/MODEL_CONFIGURATION_ISSUE.md) for detailed analysis

### 🎯 Next Steps
- Resolve model configuration system for consistent Qwen2.5-7B usage
- Improve tool response formatting for better user experience
- Expand MCP server integrations (GitHub, filesystem, web search)

## Features

### **Voice Interaction**
- **Speech-to-Text (STT)**: Real-time voice recognition using OpenAI Whisper
- **Text-to-Speech (TTS)**: Natural voice synthesis with multiple engine support
- **Voice Cloning**: Custom voice profiles for personalized responses
- **Dual Memory System**: Short-term chat context + persistent long-term fact storage

### **RAG Memory System** 🧠
- **Dual Memory Architecture**: Short-term chat context + long-term persistent facts
- **Semantic Search**: Find information by meaning, not just keywords
- **Natural Commands**: Simple "Remember that..." and "What do you remember..." interactions
- **PII Protection**: Automatic detection and warnings for sensitive information
- **ChromaDB Storage**: Production-ready vector database with data persistence

### **Plugin-Based Architecture**
- **Zero Built-in Tools**: Pure plugin system for maximum flexibility
- **Dynamic Tool Loading**: Add new capabilities without code changes
- **MCP Integration**: Model Context Protocol for external service integration
- **Plugin Tools**: Time, UI controls, memory management, and more
- **Custom Tools**: Easy plugin development framework

### **Web Control Panel**
- **Real-time Dashboard**: Monitor system status and performance
- **Settings Management**: Configure voice, audio, and system preferences
- **Tool Management**: Enable/disable plugins and manage MCP servers
- **Memory Management**: View and manage stored long-term memories
- **Live Conversation**: Web-based chat interface with voice controls

### **MCP Server Management**
- **Add/Remove Servers**: Manage external MCP tool providers
- **Server Templates**: Quick setup for popular services (GitHub, filesystem, etc.)
- **Connection Testing**: Verify server connectivity before deployment
- **Tool Discovery**: Automatic detection of available tools from connected servers

## Quick Start

### Prerequisites
- Python 3.8+
- macOS, Linux, or Windows
- Microphone and speakers for voice interaction

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Prophet60191/jarvis.git
   cd jarvis
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure API keys**
   - Copy `.env.example` to `.env`
   - Add your OpenAI API key and other service credentials

4. **Start Jarvis**
   ```bash
   python start_jarvis.py
   ```

5. **Access the web interface**
   - Open http://localhost:8080 in your browser
   - Use the control panel to configure settings and manage tools

## Usage

### Voice Commands

#### **Basic Interaction**
- **"Hey Jarvis"** - Wake word to start interaction
- **"What time is it?"** - Get current time
- **"Open the settings"** - Launch web control panel
- **"Stop listening"** - Pause voice recognition

#### **Memory System**
- **"Remember that I like iced coffee"** - Store facts in long-term memory
- **"Remember my birthday is March 15th"** - Store personal information
- **"What do you remember about my preferences?"** - Search stored memories
- **"Do you remember anything about my schedule?"** - Query specific topics

### Web Interface
- **Dashboard**: View system status and recent activity
- **Settings**: Configure voice profiles, audio settings, and preferences
- **Tools**: Manage available tools and MCP server connections
- **Performance**: Monitor system resources and response times

### MCP Server Integration
1. Navigate to the **MCP Tools & Servers** section
2. Click **"Add Server"** to configure new tool providers
3. Choose from templates or configure custom servers
4. Test connection and enable desired tools

## Development

### Project Structure
```
jarvis/
├── jarvis/                 # Core application
│   ├── core/              # Core functionality
│   ├── tools/             # Tool plugins
│   ├── ui/                # Web interface
│   └── utils/             # Utilities
├── docs/                  # Documentation
├── tools/                 # External tools
└── requirements.txt       # Dependencies
```

### Adding Custom Tools
1. Create a new tool plugin in `jarvis/tools/plugins/`
2. Inherit from `BaseTool` class
3. Implement required methods (`execute`, `get_schema`)
4. Register the tool in the plugin system

### MCP Tool Development
Follow the [MCP specification](https://modelcontextprotocol.io/) to create compatible tools that can be discovered and used by Jarvis.

## Configuration

### Environment Variables
```bash
# Required
OPENAI_API_KEY=your_openai_api_key

# Optional
ELEVENLABS_API_KEY=your_elevenlabs_key
WEATHER_API_KEY=your_weather_api_key
TTS_ENGINE=openai  # or elevenlabs, system
STT_ENGINE=openai  # or whisper_local
```

### Settings File
Configuration is managed through the web interface and stored in `jarvis/config/settings.json`.

## Troubleshooting

### Common Issues

**Voice not working?**
- Check microphone permissions
- Verify audio device settings in the web interface
- Test with `python -m speech_recognition` for basic functionality

**Web interface not loading?**
- Ensure port 8080 is available
- Check firewall settings
- Try accessing via `127.0.0.1:8080` instead of `localhost`

**MCP servers not connecting?**
- Verify server URLs and credentials
- Check network connectivity
- Review server logs in the web interface

### Debug Mode
Run with debug logging:
```bash
python start_jarvis.py --debug
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 style guidelines
- Add tests for new functionality
- Update documentation for API changes
- Ensure MCP compatibility for new tools

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- OpenAI for GPT and Whisper models
- Model Context Protocol community
- Contributors and beta testers

## Support

- **Issues**: [GitHub Issues](https://github.com/Prophet60191/jarvis/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Prophet60191/jarvis/discussions)
- **Documentation**: [Wiki](https://github.com/Prophet60191/jarvis/wiki)

---

**Made by the Jarvis community**
