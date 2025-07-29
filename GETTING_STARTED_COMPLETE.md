# 🚀 **JARVIS COMPLETE GETTING STARTED GUIDE**

Welcome to Jarvis - your intelligent voice assistant with enhanced AI capabilities, performance monitoring, and analytics! This comprehensive guide will take you from installation to mastery.

## 📋 **TABLE OF CONTENTS**

1. [System Requirements](#-system-requirements)
2. [Installation](#-installation)
3. [First-Time Setup](#-first-time-setup)
4. [Basic Configuration](#-basic-configuration)
5. [Voice Setup](#-voice-setup)
6. [Your First Conversation](#-your-first-conversation)
7. [Essential Features](#-essential-features)
8. [Analytics Dashboard](#-analytics-dashboard)
9. [Troubleshooting](#-troubleshooting)
10. [Next Steps](#-next-steps)

## 💻 **SYSTEM REQUIREMENTS**

### **Minimum Requirements**
- **Operating System**: macOS 10.15+, Windows 10+, or Linux Ubuntu 18.04+
- **Python**: 3.8 or higher
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 2GB free space
- **Audio**: Microphone and speakers/headphones
- **Internet**: Stable connection for AI model access

### **Recommended Requirements**
- **RAM**: 16GB for optimal performance
- **Storage**: 5GB free space for full features
- **CPU**: Multi-core processor for enhanced performance
- **Audio**: High-quality microphone for better voice recognition

### **Dependencies**
Jarvis will automatically install these, but you can install manually if needed:
```bash
# Core dependencies
pip install openai anthropic
pip install pyaudio speechrecognition
pip install pyttsx3 coqui-tts

# Enhanced features
pip install PyQt6 psutil
pip install chromadb faiss-cpu
pip install pytest pytest-asyncio
```

## 🔧 **INSTALLATION**

### **Method 1: Quick Install (Recommended)**

1. **Clone the Repository**
   ```bash
   git clone https://github.com/Prophet60191/jarvis.git
   cd jarvis
   ```

2. **Run the Setup Script**
   ```bash
   python setup_enhanced_dev_env.py
   ```
   
   This will:
   - Install all dependencies
   - Set up the virtual environment
   - Configure initial settings
   - Download required models

3. **Verify Installation**
   ```bash
   python validate_implementation.py
   ```
   
   You should see: ✅ **100% validation success**

### **Method 2: Manual Installation**

1. **Create Virtual Environment**
   ```bash
   python -m venv jarvis_env
   source jarvis_env/bin/activate  # On Windows: jarvis_env\Scripts\activate
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements-enhanced.txt
   ```

3. **Initialize Data Directories**
   ```bash
   python jarvis/create_jarvis_dir.py
   ```

## 🎯 **FIRST-TIME SETUP**

### **Step 1: Launch Jarvis**
```bash
python start_jarvis.py
```

On first launch, you'll see the **Setup Wizard**:

```
🎯 JARVIS FIRST-TIME SETUP WIZARD
==================================
Welcome to Jarvis! Let's get you set up.

[1/6] Checking system requirements...
✅ Python 3.9.7 detected
✅ Audio devices found
✅ Internet connection verified

[2/6] Setting up directories...
✅ Created data directories
✅ Initialized configuration files
✅ Set up logging system
```

### **Step 2: API Configuration**

You'll be prompted to configure AI services:

```
[3/6] AI Service Configuration
==============================
Jarvis supports multiple AI providers. Choose your preferred option:

1. OpenAI (GPT-4) - Recommended
2. Anthropic (Claude)
3. Local models (Advanced)

Enter your choice (1-3): 1

Please enter your OpenAI API key:
(You can get this from https://platform.openai.com/api-keys)
API Key: sk-...

✅ API key validated successfully!
```

### **Step 3: Voice Configuration**

```
[4/6] Voice Configuration
=========================
Setting up text-to-speech...

Available voices:
1. Coqui TTS (High quality, local)
2. System TTS (Fast, basic)

Choose voice system (1-2): 1

Available Coqui voices:
1. American Female (Jenny)
2. American Male (David)
3. British Female (Emma)

Choose voice (1-3): 1

✅ Voice configured: American Female (Jenny)
```

### **Step 4: Performance Settings**

```
[5/6] Performance Configuration
===============================
Configure system performance:

1. Performance Mode:
   - High Performance (recommended for 16GB+ RAM)
   - Balanced (recommended for 8GB RAM)
   - Low Resource (for 4GB RAM)

Choose mode (1-3): 2

2. Analytics:
   - Enable usage analytics? (helps improve Jarvis) [Y/n]: Y
   - Enable performance monitoring? [Y/n]: Y

✅ Performance settings configured
```

### **Step 5: Final Setup**

```
[6/6] Finalizing Setup
======================
✅ Configuration saved
✅ Analytics dashboard initialized
✅ Performance monitoring started
✅ System ready!

🎉 SETUP COMPLETE!

Jarvis is now ready to use. Here's what you can do:

• Say "Hey Jarvis" to start a conversation
• Open Analytics Dashboard: python launch_analytics_dashboard.py
• View settings: python jarvis_settings_app.py
• Get help: Say "Jarvis, help me get started"
```

## ⚙️ **BASIC CONFIGURATION**

### **Settings Interface**

Launch the settings interface:
```bash
python jarvis_settings_app.py
```

### **Key Settings to Configure**

#### **1. General Settings**
- **Wake Word**: "Hey Jarvis" (default) or customize
- **Response Speed**: Fast/Balanced/Thoughtful
- **Conversation Memory**: Enable for context retention
- **Auto-save Conversations**: Recommended for analytics

#### **2. Voice Settings**
- **Voice Selection**: Choose from available TTS voices
- **Speech Rate**: Adjust speaking speed (0.5x to 2.0x)
- **Volume**: Set comfortable listening level
- **Voice Activation**: Configure microphone sensitivity

#### **3. AI Settings**
- **Model Selection**: GPT-4 (recommended) or alternatives
- **Temperature**: Creativity level (0.1-1.0)
- **Max Tokens**: Response length limit
- **System Prompt**: Customize Jarvis personality

#### **4. Performance Settings**
- **Cache Size**: Memory allocation for performance
- **Analytics Level**: Basic/Detailed/Full
- **Monitoring Interval**: Performance check frequency
- **Auto-optimization**: Enable automatic tuning

## 🎤 **VOICE SETUP**

### **Microphone Configuration**

1. **Test Your Microphone**
   ```bash
   python jarvis/diagnose_audio.py
   ```

2. **Adjust Sensitivity**
   - Open Settings → Voice → Microphone
   - Speak normally and adjust until green indicator shows
   - Test with: "Hey Jarvis, can you hear me?"

### **Voice Selection**

1. **Browse Available Voices**
   ```bash
   python discover_us_voices.py
   ```

2. **Test Voices**
   ```bash
   python test_jarvis_voices.py
   ```

3. **Set Preferred Voice**
   - Open Settings → Voice → TTS Voice
   - Select from dropdown
   - Click "Test Voice" to preview
   - Save settings

### **Advanced Voice Features**

- **Voice Cloning**: Create custom voice (advanced users)
- **Multi-language**: Switch between languages
- **Emotion Control**: Adjust voice emotion/tone
- **Speed Control**: Real-time speech rate adjustment

## 💬 **YOUR FIRST CONVERSATION**

### **Starting Jarvis**

1. **Launch Jarvis**
   ```bash
   python start_jarvis.py
   ```

2. **Wait for Ready Signal**
   ```
   🎯 JARVIS VOICE ASSISTANT STARTING
   ===================================
   ✅ Audio system initialized
   ✅ AI models loaded
   ✅ Performance monitoring active
   ✅ Analytics tracking enabled
   
   🎤 Listening for "Hey Jarvis"...
   ```

### **Basic Conversation Examples**

#### **Getting Started**
- **You**: "Hey Jarvis"
- **Jarvis**: "Hello! I'm Jarvis, your AI assistant. How can I help you today?"
- **You**: "What can you do?"
- **Jarvis**: "I can help with many tasks! I can manage files, search the web, answer questions, control applications, analyze data, and much more. What would you like to try first?"

#### **File Management**
- **You**: "Show me my documents"
- **Jarvis**: "I'll open your Documents folder for you." *[Opens file manager]*
- **You**: "Create a new folder called 'Jarvis Projects'"
- **Jarvis**: "I've created the 'Jarvis Projects' folder in your Documents."

#### **Web Search**
- **You**: "Search for the latest news about AI"
- **Jarvis**: "I'll search for recent AI news for you." *[Opens browser with results]*

#### **System Control**
- **You**: "What's my system performance?"
- **Jarvis**: "Your CPU usage is at 15%, memory usage is 45%, and all systems are running smoothly."

### **Conversation Tips**

✅ **DO:**
- Speak clearly and naturally
- Use specific requests ("Open my email" vs "Do email stuff")
- Ask follow-up questions
- Say "thank you" - Jarvis appreciates politeness!

❌ **DON'T:**
- Shout or whisper
- Use very long, complex sentences
- Interrupt while Jarvis is speaking
- Expect instant responses for complex tasks

## 🌟 **ESSENTIAL FEATURES**

### **1. Tool Integration**
Jarvis has access to many tools:
- **File Manager**: "Open my downloads folder"
- **Web Browser**: "Search for Python tutorials"
- **Calculator**: "What's 15% of 250?"
- **Email**: "Check my email"
- **Calendar**: "What's on my schedule today?"
- **Note Taking**: "Take a note: Meeting at 3 PM"

### **2. Context Memory**
Jarvis remembers your conversation:
- **You**: "I'm working on a Python project"
- **Jarvis**: "That sounds interesting! What kind of Python project?"
- **You**: "Can you help me with it later?"
- **Jarvis**: "Of course! I'll remember you're working on a Python project."

### **3. Smart Suggestions**
Jarvis learns your patterns:
- Suggests frequently used tools
- Remembers your preferences
- Offers relevant follow-up actions
- Adapts to your workflow

### **4. Multi-step Tasks**
Handle complex workflows:
- **You**: "Help me organize my photos"
- **Jarvis**: "I'll help you organize photos. First, let me scan your Pictures folder... I found 1,247 photos. Would you like me to sort them by date, create albums, or remove duplicates?"

## 📊 **ANALYTICS DASHBOARD**

### **Launching the Dashboard**
```bash
python launch_analytics_dashboard.py
```

### **Dashboard Overview**

The analytics dashboard shows:

#### **Overview Tab**
- **Total Sessions**: Your conversation count
- **Tool Usage**: Most frequently used tools
- **Success Rate**: How often tasks complete successfully
- **System Status**: Current system health

#### **Tool Usage Tab**
- **Popular Tools**: Your most-used features
- **Tool Chains**: Common tool combinations
- **Success Rates**: Which tools work best for you
- **Usage Trends**: How your usage changes over time

#### **Performance Tab**
- **Response Times**: How fast Jarvis responds
- **System Resources**: CPU, memory, disk usage
- **Error Rates**: System reliability metrics
- **Performance Trends**: System performance over time

#### **User Behavior Tab**
- **Session Patterns**: When you use Jarvis most
- **Conversation Length**: Typical interaction duration
- **Feature Discovery**: New features you've tried
- **Productivity Metrics**: Task completion rates

### **Using Analytics to Improve**

1. **Identify Bottlenecks**: Slow-performing tools or features
2. **Optimize Workflows**: See which tool combinations work best
3. **Discover Features**: Find tools you haven't tried
4. **Track Progress**: Monitor your productivity improvements

## 🔧 **TROUBLESHOOTING**

### **Common Issues and Solutions**

#### **Jarvis Won't Start**
```bash
# Check system status
python validate_implementation.py

# Check for conflicts
python debug_jarvis_issue.py

# Reset configuration
python jarvis/setup_default_voice.py
```

#### **Voice Recognition Problems**
```bash
# Test microphone
python jarvis/diagnose_audio.py

# Adjust sensitivity in settings
python jarvis_settings_app.py
```

#### **Slow Performance**
```bash
# Check system resources
python analyze_mps_performance.py

# Optimize settings
# Open Settings → Performance → Enable Auto-optimization
```

#### **TTS Issues**
```bash
# Test TTS system
python jarvis/diagnose_tts.py

# Reset voice settings
python jarvis/setup_default_voice.py
```

### **Getting Help**

1. **Built-in Help**: Say "Jarvis, help me with [issue]"
2. **Documentation**: Check specific guides in `/docs/`
3. **Logs**: Check `jarvis/logs/` for error details
4. **Community**: GitHub issues and discussions

## 🎯 **NEXT STEPS**

### **Immediate Next Steps**
1. **Explore Tools**: Try different voice commands
2. **Customize Settings**: Adjust to your preferences
3. **Check Analytics**: Monitor your usage patterns
4. **Learn Shortcuts**: Discover time-saving features

### **Advanced Features to Explore**
1. **Plugin Development**: Create custom tools
2. **Integration Setup**: Connect external services
3. **Performance Tuning**: Optimize for your system
4. **Automation**: Set up recurring tasks

### **Learning Resources**
- **User Guide**: `USER_GUIDE.md` - Comprehensive feature guide
- **Plugin Guide**: `PLUGIN_REFERENCE_GUIDE.md` - Create custom tools
- **Architecture**: `ARCHITECTURE.md` - Understand how Jarvis works
- **API Reference**: `API_REFERENCE_ENHANCED.md` - Developer documentation

### **Community and Support**
- **GitHub Repository**: Latest updates and issues
- **Documentation**: Complete guides and references
- **Examples**: Sample configurations and use cases

## 🎉 **CONGRATULATIONS!**

You've successfully set up Jarvis and learned the basics! You now have:

✅ **Fully configured Jarvis installation**
✅ **Personalized voice and AI settings**
✅ **Understanding of core features**
✅ **Analytics dashboard for monitoring**
✅ **Troubleshooting knowledge**

**Welcome to the future of AI assistance!** 🚀

---

*Need more help? Check out our comprehensive [User Guide](USER_GUIDE.md) or visit the [Documentation Index](DOCUMENTATION_INDEX.md) for specific topics.*
