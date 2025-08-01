#!/usr/bin/env python3
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
        lines = content.split('\n')
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
    updated_content = '\n'.join(new_lines)
    env_file.write_text(updated_content)
    
    print(f"\n✅ Synced {len(jarvis_vars)} settings to .env file")
    return True

def show_current_settings():
    """Show current settings values."""
    print("\n📊 CURRENT SETTINGS VALUES")
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
        print("\n🎉 Settings sync completed successfully!")
        print("Your settings should now persist across Jarvis restarts.")
    else:
        print("\n❌ Settings sync failed.")
        print("Make sure Jarvis is running or has been run recently.")
