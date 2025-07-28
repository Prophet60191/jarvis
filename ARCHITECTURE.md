# 🏗️ Jarvis Architecture Documentation

## 🎯 **Core Design Principles**

### **1. Zero Built-in Tools**
- **No hard-coded functionality** in the core application
- **Everything is plugin-based** for maximum flexibility
- **Hot-swappable tools** without app restarts
- **User control** over all functionality

### **2. Plugin-First Architecture**
- **Single tool source**: Plugin system handles all functionality
- **Dynamic discovery**: Tools automatically loaded from plugins directory
- **Clean separation**: Core app focuses on conversation, tools are external
- **Extensible**: Add unlimited tools without touching core code

### **3. Dual Memory System**
- **Short-term memory**: Current conversation context (clears between sessions)
- **Long-term memory**: Persistent facts stored in ChromaDB vector database
- **Semantic search**: Find information by meaning, not just keywords
- **User control**: Explicit "remember" commands for data storage

## 🏗️ **System Architecture**

```
┌─────────────────────────────────────────────────────────────┐
│                    Jarvis Core Application                  │
│                  (Zero Built-in Tools)                     │
├─────────────────────────────────────────────────────────────┤
│  • Conversation Management                                  │
│  • Speech Recognition & Synthesis                          │
│  • Agent Orchestration                                     │
│  • Configuration Management                                │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Plugin System                           │
│                 (Dynamic Tool Loading)                     │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │   Time Plugin   │  │  UI Control     │  │ RAG Memory  │ │
│  │                 │  │  Plugins        │  │ System      │ │
│  │ • get_current   │  │ • open_jarvis   │  │ • remember  │ │
│  │   _time         │  │   _ui           │  │   _fact     │ │
│  │                 │  │ • close_jarvis  │  │ • search_   │ │
│  │                 │  │   _ui           │  │   long_term │ │
│  │                 │  │ • show_status   │  │   _memory   │ │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                MCP Integration Layer                        │
│               (External Services)                          │
├─────────────────────────────────────────────────────────────┤
│  • GitHub Integration                                       │
│  • File System Tools                                       │
│  • External APIs                                           │
│  • Third-party Services                                    │
└─────────────────────────────────────────────────────────────┘
```

## 🧠 **RAG Memory System**

### **Architecture:**
```
User Input: "Remember that I like coffee"
                    │
                    ▼
┌─────────────────────────────────────────┐
│           Agent Processing              │
│  • Detects "remember" command          │
│  • Routes to remember_fact tool        │
└─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────┐
│         RAG Tools Layer                 │
│  • PII Detection & Warning             │
│  • Input Validation                    │
│  • Tool Routing                        │
└─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────┐
│       RAG Memory Manager                │
│  • Text Chunking                       │
│  • Embedding Generation                │
│  • Vector Storage                      │
└─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────┐
│         ChromaDB Storage                │
│  • Persistent Vector Database          │
│  • Metadata Management                 │
│  • Semantic Search                     │
└─────────────────────────────────────────┘
```

### **Memory Types:**
1. **Short-term (Chat History)**:
   - Current conversation context
   - Pronouns and references
   - Clears between sessions

2. **Long-term (ChromaDB)**:
   - Explicitly stored facts
   - Survives app restarts
   - Semantic search enabled

## 🔧 **Tool Loading Process**

### **1. Plugin Discovery**
```python
def get_langchain_tools():
    tools = []
    
    # Auto-discover plugins (includes RAG, UI, time, etc.)
    plugin_tools = plugin_manager.get_all_tools()
    tools.extend(plugin_tools)
    
    # Add MCP integration tools (external services)
    mcp_tools = mcp_manager.get_langchain_tools()
    tools.extend(mcp_tools)
    
    return tools  # No built-in tools!
```

### **2. Plugin Structure**
```python
# Example: jarvis/tools/plugins/my_tool.py
from langchain_core.tools import tool
from jarvis.plugins.base import PluginBase, PluginMetadata

@tool
def my_awesome_function(query: str) -> str:
    """Tool description for the agent."""
    return f"Processed: {query}"

class MyToolPlugin(PluginBase):
    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="MyTool",
            version="1.0.0",
            description="My awesome tool",
            author="Developer"
        )
    
    def get_tools(self) -> List[BaseTool]:
        return [my_awesome_function]

# Required for auto-discovery
plugin = MyToolPlugin()
```

## 🎯 **Benefits of Current Architecture**

### **For Users:**
- ✅ **Complete Control**: Enable/disable any functionality
- ✅ **Persistent Memory**: Information survives across sessions
- ✅ **Natural Interaction**: Simple "remember" and "search" commands
- ✅ **Privacy Protection**: PII detection and warnings

### **For Developers:**
- ✅ **No Core Changes**: Add tools by dropping plugin files
- ✅ **Hot Reloading**: Modify tools without app restarts
- ✅ **Clean Architecture**: Each tool is self-contained
- ✅ **Easy Testing**: Tools can be tested independently

### **For System:**
- ✅ **Scalable**: Add unlimited tools without performance impact
- ✅ **Maintainable**: Clear separation of concerns
- ✅ **Flexible**: Support for multiple tool sources (plugins + MCP)
- ✅ **Robust**: Fallback mechanisms for tool failures

## 🚀 **Future Enhancements**

### **Stage 2: Document Ingestion**
- PDF, TXT, DOCX processing
- Document-based knowledge retrieval
- Source citation in responses

### **Stage 3: Memory Management UI**
- Visual memory browser
- Memory editing and deletion
- Usage statistics and analytics

### **Advanced Features**
- Proactive memory suggestions
- Conflict resolution for contradictory information
- Advanced PII protection and data governance
