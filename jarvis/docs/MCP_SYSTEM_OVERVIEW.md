# Jarvis MCP System Overview

## What is MCP?

The Model Context Protocol (MCP) is our extensible plugin system that allows adding new tools to Jarvis without modifying core code.

## Key Components

1. **Plugin Manager** - Handles plugin lifecycle
2. **Plugin Discovery** - Automatically finds plugins
3. **Plugin Generator** - Creates plugin templates
4. **Plugin CLI** - Management commands

## Quick Commands

```bash
# Generate new plugin
python manage_plugins.py generate my_tool --type tool

# List all plugins
python manage_plugins.py list

# Load a plugin
python manage_plugins.py load MyTool
```

## File Structure

```
jarvis/
├── plugins/           # MCP system core
├── tools/plugins/     # Your plugins go here
└── manage_plugins.py  # Management script
```

## Benefits

- **Zero Core Changes**: Add tools without touching main code
- **Automatic Discovery**: Plugins load automatically
- **Template Generation**: Quick start with templates
- **CLI Management**: Easy plugin management

This system makes Jarvis infinitely extensible while keeping the core stable.
