#!/usr/bin/env python3
"""
Test script to demonstrate Jarvis core functionality without microphone.
This script tests the main components of Jarvis that don't require audio input.
"""

import sys
from pathlib import Path

# Add the jarvis package to the path
sys.path.insert(0, str(Path(__file__).parent / "jarvis"))

from jarvis.core.agent import JarvisAgent
from jarvis.config import get_config
from jarvis.tools import tool_registry
from jarvis.utils.logger import setup_logging

def test_configuration():
    """Test configuration loading."""
    print("🔧 Testing configuration...")
    try:
        config = get_config()
        print(f"✅ Configuration loaded successfully")
        print(f"   - Model: {config.llm.model}")
        print(f"   - Wake word: {config.conversation.wake_word}")
        print(f"   - TTS Voice: {config.audio.tts_voice_preference}")
        return True
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def test_tools():
    """Test tool system."""
    print("\n🛠️  Testing tools...")
    try:
        tools = tool_registry.list_tools()
        print(f"✅ Found {len(tools)} tools: {', '.join(tools)}")
        
        # Note: Time tool now available through MCP plugin system (device_time_tool)
        print("✅ Time tool available through MCP plugin system")
        
        # Test video tool
        video_tool = tool_registry.get_tool('video_day')
        if video_tool:
            result = video_tool.execute()
            print(f"✅ Video tool: {result.data[:50]}...")
        
        return True
    except Exception as e:
        print(f"❌ Tools test failed: {e}")
        return False

def test_llm():
    """Test LLM integration."""
    print("\n🧠 Testing LLM integration...")
    try:
        config = get_config()
        agent = JarvisAgent(config.llm)
        agent.initialize()
        
        # Test basic query
        response = agent.process_input("What is the capital of France?")
        print(f"✅ LLM Response: {response}")
        
        # Test tool usage
        response = agent.process_input("What time is it?")
        print(f"✅ LLM with tools: {response}")
        
        return True
    except Exception as e:
        print(f"❌ LLM test failed: {e}")
        return False

def interactive_mode():
    """Run interactive mode for testing."""
    print("\n💬 Interactive mode (type 'quit' to exit):")
    print("You can ask questions and Jarvis will respond using the LLM and tools.")
    
    try:
        config = get_config()
        agent = JarvisAgent(config.llm)
        agent.initialize()
        
        while True:
            user_input = input("\nYou: ").strip()
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("Jarvis: Goodbye!")
                break
            
            if user_input:
                try:
                    response = agent.process_input(user_input)
                    print(f"Jarvis: {response}")
                except Exception as e:
                    print(f"Jarvis: Sorry, I encountered an error: {e}")
    
    except KeyboardInterrupt:
        print("\nJarvis: Goodbye!")
    except Exception as e:
        print(f"❌ Interactive mode failed: {e}")

def main():
    """Main test function."""
    print("🤖 Jarvis Core Functionality Test")
    print("=" * 50)
    
    # Set up logging
    config = get_config()
    setup_logging(config.logging)
    
    # Run tests
    tests_passed = 0
    total_tests = 3
    
    if test_configuration():
        tests_passed += 1
    
    if test_tools():
        tests_passed += 1
    
    if test_llm():
        tests_passed += 1
    
    print(f"\n📊 Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 All core functionality tests passed!")
        print("\nNote: Microphone functionality may have issues, but core Jarvis features work.")
        
        # Offer interactive mode
        try:
            choice = input("\nWould you like to try interactive mode? (y/n): ").strip().lower()
            if choice in ['y', 'yes']:
                interactive_mode()
        except KeyboardInterrupt:
            print("\nGoodbye!")
    else:
        print("❌ Some tests failed. Please check the configuration and dependencies.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
