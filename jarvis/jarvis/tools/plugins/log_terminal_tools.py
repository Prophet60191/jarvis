"""
Log Terminal Management Tools for Jarvis Voice Assistant

Provides voice-controlled log terminal management:
- Open debug logs terminal
- Close debug logs terminal
- Real-time log viewing
- Terminal window management

Author: Jarvis Team
"""

import os
import sys
import subprocess
import signal
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from langchain_core.tools import tool

from jarvis.plugins.base import PluginBase, PluginMetadata

logger = logging.getLogger(__name__)

class LogTerminalManager:
    """Manages log terminal windows and processes."""
    
    def __init__(self):
        self.log_processes: Dict[str, subprocess.Popen] = {}
        self.project_root = Path(__file__).parent.parent.parent.parent
        
    def get_log_file_path(self) -> str:
        """Get the path to the current log file."""
        log_file = self.project_root / "jarvis_debug.log"
        return str(log_file)
    
    def is_macos(self) -> bool:
        """Check if running on macOS."""
        return sys.platform == "darwin"
    
    def open_log_terminal_macos(self) -> bool:
        """Open log terminal on macOS using Terminal.app."""
        try:
            log_file = self.get_log_file_path()

            # Create the log file if it doesn't exist
            Path(log_file).touch(exist_ok=True)

            # Create a unique identifier for this logs session
            import time
            session_id = int(time.time())

            # AppleScript to open new Terminal window with tail command
            # Include session ID in title for safer identification
            applescript = f'''
            tell application "Terminal"
                activate
                set newTab to do script "echo '🔍 JARVIS DEBUG LOGS - Live View (Session {session_id})'; echo '═══════════════════════════════════════'; tail -f '{log_file}'"
                set custom title of newTab to "Jarvis Debug Logs {session_id}"
            end tell
            '''

            # Execute AppleScript
            process = subprocess.Popen([
                'osascript', '-e', applescript
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            stdout, stderr = process.communicate()

            if process.returncode == 0:
                # Store session info for safer closing
                self.log_processes['debug_logs'] = {
                    'process': process,
                    'session_id': session_id,
                    'log_file': log_file
                }
                logger.info(f"Successfully opened debug logs terminal (session {session_id})")
                return True
            else:
                logger.error(f"Failed to open logs terminal: {stderr.decode()}")
                return False

        except Exception as e:
            logger.error(f"Error opening logs terminal: {e}")
            return False
    
    def open_log_terminal_linux(self) -> bool:
        """Open log terminal on Linux using gnome-terminal or xterm."""
        try:
            log_file = self.get_log_file_path()
            Path(log_file).touch(exist_ok=True)
            
            # Try gnome-terminal first, then xterm as fallback
            commands = [
                ['gnome-terminal', '--title=Jarvis Debug Logs', '--', 'bash', '-c', 
                 f'echo "🔍 JARVIS DEBUG LOGS - Live View"; echo "═══════════════════════════════════════"; tail -f "{log_file}"'],
                ['xterm', '-title', 'Jarvis Debug Logs', '-e', 'bash', '-c', 
                 f'echo "🔍 JARVIS DEBUG LOGS - Live View"; echo "═══════════════════════════════════════"; tail -f "{log_file}"']
            ]
            
            for cmd in commands:
                try:
                    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    self.log_processes['debug_logs'] = process
                    logger.info(f"Successfully opened debug logs terminal with {cmd[0]}")
                    return True
                except FileNotFoundError:
                    continue
            
            logger.error("No suitable terminal emulator found (tried gnome-terminal, xterm)")
            return False
            
        except Exception as e:
            logger.error(f"Error opening logs terminal: {e}")
            return False
    
    def close_log_terminal(self) -> bool:
        """Close the debug logs terminal."""
        try:
            if 'debug_logs' in self.log_processes:
                log_info = self.log_processes['debug_logs']

                if self.is_macos():
                    # On macOS, use session ID for safer terminal closing
                    if isinstance(log_info, dict) and 'session_id' in log_info:
                        session_id = log_info['session_id']
                        log_file = log_info['log_file']

                        # First, kill the specific tail process
                        try:
                            kill_cmd = f"pkill -f 'tail -f {log_file}'"
                            subprocess.run(kill_cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                            logger.info(f"Killed tail process for session {session_id}")
                        except Exception as e:
                            logger.warning(f"Could not kill tail process: {e}")

                        # Then close the specific terminal tab using session ID
                        applescript = f'''
                        tell application "Terminal"
                            repeat with w in windows
                                repeat with t in tabs of w
                                    try
                                        if custom title of t contains "Jarvis Debug Logs {session_id}" then
                                            close t
                                            return
                                        end if
                                    end try
                                end repeat
                            end repeat
                        end tell
                        '''
                        subprocess.run(['osascript', '-e', applescript],
                                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    else:
                        # Fallback: just kill tail processes (safer than closing terminals)
                        log_file = self.get_log_file_path()
                        kill_cmd = f"pkill -f 'tail -f {log_file}'"
                        subprocess.run(kill_cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                        logger.info("Killed tail processes (fallback method)")
                else:
                    # On Linux, terminate the process
                    if isinstance(log_info, dict) and 'process' in log_info:
                        process = log_info['process']
                    else:
                        process = log_info  # Fallback for old format

                    process.terminate()
                    try:
                        process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        process.kill()
                
                del self.log_processes['debug_logs']
                logger.info("Successfully closed debug logs terminal")
                return True
            else:
                logger.warning("No debug logs terminal is currently open")
                return False
                
        except Exception as e:
            logger.error(f"Error closing logs terminal: {e}")
            return False

# Global instance
log_terminal_manager = LogTerminalManager()

@tool
def open_logs_terminal() -> str:
    """
    Open a new terminal window showing live debug logs from Jarvis.
    
    This opens a separate terminal window that displays real-time debug information,
    error messages, and technical details while keeping the main conversation clean.
    
    Returns:
        str: Success or error message about opening the logs terminal
    """
    try:
        logger.info("Voice command: Opening logs terminal")
        
        if log_terminal_manager.is_macos():
            success = log_terminal_manager.open_log_terminal_macos()
        else:
            success = log_terminal_manager.open_log_terminal_linux()
        
        if success:
            return "Logs terminal opened."
        else:
            return "Failed to open logs terminal."
            
    except Exception as e:
        logger.error(f"Error in open_logs_terminal tool: {e}")
        return f"❌ Error opening logs terminal: {str(e)}"

@tool
def close_logs_terminal() -> str:
    """
    Close the debug logs terminal window if it's currently open.
    
    This closes the separate terminal window showing debug logs,
    keeping only the main conversation interface active.
    
    Returns:
        str: Success or error message about closing the logs terminal
    """
    try:
        logger.info("Voice command: Closing logs terminal")
        
        success = log_terminal_manager.close_log_terminal()
        
        if success:
            return "Logs terminal closed."
        else:
            return "No logs terminal is open."
            
    except Exception as e:
        logger.error(f"Error in close_logs_terminal tool: {e}")
        return f"❌ Error closing logs terminal: {str(e)}"

@tool
def show_logs_status() -> str:
    """
    Check the status of the debug logs terminal.
    
    Returns information about whether the logs terminal is currently open
    and provides the log file location.
    
    Returns:
        str: Status information about the logs terminal
    """
    try:
        log_file = log_terminal_manager.get_log_file_path()
        is_open = 'debug_logs' in log_terminal_manager.log_processes
        
        is_open_text = "open" if is_open else "closed"
        return f"Logs terminal is {is_open_text}."
        
    except Exception as e:
        logger.error(f"Error in show_logs_status tool: {e}")
        return f"❌ Error checking logs status: {str(e)}"

class LogTerminalPlugin(PluginBase):
    """Plugin for voice-controlled log terminal management."""
    
    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="LogTerminalTools",
            version="1.0.0",
            description="Voice-controlled debug logs terminal management",
            author="Jarvis Team"
        )
    
    def get_tools(self):
        return [open_logs_terminal, close_logs_terminal, show_logs_status]

# Required for plugin discovery
PLUGIN_CLASS = LogTerminalPlugin
PLUGIN_METADATA = LogTerminalPlugin().get_metadata()
