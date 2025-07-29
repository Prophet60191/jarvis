# Open Interpreter Quick Reference

## 🚀 Setup Commands

```bash
# Install Open Interpreter
pip install open-interpreter

# Install and setup Ollama
curl -fsSL https://ollama.ai/install.sh | sh
ollama pull llama3.1:8b

# Start Jarvis
cd jarvis && python -m jarvis.main
```

## 🎤 Voice Command Templates

### Code Execution
```
"Execute code to [task description]"
"Run code to [specific operation]"
"Calculate [mathematical expression]"
"Process [data description]"
```

### File Analysis
```
"Analyze [file path]"
"Examine the [file type] file at [location]"
"Review [file name] and [analysis request]"
"Show me the structure of [file]"
```

### Script Creation
```
"Create a [language] script to [purpose]"
"Generate [script type] for [task]"
"Write code to [functionality]"
"Build a [program type] that [description]"
```

### System Tasks
```
"Check my [system aspect]"
"Show [system information]"
"Monitor [resource] usage"
"Find [file criteria]"
"Clean up [location/type]"
```

## 🛠️ Available Tools

| Tool | Purpose | Example Command |
|------|---------|-----------------|
| `execute_code` | General code execution | "Execute code to sort this list" |
| `analyze_file` | File analysis | "Analyze data.csv" |
| `create_script` | Script generation | "Create a backup script" |
| `system_task` | System operations | "Check disk usage" |

## 📁 File Types Supported

### Data Files
- **CSV**: Spreadsheet data analysis
- **JSON**: Structured data processing
- **Excel**: Workbook analysis
- **XML**: Markup data parsing

### Code Files
- **Python**: .py files
- **JavaScript**: .js files
- **Java**: .java files
- **C/C++**: .c, .cpp files

### Text Files
- **Logs**: Error analysis, pattern detection
- **Config**: Configuration file review
- **Markdown**: Document processing

## 🎯 Common Use Cases

### Data Analysis
```
"Analyze sales.csv and show monthly trends"
"Process the survey data and create charts"
"Calculate statistics for the dataset"
```

### File Management
```
"Organize my Downloads folder by file type"
"Find duplicate files in my Documents"
"Backup important files to external drive"
```

### System Monitoring
```
"Check disk usage and show largest folders"
"Monitor CPU usage for 5 minutes"
"Show running processes using most memory"
```

### Automation
```
"Create a script to rename photos by date"
"Generate a daily backup automation"
"Build a file organizer for my desktop"
```

## 🔧 Configuration Options

### Open Interpreter Settings
```python
# In jarvis/tools/open_interpreter_direct.py
interpreter.offline = True                    # Local only
interpreter.auto_run = False                  # Ask permission
interpreter.llm.model = "ollama/llama3.1:8b" # Local model
interpreter.safe_mode = "ask"                # Safety first
```

### Customization Points
- **Model Selection**: Change LLM model
- **Safety Settings**: Adjust confirmation levels
- **Output Format**: Modify result presentation
- **Tool Behavior**: Customize tool responses

## 🚨 Troubleshooting

### Quick Fixes

| Issue | Solution |
|-------|----------|
| "Open Interpreter not available" | `pip install open-interpreter` |
| Slow responses | Check if Ollama model is loaded |
| Permission errors | Run with appropriate permissions |
| Code execution fails | Verify file paths and permissions |

### Debug Commands
```bash
# Check Open Interpreter installation
python -c "import interpreter; print('OK')"

# Verify Ollama is running
ollama list

# Test model availability
ollama run llama3.1:8b "Hello"
```

## 📊 Performance Tips

### Optimization
- Keep Ollama running in background
- Use specific file paths
- Break complex tasks into steps
- Cache frequently used scripts

### Best Practices
- Start with simple commands
- Provide clear, specific instructions
- Verify results before proceeding
- Save important scripts and outputs

## 🔒 Security Notes

### Safety Features
- **Local Execution**: No external API calls
- **Permission Checks**: Confirmation for dangerous operations
- **Sandboxing**: Controlled execution environment
- **Rollback**: Ability to undo changes

### Safe Usage
- Review code before execution
- Backup important data
- Use descriptive file names
- Monitor system resources

## 🎨 Advanced Patterns

### Complex Workflows
```
"Download data from API, analyze trends, create visualizations, and generate PDF report"
```

### Multi-step Operations
```
"Process all CSV files in folder, merge data, calculate summaries, and save results"
```

### System Integration
```
"Monitor log files, extract errors, send alerts, and create dashboard"
```

## 📚 Integration Points

### Plugin System
- Tools automatically registered
- No manual configuration needed
- Seamless integration with other plugins

### Voice Interface
- Natural language processing
- Context-aware responses
- Multi-turn conversations

### Error Handling
- Graceful degradation
- Informative error messages
- Recovery mechanisms

## 🎉 Quick Start Checklist

- [ ] Open Interpreter installed
- [ ] Ollama running with llama3.1:8b
- [ ] Jarvis started successfully
- [ ] Wake word "Jarvis" working
- [ ] Test command: "Check my disk usage"

## 📞 Support

### Getting Help
1. Check error logs in Jarvis output
2. Verify all prerequisites installed
3. Test with simple commands first
4. Restart Jarvis if needed

### Common Commands for Testing
```
"Execute code to print hello world"
"Check my disk usage"
"Create a simple Python script"
"Show system information"
```

---

**Ready to start voice programming? Say "Jarvis" and begin! 🎤**
