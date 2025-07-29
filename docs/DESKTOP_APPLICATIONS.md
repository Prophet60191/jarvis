# Desktop Applications Guide

This guide covers Jarvis's native desktop applications, including the Knowledge Vault and Settings Panel, along with their robust lifecycle management system.

## Overview

Jarvis includes two native desktop applications built with PyWebView:

1. **Knowledge Vault** (`rag_app.py`) - Document management and RAG system control
2. **Settings Panel** (`jarvis_settings_app.py`) - Jarvis configuration and preferences

Both applications feature:
- Native desktop windows with web-based UI
- Voice command integration
- Robust lifecycle management
- Proper signal handling and cleanup
- Reliable open/close cycles

## Voice Commands

### Opening Applications

| Command | Action | Application |
|---------|--------|-------------|
| "Open vault" | Opens the Knowledge Vault | `rag_app.py` |
| "Open settings" | Opens the Settings Panel | `jarvis_settings_app.py` |
| "Show vault" | Opens the Knowledge Vault | `rag_app.py` |
| "Manage vault" | Opens the Knowledge Vault | `rag_app.py` |
| "Open documents" | Opens the Knowledge Vault | `rag_app.py` |

### Closing Applications

| Command | Action |
|---------|--------|
| "Close vault" | Closes the Knowledge Vault |
| "Close settings" | Closes the Settings Panel |

### Panel-Specific Opening

You can open specific panels within applications:

```
"Open vault upload"     → Opens vault with upload panel
"Open vault documents"  → Opens vault with documents panel
"Open vault memory"     → Opens vault with memory panel
"Open settings audio"   → Opens settings with audio panel
"Open settings llm"     → Opens settings with LLM panel
```

## Application Architecture

### Robust Lifecycle Management

The desktop applications use a sophisticated lifecycle management system that ensures reliable operation:

#### Signal Handling
```python
def signal_handler(signum, frame):
    print(f"\n🛑 App received signal {signum}, shutting down...")
    shutdown_event.set()
    try:
        webview.destroy()  # Clean up webview resources
    except:
        pass
    sys.exit(0)  # Clean exit

signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)
```

#### Process Group Management
- Applications start in new process groups (`start_new_session=True`)
- Graceful termination with SIGTERM to entire process group
- Force kill fallback with SIGKILL if graceful termination fails
- Cleanup of related background processes

#### Application Manager
The `AppManager` class provides:
- Application registration and tracking
- Automatic cleanup of existing instances before starting new ones
- Thread-safe operations with locks
- Comprehensive error handling and logging

### File Locations

```
jarvis/
├── rag_app.py                           # Knowledge Vault application
├── jarvis/
│   └── jarvis_settings_app.py           # Settings Panel application
└── jarvis/jarvis/utils/
    └── app_manager.py                   # Application lifecycle manager
```

### Tool Integration

Desktop applications are controlled through plugin tools:

- **Vault Tools**: `jarvis/jarvis/tools/plugins/rag_ui_tool.py`
  - `open_rag_manager()` - Opens the vault
  - `close_rag_manager()` - Closes the vault

- **Settings Tools**: `jarvis/jarvis/tools/plugins/jarvis_ui_tool.py`
  - `open_jarvis_ui()` - Opens settings
  - `close_jarvis_ui()` - Closes settings

## Knowledge Vault Application

### Features
- Document upload and management
- RAG system configuration
- Memory management interface
- Database agent monitoring
- Document versioning and history

### Panels
- **Main**: Dashboard overview
- **Upload**: Document upload interface
- **Documents**: Document library management
- **Memory**: Memory and knowledge management
- **Settings**: RAG configuration options

### Usage
```bash
# Direct launch
python rag_app.py --panel main

# Voice command
"Open vault"
"Open vault upload"
```

## Settings Panel Application

### Features
- Audio configuration (microphone, speakers, TTS)
- LLM model configuration
- Conversation settings
- Logging configuration
- Voice profile management
- Device information

### Panels
- **Main**: Settings dashboard
- **Audio**: Audio device and TTS configuration
- **LLM**: Language model settings
- **Conversation**: Chat and response settings
- **Logging**: Debug and logging options
- **General**: General application settings
- **Voice Profiles**: Voice cloning and profiles
- **Device**: System and device information

### Usage
```bash
# Direct launch
python jarvis/jarvis_settings_app.py --panel audio

# Voice command
"Open settings"
"Open settings audio"
```

## Troubleshooting

### Common Issues

#### Application Won't Open
1. Check if PyWebView is installed: `pip install pywebview`
2. Verify application files exist at correct paths
3. Check for port conflicts (default: 8080 for settings, 8081 for vault)

#### Application Won't Close
1. The new signal handling should resolve this automatically
2. If issues persist, check for zombie processes: `ps aux | grep jarvis`
3. Force kill if necessary: `pkill -f "rag_app.py"`

#### Path Resolution Issues
The robust path finding algorithm automatically locates applications:
- Searches up directory tree for project root (contains `rag_app.py`)
- Constructs absolute paths to application files
- Provides fallback to current working directory

### Debugging

Enable debug mode for detailed logging:
```bash
# Environment variable
export JARVIS_DEBUG=true

# Direct launch with debug
python rag_app.py --debug
python jarvis/jarvis_settings_app.py --debug
```

### Log Locations
- Application logs: `~/.jarvis/logs/`
- Process management logs: Check Jarvis main log output

## Development

### Adding New Desktop Applications

1. **Create Application Script**
   ```python
   # my_app.py
   import signal
   import webview
   
   def signal_handler(signum, frame):
       webview.destroy()
       sys.exit(0)
   
   signal.signal(signal.SIGTERM, signal_handler)
   signal.signal(signal.SIGINT, signal_handler)
   
   webview.create_window("My App", "http://localhost:8082")
   webview.start()
   ```

2. **Register with App Manager**
   ```python
   from jarvis.utils.app_manager import get_app_manager
   
   app_manager = get_app_manager()
   app_manager.register_app("my_app", "/path/to/my_app.py")
   ```

3. **Create Tool Plugin**
   ```python
   @tool
   def open_my_app() -> str:
       app_manager = get_app_manager()
       if app_manager.start_app("my_app"):
           return "My App is now open."
       return "Failed to open My App."
   ```

### Best Practices

1. **Always implement signal handlers** for graceful shutdown
2. **Use the AppManager** for lifecycle management
3. **Start in new process groups** to avoid conflicts
4. **Clean up webview resources** before exit
5. **Provide fallback mechanisms** for error cases
6. **Use absolute paths** for reliable file location

## Recent Fixes

### July 28, 2025 Updates

1. **Fixed Desktop App Shutdown Issues**
   - Added proper signal handlers to both applications
   - Implemented `webview.destroy()` cleanup
   - Fixed zombie process problems

2. **Resolved Settings App Path Issues**
   - Implemented robust path finding algorithm
   - Fixed incorrect path calculations
   - Added fallback mechanisms

3. **Enhanced Application Manager**
   - Added process group management
   - Implemented graceful termination with force fallback
   - Added thread-safe operations

4. **Improved Tool Integration**
   - Fixed import errors in plugin tools
   - Added fallback behavior when AppManager unavailable
   - Enhanced error handling and user feedback

These fixes ensure that desktop applications can be opened and closed reliably, multiple times, without issues.
