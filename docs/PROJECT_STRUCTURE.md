# 📁 Jarvis Project Structure

**Clean, Organized RAG-Powered Voice Assistant**

## 🏗️ Root Directory Structure

```
jarvis/
├── 📦 CORE PACKAGE
│   └── jarvis/                    # Main Python package
│       ├── audio/                 # Audio processing (TTS, STT, Wake Word)
│       ├── core/                  # Core system components
│       ├── plugins/               # Plugin system and registry
│       ├── tools/                 # RAG service and tool plugins
│       ├── ui/                    # User interface components
│       ├── utils/                 # Utility functions
│       ├── voices/                # Voice presets and audio data
│       ├── config.py              # Configuration management
│       ├── exceptions.py          # Custom exceptions
│       └── main.py                # Main application entry point
│
├── 📚 DOCUMENTATION
│   └── docs/                      # All documentation
│       ├── RAG_POWERED_ARCHITECTURE.md  # Current architecture
│       ├── PROJECT_STRUCTURE.md         # This file
│       ├── QUICK_START_CURRENT.md       # Getting started guide
│       ├── PLUGIN_REFERENCE_GUIDE.md    # Plugin development
│       └── [Other guides...]            # Additional documentation
│
├── 🧪 TESTING
│   └── tests/                     # All test files
│       ├── unit/                  # Unit tests
│       ├── integration/           # Integration tests
│       ├── robot/                 # Robot Framework tests
│       ├── fixtures/              # Test fixtures
│       └── manual/                # Manual test scripts
│
├── 🔧 SCRIPTS
│   └── scripts/                   # Utility scripts
│       ├── startup/               # Startup scripts (start_*.py, *.sh, *.bat)
│       ├── setup/                 # Setup and installation scripts
│       ├── debug/                 # Debug and diagnostic scripts
│       ├── testing/               # Testing utilities and MCP tests
│       └── robot_framework/       # Robot Framework setup
│
├── 📝 EXAMPLES
│   └── examples/                  # Usage examples
│       └── basic_usage.py         # Basic usage demonstration
│
├── 🔌 PLUGINS
│   └── plugins/                   # External plugin examples
│       └── example_plugin.py      # Plugin development example
│
├── 💾 DATA
│   └── data/                      # Runtime data
│       ├── backups/               # RAG system backups
│       ├── chat_sessions/         # Conversation history
│       ├── chroma_db/             # Vector database
│       └── documents/             # Document storage
│
├── 📊 LOGS
│   └── logs/                      # Application logs
│
├── 🎵 AUDIO
│   └── audio/                     # Audio files and resources
│
├── 🌐 PUBLIC
│   └── public/                    # Public web assets
│
└── 📋 PROJECT FILES
    ├── README.md                  # Project overview
    ├── CHANGELOG.md               # Version history
    ├── CONTRIBUTING.md            # Contribution guidelines
    ├── requirements.txt           # Python dependencies
    ├── pyproject.toml             # Project configuration
    ├── .env.example               # Environment variables template
    └── .gitignore                 # Git ignore rules
```

## 🧠 Core Package Structure

### `jarvis/core/` - System Core
```
core/
├── orchestration/                 # RAG-Powered Workflow System
│   ├── rag_powered_workflow.py   # 🧠 Main RAG workflow builder
│   ├── unified_integration.py    # 🔗 Agent integration layer
│   └── __init__.py               # Clean exports
├── context/                      # Context management
├── consciousness/                # Self-awareness system
├── browser/                      # Web automation
├── analytics/                    # Usage analytics
├── monitoring/                   # Performance monitoring
├── performance/                  # Performance optimization
├── routing/                      # Legacy (empty)
├── agent.py                      # LLM agent management
├── conversation.py               # Conversation handling
├── speech.py                     # Speech processing
├── wake_word.py                  # Wake word detection
└── [Other core modules...]
```

### `jarvis/plugins/` - Plugin System
```
plugins/
├── registry/                     # Plugin registry system
│   ├── unified_registry.py      # 🗂️ Dynamic plugin discovery
│   ├── capability_analyzer.py   # Plugin capability analysis
│   ├── relationship_mapper.py   # Plugin relationships
│   └── usage_analytics.py       # Plugin usage tracking
├── manager.py                    # Plugin management
├── base.py                       # Plugin base classes
└── enhanced_manager.py           # Enhanced plugin features
```

### `jarvis/tools/` - RAG & Tools
```
tools/
├── plugins/                      # 101+ Dynamic plugins
│   ├── aider_integration.py     # Code generation
│   ├── rag_plugin.py            # RAG system tools
│   ├── lavague_web_automation.py # Web automation
│   ├── robot_framework_controller.py # Testing
│   └── [98+ other plugins...]
├── rag_service.py               # 🧠 RAG intelligence core
├── open_interpreter_direct.py   # 🔧 Code execution
├── database_agent.py            # Data management
├── rag_backup_manager.py        # Backup management
├── rag_config_manager.py        # Configuration
└── [Other tool modules...]
```

## 🎯 Key Features of Clean Structure

### ✅ Benefits Achieved:
- **🗂️ Organized**: Everything in its proper place
- **🧹 Clean**: No duplicate directories or scattered files
- **📚 Documented**: Clear structure documentation
- **🔍 Discoverable**: Easy to find any component
- **🚀 Scalable**: Room for growth without clutter

### 🎪 From Chaos to Order:
- **Before**: 30+ files scattered in root directory
- **After**: Organized into logical directories
- **Before**: Duplicate directories (tools/, ui/, voices/)
- **After**: Single source of truth in jarvis/ package
- **Before**: Mixed test files everywhere
- **After**: All tests in tests/ directory
- **Before**: Scripts scattered around
- **After**: All scripts organized in scripts/ subdirectories

## 🚀 Navigation Guide

### For Developers:
- **Core Logic**: `jarvis/core/orchestration/`
- **Plugin Development**: `jarvis/plugins/` + `docs/PLUGIN_REFERENCE_GUIDE.md`
- **RAG System**: `jarvis/tools/rag_service.py`
- **Testing**: `tests/` directory

### For Users:
- **Getting Started**: `docs/QUICK_START_CURRENT.md`
- **Architecture**: `docs/RAG_POWERED_ARCHITECTURE.md`
- **Examples**: `examples/basic_usage.py`

### For Contributors:
- **Contributing**: `CONTRIBUTING.md`
- **Project Structure**: This file
- **Development Setup**: `scripts/setup/`

---

**This clean, organized structure reflects our evolution from a complex, scattered codebase to a professional, maintainable RAG-powered system.** 🎉
