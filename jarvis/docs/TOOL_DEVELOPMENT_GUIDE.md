# Jarvis Tool Development Guide

This guide provides comprehensive instructions for creating tools that integrate with the Jarvis AI assistant using our MCP (Model Context Protocol) plugin system.

## Overview

Jarvis tools are Python functions that extend the assistant's capabilities using LangChain's `@tool` decorator and our MCP plugin architecture. Tools are automatically discovered and loaded without requiring changes to the core codebase.

## Quick Start

### 1. Generate a Plugin Template

```bash
python manage_plugins.py generate my_tool --type tool --author "Your Name"
```

### 2. Simple Tool Example

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

### 3. Save and Test

1. Save as `jarvis/tools/plugins/my_tool.py`
2. Test: `python manage_plugins.py list`
3. Use in Jarvis - automatically available!

## Best Practices

- Use `@tool` decorator from `langchain_core.tools`
- Handle errors gracefully (return error strings)
- Document functions clearly
- Test with `manage_plugins.py` commands

For complete examples and advanced features, see the other documentation files.
