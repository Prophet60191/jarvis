# Jarvis Voice Assistant

A sophisticated AI-powered voice assistant with extensible tool integration, web-based control panel, and Model Context Protocol (MCP) support.

## 🚧 Current Status

**Latest Update**: July 27, 2025 - MCP Memory Integration Complete

### ✅ Recently Completed
- **MCP Memory System**: Successfully integrated 9 memory tools (create_entities, add_observations, search_nodes, etc.)
- **Official MCP Adapters**: Implemented using `langchain-mcp-adapters` for proper tool conversion
- **Tool Discovery**: 17 total tools now available (8 built-in + 9 MCP memory tools)
- **Memory Storage**: Knowledge graph-based memory system for user preferences and context

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
- **Conversation Memory**: Maintains context across interactions

### **Extensible Tool System**
- **Dynamic Tool Loading**: Add new capabilities without code changes
- **MCP Integration**: Model Context Protocol for seamless tool discovery
- **Built-in Tools**: Time, weather, calculations, file operations, and more
- **Custom Tools**: Easy plugin development framework

### **Web Control Panel**
- **Real-time Dashboard**: Monitor system status and performance
- **Settings Management**: Configure voice, audio, and system preferences
- **Tool Management**: Enable/disable tools and manage MCP servers
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
- **"Hey Jarvis"** - Wake word to start interaction
- **"What time is it?"** - Get current time
- **"Tell me a joke"** - Entertainment commands
- **"Open the settings"** - Launch web control panel
- **"Stop listening"** - Pause voice recognition

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
