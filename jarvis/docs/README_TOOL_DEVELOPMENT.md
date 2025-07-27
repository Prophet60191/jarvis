# Jarvis Tool Development System

A comprehensive MCP (Model Context Protocol) system for creating, validating, and integrating tools with the Jarvis AI assistant without modifying core code.

## 🚀 Quick Start

### Option 1: Use the Plugin Generator (Recommended)
```bash
python manage_plugins.py generate my_tool --type tool --author "Your Name"
```

### Option 2: Use Plugin Templates
```bash
# Generate different plugin types
python manage_plugins.py generate basic_tool --type basic
python manage_plugins.py generate advanced_tool --type advanced
```

### Option 3: Manual Plugin Creation
Create a file in `jarvis/tools/plugins/` following the MCP plugin patterns.

## ⚠️ **Critical Development Rules**

### 1. File Location
- ✅ **Correct**: `jarvis/tools/plugins/your_tool.py`
- ❌ **Wrong**: `tools/plugins/your_tool.py` (project root)

### 2. Function Naming
- **Function name = Tool name** (LangChain automatic naming)
- Use descriptive names: `get_current_time`, `calculate_sum`, `fetch_weather`
- Avoid generic names: `get_time`, `process`, `handle`

### 3. Plugin Discovery
- Files must be in `jarvis/tools/plugins/` for automatic discovery
- Use `python manage_plugins.py list` to verify discovery

## 📁 File Structure

```
jarvis/
├── docs/
│   ├── TOOL_DEVELOPMENT_GUIDE.md    # Comprehensive MCP guide
│   ├── TOOL_QUICK_REFERENCE.md      # Quick reference
│   ├── plugin_development_guide.md  # Plugin development
│   ├── MCP_SYSTEM_OVERVIEW.md       # MCP architecture overview
│   ├── installation.md              # Installation guide
│   └── README_TOOL_DEVELOPMENT.md   # This file
├── plugins/                         # Plugin system core
│   ├── base.py                      # PluginBase class
│   ├── manager.py                   # Plugin lifecycle management
│   ├── discovery.py                 # Auto-discovery system
│   ├── generator.py                 # Template generator
│   └── cli.py                       # Management CLI
├── tools/
│   ├── plugins/                     # Your plugins go here
│   │   ├── __init__.py
│   │   └── your_plugin.py           # Your new plugin
│   ├── __init__.py                  # Tool registry integration
│   └── base.py                      # Legacy tool base classes
└── manage_plugins.py                # Plugin management script
```

## 🛠️ Development Workflow

### 1. Generate Plugin
```bash
# Generate new plugin with template
python manage_plugins.py generate my_tool --type tool --author "Your Name"
```

### 2. Implement Logic
Edit the generated file in `jarvis/tools/plugins/`:
- Use `@tool` decorator from `langchain_core.tools`
- Implement tool function with error handling
- Add plugin metadata for discovery

### 3. Test Your Plugin
```bash
# List discovered plugins
python manage_plugins.py list --details

# Load your plugin
python manage_plugins.py load MyTool

# Show plugin info
python manage_plugins.py info MyTool
```

### 4. Automatic Integration
No manual registration needed! The MCP system:
- Automatically discovers your plugin
- Loads it on Jarvis startup
- Makes tools available to the AI agent

### 5. Use in Jarvis
```bash
# Start Jarvis - your tools are automatically available
python -m jarvis.main
# Say "Jarvis" and use your new tool!
```

## 📋 Tool Requirements

### Must Have
- ✅ Pydantic input schema with descriptions
- ✅ Tool function with error handling
- ✅ LangChain tool creator function
- ✅ Clear, specific tool description
- ✅ Proper return type (string)

### Should Have
- ⭐ Comprehensive docstrings
- ⭐ Input validation and sanitization
- ⭐ Logging for debugging
- ⭐ Unit tests
- ⭐ Example usage

### Nice to Have
- 🎯 Custom Pydantic validators
- 🎯 Multiple processing modes
- 🎯 Configuration options
- 🎯 Performance optimizations

## 🧪 Testing Tools

### Validation Script
```bash
python scripts/validate_tool.py jarvis/tools/my_tool.py
```

Checks for:
- Required imports and structure
- Input schema validation
- Function signatures and types
- Tool creation and functionality
- Common issues and best practices

### Manual Testing
```python
# In your tool file
if __name__ == "__main__":
    result = my_tool_function("test input")
    print(result)
```

### Unit Tests
```python
def test_my_tool():
    result = my_tool_function("valid input")
    assert "expected" in result
    
    # Test error handling
    result = my_tool_function("")
    assert "error" in result.lower()
```

## 📚 Documentation

### For Users (Tool Descriptions)
- Be specific about when to use the tool
- Explain what the tool accomplishes
- Mention key parameters and options
- Include examples if helpful

**Good**: "Get current system time and timezone information for scheduling and logging"
**Bad**: "Gets time stuff"

### For Developers (Code Comments)
- Document complex logic
- Explain parameter validation
- Note any limitations or assumptions
- Include TODO items for future improvements

## 🔧 Common Patterns

### Information Retrieval
```python
def get_info_tool(query: str, limit: int = 10) -> str:
    """Retrieve information based on query."""
    try:
        results = search_database(query, limit)
        return format_results(results)
    except Exception as e:
        return f"Search failed: {e}"
```

### Action/Command
```python
def action_tool(action: str, target: str, confirm: bool = False) -> str:
    """Perform action on target."""
    if not confirm and is_destructive(action):
        return "Destructive action requires confirmation"
    
    try:
        result = execute_action(action, target)
        return f"Action completed: {result}"
    except Exception as e:
        return f"Action failed: {e}"
```

### Data Processing
```python
def process_tool(data: str, format: str = "json") -> str:
    """Process and transform data."""
    try:
        parsed = parse_input(data)
        processed = transform_data(parsed)
        return format_output(processed, format)
    except Exception as e:
        return f"Processing failed: {e}"
```

## 🐛 Troubleshooting

### Tool Not Found
- Check registration in `jarvis/tools/__init__.py`
- Verify import statement is correct
- Ensure creator function name matches

### Input Validation Errors
- Check Pydantic schema field types
- Verify required vs optional fields
- Test with sample JSON input

### Runtime Errors
- Add logging to track execution
- Test tool function independently
- Check for missing dependencies

### Performance Issues
- Add timeout handling for long operations
- Consider async operations for I/O
- Implement result caching if appropriate

## 🎯 Best Practices

### Code Quality
- Use type hints throughout
- Follow PEP 8 style guidelines
- Add comprehensive error handling
- Include meaningful log messages

### Security
- Validate and sanitize all inputs
- Avoid executing arbitrary code
- Be careful with file operations
- Don't expose sensitive information

### User Experience
- Provide clear, helpful error messages
- Return structured, readable output
- Handle edge cases gracefully
- Be consistent with other tools

### Maintainability
- Keep functions focused and small
- Use descriptive variable names
- Document complex logic
- Write tests for critical paths

## 📖 Examples

See existing tools for reference:
- `jarvis/tools/time_tools.py` - Simple information retrieval
- `jarvis/tools/system_info.py` - System interaction
- `jarvis/tools/video_day.py` - Content generation

## 🤝 Contributing

1. **Create your tool** following this guide
2. **Test thoroughly** with the validation script
3. **Document your changes** in code and README
4. **Submit for review** before integration
5. **Update documentation** if needed

## 📞 Getting Help

1. **Check existing tools** for patterns and examples
2. **Review documentation** in `docs/` directory
3. **Use validation script** to catch common issues
4. **Test incrementally** as you develop
5. **Ask for code review** before final integration

## 🔗 Related Files

- [`TOOL_DEVELOPMENT_GUIDE.md`](TOOL_DEVELOPMENT_GUIDE.md) - Comprehensive development guide
- [`TOOL_QUICK_REFERENCE.md`](TOOL_QUICK_REFERENCE.md) - Quick reference for developers
- [`../templates/tool_template.py`](../templates/tool_template.py) - Template to copy and modify
- [`../scripts/generate_tool.py`](../scripts/generate_tool.py) - Interactive tool generator
- [`../scripts/validate_tool.py`](../scripts/validate_tool.py) - Tool validation script

---

**Happy tool building! 🛠️**
