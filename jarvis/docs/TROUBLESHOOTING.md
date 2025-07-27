# 🔧 Troubleshooting Guide

Comprehensive troubleshooting guide for Jarvis Voice Assistant.

## 📋 Quick Diagnostics

### Run Built-in Diagnostics
```bash
# Comprehensive system check
python verify_installation.py

# Test specific components
python -c "
from jarvis.config import get_config
from jarvis.core.agent import JarvisAgent
from jarvis.tools import get_langchain_tools

config = get_config()
print(f'Model: {config.llm.model}')

agent = JarvisAgent(config.llm)
tools = get_langchain_tools()
print(f'Available tools: {[tool.name for tool in tools]}')

agent.initialize(tools=tools)
response = agent.process_input('What time is it?')
print(f'Tool calling test: {response}')
"
```

## 🚨 Common Issues

### 1. Tool Calling Issues

#### **Problem**: LLM returns placeholder text like `[Current Time]`
```
Jarvis: "The current time is [Current Time]"
```

**Root Cause**: Wrong model or model not supporting function calling

**Solution**:
```bash
# Check current model
python -c "from jarvis.config import get_config; print(get_config().llm.model)"

# Should show: llama3.1:8b
# If not, update .env file:
echo 'JARVIS_MODEL="llama3.1:8b"' >> .env

# Ensure model is installed
ollama pull llama3.1:8b
ollama list | grep llama3.1
```

#### **Problem**: Tools not being discovered
```
Available tools: []
```

**Solution**:
```bash
# Check plugin discovery
python manage_plugins.py list

# Verify tool loading
python -c "
from jarvis.tools import get_langchain_tools
tools = get_langchain_tools()
print([tool.name for tool in tools])
"

# Should show: ['get_current_time', 'video_day', 'open_jarvis_ui', ...]
```

### 2. Audio Issues

#### **Problem**: Microphone not detected
```bash
# List available microphones
python -c "
import speech_recognition as sr
mics = sr.Microphone.list_microphone_names()
for i, name in enumerate(mics):
    print(f'{i}: {name}')
"

# Set correct microphone in .env
echo 'JARVIS_MIC_INDEX=2' >> .env
echo 'JARVIS_MIC_NAME="MacBook Pro Microphone"' >> .env
```

#### **Problem**: Speech recognition not working
```bash
# Test microphone permissions
python -c "
import speech_recognition as sr
r = sr.Recognizer()
with sr.Microphone() as source:
    print('Say something...')
    audio = r.listen(source, timeout=5)
    try:
        text = r.recognize_whisper(audio)
        print(f'Recognized: {text}')
    except Exception as e:
        print(f'Error: {e}')
"
```

**Solutions**:
- Check microphone permissions in System Preferences
- Adjust energy threshold: `JARVIS_ENERGY_THRESHOLD=300`
- Test with different microphone

#### **Problem**: TTS not working
```bash
# Test TTS directly
python -c "
from jarvis.config import get_config
from jarvis.audio.tts import TextToSpeechManager

config = get_config()
tts = TextToSpeechManager(config.audio)
tts.initialize()
tts.speak('Hello, this is a test', wait=True)
"
```

### 3. Ollama Connection Issues

#### **Problem**: Ollama not responding
```bash
# Check if Ollama is running
ollama list

# If not running, start it
ollama serve

# Test model
ollama run llama3.1:8b "Hello"
```

#### **Problem**: Model not found
```bash
# Pull the correct model
ollama pull llama3.1:8b

# Verify it's available
ollama list | grep llama3.1
```

### 4. Web UI Issues

#### **Problem**: Web UI not accessible
```bash
# Check if UI is running
curl http://localhost:8080/api/config

# Start UI manually
python start_ui.py --panel main --port 8080

# Try different port
python start_ui.py --panel main --port 3000
```

#### **Problem**: Configuration changes not applying
```bash
# Force configuration reload
curl -X POST http://localhost:8080/api/config/reload

# Check .env file permissions
ls -la .env

# Verify configuration
python -c "from jarvis.config import get_config; print(get_config())"
```

### 5. Plugin Issues

#### **Problem**: Plugin not loading
```bash
# Check plugin location
ls -la jarvis/tools/plugins/

# Verify plugin structure
python manage_plugins.py list --details

# Test plugin directly
python -c "
from jarvis.tools.plugins.device_time_tool import get_current_time
result = get_current_time.invoke({})
print(result)
"
```

## 🔍 Debugging Steps

### 1. Enable Debug Logging
```bash
# Add to .env file
echo 'JARVIS_LOG_LEVEL="DEBUG"' >> .env
echo 'JARVIS_VERBOSE=true' >> .env
echo 'JARVIS_DEBUG=true' >> .env

# Run with debug output
python start_jarvis.py
```

### 2. Component-by-Component Testing

#### Test Configuration
```python
from jarvis.config import get_config
config = get_config()
print(f"LLM Model: {config.llm.model}")
print(f"Audio Backend: {config.audio.tts_backend}")
print(f"Wake Word: {config.conversation.wake_word}")
```

#### Test LLM Connection
```python
from jarvis.core.agent import JarvisAgent
from jarvis.config import get_config

config = get_config()
agent = JarvisAgent(config.llm)
agent.initialize()

# Test basic response
response = agent.llm.invoke("Hello")
print(f"LLM Response: {response}")
```

#### Test Tool System
```python
from jarvis.tools import get_langchain_tools
from jarvis.plugins.manager import PluginManager

# Check plugin discovery
manager = PluginManager(auto_discover=True)
plugins = manager.get_loaded_plugin_names()
print(f"Loaded plugins: {plugins}")

# Check tools
tools = get_langchain_tools()
print(f"Available tools: {[tool.name for tool in tools]}")
```

### 3. Performance Diagnostics

#### Check System Resources
```bash
# Memory usage
python -c "
import psutil
print(f'RAM: {psutil.virtual_memory().percent}%')
print(f'CPU: {psutil.cpu_percent()}%')
"

# Disk space
df -h
```

#### Profile Jarvis Performance
```python
import time
from jarvis.config import get_config
from jarvis.core.agent import JarvisAgent
from jarvis.tools import get_langchain_tools

# Time initialization
start = time.time()
config = get_config()
agent = JarvisAgent(config.llm)
tools = get_langchain_tools()
agent.initialize(tools=tools)
init_time = time.time() - start
print(f"Initialization time: {init_time:.2f}s")

# Time response generation
start = time.time()
response = agent.process_input("What time is it?")
response_time = time.time() - start
print(f"Response time: {response_time:.2f}s")
print(f"Response: {response}")
```

## 🛠️ Advanced Troubleshooting

### Reset Configuration
```bash
# Backup current config
cp .env .env.backup

# Reset to defaults
cp .env.example .env

# Update with minimal settings
cat >> .env << EOF
JARVIS_MODEL="llama3.1:8b"
JARVIS_LOG_LEVEL="DEBUG"
JARVIS_VERBOSE=true
EOF
```

### Clean Installation
```bash
# Remove Python cache
find . -name "__pycache__" -type d -exec rm -rf {} +
find . -name "*.pyc" -delete

# Reinstall dependencies
pip uninstall -r requirements.txt -y
pip install -r requirements.txt

# Verify installation
python verify_installation.py
```

### Check Dependencies
```bash
# Verify all dependencies
pip check

# List installed packages
pip list | grep -E "(langchain|ollama|whisper|pyaudio)"

# Update dependencies
pip install --upgrade -r requirements.txt
```

## 📊 Log Analysis

### Important Log Patterns

#### Successful Tool Calling
```
INFO - jarvis.core.agent - Loaded 5 tools: ['get_current_time', ...]
DEBUG - jarvis.core.agent - Tool calling agent created successfully
INFO - jarvis.tools.plugins.device_time_tool - Successfully retrieved device time: 2:30 PM
```

#### Tool Calling Failures
```
WARNING - jarvis.core.agent - Tool call failed: [error details]
ERROR - jarvis.tools.plugins.device_time_tool - Failed to get device time: [error]
```

#### Configuration Issues
```
ERROR - jarvis.config - Failed to load configuration: [error]
WARNING - jarvis.config - Environment variable override: JARVIS_MODEL
```

### Log File Locations
```bash
# Default log output (stdout)
python start_jarvis.py 2>&1 | tee jarvis.log

# Custom log file
echo 'JARVIS_LOG_FILE="/tmp/jarvis.log"' >> .env
```

## 🆘 Getting Help

### Before Reporting Issues

1. **Run diagnostics**: `python verify_installation.py`
2. **Check logs**: Enable debug logging and review output
3. **Test components**: Use the debugging steps above
4. **Search existing issues**: Check GitHub issues for similar problems

### Reporting Issues

Include this information:
```bash
# System information
python --version
ollama --version
uname -a

# Jarvis configuration
python -c "from jarvis.config import get_config; print(get_config())"

# Available tools
python -c "from jarvis.tools import get_langchain_tools; print([t.name for t in get_langchain_tools()])"

# Error logs (with debug enabled)
# Include relevant log output
```

### Community Resources

- **GitHub Issues**: Report bugs and feature requests
- **GitHub Discussions**: Ask questions and share solutions
- **Documentation**: Check `docs/` directory for detailed guides

---

**Most issues can be resolved by ensuring llama3.1:8b is properly installed and configured!** 🚀
