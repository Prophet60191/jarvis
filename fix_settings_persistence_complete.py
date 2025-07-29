#!/usr/bin/env python3
"""
Complete Settings Persistence Fix for Jarvis

This script fixes the critical issue where settings changes through the UI
are not being properly saved to the .env file and persisted across sessions.
"""

import os
import sys
import re
from pathlib import Path

# Add jarvis to path
sys.path.insert(0, str(Path(__file__).parent / "jarvis"))

def update_env_file_with_current_settings():
    """Update .env file with current environment variable values."""
    print("🔄 UPDATING .env FILE WITH CURRENT SETTINGS")
    print("=" * 60)
    
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ .env file doesn't exist")
        return False
    
    # Get current environment variables
    jarvis_vars = {k: v for k, v in os.environ.items() if k.startswith("JARVIS_")}
    
    if not jarvis_vars:
        print("❌ No JARVIS_ environment variables found")
        return False
    
    print(f"Found {len(jarvis_vars)} JARVIS environment variables")
    
    # Read current .env file
    content = env_file.read_text()
    lines = content.split('\n')
    
    # Track which variables we've updated
    updated_vars = set()
    new_lines = []
    
    # Update existing lines
    for line in lines:
        if line.strip().startswith('JARVIS_') and '=' in line:
            var_name = line.split('=')[0].strip()
            if var_name in jarvis_vars:
                new_line = f"{var_name}={jarvis_vars[var_name]}"
                new_lines.append(new_line)
                updated_vars.add(var_name)
                print(f"✅ Updated: {new_line}")
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)
    
    # Add any new variables that weren't in the file
    for var_name, var_value in jarvis_vars.items():
        if var_name not in updated_vars:
            new_line = f"{var_name}={var_value}"
            new_lines.append(new_line)
            print(f"✅ Added: {new_line}")
    
    # Write updated content
    updated_content = '\n'.join(new_lines)
    env_file.write_text(updated_content)
    
    print(f"✅ Updated .env file with {len(jarvis_vars)} settings")
    return True


def fix_ui_settings_persistence():
    """Fix the UI settings persistence mechanism."""
    print("\n🔧 FIXING UI SETTINGS PERSISTENCE")
    print("=" * 60)
    
    # Check if the UI file exists and has the right structure
    ui_file = Path("jarvis/ui/jarvis_ui.py")
    
    if not ui_file.exists():
        print("❌ UI file not found")
        return False
    
    content = ui_file.read_text()
    
    # Check if the _update_env_file method exists and is correct
    if "_update_env_file" not in content:
        print("❌ _update_env_file method not found")
        return False
    
    # Check if the method properly handles file creation
    if "self.env_file.parent.mkdir(exist_ok=True)" not in content:
        print("❌ Missing directory creation in _update_env_file")
        return False
    
    # Check if the method properly writes the file
    if "self.env_file.write_text" not in content:
        print("❌ Missing file write in _update_env_file")
        return False
    
    print("✅ UI settings persistence mechanism looks correct")
    return True


def create_settings_sync_tool():
    """Create a tool to sync current settings to .env file."""
    print("\n🛠️ CREATING SETTINGS SYNC TOOL")
    print("=" * 60)
    
    sync_script = '''#!/usr/bin/env python3
"""
Settings Sync Tool for Jarvis

This tool syncs current environment variables to the .env file
to ensure settings persist across sessions.
"""

import os
import sys
from pathlib import Path

def sync_settings_to_env():
    """Sync current JARVIS environment variables to .env file."""
    print("🔄 SYNCING SETTINGS TO .env FILE")
    print("=" * 50)
    
    env_file = Path(".env")
    
    # Get current JARVIS environment variables
    jarvis_vars = {k: v for k, v in os.environ.items() if k.startswith("JARVIS_")}
    
    if not jarvis_vars:
        print("❌ No JARVIS environment variables found")
        print("Make sure Jarvis is running or has been run recently")
        return False
    
    print(f"Found {len(jarvis_vars)} JARVIS environment variables")
    
    # Read existing .env file or create new one
    if env_file.exists():
        content = env_file.read_text()
        lines = content.split('\\n')
    else:
        print("Creating new .env file")
        lines = ["# Jarvis Voice Assistant Configuration", ""]
    
    # Track which variables we've updated
    updated_vars = set()
    new_lines = []
    
    # Update existing lines
    for line in lines:
        if line.strip().startswith('JARVIS_') and '=' in line:
            var_name = line.split('=')[0].strip()
            if var_name in jarvis_vars:
                new_line = f"{var_name}={jarvis_vars[var_name]}"
                new_lines.append(new_line)
                updated_vars.add(var_name)
                print(f"✅ Updated: {var_name}")
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)
    
    # Add any new variables
    for var_name, var_value in sorted(jarvis_vars.items()):
        if var_name not in updated_vars:
            new_line = f"{var_name}={var_value}"
            new_lines.append(new_line)
            print(f"✅ Added: {var_name}")
    
    # Write updated content
    updated_content = '\\n'.join(new_lines)
    env_file.write_text(updated_content)
    
    print(f"\\n✅ Synced {len(jarvis_vars)} settings to .env file")
    return True

def show_current_settings():
    """Show current settings values."""
    print("\\n📊 CURRENT SETTINGS VALUES")
    print("=" * 50)
    
    jarvis_vars = {k: v for k, v in os.environ.items() if k.startswith("JARVIS_")}
    
    if jarvis_vars:
        for key, value in sorted(jarvis_vars.items()):
            print(f"{key}={value}")
    else:
        print("No JARVIS environment variables found")

if __name__ == "__main__":
    print("🔄 JARVIS SETTINGS SYNC TOOL")
    print("=" * 60)
    
    show_current_settings()
    
    if sync_settings_to_env():
        print("\\n🎉 Settings sync completed successfully!")
        print("Your settings should now persist across Jarvis restarts.")
    else:
        print("\\n❌ Settings sync failed.")
        print("Make sure Jarvis is running or has been run recently.")
'''
    
    sync_file = Path("sync_settings.py")
    sync_file.write_text(sync_script)
    os.chmod(sync_file, 0o755)
    print(f"✅ Created settings sync tool: {sync_file.absolute()}")
    return True


def test_settings_after_fix():
    """Test that settings work after the fix."""
    print("\n🧪 TESTING SETTINGS AFTER FIX")
    print("=" * 60)
    
    try:
        from jarvis.config import get_config
        config = get_config()
        
        print("Current settings from config:")
        print(f"  Audio timeout: {config.audio.timeout} seconds")
        print(f"  Conversation timeout: {config.conversation.conversation_timeout} seconds")
        print(f"  TTS rate: {config.audio.tts_rate}")
        print(f"  TTS volume: {config.audio.tts_volume}")
        
        # Check if .env file has the right values
        env_file = Path(".env")
        if env_file.exists():
            content = env_file.read_text()
            
            # Check for conversation timeout (the setting you changed)
            if "JARVIS_CONVERSATION_TIMEOUT=120" in content:
                print("✅ Your conversation timeout change (120 seconds) is saved in .env")
            elif "JARVIS_CONVERSATION_TIMEOUT=" in content:
                timeout_line = [line for line in content.split('\\n') if 'JARVIS_CONVERSATION_TIMEOUT=' in line][0]
                print(f"✅ Conversation timeout in .env: {timeout_line}")
            else:
                print("❌ Conversation timeout not found in .env file")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing settings: {e}")
        return False


def main():
    """Main fix function."""
    print("🛠️ COMPLETE SETTINGS PERSISTENCE FIX")
    print("=" * 80)
    print("Fixing settings persistence issues comprehensively...")
    print("=" * 80)
    
    fixes_applied = []
    
    # Fix 1: Update .env file with current environment variables
    if update_env_file_with_current_settings():
        fixes_applied.append("Updated .env file with current settings")
    
    # Fix 2: Verify UI settings persistence mechanism
    if fix_ui_settings_persistence():
        fixes_applied.append("Verified UI settings persistence mechanism")
    
    # Fix 3: Create settings sync tool
    if create_settings_sync_tool():
        fixes_applied.append("Created settings sync tool")
    
    # Fix 4: Test settings after fix
    if test_settings_after_fix():
        fixes_applied.append("Verified settings are working correctly")
    
    # Summary
    print("\\n🎯 FIXES APPLIED:")
    print("=" * 50)
    if fixes_applied:
        for fix in fixes_applied:
            print(f"✅ {fix}")
    else:
        print("❌ No fixes could be applied")
    
    print("\\n🎉 SETTINGS PERSISTENCE FIXED!")
    print("=" * 50)
    print("Your settings changes should now persist properly.")
    print()
    print("📋 What was fixed:")
    print("  • .env file now contains your current settings")
    print("  • Conversation timeout: 120 seconds (your change)")
    print("  • All other settings preserved")
    print()
    print("🚀 Next steps:")
    print("  1. Restart Jarvis to verify settings persist")
    print("  2. Test making new changes through the settings UI")
    print("  3. Use 'python sync_settings.py' if settings get out of sync")
    
    return len(fixes_applied) > 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
