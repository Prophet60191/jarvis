# Jarvis Tool Development Guide

This guide provides comprehensive instructions for creating tools that integrate with the Jarvis AI assistant using our MCP (Model Context Protocol) plugin system.

## Overview

Jarvis tools are Python functions that extend the assistant's capabilities using LangChain's `@tool` decorator and our MCP plugin architecture. Tools are automatically discovered and loaded without requiring changes to the core codebase.

## Tool Architecture

### Core Components

1. **LangChain @tool Decorator**: Defines tool function with automatic parameter handling
2. **Plugin Metadata**: Provides plugin information for automatic discovery
3. **Plugin Class**: Optional container for complex tools with lifecycle management
4. **Automatic Discovery**: MCP system finds and loads plugins automatically

### ⚠️ **CRITICAL: Function Name = Tool Name**

**The function name becomes the tool name automatically.** This is how LangChain's `@tool` decorator works:

```python
@tool
def get_current_time() -> str:  # Tool name will be "get_current_time"
    """Gets the current time."""
    return "Current time..."

@tool
def calculate_sum(a: int, b: int) -> int:  # Tool name will be "calculate_sum"
    """Calculates sum of two numbers."""
    return a + b
```

**Best Practices for Function Naming:**
- Use descriptive, clear function names
- Avoid generic names like `get_time()` - use `get_current_time()`
- Follow snake_case convention
- Make names unique to avoid conflicts

## Quick Start

### 1. Generate a Plugin Template

```bash
# Generate a new plugin with tools
python manage_plugins.py generate my_tool --type tool --author "Your Name" --description "My awesome tool"
```

### 2. Simple Tool Example

```python
"""
My Tool Plugin for Jarvis Voice Assistant.

Author: Your Name
"""

import logging
from typing import List
from langchain_core.tools import BaseTool, tool

from jarvis.plugins.base import PluginBase, PluginMetadata

logger = logging.getLogger(__name__)

@tool
def my_awesome_tool(query: str, count: int = 1) -> str:
    """
    Perform an awesome operation on the query.
    
    Args:
        query: The input text to process
        count: Number of times to process (default: 1)
        
    Returns:
        str: Processed result
    """
    try:
        result = f"Processed '{query}' {count} times"
        logger.info(f"Tool executed successfully: {result}")
        return result
    except Exception as e:
        logger.error(f"Tool error: {e}")
        return f"Error: {str(e)}"

class MyToolPlugin(PluginBase):
    """My Tool plugin for Jarvis."""
    
    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="MyTool",
            version="1.0.0",
            description="My awesome tool plugin",
            author="Your Name"
        )
    
    def get_tools(self) -> List[BaseTool]:
        return [my_awesome_tool]

# Plugin discovery
PLUGIN_CLASS = MyToolPlugin
PLUGIN_METADATA = MyToolPlugin().get_metadata()
```

### 3. Save and Test

1. **CRITICAL**: Save the file as `jarvis/tools/plugins/my_tool.py`
   - ✅ **Correct**: `jarvis/tools/plugins/my_tool.py` (inside jarvis package)
   - ❌ **Wrong**: `tools/plugins/my_tool.py` (project root)
   - The plugin discovery system looks in `jarvis/tools/plugins/` first

2. Test: `python manage_plugins.py list`
3. Load: `python manage_plugins.py load MyTool`

### ⚠️ **File Location is Critical**

The MCP plugin discovery system searches these directories in order:
1. `jarvis/tools/plugins/` ← **Put your plugins here**
2. `jarvis/plugins/builtin/`
3. `~/.jarvis/plugins/`
4. `./plugins/`

**Always use `jarvis/tools/plugins/` for your custom tools.**

## Advanced Tool Development

### Multiple Tools in One Plugin

```python
@tool
def tool_one(text: str) -> str:
    """First tool function."""
    return f"Tool 1 processed: {text}"

@tool  
def tool_two(number: int) -> str:
    """Second tool function."""
    return f"Tool 2 calculated: {number * 2}"

class MultiToolPlugin(PluginBase):
    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="MultiTool",
            version="1.0.0", 
            description="Plugin with multiple tools",
            author="Your Name"
        )
    
    def get_tools(self) -> List[BaseTool]:
        return [tool_one, tool_two]
```

### Tool with Complex Parameters

```python
from typing import Optional, List, Union
from enum import Enum

class ProcessingMode(str, Enum):
    FAST = "fast"
    ACCURATE = "accurate"
    BALANCED = "balanced"

@tool
def advanced_tool(
    text: str,
    mode: ProcessingMode = ProcessingMode.BALANCED,
    options: Optional[List[str]] = None,
    threshold: float = 0.5
) -> str:
    """
    Advanced tool with complex parameters.
    
    Args:
        text: Input text to process
        mode: Processing mode (fast, accurate, balanced)
        options: Optional list of processing options
        threshold: Confidence threshold (0.0-1.0)
        
    Returns:
        str: Processed result
    """
    if options is None:
        options = []
    
    result = f"Processed '{text}' in {mode.value} mode"
    if options:
        result += f" with options: {', '.join(options)}"
    result += f" (threshold: {threshold})"
    
    return result
```

## Plugin Types

### 1. Basic Plugin (Minimal Setup)

```python
from langchain_core.tools import tool
from jarvis.plugins.base import PluginMetadata

@tool
def simple_tool(input_text: str) -> str:
    """A simple standalone tool."""
    return f"Processed: {input_text}"

# Standalone tool discovery
PLUGIN_METADATA = PluginMetadata(
    name="SimpleTool",
    version="1.0.0",
    description="A simple tool",
    author="Your Name",
    tools=[simple_tool]
)
```

### 2. Tool Plugin (Recommended)

```python
from jarvis.plugins.base import PluginBase, PluginMetadata

class MyToolPlugin(PluginBase):
    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="MyTool",
            version="1.0.0",
            description="My tool plugin",
            author="Your Name"
        )
    
    def get_tools(self) -> List[BaseTool]:
        return [my_tool_function]

PLUGIN_CLASS = MyToolPlugin
PLUGIN_METADATA = MyToolPlugin().get_metadata()
```

### 3. Advanced Plugin (Full Features)

```python
class AdvancedPlugin(PluginBase):
    def __init__(self):
        super().__init__()
        self.config = {}
        self.resources = {}
    
    def initialize(self) -> None:
        super().initialize()
        # Setup resources, connections, etc.
        self.resources['cache'] = {}
    
    def cleanup(self) -> None:
        # Clean up resources
        self.resources.clear()
        super().cleanup()
    
    def configure(self, config: Dict[str, Any]) -> None:
        self.config.update(config)
    
    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="AdvancedTool",
            version="1.0.0",
            description="Advanced plugin with lifecycle management",
            author="Your Name",
            dependencies=["requests", "beautifulsoup4"],
            config_schema={
                "type": "object",
                "properties": {
                    "api_key": {"type": "string"},
                    "timeout": {"type": "number", "default": 30}
                }
            }
        )
```

## Best Practices

### 1. Error Handling

```python
@tool
def robust_tool(input_data: str) -> str:
    """Tool with proper error handling."""
    try:
        if not input_data or not input_data.strip():
            return "Error: Input cannot be empty"
        
        # Process data
        result = process_data(input_data)
        
        if not result:
            return "Warning: No results found"
        
        return f"Success: {result}"
        
    except ValueError as e:
        logger.warning(f"Invalid input: {e}")
        return f"Invalid input: {str(e)}"
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return f"Tool error: {str(e)}"
```

### 2. Input Validation

```python
@tool
def validated_tool(email: str, age: int) -> str:
    """Tool with input validation."""
    # Validate email
    if "@" not in email or "." not in email:
        return "Error: Invalid email format"
    
    # Validate age
    if age < 0 or age > 150:
        return "Error: Age must be between 0 and 150"
    
    return f"Valid user: {email}, age {age}"
```

### 3. Documentation

```python
@tool
def well_documented_tool(query: str, format_type: str = "json") -> str:
    """
    Process a query and return formatted results.
    
    This tool processes text queries and returns results in the specified format.
    Supports multiple output formats for different use cases.
    
    Args:
        query: The search query or text to process. Should be non-empty.
        format_type: Output format - "json", "text", or "xml" (default: "json")
        
    Returns:
        str: Formatted results based on the query and format type
        
    Examples:
        >>> well_documented_tool("hello world", "text")
        "Processed: hello world"
        
        >>> well_documented_tool("data query", "json")
        '{"result": "data query", "status": "success"}'
    """
    # Implementation here
    pass
```

## Testing Tools

### 1. Manual Testing

```python
if __name__ == "__main__":
    # Test your tool directly
    result = my_tool("test input")
    print(f"Result: {result}")
```

### 2. Plugin Management

```bash
# List all plugins
python manage_plugins.py list --details

# Load specific plugin
python manage_plugins.py load MyTool

# Show plugin info
python manage_plugins.py info MyTool

# Reload during development
python manage_plugins.py reload MyTool
```

This guide covers the modern MCP-based approach for Jarvis tool development with automatic discovery and LangChain integration.
