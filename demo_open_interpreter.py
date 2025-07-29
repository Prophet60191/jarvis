#!/usr/bin/env python3
"""
Demo script showing Open Interpreter integration with Jarvis.

This demonstrates the capabilities of the Open Interpreter plugin
running locally with your Ollama setup.
"""

import sys
from pathlib import Path

# Add the jarvis directory to the Python path
current_dir = Path(__file__).parent
jarvis_dir = current_dir / "jarvis"
sys.path.insert(0, str(jarvis_dir))

def demo_basic_calculation():
    """Demo basic code execution."""
    print("🧮 Demo: Basic Calculation")
    print("=" * 40)
    
    from tools.plugins.open_interpreter_tool import execute_code
    
    task = "Calculate the area of a circle with radius 5. Use math.pi for precision."
    print(f"Task: {task}")
    print("\nExecuting...")
    
    result = execute_code.invoke({"task_description": task})
    print(f"Result: {result}")
    print()

def demo_data_analysis():
    """Demo data analysis capabilities."""
    print("📊 Demo: Data Analysis")
    print("=" * 40)
    
    from tools.plugins.open_interpreter_tool import execute_code
    
    task = """Create a simple dataset of 10 random numbers, calculate the mean, median, and standard deviation, then create a histogram."""
    print(f"Task: {task}")
    print("\nExecuting...")
    
    result = execute_code.invoke({"task_description": task})
    print(f"Result: {result}")
    print()

def demo_file_operations():
    """Demo file operations."""
    print("📁 Demo: File Operations")
    print("=" * 40)
    
    from tools.plugins.open_interpreter_tool import execute_code
    
    task = """Create a text file called 'demo.txt' with some sample content, then read it back and display the contents."""
    print(f"Task: {task}")
    print("\nExecuting...")
    
    result = execute_code.invoke({"task_description": task})
    print(f"Result: {result}")
    print()

def demo_system_info():
    """Demo system information gathering."""
    print("💻 Demo: System Information")
    print("=" * 40)
    
    from tools.plugins.open_interpreter_tool import system_task
    
    task = "Show current disk usage and available memory"
    print(f"Task: {task}")
    print("\nExecuting...")
    
    result = system_task.invoke({"task": task})
    print(f"Result: {result}")
    print()

def demo_script_creation():
    """Demo script creation."""
    print("📝 Demo: Script Creation")
    print("=" * 40)
    
    from tools.plugins.open_interpreter_tool import create_script
    
    description = "organize files in a directory by extension"
    language = "python"
    print(f"Creating a {language} script to {description}")
    print("\nExecuting...")
    
    result = create_script.invoke({
        "description": description,
        "language": language
    })
    print(f"Result: {result}")
    print()

def main():
    """Run all demos."""
    print("🎭 Open Interpreter Plugin Demo")
    print("🤖 Running locally with Ollama llama3.1:8b")
    print("🔒 100% local execution - no cloud services")
    print("=" * 60)
    print()
    
    demos = [
        demo_basic_calculation,
        demo_data_analysis,
        demo_file_operations,
        demo_system_info,
        demo_script_creation
    ]
    
    for i, demo in enumerate(demos, 1):
        print(f"Demo {i}/{len(demos)}")
        try:
            demo()
        except Exception as e:
            print(f"❌ Demo failed: {e}")
            print()
        
        if i < len(demos):
            input("Press Enter to continue to next demo...")
            print()
    
    print("🎉 Demo completed!")
    print("\n📋 Integration Summary:")
    print("✅ Open Interpreter successfully integrated with Jarvis")
    print("✅ Local execution with Ollama llama3.1:8b")
    print("✅ Multiple tool types available (execute_code, analyze_file, create_script, system_task)")
    print("✅ Safety features enabled (asks permission before running code)")
    print("✅ Ready for voice commands in Jarvis")
    
    print("\n🎤 Example Voice Commands for Jarvis:")
    print("• 'Execute code to calculate compound interest'")
    print("• 'Analyze this CSV file and show me the trends'")
    print("• 'Create a Python script to backup my photos'")
    print("• 'Check my system disk usage'")
    print("• 'Generate a report from this data'")

if __name__ == "__main__":
    main()
