"""
Open Interpreter Guide Plugin for Jarvis Voice Assistant.

This plugin provides Jarvis with comprehensive knowledge about Open Interpreter
capabilities and helps guide users to successful task completion.
"""

import logging
from pathlib import Path
from typing import List

from langchain_core.tools import tool
from ..tools.base import BaseTool

logger = logging.getLogger(__name__)


@tool
def open_interpreter_help(query: str = "") -> str:
    """
    Get help and guidance about Open Interpreter capabilities in Jarvis.
    
    Use this tool when users ask about:
    - What Open Interpreter can do
    - How to use code execution features
    - Alternatives when something isn't possible
    - Examples of voice commands
    - Troubleshooting Open Interpreter issues
    
    Args:
        query: Specific question or topic about Open Interpreter (optional)
    
    Returns:
        Helpful information about Open Interpreter capabilities
    """
    
    # Core capabilities overview
    capabilities = """
🤖 Open Interpreter in Jarvis - What I Can Do:

📊 CODE EXECUTION:
• Mathematical calculations and data processing
• File operations (create, read, modify, organize)
• Data analysis with charts and visualizations
• Web scraping and API interactions
• Package installation and management
• Text processing and automation
• System monitoring and analysis

📁 FILE ANALYSIS:
• CSV/Excel: Statistical analysis, charts, trend detection
• JSON/XML: Structure analysis, data extraction
• Text files: Content analysis, pattern detection
• Code files: Syntax checking, complexity analysis
• Log files: Error detection, reporting

🛠️ SCRIPT CREATION:
• Python, JavaScript, Bash, PowerShell scripts
• Automation scripts (file organization, backups)
• Data processing and analysis scripts
• System administration tools
• Utility programs and calculators

⚙️ SYSTEM TASKS:
• Disk usage analysis and cleanup
• Process and memory monitoring
• File system operations
• Network connectivity testing
• System performance analysis

❌ WHAT I CANNOT DO:
• Open GUI applications (Terminal, browsers, etc.)
• Interact with running GUI applications
• Click buttons or type in other apps
• Real-time GUI interactions

💡 VOICE COMMAND EXAMPLES:
• "Execute code to calculate compound interest"
• "Analyze the CSV file in my Documents folder"
• "Create a Python script to organize my photos"
• "Check my disk usage and show largest folders"
• "Process this data and create a summary report"
"""
    
    # Specific query responses
    query_lower = query.lower()
    
    if "terminal" in query_lower or "open terminal" in query_lower:
        return """
🖥️ About Opening Terminal:

I can't open the Terminal application, but I can execute terminal commands for you!

INSTEAD OF opening Terminal, I can:
• Check your disk usage: "Check my disk usage"
• List files: "Show me files in my Documents folder"
• Find files: "Find all Python files in my projects"
• Run system commands: "Show running processes"
• Monitor system: "Check memory usage"

Just tell me what you want to do in the terminal, and I'll execute it for you!

EXAMPLE COMMANDS:
• "Execute code to check system information"
• "Run a command to find large files"
• "Show me the contents of my home directory"
"""
    
    elif "browser" in query_lower or "open browser" in query_lower:
        return """
🌐 About Opening Browser:

I can't open GUI applications like browsers, but I can help with web-related tasks!

INSTEAD OF opening a browser, I can:
• Download files from URLs
• Scrape website content
• Check if websites are online
• Process web data and APIs
• Download images or documents
• Extract information from web pages

EXAMPLE COMMANDS:
• "Download the file from this URL"
• "Check if google.com is accessible"
• "Scrape the headlines from this news site"
• "Download all images from this webpage"
"""
    
    elif "file" in query_lower or "analyze" in query_lower:
        return """
📁 File Analysis Capabilities:

I can analyze almost any file type with powerful code execution!

SUPPORTED FILE TYPES:
• CSV/Excel: Statistical analysis, charts, data visualization
• JSON: Structure analysis, data extraction, validation
• Text files: Content analysis, pattern detection, summaries
• Code files: Syntax checking, complexity analysis, documentation
• Log files: Error detection, pattern analysis, reporting
• Images: Metadata extraction, basic image processing

ANALYSIS TYPES:
• General: Overall file overview and insights
• Data: Statistical analysis with charts and graphs
• Code: Structure and quality analysis
• Text: Content summary and pattern detection
• Statistical: Detailed statistical analysis

EXAMPLE COMMANDS:
• "Analyze the sales data CSV and show monthly trends"
• "Examine this log file for errors"
• "Review this Python script for issues"
• "Process this JSON file and extract key information"
"""
    
    elif "script" in query_lower or "create" in query_lower:
        return """
🛠️ Script Creation Capabilities:

I can create scripts in multiple programming languages!

SUPPORTED LANGUAGES:
• Python: Data processing, automation, web development
• JavaScript: Web applications, Node.js scripts
• Bash: System administration, file operations
• PowerShell: Windows automation and management
• Shell: Unix/Linux system tasks

SCRIPT TYPES I CAN CREATE:
• File organization and automation scripts
• Data processing and analysis scripts
• System administration and monitoring tools
• Backup and maintenance scripts
• Web scrapers and data collectors
• Utility programs and calculators

EXAMPLE COMMANDS:
• "Create a Python script to organize my Downloads folder"
• "Generate a backup script for my documents"
• "Write a script to monitor system resources"
• "Create a data processing script for CSV files"
"""
    
    elif "system" in query_lower or "disk" in query_lower or "monitor" in query_lower:
        return """
⚙️ System Task Capabilities:

I can perform comprehensive system analysis and maintenance!

SYSTEM OPERATIONS:
• Disk usage analysis and cleanup
• Process monitoring and management
• Memory usage analysis and optimization
• Network connectivity testing
• File system operations and organization
• Software installation and updates
• System performance monitoring
• Log file analysis and reporting
• Backup and restore operations

EXAMPLE COMMANDS:
• "Check my disk usage and show largest folders"
• "Monitor CPU and memory usage"
• "Find and clean up temporary files"
• "Show running processes using most memory"
• "Analyze system logs for errors"
• "Create a system performance report"

I can help you maintain and monitor your system effectively!
"""
    
    elif "error" in query_lower or "problem" in query_lower or "not working" in query_lower:
        return """
🚨 Troubleshooting Open Interpreter:

If Open Interpreter isn't working properly:

COMMON ISSUES & SOLUTIONS:
• "Open Interpreter not available": Run `pip install open-interpreter`
• Slow responses: Check if Ollama model is loaded
• Permission errors: Ensure proper file/folder permissions
• Code execution fails: Verify file paths are correct

QUICK TESTS:
• "Execute code to print hello world" (basic test)
• "Check my disk usage" (system test)
• "Calculate 2 plus 2" (math test)

If problems persist:
1. Restart Jarvis
2. Check that Ollama is running: `ollama list`
3. Verify the model is available: `ollama pull llama3.1:8b`

I'm here to help you get everything working smoothly!
"""
    
    # Default response with full capabilities
    return capabilities


@tool
def suggest_alternatives(impossible_task: str) -> str:
    """
    Suggest alternatives when users request something Open Interpreter cannot do.
    
    Use this when users ask for:
    - Opening GUI applications
    - Interacting with running applications
    - Tasks that require GUI interaction
    
    Args:
        impossible_task: Description of what the user asked for that isn't possible
    
    Returns:
        Helpful alternatives and suggestions
    """
    
    task_lower = impossible_task.lower()
    
    if "terminal" in task_lower or "command prompt" in task_lower:
        return """
Instead of opening Terminal, I can execute terminal commands directly for you!

WHAT I CAN DO:
• Run any terminal command you need
• Check system information and resources
• Manage files and directories
• Monitor processes and performance
• Install software and packages

JUST SAY:
• "Check my disk usage"
• "Show files in my Documents folder"
• "Find Python files in my projects"
• "Monitor system performance"
• "Run [specific command]"

What would you like me to do in the terminal?
"""
    
    elif "browser" in task_lower or "chrome" in task_lower or "safari" in task_lower:
        return """
Instead of opening a browser, I can handle web tasks directly!

WHAT I CAN DO:
• Download files from URLs
• Scrape website content and data
• Check website availability
• Process web APIs and data
• Extract information from web pages

JUST SAY:
• "Download this file: [URL]"
• "Check if [website] is online"
• "Scrape data from [website]"
• "Download images from [webpage]"

What web-related task can I help you with?
"""
    
    elif any(app in task_lower for app in ["finder", "file explorer", "files", "folders"]):
        return """
Instead of opening file managers, I can handle file operations directly!

WHAT I CAN DO:
• List and organize files and folders
• Find files by name, type, or content
• Analyze file sizes and disk usage
• Create, move, copy, or delete files
• Organize files by date, type, or custom rules

JUST SAY:
• "Show files in my Documents folder"
• "Find large files taking up space"
• "Organize my Downloads folder"
• "Create a backup of my important files"

What file operation can I help you with?
"""
    
    else:
        return f"""
I can't directly do "{impossible_task}", but I can help you accomplish your goal in other ways!

INSTEAD, I CAN:
• Execute code to perform the underlying task
• Analyze and process data or files
• Create scripts to automate similar tasks
• Perform system operations and monitoring

Could you tell me more about what you're trying to accomplish? I can suggest specific alternatives that will get you the same result!
"""


class OpenInterpreterGuidePlugin:
    """Plugin that provides Open Interpreter guidance and help."""
    
    def get_tools(self) -> List[BaseTool]:
        """Return the Open Interpreter guide tools."""
        return [open_interpreter_help, suggest_alternatives]
    
    def get_name(self) -> str:
        """Return the plugin name."""
        return "Open Interpreter Guide"
    
    def get_description(self) -> str:
        """Return the plugin description."""
        return "Provides comprehensive guidance and help for Open Interpreter usage"


# Plugin instance for automatic discovery
plugin = OpenInterpreterGuidePlugin()
