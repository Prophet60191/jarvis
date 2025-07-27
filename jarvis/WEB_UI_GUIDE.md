# Jarvis UI Complete Guide

This guide provides comprehensive information about the Jarvis Voice Assistant Configuration Interface, available as both a native desktop application and web interface.

## 🚀 Quick Start

### 🖥️ Native Desktop App (Recommended)
```bash
# Install desktop dependencies (one-time)
python install_desktop.py

# Launch native desktop application
python start_desktop.py              # Main dashboard
python start_desktop.py settings     # Settings panel
python start_desktop.py audio        # Audio configuration

# Platform-specific shortcuts
./start_desktop.sh settings          # Unix/Linux/macOS
start_desktop.bat audio             # Windows
```

### 🌐 Web Interface (Browser-based)
```bash
# Cross-platform Python launcher
python start_ui.py                    # Main dashboard
python start_ui.py --panel settings  # Settings overview
python start_ui.py --panel audio     # Audio configuration

# Unix/Linux/macOS
./start_ui.sh                         # Main dashboard
./start_ui.sh settings               # Settings overview

# Windows
start_ui.bat                         # Main dashboard
start_ui.bat settings               # Settings overview
```

### Direct Launch
```bash
python ui/jarvis_ui.py --panel main --port 8080
```

## 🖥️ Desktop vs Web Interface

### Native Desktop Application
- **Native Window**: True desktop app with system integration
- **No Browser Required**: Embedded web view, professional appearance
- **System Integration**: Native window controls, taskbar integration
- **Performance**: Optimized for desktop use, faster startup
- **Installation**: `python install_desktop.py` (one-time setup)

### Web Interface
- **Browser-based**: Opens in your default web browser
- **Universal Access**: Works on any device with a browser
- **No Installation**: Uses existing web browser
- **Remote Access**: Can be accessed from other devices on network
- **Familiar**: Standard web interface experience

Both interfaces provide **identical functionality** - choose based on your preference!

## 🌐 Available Pages

| Panel | URL | Description |
|-------|-----|-------------|
| **main** | `/` | Dashboard overview and system status |
| **settings** | `/settings` | Configuration overview and management |
| **audio** | `/audio` | Audio, microphone, and TTS settings |
| **llm** | `/llm` | Language model configuration |
| **conversation** | `/conversation` | Wake word and conversation flow |
| **logging** | `/logging` | Log levels and output settings |
| **general** | `/general` | General application settings |
| **voice-profiles** | `/voice-profiles` | Voice cloning management |
| **device** | `/device` | Device and hardware information |

## 🎤 Voice Commands

Control the Web UI with voice commands:

```
"Jarvis, open settings"        → Opens configuration overview
"Jarvis, open audio config"    → Opens audio configuration
"Jarvis, open LLM config"      → Opens language model settings
"Jarvis, open device info"     → Opens device information
"Jarvis, open conversation config" → Opens conversation settings
"Jarvis, close UI"             → Shuts down the web interface server
```

## ⚙️ Configuration Features

### Real-time Updates
- **Instant Changes**: All configuration changes apply immediately
- **No Restart Required**: Components update automatically
- **Live Validation**: Real-time error checking and feedback

### Audio Configuration
- **Microphone Settings**: Device selection, energy threshold, timeouts
- **TTS Settings**: Rate, volume, voice preference, response delay
- **Coqui TTS**: Advanced neural TTS with 15+ languages
- **Voice Cloning**: Custom voice profile management

### LLM Configuration
- **Model Selection**: Choose from available Ollama models
- **Parameters**: Temperature, max tokens, reasoning mode
- **Behavior**: Verbose mode, debugging options

### Conversation Settings
- **Wake Word**: Customize activation phrase
- **Timeouts**: Conversation and retry settings
- **Flow Control**: Full duplex mode, response handling

## 🔧 Advanced Features

### Configuration Management
- **Export/Import**: Backup and restore configurations
- **Reload Configuration**: Manual configuration reload
- **Reset to Defaults**: Restore factory settings

### API Endpoints
```bash
# Get current configuration
curl http://localhost:8080/api/config

# Update configuration
curl -X POST http://localhost:8080/api/config \
  -H 'Content-Type: application/json' \
  -d '{"audio": {"tts_rate": 200}}'

# Reload configuration
curl -X POST http://localhost:8080/api/config/reload

# Get device information
curl http://localhost:8080/api/device-info
```

### Voice Profile Management
- **Create Profiles**: Upload audio samples for voice cloning
- **Manage Profiles**: View, activate, and delete voice profiles
- **Quality Scoring**: Automatic quality assessment

## 🛑 Shutting Down the UI

### Web Interface Shutdown
- **Settings Page**: Click the red "Shutdown UI" button
- **Confirmation Dialog**: Confirms shutdown action
- **Auto Tab Close**: Browser tab closes automatically after shutdown

### Command Line Shutdown
```bash
# Graceful shutdown (recommended)
python close_ui.py

# Force shutdown if graceful fails
python close_ui.py --force

# Shutdown on custom port
python close_ui.py --port 3000

# Show help
python close_ui.py --help
```

### Voice Command Shutdown
```
"Jarvis, close UI"    → Shuts down the web interface server
```

### API Shutdown
```bash
# Direct API call
curl -X POST http://localhost:8080/api/shutdown
```

## 🎨 Interface Features

### Modern Design
- **Dark Theme**: Professional dark UI with blue accents
- **Glass-morphism**: Modern backdrop blur effects
- **Responsive**: Works on desktop, tablet, and mobile
- **Sidebar Navigation**: Organized sections with icons

### User Experience
- **Form Validation**: Input validation with helpful constraints
- **Error Handling**: Clear error messages and recovery
- **Success Feedback**: Confirmation of successful operations
- **Auto-refresh**: Page refresh after configuration changes

## 🔍 Troubleshooting

### Common Issues

**Web UI not accessible:**
```bash
# Check if UI is running
curl http://localhost:8080/api/config

# Try different port
python start_ui.py --port 3000

# Check for port conflicts
lsof -i :8080
```

**Configuration changes not applying:**
- Use the "Reload Configuration" button
- Check browser console for JavaScript errors
- Verify .env file permissions and format

**Voice commands not working:**
- Ensure Jarvis main application is running
- Check microphone permissions
- Verify wake word detection is active

### Browser Compatibility
- **Chrome/Chromium**: Full support
- **Firefox**: Full support
- **Safari**: Full support
- **Edge**: Full support

## 📱 Mobile Access

The Web UI is fully responsive and works on mobile devices:

1. **Connect to same network** as the Jarvis server
2. **Find server IP address**: `ifconfig` or `ipconfig`
3. **Access via mobile browser**: `http://[server-ip]:8080`
4. **Touch-friendly interface**: Optimized for mobile interaction

## 🔒 Security Notes

- **Local Network Only**: Web UI is designed for local network access
- **No Authentication**: Intended for trusted local environments
- **Configuration Access**: Full access to all Jarvis settings
- **File System Access**: Limited to configuration files only

## 🚀 Performance

### System Requirements
- **RAM**: Minimal additional memory usage
- **CPU**: Low impact on system performance
- **Network**: Local HTTP server only
- **Storage**: Configuration files only

### Optimization
- **Caching**: Static assets cached by browser
- **Compression**: Gzip compression for responses
- **Lazy Loading**: Configuration loaded on demand
- **Real-time Updates**: Efficient WebSocket-like behavior

## 📚 Development

### Extending the UI
The Web UI can be extended with additional pages and features:

1. **Add new panels** to `jarvis_ui.py`
2. **Create configuration content** methods
3. **Update navigation** in the sidebar
4. **Add API endpoints** for new functionality

### API Integration
The Web UI provides a RESTful API for external integration:

- **Configuration Management**: Full CRUD operations
- **Device Information**: Hardware and system details
- **Voice Profiles**: Voice cloning management
- **Real-time Updates**: Configuration change notifications

This comprehensive Web UI makes Jarvis configuration accessible to users of all technical levels while providing powerful features for advanced users.
