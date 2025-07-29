# 📊 Log Terminal Tools User Guide

Complete guide for using Log Terminal Tools with Jarvis Voice Assistant for debugging and system monitoring.

## 🎯 What are Log Terminal Tools?

Log Terminal Tools provide voice-controlled access to Jarvis's debug logs and system information through dedicated terminal windows. This allows you to monitor Jarvis's operation, debug issues, and view real-time system information without interrupting your main workflow.

### **Key Features**
- **Real-time log viewing**: See Jarvis logs as they happen
- **Voice-controlled terminals**: Open and close log windows with voice commands
- **Cross-platform support**: Works on macOS, Linux, and Windows
- **Debug information**: Access detailed system and application information
- **Non-intrusive monitoring**: Logs display in separate windows

## 🛠️ Setup and Requirements

### **System Requirements**

**macOS**:
- Terminal.app (built-in)
- No additional setup required

**Linux**:
- Any terminal emulator (gnome-terminal, xterm, konsole, etc.)
- X11 or Wayland display server

**Windows**:
- Windows Terminal (recommended)
- PowerShell or Command Prompt
- Windows Subsystem for Linux (optional)

### **Verification**

Check if Log Terminal Tools are available:

```
"Show log status"
```

You should see confirmation that terminal tools are ready.

## 🎤 Voice Commands

### **Basic Log Management**

#### **Opening Log Terminals**
```
"Open debug logs"
"Open log terminal"
"Show debug information"
"Open system logs"
```

#### **Closing Log Terminals**
```
"Close debug logs"
"Close log terminal"
"Hide debug information"
"Close system logs"
```

#### **Status Checking**
```
"Show log status"
"Check debug terminal status"
"Are debug logs open?"
```

### **Advanced Log Operations**

#### **Specific Log Types**
```
"Open error logs only"
"Show warning messages"
"Display info level logs"
"Open verbose debug logs"
```

#### **Log Filtering**
```
"Show logs from the last 5 minutes"
"Filter logs for speech recognition"
"Display only plugin-related logs"
"Show memory system logs"
```

## 🔧 How It Works

### **1. Voice Command Processing**
1. You request to open debug logs
2. Jarvis identifies the appropriate terminal application
3. A new terminal window is launched

### **2. Log Streaming**
1. Terminal connects to Jarvis's log system
2. Real-time logs are streamed to the terminal
3. Logs are formatted for easy reading
4. Different log levels are color-coded (if supported)

### **3. Terminal Management**
1. Terminal windows are tracked by Jarvis
2. Multiple terminals can be open simultaneously
3. Closing commands properly terminate terminals
4. System resources are cleaned up automatically

## 📝 Usage Examples

### **Example 1: Debugging Voice Recognition Issues**

**Voice Command**: "Open debug logs"

**What You'll See**:
```
[2025-07-29 14:30:15] INFO: Speech recognition started
[2025-07-29 14:30:16] DEBUG: Microphone input detected
[2025-07-29 14:30:17] DEBUG: Processing audio chunk
[2025-07-29 14:30:18] INFO: Wake word detected: "jarvis"
[2025-07-29 14:30:19] DEBUG: Listening for command
[2025-07-29 14:30:20] INFO: Command recognized: "open debug logs"
[2025-07-29 14:30:21] DEBUG: Executing log_terminal_tools.open_debug_logs
```

### **Example 2: Monitoring Plugin Loading**

**Voice Command**: "Show debug information"

**What You'll See**:
```
[2025-07-29 14:25:10] INFO: Loading plugins from jarvis/tools/plugins/
[2025-07-29 14:25:11] DEBUG: Found plugin: device_time_tool.py
[2025-07-29 14:25:11] DEBUG: Found plugin: rag_plugin.py
[2025-07-29 14:25:12] INFO: Loaded 8 plugins successfully
[2025-07-29 14:25:12] DEBUG: Plugin tools registered with LangChain
```

### **Example 3: Troubleshooting Memory System**

**Voice Command**: "Display only plugin-related logs"

**What You'll See**:
```
[2025-07-29 14:35:20] DEBUG: RAG plugin: Storing memory chunk
[2025-07-29 14:35:21] INFO: RAG plugin: Memory stored successfully
[2025-07-29 14:35:22] DEBUG: User profile plugin: Name updated
[2025-07-29 14:35:23] INFO: Desktop app plugin: Vault opened
```

## 🎨 Log Format and Information

### **Log Levels**

**INFO**: General information about system operation
- Plugin loading/unloading
- Voice command recognition
- System status changes

**DEBUG**: Detailed technical information
- Function entry/exit
- Variable values
- Processing steps

**WARNING**: Potential issues that don't stop operation
- Configuration problems
- Performance concerns
- Deprecated feature usage

**ERROR**: Problems that affect functionality
- Plugin loading failures
- API connection issues
- Processing errors

### **Log Categories**

**Speech System**:
```
[SPEECH] Microphone initialized
[SPEECH] Wake word detection active
[SPEECH] Command processing started
```

**Plugin System**:
```
[PLUGIN] Loading device_time_tool
[PLUGIN] Tool registered: get_current_time
[PLUGIN] Plugin initialization complete
```

**Memory System**:
```
[RAG] ChromaDB connection established
[RAG] Memory search query: "coffee preferences"
[RAG] Retrieved 3 relevant memories
```

**Desktop Apps**:
```
[DESKTOP] Opening vault application
[DESKTOP] Port 8080 available
[DESKTOP] Application started successfully
```

## ⚙️ Configuration Options

### **Log Level Control**

You can control what level of detail appears in logs:

```
"Set debug level to verbose"
"Show only error and warning logs"
"Enable full debug logging"
"Reduce log verbosity"
```

### **Terminal Preferences**

**macOS Terminal Customization**:
- Logs open in new Terminal.app windows
- Uses system default terminal profile
- Supports color coding and formatting

**Linux Terminal Options**:
- Automatically detects available terminal emulator
- Supports gnome-terminal, xterm, konsole
- Respects system terminal preferences

### **Log Filtering**

Filter logs by component or time:

```
"Show only speech recognition logs"
"Display logs from the last hour"
"Filter out debug messages"
"Show plugin loading logs only"
```

## 🔍 Monitoring and Debugging

### **System Health Monitoring**

Use log terminals to monitor:

**Performance Issues**:
- Slow response times
- Memory usage patterns
- CPU utilization spikes

**Plugin Problems**:
- Loading failures
- Runtime errors
- Configuration issues

**Voice Recognition Issues**:
- Microphone problems
- Wake word detection
- Command processing errors

### **Troubleshooting Workflow**

1. **Open debug logs**: `"Open debug logs"`
2. **Reproduce the issue**: Perform the problematic action
3. **Observe log output**: Look for errors or warnings
4. **Identify the problem**: Find the root cause in logs
5. **Close logs when done**: `"Close debug logs"`

### **Common Log Patterns**

**Successful Operation**:
```
[INFO] Command received: "what time is it"
[DEBUG] Routing to device_time_tool
[DEBUG] Executing get_current_time()
[INFO] Response: "It's 2:30 PM"
```

**Plugin Error**:
```
[ERROR] Plugin loading failed: missing_plugin.py
[DEBUG] ImportError: No module named 'missing_dependency'
[WARNING] Plugin disabled: missing_plugin
```

**Memory System Activity**:
```
[DEBUG] RAG search query: "user preferences"
[DEBUG] ChromaDB query executed
[INFO] Found 2 relevant memories
[DEBUG] Returning formatted results
```

## 🎯 Best Practices

### **Effective Log Monitoring**

**✅ Good Practices**:
- Open logs before reproducing issues
- Keep log windows visible during debugging
- Close logs when not needed to save resources
- Use specific log filtering for focused debugging

**❌ Avoid**:
- Leaving multiple log terminals open unnecessarily
- Ignoring error messages in logs
- Closing logs too quickly when debugging

### **Performance Considerations**

1. **Resource Usage**: Log terminals consume system resources
2. **Log Rotation**: Old logs are automatically managed
3. **Filtering**: Use filters to reduce log volume
4. **Cleanup**: Close terminals when debugging is complete

### **Security Notes**

1. **Sensitive Information**: Logs may contain user data
2. **API Keys**: Credentials are masked in logs
3. **Privacy**: Personal information is filtered when possible
4. **Local Storage**: All logs remain on your local machine

## 🚀 Advanced Features

### **Multiple Terminal Windows**

You can open multiple log terminals for different purposes:

```
"Open debug logs"           # General debugging
"Open error logs only"      # Error monitoring
"Show plugin logs"          # Plugin-specific issues
```

### **Log Analysis**

Use terminal features for log analysis:

**Search in Logs**:
- Use Ctrl+F (Cmd+F on macOS) to search
- Look for specific error messages
- Find patterns in log output

**Copy Log Information**:
- Select and copy relevant log entries
- Share error messages for support
- Save important debugging information

### **Integration with Development**

**For Plugin Development**:
- Monitor plugin loading and execution
- Debug custom tool implementations
- Test error handling and edge cases

**For System Administration**:
- Monitor system health and performance
- Track resource usage patterns
- Identify configuration issues

## 📚 Additional Resources

### **Jarvis Documentation**
- [Troubleshooting Guide](TROUBLESHOOTING.md)
- [Plugin Development Guide](TOOL_DEVELOPMENT_GUIDE.md)
- [API Documentation](API_DOCUMENTATION.md)

### **System Tools**
- [macOS Terminal User Guide](https://support.apple.com/guide/terminal/)
- [Linux Terminal Basics](https://ubuntu.com/tutorials/command-line-for-beginners)
- [Windows Terminal Documentation](https://docs.microsoft.com/en-us/windows/terminal/)

### **Debugging Resources**
- [Python Logging Documentation](https://docs.python.org/3/library/logging.html)
- [Debugging Best Practices](https://realpython.com/python-debugging-pdb/)

---

**Pro Tip**: Keep a log terminal open during initial setup and when trying new features. The real-time feedback helps you understand how Jarvis processes your commands and can quickly identify any issues!
