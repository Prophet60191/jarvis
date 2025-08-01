# 🏗️ Jarvis Architecture Documentation

## 🎯 **Core Design Principles**

### **1. True Separation of Concerns**
- **Independent Components**: Core system, plugins, UIs, and integrations operate independently
- **Fault Isolation**: Component failures don't cascade to other parts
- **Clean Interfaces**: Well-defined boundaries between all system components
- **Modular Development**: Each component can be developed, tested, and deployed separately

### **2. Zero Built-in Functionality**
- **No hard-coded tools** in the core application (even time queries are plugins)
- **Everything is plugin-based** for maximum flexibility and customization
- **Hot-swappable components** without system restarts
- **User control** over all functionality and system behavior

### **3. Plugin-First Architecture**
- **Single tool source**: Plugin system handles all functionality
- **Dynamic discovery**: Tools automatically loaded from plugins directory
- **Clean separation**: Core app focuses on conversation orchestration only
- **Unlimited extensibility**: Add tools without touching core code

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
│  │   Time Plugin   │  │ Desktop Apps    │  │ RAG Memory  │ │
│  │                 │  │ Management      │  │ System      │ │
│  │ • get_current   │  │ • open_vault    │  │ • remember  │ │
│  │   _time         │  │ • close_vault   │  │   _fact     │ │
│  │                 │  │ • open_settings │  │ • search_   │ │
│  │                 │  │ • close_settings│  │   long_term │ │
│  │                 │  │                 │  │   _memory   │ │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │ User Profile    │  │ Application     │  │ Custom      │ │
│  │ Management      │  │ Lifecycle       │  │ Plugins     │ │
│  │ • set_my_name   │  │ Manager         │  │ • [User     │ │
│  │ • get_my_name   │  │ • Process       │  │   Defined]  │ │
│  │ • set_pronouns  │  │   Groups        │  │             │ │
│  │ • show_profile  │  │ • Signal        │  │             │ │
│  │ • privacy_ctrl  │  │   Handling      │  │             │ │
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

## 🏗️ **Service Layer Architecture**

### **Clean Abstraction Layers:**
```
┌─────────────────────────────────────────┐
│           Presentation Layer            │
│  • OptimizedController                  │
│  • ConversationManager                  │
└─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────┐
│            Service Layer                │
│  • MemoryService (unified memory ops)  │
│  • ToolService (tool management)       │
│  • PerformanceService (monitoring)     │
└─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────┐
│           Business Logic Layer          │
│  • RAG Tools (memory operations)       │
│  • Tool Selection Managers             │
│  • Performance Monitors                │
└─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────┐
│            Data Layer                   │
│  • ChromaDB (vector storage)           │
│  • Configuration (settings)            │
│  • Plugin System (extensibility)       │
└─────────────────────────────────────────┘
```

### **Service Layer Benefits:**
- ✅ **Dependency Injection**: Clean separation of concerns
- ✅ **Interface Abstraction**: Consistent APIs across services
- ✅ **Backward Compatibility**: Existing functionality preserved
- ✅ **Testability**: Services can be mocked and tested independently
- ✅ **Maintainability**: Changes isolated to service implementations

## 🎯 **Benefits of Current Architecture**

### **For Users:**
- ✅ **Complete Control**: Enable/disable any functionality
- ✅ **Persistent Memory**: Information survives across sessions
- ✅ **Natural Interaction**: Simple "remember", "search", and "forget" commands
- ✅ **Privacy Protection**: PII detection and warnings
- ✅ **Performance Monitoring**: Real-time performance feedback

### **For Developers:**
- ✅ **No Core Changes**: Add tools by dropping plugin files
- ✅ **Hot Reloading**: Modify tools without app restarts
- ✅ **Clean Architecture**: Service layer abstraction
- ✅ **Easy Testing**: Services and tools can be tested independently
- ✅ **Professional Patterns**: Dependency injection, factory patterns, singletons

### **For System:**
- ✅ **Scalable**: Add unlimited tools without performance impact
- ✅ **Maintainable**: Clear separation of concerns
- ✅ **Flexible**: Support for multiple tool sources (plugins + MCP)
- ✅ **Robust**: Fallback mechanisms for tool failures

## 🆕 **Recent Architectural Improvements (July 2025)**

### **Desktop Application Management**
- **Robust Lifecycle System**: Complete process management with signal handling
- **Application Manager**: Centralized control for desktop app startup/shutdown
- **Process Groups**: Proper isolation and cleanup of background processes
- **Signal Handling**: Graceful termination with SIGTERM/SIGINT support
- **Path Resolution**: Dynamic path finding for reliable app location

### **User Personalization System**
- **Profile Management**: Persistent storage of user name, pronouns, preferences
- **Privacy-Conscious Design**: Names excluded from PII filtering, user-controlled storage
- **Voice Integration**: Natural language commands for profile management
- **System Integration**: Personalized responses using stored user information

### **Enhanced Tool Reliability**
- **Import Error Handling**: Graceful degradation when components unavailable
- **Fallback Mechanisms**: Multiple layers of error recovery
- **Path Robustness**: Dynamic resolution of application and resource paths
- **Thread Safety**: Lock-based synchronization for concurrent operations

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
