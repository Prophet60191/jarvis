#!/usr/bin/env python3
"""
Settings Verification Tool for Jarvis

This tool helps verify that settings changes are properly saved and applied.
"""

import os
import sys
from pathlib import Path

# Add jarvis to path
sys.path.insert(0, str(Path(__file__).parent / "jarvis"))

def verify_current_settings():
    """Verify current settings values."""
    print("🔍 CURRENT SETTINGS VERIFICATION")
    print("=" * 60)
    
    try:
        from jarvis.config import get_config
        config = get_config()
        
        print("📊 Current Configuration Values:")
        print("-" * 40)
        print(f"Audio timeout: {config.audio.timeout} seconds")
        print(f"Phrase time limit: {config.audio.phrase_time_limit} seconds")
        print(f"Energy threshold: {config.audio.energy_threshold}")
        print(f"Conversation timeout: {config.conversation.conversation_timeout} seconds")
        print(f"Wake word: {config.conversation.wake_word}")
        print(f"LLM model: {config.llm.model}")
        print(f"Debug mode: {config.general.debug}")
        
        print("\n🌍 Environment Variables:")
        print("-" * 40)
        jarvis_vars = {k: v for k, v in os.environ.items() if k.startswith("JARVIS_")}
        if jarvis_vars:
            for key, value in sorted(jarvis_vars.items()):
                print(f"{key}={value}")
        else:
            print("No JARVIS_ environment variables found")
        
        print("\n📁 .env File Contents:")
        print("-" * 40)
        env_file = Path(".env")
        if env_file.exists():
            content = env_file.read_text()
            jarvis_lines = [line for line in content.split("\n") if line.startswith("JARVIS_")]
            if jarvis_lines:
                for line in jarvis_lines:
                    print(line)
            else:
                print("No JARVIS_ settings in .env file")
        else:
            print(".env file does not exist")
            
        return True
        
    except Exception as e:
        print(f"❌ Error verifying settings: {e}")
        return False

def test_settings_change():
    """Test changing a setting and verifying it takes effect."""
    print("\n🧪 TESTING SETTINGS CHANGE")
    print("=" * 60)
    
    try:
        from jarvis.config import get_config, reload_config
        from dotenv import load_dotenv
        
        # Get current config
        config = get_config()
        original_timeout = config.audio.timeout
        print(f"Original audio timeout: {original_timeout}")
        
        # Modify .env file
        env_file = Path(".env")
        if not env_file.exists():
            print("❌ .env file doesn't exist")
            return False
        
        content = env_file.read_text()
        new_timeout = 7.5
        
        # Replace or add the timeout setting
        if "JARVIS_AUDIO_TIMEOUT=" in content:
            import re
            content = re.sub(r"JARVIS_AUDIO_TIMEOUT=.*", f"JARVIS_AUDIO_TIMEOUT={new_timeout}", content)
        else:
            content += f"\nJARVIS_AUDIO_TIMEOUT={new_timeout}\n"
        
        env_file.write_text(content)
        print(f"Modified .env file with timeout: {new_timeout}")
        
        # Reload configuration
        load_dotenv(override=True)
        new_config = reload_config()
        
        if abs(new_config.audio.timeout - new_timeout) < 0.01:
            print("✅ Settings change successful!")
            
            # Restore original value
            content = content.replace(f"JARVIS_AUDIO_TIMEOUT={new_timeout}", f"JARVIS_AUDIO_TIMEOUT={original_timeout}")
            env_file.write_text(content)
            load_dotenv(override=True)
            reload_config()
            print("✅ Original settings restored")
            return True
        else:
            print(f"❌ Settings change failed. Expected {new_timeout}, got {new_config.audio.timeout}")
            return False
            
    except Exception as e:
        print(f"❌ Settings change test failed: {e}")
        return False

if __name__ == "__main__":
    print("🎯 JARVIS SETTINGS VERIFICATION TOOL")
    print("=" * 80)
    
    success = verify_current_settings()
    if success:
        test_settings_change()
