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

**Remember**: These rules are based on actual debugging and research. Following them prevents hours of troubleshooting!
