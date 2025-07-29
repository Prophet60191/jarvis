# 📚 Jarvis Plugin Reference Guide

Complete API reference and technical documentation for the Jarvis plugin system.

## 🏗️ **Plugin Architecture**

### **Core Components**

#### **PluginBase Class**
```python
from jarvis.plugins.base import PluginBase, PluginMetadata

class MyPlugin(PluginBase):
    """Base class for all Jarvis plugins."""
    
    def get_metadata(self) -> PluginMetadata:
        """Return plugin metadata. REQUIRED."""
        return PluginMetadata(
            name="MyPlugin",           # Unique plugin name
            version="1.0.0",          # Semantic version
            description="My plugin",   # Brief description
            author="Your Name"         # Plugin author
        )
    
    def get_tools(self) -> List[BaseTool]:
        """Return list of tools. REQUIRED."""
        return [my_tool_function]
    
    def initialize(self) -> bool:
        """Optional: Initialize plugin resources."""
        return True
    
    def cleanup(self) -> bool:
        """Optional: Clean up plugin resources."""
        return True
```

#### **PluginMetadata Class**
```python
@dataclass
class PluginMetadata:
    name: str                    # Plugin identifier
    version: str                 # Version string (e.g., "1.0.0")
    description: str             # Brief description
    author: str                  # Author name
    dependencies: List[str] = field(default_factory=list)  # Optional dependencies
    tags: List[str] = field(default_factory=list)          # Optional tags
    min_jarvis_version: str = "1.0.0"                      # Minimum Jarvis version
```

### **Required Exports**
Every plugin file must export these variables:

```python
# At the end of your plugin file
PLUGIN_CLASS = MyPlugin
PLUGIN_METADATA = MyPlugin().get_metadata()
```

## 🛠️ **Tool Creation**

### **Basic Tool Structure**
```python
from langchain_core.tools import tool

@tool
def my_tool(parameter: str) -> str:
    """
    Tool description for the AI.
    
    This description helps the AI understand when and how to use your tool.
    Be specific about the tool's purpose and expected inputs/outputs.
    
    Args:
        parameter: Description of the parameter
        
    Returns:
        str: Description of the return value
    """
    try:
        # Your tool implementation
        result = f"Processed: {parameter}"
        return result
    except Exception as e:
        return f"Error: {str(e)}"
```

### **Parameter Types**
```python
from typing import Optional, List, Dict, Union

@tool
def advanced_tool(
    required_param: str,                    # Required string
    optional_param: Optional[str] = None,   # Optional string
    number_param: int = 10,                 # Integer with default
    float_param: float = 1.5,               # Float with default
    bool_param: bool = False,               # Boolean with default
    list_param: List[str] = None,           # List parameter
    dict_param: Dict[str, str] = None       # Dictionary parameter
) -> str:
    """Tool with various parameter types."""
    # Handle None defaults
    if list_param is None:
        list_param = []
    if dict_param is None:
        dict_param = {}
    
    # Implementation
    return "Success"
```

### **Error Handling Patterns**
```python
@tool
def robust_tool(data: str) -> str:
    """Tool with comprehensive error handling."""
    try:
        # Input validation
        if not data:
            return "Error: Data parameter is required"
        
        if len(data) > 1000:
            return "Error: Data too long (max 1000 characters)"
        
        # Processing
        result = process_data(data)
        
        # Success logging
        logger.info(f"Tool executed successfully: {data[:50]}...")
        return f"Success: {result}"
        
    except ValueError as e:
        logger.error(f"Invalid input: {e}")
        return f"Error: Invalid input - {str(e)}"
    
    except ConnectionError as e:
        logger.error(f"Connection failed: {e}")
        return "Error: Could not connect to external service"
    
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return f"Error: An unexpected error occurred - {str(e)}"
```

## 🔍 **Plugin Discovery System**

### **Discovery Methods**
The plugin system uses multiple discovery methods:

1. **File-based Discovery**: Scans `jarvis/jarvis/tools/plugins/` directory
2. **Module Discovery**: Imports Python modules with plugin exports
3. **Metadata Discovery**: Validates plugin structure and metadata

### **Discovery Requirements**
For a plugin to be discovered, it must:

- ✅ Be located in `jarvis/jarvis/tools/plugins/`
- ✅ Be a valid Python file (`.py` extension)
- ✅ Have `PLUGIN_CLASS` export
- ✅ Have `PLUGIN_METADATA` export
- ✅ Inherit from `PluginBase`
- ✅ Implement required methods

### **Discovery Process**
```python
# 1. File scanning
discovered_files = scan_plugin_directory()

# 2. Module importing
for file in discovered_files:
    module = import_plugin_module(file)
    
# 3. Validation
if hasattr(module, 'PLUGIN_CLASS') and hasattr(module, 'PLUGIN_METADATA'):
    plugin_class = module.PLUGIN_CLASS
    metadata = module.PLUGIN_METADATA
    
# 4. Registration
plugin_manager.register_plugin(plugin_class, metadata)
```

## 📦 **Plugin Manager API**

### **Core Methods**
```python
from jarvis.plugins.manager import PluginManager

# Initialize manager
manager = PluginManager()

# Discovery
discovered = manager.discovery.discover_plugins()

# Loading
success = manager.load_plugin("MyPlugin")
tools = manager.get_plugin_tools("MyPlugin")

# Management
loaded_plugins = manager.get_loaded_plugin_names()
plugin_info = manager.get_plugin_info("MyPlugin")

# Cleanup
manager.unload_plugin("MyPlugin")
manager.unload_all_plugins()
```

### **Plugin States**
- **Discovered**: Found but not loaded
- **Loading**: Currently being loaded
- **Loaded**: Successfully loaded and available
- **Error**: Failed to load due to errors
- **Unloaded**: Previously loaded but now unloaded

## 🔧 **CLI Commands Reference**

### **Plugin Management**
```bash
# List all plugins
python manage_plugins.py list
python manage_plugins.py list --details
python manage_plugins.py list --loaded

# Plugin information
python manage_plugins.py info PluginName
python manage_plugins.py validate PluginName

# Load/unload plugins
python manage_plugins.py load PluginName
python manage_plugins.py unload PluginName
python manage_plugins.py reload PluginName

# Testing
python manage_plugins.py test PluginName
python manage_plugins.py check-conflicts
```

### **Plugin Generation**
```bash
# Basic plugin
python manage_plugins.py generate plugin_name --type tool --author "Name"

# With description
python manage_plugins.py generate plugin_name --type tool --author "Name" --description "Description"

# Advanced plugin
python manage_plugins.py generate plugin_name --type advanced --author "Name"

# Custom output directory (must be in plugins folder)
python manage_plugins.py generate plugin_name --type tool --author "Name" --output jarvis/jarvis/tools/plugins/
```

## 🏷️ **Plugin Templates**

### **Available Template Types**

#### **1. Basic Tool Template (`--type tool`)**
- Single tool function
- Basic error handling
- Minimal structure
- Good for simple utilities

#### **2. Advanced Template (`--type advanced`)**
- Multiple tools
- Configuration management
- State management
- Comprehensive error handling
- Logging integration

#### **3. Service Template (`--type service`)**
- External service integration
- API client patterns
- Authentication handling
- Rate limiting
- Retry logic

### **Template Customization**
```python
# Custom template in generator.py
CUSTOM_TEMPLATE = '''
"""
{plugin_name} Plugin for Jarvis Voice Assistant.

Custom template with specific patterns.

Author: {author}
Date: {date}
"""

import logging
from typing import List
from langchain_core.tools import tool
from jarvis.plugins.base import PluginBase, PluginMetadata

logger = logging.getLogger(__name__)

@tool
def {function_name}(input_data: str) -> str:
    """Custom tool implementation."""
    try:
        # Custom logic here
        return f"Custom result: {{input_data}}"
    except Exception as e:
        logger.error(f"Error in {function_name}: {{e}}")
        return f"Error: {{str(e)}}"

class {class_name}(PluginBase):
    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="{plugin_name}",
            version="1.0.0",
            description="{description}",
            author="{author}"
        )
    
    def get_tools(self):
        return [{function_name}]

PLUGIN_CLASS = {class_name}
PLUGIN_METADATA = {class_name}().get_metadata()
'''
```

## 🔒 **Security Considerations**

### **Input Validation**
```python
@tool
def secure_tool(user_input: str) -> str:
    """Tool with proper input validation."""
    # Length validation
    if len(user_input) > MAX_INPUT_LENGTH:
        return "Error: Input too long"
    
    # Content validation
    if contains_malicious_content(user_input):
        return "Error: Invalid input content"
    
    # Sanitization
    sanitized_input = sanitize_input(user_input)
    
    return process_safely(sanitized_input)
```

### **Resource Management**
```python
class ResourceManagedPlugin(PluginBase):
    def __init__(self):
        self.resources = []
    
    def initialize(self) -> bool:
        """Acquire resources safely."""
        try:
            self.resources.append(acquire_resource())
            return True
        except Exception as e:
            logger.error(f"Failed to initialize: {e}")
            return False
    
    def cleanup(self) -> bool:
        """Release resources properly."""
        try:
            for resource in self.resources:
                release_resource(resource)
            self.resources.clear()
            return True
        except Exception as e:
            logger.error(f"Failed to cleanup: {e}")
            return False
```

## 🐛 **Debugging & Troubleshooting**

### **Common Issues**

#### **Plugin Not Discovered**
```bash
# Check file location
ls jarvis/jarvis/tools/plugins/your_plugin.py

# Validate syntax
python -m py_compile jarvis/jarvis/tools/plugins/your_plugin.py

# Check exports
python -c "
import sys
sys.path.append('jarvis')
from jarvis.tools.plugins.your_plugin import PLUGIN_CLASS, PLUGIN_METADATA
print('Exports found:', PLUGIN_CLASS, PLUGIN_METADATA)
"
```

#### **Import Errors**
```python
# Debug imports
try:
    from jarvis.plugins.base import PluginBase, PluginMetadata
    print("✅ Base imports successful")
except ImportError as e:
    print(f"❌ Import error: {e}")

try:
    from langchain_core.tools import tool
    print("✅ LangChain imports successful")
except ImportError as e:
    print(f"❌ LangChain import error: {e}")
```

#### **Tool Not Available**
```python
# Check tool registration
manager = PluginManager()
tools = manager.get_all_tools()
tool_names = [tool.name for tool in tools]
print("Available tools:", tool_names)
```

### **Logging Configuration**
```python
import logging

# Configure plugin logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Add handler if needed
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
```

## 📊 **Performance Considerations**

### **Efficient Tool Design**
```python
@tool
def efficient_tool(data: str) -> str:
    """Tool optimized for performance."""
    # Early validation
    if not data:
        return "Error: No data provided"
    
    # Avoid expensive operations in validation
    if len(data) > 10000:  # Simple length check
        return "Error: Data too large"
    
    # Use generators for large datasets
    def process_chunks():
        for chunk in chunk_data(data, 1000):
            yield process_chunk(chunk)
    
    # Lazy evaluation
    results = list(process_chunks())
    return f"Processed {len(results)} chunks"
```

### **Memory Management**
```python
class MemoryEfficientPlugin(PluginBase):
    def __init__(self):
        self._cache = {}
        self._max_cache_size = 100
    
    def get_cached_result(self, key: str):
        """Implement LRU cache with size limit."""
        if len(self._cache) > self._max_cache_size:
            # Remove oldest entries
            oldest_keys = list(self._cache.keys())[:10]
            for old_key in oldest_keys:
                del self._cache[old_key]
        
        return self._cache.get(key)
```

This reference guide provides the complete technical foundation for developing robust, secure, and efficient Jarvis plugins. Use it alongside the [Tool Development Guide](TOOL_DEVELOPMENT_GUIDE.md) for comprehensive plugin development.
