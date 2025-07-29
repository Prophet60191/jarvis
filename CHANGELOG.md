# Jarvis Voice Assistant - Changelog

All notable changes to the Jarvis Voice Assistant project are documented in this file.

## [2.1.0] - 2025-07-28 - Desktop Application Management & User Personalization

### 🎉 Major Features Added

#### Desktop Application Management System
- **Robust Application Manager** (`jarvis/jarvis/utils/app_manager.py`)
  - Complete lifecycle management for desktop applications
  - Process group management with `start_new_session=True`
  - Graceful termination with SIGTERM, force kill fallback with SIGKILL
  - Thread-safe operations with locks and atomic state changes
  - Comprehensive error handling and logging

- **Enhanced Desktop Applications**
  - Added proper signal handlers to `rag_app.py` and `jarvis_settings_app.py`
  - Implemented `webview.destroy()` cleanup before exit
  - Fixed zombie process issues and resource cleanup
  - Applications now respond to termination signals properly

#### User Profile & Personalization System
- **User Profile Management** (`jarvis/jarvis/core/user_profile.py`)
  - Persistent storage of user name, preferred name, and pronouns
  - Privacy-conscious design with user-controlled data storage
  - JSON-based profile storage in `~/.jarvis/user_profile.json`
  - Support for privacy levels: minimal, standard, full

- **Voice Commands for Profile Management** (`jarvis/jarvis/tools/plugins/user_profile_tool.py`)
  - `set_my_name()` - "My name is John", "Call me Sarah"
  - `get_my_name()` - "What's my name?", "Do you know my name?"
  - `set_my_pronouns()` - "My pronouns are he/him"
  - `show_my_profile()` - "Show my profile", "What do you know about me?"
  - `enable_name_usage()` / `disable_name_usage()` - Privacy controls
  - `clear_my_profile()` - "Clear my profile"

### 🔧 Major Fixes

#### Desktop Application Issues
- **Fixed App Reopening Problem**: Desktop apps can now be opened and closed repeatedly without issues
- **Resolved Settings Path Issues**: Fixed incorrect path calculation for `jarvis_settings_app.py`
- **Enhanced Process Cleanup**: Proper cleanup of background processes and webview resources
- **Improved Error Handling**: Better error messages and fallback mechanisms

#### Tool System Improvements
- **Fixed Import Errors**: Resolved relative import issues in plugin tools
- **Enhanced Path Resolution**: Robust path finding algorithm for application location
- **Fallback Mechanisms**: Tools work even when some components are unavailable
- **Better Error Recovery**: Graceful degradation when systems are unavailable

### 🆕 New Files Added

#### Core System Files
- `jarvis/jarvis/utils/app_manager.py` - Application lifecycle manager
- `jarvis/jarvis/core/user_profile.py` - User profile management system
- `jarvis/jarvis/tools/plugins/user_profile_tool.py` - Profile voice commands

#### Setup and Management Scripts
- `setup_user_profile.py` - Interactive user profile setup
- `Launch_Jarvis.py` - Enhanced startup script with environment checks
- `Start_Jarvis.py` - Basic startup script for desktop
- `start_jarvis.sh` - Shell script launcher for macOS/Linux

#### Documentation
- `docs/DESKTOP_APPLICATIONS.md` - Complete desktop applications guide
- `docs/APPLICATION_MANAGER.md` - Application lifecycle management documentation
- `docs/USER_PROFILE_SYSTEM.md` - User personalization system guide

#### Testing and Debug Scripts
- `test_user_profile.py` - User profile system testing
- `test_robust_app_management.py` - Application management testing
- `debug_tool_loading.py` - Tool loading diagnostics

### 📝 Modified Files

#### Core Application Files
- `jarvis/jarvis/core/agent.py` - Added personalization to system prompt
- `jarvis/jarvis/config.py` - Added user profile configuration options
- `jarvis/jarvis/tools/plugins/rag_plugin.py` - Excluded names from PII filtering

#### Desktop Applications
- `rag_app.py` - Added signal handlers and proper shutdown
- `jarvis/jarvis_settings_app.py` - Added signal handlers and proper shutdown

#### Tool Plugins
- `jarvis/jarvis/tools/plugins/rag_ui_tool.py` - Enhanced with robust app manager
- `jarvis/jarvis/tools/plugins/jarvis_ui_tool.py` - Enhanced with robust app manager

#### Documentation
- `README.md` - Updated with new features and current status
- `ARCHITECTURE.md` - Added new components and recent improvements

### 🎯 Voice Commands Added

#### Desktop Application Control
- "Open vault" / "Close vault" - Knowledge vault management
- "Open settings" / "Close settings" - Settings panel control
- "Open vault upload" - Open vault with specific panel
- "Open settings audio" - Open settings with specific panel

#### User Profile Management
- "My name is [name]" - Set your name
- "Call me [nickname]" - Set preferred name
- "What's my name?" - Get stored name
- "My pronouns are [pronouns]" - Set pronouns
- "Show my profile" - Display profile information
- "Allow Jarvis to use my name" - Enable name usage
- "Don't use my name" - Disable name usage
- "Clear my profile" - Remove all profile data

### 🔒 Privacy & Security Improvements

#### Name Storage Policy
- **Names NOT Treated as PII**: Names are explicitly excluded from PII filtering
- **User-Controlled Storage**: Full control over what information is stored
- **Transparent Data Handling**: Clear indication of what data is stored and how it's used
- **Easy Data Removal**: Simple commands to clear all stored information

#### Privacy Controls
- **Privacy Levels**: Configurable levels (minimal, standard, full)
- **Granular Controls**: Separate controls for different types of information
- **Consent-Based**: Explicit user consent for information storage
- **Audit Trail**: Timestamps for profile creation and updates

### ⚙️ Configuration Enhancements

#### Environment Variables Added
```bash
JARVIS_ENABLE_USER_PROFILE=true    # Enable user profile system
JARVIS_ALLOW_NAME_STORAGE=true     # Allow name storage
JARVIS_PRIVACY_LEVEL=standard      # Set privacy level
```

#### Configuration Options Added
- `enable_user_profile: bool = True`
- `allow_name_storage: bool = True`
- `privacy_level: str = "standard"`

### 🧪 Testing & Quality Assurance

#### New Test Scripts
- Comprehensive testing of user profile system
- Application lifecycle management testing
- Tool loading and import error testing
- Path resolution validation

#### Debug Tools
- Enhanced diagnostic scripts for troubleshooting
- Tool loading verification
- Process management debugging
- Profile system validation

### 📚 Documentation Improvements

#### New Documentation
- Complete desktop applications guide with troubleshooting
- Application manager system documentation with examples
- User profile system guide with privacy information
- Updated architecture documentation with new components

#### Enhanced Existing Docs
- Updated README with current status and new features
- Enhanced architecture documentation with recent improvements
- Added comprehensive changelog (this file)

### 🔄 Migration Notes

#### For Existing Users
1. **No Breaking Changes**: All existing functionality preserved
2. **Optional Features**: New features are opt-in and don't affect existing workflows
3. **Automatic Migration**: Profile system initializes automatically on first use
4. **Backward Compatibility**: All existing voice commands continue to work

#### For Developers
1. **New APIs Available**: User profile and application management APIs
2. **Enhanced Tool Development**: Better error handling and fallback mechanisms
3. **Improved Testing**: New testing utilities and debug tools
4. **Documentation**: Comprehensive guides for new systems

### 🎯 Performance Improvements

#### Application Management
- **Faster Startup**: Improved application launch times
- **Better Resource Management**: Proper cleanup prevents resource leaks
- **Reduced Memory Usage**: Elimination of zombie processes
- **Improved Reliability**: Consistent behavior across multiple open/close cycles

#### Tool System
- **Better Error Handling**: Graceful degradation instead of failures
- **Improved Loading**: Enhanced plugin loading with better error recovery
- **Reduced Latency**: Faster tool execution with optimized imports

### 🐛 Bug Fixes

#### Critical Fixes
- **Desktop Apps Not Reopening**: Fixed apps hanging after first close
- **Settings App Path Issues**: Corrected path resolution for settings application
- **Zombie Processes**: Eliminated background processes that wouldn't terminate
- **Import Errors**: Fixed relative import issues in plugin system

#### Minor Fixes
- **Tool Loading Errors**: Better error handling for missing dependencies
- **Path Resolution**: More robust file and directory location
- **Signal Handling**: Proper cleanup on application termination
- **Memory Leaks**: Fixed resource cleanup in desktop applications

---

## [2.0.0] - 2025-07-27 - RAG Memory System & Plugin Architecture

### Major Features
- RAG Memory System with ChromaDB
- Plugin-based architecture with zero built-in tools
- Dual memory system (short-term + long-term)
- PII protection and semantic search

### Core Changes
- Complete rewrite of memory system
- Migration from MCP memory tools to RAG tools
- Dynamic plugin loading system
- Enhanced user experience with contextual messages

---

## Previous Versions

For changes prior to version 2.0.0, please refer to the git commit history or previous documentation versions.

---

## Version Numbering

This project follows [Semantic Versioning](https://semver.org/):
- **MAJOR** version for incompatible API changes
- **MINOR** version for new functionality in a backwards compatible manner
- **PATCH** version for backwards compatible bug fixes

## Contributing

When contributing to this project, please:
1. Update this changelog with your changes
2. Follow the existing format and categorization
3. Include both user-facing and developer-facing changes
4. Add migration notes for breaking changes
