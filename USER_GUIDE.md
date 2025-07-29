# 🎯 Jarvis Voice Assistant - Complete User Guide

Welcome to Jarvis, your AI-powered voice assistant! This comprehensive guide will help you get the most out of Jarvis, from basic setup to advanced features.

## 📋 Table of Contents

1. [Getting Started](#getting-started)
2. [Basic Voice Commands](#basic-voice-commands)
3. [Memory System](#memory-system)
4. [User Profile & Personalization](#user-profile--personalization)
5. [Desktop Applications](#desktop-applications)
6. [Voice & Audio Settings](#voice--audio-settings)
7. [Advanced Features](#advanced-features)
8. [Troubleshooting](#troubleshooting)

## 🚀 Getting Started

### What is Jarvis?

Jarvis is a sophisticated AI voice assistant built on **True Separation of Concerns** architecture. Unlike monolithic assistants, Jarvis:

- **Keeps your data private** - Everything stays on your computer
- **Works offline** - No internet required for core functionality
- **Is truly modular** - Core system, plugins, UIs, and integrations are completely independent
- **Allows safe customization** - Add functionality without breaking existing features
- **Enables independent development** - Modify any component without affecting others
- **Provides fault isolation** - Component failures don't cascade to other parts
- **Remembers information** - Persistent memory across sessions
- **Learns your preferences** - Personalized responses

### First Time Setup

1. **Installation**: Follow the [Installation Guide](jarvis/docs/installation.md)
2. **Start Jarvis**: Run `python start_jarvis.py`
3. **Test your microphone**: Say "Hey Jarvis" and wait for acknowledgment
4. **Set your name**: Say "My name is [Your Name]"
5. **Test basic commands**: Try "What time is it?"

### Understanding the Interface

Jarvis has multiple interfaces:

- **Voice Interface**: Primary interaction method
- **Web Interface**: Configuration and management (http://localhost:8080)
- **Desktop Apps**: Knowledge vault and settings panels
- **Command Line**: For advanced users and debugging

## 🎤 Basic Voice Commands

### Wake Word

**Default**: "Hey Jarvis" or "Jarvis"

Say the wake word and wait for the acknowledgment sound before giving your command.

### Essential Commands

#### **Time & Information**
```
"What time is it?"
"What's the date today?"
"What day is it?"
```

#### **System Control**
```
"Open settings"          → Opens configuration panel
"Close settings"         → Closes configuration panel
"Open vault"            → Opens knowledge management
"Close vault"           → Closes knowledge management
"Stop listening"        → Pauses voice recognition
"Start listening"       → Resumes voice recognition
```

#### **Help & Status**
```
"What can you do?"      → Lists available capabilities
"Show my profile"       → Displays your personal information
"What do you remember about me?" → Shows stored memories
```

### Command Tips

- **Speak clearly** and at normal pace
- **Wait for acknowledgment** after the wake word
- **Use natural language** - Jarvis understands conversational speech
- **Be specific** when possible for better results

## 🧠 Memory System

Jarvis has a sophisticated dual memory system that helps it remember information across conversations.

### How Memory Works

**Short-Term Memory**:
- Remembers context within the current conversation
- Includes recent exchanges and references
- Clears when you restart Jarvis

**Long-Term Memory**:
- Permanently stores facts you explicitly ask it to remember
- Survives across sessions and restarts
- Uses semantic search to find relevant information

### Storing Information

Use natural "remember" commands:

```
"Remember that I like iced coffee over hot coffee"
"Remember my birthday is March 15th"
"Remember that I work from home on Fridays"
"Remember my favorite pizza place is Tony's on Main Street"
"Remember I'm allergic to shellfish"
"Store this fact: I prefer morning workouts"
```

### Retrieving Information

Ask Jarvis to recall stored information:

```
"What do you remember about my coffee preferences?"
"Do you remember my birthday?"
"What have I told you about my work schedule?"
"Tell me what you know about my food allergies"
"What do you remember about my favorite restaurants?"
"Do you remember anything about my exercise routine?"
```

### Memory Management

```
"What do you remember about me?"     → Shows all stored information
"Forget everything about coffee"     → Removes specific memories
"Clear all my memories"              → Removes all stored information
```

### Privacy & Data

- **All data stays local** - Never transmitted to external servers
- **You control what's stored** - Only information you explicitly ask to remember
- **Easy to delete** - Simple commands to remove any or all memories
- **Transparent storage** - You can view exactly what's stored

## 👤 User Profile & Personalization

Jarvis can learn about you to provide personalized responses and remember your preferences.

### Setting Up Your Profile

#### **Your Name**
```
"My name is Sarah"                   → Sets your name
"Call me Mike"                       → Sets preferred name
"I'm Jennifer, but call me Jen"      → Sets both full and preferred name
```

#### **Pronouns**
```
"My pronouns are she/her"
"Use he/him pronouns for me"
"I use they/them pronouns"
```

#### **Preferences**
```
"Remember that I prefer to be called by my first name"
"Remember I like formal responses"
"Remember I prefer brief answers"
```

### Managing Your Profile

#### **Viewing Profile Information**
```
"Show my profile"                    → Displays all profile information
"What's my name?"                    → Shows your name
"What do you know about me?"         → Shows profile summary
```

#### **Privacy Controls**
```
"Allow Jarvis to use my name"        → Enables name usage
"Don't use my name in responses"     → Disables name usage
"Clear my profile"                   → Removes all profile information
```

### How Personalization Works

Once you've set up your profile, Jarvis will:
- **Use your name** in responses when appropriate
- **Remember your preferences** for response style
- **Provide personalized recommendations** based on stored information
- **Adapt communication style** to your preferences

## 🖥️ Desktop Applications

Jarvis includes powerful desktop applications for advanced management and configuration.

### Knowledge Vault

The Knowledge Vault is your document management and memory system interface.

#### **Opening the Vault**
```
"Open vault"                         → Opens main vault interface
"Open vault upload"                  → Opens with upload panel
"Open vault search"                  → Opens with search panel
```

#### **Vault Features**
- **Document Upload**: Add PDFs, text files, and other documents
- **Memory Search**: Find stored information with semantic search
- **Backup Management**: Create and restore memory backups
- **Quality Metrics**: View memory system performance
- **Data Export**: Export your data in various formats

#### **Using the Vault**
1. **Upload Documents**: Drag and drop files or use the upload button
2. **Search Memories**: Use the search bar to find stored information
3. **Manage Backups**: Create regular backups of your data
4. **View Statistics**: Monitor memory usage and quality metrics

### Settings Panel

The Settings Panel provides comprehensive configuration options.

#### **Opening Settings**
```
"Open settings"                      → Opens main settings interface
"Open settings audio"                → Opens audio configuration
"Open settings general"              → Opens general settings
```

#### **Settings Categories**

**Audio Settings**:
- Microphone selection and sensitivity
- Text-to-speech voice and speed
- Audio input/output device configuration

**LLM Settings**:
- AI model selection and parameters
- Response creativity and length settings
- Reasoning and verbose mode options

**Conversation Settings**:
- Wake word customization
- Timeout and retry settings
- Conversation flow preferences

**General Settings**:
- User profile management
- Privacy and data settings
- System preferences

#### **Making Changes**
1. **Navigate** to the appropriate settings section
2. **Modify** settings using the interface controls
3. **Test** changes with the preview buttons
4. **Save** changes (most apply automatically)

### Closing Applications

```
"Close vault"                        → Closes knowledge vault
"Close settings"                     → Closes settings panel
```

Or use the close buttons in the application interfaces.

## 🔊 Voice & Audio Settings

Customize Jarvis's voice and audio behavior to match your preferences.

### Microphone Configuration

#### **Selecting Your Microphone**
1. Open settings: "Open settings audio"
2. Choose your microphone from the device list
3. Test microphone with the test button
4. Adjust sensitivity if needed

#### **Microphone Tips**
- **Use a quality microphone** for better recognition
- **Reduce background noise** for clearer commands
- **Speak 6-12 inches** from the microphone
- **Test different positions** to find the sweet spot

### Text-to-Speech (Voice) Settings

#### **Choosing a Voice**
Jarvis supports multiple TTS engines:

**Coqui TTS** (Recommended):
- High-quality neural voices
- Multiple languages and accents
- Customizable voice characteristics
- Voice cloning capabilities

**System TTS**:
- Uses your operating system's built-in voices
- Fast and lightweight
- Good compatibility

#### **Voice Customization**
1. **Select TTS Engine**: Choose between Coqui and system TTS
2. **Pick a Voice**: Browse available voices
3. **Adjust Speed**: Set speaking rate (words per minute)
4. **Set Volume**: Control voice volume level
5. **Test Settings**: Use preview to hear changes

#### **Voice Cloning** (Advanced)
Create a custom voice that sounds like you:

1. **Record Samples**: Provide 10-30 seconds of clear speech
2. **Upload Audio**: Use the voice cloning interface
3. **Train Model**: Wait for processing (5-10 minutes)
4. **Test Voice**: Preview your custom voice
5. **Activate**: Select your voice from the list

### Audio Troubleshooting

**Voice Recognition Issues**:
- Check microphone permissions
- Test microphone in system settings
- Reduce background noise
- Speak closer to microphone

**TTS Problems**:
- Try different voice engines
- Check audio output device
- Adjust volume settings
- Test with system audio

## 🚀 Advanced Features

### Plugin System

Jarvis uses a powerful plugin system that allows you to extend its capabilities.

#### **Available Plugins**
- **Time Tools**: Date, time, and calendar functions
- **Memory Tools**: Advanced memory management
- **Profile Tools**: User personalization features
- **UI Tools**: Desktop application control
- **Integration Tools**: External service connections

#### **Managing Plugins**
```bash
# List available plugins
python manage_plugins.py list

# Enable/disable plugins
python manage_plugins.py enable PluginName
python manage_plugins.py disable PluginName

# Create new plugins
python manage_plugins.py generate my_tool --type tool
```

### Custom Commands

You can create custom voice commands by developing plugins:

1. **Generate Plugin Template**: Use the plugin generator
2. **Define Commands**: Create functions with the `@tool` decorator
3. **Add Documentation**: Provide clear descriptions
4. **Test Plugin**: Verify functionality
5. **Deploy**: Place in the plugins directory

### Integration Options

**Open Interpreter**:
- Execute code and scripts
- Data analysis and visualization
- File system operations

**Robot Framework**:
- Automated testing capabilities
- Test execution and reporting

**Web Automation**:
- Browser control and automation
- Web scraping and interaction

### Backup and Recovery

#### **Creating Backups**
```
"Create a backup"                    → Creates memory system backup
"Backup my data"                     → Full data backup
```

Or use the vault interface for manual backups.

#### **Restoring Backups**
1. Open the Knowledge Vault
2. Navigate to Backup Management
3. Select backup to restore
4. Confirm restoration

#### **Manual Backup**
```bash
# Backup data directory
cp -r data/ backup_$(date +%Y%m%d)/

# Backup user profile
cp -r ~/.jarvis/ profile_backup_$(date +%Y%m%d)/
```

## 🔧 Troubleshooting

### Common Issues

#### **Jarvis Doesn't Respond to Voice**
1. **Check wake word**: Say "Hey Jarvis" clearly
2. **Test microphone**: Verify microphone is working
3. **Check permissions**: Ensure microphone access is allowed
4. **Reduce noise**: Move to quieter environment

#### **Commands Not Working**
1. **Speak clearly**: Use normal pace and clear pronunciation
2. **Wait for acknowledgment**: Pause after wake word
3. **Try alternatives**: Use different phrasing
4. **Check available tools**: Some commands may not be loaded

#### **Desktop Apps Won't Open**
1. **Install dependencies**: Run `python install_desktop.py`
2. **Check ports**: Ensure ports 8080/8081 are available
3. **Try manual launch**: Run apps directly to see errors
4. **Restart Jarvis**: Sometimes a restart resolves issues

#### **Memory Not Working**
1. **Use explicit commands**: Say "remember" clearly
2. **Check storage**: Verify data directory permissions
3. **Test retrieval**: Try "what do you remember about..."
4. **Clear and retry**: Clear memories and start fresh

### Getting Help

1. **Check Documentation**: Review guides in `docs/` directory
2. **Use Troubleshooting Guide**: See [Troubleshooting](jarvis/docs/TROUBLESHOOTING.md)
3. **Check FAQ**: Review [Frequently Asked Questions](jarvis/docs/FAQ.md)
4. **GitHub Issues**: Report bugs or ask questions
5. **GitHub Discussions**: Community support and ideas

### Performance Tips

1. **Use appropriate AI model**: Balance performance and capability
2. **Close unused applications**: Free up system resources
3. **Regular maintenance**: Clear old logs and temporary files
4. **Monitor resources**: Check CPU and memory usage
5. **Update regularly**: Keep Jarvis and dependencies current

---

## 🎉 Congratulations!

You now have a comprehensive understanding of Jarvis Voice Assistant. Start with basic commands, explore the memory system, and gradually try advanced features as you become more comfortable.

**Remember**: Jarvis is designed to be helpful, private, and customizable. Don't hesitate to experiment with different commands and features to find what works best for you.

**Need more help?** Check the documentation in the `docs/` directory or visit our GitHub repository for support and community discussions.

Happy voice assisting! 🎤✨
