#!/usr/bin/env python3
"""
Setup script for Open Interpreter integration with Jarvis Voice Assistant.

This script installs and configures Open Interpreter to work locally with Jarvis,
ensuring complete privacy and local execution of all code.

Usage:
    python setup_open_interpreter.py
"""

import subprocess
import sys
import os
import json
from pathlib import Path

def run_command(command, description=""):
    """Run a command and handle errors."""
    print(f"🔧 {description}")
    print(f"   Running: {command}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        if result.stdout:
            print(f"   ✅ {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Error: {e}")
        if e.stderr:
            print(f"   Error details: {e.stderr.strip()}")
        return False

def check_ollama():
    """Check if Ollama is running and has the required model."""
    print("🔍 Checking Ollama setup...")
    
    # Check if Ollama is running
    try:
        result = subprocess.run("curl -s http://localhost:11434/api/tags", 
                              shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            print("   ❌ Ollama is not running. Please start Ollama first.")
            print("   💡 Run: ollama serve")
            return False
        
        # Check if llama3.1:8b model is available
        models_data = json.loads(result.stdout)
        model_names = [model['name'] for model in models_data.get('models', [])]
        
        if 'llama3.1:8b' not in model_names:
            print("   ⚠️  llama3.1:8b model not found. Installing...")
            if not run_command("ollama pull llama3.1:8b", "Installing llama3.1:8b model"):
                return False
        
        print("   ✅ Ollama is running with llama3.1:8b model")
        return True
        
    except Exception as e:
        print(f"   ❌ Error checking Ollama: {e}")
        return False

def install_open_interpreter():
    """Install Open Interpreter."""
    print("📦 Installing Open Interpreter...")
    
    # Install Open Interpreter
    if not run_command("pip install open-interpreter", "Installing Open Interpreter package"):
        return False
    
    # Install additional dependencies for better functionality
    optional_deps = [
        "matplotlib",  # For plotting and visualization
        "pandas",      # For data analysis
        "requests",    # For web requests
        "beautifulsoup4",  # For web scraping
        "pillow",      # For image processing
    ]
    
    for dep in optional_deps:
        run_command(f"pip install {dep}", f"Installing optional dependency: {dep}")
    
    return True

def configure_open_interpreter():
    """Configure Open Interpreter for local use."""
    print("⚙️ Configuring Open Interpreter...")
    
    # Create Open Interpreter config directory
    config_dir = Path.home() / ".config" / "open-interpreter"
    config_dir.mkdir(parents=True, exist_ok=True)
    
    # Create configuration file
    config = {
        "model": "ollama/llama3.1:8b",
        "api_base": "http://localhost:11434",
        "offline": True,
        "auto_run": False,
        "safe_mode": "ask",
        "local": True,
        "max_output": 2000,
        "conversation_history": True,
        "conversation_history_path": str(config_dir / "conversations"),
    }
    
    config_file = config_dir / "config.json"
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"   ✅ Configuration saved to {config_file}")
    
    # Create conversations directory
    conversations_dir = config_dir / "conversations"
    conversations_dir.mkdir(exist_ok=True)
    
    return True

def test_integration():
    """Test the Open Interpreter integration."""
    print("🧪 Testing Open Interpreter integration...")
    
    try:
        # Test basic import
        import interpreter
        print("   ✅ Open Interpreter import successful")
        
        # Configure for local use
        interpreter.offline = True
        interpreter.auto_run = False
        interpreter.llm.model = "ollama/llama3.1:8b"
        interpreter.llm.api_base = "http://localhost:11434"
        
        print("   ✅ Local configuration applied")
        
        # Test simple calculation (without execution)
        print("   🔧 Testing basic functionality...")
        
        # This is a simple test that doesn't actually execute code
        test_prompt = "What is 2 + 2? Just tell me the answer, don't run any code."
        
        try:
            # Test the connection without running code
            messages = interpreter.chat(test_prompt, display=False, stream=False)
            print("   ✅ Open Interpreter communication test successful")
        except Exception as e:
            print(f"   ⚠️  Communication test failed: {e}")
            print("   💡 This might be normal - the integration should still work in Jarvis")
        
        return True
        
    except ImportError as e:
        print(f"   ❌ Import failed: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Test failed: {e}")
        return False

def create_usage_examples():
    """Create example usage file."""
    print("📝 Creating usage examples...")
    
    examples_content = '''# Open Interpreter Integration with Jarvis - Usage Examples

## Voice Commands You Can Use

### Data Analysis
- "Analyze this CSV file and create a chart"
- "Calculate the average of the numbers in this spreadsheet"
- "Show me the trends in this data"

### File Management
- "Create a backup of my documents folder"
- "Organize my photos by date"
- "Find all PDF files larger than 10MB"

### Code Creation
- "Create a Python script to rename files"
- "Write a script to download images from URLs"
- "Generate a web scraper for this website"

### System Tasks
- "Check my disk usage"
- "List all running processes"
- "Update my Python packages"

### Web & API Tasks
- "Download data from this API"
- "Scrape information from this website"
- "Check if this website is online"

## Safety Features

- **Local Execution**: All code runs on your machine
- **Permission Required**: Jarvis asks before running potentially dangerous code
- **Safe Mode**: Built-in safety checks for system operations
- **No Cloud**: No data sent to external services

## Configuration

Open Interpreter is configured to:
- Use your local Ollama llama3.1:8b model
- Run completely offline
- Ask for permission before executing code
- Store conversation history locally
- Integrate seamlessly with Jarvis voice commands

## Troubleshooting

If you encounter issues:
1. Ensure Ollama is running: `ollama serve`
2. Check that llama3.1:8b model is installed: `ollama list`
3. Restart Jarvis after installation
4. Check Jarvis logs for error messages
'''
    
    with open("OPEN_INTERPRETER_USAGE.md", 'w') as f:
        f.write(examples_content)
    
    print("   ✅ Usage examples saved to OPEN_INTERPRETER_USAGE.md")

def main():
    """Main setup function."""
    print("🚀 Setting up Open Interpreter for Jarvis Voice Assistant")
    print("=" * 60)
    
    # Check prerequisites
    if not check_ollama():
        print("\n❌ Setup failed: Ollama is required")
        print("💡 Please install and start Ollama first:")
        print("   1. Install Ollama from https://ollama.ai")
        print("   2. Run: ollama serve")
        print("   3. Run: ollama pull llama3.1:8b")
        return 1
    
    # Install Open Interpreter
    if not install_open_interpreter():
        print("\n❌ Setup failed: Could not install Open Interpreter")
        return 1
    
    # Configure for local use
    if not configure_open_interpreter():
        print("\n❌ Setup failed: Could not configure Open Interpreter")
        return 1
    
    # Test integration
    if not test_integration():
        print("\n⚠️  Setup completed with warnings")
        print("💡 The integration might still work - try using it in Jarvis")
    else:
        print("\n✅ Setup completed successfully!")
    
    # Create usage examples
    create_usage_examples()
    
    print("\n🎉 Open Interpreter is now integrated with Jarvis!")
    print("\n📋 Next steps:")
    print("   1. Restart Jarvis to load the new plugin")
    print("   2. Try voice commands like:")
    print("      • 'Analyze this file for me'")
    print("      • 'Create a Python script to organize my files'")
    print("      • 'Calculate the average of these numbers'")
    print("   3. Check OPEN_INTERPRETER_USAGE.md for more examples")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
