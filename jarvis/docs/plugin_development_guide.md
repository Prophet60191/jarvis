# Jarvis Plugin Development Guide

## Overview

Jarvis uses a plugin architecture that allows you to extend functionality without modifying core code. Plugins are automatically discovered and loaded at startup, making it easy to add new tools and capabilities.

## Quick Start

### 1. Generate a Plugin Template

```bash
# Generate a new plugin
python manage_plugins.py generate my_plugin --type tool --author "Your Name"
```

### 2. Edit the Generated Plugin

The generated file will be in `jarvis/tools/plugins/my_plugin.py`:

```python
"""
My Plugin for Jarvis Voice Assistant.

Author: Your Name
"""

import logging
from typing import List
from langchain_core.tools import BaseTool, tool

from jarvis.plugins.base import PluginBase, PluginMetadata

logger = logging.getLogger(__name__)

@tool
def my_tool(message: str = "Hello") -> str:
    """
    A simple example tool that returns a greeting.

    IMPORTANT: The function name 'my_tool' becomes the tool name.
    Use descriptive names like 'get_weather', 'calculate_sum', etc.

    Args:
        message: The greeting message to return

    Returns:
        str: A formatted greeting message
    """
    return f"{message} from my plugin!"

class MyPlugin(PluginBase):
    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="MyPlugin",
            version="1.0.0",
            description="An example plugin",
            author="Your Name"
        )

    def get_tools(self) -> List[BaseTool]:
        return [my_tool]

# Plugin discovery
PLUGIN_CLASS = MyPlugin
PLUGIN_METADATA = MyPlugin().get_metadata()
```

### 3. Test Your Plugin

```bash
# List discovered plugins
python manage_plugins.py list

# Load your plugin
python manage_plugins.py load MyPlugin

# Test in Jarvis - your tool is now available!
```

## Plugin Architecture

### Core Components

1. **PluginBase**: Abstract base class all plugins must inherit from
2. **PluginMetadata**: Structured metadata for plugin information
3. **PluginManager**: Handles discovery, loading, and lifecycle
4. **PluginDiscovery**: Scans directories for plugin files

### Plugin Lifecycle

1. **Discovery**: Plugin files are scanned from `plugins/` directory
2. **Loading**: Plugin classes are instantiated
3. **Initialization**: `initialize()` method is called
4. **Registration**: Tools are registered with the tool registry
5. **Cleanup**: `cleanup()` method is called on shutdown

## Creating Plugins

### Method 1: LangChain @tool Functions (Recommended)

```python
from langchain_core.tools import tool
from jarvis.plugins.base import PluginBase, PluginMetadata

@tool
def weather_forecast(city: str) -> str:
    """Get weather forecast for a city."""
    # Your implementation here
    return f"Weather in {city}: Sunny, 75°F"

@tool  
def current_weather(city: str) -> str:
    """Get current weather for a city."""
    # Your implementation here
    return f"Current weather in {city}: Clear, 72°F"

class WeatherPlugin(PluginBase):
    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="WeatherPlugin",
            version="1.0.0", 
            description="Provides weather information tools",
            author="Weather Team",
            dependencies=["requests"],  # Optional external dependencies
            tools=[weather_forecast, current_weather]
        )
    
    def get_tools(self):
        return [weather_forecast, current_weather]

PLUGIN_CLASS = WeatherPlugin
PLUGIN_METADATA = WeatherPlugin().get_metadata()
```

### Method 2: BaseTool Classes (Legacy)

```python
from jarvis.tools.base import BaseTool, ToolResult, create_success_result
from jarvis.plugins.base import PluginBase, PluginMetadata

class CalculatorTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="calculator",
            description="Perform basic math calculations"
        )
    
    def execute(self, expression: str) -> ToolResult:
        try:
            result = eval(expression)  # Note: eval is unsafe, use proper parser
            return create_success_result(str(result))
        except Exception as e:
            return create_error_result(str(e))

class CalculatorPlugin(PluginBase):
    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="CalculatorPlugin",
            version="1.0.0",
            description="Basic calculator functionality",
            author="Math Team"
        )
    
    def get_tools(self):
        return [CalculatorTool()]

PLUGIN_CLASS = CalculatorPlugin  
PLUGIN_METADATA = CalculatorPlugin().get_metadata()
```

## Plugin Metadata

### Required Fields

- `name`: Unique plugin identifier
- `version`: Semantic version (e.g., "1.0.0")
- `description`: Brief description of plugin functionality
- `author`: Plugin author/maintainer

### Optional Fields

- `dependencies`: List of Python packages required
- `min_jarvis_version`: Minimum Jarvis version required
- `enabled`: Whether plugin is enabled by default
- `tools`: List of tools provided (auto-populated)

## Best Practices

### 1. Error Handling

Always handle errors gracefully:

```python
@tool
def risky_operation(input_data: str) -> str:
    """An operation that might fail."""
    try:
        # Your risky code here
        result = process_data(input_data)
        return f"Success: {result}"
    except Exception as e:
        logger.error(f"Operation failed: {e}")
        return f"Error: {str(e)}"
```

### 2. Dependency Management

Handle optional dependencies gracefully:

```python
def validate_dependencies(self) -> bool:
    """Check if optional dependencies are available."""
    try:
        import requests
        return True
    except ImportError:
        logger.warning("requests not available - some features disabled")
        return True  # Still allow plugin to load
```

### 3. Logging

Use proper logging:

```python
import logging
logger = logging.getLogger(__name__)

class MyPlugin(PluginBase):
    def initialize(self):
        super().initialize()
        logger.info("MyPlugin initialized successfully")
```

### 4. Tool Documentation

Provide clear tool descriptions:

```python
@tool
def complex_tool(param1: str, param2: int = 10) -> str:
    """
    Perform a complex operation with detailed documentation.
    
    Args:
        param1: Description of first parameter
        param2: Description of second parameter (default: 10)
        
    Returns:
        Detailed description of return value
    """
    return f"Processed {param1} with value {param2}"
```

## Testing Plugins

### Unit Testing

```python
# tests/test_my_plugin.py
import pytest
from plugins.my_plugin import MyPlugin, my_tool

def test_plugin_metadata():
    plugin = MyPlugin()
    metadata = plugin.get_metadata()
    assert metadata.name == "MyPlugin"
    assert metadata.version == "1.0.0"

def test_my_tool():
    result = my_tool.invoke({"message": "Test"})
    assert "Test from my plugin!" in result
```

### Integration Testing

```python
def test_plugin_loading():
    from jarvis.plugins.manager import PluginManager
    
    manager = PluginManager(auto_discover=False)
    manager.load_plugin("MyPlugin", MyPlugin)
    
    assert "MyPlugin" in manager.get_loaded_plugin_names()
    tools = manager.get_all_tools()
    assert len(tools) > 0
```

## Troubleshooting

### Common Issues

1. **Plugin not discovered**: Check file naming and `PLUGIN_CLASS`/`PLUGIN_METADATA` exports
2. **Import errors**: Verify dependencies and import paths
3. **Tool not working**: Check LangChain tool decorator and function signature
4. **Metadata errors**: Ensure all required metadata fields are provided

### Debug Mode

Enable debug logging to see plugin loading details:

```python
import logging
logging.getLogger('jarvis.plugins').setLevel(logging.DEBUG)
```

## Examples

See the `plugins/` directory for complete examples:
- `time_plugin.py`: LangChain tools with device-first time functionality
- `system_plugin.py`: System information tools with optional dependencies

## Contributing

When contributing plugins:
1. Follow the established patterns
2. Include comprehensive tests
3. Document all tools clearly
4. Handle errors gracefully
5. Consider optional dependencies
