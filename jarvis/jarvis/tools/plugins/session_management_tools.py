"""
Session Management Tools

Tools for saving, recalling, and managing conversation sessions.
Integrates with the conversation memory manager and session save system.
"""

import logging
from langchain.tools import tool

# Use absolute import to avoid relative import issues
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from jarvis.core.memory.conversation_memory_manager import get_conversation_memory_manager

logger = logging.getLogger(__name__)


@tool
def save_conversation_session(session_name: str) -> str:
    """
    Save the current conversation session with a user-provided name.
    
    Use when user says:
    - "Save this session as [name]"
    - "Save our conversation as [name]"
    - "Remember this conversation as [name]"
    - "Call this session [name]"
    
    Args:
        session_name: Name to give the saved session
        
    Returns:
        Confirmation message about the saved session
        
    Example:
        User: "Save this session as Python Learning"
        Result: Session saved and will continue to update automatically
    """
    try:
        memory_manager = get_conversation_memory_manager()
        result = memory_manager.save_current_session(session_name)
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to save session: {e}")
        return f"Sorry, I couldn't save the session: {str(e)}"


@tool
def recall_conversation_session(session_name: str) -> str:
    """
    Recall and display a previously saved conversation session.
    
    Use when user says:
    - "Show me the [session name] session"
    - "Recall the [session name] conversation"
    - "Continue the [session name] session"
    - "What did we discuss in [session name]?"
    
    Args:
        session_name: Name of the session to recall
        
    Returns:
        The recalled session content and confirmation that it's now active
        
    Example:
        User: "Show me the Python Learning session"
        Result: Displays the saved conversation and makes it active for continuation
    """
    try:
        memory_manager = get_conversation_memory_manager()
        result = memory_manager.recall_session(session_name)
        
        if result:
            return result
        else:
            return f"I couldn't find a session named '{session_name}'. Use 'list my sessions' to see available sessions."
        
    except Exception as e:
        logger.error(f"Failed to recall session: {e}")
        return f"Sorry, I couldn't recall the session: {str(e)}"


@tool
def list_conversation_sessions() -> str:
    """
    List all saved conversation sessions.
    
    Use when user says:
    - "Show me my saved sessions"
    - "List my conversation history"
    - "What sessions do I have?"
    - "Show my saved conversations"
    - "What have we talked about before?"
    
    Returns:
        Formatted list of all saved sessions with names, dates, and message counts
        
    Example:
        User: "Show me my saved sessions"
        Result: Lists all saved sessions with details
    """
    try:
        memory_manager = get_conversation_memory_manager()
        result = memory_manager.list_saved_sessions()
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to list sessions: {e}")
        return f"Sorry, I couldn't list the sessions: {str(e)}"


@tool
def confirm_session_save(confirmation: str) -> str:
    """
    Confirm saving the current session when Jarvis suggests it.
    
    Use when user responds to a save suggestion with:
    - "Yes, save it"
    - "Yes, save this session"
    - "Save it"
    - "Yes"
    
    This tool will ask for a session name if the user confirms.
    
    Args:
        confirmation: User's confirmation response
        
    Returns:
        Request for session name or confirmation of save
        
    Example:
        Jarvis: "Would you like me to save this session?"
        User: "Yes, save it"
        Result: "Great! What would you like to call this session?"
    """
    try:
        confirmation_lower = confirmation.lower().strip()
        
        # Check if this is a positive confirmation
        positive_responses = ['yes', 'save it', 'yes save it', 'save this session', 'yes save this']
        
        if any(response in confirmation_lower for response in positive_responses):
            return ("Great! What would you like to call this session? "
                   "For example, you could say 'Call it Python Learning Session' or just give me a name.")
        else:
            return "No problem! We'll continue our conversation without saving."
        
    except Exception as e:
        logger.error(f"Failed to process session save confirmation: {e}")
        return "I didn't quite catch that. Would you like to save this session?"


def get_session_management_tools():
    """
    Get all session management tools.
    
    Returns:
        List of session management tools
    """
    return [
        save_conversation_session,
        recall_conversation_session,
        list_conversation_sessions,
        confirm_session_save
    ]
