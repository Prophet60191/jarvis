"""
User Help Tool Plugin

Provides voice command integration for the Jarvis User Help UI,
allowing users to open, search, and close the help interface via voice commands.
"""

import subprocess
import sys
import time
import psutil
from pathlib import Path
from typing import Dict, Any, Optional, List

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Global process tracking
_help_ui_process = None
_help_ui_pid = None

def get_metadata() -> Dict[str, Any]:
    """Get tool metadata for Jarvis plugin system."""
    return {
        "name": "user_help_tool",
        "version": "1.0.0",
        "description": "Voice-controlled User Help UI for Jarvis documentation",
        "author": "Jarvis Team",
        "capabilities": [
            "documentation_access",
            "help_interface",
            "voice_controlled_ui",
            "search_documentation",
            "bookmark_management"
        ],
        "dependencies": ["PyQt6"],
        "voice_commands": [
            "open user help",
            "show user help",
            "open help",
            "show documentation",
            "close user help",
            "close help",
            "search help for [query]"
        ],
        "ui_integration": True,
        "process_management": True
    }

def open_user_help(**kwargs) -> Dict[str, Any]:
    """
    Open the Jarvis User Help UI.
    
    Voice commands:
    - "Hey Jarvis, open user help"
    - "Hey Jarvis, show user help"
    - "Hey Jarvis, open help"
    - "Hey Jarvis, show documentation"
    
    Returns:
        Dict with operation status and details
    """
    global _help_ui_process, _help_ui_pid
    
    try:
        # Check if help UI is already running
        if _help_ui_process and _help_ui_process.poll() is None:
            return {
                "success": True,
                "message": "User Help is already open",
                "action": "focus_existing",
                "process_id": _help_ui_pid
            }
        
        # Path to the help UI script - use the launcher for simplicity
        help_ui_script = project_root / "launch_user_help.py"
        
        if not help_ui_script.exists():
            return {
                "success": False,
                "error": "User Help UI script not found",
                "message": "The help interface is not available. Please check the installation.",
                "file_path": str(help_ui_script)
            }
        
        # Launch the help UI
        _help_ui_process = subprocess.Popen([
            sys.executable, str(help_ui_script)
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        _help_ui_pid = _help_ui_process.pid
        
        # Give it a moment to start
        time.sleep(1)
        
        # Check if it started successfully
        if _help_ui_process.poll() is None:
            return {
                "success": True,
                "message": "User Help opened successfully",
                "action": "opened",
                "process_id": _help_ui_pid,
                "instructions": "You can now search documentation, browse guides, and bookmark important pages."
            }
        else:
            # Process failed to start
            stdout, stderr = _help_ui_process.communicate()
            return {
                "success": False,
                "error": "Failed to start User Help UI",
                "message": "The help interface could not be launched.",
                "stdout": stdout.decode() if stdout else "",
                "stderr": stderr.decode() if stderr else ""
            }
    
    except Exception as e:
        return {
            "success": False,
            "error": f"Error opening User Help: {str(e)}",
            "message": "An error occurred while trying to open the help interface."
        }

def close_user_help(**kwargs) -> Dict[str, Any]:
    """
    Close the Jarvis User Help UI.
    
    Voice commands:
    - "Hey Jarvis, close user help"
    - "Hey Jarvis, close help"
    
    Returns:
        Dict with operation status and details
    """
    global _help_ui_process, _help_ui_pid
    
    try:
        closed_processes = []
        
        # Try to close the tracked process first
        if _help_ui_process and _help_ui_process.poll() is None:
            try:
                _help_ui_process.terminate()
                _help_ui_process.wait(timeout=5)
                closed_processes.append(_help_ui_pid)
                _help_ui_process = None
                _help_ui_pid = None
            except subprocess.TimeoutExpired:
                _help_ui_process.kill()
                _help_ui_process.wait()
                closed_processes.append(_help_ui_pid)
                _help_ui_process = None
                _help_ui_pid = None
        
        # Also search for any other help UI processes
        help_processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = proc.info['cmdline']
                if cmdline and any('user_help_ui.py' in arg for arg in cmdline):
                    help_processes.append(proc)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        # Close any found processes
        for proc in help_processes:
            try:
                proc.terminate()
                proc.wait(timeout=3)
                closed_processes.append(proc.pid)
            except (psutil.TimeoutExpired, psutil.NoSuchProcess):
                try:
                    proc.kill()
                    closed_processes.append(proc.pid)
                except psutil.NoSuchProcess:
                    pass
        
        if closed_processes:
            return {
                "success": True,
                "message": "User Help closed successfully",
                "action": "closed",
                "closed_processes": closed_processes
            }
        else:
            return {
                "success": True,
                "message": "User Help was not running",
                "action": "not_running"
            }
    
    except Exception as e:
        return {
            "success": False,
            "error": f"Error closing User Help: {str(e)}",
            "message": "An error occurred while trying to close the help interface."
        }

def search_help(query: str = "", **kwargs) -> Dict[str, Any]:
    """
    Search the User Help documentation.
    
    Voice commands:
    - "Hey Jarvis, search help for [query]"
    
    Args:
        query: Search term to look for in documentation
    
    Returns:
        Dict with search results and status
    """
    try:
        if not query:
            return {
                "success": False,
                "error": "No search query provided",
                "message": "Please specify what you'd like to search for in the help documentation."
            }
        
        # First, ensure help UI is open
        help_status = open_user_help()
        if not help_status["success"]:
            return help_status
        
        # Note: In a full implementation, we could send the search query
        # to the help UI via IPC (Inter-Process Communication)
        # For now, we'll just open the help and inform the user
        
        return {
            "success": True,
            "message": f"User Help opened. Please search for '{query}' using the search box.",
            "action": "search_requested",
            "query": query,
            "instructions": f"I've opened the User Help interface. You can now search for '{query}' using the search box at the top left."
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": f"Error searching help: {str(e)}",
            "message": "An error occurred while trying to search the help documentation."
        }

def get_help_status(**kwargs) -> Dict[str, Any]:
    """
    Get the current status of the User Help UI.
    
    Returns:
        Dict with current status information
    """
    global _help_ui_process, _help_ui_pid
    
    try:
        is_running = False
        process_info = {}
        
        # Check tracked process
        if _help_ui_process and _help_ui_process.poll() is None:
            is_running = True
            process_info["tracked_pid"] = _help_ui_pid
        
        # Check for any help UI processes
        help_processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'create_time']):
            try:
                cmdline = proc.info['cmdline']
                if cmdline and any('user_help_ui.py' in arg for arg in cmdline):
                    help_processes.append({
                        "pid": proc.info['pid'],
                        "name": proc.info['name'],
                        "create_time": proc.info['create_time']
                    })
                    is_running = True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        return {
            "success": True,
            "is_running": is_running,
            "tracked_process": _help_ui_pid,
            "all_processes": help_processes,
            "process_count": len(help_processes)
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": f"Error checking help status: {str(e)}"
        }

def show_help_info(**kwargs) -> Dict[str, Any]:
    """
    Show information about the User Help system.
    
    Voice commands:
    - "Hey Jarvis, tell me about user help"
    - "Hey Jarvis, what is user help"
    
    Returns:
        Dict with help system information
    """
    return {
        "success": True,
        "message": "Jarvis User Help provides comprehensive documentation access",
        "features": [
            "Search through all Jarvis documentation",
            "Browse guides and references",
            "Bookmark important pages",
            "Voice command integration",
            "Clean, accessible interface"
        ],
        "voice_commands": [
            "Open user help - Opens the help interface",
            "Close user help - Closes the help interface", 
            "Search help for [topic] - Opens help and suggests search"
        ],
        "documentation_included": [
            "Getting Started Guide",
            "Voice Commands Reference",
            "User Guide",
            "Analytics Dashboard Guide",
            "Troubleshooting Guide",
            "RAG Memory User Guide",
            "Plugin Reference Guide",
            "Device Time Tool Guide",
            "Aider Integration Guide",
            "LaVague Web Automation Guide",
            "Log Terminal Tools Guide",
            "Open Interpreter User Guide",
            "Robot Framework User Guide",
            "Architecture Documentation",
            "System Integration Guide",
            "Performance Optimization Guide",
            "And more comprehensive guides..."
        ]
    }

# Tool registration for Jarvis
TOOLS = [
    {
        "name": "open_user_help",
        "function": open_user_help,
        "description": "Open the Jarvis User Help documentation interface",
        "voice_commands": [
            "open user help",
            "show user help", 
            "open help",
            "show documentation"
        ]
    },
    {
        "name": "close_user_help", 
        "function": close_user_help,
        "description": "Close the Jarvis User Help documentation interface",
        "voice_commands": [
            "close user help",
            "close help"
        ]
    },
    {
        "name": "search_help",
        "function": search_help,
        "description": "Search the Jarvis help documentation",
        "voice_commands": [
            "search help for {query}"
        ],
        "parameters": {
            "query": {
                "type": "string",
                "description": "Search term to look for in documentation",
                "required": True
            }
        }
    },
    {
        "name": "get_help_status",
        "function": get_help_status,
        "description": "Check if the User Help UI is currently running",
        "voice_commands": [
            "is help open",
            "check help status"
        ]
    },
    {
        "name": "show_help_info",
        "function": show_help_info,
        "description": "Show information about the User Help system",
        "voice_commands": [
            "tell me about user help",
            "what is user help",
            "help info"
        ]
    }
]

if __name__ == "__main__":
    # Test the tool functions
    print("Testing User Help Tool...")
    
    # Test opening help
    result = open_user_help()
    print(f"Open result: {result}")
    
    # Wait a moment
    time.sleep(2)
    
    # Test status
    status = get_help_status()
    print(f"Status: {status}")
    
    # Test closing help
    close_result = close_user_help()
    print(f"Close result: {close_result}")
