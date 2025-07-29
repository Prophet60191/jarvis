# 📚 Jarvis Documentation

Welcome to the comprehensive documentation for Jarvis Voice Assistant! This guide will help you understand, use, and contribute to Jarvis.

## 🚀 Quick Start

**New to Jarvis?** Start here:

1. **[Complete User Guide](../USER_GUIDE.md)** - Comprehensive guide for end users
2. **[Installation Guide](installation.md)** - Get Jarvis running on your system
3. **[Developer Quick Start](DEVELOPER_QUICK_START.md)** - For developers wanting to contribute or extend Jarvis
4. **[Documentation Index](../DOCUMENTATION_INDEX.md)** - Find all guides and references

## 📖 Documentation Structure

### 🏗️ **Architecture & Design**
- **[Architecture Overview](ARCHITECTURE.md)** - Complete system architecture and design decisions
- **[MCP System Overview](MCP_SYSTEM_OVERVIEW.md)** - Plugin system architecture and implementation

### 🔗 **MCP Integration (NEW!)**
- **[MCP Integration Guide](MCP_INTEGRATION_GUIDE.md)** - Complete guide to external tool integration
- **[MCP API Reference](MCP_API_REFERENCE.md)** - Technical API documentation for MCP components
- **[MCP Troubleshooting](MCP_TROUBLESHOOTING.md)** - Common MCP issues and solutions

### 🛠️ **Development**
- **[Developer Quick Start](DEVELOPER_QUICK_START.md)** - Comprehensive developer onboarding
- **[API Documentation](API_DOCUMENTATION.md)** - Complete API reference for all components
- **[Tool Development Guide](TOOL_DEVELOPMENT_GUIDE.md)** - Detailed guide for creating tools and plugins
- **[Tool Quick Reference](TOOL_QUICK_REFERENCE.md)** - Quick reference for tool development
- **[Plugin Development Guide](plugin_development_guide.md)** - MCP plugin system guide
- **[Developer Critical Notes](DEVELOPER_CRITICAL_NOTES.md)** - Must-read notes for developers

### 🔧 **Setup & Configuration**
- **[Installation Guide](installation.md)** - Complete installation instructions
- **[Configuration Guide](../README.md#configuration)** - All configuration options and settings
- **[Web UI Guide](../WEB_UI_GUIDE.md)** - Web interface usage and features

### 🆘 **Support & Troubleshooting**
- **[Troubleshooting Guide](TROUBLESHOOTING.md)** - Comprehensive problem-solving guide
- **[Contributing Guide](../CONTRIBUTING.md)** - How to contribute to the project

## 🎯 Documentation by Use Case

### **I want to use Jarvis**
1. [Installation Guide](installation.md) - Set up Jarvis
2. [Main README](../README.md) - Learn basic usage
3. [Web UI Guide](../WEB_UI_GUIDE.md) - Configure through web interface
4. [Troubleshooting Guide](TROUBLESHOOTING.md) - Solve common issues

### **I want to develop plugins/tools**
1. [Developer Quick Start](DEVELOPER_QUICK_START.md) - Get development environment ready
2. [Tool Development Guide](TOOL_DEVELOPMENT_GUIDE.md) - Learn tool creation
3. [API Documentation](API_DOCUMENTATION.md) - Understand the APIs
4. [Developer Critical Notes](DEVELOPER_CRITICAL_NOTES.md) - Avoid common pitfalls

### **I want to contribute to Jarvis core**
1. [Architecture Overview](ARCHITECTURE.md) - Understand the system design
2. [Developer Quick Start](DEVELOPER_QUICK_START.md) - Set up development environment
3. [API Documentation](API_DOCUMENTATION.md) - Learn the internal APIs
4. [Contributing Guide](../CONTRIBUTING.md) - Follow contribution guidelines

### **I want to understand how Jarvis works**
1. [Architecture Overview](ARCHITECTURE.md) - System design and components
2. [MCP System Overview](MCP_SYSTEM_OVERVIEW.md) - Plugin architecture
3. [API Documentation](API_DOCUMENTATION.md) - Technical implementation details

## 🔍 Key Features Documentation

### **Tool Calling System**
- **Current Model**: llama3.1:8b (optimized for reliable tool calling)
- **Plugin System**: MCP-based architecture for extensibility
- **Built-in Tools**: Time, UI control, video advice
- **Development**: [Tool Development Guide](TOOL_DEVELOPMENT_GUIDE.md)

### **Audio System**
- **Speech Recognition**: Faster-Whisper (local, privacy-focused)
- **Text-to-Speech**: Apple TTS with enhanced fallback
- **Wake Word**: Customizable with confidence scoring
- **Configuration**: [Audio settings in main README](../README.md#audio-settings)

### **Web Interface**
- **Modern UI**: Dark theme with responsive design
- **Real-time Config**: Changes apply without restart
- **Voice Control**: "Jarvis, open settings"
- **Guide**: [Web UI Guide](../WEB_UI_GUIDE.md)

### **Privacy & Security**
- **100% Local**: No external API calls
- **Offline Operation**: Works without internet
- **No Data Collection**: Everything stays on your device
- **Details**: [Privacy section in main README](../README.md#privacy--local-operation)

## 📋 Documentation Standards

### **For Contributors**

When updating documentation:

1. **Keep it current**: Update docs when code changes
2. **Be comprehensive**: Include examples and use cases
3. **Test examples**: Ensure all code examples work
4. **Cross-reference**: Link related documentation
5. **User-focused**: Write for the intended audience

### **Documentation Types**

- **Guides**: Step-by-step instructions (installation.md)
- **References**: Complete API documentation (API_DOCUMENTATION.md)
- **Overviews**: High-level explanations (ARCHITECTURE.md)
- **Troubleshooting**: Problem-solving guides (TROUBLESHOOTING.md)

## 🔄 Recent Updates

### **Latest Changes** (Current)
- ✅ Updated to llama3.1:8b as default model
- ✅ Fixed tool calling reliability issues
- ✅ Enhanced TTS fallback system with user configuration
- ✅ Comprehensive documentation overhaul
- ✅ Added troubleshooting and API documentation

### **Key Improvements**
- **Tool Calling**: Now works reliably with llama3.1:8b
- **Configuration**: Fully configurable TTS fallback system
- **Documentation**: Complete developer and user guides
- **Stability**: Enhanced error handling and recovery

## 🤝 Contributing to Documentation

### **How to Help**

1. **Report Issues**: Found outdated info? Create an issue
2. **Suggest Improvements**: Ideas for better documentation
3. **Submit Updates**: Fix errors or add missing information
4. **Write Examples**: Add more usage examples

### **Documentation Guidelines**

- **Clear and Concise**: Easy to understand
- **Well-Structured**: Logical organization
- **Code Examples**: Working, tested examples
- **Cross-Platform**: Consider different operating systems
- **Up-to-Date**: Reflect current codebase

## 📞 Getting Help

### **If you can't find what you need:**

1. **Search Issues**: Check [GitHub Issues](https://github.com/Prophet60191/jarvis/issues)
2. **Ask Questions**: Use [GitHub Discussions](https://github.com/Prophet60191/jarvis/discussions)
3. **Check Troubleshooting**: [Troubleshooting Guide](TROUBLESHOOTING.md)
4. **Review Examples**: Look at `examples/` directory

### **For Developers**

- **API Questions**: [API Documentation](API_DOCUMENTATION.md)
- **Architecture Questions**: [Architecture Overview](ARCHITECTURE.md)
- **Plugin Development**: [Tool Development Guide](TOOL_DEVELOPMENT_GUIDE.md)
- **Critical Issues**: [Developer Critical Notes](DEVELOPER_CRITICAL_NOTES.md)

---

## 📚 Complete Documentation Index

### **Core Documentation**
- [Main README](../README.md) - Project overview
- [Installation Guide](installation.md) - Setup instructions
- [Architecture Overview](ARCHITECTURE.md) - System design
- [API Documentation](API_DOCUMENTATION.md) - Complete API reference

### **Development**
- [Developer Quick Start](DEVELOPER_QUICK_START.md) - Developer onboarding
- [Tool Development Guide](TOOL_DEVELOPMENT_GUIDE.md) - Create tools and plugins
- [Tool Quick Reference](TOOL_QUICK_REFERENCE.md) - Quick development reference
- [Plugin Development Guide](plugin_development_guide.md) - MCP plugin system
- [MCP System Overview](MCP_SYSTEM_OVERVIEW.md) - Plugin architecture
- [Developer Critical Notes](DEVELOPER_CRITICAL_NOTES.md) - Important developer notes

### **User Guides**
- [Web UI Guide](../WEB_UI_GUIDE.md) - Web interface usage
- [Troubleshooting Guide](TROUBLESHOOTING.md) - Problem solving
- [Contributing Guide](../CONTRIBUTING.md) - How to contribute

### **Planning & Development**
- [Coqui TTS Planning](../COQUI_TTS_PLANNING.md) - TTS system planning

---

**Welcome to Jarvis! We're excited to have you as part of our community.** 🚀
