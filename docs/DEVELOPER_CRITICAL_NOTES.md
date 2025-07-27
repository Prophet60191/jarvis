# 🚨 CRITICAL DEVELOPER NOTES

## ⚠️ **MUST READ BEFORE DEVELOPING TOOLS**

This document contains critical information discovered through research and debugging that **MUST** be followed for successful tool development.

## 🔥 **Critical Rules (Non-Negotiable)**

### 1. **File Location**
```
✅ CORRECT: jarvis/tools/plugins/your_tool.py
❌ WRONG:   tools/plugins/your_tool.py
❌ WRONG:   plugins/your_tool.py
❌ WRONG:   jarvis/plugins/your_tool.py
```

**Why**: The MCP plugin discovery system searches directories in this order:
1. `jarvis/tools/plugins/` ← **Your plugins go here**
2. `jarvis/plugins/builtin/`
3. `~/.jarvis/plugins/`
4. `./plugins/`

### 2. **Function Name = Tool Name**
```python
# ✅ CORRECT: Descriptive, specific names
@tool
def get_current_time() -> str:  # Tool name: "get_current_time"

@tool  
def calculate_fibonacci(n: int) -> int:  # Tool name: "calculate_fibonacci"

# ❌ WRONG: Generic, conflict-prone names
@tool
def get_time() -> str:  # Too generic, may conflict

@tool
def process(data: str) -> str:  # Too vague
```

**Why**: LangChain's `@tool` decorator automatically uses the function name as the tool identifier. Generic names cause conflicts.

### 3. **Plugin Generator Default Location**
```bash
# This command creates files in the CORRECT location
python manage_plugins.py generate my_tool --type tool --author "Your Name"
# Creates: jarvis/tools/plugins/my_tool.py
```

**Why**: We fixed the plugin generator to use the correct default directory.

## 🧪 **Verification Steps**

### 1. Check Plugin Discovery
```bash
python manage_plugins.py list
# Should show your plugin
```

### 2. Verify Tool Loading
```bash
python -m jarvis.main
# Check logs for: "Loaded X tools: ['your_tool_name', ...]"
```

### 3. Test Tool Function
```python
from jarvis.tools.plugins.your_tool import your_function
result = your_function.invoke({})
print(result)
```

## 🐛 **Common Issues & Solutions**

### Issue: Plugin Not Discovered
```
❌ Problem: "Loaded 0 plugin tools"
✅ Solution: Move file to jarvis/tools/plugins/
```

### Issue: Tool Name Conflicts
```
❌ Problem: "The current time is [get_time_tool()]"
✅ Solution: Use specific function names like get_current_time()
```

### Issue: Import Errors
```
❌ Problem: "NameError: name 'tool_registry' is not defined"
✅ Solution: Ensure proper imports in main.py (already fixed)
```

## 📚 **Research Sources Applied**

1. **LangChain Documentation**: Function name becomes tool name
2. **MCP Best Practices**: Plugin directory structure requirements
3. **Debugging Experience**: Real-world issues and solutions

## 🎯 **Success Checklist**

- [ ] File in `jarvis/tools/plugins/`
- [ ] Descriptive function name
- [ ] `@tool` decorator from `langchain_core.tools`
- [ ] Plugin metadata with `PLUGIN_CLASS` and `PLUGIN_METADATA`
- [ ] Verified with `python manage_plugins.py list`
- [ ] Tested tool loading in Jarvis

## 🚀 **Quick Template**

```python
"""
Your Tool Plugin for Jarvis Voice Assistant.

Author: Your Name
"""

import logging
from typing import List
from langchain_core.tools import BaseTool, tool
from jarvis.plugins.base import PluginBase, PluginMetadata

logger = logging.getLogger(__name__)

@tool
def your_descriptive_function_name(param: str) -> str:
    """
    Clear description of what your tool does.
    
    Args:
        param: Description of parameter
        
    Returns:
        str: Description of return value
    """
    try:
        result = f"Processed: {param}"
        logger.info(f"Tool executed successfully")
        return result
    except Exception as e:
        logger.error(f"Tool error: {e}")
        return f"Error: {str(e)}"

class YourToolPlugin(PluginBase):
    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="YourTool",
            version="1.0.0",
            description="Your tool description",
            author="Your Name"
        )
    
    def get_tools(self) -> List[BaseTool]:
        return [your_descriptive_function_name]

# Required for plugin discovery
PLUGIN_CLASS = YourToolPlugin
PLUGIN_METADATA = YourToolPlugin().get_metadata()
```

## 🔗 **Related Documentation**

- [TOOL_DEVELOPMENT_GUIDE.md](TOOL_DEVELOPMENT_GUIDE.md) - Comprehensive guide
- [TOOL_QUICK_REFERENCE.md](TOOL_QUICK_REFERENCE.md) - Quick reference
- [MCP_SYSTEM_OVERVIEW.md](MCP_SYSTEM_OVERVIEW.md) - Architecture overview

**Remember**: These rules are based on actual debugging and research. Following them prevents hours of troubleshooting!
