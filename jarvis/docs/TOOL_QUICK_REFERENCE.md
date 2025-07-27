# Jarvis Tool Development Quick Reference

## 🚀 Quick Start Checklist

1. **Generate plugin**: `python manage_plugins.py generate my_tool --type tool`
2. **Edit the generated file** in `jarvis/tools/plugins/` ← **CRITICAL LOCATION**
3. **Use @tool decorator** from `langchain_core.tools`
4. **⚠️ Function name = Tool name** (use descriptive names)
5. **Add plugin metadata** for automatic discovery
6. **Test your plugin**: `python manage_plugins.py list`
7. **Load and use**: Automatically available in Jarvis

## ⚠️ **Critical Rules**

- **File Location**: Must be in `jarvis/tools/plugins/` (not `tools/plugins/`)
- **Function Name**: Becomes the tool name (use `get_current_time` not `get_time`)
- **Descriptive Names**: Avoid generic names that might conflict

## 📋 Essential Components

### LangChain Tool Function
```python
from langchain_core.tools import tool

@tool
def your_tool(param: str, optional: int = 1) -> str:
    """
    Description of what your tool does.

    Args:
        param: Clear description of parameter
        optional: Optional parameter with default (default: 1)

    Returns:
        str: Description of return value
    """
    try:
        # Your logic here
        return f"Processed {param} with {optional}"
    except Exception as e:
        return f"Error: {str(e)}"
```

### Plugin Class
```python
from jarvis.plugins.base import PluginBase, PluginMetadata

class YourToolPlugin(PluginBase):
    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="YourTool",
            version="1.0.0",
            author="Your Name",
            description="Brief description"
        )

    def get_tools(self) -> List[BaseTool]:
        return [your_tool]

# Plugin Discovery
PLUGIN_CLASS = YourToolPlugin
PLUGIN_METADATA = YourToolPlugin().get_metadata()
```

## 🔧 Common Field Types

### Basic Types
```python
# String with validation
text: str = Field(description="Text input", min_length=1, max_length=500)

# Integer with range
count: int = Field(default=10, ge=1, le=100, description="Count (1-100)")

# Boolean
enabled: bool = Field(default=False, description="Enable feature")

# Optional with default
optional_text: Optional[str] = Field(default=None, description="Optional text")
```

### Advanced Types
```python
# Enum for choices
class ModeEnum(str, Enum):
    FAST = "fast"
    SLOW = "slow"

mode: ModeEnum = Field(default=ModeEnum.FAST, description="Processing mode")

# List with limits
tags: List[str] = Field(default=[], max_items=5, description="Tags list")

# Dictionary
options: Dict[str, Any] = Field(default={}, description="Key-value options")

# Union for multiple types
value: Union[str, int] = Field(description="String or integer value")
```

### Custom Validation
```python
@validator('email')
def validate_email(cls, v):
    if '@' not in v:
        raise ValueError('Invalid email format')
    return v.lower()
```

## 🛡️ Error Handling Patterns

### Input Validation
```python
if not param or not param.strip():
    raise ValueError("Parameter cannot be empty")
```

### Try-Catch Structure
```python
try:
    # Main logic
    result = process_data(param)
    return f"Success: {result}"
except ValueError as e:
    logger.warning(f"Invalid input: {e}")
    return f"Invalid input: {e}"
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    return f"Tool error: {e}"
```

## 📝 Tool Description Guidelines

### Good Descriptions
- "Get current system time and timezone information"
- "Search for files by name or content in specified directory"
- "Convert text between different formats (JSON, XML, CSV)"

### Bad Descriptions
- "Does stuff with data"
- "Useful tool"
- "Processes input"

### Description Template
```
"[Action verb] [what it does] [when to use it]. [Key features/options]."
```

## 🧪 Testing Your Tool

### Manual Testing
```python
# Test in your tool file
if __name__ == "__main__":
    result = your_tool_function("test input")
    print(result)
```

### Unit Tests
```python
def test_your_tool():
    result = your_tool_function("valid input")
    assert "expected" in result
    
    # Test error handling
    result = your_tool_function("")
    assert "error" in result.lower()
```

### Integration Test
```python
def test_tool_registration():
    from jarvis.tools import tool_registry
    tools = tool_registry.get_langchain_tools()
    tool_names = [t.name for t in tools]
    assert "your_tool" in tool_names
```

## 📁 File Structure

```
jarvis/tools/
├── __init__.py          # Core tool registry (don't modify)
├── plugins/             # Place your tools here
│   └── your_tool.py     # Your tool implementation
├── system_info.py       # Example: System tools
├── time_tools.py        # Example: Time tools
└── video_day.py         # Example: Content tools

templates/
└── tool_template.py     # Copy this to start

docs/
├── TOOL_DEVELOPMENT_GUIDE.md  # Full guide
└── TOOL_QUICK_REFERENCE.md    # This file
```

## 🔄 Registration Process

1. **Add plugin metadata** to your tool file:
```python
from jarvis.plugins.base import PluginMetadata

# Create tool instance
your_tool = create_your_tool()

# Define plugin metadata
PLUGIN_METADATA = PluginMetadata(
    name="YourToolPlugin",
    version="1.0.0",
    author="Your Name",
    description="Brief description",
    tools=[your_tool]
)
```

2. **Place in plugins directory**: `jarvis/tools/plugins/your_tool.py`

3. **Automatic discovery**: Jarvis will find and load your tool on startup

**Do not modify `jarvis/tools/__init__.py`** - the plugin system handles registration automatically.

## 🐛 Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| Tool not found | Check registration in `__init__.py` |
| JSON parsing error | Verify input schema matches function params |
| Import error | Check all dependencies are installed |
| Validation error | Review Pydantic field definitions |
| Tool timeout | Add proper error handling and logging |

## 💡 Best Practices

### ✅ Do
- Use clear, descriptive names
- Add comprehensive error handling
- Include detailed docstrings
- Validate all inputs
- Log important operations
- Return user-friendly messages
- Test thoroughly before integration

### ❌ Don't
- Use generic error messages
- Skip input validation
- Ignore edge cases
- Make tools too complex
- Forget to handle exceptions
- Use unclear parameter names
- Skip documentation

## 🎯 Tool Categories

### Information Tools
- Get system info, time, weather
- Query databases or APIs
- Search files or content

### Action Tools
- File operations
- System commands
- API calls

### Processing Tools
- Text transformation
- Data analysis
- Format conversion

### Utility Tools
- Calculations
- Validations
- Formatting

## 📞 Getting Help

1. **Check existing tools** for patterns and examples
2. **Review the full guide** in `TOOL_DEVELOPMENT_GUIDE.md`
3. **Test with the template** before building from scratch
4. **Ask for code review** before final integration

## 🔗 Related Files

- `manage_plugins.py` - Plugin management CLI
- `docs/TOOL_DEVELOPMENT_GUIDE.md` - Comprehensive guide
- `docs/MCP_SYSTEM_OVERVIEW.md` - MCP architecture overview
- `jarvis/tools/plugins/` - Plugin directory
- `jarvis/plugins/` - MCP system core
