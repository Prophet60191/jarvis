#!/usr/bin/env python3
"""
User Profile Setup Script for Jarvis Voice Assistant

This script helps you set up your user profile, including your name
and personalization preferences for Jarvis.
"""

import sys
from pathlib import Path

# Add jarvis to path
sys.path.insert(0, str(Path(__file__).parent / "jarvis"))

def setup_user_profile():
    """Interactive setup for user profile."""
    print("🎤 JARVIS USER PROFILE SETUP")
    print("=" * 60)
    print("This script will help you set up your personal information")
    print("so Jarvis can provide a more personalized experience.")
    print("=" * 60)
    
    try:
        from jarvis.core.user_profile import get_user_profile_manager
        
        manager = get_user_profile_manager()
        current_profile = manager.get_profile()
        
        print("\n📋 CURRENT PROFILE:")
        print("-" * 30)
        if current_profile.name:
            print(f"Name: {current_profile.name}")
            if current_profile.preferred_name and current_profile.preferred_name != current_profile.name:
                print(f"Preferred name: {current_profile.preferred_name}")
        else:
            print("Name: Not set")
        
        if current_profile.pronouns:
            print(f"Pronouns: {current_profile.pronouns}")
        else:
            print("Pronouns: Not set")
        
        print(f"Privacy level: {current_profile.privacy_level}")
        print(f"Name storage: {'Enabled' if current_profile.allow_name_storage else 'Disabled'}")
        
        print("\n🔧 SETUP OPTIONS:")
        print("-" * 30)
        print("1. Set your name")
        print("2. Set your pronouns")
        print("3. Configure privacy settings")
        print("4. Enable name usage")
        print("5. Show current profile")
        print("6. Clear profile")
        print("0. Exit")
        
        while True:
            try:
                choice = input("\nEnter your choice (0-6): ").strip()
                
                if choice == "0":
                    print("\n✅ Setup complete! Restart Jarvis to use your new profile.")
                    break
                
                elif choice == "1":
                    setup_name(manager)
                
                elif choice == "2":
                    setup_pronouns(manager)
                
                elif choice == "3":
                    setup_privacy(manager)
                
                elif choice == "4":
                    enable_name_usage(manager)
                
                elif choice == "5":
                    show_profile(manager)
                
                elif choice == "6":
                    clear_profile(manager)
                
                else:
                    print("❌ Invalid choice. Please enter 0-6.")
                    
            except KeyboardInterrupt:
                print("\n\n👋 Setup cancelled. Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
                
    except ImportError as e:
        print(f"❌ Error importing user profile system: {e}")
        print("Make sure you're running this from the Jarvis project directory.")
        return 1
    
    return 0


def setup_name(manager):
    """Set up user name."""
    print("\n👤 NAME SETUP")
    print("-" * 20)
    
    full_name = input("Enter your full name: ").strip()
    if not full_name:
        print("❌ Name cannot be empty.")
        return
    
    preferred_name = input(f"What should I call you? (press Enter for '{full_name}'): ").strip()
    if not preferred_name:
        preferred_name = full_name
    
    if manager.set_name(full_name, preferred_name):
        if preferred_name != full_name:
            print(f"✅ Great! I'll remember that your name is {full_name}, and I'll call you {preferred_name}.")
        else:
            print(f"✅ Perfect! I'll remember that your name is {full_name}.")
    else:
        print("❌ Failed to save your name. Please try again.")


def setup_pronouns(manager):
    """Set up user pronouns."""
    print("\n🏷️  PRONOUN SETUP")
    print("-" * 20)
    print("Common options: he/him, she/her, they/them")
    
    pronouns = input("Enter your pronouns: ").strip()
    if not pronouns:
        print("❌ Pronouns cannot be empty.")
        return
    
    if manager.set_pronouns(pronouns):
        print(f"✅ Got it! I'll use {pronouns} pronouns when referring to you.")
    else:
        print("❌ Failed to save your pronouns. Please try again.")


def setup_privacy(manager):
    """Set up privacy settings."""
    print("\n🔒 PRIVACY SETUP")
    print("-" * 20)
    print("Privacy levels:")
    print("  minimal  - Store only essential information")
    print("  standard - Store name and basic preferences (recommended)")
    print("  full     - Store detailed personalization data")
    
    level = input("Choose privacy level (minimal/standard/full): ").strip().lower()
    
    if level not in ["minimal", "standard", "full"]:
        print("❌ Invalid privacy level. Please choose minimal, standard, or full.")
        return
    
    if manager.set_privacy_level(level):
        print(f"✅ Privacy level set to '{level}'.")
    else:
        print("❌ Failed to update privacy settings. Please try again.")


def enable_name_usage(manager):
    """Enable name usage."""
    print("\n✅ ENABLE NAME USAGE")
    print("-" * 25)
    
    choice = input("Allow Jarvis to use your name in conversations? (y/n): ").strip().lower()
    
    if choice in ['y', 'yes']:
        if manager.allow_name_usage(True):
            print("✅ Name usage enabled! Jarvis can now use your name in conversations.")
        else:
            print("❌ Failed to enable name usage.")
    elif choice in ['n', 'no']:
        if manager.allow_name_usage(False):
            print("✅ Name usage disabled. Jarvis won't use your name in conversations.")
        else:
            print("❌ Failed to disable name usage.")
    else:
        print("❌ Please answer 'y' or 'n'.")


def show_profile(manager):
    """Show current profile."""
    print("\n📋 CURRENT PROFILE")
    print("-" * 25)
    
    profile = manager.get_profile()
    
    print(f"Name: {profile.name or 'Not set'}")
    if profile.preferred_name and profile.preferred_name != profile.name:
        print(f"Preferred name: {profile.preferred_name}")
    print(f"Pronouns: {profile.pronouns or 'Not set'}")
    print(f"Privacy level: {profile.privacy_level}")
    print(f"Name storage: {'Enabled' if profile.allow_name_storage else 'Disabled'}")
    print(f"Created: {profile.created_at}")
    print(f"Updated: {profile.updated_at}")


def clear_profile(manager):
    """Clear user profile."""
    print("\n🗑️  CLEAR PROFILE")
    print("-" * 20)
    print("⚠️  This will permanently delete all your profile information.")
    
    confirm = input("Are you sure? Type 'DELETE' to confirm: ").strip()
    
    if confirm == "DELETE":
        if manager.clear_profile():
            print("✅ Profile cleared successfully.")
        else:
            print("❌ Failed to clear profile.")
    else:
        print("❌ Profile clearing cancelled.")


def main():
    """Main entry point."""
    return setup_user_profile()


if __name__ == "__main__":
    sys.exit(main())
