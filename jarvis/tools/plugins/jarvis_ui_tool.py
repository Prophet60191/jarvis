"""
Jarvis UI Control Tool Plugin for Jarvis Voice Assistant.

This tool allows voice-activated control of the Jarvis UI application,
enabling users to open configuration panels, system status, and settings
through voice commands.

Author: Jarvis Assistant
"""

import logging
import subprocess
import os
import sys
from typing import List, Optional
from langchain_core.tools import tool
from jarvis.plugins.base import PluginBase, PluginMetadata

logger = logging.getLogger(__name__)


@tool
def open_jarvis_ui(panel: str = "main") -> str:
    """
    Open the Jarvis configuration interface when user asks to "open settings", "show settings", "open config", "open configuration", "open jarvis settings", or similar requests. This opens the native desktop app for configuring Jarvis.

    Use this tool when the user wants to:
    - Open settings, configuration, or preferences
    - Configure audio, microphone, or voice settings
    - Adjust LLM or AI model settings
    - Change conversation or wake word settings
    - View device information
    - Manage voice profiles
    - Access any Jarvis configuration options

    Args:
        panel: Which panel to open. Options: 'main', 'settings', 'audio', 'llm', 'conversation', 'logging', 'general', 'voice-profiles', 'device'

    Returns:
        Status message about opening the UI
    """
    try:
        # Get the current directory (where Jarvis is running)
        jarvis_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

        # Try desktop app first (preferred)
        desktop_script = os.path.join(jarvis_dir, "jarvis_app.py")

        if os.path.exists(desktop_script):
            # Check if pywebview is available for desktop app
            try:
                import webview
                # Launch the desktop application with the specified panel
                cmd = [sys.executable, desktop_script, "--panel", panel]

                # Launch in background (non-blocking)
                subprocess.Popen(
                    cmd,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    start_new_session=True
                )

                logger.info(f"Launched Jarvis Desktop App with panel: {panel}")

                panel_names = {
                    "main": "Main Dashboard",
                    "settings": "Settings Panel",
                    "audio": "Audio Configuration",
                    "llm": "LLM Configuration",
                    "conversation": "Conversation Settings",
                    "logging": "Logging Configuration",
                    "general": "General Settings",
                    "voice-profiles": "Voice Profiles",
                    "device": "Device Information"
                }

                panel_name = panel_names.get(panel, f"'{panel}' panel")
                return f"Opening Jarvis {panel_name} in the desktop app. The window should appear on your screen shortly."

            except ImportError:
                logger.warning("pywebview not available, falling back to web interface")
                # Fall through to web interface
                pass

        # Fallback to web interface
        ui_script = os.path.join(jarvis_dir, "ui", "jarvis_ui.py")

        # Check if UI script exists
        if not os.path.exists(ui_script):
            return "Jarvis UI application not found. Please install the desktop app with: python install_desktop.py"

        # Launch the web UI application with the specified panel (no browser window)
        cmd = [sys.executable, ui_script, "--panel", panel, "--no-browser"]

        # Launch in background (non-blocking)
        subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True
        )

        logger.info(f"Launched Jarvis Web UI with panel: {panel}")

        panel_names = {
            "main": "Main Dashboard",
            "settings": "Settings Panel",
            "audio": "Audio Configuration",
            "llm": "LLM Configuration",
            "conversation": "Conversation Settings",
            "logging": "Logging Configuration",
            "general": "General Settings",
            "voice-profiles": "Voice Profiles",
            "device": "Device Information"
        }

        panel_name = panel_names.get(panel, f"'{panel}' panel")
        return f"Opening Jarvis {panel_name} in the desktop app. The interface should appear shortly."
        
    except Exception as e:
        logger.error(f"Failed to open Jarvis UI: {e}")
        return f"Sorry, I couldn't open the Jarvis UI. Error: {str(e)}"


@tool
def close_jarvis_ui() -> str:
    """
    Close the Jarvis UI application (both desktop app and web interface).

    Returns:
        Status message about closing the UI
    """
    try:
        # Try to close via API first (works for both desktop and web)
        try:
            import requests
            response = requests.post("http://localhost:8080/api/shutdown", timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    return "Jarvis UI has been closed successfully."
        except:
            # API shutdown failed, try process termination
            pass

        # Find and terminate Jarvis UI processes
        import psutil

        closed_count = 0
        ui_processes = ['jarvis_ui.py', 'jarvis_app.py', 'start_desktop.py']

        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = proc.info['cmdline']
                if cmdline:
                    cmdline_str = ' '.join(cmdline)
                    for ui_process in ui_processes:
                        if ui_process in cmdline_str:
                            proc.terminate()
                            closed_count += 1
                            logger.info(f"Terminated Jarvis UI process: {proc.info['pid']} ({ui_process})")
                            break
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        if closed_count > 0:
            return f"Closed {closed_count} Jarvis UI window(s)."
        else:
            return "No Jarvis UI windows were found running."
            
    except ImportError:
        return "Cannot close UI automatically. Please close the Jarvis UI window manually."
    except Exception as e:
        logger.error(f"Failed to close Jarvis UI: {e}")
        return f"Error closing Jarvis UI: {str(e)}"


@tool
def show_jarvis_status() -> str:
    """
    Show current Jarvis system status and configuration.
    
    Returns:
        Current system status information
    """
    try:
        # Get basic system info
        import platform
        import psutil
        
        # System info
        system_info = {
            "Platform": platform.system(),
            "Python Version": platform.python_version(),
            "CPU Usage": f"{psutil.cpu_percent(interval=1):.1f}%",
            "Memory Usage": f"{psutil.virtual_memory().percent:.1f}%",
            "Available Memory": f"{psutil.virtual_memory().available / (1024**3):.1f} GB"
        }
        
        status_text = "Jarvis System Status:\n"
        for key, value in system_info.items():
            status_text += f"• {key}: {value}\n"

        # Add audio info
        status_text += "\nAudio Configuration:\n"
        status_text += "• Speech Recognition: Whisper (Local)\n"
        status_text += "• Text-to-Speech: Apple System Voices\n"
        status_text += "• Microphone: Active\n"
        
        return status_text.strip()
        
    except Exception as e:
        logger.error(f"Failed to get system status: {e}")
        return f"Error getting system status: {str(e)}"


class JarvisUIToolPlugin(PluginBase):
    """Plugin for Jarvis UI control tools."""
    
    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="JarvisUITool",
            version="1.0.0",
            description="Voice-activated Jarvis UI control and system status tools",
            author="Jarvis Assistant",
            tags=["ui", "control", "status", "configuration"]
        )
    
    def get_tools(self) -> List:
        return [open_jarvis_ui, close_jarvis_ui, show_jarvis_status]


# Create plugin instance for automatic discovery
plugin = JarvisUIToolPlugin()
