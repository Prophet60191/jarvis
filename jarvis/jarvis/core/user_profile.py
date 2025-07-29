#!/usr/bin/env python3
"""
User Profile Management for Jarvis Voice Assistant

This module handles user profile information including name, preferences,
and personalization settings. It ensures names and personal information
are properly stored and used without being filtered as PII.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class UserProfile:
    """User profile data structure."""
    
    # Personal Information
    name: Optional[str] = None
    preferred_name: Optional[str] = None  # What they want to be called
    pronouns: Optional[str] = None  # he/him, she/her, they/them, etc.
    
    # Preferences
    timezone: Optional[str] = None
    location: Optional[str] = None
    language: str = "en"
    
    # Personalization Settings
    privacy_level: str = "standard"  # minimal, standard, full
    allow_name_storage: bool = True
    allow_preference_storage: bool = True
    
    # Metadata
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    version: str = "1.0"
    
    def __post_init__(self):
        """Initialize timestamps if not provided."""
        now = datetime.now().isoformat()
        if not self.created_at:
            self.created_at = now
        self.updated_at = now


class UserProfileManager:
    """Manages user profile storage and retrieval."""
    
    def __init__(self, data_dir: Optional[Path] = None):
        """
        Initialize the user profile manager.
        
        Args:
            data_dir: Directory to store user profile data
        """
        self.data_dir = data_dir or Path.home() / ".jarvis"
        self.profile_file = self.data_dir / "user_profile.json"
        self._profile: Optional[UserProfile] = None
        
        # Ensure data directory exists
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Load existing profile
        self._load_profile()
    
    def _load_profile(self) -> None:
        """Load user profile from disk."""
        try:
            if self.profile_file.exists():
                with open(self.profile_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self._profile = UserProfile(**data)
                    logger.info("User profile loaded successfully")
            else:
                self._profile = UserProfile()
                logger.info("Created new user profile")
        except Exception as e:
            logger.error(f"Error loading user profile: {e}")
            self._profile = UserProfile()
    
    def _save_profile(self) -> bool:
        """Save user profile to disk."""
        try:
            if self._profile:
                self._profile.updated_at = datetime.now().isoformat()
                with open(self.profile_file, 'w', encoding='utf-8') as f:
                    json.dump(asdict(self._profile), f, indent=2, ensure_ascii=False)
                logger.info("User profile saved successfully")
                return True
        except Exception as e:
            logger.error(f"Error saving user profile: {e}")
        return False
    
    def get_profile(self) -> UserProfile:
        """Get the current user profile."""
        if not self._profile:
            self._load_profile()
        return self._profile
    
    def update_profile(self, **kwargs) -> bool:
        """
        Update user profile with new information.
        
        Args:
            **kwargs: Profile fields to update
            
        Returns:
            True if update was successful
        """
        try:
            if not self._profile:
                self._profile = UserProfile()
            
            # Update fields
            for key, value in kwargs.items():
                if hasattr(self._profile, key):
                    setattr(self._profile, key, value)
                    logger.info(f"Updated profile field: {key}")
                else:
                    logger.warning(f"Unknown profile field: {key}")
            
            return self._save_profile()
        except Exception as e:
            logger.error(f"Error updating profile: {e}")
            return False
    
    def set_name(self, name: str, preferred_name: Optional[str] = None) -> bool:
        """
        Set the user's name.
        
        Args:
            name: Full name
            preferred_name: What they prefer to be called
            
        Returns:
            True if successful
        """
        return self.update_profile(
            name=name,
            preferred_name=preferred_name or name
        )
    
    def get_name(self) -> Optional[str]:
        """Get the user's preferred name."""
        profile = self.get_profile()
        return profile.preferred_name or profile.name
    
    def get_full_name(self) -> Optional[str]:
        """Get the user's full name."""
        profile = self.get_profile()
        return profile.name
    
    def set_pronouns(self, pronouns: str) -> bool:
        """Set the user's pronouns."""
        return self.update_profile(pronouns=pronouns)
    
    def get_pronouns(self) -> Optional[str]:
        """Get the user's pronouns."""
        profile = self.get_profile()
        return profile.pronouns
    
    def set_privacy_level(self, level: str) -> bool:
        """
        Set privacy level.
        
        Args:
            level: Privacy level (minimal, standard, full)
            
        Returns:
            True if successful
        """
        valid_levels = ["minimal", "standard", "full"]
        if level not in valid_levels:
            logger.error(f"Invalid privacy level: {level}. Must be one of {valid_levels}")
            return False
        
        return self.update_profile(privacy_level=level)
    
    def allow_name_usage(self, allow: bool = True) -> bool:
        """Enable or disable name storage and usage."""
        return self.update_profile(allow_name_storage=allow)
    
    def is_name_usage_allowed(self) -> bool:
        """Check if name usage is allowed."""
        profile = self.get_profile()
        return profile.allow_name_storage
    
    def get_greeting_name(self) -> str:
        """Get the appropriate name for greetings."""
        if not self.is_name_usage_allowed():
            return "there"
        
        name = self.get_name()
        return name if name else "there"
    
    def export_profile(self) -> Dict[str, Any]:
        """Export profile as dictionary."""
        profile = self.get_profile()
        return asdict(profile)
    
    def import_profile(self, data: Dict[str, Any]) -> bool:
        """Import profile from dictionary."""
        try:
            self._profile = UserProfile(**data)
            return self._save_profile()
        except Exception as e:
            logger.error(f"Error importing profile: {e}")
            return False
    
    def clear_profile(self) -> bool:
        """Clear all profile data."""
        try:
            self._profile = UserProfile()
            if self.profile_file.exists():
                self.profile_file.unlink()
            logger.info("User profile cleared")
            return True
        except Exception as e:
            logger.error(f"Error clearing profile: {e}")
            return False


# Global instance
_user_profile_manager: Optional[UserProfileManager] = None


def get_user_profile_manager() -> UserProfileManager:
    """Get the global user profile manager instance."""
    global _user_profile_manager
    if _user_profile_manager is None:
        _user_profile_manager = UserProfileManager()
    return _user_profile_manager


def get_user_name() -> Optional[str]:
    """Convenience function to get user's preferred name."""
    manager = get_user_profile_manager()
    return manager.get_name()


def set_user_name(name: str, preferred_name: Optional[str] = None) -> bool:
    """Convenience function to set user's name."""
    manager = get_user_profile_manager()
    return manager.set_name(name, preferred_name)
