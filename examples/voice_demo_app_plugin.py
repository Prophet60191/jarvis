#!/usr/bin/env python3
"""
Voice Demo App Plugin

This plugin provides voice commands to open and close the Voice Demo App.
Copy this file to jarvis/jarvis/tools/plugins/ to enable voice commands.

Voice Commands:
- "Hey Jarvis, open my demo app"
- "Hey Jarvis, show my demo app" 
- "Hey Jarvis, close my demo app"
- "Hey Jarvis, close the demo app"

Installation:
1. Copy this file to: jarvis/jarvis/tools/plugins/voice_demo_app_plugin.py
2. Restart Jarvis
3. Test with voice commands

Usage Example:
    User: "Hey Jarvis, open my demo app"
    Jarvis: "Voice Demo App is now open in the desktop app."
    
    User: "Hey Jarvis, close my demo app"  
    Jarvis: "I've successfully closed the Voice Demo App."
"""

import logging
from langchain.tools import tool
from jarvis.utils.app_manager import get_app_manager

logger = logging.getLogger(__name__)

@tool
def open_voice_demo_app(panel: str = "main") -> str:
    """
    Open the Voice Demo App when user asks to open it.
    
    Use this tool when the user wants to:
    - Open the voice demo application
    - Show the demo app
    - Launch the voice-controlled UI demo
    - Access the demo interface
    
    Common user phrases:
    - "open my demo app"
    - "show my demo app"
    - "launch the demo app"
    - "open voice demo"
    - "start the demo application"
    
    Args:
        panel: Which panel to open (main, settings, help, etc.)
        
    Returns:
        Status message about opening the app
    """
    try:
        logger.info(f"Opening Voice Demo App with panel: {panel}")
        
        # Get the application manager
        app_manager = get_app_manager()
        
        if app_manager:
            # App name must match the registration name in the app
            app_name = "voice_demo_app"
            
            # Check if app is already running
            if app_manager.is_app_running(app_name):
                return "Voice Demo App is already open and running."
            
            # Try to start the app
            if app_manager.start_app(app_name):
                panel_names = {
                    "main": "main interface",
                    "voice": "voice commands panel", 
                    "status": "status panel",
                    "settings": "settings panel",
                    "help": "help panel"
                }
                
                panel_name = panel_names.get(panel, f"'{panel}' panel")
                return f"Voice Demo App ({panel_name}) is now open in the desktop app."
            else:
                return "I encountered an error while trying to open the Voice Demo App. Please make sure the app is properly installed and try again."
        else:
            return "Application manager is not available. Please check your Jarvis configuration and try again."
            
    except Exception as e:
        logger.error(f"Error opening Voice Demo App: {e}")
        return f"I encountered an error while trying to open the Voice Demo App: {str(e)}"

@tool
def close_voice_demo_app() -> str:
    """
    Close the Voice Demo App when user asks to close it.
    
    Use this tool when the user wants to:
    - Close the voice demo application
    - Shut down the demo app
    - Stop the voice-controlled UI demo
    - Exit the demo interface
    
    Common user phrases:
    - "close my demo app"
    - "close the demo app"
    - "shut down demo app"
    - "close voice demo"
    - "exit the demo application"
    
    Returns:
        Status message about closing the app
    """
    try:
        logger.info("Attempting to close Voice Demo App")
        
        # Get the application manager
        app_manager = get_app_manager()
        
        if app_manager:
            # App name must match the registration name
            app_name = "voice_demo_app"
            
            # Check if app is running
            if app_manager.is_app_running(app_name):
                # Try to stop the app
                if app_manager.stop_app(app_name):
                    return "I've successfully closed the Voice Demo App."
                else:
                    return "I encountered an error while trying to close the Voice Demo App. You may need to close it manually."
            else:
                return "The Voice Demo App doesn't appear to be running, or it's already closed."
        else:
            return "Application manager is not available. Cannot close the app automatically."
            
    except Exception as e:
        logger.error(f"Error closing Voice Demo App: {e}")
        return f"I encountered an error while trying to close the Voice Demo App: {str(e)}"

@tool
def check_voice_demo_app_status() -> str:
    """
    Check if the Voice Demo App is currently running.
    
    Use this tool when the user wants to:
    - Check if the demo app is running
    - Get the status of the voice demo
    - See if the demo application is active
    
    Common user phrases:
    - "is my demo app running?"
    - "check demo app status"
    - "is the voice demo open?"
    - "show demo app status"
    
    Returns:
        Current status of the Voice Demo App
    """
    try:
        logger.info("Checking Voice Demo App status")
        
        # Get the application manager
        app_manager = get_app_manager()
        
        if app_manager:
            app_name = "voice_demo_app"
            
            if app_manager.is_app_running(app_name):
                # Get additional status information if available
                status_info = app_manager.get_app_status(app_name)
                if status_info and isinstance(status_info, dict):
                    uptime = status_info.get('uptime', 'unknown')
                    return f"Voice Demo App is currently running (uptime: {uptime})."
                else:
                    return "Voice Demo App is currently running."
            else:
                return "Voice Demo App is not currently running."
        else:
            return "Cannot check app status - application manager is not available."
            
    except Exception as e:
        logger.error(f"Error checking Voice Demo App status: {e}")
        return f"Unable to check Voice Demo App status: {str(e)}"

# Additional helper tools for specific panels

@tool
def open_voice_demo_help() -> str:
    """Open the Voice Demo App help panel specifically."""
    return open_voice_demo_app("help")

@tool  
def open_voice_demo_settings() -> str:
    """Open the Voice Demo App settings panel specifically."""
    return open_voice_demo_app("settings")

@tool
def show_voice_demo_commands() -> str:
    """
    Show available voice commands for the Voice Demo App.
    
    Use this tool when the user wants to:
    - Learn about available voice commands
    - Get help with voice commands
    - See what they can say to control the app
    
    Returns:
        List of available voice commands
    """
    return """
Voice Demo App Commands:

🔊 Opening Commands:
• "Hey Jarvis, open my demo app"
• "Jarvis, show my demo app"
• "Launch the demo app"
• "Open voice demo"
• "Start the demo application"

🔇 Closing Commands:
• "Hey Jarvis, close my demo app"
• "Jarvis, close the demo app"
• "Shut down demo app"
• "Close voice demo"
• "Exit the demo application"

📊 Status Commands:
• "Check demo app status"
• "Is my demo app running?"
• "Show demo app status"

🆘 Help Commands:
• "Open demo app help"
• "Show voice demo commands"
• "Open demo app settings"

Try any of these commands after saying "Hey Jarvis" and waiting for acknowledgment!
    """
