# 🎤 Start Jarvis Voice Assistant

## 🚀 Quick Start

**To start Jarvis, run this single command:**

```bash
cd "/Users/josed/Desktop/Voice App" && python start_jarvis.py
```

## ✅ What's Included

Your Jarvis voice assistant includes:

### 🎯 **Core Features:**
- ✅ **Wake Word Detection**: Say "Hey Jarvis" or "Jarvis"
- ✅ **Speech Recognition**: Whisper + Google fallback
- ✅ **Text-to-Speech**: Coqui TTS with your preferred voice
- ✅ **Conversation Mode**: 30-second timeout, continuous listening

### 🔧 **MCP Tools (15 tools):**
- ✅ **Time Server**: Current time, date, datetime info
- ✅ **Filesystem Access**: Read, write, list, search files and directories

### 🧠 **RAG Memory System (6 tools):**
- ✅ **Conversation Search**: Search your chat history
- ✅ **Memory Storage**: Remember facts and preferences
- ✅ **Document Search**: Search ingested documents
- ✅ **Intelligent Search**: Advanced query optimization

## 🗣️ Voice Commands

### **Wake Up Jarvis:**
- "Hey Jarvis"
- "Jarvis"

### **Time & Date:**
- "What time is it?"
- "Tell me the current date"
- "What's the current date and time?"

### **File Management:**
- "List my desktop files"
- "What files are in my Documents folder?"
- "Show me the contents of my home directory"

### **Memory & Search:**
- "Search my conversations for coffee"
- "What do you remember about coffee?"
- "Do you remember what I told you about coffee?"
- "Search my memories for coffee preferences"

### **Store Memories:**
- "Remember that I like coffee in the morning"
- "Remember this: I prefer dark roast coffee"
- "I like espresso with oat milk"
- "My favorite coffee is cappuccino"

### **General AI:**
- "Hello, how are you?"
- "Tell me a joke"
- "What is artificial intelligence?"
- "Help me plan my day"

## 🎯 System Status

**Currently Running:**
- ✅ **2 MCP Servers**: Time Server + Filesystem Access
- ✅ **15 MCP Tools**: External tool architecture
- ✅ **6 RAG Tools**: Memory and conversation search
- ✅ **Wake Word Detection**: Reliable and responsive
- ✅ **Voice Quality**: Professional Coqui TTS

## 🔧 Troubleshooting

**If Jarvis doesn't respond:**
1. Check that the wake word was detected (you'll see "🎯 WAKE WORD DETECTED!")
2. Speak clearly and wait for the "🎤 Listening for command..." prompt
3. Try restarting: `Ctrl+C` then run the start command again

**If tools don't work:**
- MCP tools load automatically on startup
- RAG tools require the vector database to be initialized
- Check the startup logs for any failed tool loading

## 📊 Performance

**Startup Time:** ~30 seconds (loading models and tools)
**Response Time:** ~2-3 seconds for most commands
**Memory Usage:** Optimized for local execution
**Tool Count:** 21 total tools (15 MCP + 6 RAG)

---

**🎉 Enjoy your fully functional Jarvis voice assistant!**
