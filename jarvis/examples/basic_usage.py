#!/usr/bin/env python3
"""
Basic usage example for Jarvis Voice Assistant.

This script demonstrates how to use Jarvis programmatically,
including initialization, configuration, and basic interactions.
"""

import sys
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from jarvis.config import JarvisConfig, AudioConfig, ConversationConfig, LLMConfig
from jarvis.core.speech import SpeechManager
from jarvis.core.agent import JarvisAgent
from jarvis.core.conversation import ConversationManager
from jarvis.tools import get_langchain_tools
from jarvis.utils.logger import setup_logging, get_logger


def basic_speech_example():
    """Demonstrate basic speech recognition and TTS."""
    print("🎤 Basic Speech Example")
    print("=" * 40)
    
    # Create configuration
    audio_config = AudioConfig(
        mic_index=2,
        energy_threshold=100,
        timeout=3.0,
        phrase_time_limit=5.0
    )
    
    # Initialize speech manager
    speech_manager = SpeechManager(audio_config)
    
    try:
        speech_manager.initialize()
        print("✅ Speech system initialized")
        
        # Test TTS
        speech_manager.speak_text("Hello! I am Jarvis. Speech system is working.")
        
        # Test speech recognition
        print("🎤 Say something (you have 5 seconds)...")
        text = speech_manager.listen_for_speech(timeout=5.0)
        
        if text:
            print(f"👂 I heard: '{text}'")
            speech_manager.speak_text(f"You said: {text}")
        else:
            print("🔇 No speech detected")
            speech_manager.speak_text("I didn't hear anything")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        speech_manager.cleanup()


def basic_agent_example():
    """Demonstrate basic AI agent interaction."""
    print("\n🧠 Basic Agent Example")
    print("=" * 40)
    
    # Create configuration
    llm_config = LLMConfig(
        model="qwen2.5:1.5b",
        temperature=0.7,
        verbose=False
    )
    
    # Initialize agent
    agent = JarvisAgent(llm_config)
    
    try:
        # Get tools from both registry and plugins
        from jarvis.tools import get_langchain_tools
        langchain_tools = get_langchain_tools()
        agent.initialize(tools=langchain_tools)
        print(f"✅ Agent initialized with {len(langchain_tools)} tools")
        
        # Test basic interaction
        test_queries = [
            "Hello, how are you?",
            "What time is it?",
            "What time is it in Tokyo?",
            "Give me video content advice for today"
        ]
        
        for query in test_queries:
            print(f"\n👤 User: {query}")
            try:
                response = agent.process_input(query)
                print(f"🤖 Jarvis: {response}")
            except Exception as e:
                print(f"❌ Error processing query: {e}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        agent.cleanup()


def tool_usage_example():
    """Demonstrate tool usage."""
    print("\n🔧 Tool Usage Example")
    print("=" * 40)
    
    # List available tools
    tools = tool_registry.list_tools()
    print(f"📋 Available tools: {', '.join(tools)}")
    
    # Test time tool (now available as MCP plugin)
    print("\n⏰ Testing Time Tool:")
    try:
        # Note: Time tool is now available through MCP plugin system
        # Use plugin_manager to access device_time_tool
        print("Time tool now available through MCP plugin system (device_time_tool)")

    except Exception as e:
        print(f"❌ Time tool error: {e}")
    
    # Test video tool
    print("\n🎥 Testing Video Tool:")
    try:
        result = tool_registry.execute_tool("video_day")
        print(f"Video advice: {result.data[:200]}...")
        
        result = tool_registry.execute_tool("video_day", topic="productivity")
        print(f"Productivity advice: {result.data[:200]}...")
        
    except Exception as e:
        print(f"❌ Video tool error: {e}")


def conversation_example():
    """Demonstrate conversation management."""
    print("\n💬 Conversation Example")
    print("=" * 40)
    
    # Create configurations
    audio_config = AudioConfig(mic_index=2, timeout=2.0)
    conversation_config = ConversationConfig(wake_word="test", conversation_timeout=15)
    llm_config = LLMConfig(model="qwen2.5:1.5b")
    
    # Initialize components
    speech_manager = SpeechManager(audio_config)
    agent = JarvisAgent(llm_config)
    
    try:
        # Initialize components
        speech_manager.initialize()
        from jarvis.tools import get_langchain_tools
        langchain_tools = get_langchain_tools()
        agent.initialize(tools=langchain_tools)
        
        # Create conversation manager
        conversation_manager = ConversationManager(
            conversation_config,
            speech_manager,
            agent
        )
        
        print("✅ Conversation system initialized")
        
        # Simulate conversation flow
        print("🎤 Simulating conversation...")
        speech_manager.speak_text("Conversation system ready. Say 'test' to start.")
        
        # In a real scenario, you would listen for the wake word
        # For this example, we'll simulate it
        print("👂 Listening for wake word 'test'...")
        print("💡 In a real scenario, say 'test' followed by your question")
        
        # Simulate wake word detection
        time.sleep(1)
        print("✅ Wake word detected (simulated)")
        
        # Enter conversation mode
        conversation_manager.enter_conversation_mode()
        
        # Simulate user input
        test_command = "What time is it in Paris?"
        print(f"👤 Simulated user input: '{test_command}'")
        
        # Process command
        response = conversation_manager.process_command(test_command)
        print(f"🤖 Jarvis response: {response}")
        
        # Deliver response
        conversation_manager.respond(response)
        
        print("✅ Conversation example completed")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        speech_manager.cleanup()
        agent.cleanup()


def configuration_example():
    """Demonstrate configuration management."""
    print("\n⚙️ Configuration Example")
    print("=" * 40)
    
    # Create custom configuration
    config = JarvisConfig()
    
    # Display current configuration
    print("📋 Current Configuration:")
    print(f"  Wake word: {config.conversation.wake_word}")
    print(f"  Model: {config.llm.model}")
    print(f"  Microphone: {config.audio.mic_name} (index: {config.audio.mic_index})")
    print(f"  TTS Rate: {config.audio.tts_rate} WPM")
    print(f"  Log Level: {config.logging.level}")
    print(f"  Debug Mode: {config.general.debug}")
    
    # Validate configuration
    try:
        config.validate()
        print("✅ Configuration is valid")
    except Exception as e:
        print(f"❌ Configuration error: {e}")
    
    # Show environment variable mapping
    print("\n🌍 Environment Variables:")
    env_vars = [
        ("JARVIS_WAKE_WORD", config.conversation.wake_word),
        ("JARVIS_MODEL", config.llm.model),
        ("JARVIS_MIC_INDEX", config.audio.mic_index),
        ("JARVIS_LOG_LEVEL", config.logging.level),
    ]
    
    for var_name, value in env_vars:
        print(f"  {var_name}={value}")


def system_info_example():
    """Display system information."""
    print("\n💻 System Information")
    print("=" * 40)
    
    from jarvis.utils.helpers import get_system_info
    
    info = get_system_info()
    
    print(f"🖥️  Platform: {info['platform']}")
    print(f"🐍 Python: {info['python_version']} ({info['python_implementation']})")
    print(f"💾 Memory: {info.get('total_memory_gb', 'N/A')} GB total")
    print(f"🔧 CPU Cores: {info.get('cpu_count', 'N/A')}")
    
    # Check microphones
    try:
        import speech_recognition as sr
        mics = sr.Microphone.list_microphone_names()
        print(f"🎤 Microphones: {len(mics)} available")
        for i, name in enumerate(mics[:3]):  # Show first 3
            print(f"   {i}: {name}")
        if len(mics) > 3:
            print(f"   ... and {len(mics) - 3} more")
    except Exception as e:
        print(f"🎤 Microphone check failed: {e}")
    
    # Check Ollama
    try:
        import ollama
        models = ollama.list()
        print(f"🧠 Ollama Models: {len(models.get('models', []))} available")
        for model in models.get('models', [])[:3]:  # Show first 3
            print(f"   - {model['name']}")
    except Exception as e:
        print(f"🧠 Ollama check failed: {e}")


def main():
    """Run all examples."""
    print("🤖 Jarvis Voice Assistant - Usage Examples")
    print("=" * 60)
    
    # Setup basic logging
    from jarvis.config import LoggingConfig
    setup_logging(LoggingConfig(level="INFO"))
    
    try:
        # Run examples
        system_info_example()
        configuration_example()
        tool_usage_example()
        basic_agent_example()
        
        # Interactive examples (require user input)
        print("\n" + "=" * 60)
        print("🎤 Interactive Examples (require microphone)")
        print("=" * 60)
        
        response = input("Run speech examples? (y/N): ").lower().strip()
        if response == 'y':
            basic_speech_example()
            
            response = input("Run conversation example? (y/N): ").lower().strip()
            if response == 'y':
                conversation_example()
        
        print("\n🎉 All examples completed!")
        print("\n💡 Next steps:")
        print("   - Run 'python -m jarvis.main' to start the full application")
        print("   - Check out the documentation in docs/")
        print("   - Explore the source code in jarvis/")
        
    except KeyboardInterrupt:
        print("\n\n👋 Examples interrupted by user")
    except Exception as e:
        print(f"\n❌ Example failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
