# 🧠 Jarvis RAG Memory System - User Guide

## Overview

Jarvis now features a **plugin-based architecture** with a sophisticated **dual memory system**:

### **🏗️ Architecture Highlights:**
- **Zero Built-in Tools**: Everything is plugin-based for maximum flexibility
- **Dynamic Tool Loading**: Add/remove functionality without changing core code
- **RAG Memory System**: Advanced semantic search with persistent storage

### **🧠 Dual Memory System:**
- **Short-Term Memory**: Remembers context within your current conversation
- **Long-Term Memory**: Permanently stores facts you explicitly ask Jarvis to remember

This means Jarvis can now remember your preferences, important information, and personal details across multiple conversations and sessions!

---

## 🎤 Voice Commands

### **Storing Information (Long-Term Memory)**

Tell Jarvis to remember important facts using natural language:

```
"Jarvis, remember that I like iced coffee over hot coffee"
"Remember that my favorite pizza place is Tony's on Main Street"  
"Please remember that I have a meeting with Sarah every Tuesday at 2 PM"
"Remember that I'm allergic to shellfish"
"Store this fact: I prefer working out in the morning"
"Remember my birthday is March 15th"
```

**What happens:** Jarvis stores this information permanently and can recall it in future conversations.

### **Retrieving Information (Long-Term Memory)**

Ask Jarvis about things you've told it to remember:

```
"What do you remember about my coffee preferences?"
"Do you remember anything about my food allergies?"
"What have I told you about my work schedule?"
"Tell me what you know about my favorite restaurants"
"What do you remember about me?"
"Do you remember my birthday?"
```

**What happens:** Jarvis searches through all stored memories and returns relevant information.

### **Conversational Context (Short-Term Memory)**

Within the same conversation, Jarvis remembers context:

```
You: "What time is it?"
Jarvis: "It's 2:30 PM"
You: "What about the weather?"
Jarvis: "I don't have access to current weather data..."
You: "Okay, can you remind me of that time again?"
Jarvis: "It's 2:30 PM" (remembers "that time" = the time from earlier)
```

---

## 🔒 Privacy & Security

### **PII Detection**

Jarvis automatically detects potentially sensitive information and warns you:

```
You: "Remember my phone number is 555-123-4567"
Jarvis: "⚠️ WARNING: Detected potential sensitive information (phone). 
        I've committed that to my long-term memory: 'my phone number is 555-123-4567'"
```

**Detected PII Types:**
- Phone numbers
- Email addresses  
- Social Security Numbers
- Credit card numbers
- Street addresses

### **What Gets Stored**

- ✅ **Stored**: Facts you explicitly ask Jarvis to remember using "remember" commands
- ❌ **Not Stored**: General conversation, questions, or casual chat
- ❌ **Not Stored**: Temporary context (cleared between sessions)

### **Important: Explicit Memory Storage**

**Jarvis will ONLY store information in long-term memory when you explicitly tell it to "remember" something.** This is a deliberate safety feature:

```
❌ Casual mention: "I like pizza"
   → Not stored automatically

✅ Explicit request: "Remember that I like pizza"
   → Stored in long-term memory
```

**Why this matters:**
- **Privacy Protection**: Prevents accidental storage of sensitive information
- **User Control**: You decide exactly what gets remembered permanently
- **Intentional Memory**: Only important facts you want recalled later are stored
- **Fool-Proof Design**: No surprises about what information persists

---

## 💡 Best Practices

### **Always Use "Remember" Commands**

**Critical:** Jarvis only stores information when you explicitly use "remember" commands:

✅ **Correct:** "Remember that I like my steak medium-rare"
❌ **Won't be stored:** "I like my steak medium-rare" (casual mention)

✅ **Correct:** "Please remember that I work from home on Fridays"
❌ **Won't be stored:** "I work from home on Fridays" (just sharing information)

### **Be Explicit and Intentional**

### **Use Natural Language**

✅ **Good:** "Remember that I work from home on Fridays"
✅ **Good:** "Please store this: I'm vegetarian"
✅ **Good:** "Don't forget that I have a cat named Whiskers"

### **Organize Information Logically**

```
"Remember my food preferences: I'm vegetarian and allergic to nuts"
"Remember my work schedule: I work from home on Fridays and have team meetings on Mondays at 10 AM"
"Remember my family: I have two kids, Emma (8) and Jake (12)"
```

---

## 🎯 Example Conversations

### **Setting Up Preferences**

```
You: "Hey Jarvis, I want you to remember some things about me"
Jarvis: "Of course! What would you like me to remember?"

You: "Remember that I like my coffee iced, not hot"
Jarvis: "I've committed that to my long-term memory: 'I like my coffee iced, not hot'"

You: "Also remember that I'm a morning person and prefer to work out at 6 AM"
Jarvis: "I've committed that to my long-term memory: 'I'm a morning person and prefer to work out at 6 AM'"

You: "And remember that I have a standing meeting with my team every Wednesday at 2 PM"
Jarvis: "I've committed that to my long-term memory: 'I have a standing meeting with my team every Wednesday at 2 PM'"
```

### **Retrieving Information Later**

```
[Different conversation, days later]

You: "What do you know about my beverage preferences?"
Jarvis: "I remember that you like your coffee iced, not hot."

You: "What about my exercise routine?"
Jarvis: "I remember that you're a morning person and prefer to work out at 6 AM."

You: "Do I have any regular meetings?"
Jarvis: "I remember that you have a standing meeting with your team every Wednesday at 2 PM."
```

### **Contextual Conversation**

```
You: "What time is it?"
Jarvis: "It's 3:45 PM"

You: "Is that before or after my team meeting?"
Jarvis: "That's after your team meeting. I remember you have a standing meeting with your team every Wednesday at 2 PM, so 3:45 PM would be after that meeting."
```

---

## 🔧 Technical Details

### **Memory Persistence**

- **Long-term memories** survive app restarts, computer reboots, and system updates
- **Short-term memory** clears when you end a conversation or start a new session
- Memories are stored locally on your device (not in the cloud)

### **Search Capabilities**

- **Semantic Search**: Finds information by meaning, not just exact words
- **Example**: Asking "food preferences" will find memories about "vegetarian" and "allergies"

### **Memory Limits**

- No practical limit on stored memories
- Each memory is chunked and indexed for efficient retrieval
- Older memories remain accessible indefinitely

### **Debug Tools (Development Mode)**

When Jarvis is running in debug mode, additional tools are available:

- **"View all long-term memories"** - Shows all stored facts
- **"Get memory statistics"** - Displays usage statistics and memory breakdown

---

## 🚨 Troubleshooting

### **"No relevant information found"**

If Jarvis says this, it means:
- You haven't asked it to remember that information yet
- The information might be stored with different wording
- Try rephrasing your question

### **Information Not Persisting**

**Most common issue:** You mentioned something but didn't use a "remember" command.

- ❌ **Problem:** "I told Jarvis I like coffee, but it doesn't remember"
- ✅ **Solution:** Use explicit commands: "Remember that I like coffee"
- **Key Point:** Casual mentions are never stored automatically
- **This is intentional:** Protects your privacy and gives you full control

### **PII Warnings**

- These are protective warnings, not errors
- Information is still stored if you confirm
- Consider if sensitive information should really be stored

---

## 🎉 Getting Started

1. **Start a conversation** with "Hey Jarvis"
2. **Tell Jarvis to remember** a few key facts about yourself
3. **End the conversation** and start a new one later
4. **Ask Jarvis** what it remembers about you
5. **Enjoy** having an AI assistant that actually remembers!

---

*This guide covers Stage 1 of the RAG memory system. Future updates will include document ingestion and advanced memory management features.*
