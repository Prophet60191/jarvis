# Frequently Asked Questions (FAQ)

## 🤔 General Questions

### What is Jarvis Voice Assistant?

Jarvis is a sophisticated AI-powered voice assistant with a plugin-based architecture. It features:
- Voice interaction with speech-to-text and text-to-speech
- Extensible tool system with zero built-in tools
- RAG memory system for persistent information storage
- Desktop applications for configuration and document management
- Model Context Protocol (MCP) support for external integrations

### What makes Jarvis different from other voice assistants?

- **Plugin-First Architecture**: Everything is a plugin, no hard-coded functionality
- **Dual Memory System**: Short-term chat context + persistent long-term memory
- **Privacy-Focused**: All data stays on your local machine
- **Developer-Friendly**: Easy to extend with custom tools and integrations
- **Open Source**: Full control over your voice assistant

### What are the system requirements?

**Minimum**:
- Python 3.8+
- 4GB RAM
- 5GB storage
- Microphone and speakers

**Recommended**:
- Python 3.11+
- 8GB+ RAM (16GB for optimal performance)
- 10GB+ storage
- Quality USB microphone

## 🛠️ Installation & Setup

### How do I install Jarvis?

1. Clone the repository: `git clone https://github.com/Prophet60191/jarvis.git`
2. Install dependencies: `pip install -r requirements.txt`
3. Install Ollama and pull the recommended model: `ollama pull llama3.1:8b`
4. Start Jarvis: `python start_jarvis.py`

See the [Installation Guide](installation.md) for detailed instructions.

### Which AI model should I use?

**Recommended**: `llama3.1:8b`
- Excellent tool calling capabilities
- Good balance of performance and resource usage
- Reliable for voice assistant tasks

**Alternatives**:
- `qwen2.5:1.5b` - For low-end systems (4GB RAM)
- `qwen2.5:14b` - For high-end systems (16GB+ RAM)

### Do I need API keys?

No! Jarvis works completely offline with local models via Ollama. Optional API keys:
- **OpenAI**: For cloud-based speech recognition (alternative to local Whisper)
- **ElevenLabs**: For premium text-to-speech voices

## 🎤 Voice Commands

### What's the wake word?

The default wake word is **"Jarvis"**. You can customize it in the configuration.

### What voice commands are available?

**Basic Commands**:
- "What time is it?"
- "Open settings" / "Close settings"
- "Open vault" / "Close vault"

**Memory Commands**:
- "Remember that I like coffee"
- "What do you remember about my preferences?"

**Profile Commands**:
- "My name is John"
- "What's my name?"
- "Show my profile"

See the [User Guide](#) for a complete list.

### Why isn't Jarvis responding to my voice?

Common causes:
1. **Microphone issues**: Check permissions and device selection
2. **Wake word not detected**: Speak clearly and close to microphone
3. **Background noise**: Reduce ambient noise
4. **Model issues**: Ensure `llama3.1:8b` is installed and running

See [Troubleshooting Guide](TROUBLESHOOTING.md) for detailed solutions.

## 🧠 Memory System

### How does the memory system work?

Jarvis has a **dual memory system**:

1. **Short-term memory**: Current conversation context (clears between sessions)
2. **Long-term memory**: Persistent facts stored in ChromaDB vector database

### How do I store information?

Use natural language with "remember" commands:
- "Remember that I like iced coffee"
- "Remember my birthday is March 15th"
- "Store this fact: I work from home on Fridays"

### How do I retrieve stored information?

Ask Jarvis to recall information:
- "What do you remember about my preferences?"
- "Do you remember my birthday?"
- "What have I told you about my schedule?"

### Is my data private?

Yes! All data is stored locally on your machine:
- **No cloud storage**: Everything stays on your computer
- **No data transmission**: Information never leaves your device
- **User control**: You can view, edit, or delete stored information anytime

## 🔧 Tools & Plugins

### How do I add new tools?

1. **Generate a plugin template**:
   ```bash
   python manage_plugins.py generate my_tool --type tool --author "Your Name"
   ```

2. **Edit the generated file** in `jarvis/jarvis/tools/plugins/`

3. **Restart Jarvis** to load the new tool

See [Tool Development Guide](TOOL_DEVELOPMENT_GUIDE.md) for details.

### What tools are included?

**Core Tools**:
- Time and date functions
- Memory management (remember/recall)
- User profile management
- Desktop application control
- RAG document management

**Available Integrations**:
- Open Interpreter for code execution
- Robot Framework for testing
- Web automation tools
- Custom MCP servers

### Can I disable tools I don't need?

Yes! Use the plugin management system:
```bash
# List available plugins
python manage_plugins.py list

# Disable a plugin
python manage_plugins.py disable PluginName

# Re-enable a plugin
python manage_plugins.py enable PluginName
```

## 🖥️ Desktop Applications

### What desktop applications are included?

1. **Knowledge Vault**: Document management and RAG system control
2. **Settings Panel**: Jarvis configuration and preferences

### How do I open desktop applications?

**Voice Commands**:
- "Open vault" / "Close vault"
- "Open settings" / "Close settings"

**Command Line**:
```bash
python rag_app.py          # Knowledge vault
python jarvis_settings_app.py  # Settings panel
```

### Desktop apps won't open. What should I do?

1. **Install desktop dependencies**:
   ```bash
   python install_desktop.py
   ```

2. **Check for port conflicts**:
   ```bash
   lsof -i :8080
   lsof -i :8081
   ```

3. **Try manual launch** to see error messages

## 🔊 Audio & Voice

### How do I change the voice?

Jarvis uses Coqui TTS with multiple voice options:

1. **Open settings**: "Open settings" or `python jarvis_settings_app.py`
2. **Navigate to Audio section**
3. **Select preferred voice** from the dropdown
4. **Test the voice** with the preview button

### Can I use my own voice?

Yes! Jarvis supports voice cloning:

1. **Record voice samples** (10-30 seconds of clear speech)
2. **Upload samples** through the settings interface
3. **Train voice model** (takes a few minutes)
4. **Select your custom voice** from the voice list

### Audio quality is poor. How can I improve it?

1. **Use a quality microphone**: USB microphones work better than built-in ones
2. **Reduce background noise**: Find a quiet environment
3. **Adjust microphone gain**: Use system audio settings
4. **Check sample rate**: Ensure microphone supports 16kHz or higher

## 🔒 Privacy & Security

### What data does Jarvis collect?

Jarvis is privacy-first:
- **No telemetry**: No usage data is collected or transmitted
- **Local processing**: All AI processing happens on your machine
- **User-controlled storage**: You decide what information to store
- **No cloud dependencies**: Works completely offline

### Can I see what information is stored?

Yes! You have full transparency:
- **Voice command**: "Show my profile" or "What do you remember about me?"
- **Settings interface**: View stored memories in the vault application
- **File access**: Data is stored in readable JSON format in `~/.jarvis/`

### How do I delete stored information?

**Complete reset**:
- Voice: "Clear my profile"
- Command: `rm -rf ~/.jarvis/`

**Selective deletion**:
- Use the vault application to manage specific memories
- Edit JSON files directly in `~/.jarvis/`

## 🚀 Performance

### Jarvis is running slowly. How can I speed it up?

1. **Use appropriate model**: `qwen2.5:1.5b` for lower-end systems
2. **Close unnecessary applications**: Free up RAM and CPU
3. **Check system resources**: Monitor with `htop` or Activity Monitor
4. **Optimize Ollama**: Ensure it has sufficient resources allocated

### How much resources does Jarvis use?

**Typical usage**:
- **RAM**: 2-4GB (depends on AI model)
- **CPU**: Low when idle, moderate during processing
- **Storage**: ~1GB for application, ~5GB for AI model
- **Network**: None (fully offline)

## 🆘 Support

### Where can I get help?

1. **Documentation**: Check all guides in the `docs/` directory
2. **Troubleshooting**: See [Troubleshooting Guide](TROUBLESHOOTING.md)
3. **GitHub Issues**: [Report bugs or request features](https://github.com/Prophet60191/jarvis/issues)
4. **GitHub Discussions**: [Ask questions and share ideas](https://github.com/Prophet60191/jarvis/discussions)

### How do I report a bug?

1. **Check existing issues** on GitHub
2. **Gather system information**:
   ```bash
   python -c "import platform, sys; print(f'OS: {platform.system()} {platform.release()}'); print(f'Python: {sys.version}')"
   ```
3. **Include error logs** from `jarvis/logs/jarvis.log`
4. **Describe steps to reproduce** the issue
5. **Create a new issue** with all the information

### How can I contribute?

- **Report bugs**: Help identify and fix issues
- **Suggest features**: Share ideas for improvements
- **Write documentation**: Help improve guides and tutorials
- **Develop tools**: Create plugins and integrations
- **Test changes**: Help validate new features

See [Contributing Guide](../CONTRIBUTING.md) for details.

---

**Still have questions?** Check the [GitHub Discussions](https://github.com/Prophet60191/jarvis/discussions) or create a new issue!
