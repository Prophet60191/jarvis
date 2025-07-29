"""
Aider Integration Plugin for Jarvis Voice Assistant.

This plugin provides seamless handoff between Jarvis and Aider for advanced code editing,
allowing voice commands to trigger Aider sessions and return control to Jarvis.
"""

import asyncio
import logging
import os
import subprocess
import tempfile
import time
from pathlib import Path
from typing import List, Optional, Dict, Any

from langchain_core.tools import tool
from jarvis.tools.base import BaseTool
from jarvis.plugins.base import PluginBase, PluginMetadata

logger = logging.getLogger(__name__)


@tool
def aider_code_edit(task_description: str, files: str = "", auto_commit: bool = True, model: str = "gpt-4") -> str:
    """
    Hand off code editing tasks to Aider AI for advanced code manipulation.
    
    Use this tool when users ask to:
    - "Edit this file to add [feature]"
    - "Refactor this code to [improvement]"
    - "Fix the bug in [file]"
    - "Add error handling to [function]"
    - "Update all imports in the project"
    - "Rename this class everywhere"
    - "Apply this pattern to all similar functions"
    
    Args:
        task_description: Natural language description of what to edit/change
        files: Specific files to work with (optional, can be inferred)
        auto_commit: Whether to automatically commit changes (default: True)
        model: AI model for Aider to use (default: gpt-4)
    
    Returns:
        Results of the Aider session and what was changed
    """
    try:
        logger.info(f"🔄 Handing off to Aider: {task_description}")
        
        # Check if Aider is installed
        try:
            subprocess.run(["aider", "--version"], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            return "❌ Aider is not installed. Please install with: pip install aider-chat"
        
        # Get current working directory (should be the project root)
        cwd = Path.cwd()
        
        # Build Aider command
        cmd = ["aider"]
        
        # Add model specification
        cmd.extend(["--model", model])
        
        # Add auto-commit if requested
        if auto_commit:
            cmd.append("--auto-commits")
        
        # Add files if specified
        if files:
            # Handle multiple files (comma or space separated)
            file_list = [f.strip() for f in files.replace(',', ' ').split() if f.strip()]
            for file_path in file_list:
                if Path(file_path).exists():
                    cmd.append(file_path)
                else:
                    logger.warning(f"File not found: {file_path}")
        else:
            # Let Aider work with the current directory
            cmd.append(".")
        
        # Add the task as a message
        cmd.extend(["--message", task_description])
        
        # Add yes flag to avoid interactive prompts
        cmd.append("--yes")
        
        logger.info(f"🚀 Launching Aider: {' '.join(cmd)}")
        
        # Create a temporary log file for Aider output
        with tempfile.NamedTemporaryFile(mode='w+', suffix='.log', delete=False) as log_file:
            log_path = log_file.name
        
        # Run Aider with timeout
        start_time = time.time()
        result = subprocess.run(
            cmd,
            cwd=str(cwd),
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        end_time = time.time()
        
        # Parse results
        success = result.returncode == 0
        duration = end_time - start_time
        
        # Extract meaningful information from output
        output_lines = result.stdout.split('\n')
        error_lines = result.stderr.split('\n') if result.stderr else []
        
        # Look for commit information
        commit_info = ""
        for line in output_lines:
            if "committed" in line.lower() or "commit" in line.lower():
                commit_info += line + "\n"
        
        # Look for file changes
        changed_files = []
        for line in output_lines:
            if "modified:" in line or "created:" in line or "deleted:" in line:
                changed_files.append(line.strip())
        
        if success:
            response = f"✅ Aider task completed successfully!\n\n"
            response += f"📋 Task: {task_description}\n"
            response += f"⏱️ Duration: {duration:.1f} seconds\n"
            
            if changed_files:
                response += f"📝 Files changed:\n"
                for file_change in changed_files[:5]:  # Limit to first 5
                    response += f"  • {file_change}\n"
                if len(changed_files) > 5:
                    response += f"  • ... and {len(changed_files) - 5} more files\n"
            
            if commit_info:
                response += f"📦 Git commits:\n{commit_info}\n"
            
            response += f"🔄 Control returned to Jarvis. You can now ask me to review the changes or continue with other tasks."
            
        else:
            response = f"❌ Aider task encountered issues.\n\n"
            response += f"📋 Task: {task_description}\n"
            response += f"⏱️ Duration: {duration:.1f} seconds\n"
            
            if error_lines:
                response += f"🔍 Error details:\n"
                for error_line in error_lines[:3]:  # First 3 error lines
                    if error_line.strip():
                        response += f"  • {error_line.strip()}\n"
            
            response += f"\n💡 You can try rephrasing the request or specifying different files."
        
        # Clean up log file
        try:
            os.unlink(log_path)
        except:
            pass
        
        logger.info(f"🔄 Aider handoff completed: success={success}, duration={duration:.1f}s")
        return response
        
    except subprocess.TimeoutExpired:
        error_msg = f"⏰ Aider task timed out after 5 minutes.\n\nTask: {task_description}\n\nThe task was too complex or Aider encountered an issue. Try breaking it into smaller steps."
        logger.error("Aider task timed out")
        return error_msg
        
    except Exception as e:
        error_msg = f"❌ Failed to hand off to Aider: {str(e)}\n\nTask: {task_description}\n\nPlease ensure Aider is properly installed and configured."
        logger.error(f"Aider handoff failed: {e}")
        return error_msg


@tool
def aider_project_refactor(refactor_description: str, target_directory: str = ".", model: str = "gpt-4") -> str:
    """
    Use Aider to perform large-scale project refactoring.
    
    Use this tool when users ask to:
    - "Refactor the entire project to use [pattern]"
    - "Update all files to follow [convention]"
    - "Modernize this codebase"
    - "Apply [architectural change] across the project"
    
    Args:
        refactor_description: Description of the refactoring to perform
        target_directory: Directory to refactor (default: current directory)
        model: AI model for Aider to use
    
    Returns:
        Results of the project-wide refactoring
    """
    try:
        logger.info(f"🔄 Starting project refactor with Aider: {refactor_description}")
        
        # Check if Aider is installed
        try:
            subprocess.run(["aider", "--version"], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            return "❌ Aider is not installed. Please install with: pip install aider-chat"
        
        target_path = Path(target_directory)
        if not target_path.exists():
            return f"❌ Target directory not found: {target_directory}"
        
        # Build Aider command for project-wide refactoring
        cmd = [
            "aider",
            "--model", model,
            "--auto-commits",
            "--message", f"Project refactoring: {refactor_description}",
            "--yes",
            str(target_path)
        ]
        
        logger.info(f"🚀 Launching Aider for project refactor: {' '.join(cmd)}")
        
        # Run Aider with extended timeout for large refactoring
        start_time = time.time()
        result = subprocess.run(
            cmd,
            cwd=str(target_path),
            capture_output=True,
            text=True,
            timeout=600  # 10 minute timeout for large refactoring
        )
        end_time = time.time()
        
        success = result.returncode == 0
        duration = end_time - start_time
        
        if success:
            response = f"✅ Project refactoring completed!\n\n"
            response += f"📋 Refactoring: {refactor_description}\n"
            response += f"📁 Target: {target_directory}\n"
            response += f"⏱️ Duration: {duration:.1f} seconds\n"
            response += f"🔄 Control returned to Jarvis. The refactoring is complete and committed."
        else:
            response = f"❌ Project refactoring encountered issues.\n\n"
            response += f"📋 Refactoring: {refactor_description}\n"
            response += f"⏱️ Duration: {duration:.1f} seconds\n"
            response += f"💡 You may need to review the changes manually or try a more specific approach."
        
        logger.info(f"🔄 Project refactor completed: success={success}")
        return response
        
    except subprocess.TimeoutExpired:
        return f"⏰ Project refactoring timed out after 10 minutes.\n\nThis was a large refactoring task. You can check what changes were made and continue manually if needed."
        
    except Exception as e:
        error_msg = f"❌ Project refactoring failed: {str(e)}"
        logger.error(f"Project refactor failed: {e}")
        return error_msg


@tool
def check_aider_status() -> str:
    """
    Check if Aider is installed and working properly.
    
    Use this tool when users ask:
    - "Is Aider working"
    - "Can you use Aider"
    - "Check Aider status"
    
    Returns:
        Status of Aider installation and capabilities
    """
    try:
        # Check if Aider is installed
        result = subprocess.run(["aider", "--version"], capture_output=True, text=True)
        
        if result.returncode == 0:
            version_info = result.stdout.strip()
            
            response = f"✅ Aider is installed and ready!\n\n"
            response += f"📦 Version: {version_info}\n\n"
            response += f"🛠️ Capabilities:\n"
            response += f"• Direct code file editing\n"
            response += f"• Multi-file refactoring\n"
            response += f"• Automatic git commits\n"
            response += f"• Project-wide changes\n"
            response += f"• Intelligent code understanding\n\n"
            response += f"🎤 Voice Commands:\n"
            response += f"• 'Edit [file] to add [feature]'\n"
            response += f"• 'Refactor this code to [improvement]'\n"
            response += f"• 'Fix the bug in [file]'\n"
            response += f"• 'Update all imports in the project'\n\n"
            response += f"🔄 Jarvis will hand off tasks to Aider and take back control when complete."
            
            return response
        else:
            return f"❌ Aider is installed but not responding properly.\n\nError: {result.stderr}"
            
    except FileNotFoundError:
        return f"❌ Aider is not installed.\n\nTo install Aider:\npip install aider-chat\n\nOnce installed, you'll be able to use voice commands for advanced code editing!"
        
    except Exception as e:
        return f"❌ Error checking Aider status: {str(e)}"


class AiderIntegrationPlugin(PluginBase):
    """Plugin that provides seamless Jarvis-Aider handoff for advanced code editing."""
    
    def get_metadata(self) -> PluginMetadata:
        """Return plugin metadata."""
        return PluginMetadata(
            name="AiderIntegration",
            version="1.0.0",
            description="Seamless handoff between Jarvis and Aider for advanced code editing and refactoring",
            author="Jarvis Team",
            dependencies=[]  # Aider is checked at runtime
        )
    
    def get_tools(self) -> List[BaseTool]:
        """Return the Aider integration tools."""
        return [
            aider_code_edit,
            aider_project_refactor,
            check_aider_status
        ]


# Required variables for plugin discovery system
PLUGIN_CLASS = AiderIntegrationPlugin
PLUGIN_METADATA = AiderIntegrationPlugin().get_metadata()
