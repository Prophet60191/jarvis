# 🛠️ Jarvis Tool Development Guide

Complete guide for creating plugins and tools that integrate with the Jarvis AI assistant using our MCP (Model Context Protocol) plugin system.

## 🎯 Overview

Jarvis tools are Python functions that extend the assistant's capabilities using LangChain's `@tool` decorator and our MCP plugin architecture. Tools are automatically discovered and loaded without requiring changes to the core codebase.

### **Key Features**
- ✅ **Zero Core Changes**: Add tools without modifying main code
- ✅ **Automatic Discovery**: Plugins load automatically at startup
- ✅ **Template Generation**: Quick start with built-in templates
- ✅ **CLI Management**: Easy plugin management commands
- ✅ **Hot Reloading**: Modify plugins without restarting Jarvis

## 📁 **File Structure & Placement**

### **Required Directory Structure**
```
jarvis/
├── jarvis/
│   ├── plugins/                    # Plugin system core (DON'T MODIFY)
│   │   ├── base.py                # PluginBase class
│   │   ├── manager.py             # Plugin lifecycle management
│   │   ├── discovery.py           # Auto-discovery system
│   │   ├── generator.py           # Template generator
│   │   └── cli.py                 # Management CLI
│   └── tools/
│       └── plugins/               # 👈 YOUR PLUGINS GO HERE
│           ├── my_plugin.py       # Your plugin files
│           ├── another_tool.py    # More plugins
│           └── __pycache__/       # Auto-generated
├── manage_plugins.py              # Plugin management script
└── docs/                          # Documentation
```

### **Where to Place Your Plugins**
- ✅ **Correct**: `jarvis/jarvis/tools/plugins/your_plugin.py`
- ❌ **Wrong**: `jarvis/plugins/your_plugin.py`
- ❌ **Wrong**: `plugins/your_plugin.py`
- ❌ **Wrong**: `jarvis/jarvis/plugins/your_plugin.py`

## 🚀 **Quick Start**

### **Method 1: Use Plugin Generator (Recommended)**

```bash
# Generate a basic plugin
python manage_plugins.py generate my_awesome_tool --type tool --author "Your Name"

# Generate with description
python manage_plugins.py generate weather_tool --type tool --author "John Doe" --description "Get weather information"

# Generate advanced plugin
python manage_plugins.py generate advanced_tool --type advanced --author "Your Name"
```

### **Method 2: Manual Creation**

Create `jarvis/jarvis/tools/plugins/my_tool.py`:

```python
"""
My Tool Plugin for Jarvis Voice Assistant.

This plugin provides [describe functionality].

Author: Your Name
Date: 2025-07-29
"""

import logging
from typing import List
from langchain_core.tools import BaseTool, tool
from jarvis.plugins.base import PluginBase, PluginMetadata

logger = logging.getLogger(__name__)

@tool
def my_awesome_function(input_text: str) -> str:
    """
    Brief description of what this tool does.

    Use this tool when the user wants to [describe when to use].

    Args:
        input_text: Description of the input parameter

    Returns:
        str: Description of what the tool returns
    """
    try:
        # Your tool implementation here
        result = f"Processed: {input_text}"
        logger.info(f"Successfully processed: {input_text}")
        return result
    except Exception as e:
        logger.error(f"Error in my_awesome_function: {e}")
        return f"Error: Could not process input. {str(e)}"

class MyToolPlugin(PluginBase):
    """Plugin class for My Tool."""

    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="MyTool",
            version="1.0.0",
            description="My awesome tool for Jarvis",
            author="Your Name"
        )

    def get_tools(self) -> List[BaseTool]:
        return [my_awesome_function]

# Required exports for auto-discovery
PLUGIN_CLASS = MyToolPlugin
PLUGIN_METADATA = MyToolPlugin().get_metadata()
```

### **Method 3: Test Your Plugin**

```bash
# List all plugins (including yours)
python manage_plugins.py list

# List with details
python manage_plugins.py list --details

# Load a specific plugin
python manage_plugins.py load MyTool

# Test plugin functionality
python manage_plugins.py test MyTool
```

## 🎯 **Tool Naming Convention**

### **CRITICAL: Function Names Become Tool Names**

The function name you use with `@tool` becomes the internal tool name:

```python
@tool
def get_current_weather(location: str) -> str:  # Tool name: "get_current_weather"
    """Get weather for a location."""
    pass

@tool
def calculate_tip(bill: float, percentage: float) -> str:  # Tool name: "calculate_tip"
    """Calculate tip amount."""
    pass
```

### **Best Practices for Naming**
- ✅ **Descriptive**: `get_current_weather` not `weather`
- ✅ **Unique**: Avoid conflicts with existing tools
- ✅ **Snake Case**: `my_function` not `myFunction`
- ✅ **Verb-Noun**: `get_time`, `calculate_sum`, `send_email`
- ❌ **Generic**: `get_data`, `process`, `handle`

## 📋 **Plugin Templates**

### **Basic Plugin Template**
```python
"""Basic plugin with single tool."""

from langchain_core.tools import tool
from jarvis.plugins.base import PluginBase, PluginMetadata

@tool
def simple_tool(input_data: str) -> str:
    """Simple tool that processes input."""
    return f"Processed: {input_data}"

class SimplePlugin(PluginBase):
    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="SimplePlugin",
            version="1.0.0",
            description="A simple example plugin",
            author="Your Name"
        )

    def get_tools(self):
        return [simple_tool]

PLUGIN_CLASS = SimplePlugin
PLUGIN_METADATA = SimplePlugin().get_metadata()
```

### **Multi-Tool Plugin Template**
```python
"""Plugin with multiple related tools."""

from langchain_core.tools import tool
from jarvis.plugins.base import PluginBase, PluginMetadata

@tool
def add_numbers(a: float, b: float) -> str:
    """Add two numbers together."""
    try:
        result = a + b
        return f"The sum of {a} and {b} is {result}"
    except Exception as e:
        return f"Error adding numbers: {str(e)}"

@tool
def multiply_numbers(a: float, b: float) -> str:
    """Multiply two numbers together."""
    try:
        result = a * b
        return f"The product of {a} and {b} is {result}"
    except Exception as e:
        return f"Error multiplying numbers: {str(e)}"

class MathPlugin(PluginBase):
    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="MathPlugin",
            version="1.0.0",
            description="Basic math operations",
            author="Your Name"
        )

    def get_tools(self):
        return [add_numbers, multiply_numbers]

PLUGIN_CLASS = MathPlugin
PLUGIN_METADATA = MathPlugin().get_metadata()
```

### **Advanced Plugin Template**
```python
"""Advanced plugin with configuration and state management."""

import logging
import json
from pathlib import Path
from typing import List, Dict, Any
from langchain_core.tools import tool
from jarvis.plugins.base import PluginBase, PluginMetadata

logger = logging.getLogger(__name__)

class AdvancedPlugin(PluginBase):
    """Advanced plugin with configuration and state."""

    def __init__(self):
        super().__init__()
        self.config_file = Path("config/advanced_plugin.json")
        self.config = self.load_config()

    def load_config(self) -> Dict[str, Any]:
        """Load plugin configuration."""
        if self.config_file.exists():
            try:
                return json.loads(self.config_file.read_text())
            except Exception as e:
                logger.error(f"Failed to load config: {e}")
        return {"api_key": "", "timeout": 30}

    def save_config(self):
        """Save plugin configuration."""
        try:
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            self.config_file.write_text(json.dumps(self.config, indent=2))
        except Exception as e:
            logger.error(f"Failed to save config: {e}")

    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="AdvancedPlugin",
            version="1.0.0",
            description="Advanced plugin with configuration",
            author="Your Name"
        )

    def get_tools(self):
        return [
            self.create_configured_tool(),
            self.create_status_tool()
        ]

    def create_configured_tool(self):
        """Create a tool that uses plugin configuration."""
        @tool
        def configured_operation(data: str) -> str:
            """Perform operation using plugin configuration."""
            try:
                timeout = self.config.get("timeout", 30)
                # Use configuration in your tool logic
                result = f"Processed '{data}' with timeout {timeout}s"
                logger.info(f"Configured operation completed: {result}")
                return result
            except Exception as e:
                logger.error(f"Configured operation failed: {e}")
                return f"Error: {str(e)}"

        return configured_operation

    def create_status_tool(self):
        """Create a tool that shows plugin status."""
        @tool
        def plugin_status() -> str:
            """Get the status of the advanced plugin."""
            try:
                status = {
                    "name": self.get_metadata().name,
                    "version": self.get_metadata().version,
                    "config_loaded": bool(self.config),
                    "config_file": str(self.config_file)
                }
                return f"Plugin Status: {json.dumps(status, indent=2)}"
            except Exception as e:
                return f"Error getting status: {str(e)}"

        return plugin_status

# Create instance for auto-discovery
_plugin_instance = AdvancedPlugin()
PLUGIN_CLASS = AdvancedPlugin
PLUGIN_METADATA = _plugin_instance.get_metadata()
```

## 🔧 **Plugin Management Commands**

### **List Plugins**
```bash
# List all discovered plugins
python manage_plugins.py list

# List with detailed information
python manage_plugins.py list --details

# List only loaded plugins
python manage_plugins.py list --loaded
```

### **Generate New Plugins**
```bash
# Basic plugin
python manage_plugins.py generate my_plugin --type tool --author "Your Name"

# Plugin with description
python manage_plugins.py generate weather_plugin --type tool --author "John Doe" --description "Weather information tools"

# Advanced plugin with configuration
python manage_plugins.py generate advanced_plugin --type advanced --author "Your Name"

# Plugin in custom location (still must be in plugins directory)
python manage_plugins.py generate custom_plugin --type tool --author "Your Name" --output jarvis/jarvis/tools/plugins/
```

### **Load and Test Plugins**
```bash
# Load a specific plugin
python manage_plugins.py load MyPlugin

# Unload a plugin
python manage_plugins.py unload MyPlugin

# Test plugin functionality
python manage_plugins.py test MyPlugin

# Reload a plugin (useful during development)
python manage_plugins.py reload MyPlugin
```

### **Plugin Information**
```bash
# Get detailed info about a plugin
python manage_plugins.py info MyPlugin

# Validate plugin structure
python manage_plugins.py validate MyPlugin

# Check for plugin conflicts
python manage_plugins.py check-conflicts
```

## ✅ **Best Practices**

### **Code Quality**
- ✅ **Use type hints**: `def my_tool(input: str) -> str:`
- ✅ **Handle exceptions**: Always wrap in try/catch blocks
- ✅ **Log operations**: Use `logging` for debugging
- ✅ **Return strings**: Tools should return string messages
- ✅ **Clear docstrings**: Describe when and how to use the tool

### **Error Handling**
```python
@tool
def robust_tool(input_data: str) -> str:
    """Example of proper error handling."""
    try:
        # Validate input
        if not input_data or not input_data.strip():
            return "Error: Input data is required"

        # Process data
        result = process_data(input_data)

        # Log success
        logger.info(f"Successfully processed: {input_data}")
        return f"Success: {result}"

    except ValueError as e:
        logger.error(f"Invalid input: {e}")
        return f"Error: Invalid input - {str(e)}"
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return f"Error: Could not process data - {str(e)}"
```

### **Documentation Standards**
```python
@tool
def well_documented_tool(param1: str, param2: int = 10) -> str:
    """
    Brief one-line description of what this tool does.

    Longer description explaining the tool's purpose, when to use it,
    and any important details about its behavior.

    Use this tool when the user wants to:
    - Specific use case 1
    - Specific use case 2
    - Specific use case 3

    Args:
        param1: Description of the first parameter
        param2: Description of the second parameter (default: 10)

    Returns:
        str: Description of what the tool returns

    Example:
        User: "Please process my data"
        Tool: "Successfully processed: your data"
    """
    # Implementation here
    pass
```

### **Plugin Structure**
- ✅ **One plugin per file**: Keep plugins focused and manageable
- ✅ **Related tools together**: Group similar functionality
- ✅ **Clear naming**: Use descriptive file and class names
- ✅ **Proper imports**: Import only what you need
- ✅ **Required exports**: Always include `PLUGIN_CLASS` and `PLUGIN_METADATA`

## 🚨 **Common Issues & Solutions**

### **Plugin Not Discovered**
```bash
# Check if file is in correct location
ls jarvis/jarvis/tools/plugins/your_plugin.py

# Verify plugin structure
python manage_plugins.py validate your_plugin

# Check for syntax errors
python -m py_compile jarvis/jarvis/tools/plugins/your_plugin.py
```

### **Tool Not Available in Jarvis**
1. **Check plugin is loaded**: `python manage_plugins.py list --loaded`
2. **Verify tool function**: Ensure `@tool` decorator is used
3. **Check exports**: Verify `PLUGIN_CLASS` and `PLUGIN_METADATA` exist
4. **Restart Jarvis**: Some changes require restart

### **Import Errors**
```python
# Correct imports
from langchain_core.tools import tool  # ✅
from jarvis.plugins.base import PluginBase, PluginMetadata  # ✅

# Incorrect imports
from langchain.tools import tool  # ❌ Old version
from plugins.base import PluginBase  # ❌ Wrong path
```

## 📚 **Additional Resources**

- **[Plugin Reference Guide](PLUGIN_REFERENCE_GUIDE.md)**: Complete API reference
- **[Existing Plugins](../jarvis/tools/plugins/)**: Study working examples
- **[LangChain Tools](https://python.langchain.com/docs/modules/agents/tools/)**: Official LangChain documentation
- **[Voice Command Integration](UI_TEMPLATE_SYSTEM.md#voice-command-integration)**: Add voice commands to your tools

## 🎯 **Quick Checklist**

Before submitting your plugin:

- [ ] Plugin file in `jarvis/jarvis/tools/plugins/`
- [ ] Uses `@tool` decorator from `langchain_core.tools`
- [ ] Includes `PluginBase` class with metadata
- [ ] Has `PLUGIN_CLASS` and `PLUGIN_METADATA` exports
- [ ] Functions have clear, unique names
- [ ] Comprehensive docstrings with use cases
- [ ] Proper error handling with try/catch
- [ ] Returns string messages
- [ ] Tested with `python manage_plugins.py test`
- [ ] No syntax errors or import issues

**Ready to build?** Start with `python manage_plugins.py generate my_first_plugin --type tool --author "Your Name"` and follow this guide! 🚀
