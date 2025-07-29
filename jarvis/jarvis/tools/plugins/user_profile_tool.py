"""
User Profile Management Tool Plugin for Jarvis Voice Assistant.

This plugin provides voice commands for managing user profile information,
including name storage and personalization settings.
"""

import logging
from langchain_core.tools import tool

# Import user profile manager with proper error handling
try:
    from jarvis.core.user_profile import get_user_profile_manager, UserProfile
except ImportError:
    # Fallback if user_profile not available
    def get_user_profile_manager():
        return None

logger = logging.getLogger(__name__)


@tool
def set_my_name(name: str, preferred_name: str = None) -> str:
    """
    Set your name for Jarvis to remember and use in conversations.
    
    Use this tool when the user says things like:
    - "My name is John"
    - "Call me Sarah"
    - "Remember that my name is Michael"
    - "I'm David, but call me Dave"
    - "Set my name to Jennifer"
    
    This allows Jarvis to personalize responses and remember your name
    across all conversations without treating it as sensitive information.
    
    Args:
        name: Your full name
        preferred_name: What you prefer to be called (optional, defaults to name)
        
    Returns:
        Confirmation message about name storage
    """
    try:
        manager = get_user_profile_manager()
        if not manager:
            return "Sorry, the user profile system is not available right now."
        
        # Use preferred_name if provided, otherwise use name
        display_name = preferred_name if preferred_name else name
        
        if manager.set_name(name, preferred_name):
            logger.info(f"User name set: {name} (preferred: {display_name})")
            
            if preferred_name and preferred_name != name:
                return f"Perfect! I'll remember that your name is {name}, and I'll call you {preferred_name}. Nice to meet you, {preferred_name}!"
            else:
                return f"Perfect! I'll remember that your name is {name}. Nice to meet you, {name}!"
        else:
            return "I had trouble saving your name. Please try again."
            
    except Exception as e:
        logger.error(f"Error setting user name: {e}")
        return "I encountered an error while trying to save your name. Please try again."


@tool
def get_my_name() -> str:
    """
    Get your stored name.
    
    Use this tool when the user asks:
    - "What's my name?"
    - "Do you know my name?"
    - "What do you call me?"
    - "Who am I?"
    
    Returns:
        Your stored name or indication if no name is stored
    """
    try:
        manager = get_user_profile_manager()
        if not manager:
            return "Sorry, the user profile system is not available right now."
        
        name = manager.get_name()
        full_name = manager.get_full_name()
        
        if name:
            if full_name and full_name != name:
                return f"I know you as {name}. Your full name is {full_name}."
            else:
                return f"I know you as {name}."
        else:
            return "I don't have your name stored yet. You can tell me your name by saying 'My name is...' or 'Call me...'"
            
    except Exception as e:
        logger.error(f"Error getting user name: {e}")
        return "I had trouble retrieving your name information."


@tool
def set_my_pronouns(pronouns: str) -> str:
    """
    Set your pronouns for Jarvis to use when referring to you.
    
    Use this tool when the user says:
    - "My pronouns are he/him"
    - "Use she/her pronouns for me"
    - "I use they/them pronouns"
    - "Set my pronouns to he/him"
    
    Args:
        pronouns: Your pronouns (e.g., "he/him", "she/her", "they/them")
        
    Returns:
        Confirmation message about pronoun storage
    """
    try:
        manager = get_user_profile_manager()
        if not manager:
            return "Sorry, the user profile system is not available right now."
        
        if manager.set_pronouns(pronouns):
            logger.info(f"User pronouns set: {pronouns}")
            return f"Got it! I'll use {pronouns} pronouns when referring to you."
        else:
            return "I had trouble saving your pronouns. Please try again."
            
    except Exception as e:
        logger.error(f"Error setting user pronouns: {e}")
        return "I encountered an error while trying to save your pronouns. Please try again."


@tool
def show_my_profile() -> str:
    """
    Show your stored profile information.
    
    Use this tool when the user asks:
    - "Show my profile"
    - "What do you know about me?"
    - "What information do you have stored?"
    - "Show my personal information"
    
    Returns:
        Summary of stored profile information
    """
    try:
        manager = get_user_profile_manager()
        if not manager:
            return "Sorry, the user profile system is not available right now."
        
        profile = manager.get_profile()
        
        info_parts = []
        
        # Name information
        if profile.name:
            if profile.preferred_name and profile.preferred_name != profile.name:
                info_parts.append(f"Name: {profile.name} (I call you {profile.preferred_name})")
            else:
                info_parts.append(f"Name: {profile.name}")
        
        # Pronouns
        if profile.pronouns:
            info_parts.append(f"Pronouns: {profile.pronouns}")
        
        # Privacy settings
        info_parts.append(f"Privacy level: {profile.privacy_level}")
        info_parts.append(f"Name storage: {'Enabled' if profile.allow_name_storage else 'Disabled'}")
        
        if info_parts:
            return "Here's your profile information:\n" + "\n".join(f"• {info}" for info in info_parts)
        else:
            return "I don't have any profile information stored for you yet. You can tell me your name or set other preferences."
            
    except Exception as e:
        logger.error(f"Error showing user profile: {e}")
        return "I had trouble retrieving your profile information."


@tool
def enable_name_usage() -> str:
    """
    Enable name storage and usage by Jarvis.
    
    Use this tool when the user says:
    - "Allow Jarvis to use my name"
    - "Enable name storage"
    - "You can remember my name"
    - "Turn on name usage"
    
    Returns:
        Confirmation message about enabling name usage
    """
    try:
        manager = get_user_profile_manager()
        if not manager:
            return "Sorry, the user profile system is not available right now."
        
        if manager.allow_name_usage(True):
            logger.info("Name usage enabled by user")
            return "Perfect! I can now store and use your name in our conversations. This helps me provide more personalized responses."
        else:
            return "I had trouble updating your privacy settings. Please try again."
            
    except Exception as e:
        logger.error(f"Error enabling name usage: {e}")
        return "I encountered an error while updating your settings. Please try again."


@tool
def disable_name_usage() -> str:
    """
    Disable name storage and usage by Jarvis.
    
    Use this tool when the user says:
    - "Don't use my name"
    - "Disable name storage"
    - "Stop remembering my name"
    - "Turn off name usage"
    
    Returns:
        Confirmation message about disabling name usage
    """
    try:
        manager = get_user_profile_manager()
        if not manager:
            return "Sorry, the user profile system is not available right now."
        
        if manager.allow_name_usage(False):
            logger.info("Name usage disabled by user")
            return "Understood. I won't use your name in conversations anymore, though I'll keep it stored in case you want to re-enable this feature later."
        else:
            return "I had trouble updating your privacy settings. Please try again."
            
    except Exception as e:
        logger.error(f"Error disabling name usage: {e}")
        return "I encountered an error while updating your settings. Please try again."


@tool
def clear_my_profile() -> str:
    """
    Clear all stored profile information.
    
    Use this tool when the user says:
    - "Clear my profile"
    - "Delete my personal information"
    - "Remove all my data"
    - "Reset my profile"
    
    Returns:
        Confirmation message about profile clearing
    """
    try:
        manager = get_user_profile_manager()
        if not manager:
            return "Sorry, the user profile system is not available right now."
        
        if manager.clear_profile():
            logger.info("User profile cleared by user request")
            return "I've cleared all your profile information. Your name, pronouns, and preferences have been removed from my memory."
        else:
            return "I had trouble clearing your profile. Please try again."
            
    except Exception as e:
        logger.error(f"Error clearing user profile: {e}")
        return "I encountered an error while trying to clear your profile. Please try again."
