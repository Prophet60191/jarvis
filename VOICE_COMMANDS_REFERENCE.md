# **JARVIS VOICE COMMANDS REFERENCE**

Complete reference guide for all Jarvis Voice Assistant voice commands and speech patterns.

## **QUICK START**

### **Wake Word**
- **"Hey Jarvis"** - Primary wake word
- **"Jarvis"** - Alternative wake word

**Usage**: Say the wake word and wait for the acknowledgment sound before giving your command.

### **Basic Pattern**
```
"Hey Jarvis, [command]"
```

## **CORE SYSTEM COMMANDS**

### **Time & Date**
```
"What time is it?"
"What's the date today?"
"What day is it?"
"What's the current time?"
"Tell me the date"
```

### **System Control**
```
"Open settings"
"Close settings"
"Open the settings"
"Close the settings"
"Open settings audio"          # Open audio settings specifically
"Stop listening"               # Pause voice recognition
"Start listening"              # Resume voice recognition
```

### **Help & Information**
```
"What can you do?"
"Show my profile"
"What do you remember about me?"
"Help me"
"What are your capabilities?"
```

## **DESKTOP APPLICATIONS**

### **Knowledge Vault**
```
"Open vault"
"Open the vault"
"Open vault upload"            # Open with upload panel
"Close vault"
"Close the vault"
```

### **User Help Interface**
```
"Open user help"
"Show user help"
"Open help"
"Show documentation"
"Close user help"
"Close help"
"Search help for [topic]"      # Opens help and suggests search
```

## **MEMORY & KNOWLEDGE**

### **Personal Information**
```
"My name is [Your Name]"
"What's my name?"
"Remember that I like [preference]"
"Remember that [fact]"
"What do you remember about [topic]?"
"Forget about [topic]"
"Show my memories"
```

### **Knowledge Management**
```
"Store this information: [content]"
"What do you know about [topic]?"
"Search for [query]"
"Find information about [subject]"
```

## **DEVELOPMENT TOOLS**

### **Aider Integration (AI Code Editing)**
```
"Edit code with Aider"
"Refactor this file with Aider"
"Use Aider to [coding task]"
"Aider help with [code problem]"
```

### **Open Interpreter (Code Execution)**
```
"Execute code to [task description]"
"Run code to [specific operation]"
"Calculate [mathematical expression]"
"Process [data description]"
"Analyze [file path]"
"Create a [language] script to [purpose]"
"Check my [system aspect]"
```

### **Robot Framework (Testing)**
```
"Run Robot Framework tests"
"Execute test suite [name]"
"Run automated tests"
"Check test results"
```

## **WEB AUTOMATION**

### **LaVague Web Automation**
```
"Go to [website] and [action]"
"Search [website] for [query]"
"Fill out the form on [website]"
"Click [element] on [website]"
"Extract [data] from [website]"
```

**Examples**:
```
"Go to Amazon and search for wireless keyboards under $50"
"Fill out the contact form on example.com"
"Extract all product prices from the shopping page"
```

## **SYSTEM MONITORING**

### **Log Terminal Tools**
```
"Show system logs"
"Check error logs"
"Monitor [service] logs"
"Clear log files"
"Export logs"
```

### **Performance Monitoring**
```
"Show system performance"
"Check CPU usage"
"Monitor memory usage"
"Display system status"
```

## **ADVANCED PATTERNS**

### **Chained Commands**
You can combine multiple actions:
```
"Open settings, go to audio, and test the microphone"
"Remember my preference and then show my profile"
"Search for Python tutorials and open the first result"
```

### **Conditional Commands**
```
"If it's after 5 PM, remind me to [task]"
"When [condition], then [action]"
```

### **Context-Aware Commands**
Jarvis remembers context within conversations:
```
You: "Open the Python file"
Jarvis: "Which Python file would you like me to open?"
You: "The main one"          # Jarvis understands context
```

## **VOICE COMMAND TIPS**

### **Best Practices**
1. **Speak Clearly**: Use normal speaking pace and volume
2. **Wait for Acknowledgment**: Let Jarvis respond before next command
3. **Be Specific**: "Open settings audio" vs "Open settings"
4. **Use Natural Language**: Jarvis understands conversational speech
5. **Pause Between Commands**: Give Jarvis time to process

### **Common Patterns**
- **Action + Object**: "Open settings", "Close vault"
- **Question Format**: "What time is it?", "What's my name?"
- **Imperative**: "Remember that...", "Show me..."
- **Request Format**: "Please open...", "Can you show me..."

### **Troubleshooting Voice Commands**
```
"Test microphone"             # Check if Jarvis can hear you
"Repeat that"                 # Ask Jarvis to repeat last response
"I didn't understand"         # Get clarification
"Help with voice commands"    # Get command suggestions
```

## **CUSTOMIZATION**

### **Wake Word Configuration**
You can customize the wake word in settings:
- Default: "Hey Jarvis" or "Jarvis"
- Custom options available in audio settings

### **Voice Recognition Settings**
- **Sensitivity**: Adjust microphone sensitivity
- **Timeout**: Set how long Jarvis waits for commands
- **Language**: Configure speech recognition language

### **Response Preferences**
- **Verbosity**: Control how detailed responses are
- **Confirmation**: Enable/disable command confirmations
- **Feedback**: Adjust audio feedback settings

## **PLUGIN-SPECIFIC COMMANDS**

### **Device Time Tool**
```
"What time is it?"
"What's the date?"
"What day is today?"
"Show me the current time"
"Tell me today's date"
```

### **User Profile Tool**
```
"My name is [name]"
"What's my name?"
"Show my profile"
"Update my profile"
"Set my preference for [item] to [value]"
```

### **RAG Memory Tool**
```
"Remember that [information]"
"What do you remember about [topic]?"
"Search your memory for [query]"
"Forget about [topic]"
"Show all memories"
"Clear memory"
```

## **VOICE COMMAND DEVELOPMENT**

### **Creating Custom Commands**
Developers can add new voice commands by:
1. Creating plugin tools with voice command metadata
2. Defining command patterns and triggers
3. Implementing command handlers
4. Testing with voice recognition

### **Command Pattern Examples**
```python
# In plugin development
voice_commands = [
    "do [action]",
    "perform [task]",
    "[action] the [object]"
]
```

## **TROUBLESHOOTING**

### **Common Issues**
1. **Jarvis doesn't respond**: Check wake word, microphone settings
2. **Commands not recognized**: Speak more clearly, check for background noise
3. **Wrong action**: Use more specific commands
4. **No audio feedback**: Check TTS settings and volume

### **Testing Commands**
```
"Test voice recognition"      # Test if Jarvis can hear you
"Test text to speech"         # Test if Jarvis can speak
"What commands are available?" # Get list of available commands
"Help with [specific feature]" # Get help for specific functionality
```

### **Debug Commands**
```
"Show system status"
"Check audio settings"
"Display available tools"
"What plugins are loaded?"
```

## **VOICE COMMAND REFERENCE BY CATEGORY**

### **Essential Daily Use**
- Time/Date queries
- Settings management
- Basic help commands
- Profile management

### **Knowledge Management**
- Memory storage/retrieval
- Information search
- Document management
- Knowledge vault access

### **Development & Automation**
- Code execution
- File analysis
- Web automation
- Testing frameworks

### **System Administration**
- Log monitoring
- Performance checking
- Configuration management
- Troubleshooting tools

## **CONCLUSION**

Jarvis supports a wide range of voice commands from basic system control to advanced development tasks. The key to effective use is:

1. **Start Simple**: Master basic commands first
2. **Be Natural**: Use conversational language
3. **Stay Consistent**: Use similar patterns for similar actions
4. **Explore Gradually**: Try new commands as you become comfortable
5. **Customize**: Adjust settings to match your preferences

**Remember**: Jarvis is designed to understand natural speech, so don't worry about exact wording. If a command doesn't work, try rephrasing it naturally.

---

*For technical details about implementing voice commands, see the [Tool Development Guide](jarvis/docs/TOOL_DEVELOPMENT_GUIDE.md) and [Plugin Reference Guide](PLUGIN_REFERENCE_GUIDE.md).*
