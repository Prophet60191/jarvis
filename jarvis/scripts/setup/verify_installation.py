#!/usr/bin/env python3
"""
Installation verification script for Jarvis Voice Assistant.

This script checks if all components are properly installed and configured.
"""

import sys
import os
from pathlib import Path

def check_python_version():
    """Check Python version."""
    print("🐍 Checking Python version...")
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} (OK)")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} (Need 3.8+)")
        return False

def check_dependencies():
    """Check required dependencies."""
    print("\n📦 Checking dependencies...")
    
    required_packages = [
        ('langchain', 'LangChain'),
        ('langchain_ollama', 'LangChain Ollama'),
        ('speech_recognition', 'Speech Recognition'),
        ('pyttsx3', 'Text-to-Speech'),
        ('numpy', 'NumPy'),
        ('pytz', 'Timezone support')
    ]
    
    all_good = True
    for package, name in required_packages:
        try:
            __import__(package)
            print(f"✅ {name}")
        except ImportError:
            print(f"❌ {name} (missing)")
            all_good = False
    
    return all_good

def check_jarvis_structure():
    """Check Jarvis package structure."""
    print("\n🏗️  Checking Jarvis structure...")
    
    required_paths = [
        'jarvis/__init__.py',
        'jarvis/main.py',
        'jarvis/config.py',
        'jarvis/exceptions.py',
        'jarvis/audio/__init__.py',
        'jarvis/core/__init__.py',
        'jarvis/tools/__init__.py',
        'jarvis/utils/__init__.py',
    ]
    
    all_good = True
    for path in required_paths:
        if Path(path).exists():
            print(f"✅ {path}")
        else:
            print(f"❌ {path} (missing)")
            all_good = False
    
    return all_good

def check_ollama():
    """Check Ollama installation."""
    print("\n🧠 Checking Ollama...")
    
    try:
        import subprocess
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Ollama is installed and running")
            models = [line.split()[0] for line in result.stdout.strip().split('\n')[1:] if line.strip()]
            if models:
                print(f"📋 Available models: {', '.join(models)}")
            else:
                print("⚠️  No models installed. Run: ollama pull qwen2.5:1.5b")
            return True
        else:
            print("❌ Ollama not responding")
            return False
    except FileNotFoundError:
        print("❌ Ollama not installed")
        return False
    except Exception as e:
        print(f"❌ Ollama check failed: {e}")
        return False

def check_audio():
    """Check audio capabilities."""
    print("\n🎤 Checking audio capabilities...")
    
    try:
        import speech_recognition as sr
        mics = sr.Microphone.list_microphone_names()
        print(f"✅ Found {len(mics)} microphones")
        if mics:
            print(f"🎤 Default microphone: {mics[0] if mics else 'None'}")
    except Exception as e:
        print(f"❌ Microphone check failed: {e}")
        return False
    
    try:
        import pyttsx3
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        print(f"✅ Found {len(voices) if voices else 0} TTS voices")
        engine.stop()
    except Exception as e:
        print(f"❌ TTS check failed: {e}")
        return False
    
    return True

def check_configuration():
    """Check configuration."""
    print("\n⚙️  Checking configuration...")
    
    try:
        # Add project root to path
        sys.path.insert(0, str(Path(__file__).parent))
        
        from jarvis.config import get_config
        config = get_config()
        config.validate()
        print("✅ Configuration is valid")
        print(f"🎤 Microphone: {config.audio.mic_name}")
        print(f"🧠 Model: {config.llm.model}")
        print(f"👂 Wake word: {config.conversation.wake_word}")
        return True
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

def run_basic_test():
    """Run basic functionality test."""
    print("\n🧪 Running basic tests...")
    
    try:
        # Add project root to path
        sys.path.insert(0, str(Path(__file__).parent))
        
        from jarvis.tools import tool_registry
        tools = tool_registry.list_tools()
        print(f"✅ Found {len(tools)} tools: {', '.join(tools)}")
        
        # Test time tool (now available through plugin system)
        from jarvis.tools import get_langchain_tools
        langchain_tools = get_langchain_tools()
        time_tool = next((tool for tool in langchain_tools if tool.name == "get_current_time"), None)
        if time_tool:
            result = time_tool.invoke({})
            print(f"✅ Time tool working: {result}")
        else:
            print("❌ Time tool not found")
            return False
        
        # Test video tool
        result = tool_registry.execute_tool("video_day")
        if result.is_success:
            print("✅ Video tool working")
        else:
            print("❌ Video tool failed")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Basic test failed: {e}")
        return False

def main():
    """Main verification function."""
    print("🤖 Jarvis Voice Assistant - Installation Verification")
    print("=" * 60)
    
    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("Jarvis Structure", check_jarvis_structure),
        ("Ollama", check_ollama),
        ("Audio", check_audio),
        ("Configuration", check_configuration),
        ("Basic Tests", run_basic_test),
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ {name} check crashed: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 VERIFICATION SUMMARY")
    print("=" * 60)
    
    passed = 0
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {name}")
        if result:
            passed += 1
    
    print(f"\n🎯 {passed}/{len(results)} checks passed")
    
    if passed == len(results):
        print("\n🎉 All checks passed! Jarvis is ready to use.")
        print("\n🚀 Next steps:")
        print("   1. Run: python -m jarvis.main")
        print("   2. Say 'Jarvis' to activate")
        print("   3. Ask questions or give commands")
        return 0
    else:
        print(f"\n⚠️  {len(results) - passed} checks failed. Please fix the issues above.")
        print("\n🔧 Common fixes:")
        print("   - Install missing dependencies: pip install -r requirements.txt")
        print("   - Install Ollama: https://ollama.ai")
        print("   - Pull a model: ollama pull qwen2.5:1.5b")
        return 1

if __name__ == "__main__":
    sys.exit(main())
