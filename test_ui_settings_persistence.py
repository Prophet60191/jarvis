#!/usr/bin/env python3
"""
Test UI Settings Persistence

This script tests that settings changes through the UI are properly
saved and persist across configuration reloads.
"""

import os
import sys
import json
from pathlib import Path

# Add jarvis to path
sys.path.insert(0, str(Path(__file__).parent / "jarvis"))

def test_conversation_timeout_persistence():
    """Test that your conversation timeout setting persists properly."""
    print("🧪 TESTING CONVERSATION TIMEOUT PERSISTENCE")
    print("=" * 70)
    
    try:
        from jarvis.config import get_config, reload_config
        from dotenv import load_dotenv
        
        # Get current config
        config = get_config()
        current_timeout = config.conversation.conversation_timeout
        
        print(f"Current conversation timeout: {current_timeout} seconds")
        
        # Check if it matches your setting (120 seconds)
        if current_timeout == 120:
            print("✅ Your timeout setting (120 seconds / 2 minutes) is active")
        else:
            print(f"⚠️ Unexpected timeout value: {current_timeout}")
        
        # Check .env file
        env_file = Path(".env")
        if env_file.exists():
            content = env_file.read_text()
            if "JARVIS_CONVERSATION_TIMEOUT=120" in content:
                print("✅ Your setting is saved in .env file")
            else:
                print("❌ Your setting is NOT saved in .env file")
                return False
        else:
            print("❌ .env file doesn't exist")
            return False
        
        # Test reload from .env file
        print("\n🔄 Testing configuration reload...")
        
        # Clear environment variable to force reload from .env
        if "JARVIS_CONVERSATION_TIMEOUT" in os.environ:
            old_env_value = os.environ["JARVIS_CONVERSATION_TIMEOUT"]
            del os.environ["JARVIS_CONVERSATION_TIMEOUT"]
        else:
            old_env_value = None
        
        # Reload from .env file
        load_dotenv(override=True)
        new_config = reload_config()
        
        if new_config.conversation.conversation_timeout == 120:
            print("✅ Settings reload successful - timeout persists from .env file")
            
            # Restore environment variable if it existed
            if old_env_value:
                os.environ["JARVIS_CONVERSATION_TIMEOUT"] = old_env_value
            
            return True
        else:
            print(f"❌ Settings reload failed - got {new_config.conversation.conversation_timeout} instead of 120")
            
            # Restore environment variable if it existed
            if old_env_value:
                os.environ["JARVIS_CONVERSATION_TIMEOUT"] = old_env_value
            
            return False
        
    except Exception as e:
        print(f"❌ Error testing conversation timeout persistence: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_ui_config_update_simulation():
    """Simulate a UI configuration update to test the persistence mechanism."""
    print("\n🎮 SIMULATING UI CONFIGURATION UPDATE")
    print("=" * 70)
    
    try:
        # Import the UI config manager
        sys.path.insert(0, str(Path(__file__).parent / "jarvis" / "ui"))
        from jarvis_ui import ConfigManager
        
        config_manager = ConfigManager()
        print("✅ ConfigManager loaded successfully")
        
        # Get current conversation timeout
        from jarvis.config import get_config
        config = get_config()
        original_timeout = config.conversation.conversation_timeout
        print(f"Original timeout: {original_timeout} seconds")
        
        # Test updating to a different value
        test_timeout = 90  # 1.5 minutes
        test_updates = {
            "conversation": {
                "conversation_timeout": test_timeout
            }
        }
        
        print(f"🔄 Testing update to {test_timeout} seconds...")
        result = config_manager.update_config(test_updates)
        
        if result.get("success"):
            print("✅ UI configuration update successful")
            
            # Check if .env file was updated
            env_file = Path(".env")
            content = env_file.read_text()
            
            if f"JARVIS_CONVERSATION_TIMEOUT={test_timeout}" in content:
                print("✅ .env file updated correctly")
                
                # Verify config reload works
                from jarvis.config import reload_config
                new_config = reload_config()
                
                if new_config.conversation.conversation_timeout == test_timeout:
                    print("✅ Configuration reload successful")
                    
                    # Restore original setting
                    restore_updates = {
                        "conversation": {
                            "conversation_timeout": original_timeout
                        }
                    }
                    config_manager.update_config(restore_updates)
                    print(f"✅ Original setting ({original_timeout} seconds) restored")
                    
                    return True
                else:
                    print(f"❌ Configuration reload failed - got {new_config.conversation.conversation_timeout}")
                    return False
            else:
                print("❌ .env file not updated correctly")
                print(f"Looking for: JARVIS_CONVERSATION_TIMEOUT={test_timeout}")
                print(f"Found in file: {[line for line in content.split() if 'CONVERSATION_TIMEOUT' in line]}")
                return False
        else:
            print(f"❌ UI configuration update failed: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error simulating UI config update: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_other_settings_persistence():
    """Test that other settings you might have changed also persist."""
    print("\n🔍 CHECKING OTHER SETTINGS PERSISTENCE")
    print("=" * 70)
    
    try:
        from jarvis.config import get_config
        config = get_config()
        
        # Check various settings that might have been changed
        settings_to_check = [
            ("TTS Rate", config.audio.tts_rate, "JARVIS_TTS_RATE"),
            ("TTS Volume", config.audio.tts_volume, "JARVIS_TTS_VOLUME"),
            ("Audio Timeout", config.audio.timeout, "JARVIS_AUDIO_TIMEOUT"),
            ("Wake Word", config.conversation.wake_word, "JARVIS_WAKE_WORD"),
            ("LLM Model", config.llm.model, "JARVIS_MODEL"),
        ]
        
        env_file = Path(".env")
        if not env_file.exists():
            print("❌ .env file doesn't exist")
            return False
        
        content = env_file.read_text()
        
        print("📊 Settings Persistence Check:")
        print("-" * 40)
        
        all_good = True
        for setting_name, config_value, env_var in settings_to_check:
            # Check if environment variable exists
            env_value = os.environ.get(env_var)
            
            # Check if it's in .env file
            env_file_has_setting = f"{env_var}=" in content
            
            if env_value is not None:
                # Convert for comparison
                if isinstance(config_value, bool):
                    env_value_converted = env_value.lower() == "true"
                elif isinstance(config_value, (int, float)):
                    env_value_converted = type(config_value)(env_value)
                else:
                    env_value_converted = env_value
                
                if config_value == env_value_converted:
                    status = "✅" if env_file_has_setting else "⚠️"
                    persistence = "in .env" if env_file_has_setting else "env only"
                    print(f"{status} {setting_name}: {config_value} ({persistence})")
                    
                    if not env_file_has_setting:
                        all_good = False
                else:
                    print(f"❌ {setting_name}: config={config_value}, env={env_value_converted}")
                    all_good = False
            else:
                print(f"⚠️ {setting_name}: {config_value} (no env var)")
        
        return all_good
        
    except Exception as e:
        print(f"❌ Error checking other settings: {e}")
        return False


def main():
    """Main test function."""
    print("🔧 COMPREHENSIVE SETTINGS PERSISTENCE TEST")
    print("=" * 80)
    print("Testing that all settings changes are properly saved and persist...")
    print("=" * 80)
    
    tests_passed = 0
    total_tests = 3
    
    # Test 1: Conversation timeout persistence
    if test_conversation_timeout_persistence():
        tests_passed += 1
        print("✅ Test 1 PASSED: Conversation timeout persistence")
    else:
        print("❌ Test 1 FAILED: Conversation timeout persistence")
    
    # Test 2: UI config update simulation
    if test_ui_config_update_simulation():
        tests_passed += 1
        print("✅ Test 2 PASSED: UI configuration update simulation")
    else:
        print("❌ Test 2 FAILED: UI configuration update simulation")
    
    # Test 3: Other settings persistence
    if test_other_settings_persistence():
        tests_passed += 1
        print("✅ Test 3 PASSED: Other settings persistence")
    else:
        print("❌ Test 3 FAILED: Other settings persistence")
    
    # Summary
    print(f"\n🎯 TEST RESULTS: {tests_passed}/{total_tests} PASSED")
    print("=" * 80)
    
    if tests_passed == total_tests:
        print("🎉 ALL TESTS PASSED!")
        print("✅ Settings persistence is working correctly")
        print("✅ Your conversation timeout (120 seconds) is properly saved")
        print("✅ UI changes will persist across Jarvis restarts")
    elif tests_passed > 0:
        print("⚠️ SOME TESTS PASSED")
        print("Settings persistence is partially working")
        print("Some issues may need additional attention")
    else:
        print("❌ ALL TESTS FAILED")
        print("Settings persistence is not working properly")
        print("Manual investigation required")
    
    print(f"\n🚀 Your conversation timeout is set to 120 seconds (2 minutes)")
    print("This setting should persist across all Jarvis sessions.")


if __name__ == "__main__":
    main()
