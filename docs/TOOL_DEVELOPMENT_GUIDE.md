# Jarvis Tool Development Guide

This guide provides comprehensive instructions for creating tools that integrate with the Jarvis AI assistant using our MCP (Model Context Protocol) plugin system.

## Overview

Jarvis tools are Python functions that extend the assistant's capabilities using LangChain's `@tool` decorator and our MCP plugin architecture. Tools are automatically discovered and loaded without requiring changes to the core codebase.

### Recent Enhancements (July 2025)

- **Desktop Application Management**: Tools can now control desktop applications with robust lifecycle management
- **User Profile Integration**: Tools can access and use stored user information for personalization
- **Enhanced Error Handling**: Improved fallback mechanisms and graceful degradation
- **Application Manager API**: New APIs for managing desktop application processes

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

## Desktop Application Management

### Using the Application Manager

Tools can control desktop applications using the robust Application Manager:

```python
from langchain_core.tools import tool

# Import with error handling
try:
    from jarvis.utils.app_manager import get_app_manager
except ImportError:
    def get_app_manager():
        return None

@tool
def open_my_app(panel: str = "main") -> str:
    """Open a custom desktop application."""
    try:
        app_manager = get_app_manager()
        if app_manager:
            # Use robust manager
            app_manager.register_app(
                name="my_app",
                script_path="/path/to/my_app.py",
                args=["--panel", panel]
            )

            if app_manager.start_app("my_app"):
                return f"My App ({panel}) is now open."
            else:
                return "Failed to open My App."
        else:
            # Fallback to direct launch
            import subprocess
            subprocess.Popen(["python", "/path/to/my_app.py"])
            return "Opening My App..."
    except Exception as e:
        return f"Error: {str(e)}"

@tool
def close_my_app() -> str:
    """Close the custom desktop application."""
    try:
        app_manager = get_app_manager()
        if app_manager and app_manager.is_app_running("my_app"):
            if app_manager.stop_app("my_app"):
                return "My App closed successfully."
            else:
                return "Failed to close My App."
        else:
            return "My App is not running."
    except Exception as e:
        return f"Error: {str(e)}"
```

## User Profile Integration

### Accessing User Information

Tools can access stored user information for personalization:

```python
from langchain_core.tools import tool

# Import with error handling
try:
    from jarvis.core.user_profile import get_user_profile_manager
except ImportError:
    def get_user_profile_manager():
        return None

@tool
def personalized_greeting() -> str:
    """Provide a personalized greeting using stored user information."""
    try:
        manager = get_user_profile_manager()
        if manager:
            name = manager.get_name()
            pronouns = manager.get_pronouns()

            if name:
                greeting = f"Hello, {name}!"
                if pronouns:
                    greeting += f" I'll use {pronouns} pronouns when referring to you."
                return greeting
            else:
                return "Hello! I don't have your name stored yet. You can tell me by saying 'My name is...'"
        else:
            return "Hello there!"
    except Exception as e:
        return f"Hello! (Profile system unavailable: {str(e)})"

@tool
def check_user_preferences() -> str:
    """Check user's stored preferences and settings."""
    try:
        manager = get_user_profile_manager()
        if manager:
            profile = manager.get_profile()

            info = []
            if profile.name:
                info.append(f"Name: {profile.name}")
            if profile.pronouns:
                info.append(f"Pronouns: {profile.pronouns}")
            info.append(f"Privacy level: {profile.privacy_level}")

            if info:
                return "Your preferences:\n" + "\n".join(f"• {item}" for item in info)
            else:
                return "No preferences stored yet."
        else:
            return "User profile system not available."
    except Exception as e:
        return f"Error checking preferences: {str(e)}"
```

## Enhanced Error Handling

### Robust Tool Development

Modern tools should include comprehensive error handling:

```python
from langchain_core.tools import tool
import logging

logger = logging.getLogger(__name__)

@tool
def robust_tool_example(input_data: str) -> str:
    """Example of robust tool with comprehensive error handling."""
    try:
        # Validate input
        if not input_data or not input_data.strip():
            return "Error: Input data cannot be empty."

        # Try primary functionality
        try:
            from some_optional_library import process_data
            result = process_data(input_data)
            logger.info(f"Successfully processed data: {input_data}")
            return f"Processed: {result}"

        except ImportError:
            # Fallback when optional library unavailable
            logger.warning("Optional library not available, using fallback")
            result = input_data.upper()  # Simple fallback
            return f"Fallback processing: {result}"

        except Exception as e:
            # Handle processing errors
            logger.error(f"Processing error: {e}")
            return f"Processing failed: {str(e)}"

    except Exception as e:
        # Handle unexpected errors
        logger.error(f"Unexpected error in robust_tool_example: {e}")
        return f"Tool error: {str(e)}"
```

## Best Practices (Updated)

1. **Clear Documentation**: Write comprehensive docstrings with examples
2. **Error Handling**: Always handle exceptions gracefully with fallbacks
3. **Type Hints**: Use proper type annotations for all parameters
4. **Validation**: Validate inputs before processing
5. **Logging**: Use appropriate logging levels for debugging
6. **Testing**: Test tools thoroughly before deployment
7. **Performance**: Consider performance implications for long-running operations
8. **Fallback Mechanisms**: Provide graceful degradation when dependencies unavailable
9. **User Personalization**: Use stored user information when appropriate
10. **Resource Cleanup**: Properly clean up resources in desktop applications
11. **Import Safety**: Handle import errors gracefully with try/except blocks
12. **Path Resolution**: Use robust path finding for file and application locations

## See Also

- [Desktop Applications Guide](DESKTOP_APPLICATIONS.md) - Complete guide to desktop app management
- [Application Manager](APPLICATION_MANAGER.md) - Process lifecycle management documentation
- [User Profile System](USER_PROFILE_SYSTEM.md) - User personalization and profile management

This guide covers the modern MCP-based approach for Jarvis tool development with automatic discovery, LangChain integration, and enhanced system capabilities.
