#!/usr/bin/env python3
import sys
import asyncio
from pathlib import Path

# Add the jarvis package to the path
sys.path.insert(0, str(Path(__file__).parent))

# Test prompt for Chrome tool
TOOL_CREATION_TEST = {
    "prompt": "Make a tool that will open Chrome",
    "missing_tool": "chrome_launcher",
    "expected_behavior": "create_tool",
    "expected_workflow": ["aider", "open_interpreter"],
    "description": "Should create a Chrome launcher tool"
}

async def test_chrome_tool():
    """Test Chrome tool creation."""
    from jarvis.core.agent import JarvisAgent
    from jarvis.config import JarvisConfig
    
    print("🧪 Testing Chrome Tool Creation")
    print("=" * 50)
    print(f"📝 Prompt: {TOOL_CREATION_TEST['prompt']}")
    print("-" * 40)
    
    # Initialize Jarvis
    config = JarvisConfig()
    agent = JarvisAgent(config)
    
    # Send the prompt
    response = await agent.process_request(TOOL_CREATION_TEST["prompt"])
    print("\n🤖 Jarvis Response:")
    print(response)

async def main():
    """Run the Chrome tool creation test."""
    await test_chrome_tool()

if __name__ == "__main__":
    asyncio.run(main())
