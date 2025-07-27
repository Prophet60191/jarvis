# Jarvis MCP System Overview

This document provides an overview of the Model Context Protocol (MCP) system implemented in Jarvis for extensible tool development.

## What is MCP?

The Model Context Protocol (MCP) is a standardized approach for creating extensible AI systems that can be enhanced with new capabilities without modifying core code. Our implementation allows developers to add new tools to Jarvis through a plugin architecture.

## System Architecture

### Core Components

1. **Plugin Base** (`jarvis/plugins/base.py`)
   - `PluginBase`: Abstract base class for all plugins
   - `PluginMetadata`: Structured plugin information
   - Lifecycle management (initialize, cleanup)

2. **Plugin Discovery** (`jarvis/plugins/discovery.py`)
   - Automatic scanning of plugin directories
   - Multiple discovery methods (metadata, class, standalone tools)
   - Support for different plugin patterns

3. **Plugin Manager** (`jarvis/plugins/manager.py`)
   - Centralized plugin lifecycle management
   - Loading, unloading, reloading capabilities
   - Tool aggregation from all plugins

4. **Plugin Generator** (`jarvis/plugins/generator.py`)
   - Template-based plugin generation
   - Three plugin types: basic, tool, advanced
   - Automatic boilerplate code generation

5. **Plugin CLI** (`jarvis/plugins/cli.py`)
   - Command-line interface for plugin management
   - List, load, unload, reload, enable, disable commands

## Tool Development Workflow

### 1. Generate Plugin Template
```bash
python manage_plugins.py generate my_tool --type tool --author "Your Name"
```

### 2. Implement Tool Logic
```python
from langchain_core.tools import tool
from jarvis.plugins.base import PluginBase, PluginMetadata

@tool
def my_tool(query: str) -> str:
    """My awesome tool implementation."""
    return f"Processed: {query}"

class MyToolPlugin(PluginBase):
    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="MyTool",
            version="1.0.0",
            description="My awesome tool",
            author="Your Name"
        )
    
    def get_tools(self):
        return [my_tool]

PLUGIN_CLASS = MyToolPlugin
PLUGIN_METADATA = MyToolPlugin().get_metadata()
```

### 3. Test and Deploy
```bash
# List plugins
python manage_plugins.py list

# Load plugin
python manage_plugins.py load MyTool

# Use in Jarvis - automatically available!
```

## Plugin Types

### 1. Basic Plugin
- Minimal setup with standalone tools
- Direct `@tool` decorator usage
- Simple metadata definition

### 2. Tool Plugin (Recommended)
- Plugin class with proper structure
- Multiple tools per plugin
- Configuration support

### 3. Advanced Plugin
- Full lifecycle management
- Resource initialization/cleanup
- Dependency validation
- Configuration schema

## Integration with LangChain

Our MCP system seamlessly integrates with LangChain:

- Uses `@tool` decorator from `langchain_core.tools`
- **Function name becomes tool name automatically**
- Automatic parameter handling and validation
- Compatible with LangChain agent systems
- No manual tool registration required

### ⚠️ **Critical LangChain Integration Rules**

1. **Function Name = Tool Name**: LangChain uses the function name as the tool identifier
2. **Descriptive Naming**: Use clear, specific function names (e.g., `get_current_time` not `get_time`)
3. **Avoid Conflicts**: Generic names may conflict with other tools
4. **File Location**: Must be in `jarvis/tools/plugins/` for discovery

## Key Benefits

### For Developers
- **Zero Core Modification**: Add tools without changing main codebase
- **Template Generation**: Quick start with plugin templates
- **Automatic Discovery**: Plugins are found and loaded automatically
- **CLI Management**: Easy plugin management from command line

### For Users
- **Extensible**: Unlimited tool expansion capability
- **Modular**: Enable/disable tools as needed
- **Maintainable**: Clean separation between core and extensions
- **Reliable**: Proper error handling and resource management

## File Structure

```
jarvis/
├── plugins/                    # MCP system core
│   ├── __init__.py
│   ├── base.py                # Plugin base classes
│   ├── discovery.py           # Auto-discovery system
│   ├── manager.py             # Plugin lifecycle management
│   ├── generator.py           # Template generator
│   └── cli.py                 # Management CLI
├── tools/
│   ├── plugins/               # Plugin storage directory
│   │   ├── __init__.py
│   │   └── your_plugin.py     # Your plugins here
│   ├── __init__.py            # Integration with tool registry
│   └── base.py                # Legacy tool classes
└── manage_plugins.py          # Plugin management script
```

## Plugin Discovery Methods

The system supports multiple plugin discovery patterns:

1. **Plugin Class with Metadata**
   ```python
   PLUGIN_CLASS = MyPlugin
   PLUGIN_METADATA = MyPlugin().get_metadata()
   ```

2. **Standalone Metadata**
   ```python
   PLUGIN_METADATA = PluginMetadata(
       name="MyTool",
       tools=[my_tool_function]
   )
   ```

3. **Standalone Tools**
   - Automatic detection of `@tool` decorated functions
   - No explicit metadata required

## Configuration and Dependencies

Plugins can specify:
- **Dependencies**: Required Python packages
- **Configuration Schema**: JSON schema for plugin settings
- **Minimum Jarvis Version**: Compatibility requirements

## Error Handling

The MCP system includes comprehensive error handling:
- Plugin loading failures don't crash the system
- Individual tool errors are isolated
- Detailed logging for debugging
- Graceful degradation when plugins fail

## Future Extensibility

The MCP architecture is designed for future enhancements:
- Remote plugin loading
- Plugin marketplace integration
- Advanced dependency management
- Plugin sandboxing and security

## Migration from Legacy Tools

Existing tools can be migrated to the MCP system:
1. Wrap existing tool functions with `@tool` decorator
2. Create plugin metadata
3. Move to `jarvis/tools/plugins/` directory
4. Remove manual registration from `__init__.py`

## Best Practices

1. **Use Plugin Templates**: Start with generated templates
2. **Follow Naming Conventions**: Clear, descriptive plugin names
3. **Handle Errors Gracefully**: Return error strings, don't raise exceptions
4. **Document Thoroughly**: Clear tool descriptions and parameter docs
5. **Test Incrementally**: Use CLI tools for testing during development

This MCP system provides a robust, extensible foundation for Jarvis tool development while maintaining compatibility with existing LangChain-based tools.
