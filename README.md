# Jarvis Voice Assistant

A 100% local, privacy-focused voice-activated AI assistant inspired by Tony Stark's Jarvis. Built with Python and powered by local AI models with zero external API calls. Features advanced speech recognition, natural conversation flow, and complete offline operation.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Privacy](https://img.shields.io/badge/privacy-100%25%20local-green.svg)](https://github.com/Prophet60191/jarvis)
[![Apple Silicon](https://img.shields.io/badge/Apple%20Silicon-optimized-blue.svg)](https://github.com/Prophet60191/jarvis)

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
- **Local LLM**: Powered by Ollama for complete privacy and offline operation
- **Tool Integration**: Extensible tool system with LangChain compatibility
- **Reasoning**: Optional reasoning mode for complex queries
- **Context Awareness**: Maintains conversation context and history
- **Natural Conversation**: Seamless follow-up questions without repeating wake word

### Professional Architecture
- **Modular Design**: Clean separation of concerns with dependency injection
- **Configuration Management**: Environment-based configuration with validation
- **Error Handling**: Comprehensive exception hierarchy with detailed logging
- **Testing**: Full test suite with unit and integration tests
- **Documentation**: Comprehensive documentation and examples

### Built-in Tools
- **Time Tool**: Get current time in 80+ cities worldwide with timezone support
- **Video Tool**: Video content creation advice with platform-specific tips
- **Extensible**: Easy to add custom tools with the provided base classes

### Technology Stack
- **Speech Recognition**: Faster-Whisper (OpenAI Whisper optimized)
- **Text-to-Speech**: Apple System Voices (macOS native)
- **AI Model**: Ollama (qwen2.5:1.5b or any compatible model)
- **Audio Processing**: PyAudio, speech_recognition
- **Framework**: LangChain for tool integration
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
# Pull a compatible model
ollama pull qwen2.5:1.5b
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

6. **Start talking:**
   - Say "Jarvis" clearly
   - Wait for the acknowledgment
   - Ask your question or give a command
   - **New**: Ask follow-up questions immediately (no need to say "Jarvis" again!)
   - Press Ctrl+C to exit

## Usage Examples

### Natural Conversation Flow
```
You: "Jarvis"
Jarvis: "Yes sir?"
You: "What time is it in New York?"
Jarvis: "The current time in New York is 2:30 PM on Monday, January 15, 2024"
[Auto-listening for 5 seconds...]
You: "What about in Tokyo?" (no need to say "Jarvis" again!)
Jarvis: "In Tokyo, it's currently 4:30 AM on Tuesday, January 16, 2024"
```

### Video Content Advice
```
You: "Jarvis"
Jarvis: "Yes sir?"
You: "Give me video content advice for today"
Jarvis: "For Monday video content: Monday Motivation videos perform well..."
```

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

Jarvis uses environment variables for configuration. Copy `.env.example` to `.env` and customize:

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
JARVIS_MODEL="qwen2.5:1.5b"           # Ollama model name
JARVIS_TEMPERATURE=0.7                # Response creativity (0.0-2.0)
JARVIS_VERBOSE=false                  # Verbose AI output
```

## Architecture

Jarvis follows a modular architecture with clear separation of concerns:

```
jarvis/
├── audio/           # Audio management (microphone, TTS, processing)
├── core/            # Core business logic (agent, speech, conversation)
├── tools/           # Tool system (base classes, registry, implementations)
├── utils/           # Utilities (logging, decorators, helpers)
├── config.py        # Configuration management
├── exceptions.py    # Custom exception hierarchy
└── main.py          # Application entry point
```

### Key Components

- **SpeechManager**: Coordinates speech recognition and TTS
- **JarvisAgent**: Manages LLM interaction and tool execution
- **ConversationManager**: Handles conversation flow and state
- **WakeWordDetector**: Detects wake words with confidence scoring
- **ToolRegistry**: Manages available tools and their execution

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

### Adding Custom Tools

1. **Create a tool class:**
```python
from jarvis.tools.base import BaseTool, ToolResult, create_success_result

class MyTool(BaseTool):
    def __init__(self):
        super().__init__("my_tool", "Description of my tool")
    
    def execute(self, **kwargs):
        result = "Tool result"
        return create_success_result(result)
    
    def get_parameters(self):
        return {
            "param1": {
                "type": "string",
                "description": "Parameter description",
                "required": False
            }
        }
```

2. **Register the tool:**
```python
from jarvis.tools import tool_registry
tool_registry.register(MyTool())
```

## Documentation

- [Installation Guide](docs/installation.md)
- [Configuration Reference](docs/configuration.md)
- [Architecture Overview](docs/architecture.md)
- [API Documentation](docs/api.md)
- [Tool Development Guide](docs/tools.md)
- [Troubleshooting](docs/troubleshooting.md)

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

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Inspired by Tony Stark's Jarvis from the Marvel Cinematic Universe
- Built with [Ollama](https://ollama.ai) for local LLM inference
- Uses [LangChain](https://langchain.com) for AI tool integration
- Speech recognition powered by OpenAI Whisper (Faster-Whisper implementation)
- Text-to-speech using Apple's native system voices

"Sometimes you gotta run before you can walk." - Tony Stark