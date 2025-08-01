# 🔌 Jarvis Plugin Reference Guide

Complete reference for all Jarvis Voice Assistant plugins and their capabilities.

## 📋 Plugin Overview

Jarvis uses a plugin-based architecture where all functionality is provided through plugins. This guide covers all available plugins and their voice commands.

### **Plugin Categories**

- **🕐 Time & Date**: Current time and date information
- **🧠 Memory & RAG**: Information storage and retrieval
- **👤 User Profile**: Personal information management
- **🖥️ Desktop Apps**: Application control and management
- **💻 Development**: Code editing and automation tools
- **🌐 Web Automation**: Browser automation and web scraping
- **📊 System Tools**: Logging and terminal management
- **🤖 Testing**: Automated testing frameworks

## 🔌 Available Plugins

### **1. Device Time Tool** 🕐
**Purpose**: Provides current time and date information from your local device.

**Voice Commands**:
```
"What time is it?"
"What's the current time?"
"Tell me the time"
```

**Features**:
- 12-hour format display
- Local timezone support
- Error handling for system issues

**Technical Details**:
- Plugin file: `device_time_tool.py`
- Function: `get_current_time()`
- Returns: Time in format "2:30 PM"

---

### **2. RAG Memory Plugin** 🧠
**Purpose**: Advanced memory system for storing and retrieving information using semantic search.

**Voice Commands**:
```
# Storing Information
"Remember that I like iced coffee"
"Remember my birthday is March 15th"
"Store this fact: I work from home on Fridays"

# Retrieving Information
"What do you remember about my coffee preferences?"
"Do you remember my birthday?"
"Search my memories for work schedule"
```

**Features**:
- Semantic search capabilities
- Persistent storage across sessions
- PII detection and warnings
- Intelligent query optimization
- Document ingestion support

**Technical Details**:
- Plugin file: `rag_plugin.py`
- Storage: ChromaDB vector database
- Functions: `remember_fact()`, `search_long_term_memory()`, `search_conversations()`

**Documentation**: See [RAG Memory User Guide](JARVIS_RAG_MEMORY_USER_GUIDE.md)

---

### **3. User Profile Tool** 👤
**Purpose**: Manages personal information like name, pronouns, and preferences.

**Voice Commands**:
```
# Setting Information
"My name is Sarah"
"Call me Mike"
"My pronouns are she/her"

# Getting Information
"What's my name?"
"Show my profile"
"What do you know about me?"

# Privacy Controls
"Allow Jarvis to use my name"
"Don't use my name"
"Clear my profile"
```

**Features**:
- Name and preferred name storage
- Pronoun support
- Privacy controls
- Persistent profile storage
- Personalized responses

**Technical Details**:
- Plugin file: `user_profile_tool.py`
- Storage: `~/.jarvis/user_profile.json`
- Functions: `set_my_name()`, `get_my_name()`, `show_my_profile()`

**Documentation**: See [User Profile System Guide](docs/USER_PROFILE_SYSTEM.md)

---

### **4. RAG UI Tool** 🖥️
**Purpose**: Controls the Knowledge Vault desktop application for document management.

**Voice Commands**:
```
"Open vault"
"Open the vault"
"Open vault upload"
"Close vault"
"Close the vault"
"Show RAG status"
```

**Features**:
- Document upload and management
- Memory search interface
- Backup and restore functionality
- Quality metrics viewing
- Data export capabilities

**Technical Details**:
- Plugin file: `rag_ui_tool.py`
- Application: `rag_app.py`
- Functions: `open_rag_manager()`, `close_rag_manager()`

**Documentation**: See [Desktop Applications Guide](docs/DESKTOP_APPLICATIONS.md)

---

### **5. Jarvis UI Tool** 🖥️
**Purpose**: Controls the Settings Panel desktop application for system configuration.

**Voice Commands**:
```
"Open settings"
"Open the settings"
"Open settings audio"
"Close settings"
"Close the settings"
```

**Features**:
- Audio configuration
- LLM model settings
- Conversation parameters
- User interface preferences
- System configuration

**Technical Details**:
- Plugin file: `jarvis_ui_tool.py`
- Application: `jarvis_settings_app.py`
- Functions: `open_settings()`, `close_settings()`

**Documentation**: See [Web UI Guide](jarvis/WEB_UI_GUIDE.md)

---

### **6. Aider Integration Plugin** 💻
**Purpose**: Seamless handoff to Aider AI for advanced code editing and refactoring.

**Voice Commands**:
```
"Edit this file to add [feature]"
"Refactor this code to [improvement]"
"Fix the bug in [file]"
"Add error handling to [function]"
"Update all imports in the project"
"Rename this class everywhere"
"Check Aider status"
```

**Features**:
- Direct code file editing
- Multi-file refactoring
- Automatic git commits
- Project-wide changes
- Intelligent code understanding

**Setup Requirements**:
```bash
# Install Aider
pip install aider-chat

# Verify installation
aider --version
```

**Technical Details**:
- Plugin file: `aider_integration.py`
- Functions: `aider_code_edit()`, `aider_project_refactor()`, `check_aider_status()`
- Models: Supports GPT-4, Claude, and other AI models

**Usage Examples**:
- "Edit main.py to add error logging"
- "Refactor the entire project to use async/await"
- "Fix the authentication bug in auth.py"

---

### **7. LaVague Web Automation Plugin** 🌐
**Purpose**: AI-powered web automation using natural language commands.

**Voice Commands**:
```
"Navigate to [website] and [do something]"
"Fill out the form on [website]"
"Search for [something] on [website]"
"Click the [button/link] on [website]"
"Extract information from [website]"
"Get the [data] from [website]"
"Check LaVague status"
```

**Features**:
- Natural language web automation
- Form filling capabilities
- Data extraction and scraping
- Browser interaction
- Headless operation support

**Setup Requirements**:
```bash
# Install LaVague
pip install lavague-core lavague-drivers-selenium

# Install browser driver
# Chrome/Chromium driver will be auto-installed
```

**Technical Details**:
- Plugin file: `lavague_web_automation.py`
- Functions: `web_automation_task()`, `web_scraping_task()`, `web_form_filling()`
- Browser: Uses Selenium WebDriver

**Usage Examples**:
- "Navigate to Amazon and search for laptops"
- "Fill out the contact form on example.com"
- "Extract the price from this product page"

---

### **8. Log Terminal Tools Plugin** 📊
**Purpose**: Manages log terminal windows for debugging and monitoring.

**Voice Commands**:
```
"Open debug logs"
"Open log terminal"
"Close debug logs"
"Close log terminal"
"Show log status"
```

**Features**:
- Real-time log viewing
- Terminal window management
- Debug information display
- Cross-platform support
- Process management

**Technical Details**:
- Plugin file: `log_terminal_tools.py`
- Functions: `open_debug_logs()`, `close_debug_logs()`
- Platforms: macOS Terminal.app, Linux terminals

**Usage Examples**:
- "Open debug logs" - Opens terminal showing live Jarvis logs
- "Close debug logs" - Closes the log terminal window

---

### **9. Robot Framework Controller Plugin** 🤖
**Purpose**: Automated testing framework integration for test execution and management.

**Voice Commands**:
```
"Run tests"
"Run smoke tests"
"Run all tests"
"Check test status"
"Show test results"
```

**Features**:
- Test suite execution
- Smoke test support
- Result reporting
- Test validation
- Integration testing

**Setup Requirements**:
```bash
# Install Robot Framework
pip install robotframework
pip install robotframework-seleniumlibrary
```

**Technical Details**:
- Plugin file: `robot_framework_controller.py`
- Functions: `run_robot_tests()`, `check_test_status()`
- Framework: Robot Framework with Selenium

**Documentation**: See [Robot Framework User Guide](jarvis/docs/ROBOT_FRAMEWORK_USER_GUIDE.md)

## 🛠️ Plugin Management

### **Listing Available Plugins**
```bash
python manage_plugins.py list
```

### **Enabling/Disabling Plugins**
```bash
# Disable a plugin
python manage_plugins.py disable PluginName

# Enable a plugin
python manage_plugins.py enable PluginName
```

### **Creating Custom Plugins**
```bash
# Generate new plugin template
python manage_plugins.py generate my_tool --type tool --author "Your Name"
```

## 🔧 Plugin Status Check

### **Voice Commands to Check Plugin Status**
```
"Check Aider status"        → Verify Aider installation
"Check LaVague status"      → Verify web automation setup
"Show RAG status"           → Display memory system status
"Show log status"           → Display terminal status
```

### **Command Line Status Check**
```bash
# Test specific plugin
python -c "
from jarvis.tools.plugins.device_time_tool import get_current_time
result = get_current_time.invoke({})
print(result)
"
```

## 📚 Additional Resources

### **Plugin Development**
- [Tool Development Guide](jarvis/docs/TOOL_DEVELOPMENT_GUIDE.md)
- [Plugin Development Guide](jarvis/docs/plugin_development_guide.md)
- [MCP System Overview](jarvis/docs/MCP_SYSTEM_OVERVIEW.md)

### **User Guides**
- [Complete User Guide](USER_GUIDE.md)
- [Desktop Applications Guide](docs/DESKTOP_APPLICATIONS.md)
- [User Profile System Guide](docs/USER_PROFILE_SYSTEM.md)

### **Technical Documentation**
- [API Documentation](jarvis/docs/API_DOCUMENTATION.md)
- [Architecture Overview](ARCHITECTURE.md)
- [Troubleshooting Guide](jarvis/docs/TROUBLESHOOTING.md)

---

**Note**: This reference covers all currently available plugins. New plugins are automatically discovered and loaded when placed in the `jarvis/jarvis/tools/plugins/` directory.
