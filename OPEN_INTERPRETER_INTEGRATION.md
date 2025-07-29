# Open Interpreter Integration with Jarvis Voice Assistant

## 🎯 Overview

This integration adds powerful local code execution capabilities to Jarvis using Open Interpreter, enabling your voice assistant to:

- **Execute code locally** in Python, JavaScript, Shell, and more
- **Analyze data** and create visualizations
- **Manipulate files** and automate system tasks
- **Create scripts** and tools on demand
- **Process documents** and extract information
- **Perform calculations** and data analysis

**🔒 Privacy First**: Everything runs locally on your machine - no cloud services, no data sharing.

## 🏗️ Architecture

### Local-Only Execution
```
Voice Command → Jarvis Agent → Open Interpreter Plugin → Local Code Execution
     ↓                                                           ↓
User Speech ←─── TTS Response ←─── Result Processing ←─── Local Results
```

### Integration Points
- **LLM**: Uses your existing Ollama llama3.1:8b model
- **Execution**: All code runs on your local machine
- **Safety**: Asks permission before running potentially dangerous code
- **Memory**: Maintains session context for follow-up commands

## 🚀 Installation & Setup

### 1. Run the Setup Script
```bash
python setup_open_interpreter.py
```

This script will:
- ✅ Check that Ollama is running with llama3.1:8b
- ✅ Install Open Interpreter and dependencies
- ✅ Configure for local-only operation
- ✅ Test the integration
- ✅ Create usage examples

### 2. Manual Installation (Alternative)
```bash
# Install Open Interpreter
pip install open-interpreter

# Install optional dependencies for enhanced functionality
pip install matplotlib pandas requests beautifulsoup4 pillow

# Ensure Ollama is running
ollama serve

# Ensure you have the required model
ollama pull llama3.1:8b
```

### 3. Restart Jarvis
After installation, restart Jarvis to load the new plugin:
```bash
python start_jarvis.py
```

## 🎤 Voice Commands & Examples

### Data Analysis
```
"Analyze this CSV file and create a chart"
"Calculate the average of the numbers in this spreadsheet"
"Show me the correlation between these columns"
"Create a histogram of this data"
```

### File Management
```
"Create a backup of my documents folder"
"Organize my photos by date"
"Find all PDF files larger than 10MB"
"Rename all files in this folder to lowercase"
```

### Code Creation
```
"Create a Python script to download images from URLs"
"Write a script to convert CSV to JSON"
"Generate a web scraper for this website"
"Create a utility to monitor disk space"
```

### System Administration
```
"Check my disk usage and show a summary"
"List all running processes using more than 100MB RAM"
"Update all my Python packages"
"Check which ports are open on my system"
```

### Web & API Tasks
```
"Download data from this REST API"
"Scrape the headlines from this news website"
"Check if my website is online"
"Get the weather data for my location"
```

### Document Processing
```
"Extract text from this PDF file"
"Convert this Word document to plain text"
"Analyze the sentiment of this text file"
"Create a summary of this document"
```

## 🛠️ Available Tools

### 1. `execute_code`
**Purpose**: General code execution for any task
**Usage**: "Execute code to [task description]"
**Features**:
- Multi-language support (Python, JavaScript, Shell, etc.)
- Session persistence
- Safety checks

### 2. `analyze_file`
**Purpose**: Analyze files with code
**Usage**: "Analyze this file: [file_path]"
**Types**:
- `general`: Overall analysis
- `data`: Statistical analysis
- `code`: Code structure analysis
- `text`: Text content analysis

### 3. `create_script`
**Purpose**: Generate scripts and programs
**Usage**: "Create a [language] script that [description]"
**Languages**: Python, JavaScript, Bash, PowerShell, etc.

### 4. `system_task`
**Purpose**: System administration and maintenance
**Usage**: "Perform this system task: [description]"
**Capabilities**: File management, system monitoring, software installation

## 🔒 Security & Safety Features

### Local Execution Only
- **No Cloud**: All processing happens on your machine
- **No API Calls**: Uses your local Ollama instance
- **No Data Sharing**: Nothing leaves your computer

### Permission System
- **Safe Mode**: Asks before running potentially dangerous code
- **Code Review**: Shows you the code before execution
- **User Control**: You approve or deny each execution

### Sandboxing
- **Isolated Environment**: Code runs in controlled context
- **Resource Limits**: Prevents runaway processes
- **Error Handling**: Graceful failure recovery

## ⚙️ Configuration

### Default Settings
```python
# Open Interpreter Configuration
offline = True                    # No internet required
auto_run = False                 # Ask permission before running code
safe_mode = "ask"               # Safety checks enabled
model = "ollama/llama3.1:8b"    # Use your local model
api_base = "http://localhost:11434"  # Local Ollama server
```

### Customization
You can modify settings in `jarvis/tools/plugins/open_interpreter_tool.py`:

```python
# In get_interpreter() function
_interpreter_instance.auto_run = True  # Auto-run trusted code
_interpreter_instance.safe_mode = "off"  # Disable safety (not recommended)
```

## 🧪 Testing the Integration

### Basic Test
```
You: "What is 2 + 2? Calculate it with code."
Jarvis: [Shows Python code] "print(2 + 2)"
Jarvis: "The result is 4."
```

### File Analysis Test
```
You: "Analyze the data in my sales.csv file"
Jarvis: [Executes pandas code to analyze the CSV]
Jarvis: "I found 1,250 sales records. The average sale amount is $156.78..."
```

### Script Creation Test
```
You: "Create a Python script to organize my downloads folder"
Jarvis: [Generates and shows Python script]
Jarvis: "I've created a script that organizes files by type. Should I run it?"
```

## 🔧 Troubleshooting

### Common Issues

#### 1. "Open Interpreter not available"
**Solution**: Run the setup script or install manually:
```bash
pip install open-interpreter
```

#### 2. "Connection to Ollama failed"
**Solution**: Ensure Ollama is running:
```bash
ollama serve
```

#### 3. "Model not found"
**Solution**: Install the required model:
```bash
ollama pull llama3.1:8b
```

#### 4. "Permission denied" errors
**Solution**: Check file permissions and run with appropriate privileges

### Debug Mode
Enable debug logging in Jarvis to see detailed execution information:
```python
# In jarvis config
logging.level = "DEBUG"
```

### Log Files
Check these locations for error information:
- Jarvis logs: `jarvis_debug.log`
- Open Interpreter logs: `~/.config/open-interpreter/logs/`

## 🚀 Advanced Usage

### Session Persistence
Open Interpreter maintains context across commands:
```
You: "Create a list of numbers from 1 to 10"
Jarvis: [Creates the list]
You: "Now calculate the sum of that list"
Jarvis: [Uses the previously created list]
```

### Multi-step Tasks
```
You: "Download this dataset, clean it, and create a visualization"
Jarvis: [Executes multiple code blocks in sequence]
```

### Integration with Jarvis RAG
Combine with Jarvis's memory system:
```
You: "Remember that I prefer matplotlib for charts"
[Later]
You: "Create a chart from this data"
Jarvis: [Uses matplotlib based on your preference]
```

## 📊 Performance Considerations

### Resource Usage
- **CPU**: Code execution uses local CPU resources
- **Memory**: Large datasets may require significant RAM
- **Storage**: Generated files and logs consume disk space

### Optimization Tips
- Use efficient algorithms for large datasets
- Clean up temporary files regularly
- Monitor system resources during heavy tasks

## 🔮 Future Enhancements

### Planned Features
- **Code Templates**: Pre-built scripts for common tasks
- **Result Caching**: Cache results for repeated operations
- **Enhanced Safety**: More sophisticated code analysis
- **GUI Integration**: Visual code editor and results viewer

### Community Contributions
- Submit plugin improvements via GitHub
- Share useful code templates and examples
- Report bugs and suggest features

## 📚 Additional Resources

- [Open Interpreter Documentation](https://docs.openinterpreter.com/)
- [Jarvis Plugin Development Guide](docs/TOOL_DEVELOPMENT_GUIDE.md)
- [Ollama Documentation](https://ollama.ai/docs)
- [Usage Examples](OPEN_INTERPRETER_USAGE.md)

---

**🎉 Enjoy your enhanced Jarvis with powerful local code execution capabilities!**
