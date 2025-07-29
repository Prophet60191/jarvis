"""
Direct Open Interpreter Integration for Jarvis Voice Assistant.

This module provides a simple, direct integration with Open Interpreter,
bypassing the complex MCP protocol for maximum reliability and performance.
"""

import logging
import os
from typing import List, Optional, Dict, Any
from pathlib import Path

from langchain_core.tools import tool
from langchain_core.tools import BaseTool

logger = logging.getLogger(__name__)

# Global interpreter instance for session persistence
_interpreter_instance = None


def get_interpreter():
    """Get or create the Open Interpreter instance."""
    global _interpreter_instance
    
    if _interpreter_instance is None:
        try:
            import interpreter
            
            # Create OpenInterpreter instance
            _interpreter_instance = interpreter.OpenInterpreter()
            
            # Configure for local-only execution
            _interpreter_instance.offline = True
            _interpreter_instance.auto_run = False  # Ask for permission before running code
            
            # Configure for local Ollama
            _interpreter_instance.llm.model = "ollama/llama3.1:8b"
            _interpreter_instance.llm.api_base = "http://localhost:11434"
            
            # Configure safety settings
            _interpreter_instance.safe_mode = "ask"
            _interpreter_instance.shrink_images = True
            
            logger.info("Open Interpreter initialized in local mode")
            
        except ImportError:
            logger.error("Open Interpreter not installed. Run: pip install open-interpreter")
            return None
        except Exception as e:
            logger.error(f"Failed to initialize Open Interpreter: {e}")
            return None
    
    return _interpreter_instance


@tool
def execute_code(task_description: str) -> str:
    """
    Execute code to accomplish a task using Open Interpreter running locally.
    
    Use this tool when the user asks you to:
    - Analyze data or create visualizations
    - Manipulate files or directories
    - Perform calculations or data processing
    - Create scripts or automate tasks
    - Install packages or manage dependencies
    - Interact with APIs or web services
    - Generate reports or documents
    - Perform system administration tasks
    
    Examples of when to use:
    - "Analyze this CSV file and create a chart"
    - "Create a Python script to organize my photos"
    - "Calculate the average of these numbers"
    - "Download data from this API and save it"
    - "Create a backup of my documents folder"
    - "Generate a report from this data"
    - "Check my disk usage and show largest folders"
    
    Args:
        task_description: Clear description of what you want to accomplish
    
    Returns:
        Result of the code execution or error message
    """
    interpreter = get_interpreter()
    if not interpreter:
        return "Open Interpreter is not available. Please install it with: pip install open-interpreter"
    
    try:
        logger.info(f"Executing task: {task_description}")
        
        # Use chat method to interact with interpreter
        messages = interpreter.chat(task_description, display=False, stream=False)
        
        # Extract the result from messages
        result_parts = []
        for message in messages:
            if message.get("type") == "message":
                content = message.get("content", "")
                if content:
                    result_parts.append(content)
            elif message.get("type") == "code":
                # Show what code was executed
                language = message.get("format", "unknown")
                code = message.get("content", "")
                result_parts.append(f"Executed {language} code:\n```{language}\n{code}\n```")
        
        result = "\n\n".join(result_parts) if result_parts else "Task completed successfully"
        logger.info("Code execution completed successfully")
        return result
        
    except Exception as e:
        error_msg = f"Error executing code: {str(e)}"
        logger.error(error_msg)
        return error_msg


@tool
def analyze_file(file_path: str, analysis_type: str = "general") -> str:
    """
    Analyze a file using Open Interpreter's code execution capabilities.
    
    Use this tool when the user wants to:
    - Analyze data files (CSV, JSON, Excel, etc.)
    - Examine code files for structure or issues
    - Process text files or documents
    - Extract information from files
    - Generate summaries or reports from file content
    
    Args:
        file_path: Path to the file to analyze
        analysis_type: Type of analysis - 'general', 'data', 'code', 'text', 'statistical'
    
    Returns:
        Analysis results or error message
    """
    if not os.path.exists(file_path):
        return f"File not found: {file_path}"
    
    # Create analysis prompt based on type
    analysis_prompts = {
        "general": f"Analyze the file at '{file_path}' and provide a comprehensive overview of its contents, structure, and key insights.",
        "data": f"Perform a detailed data analysis of '{file_path}'. Include statistics, patterns, and visualizations if appropriate.",
        "code": f"Analyze the code in '{file_path}'. Check for structure, potential issues, and provide insights about functionality.",
        "text": f"Analyze the text content in '{file_path}'. Provide a summary, key themes, and any notable patterns.",
        "statistical": f"Perform statistical analysis on the data in '{file_path}'. Include descriptive statistics, distributions, and correlations."
    }
    
    prompt = analysis_prompts.get(analysis_type, analysis_prompts["general"])
    return execute_code(prompt)


@tool
def create_script(description: str, language: str = "python", save_path: Optional[str] = None) -> str:
    """
    Create a script file using Open Interpreter.
    
    Use this tool when the user wants to:
    - Create automation scripts
    - Generate utility programs
    - Build data processing scripts
    - Create system administration tools
    
    Args:
        description: What the script should do
        language: Programming language ('python', 'javascript', 'bash', etc.)
        save_path: Optional path to save the script
    
    Returns:
        Script creation result
    """
    prompt = f"Create a {language} script that {description}."
    if save_path:
        prompt += f" Save it to '{save_path}'."
    
    return execute_code(prompt)


@tool
def system_task(task: str) -> str:
    """
    Perform system administration or file management tasks.
    
    Use this tool when the user wants to:
    - Manage files and directories
    - Check system information (disk usage, memory, processes)
    - Install or update software
    - Monitor system resources
    - Perform maintenance tasks
    
    Args:
        task: Description of the system task to perform
    
    Returns:
        Task execution result
    """
    return execute_code(f"Perform this system task: {task}")


def get_open_interpreter_tools() -> List[BaseTool]:
    """
    Get all Open Interpreter tools as LangChain tools.
    
    Returns:
        List of LangChain-compatible tools
    """
    return [execute_code, analyze_file, create_script, system_task]


def is_open_interpreter_available() -> bool:
    """
    Check if Open Interpreter is available and properly configured.
    
    Returns:
        True if Open Interpreter is available, False otherwise
    """
    interpreter = get_interpreter()
    return interpreter is not None


# Export tools for easy import
__all__ = [
    "execute_code",
    "analyze_file", 
    "create_script",
    "system_task",
    "get_open_interpreter_tools",
    "is_open_interpreter_available"
]
