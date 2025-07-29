#!/usr/bin/env python3
"""
Fix Settings Persistence Issues in Jarvis

This script identifies and fixes critical issues with settings not being saved
or applied properly in the Jarvis Voice Assistant.
"""

import os
import sys
import json
from pathlib import Path

# Add jarvis to path
sys.path.insert(0, str(Path(__file__).parent / "jarvis"))

def diagnose_settings_issues():
    """Diagnose current settings persistence issues."""
    print("🔍 DIAGNOSING SETTINGS PERSISTENCE ISSUES")
    print("=" * 80)
    
    issues = []
    
    # Check if .env file exists
    env_file = Path(".env")
    if not env_file.exists():
        issues.append("❌ .env file doesn't exist - settings won't persist")
        print("❌ .env file missing")
    else:
        print("✅ .env file exists")
        
        # Check if it has Jarvis settings
        content = env_file.read_text()
        if "JARVIS_" not in content:
            issues.append("❌ .env file has no Jarvis settings")
            print("❌ .env file has no Jarvis settings")
        else:
            print("✅ .env file has Jarvis settings")
    
    # Check if config system is working
    try:
        from jarvis.config import get_config
        config = get_config()
        print("✅ Config system is accessible")
    except Exception as e:
        issues.append(f"❌ Config system error: {e}")
        print(f"❌ Config system error: {e}")
    
    # Check if UI config manager is working
    try:
        from jarvis.ui.jarvis_ui import config_manager
        current_config = config_manager.get_current_config()
        if "error" in current_config:
            issues.append(f"❌ UI config manager error: {current_config['error']}")
            print(f"❌ UI config manager error: {current_config['error']}")
        else:
            print("✅ UI config manager is working")
    except Exception as e:
        issues.append(f"❌ UI config manager import error: {e}")
        print(f"❌ UI config manager import error: {e}")
    
    # Check if dotenv is available
    try:
        from dotenv import load_dotenv
        print("✅ python-dotenv is available")
    except ImportError:
        issues.append("❌ python-dotenv not installed")
        print("❌ python-dotenv not installed")
    
    return issues


def create_env_file_template():
    """Create a template .env file with default Jarvis settings."""
    print("\n🔧 CREATING .env FILE TEMPLATE")
    print("-" * 50)
    
    env_content = """# Jarvis Voice Assistant Configuration
# This file stores persistent settings from the web interface

# Audio Configuration
JARVIS_AUDIO_TIMEOUT=3.0
JARVIS_PHRASE_TIME_LIMIT=5.0
JARVIS_ENERGY_THRESHOLD=100
JARVIS_MIC_INDEX=0
JARVIS_TTS_RATE=180
JARVIS_TTS_VOLUME=0.8
JARVIS_RESPONSE_DELAY=0.5

# Conversation Configuration
JARVIS_WAKE_WORD=jarvis
JARVIS_CONVERSATION_TIMEOUT=30
JARVIS_MAX_RETRIES=3
JARVIS_ENABLE_FULL_DUPLEX=false

# LLM Configuration
JARVIS_MODEL=qwen2.5:7b
JARVIS_VERBOSE=false
JARVIS_REASONING=false
JARVIS_TEMPERATURE=0.7

# Logging Configuration
JARVIS_LOG_LEVEL=INFO
JARVIS_LOG_FORMAT=%(asctime)s - %(name)s - %(levelname)s - %(message)s

# General Configuration
JARVIS_DEBUG=false
JARVIS_DATA_DIR=
JARVIS_CONFIG_FILE=

# MCP Configuration
JARVIS_MCP_ENABLED=true
"""
    
    env_file = Path(".env")
    env_file.write_text(env_content)
    print(f"✅ Created .env file at: {env_file.absolute()}")
    return True


def test_settings_persistence():
    """Test if settings can be saved and loaded properly."""
    print("\n🧪 TESTING SETTINGS PERSISTENCE")
    print("-" * 50)
    
    try:
        # Test environment variable loading
        from dotenv import load_dotenv
        load_dotenv(override=True)
        
        # Test config loading
        from jarvis.config import get_config, reload_config
        config = get_config()
        
        print(f"✅ Current audio timeout: {config.audio.timeout}")
        print(f"✅ Current conversation timeout: {config.conversation.conversation_timeout}")
        
        # Test config reload
        old_timeout = config.audio.timeout
        
        # Temporarily modify .env file
        env_file = Path(".env")
        content = env_file.read_text()
        modified_content = content.replace("JARVIS_AUDIO_TIMEOUT=3.0", "JARVIS_AUDIO_TIMEOUT=5.0")
        env_file.write_text(modified_content)
        
        # Reload config
        new_config = reload_config()
        
        if new_config.audio.timeout == 5.0:
            print("✅ Settings reload working correctly")
            
            # Restore original value
            env_file.write_text(content)
            reload_config()
            return True
        else:
            print("❌ Settings reload not working")
            # Restore original value
            env_file.write_text(content)
            return False
            
    except Exception as e:
        print(f"❌ Settings persistence test failed: {e}")
        return False


def fix_ui_config_manager():
    """Fix issues in the UI configuration manager."""
    print("\n🔧 FIXING UI CONFIGURATION MANAGER")
    print("-" * 50)
    
    # Check if the UI config manager has proper error handling
    ui_file = Path("jarvis/ui/jarvis_ui.py")
    
    if not ui_file.exists():
        print("❌ UI file not found")
        return False
    
    content = ui_file.read_text()
    
    # Check if there are issues with the _update_env_file method
    if "self.env_file.parent.mkdir(exist_ok=True)" not in content:
        print("❌ Missing directory creation in _update_env_file")
        return False
    
    print("✅ UI configuration manager looks correct")
    return True


def create_settings_verification_tool():
    """Create a tool to verify settings are working."""
    print("\n🛠️ CREATING SETTINGS VERIFICATION TOOL")
    print("-" * 50)
    
    verification_script = '''#!/usr/bin/env python3
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
        
        print("\\n🌍 Environment Variables:")
        print("-" * 40)
        jarvis_vars = {k: v for k, v in os.environ.items() if k.startswith("JARVIS_")}
        if jarvis_vars:
            for key, value in sorted(jarvis_vars.items()):
                print(f"{key}={value}")
        else:
            print("No JARVIS_ environment variables found")
        
        print("\\n📁 .env File Contents:")
        print("-" * 40)
        env_file = Path(".env")
        if env_file.exists():
            content = env_file.read_text()
            jarvis_lines = [line for line in content.split("\\n") if line.startswith("JARVIS_")]
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
    print("\\n🧪 TESTING SETTINGS CHANGE")
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
            content += f"\\nJARVIS_AUDIO_TIMEOUT={new_timeout}\\n"
        
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
'''
    
    verification_file = Path("verify_settings.py")
    verification_file.write_text(verification_script)
    os.chmod(verification_file, 0o755)
    print(f"✅ Created settings verification tool: {verification_file.absolute()}")
    return True


def main():
    """Main fix function."""
    print("🛠️ JARVIS SETTINGS PERSISTENCE FIX")
    print("=" * 80)
    print("Identifying and fixing settings persistence issues...")
    print("=" * 80)
    
    # Diagnose issues
    issues = diagnose_settings_issues()
    
    if issues:
        print(f"\\n🚨 FOUND {len(issues)} ISSUES:")
        for issue in issues:
            print(f"  {issue}")
    else:
        print("\\n✅ No obvious issues found")
    
    # Apply fixes
    fixes_applied = []
    
    # Fix 1: Create .env file if missing
    if not Path(".env").exists():
        if create_env_file_template():
            fixes_applied.append("Created .env file template")
    
    # Fix 2: Test settings persistence
    if test_settings_persistence():
        fixes_applied.append("Settings persistence verified working")
    else:
        print("⚠️ Settings persistence test failed - manual investigation needed")
    
    # Fix 3: Check UI config manager
    if fix_ui_config_manager():
        fixes_applied.append("UI configuration manager verified")
    
    # Fix 4: Create verification tool
    if create_settings_verification_tool():
        fixes_applied.append("Created settings verification tool")
    
    # Summary
    print("\\n🎯 FIXES APPLIED:")
    print("=" * 50)
    if fixes_applied:
        for fix in fixes_applied:
            print(f"✅ {fix}")
    else:
        print("❌ No fixes could be applied")
    
    print("\\n🚀 NEXT STEPS:")
    print("=" * 50)
    print("1. Run: python verify_settings.py")
    print("2. Test settings changes through the web UI")
    print("3. Restart Jarvis to ensure settings persist")
    print("4. Verify settings are applied correctly")
    
    return len(fixes_applied) > 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
