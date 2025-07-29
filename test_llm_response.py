#!/usr/bin/env python3
"""
Test LLM response time to diagnose timeout issues.
"""

import sys
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_llm_basic():
    """Test basic LLM response without tools."""
    
    print("🧠 TESTING LLM BASIC RESPONSE")
    print("=" * 35)
    
    try:
        from langchain_ollama import ChatOllama
        from jarvis.jarvis.config import JarvisConfig
        
        config = JarvisConfig()
        print(f"✅ Using LLM model: {config.llm.model}")
        
        # Create LLM instance
        llm = ChatOllama(
            model=config.llm.model,
            temperature=config.llm.temperature
        )
        
        print("✅ LLM instance created")
        
        # Test simple query
        test_queries = [
            "What time is it?",
            "Hello, can you respond?",
            "What is 2+2?"
        ]
        
        for query in test_queries:
            print(f"\n🔍 Testing: '{query}'")
            start_time = time.time()
            
            try:
                response = llm.invoke(query)
                end_time = time.time()
                duration = end_time - start_time
                
                print(f"✅ Response in {duration:.2f}s: {response.content[:100]}...")
                
                if duration > 10:
                    print("⚠️  Response took longer than 10 seconds")
                    
            except Exception as e:
                print(f"❌ Error: {e}")
                
    except ImportError as e:
        print(f"❌ Import error: {e}")
    except Exception as e:
        print(f"❌ Setup error: {e}")

def test_agent_without_tools():
    """Test agent response without tools to isolate the issue."""
    
    print("\n🤖 TESTING AGENT WITHOUT TOOLS")
    print("=" * 35)
    
    try:
        from langchain_ollama import ChatOllama
        from langchain.agents import create_react_agent, AgentExecutor
        from langchain.prompts import PromptTemplate
        from langchain.memory import ConversationBufferMemory
        from jarvis.jarvis.config import JarvisConfig
        
        config = JarvisConfig()
        
        # Create LLM
        llm = ChatOllama(
            model=config.llm.model,
            temperature=config.llm.temperature
        )
        
        # Test simple direct LLM call
        test_query = "What time is it?"
        print(f"🔍 Testing direct LLM call: '{test_query}'")

        start_time = time.time()
        try:
            response = llm.invoke(test_query)
            end_time = time.time()
            duration = end_time - start_time

            print(f"✅ Direct LLM response in {duration:.2f}s: {response.content}")

            if duration > 5:
                print("⚠️  LLM response took longer than 5 seconds")
            else:
                print("✅ LLM responding quickly - issue may be in agent/tool system")

        except Exception as e:
            print(f"❌ Direct LLM call failed: {e}")

    except Exception as e:
        print(f"❌ Agent test setup error: {e}")

def test_ollama_connection():
    """Test if Ollama is running and responsive."""

    print("\n🔌 TESTING OLLAMA CONNECTION")
    print("=" * 30)

    try:
        import requests

        # Test Ollama API
        print("🔍 Checking Ollama API...")
        response = requests.get("http://localhost:11434/api/tags", timeout=5)

        if response.status_code == 200:
            models = response.json()
            print("✅ Ollama is running")
            print(f"📋 Available models: {len(models.get('models', []))}")

            # Check if our model is available
            model_names = [m['name'] for m in models.get('models', [])]
            target_model = "qwen2.5:7b-instruct"

            if target_model in model_names:
                print(f"✅ Target model '{target_model}' is available")
            else:
                print(f"⚠️  Target model '{target_model}' not found")
                print(f"Available models: {model_names}")
        else:
            print(f"❌ Ollama API returned status {response.status_code}")

    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Ollama - is it running?")
        print("💡 Try: ollama serve")
    except Exception as e:
        print(f"❌ Ollama connection test failed: {e}")

def main():
    """Run all diagnostic tests."""

    print("🔍 JARVIS LLM TIMEOUT DIAGNOSTIC")
    print("=" * 50)
    print("Investigating why 'What time is it?' times out after 30 seconds...")
    print()

    # Test 1: Ollama connection
    test_ollama_connection()

    # Test 2: Basic LLM response
    test_llm_basic()

    # Test 3: Agent without tools
    test_agent_without_tools()

    print("\n🎯 DIAGNOSTIC COMPLETE")
    print("=" * 25)
    print("If LLM responds quickly but agent times out, the issue is in:")
    print("• Tool selection/execution pipeline")
    print("• Agent executor configuration")
    print("• Tool loading or discovery")
    print()
    print("If LLM is slow, the issue is in:")
    print("• Ollama performance or model loading")
    print("• Network connectivity to LLM")
    print("• Model configuration")

if __name__ == "__main__":
    main()
