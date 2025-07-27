# 📚 Jarvis API Documentation

Complete API reference for Jarvis Voice Assistant developers.

## 📋 Table of Contents

- [Core APIs](#core-apis)
- [Configuration API](#configuration-api)
- [Plugin System API](#plugin-system-api)
- [Web Interface API](#web-interface-api)
- [Tool Development API](#tool-development-api)
- [Audio System API](#audio-system-api)

## 🔧 Core APIs

### JarvisAgent

Main AI agent for processing user input and managing tool execution.

```python
from jarvis.core.agent import JarvisAgent
from jarvis.config import get_config

# Initialize
config = get_config()
agent = JarvisAgent(config.llm)
agent.initialize(tools=tools)

# Process input
response = agent.process_input("What time is it?")
```

#### Methods

**`__init__(config: LLMConfig)`**
- Initialize the agent with LLM configuration
- **Parameters**: `config` - LLM configuration object
- **Returns**: JarvisAgent instance

**`initialize(tools: Optional[List[BaseTool]] = None) -> None`**
- Initialize the LLM and agent with tools
- **Parameters**: `tools` - List of LangChain tools to make available
- **Raises**: `ModelLoadError`, `LLMError`

**`process_input(user_input: str) -> str`**
- Process user input and generate response
- **Parameters**: `user_input` - User's text input
- **Returns**: Agent's response as string
- **Raises**: `ModelInferenceError`, `ToolError`

**`add_tools(tools: List[BaseTool]) -> None`**
- Add tools to the agent dynamically
- **Parameters**: `tools` - List of tools to add

**`get_available_tools() -> List[str]`**
- Get list of available tool names
- **Returns**: List of tool names

### SpeechManager

Handles speech recognition and text-to-speech operations.

```python
from jarvis.core.speech import SpeechManager

# Initialize
speech = SpeechManager(config.audio)
speech.initialize()

# Use
text = speech.listen()
speech.speak("Hello!")
```

#### Methods

**`listen(timeout: Optional[float] = None) -> Optional[str]`**
- Listen for speech input
- **Parameters**: `timeout` - Maximum time to wait for speech
- **Returns**: Recognized text or None

**`speak(text: str, wait: bool = False) -> None`**
- Convert text to speech
- **Parameters**: 
  - `text` - Text to speak
  - `wait` - Whether to wait for speech completion

**`is_listening() -> bool`**
- Check if currently listening for input
- **Returns**: True if listening, False otherwise

## ⚙️ Configuration API

### Configuration Management

```python
from jarvis.config import get_config

# Get current configuration
config = get_config()

# Access configuration sections
audio_config = config.audio
llm_config = config.llm
conversation_config = config.conversation
```

### Configuration Classes

#### `LLMConfig`
```python
@dataclass
class LLMConfig:
    model: str = "llama3.1:8b"           # Ollama model name
    verbose: bool = False                # Verbose output
    reasoning: bool = False              # Enable reasoning mode
    temperature: float = 0.7             # Response creativity (0.0-2.0)
    max_tokens: Optional[int] = None     # Maximum tokens per response
```

#### `AudioConfig`
```python
@dataclass
class AudioConfig:
    # Microphone settings
    mic_index: Optional[int] = None      # Microphone index
    mic_name: Optional[str] = None       # Microphone name
    energy_threshold: int = 100          # Voice detection sensitivity
    
    # TTS settings
    tts_backend: str = "apple"           # TTS backend (apple, coqui)
    tts_rate: int = 190                  # Speech rate (WPM)
    tts_volume: float = 0.9              # Volume (0.0-1.0)
    tts_voice_preference: str = "Daniel" # Preferred voice
    
    # Fallback settings
    tts_fallback_enabled: bool = True    # Enable enhanced fallback
    tts_fallback_voices: List[str] = field(default_factory=lambda: [
        "daniel", "alex", "samantha", "victoria", "karen"
    ])
    tts_fallback_rate_cap: int = 200     # Maximum fallback rate
```

#### `ConversationConfig`
```python
@dataclass
class ConversationConfig:
    wake_word: str = "jarvis"            # Wake word
    conversation_timeout: int = 30       # Timeout in seconds
    max_retries: int = 3                 # Maximum retry attempts
    enable_full_duplex: bool = False     # Full-duplex mode
```

### Environment Variables

All configuration can be overridden with environment variables:

```bash
# LLM Configuration
JARVIS_MODEL="llama3.1:8b"
JARVIS_TEMPERATURE=0.7
JARVIS_VERBOSE=false

# Audio Configuration  
JARVIS_MIC_INDEX=0
JARVIS_TTS_RATE=190
JARVIS_TTS_VOLUME=0.9
JARVIS_TTS_VOICE="Daniel"
JARVIS_TTS_FALLBACK_ENABLED=true
JARVIS_TTS_FALLBACK_VOICES="daniel,alex,samantha"
JARVIS_TTS_FALLBACK_RATE_CAP=200

# Conversation Configuration
JARVIS_WAKE_WORD="jarvis"
JARVIS_CONVERSATION_TIMEOUT=30
```

## 🔌 Plugin System API

### PluginManager

Manages plugin discovery, loading, and tool registration.

```python
from jarvis.plugins.manager import PluginManager

# Initialize with auto-discovery
manager = PluginManager(auto_discover=True)

# Get plugins and tools
plugins = manager.get_loaded_plugin_names()
tools = manager.get_all_tools()
```

#### Methods

**`get_loaded_plugin_names() -> List[str]`**
- Get names of all loaded plugins
- **Returns**: List of plugin names

**`get_plugin(name: str) -> Optional[PluginBase]`**
- Get a specific plugin by name
- **Parameters**: `name` - Plugin name
- **Returns**: Plugin instance or None

**`get_all_tools() -> List[BaseTool]`**
- Get all tools from all loaded plugins
- **Returns**: List of LangChain tools

### Plugin Base Class

```python
from jarvis.plugins.base import PluginBase, PluginMetadata

class MyPlugin(PluginBase):
    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="MyPlugin",
            version="1.0.0",
            description="My custom plugin",
            author="Developer Name"
        )
    
    def get_tools(self) -> List[BaseTool]:
        return [my_tool_function]
```

### Tool Registry

```python
from jarvis.tools import get_langchain_tools, tool_registry

# Get all available tools (built-in + plugins)
all_tools = get_langchain_tools()

# Get only built-in tools
builtin_tools = tool_registry.get_langchain_tools()
```

## 🌐 Web Interface API

### HTTP Endpoints

#### Configuration Endpoints

**`GET /api/config`**
- Retrieve current configuration
- **Returns**: JSON configuration object

**`POST /api/config`**
- Update configuration settings
- **Body**: JSON with configuration updates
- **Returns**: Success/error status

**`POST /api/config/reload`**
- Trigger configuration reload
- **Returns**: Success/error status

#### Device Information

**`GET /api/device-info`**
- Get device and system information
- **Returns**: JSON with device details

#### Voice Profiles

**`GET /api/voice-profiles`**
- Get available voice profiles
- **Returns**: JSON array of voice profiles

### Web UI Integration

```python
from ui.jarvis_ui import JarvisUI

# Start web interface
ui = JarvisUI(port=8080, panel="main")
ui.run()
```

## 🛠️ Tool Development API

### Creating Tools

```python
from langchain_core.tools import tool

@tool
def my_custom_tool(query: str) -> str:
    """
    Description of what the tool does.
    
    Args:
        query: Input parameter description
        
    Returns:
        str: Description of return value
    """
    try:
        # Tool implementation
        result = f"Processed: {query}"
        return result
    except Exception as e:
        return f"Error: {str(e)}"
```

### Tool Best Practices

1. **Descriptive Names**: Use specific function names
2. **Clear Docstrings**: LLM uses these for understanding
3. **Type Hints**: Always include parameter and return types
4. **Error Handling**: Handle exceptions gracefully
5. **Logging**: Use appropriate logging levels

### Plugin Template Generation

```bash
# Generate new plugin
python manage_plugins.py generate my_tool --type tool --author "Your Name"

# List plugins
python manage_plugins.py list --details

# Load specific plugin
python manage_plugins.py load MyTool
```

## 🎵 Audio System API

### TTS Manager

```python
from jarvis.audio.tts import TextToSpeechManager

# Initialize
tts = TextToSpeechManager(config.audio)
tts.initialize()

# Speak text
tts.speak("Hello, world!", wait=True)
```

### Wake Word Detection

```python
from jarvis.audio.wake_word import WakeWordDetector

# Initialize
detector = WakeWordDetector(config.conversation)

# Check for wake word
is_detected = detector.detect(audio_data)
```

## 🔍 Error Handling

### Exception Hierarchy

```python
from jarvis.exceptions import (
    JarvisError,           # Base exception
    ConfigurationError,    # Configuration issues
    ModelLoadError,        # Model loading failures
    ModelInferenceError,   # Model inference failures
    ToolError,            # Tool execution errors
    AudioError,           # Audio system errors
    LLMError              # LLM-related errors
)
```

### Error Handling Example

```python
try:
    response = agent.process_input("What time is it?")
except ModelInferenceError as e:
    logger.error(f"Model inference failed: {e}")
    # Handle model error
except ToolError as e:
    logger.error(f"Tool execution failed: {e}")
    # Handle tool error
except JarvisError as e:
    logger.error(f"Jarvis error: {e}")
    # Handle general Jarvis error
```

## 📝 Logging

### Logger Configuration

```python
import logging

# Get Jarvis logger
logger = logging.getLogger("jarvis.my_component")

# Log levels
logger.debug("Debug information")
logger.info("General information")
logger.warning("Warning message")
logger.error("Error occurred")
logger.critical("Critical error")
```

### Log Configuration

```bash
# Environment variables
JARVIS_LOG_LEVEL="DEBUG"     # DEBUG, INFO, WARNING, ERROR, CRITICAL
JARVIS_LOG_FILE=""           # Optional log file path
```

---

For more detailed examples and advanced usage, see the [Developer Quick Start Guide](DEVELOPER_QUICK_START.md) and [Tool Development Guide](TOOL_DEVELOPMENT_GUIDE.md).
