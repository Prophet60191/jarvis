# 🏗️ Jarvis Architecture Documentation

Comprehensive architecture overview of Jarvis Voice Assistant.

## 📋 Table of Contents

- [System Overview](#system-overview)
- [Component Architecture](#component-architecture)
- [Data Flow](#data-flow)
- [Design Decisions](#design-decisions)
- [Technology Stack](#technology-stack)
- [Security & Privacy](#security--privacy)

## 🌟 System Overview

Jarvis is a **privacy-first, locally-running voice assistant** built with a modular, plugin-based architecture. The system is designed for extensibility, reliability, and complete offline operation.

### Core Principles

1. **Privacy First**: All processing happens locally, no external API calls
2. **Modular Design**: Clear separation of concerns with dependency injection
3. **Plugin Architecture**: Extensible without core code modifications
4. **Real-time Configuration**: Dynamic configuration updates without restarts
5. **Tool Calling Reliability**: Optimized for consistent function calling

## 🏛️ Component Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        JARVIS ARCHITECTURE                      │
├─────────────────────────────────────────────────────────────────┤
│  🎤 AUDIO LAYER                                                │
│  ├── SpeechManager                                             │
│  │   ├── Whisper (Speech Recognition)                         │
│  │   ├── Apple TTS (Primary)                                  │
│  │   ├── Enhanced Fallback TTS                                │
│  │   └── Audio Processing Pipeline                            │
│  ├── WakeWordDetector                                          │
│  │   ├── Confidence Scoring                                   │
│  │   └── Noise Filtering                                      │
│  └── AudioDeviceManager                                        │
│      ├── Microphone Management                                 │
│      └── Speaker/Headphone Output                              │
├─────────────────────────────────────────────────────────────────┤
│  🧠 AI LAYER                                                   │
│  ├── JarvisAgent                                               │
│  │   ├── llama3.1:8b (Ollama)                                │
│  │   ├── LangChain Integration                                 │
│  │   ├── Tool Calling Engine                                   │
│  │   └── Context Management                                    │
│  ├── ConversationManager                                       │
│  │   ├── State Management                                      │
│  │   ├── Auto-Listen Logic                                     │
│  │   └── Session Handling                                      │
│  └── ResponseProcessor                                          │
│      ├── Natural Language Generation                           │
│      └── Response Formatting                                   │
├─────────────────────────────────────────────────────────────────┤
│  🔧 TOOL LAYER (MCP SYSTEM)                                   │
│  ├── PluginManager                                             │
│  │   ├── Auto-Discovery Engine                                 │
│  │   ├── Dynamic Loading                                       │
│  │   └── Error Isolation                                       │
│  ├── ToolRegistry                                              │
│  │   ├── Built-in Tools                                        │
│  │   ├── Plugin Tools                                          │
│  │   └── Tool Execution Engine                                 │
│  └── Built-in Tools                                            │
│      ├── TimeTools (get_current_time)                          │
│      ├── UIControlTools (open/close UI)                        │
│      └── VideoTools (content advice)                           │
├─────────────────────────────────────────────────────────────────┤
│  🌐 INTERFACE LAYER                                            │
│  ├── Web UI Server                                             │
│  │   ├── Configuration Interface                               │
│  │   ├── Real-time Updates                                     │
│  │   ├── Voice Command Integration                             │
│  │   └── Mobile Responsive Design                              │
│  ├── Desktop Application                                       │
│  │   ├── Native Window Management                              │
│  │   └── System Integration                                    │
│  └── CLI Tools                                                 │
│      ├── Plugin Management                                     │
│      └── System Diagnostics                                    │
├─────────────────────────────────────────────────────────────────┤
│  ⚙️ CONFIGURATION LAYER                                        │
│  ├── ConfigurationManager                                      │
│  │   ├── Dynamic Reloading                                     │
│  │   ├── Environment Variables                                 │
│  │   ├── .env File Support                                     │
│  │   └── Web UI Integration                                    │
│  ├── Validation Engine                                         │
│  │   ├── Type Checking                                         │
│  │   ├── Range Validation                                      │
│  │   └── Dependency Verification                               │
│  └── Default Management                                         │
│      ├── Sensible Defaults                                     │
│      └── Platform Optimization                                 │
├─────────────────────────────────────────────────────────────────┤
│  🛡️ INFRASTRUCTURE LAYER                                      │
│  ├── Exception Handling                                        │
│  │   ├── Custom Exception Hierarchy                            │
│  │   ├── Error Recovery                                        │
│  │   └── Graceful Degradation                                  │
│  ├── Logging System                                            │
│  │   ├── Structured Logging                                    │
│  │   ├── Performance Metrics                                   │
│  │   └── Debug Information                                     │
│  └── Testing Framework                                          │
│      ├── Unit Tests                                            │
│      ├── Integration Tests                                     │
│      └── Performance Tests                                     │
└─────────────────────────────────────────────────────────────────┘
```

## 🔄 Data Flow

### 1. Voice Input Processing

```
User Speech → Microphone → Wake Word Detection → Speech Recognition → Text Processing
     ↓
Audio Buffer → Whisper Model → Recognized Text → Conversation Manager
```

### 2. AI Processing & Tool Calling

```
User Text → JarvisAgent → llama3.1:8b → Tool Selection → Tool Execution
     ↓
LangChain → Tool Registry → Plugin System → Tool Response → Response Generation
```

### 3. Audio Output

```
Response Text → TTS Manager → Apple TTS (Primary) → Audio Output
     ↓                              ↓
Enhanced Fallback ← Fallback Logic ← TTS Failure
```

### 4. Configuration Flow

```
Web UI Changes → Configuration API → ConfigurationManager → Component Updates
     ↓                                        ↓
Environment Variables → .env File → Dynamic Reload → Real-time Application
```

## 🎯 Design Decisions

### 1. Model Selection: llama3.1:8b

**Decision**: Use llama3.1:8b as the single default model

**Rationale**:
- **Excellent tool calling**: Reliably calls functions instead of generating placeholders
- **Natural language**: Strong conversational abilities
- **Code capability**: Good at technical queries and code generation
- **Performance**: Fast enough for real-time conversation
- **Resource efficiency**: Runs well on 8GB+ RAM systems

**Alternatives Considered**:
- qwen2.5-coder:7b (poor tool calling)
- Multiple model support (too complex)

### 2. Plugin Architecture: MCP System

**Decision**: Model Context Protocol (MCP) based plugin system

**Rationale**:
- **Zero core changes**: Add tools without modifying main codebase
- **Automatic discovery**: Plugins found and loaded automatically
- **Industry standard**: Following established patterns
- **Developer friendly**: Templates and CLI tools

**Implementation**:
- Plugins in `jarvis/tools/plugins/`
- Auto-discovery on startup
- LangChain tool integration
- Error isolation per plugin

### 3. Audio System: Hybrid TTS

**Decision**: Apple TTS primary with enhanced fallback

**Rationale**:
- **Quality**: Apple TTS provides excellent voice quality
- **Reliability**: Enhanced fallback ensures consistent operation
- **Performance**: Fast response times
- **User control**: Configurable voice preferences

**Architecture**:
- Primary: Apple System TTS
- Fallback: Enhanced pyttsx3 with optimized settings
- Configuration: User-customizable voice selection

### 4. Configuration: Dynamic Updates

**Decision**: Real-time configuration without restarts

**Rationale**:
- **User experience**: Immediate feedback on changes
- **Development efficiency**: Faster iteration cycles
- **Production friendly**: No downtime for config changes

**Implementation**:
- Web UI triggers configuration reload
- Components subscribe to config changes
- Validation before applying changes

## 🛠️ Technology Stack

### Core Technologies

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| **AI Model** | llama3.1:8b via Ollama | Latest | LLM inference and tool calling |
| **Speech Recognition** | Faster-Whisper | Latest | Local speech-to-text |
| **Text-to-Speech** | Apple TTS + pyttsx3 | System | High-quality voice synthesis |
| **Tool Framework** | LangChain | 0.1+ | Tool integration and execution |
| **Web Framework** | Built-in HTTP server | Python 3.8+ | Configuration interface |
| **Plugin System** | Custom MCP implementation | - | Extensible tool architecture |

### Dependencies

```python
# Core AI
langchain-community
langchain-core
ollama

# Audio Processing
faster-whisper
pyaudio
speech-recognition
pyttsx3

# Web Interface
http.server (built-in)
json (built-in)

# Development
pytest
pytest-cov
black
flake8
```

### Platform Optimization

- **macOS**: Primary platform with Apple Silicon optimization
- **Linux**: Full support with alternative TTS backends
- **Windows**: Experimental support

## 🔒 Security & Privacy

### Privacy Architecture

1. **No External Calls**: All processing happens locally
2. **No Data Collection**: No telemetry or analytics
3. **Local Storage**: All data stays on device
4. **Offline Operation**: Works without internet after setup

### Security Measures

1. **Input Validation**: All user inputs validated and sanitized
2. **Error Isolation**: Plugin errors don't crash main system
3. **Resource Limits**: Memory and CPU usage monitoring
4. **Safe Defaults**: Secure configuration defaults

### Data Flow Security

```
User Voice → Local Processing → Local AI → Local Response
     ↓              ↓              ↓           ↓
No Network ← No Cloud APIs ← No External ← No Tracking
```

## 📊 Performance Characteristics

### Initialization Times
- **Cold Start**: ~3-5 seconds (model loading)
- **Warm Start**: ~1-2 seconds (cached model)
- **Plugin Loading**: ~0.5 seconds (auto-discovery)

### Response Times
- **Simple Queries**: 0.5-2 seconds
- **Tool Calling**: 1-3 seconds
- **Complex Reasoning**: 2-5 seconds

### Resource Usage
- **RAM**: 2-4GB (model + application)
- **CPU**: Moderate during inference, low at idle
- **Storage**: ~5GB (model + application)

## 🔮 Future Architecture Considerations

### Planned Enhancements

1. **Multi-language Support**: Extend to other languages
2. **Advanced Tool Chaining**: Complex multi-tool workflows
3. **Performance Optimization**: Model quantization and caching
4. **Mobile Support**: iOS/Android applications

### Scalability Considerations

1. **Plugin Ecosystem**: Community plugin marketplace
2. **Model Flexibility**: Support for different model sizes
3. **Deployment Options**: Docker, cloud deployment guides
4. **Integration APIs**: External system integration

---

This architecture provides a solid foundation for a privacy-focused, extensible voice assistant while maintaining simplicity and reliability. The modular design allows for easy maintenance and future enhancements without breaking existing functionality.
