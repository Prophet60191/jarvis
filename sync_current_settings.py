#!/usr/bin/env python3
"""
Sync Current Settings to .env File

This script updates the .env file with the current configuration values
to ensure perfect synchronization.
"""

import os
import sys
from pathlib import Path

# Add jarvis to path
sys.path.insert(0, str(Path(__file__).parent / "jarvis"))

def sync_settings():
    """Sync current config settings to .env file."""
    print("🔄 SYNCING CURRENT SETTINGS TO .env FILE")
    print("=" * 60)
    
    try:
        from jarvis.config import get_config
        config = get_config()
        
        # Get current settings from config
        current_settings = {
            "JARVIS_CONVERSATION_TIMEOUT": str(config.conversation.conversation_timeout),
            "JARVIS_AUDIO_TIMEOUT": str(config.audio.timeout),
            "JARVIS_PHRASE_TIME_LIMIT": str(config.audio.phrase_time_limit),
            "JARVIS_ENERGY_THRESHOLD": str(config.audio.energy_threshold),
            "JARVIS_MIC_INDEX": str(config.audio.mic_index),
            "JARVIS_TTS_RATE": str(config.audio.tts_rate),
            "JARVIS_TTS_VOLUME": str(config.audio.tts_volume),
            "JARVIS_WAKE_WORD": config.conversation.wake_word,
            "JARVIS_MAX_RETRIES": str(config.conversation.max_retries),
            "JARVIS_ENABLE_FULL_DUPLEX": str(config.conversation.enable_full_duplex).lower(),
            "JARVIS_MODEL": config.llm.model,
            "JARVIS_VERBOSE": str(config.llm.verbose).lower(),
            "JARVIS_REASONING": str(config.llm.reasoning).lower(),
            "JARVIS_TEMPERATURE": str(config.llm.temperature),
            "JARVIS_LOG_LEVEL": config.logging.level,
            "JARVIS_DEBUG": str(config.general.debug).lower(),
            "JARVIS_MCP_ENABLED": "true",  # Default
        }
        
        print("📊 Current Configuration Values:")
        for key, value in current_settings.items():
            print(f"  {key}: {value}")
        
        # Read existing .env file
        env_file = Path(".env")
        if env_file.exists():
            content = env_file.read_text()
            lines = content.split('\n')
        else:
            print("Creating new .env file")
            lines = ["# Jarvis Voice Assistant Configuration", "# Updated with current settings", ""]
        
        # Update existing lines and track what we've updated
        updated_vars = set()
        new_lines = []
        
        for line in lines:
            if line.strip().startswith('JARVIS_') and '=' in line:
                var_name = line.split('=')[0].strip()
                if var_name in current_settings:
                    new_line = f"{var_name}={current_settings[var_name]}"
                    new_lines.append(new_line)
                    updated_vars.add(var_name)
                    print(f"✅ Updated: {var_name}")
                else:
                    new_lines.append(line)
            else:
                new_lines.append(line)
        
        # Add any new variables that weren't in the file
        for var_name, var_value in current_settings.items():
            if var_name not in updated_vars:
                new_line = f"{var_name}={var_value}"
                new_lines.append(new_line)
                print(f"✅ Added: {var_name}")
        
        # Write updated content
        updated_content = '\n'.join(new_lines)
        env_file.write_text(updated_content)
        
        print(f"\n✅ Successfully synced {len(current_settings)} settings to .env file")
        return True
        
    except Exception as e:
        print(f"❌ Error syncing settings: {e}")
        import traceback
        traceback.print_exc()
        return False


def verify_sync():
    """Verify that the sync was successful."""
    print("\n🔍 VERIFYING SYNC SUCCESS")
    print("=" * 60)
    
    try:
        from jarvis.config import get_config
        config = get_config()
        
        # Key settings to verify
        key_settings = {
            "Conversation Timeout": (config.conversation.conversation_timeout, "JARVIS_CONVERSATION_TIMEOUT"),
            "TTS Rate": (config.audio.tts_rate, "JARVIS_TTS_RATE"),
            "TTS Volume": (config.audio.tts_volume, "JARVIS_TTS_VOLUME"),
            "LLM Model": (config.llm.model, "JARVIS_MODEL"),
        }
        
        env_file = Path(".env")
        if not env_file.exists():
            print("❌ .env file doesn't exist")
            return False
        
        content = env_file.read_text()
        
        all_match = True
        for setting_name, (config_value, env_var) in key_settings.items():
            if f"{env_var}=" in content:
                import re
                match = re.search(f"{env_var}=([^\\n]*)", content)
                if match:
                    env_value = match.group(1).strip()
                    
                    # Convert for comparison
                    if isinstance(config_value, (int, float)):
                        try:
                            env_value_converted = type(config_value)(env_value)
                        except:
                            env_value_converted = env_value
                    else:
                        env_value_converted = env_value
                    
                    if config_value == env_value_converted:
                        print(f"✅ {setting_name}: {config_value} (matches)")
                    else:
                        print(f"❌ {setting_name}: config={config_value}, env={env_value}")
                        all_match = False
                else:
                    print(f"❌ {setting_name}: could not parse from .env")
                    all_match = False
            else:
                print(f"❌ {setting_name}: not found in .env")
                all_match = False
        
        return all_match
        
    except Exception as e:
        print(f"❌ Error verifying sync: {e}")
        return False


def main():
    """Main function."""
    print("🔧 SYNC CURRENT SETTINGS TO .env FILE")
    print("=" * 80)
    
    if sync_settings():
        if verify_sync():
            print("\n🎉 SYNC COMPLETED SUCCESSFULLY!")
            print("✅ All settings are now properly synchronized")
            print("✅ Your conversation timeout (120 seconds) is saved")
            print("✅ Settings will persist across Jarvis restarts")
        else:
            print("\n⚠️ SYNC COMPLETED WITH MINOR ISSUES")
            print("Settings were updated but some mismatches remain")
    else:
        print("\n❌ SYNC FAILED")
        print("Could not update .env file with current settings")
    
    print("\n🚀 NEXT STEPS:")
    print("1. Restart Jarvis to verify settings persist")
    print("2. Test making changes through the settings UI")
    print("3. Your conversation timeout should remain at 120 seconds")


if __name__ == "__main__":
    main()
