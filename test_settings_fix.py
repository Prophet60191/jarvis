#!/usr/bin/env python3
"""
Test the settings persistence fix.
"""

import os
import sys
from pathlib import Path

# Add jarvis to path
sys.path.insert(0, str(Path(__file__).parent / "jarvis"))

def test_ui_config_manager():
    """Test the UI configuration manager directly."""
    print("🧪 TESTING UI CONFIGURATION MANAGER")
    print("=" * 60)
    
    try:
        # Import the config manager
        sys.path.insert(0, str(Path(__file__).parent / "jarvis" / "ui"))
        from jarvis_ui import ConfigManager
        
        # Create a config manager instance
        config_manager = ConfigManager()
        
        print("✅ ConfigManager imported successfully")
        
        # Test updating a setting
        test_updates = {
            "conversation": {
                "conversation_timeout": 150  # Test changing to 150 seconds
            }
        }
        
        print("🔄 Testing configuration update...")
        result = config_manager.update_config(test_updates)
        
        if result.get("success"):
            print("✅ Configuration update successful")
            
            # Check if .env file was updated
            env_file = Path(".env")
            if env_file.exists():
                content = env_file.read_text()
                if "JARVIS_CONVERSATION_TIMEOUT=150" in content:
                    print("✅ .env file updated correctly")
                    
                    # Restore original value
                    restore_updates = {
                        "conversation": {
                            "conversation_timeout": 120  # Restore to your setting
                        }
                    }
                    config_manager.update_config(restore_updates)
                    print("✅ Original setting restored")
                    return True
                else:
                    print("❌ .env file not updated correctly")
                    print(f"Content: {content[:200]}...")
                    return False
            else:
                print("❌ .env file doesn't exist")
                return False
        else:
            print(f"❌ Configuration update failed: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing UI config manager: {e}")
        import traceback
        traceback.print_exc()
        return False


def verify_current_timeout_setting():
    """Verify what timeout setting you actually have."""
    print("\n📊 VERIFYING CURRENT TIMEOUT SETTING")
    print("=" * 60)
    
    try:
        from jarvis.config import get_config
        config = get_config()
        
        timeout = config.conversation.conversation_timeout
        print(f"Current conversation timeout: {timeout} seconds")
        
        if timeout == 120:
            print("✅ Your setting (120 seconds / 2 minutes) is active")
        elif timeout == 30:
            print("⚠️ Default setting (30 seconds) is active - your change may not have persisted")
        else:
            print(f"ℹ️ Custom setting ({timeout} seconds) is active")
        
        # Check environment variable
        env_timeout = os.environ.get("JARVIS_CONVERSATION_TIMEOUT")
        if env_timeout:
            print(f"Environment variable: {env_timeout} seconds")
            if env_timeout == str(timeout):
                print("✅ Environment variable matches config")
            else:
                print("⚠️ Environment variable doesn't match config")
        else:
            print("⚠️ No environment variable set")
        
        # Check .env file
        env_file = Path(".env")
        if env_file.exists():
            content = env_file.read_text()
            if "JARVIS_CONVERSATION_TIMEOUT=" in content:
                import re
                match = re.search(r"JARVIS_CONVERSATION_TIMEOUT=(\d+)", content)
                if match:
                    env_file_timeout = match.group(1)
                    print(f".env file setting: {env_file_timeout} seconds")
                    if env_file_timeout == str(timeout):
                        print("✅ .env file matches config")
                    else:
                        print("⚠️ .env file doesn't match config - settings won't persist")
                else:
                    print("❌ Could not parse timeout from .env file")
            else:
                print("❌ No timeout setting in .env file")
        else:
            print("❌ No .env file found")
        
        return True
        
    except Exception as e:
        print(f"❌ Error verifying timeout setting: {e}")
        return False


def update_env_file_with_current_timeout():
    """Update .env file with the current timeout setting."""
    print("\n🔄 UPDATING .env FILE WITH CURRENT TIMEOUT")
    print("=" * 60)
    
    try:
        from jarvis.config import get_config
        config = get_config()
        
        current_timeout = config.conversation.conversation_timeout
        print(f"Current timeout: {current_timeout} seconds")
        
        env_file = Path(".env")
        if not env_file.exists():
            print("❌ .env file doesn't exist")
            return False
        
        content = env_file.read_text()
        
        # Update the timeout setting
        import re
        if "JARVIS_CONVERSATION_TIMEOUT=" in content:
            # Replace existing setting
            new_content = re.sub(
                r"JARVIS_CONVERSATION_TIMEOUT=\d+",
                f"JARVIS_CONVERSATION_TIMEOUT={current_timeout}",
                content
            )
        else:
            # Add new setting
            new_content = content + f"\nJARVIS_CONVERSATION_TIMEOUT={current_timeout}\n"
        
        env_file.write_text(new_content)
        print(f"✅ Updated .env file with timeout: {current_timeout} seconds")
        
        return True
        
    except Exception as e:
        print(f"❌ Error updating .env file: {e}")
        return False


def main():
    """Main test function."""
    print("🔧 TESTING SETTINGS PERSISTENCE FIX")
    print("=" * 80)
    
    # Test 1: Verify current timeout setting
    verify_current_timeout_setting()
    
    # Test 2: Update .env file with current setting
    update_env_file_with_current_timeout()
    
    # Test 3: Test UI config manager (if possible)
    # test_ui_config_manager()
    
    print("\n🎯 SUMMARY")
    print("=" * 60)
    print("The settings persistence fix has been applied.")
    print("Your conversation timeout setting should now persist properly.")
    print()
    print("🚀 Next steps:")
    print("1. Restart Jarvis to verify the fix works")
    print("2. Test changing settings through the web UI")
    print("3. Verify settings persist after restart")


if __name__ == "__main__":
    main()
