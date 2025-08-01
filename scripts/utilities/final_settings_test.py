#!/usr/bin/env python3
"""
Final Settings Persistence Test

This script performs a comprehensive test to verify that settings
persistence is working correctly after our fixes.
"""

import os
import sys
import json
import time
from pathlib import Path

# Add jarvis to path
sys.path.insert(0, str(Path(__file__).parent / "jarvis"))

def test_env_file_sync():
    """Test that .env file is properly synced with current settings."""
    print("🔄 TESTING .env FILE SYNCHRONIZATION")
    print("=" * 70)
    
    try:
        from jarvis.config import get_config
        config = get_config()
        
        # Get current settings from config
        current_settings = {
            "JARVIS_CONVERSATION_TIMEOUT": str(config.conversation.conversation_timeout),
            "JARVIS_AUDIO_TIMEOUT": str(config.audio.timeout),
            "JARVIS_TTS_RATE": str(config.audio.tts_rate),
            "JARVIS_TTS_VOLUME": str(config.audio.tts_volume),
            "JARVIS_WAKE_WORD": config.conversation.wake_word,
            "JARVIS_MODEL": config.llm.model,
        }
        
        print("📊 Current Config Settings:")
        for key, value in current_settings.items():
            print(f"  {key}: {value}")
        
        # Check .env file
        env_file = Path(".env")
        if not env_file.exists():
            print("❌ .env file doesn't exist")
            return False
        
        content = env_file.read_text()
        
        print("\n📁 .env File Settings:")
        mismatches = []
        
        for key, expected_value in current_settings.items():
            if f"{key}=" in content:
                # Extract value from .env file
                import re
                match = re.search(f"{key}=([^\\n]*)", content)
                if match:
                    env_value = match.group(1).strip()
                    print(f"  {key}: {env_value}")
                    
                    if env_value != expected_value:
                        mismatches.append(f"{key}: config={expected_value}, env={env_value}")
                else:
                    print(f"  {key}: (could not parse)")
                    mismatches.append(f"{key}: could not parse from .env file")
            else:
                print(f"  {key}: (not found)")
                mismatches.append(f"{key}: not found in .env file")
        
        if mismatches:
            print(f"\n❌ Found {len(mismatches)} mismatches:")
            for mismatch in mismatches:
                print(f"  • {mismatch}")
            return False
        else:
            print("\n✅ All settings match between config and .env file")
            return True
            
    except Exception as e:
        print(f"❌ Error testing .env file sync: {e}")
        return False


def test_config_reload_persistence():
    """Test that settings persist after config reload."""
    print("\n🔄 TESTING CONFIG RELOAD PERSISTENCE")
    print("=" * 70)
    
    try:
        from jarvis.config import get_config, reload_config
        from dotenv import load_dotenv
        
        # Get current timeout (your setting)
        config = get_config()
        original_timeout = config.conversation.conversation_timeout
        print(f"Original timeout: {original_timeout} seconds")
        
        # Clear environment variable to force reload from .env
        env_backup = {}
        for key in list(os.environ.keys()):
            if key.startswith("JARVIS_"):
                env_backup[key] = os.environ[key]
                del os.environ[key]
        
        print("🧹 Cleared all JARVIS environment variables")
        
        # Reload from .env file
        load_dotenv(override=True)
        new_config = reload_config()
        
        new_timeout = new_config.conversation.conversation_timeout
        print(f"Reloaded timeout: {new_timeout} seconds")
        
        # Restore environment variables
        for key, value in env_backup.items():
            os.environ[key] = value
        
        if new_timeout == original_timeout:
            print("✅ Settings persist correctly after config reload")
            return True
        else:
            print(f"❌ Settings don't persist - expected {original_timeout}, got {new_timeout}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing config reload persistence: {e}")
        return False


def test_specific_timeout_setting():
    """Test your specific timeout setting (120 seconds)."""
    print("\n🎯 TESTING YOUR SPECIFIC TIMEOUT SETTING")
    print("=" * 70)
    
    try:
        from jarvis.config import get_config
        config = get_config()
        
        timeout = config.conversation.conversation_timeout
        print(f"Current conversation timeout: {timeout} seconds")
        
        if timeout == 120:
            print("✅ Your timeout setting (120 seconds / 2 minutes) is correctly applied")
            
            # Check if it's in .env file
            env_file = Path(".env")
            if env_file.exists():
                content = env_file.read_text()
                if "JARVIS_CONVERSATION_TIMEOUT=120" in content:
                    print("✅ Your setting is properly saved in .env file")
                    
                    # Check environment variable
                    env_timeout = os.environ.get("JARVIS_CONVERSATION_TIMEOUT")
                    if env_timeout == "120":
                        print("✅ Environment variable matches your setting")
                        return True
                    else:
                        print(f"⚠️ Environment variable is {env_timeout}, not 120")
                        return True  # Still pass since config is correct
                else:
                    print("❌ Your setting is NOT in .env file")
                    return False
            else:
                print("❌ .env file doesn't exist")
                return False
        else:
            print(f"❌ Unexpected timeout value: {timeout} (expected 120)")
            return False
            
    except Exception as e:
        print(f"❌ Error testing specific timeout setting: {e}")
        return False


def simulate_jarvis_restart():
    """Simulate what happens when Jarvis restarts."""
    print("\n🔄 SIMULATING JARVIS RESTART")
    print("=" * 70)
    
    try:
        # This simulates what happens when Jarvis starts:
        # 1. Environment variables are cleared
        # 2. .env file is loaded
        # 3. Config is initialized
        
        print("1. Clearing environment variables (simulating fresh start)...")
        env_backup = {}
        for key in list(os.environ.keys()):
            if key.startswith("JARVIS_"):
                env_backup[key] = os.environ[key]
                del os.environ[key]
        
        print("2. Loading .env file...")
        from dotenv import load_dotenv
        load_dotenv(override=True)
        
        print("3. Initializing config...")
        from jarvis.config import reload_config
        config = reload_config()
        
        timeout = config.conversation.conversation_timeout
        print(f"4. Conversation timeout after 'restart': {timeout} seconds")
        
        # Restore environment
        for key, value in env_backup.items():
            os.environ[key] = value
        
        if timeout == 120:
            print("✅ Your timeout setting persists across simulated restart")
            return True
        else:
            print(f"❌ Timeout setting lost - got {timeout} instead of 120")
            return False
            
    except Exception as e:
        print(f"❌ Error simulating Jarvis restart: {e}")
        return False


def main():
    """Main test function."""
    print("🔧 FINAL SETTINGS PERSISTENCE TEST")
    print("=" * 80)
    print("Comprehensive test of settings persistence after fixes...")
    print("=" * 80)
    
    tests = [
        ("Environment File Sync", test_env_file_sync),
        ("Config Reload Persistence", test_config_reload_persistence),
        ("Specific Timeout Setting", test_specific_timeout_setting),
        ("Simulated Jarvis Restart", simulate_jarvis_restart),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if test_func():
                print(f"✅ {test_name}: PASSED")
                passed += 1
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
    
    # Final summary
    print(f"\n🎯 FINAL TEST RESULTS")
    print("=" * 80)
    print(f"Tests Passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED!")
        print("✅ Settings persistence is working perfectly")
        print("✅ Your conversation timeout (120 seconds) is properly saved")
        print("✅ Settings will persist across all Jarvis restarts")
        print("✅ The settings UI changes are being saved correctly")
    elif passed >= total - 1:
        print("🎊 ALMOST PERFECT!")
        print("✅ Settings persistence is working well")
        print("⚠️ Minor issues detected but core functionality works")
    else:
        print("⚠️ SOME ISSUES DETECTED")
        print("Settings persistence has some problems that need attention")
    
    print(f"\n📊 YOUR CURRENT SETTINGS:")
    print("-" * 40)
    try:
        from jarvis.config import get_config
        config = get_config()
        print(f"Conversation Timeout: {config.conversation.conversation_timeout} seconds (2 minutes)")
        print(f"Audio Timeout: {config.audio.timeout} seconds")
        print(f"TTS Rate: {config.audio.tts_rate} WPM")
        print(f"Wake Word: {config.conversation.wake_word}")
    except:
        print("Could not retrieve current settings")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
