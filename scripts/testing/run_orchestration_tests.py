#!/usr/bin/env python3
"""
Orchestration Testing Runner

Easy-to-use script for testing Jarvis orchestration capabilities with real prompts.
"""

import sys
import asyncio
import argparse
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description="Test Jarvis Enhanced Orchestration")
    parser.add_argument(
        "test_type", 
        choices=["comprehensive", "learning", "single"],
        help="Type of test to run"
    )
    parser.add_argument(
        "--prompt", 
        type=str, 
        help="Single prompt to test (required for 'single' test type)"
    )
    parser.add_argument(
        "--verbose", 
        action="store_true", 
        help="Enable verbose output"
    )
    
    args = parser.parse_args()
    
    print("🚀 Jarvis Enhanced Orchestration Testing")
    print("=" * 50)
    
    if args.test_type == "comprehensive":
        print("Running comprehensive orchestration test with multiple prompt categories...")
        from real_world_orchestration_test import main as run_comprehensive
        asyncio.run(run_comprehensive())
        
    elif args.test_type == "learning":
        print("Running orchestration learning session with progressive complexity...")
        from orchestration_learning_session import main as run_learning
        asyncio.run(run_learning())
        
    elif args.test_type == "single":
        if not args.prompt:
            print("❌ Error: --prompt is required for single test type")
            sys.exit(1)
        
        print(f"Testing single prompt: {args.prompt}")
        asyncio.run(test_single_prompt(args.prompt, args.verbose))
    
    print("\n✅ Testing complete!")

async def test_single_prompt(prompt: str, verbose: bool = False):
    """Test a single prompt and show detailed analysis."""
    try:
        # Add the jarvis package to the path
        sys.path.insert(0, str(Path(__file__).parent / "jarvis"))
        
        from jarvis.core.agent import JarvisAgent
        from jarvis.config import LLMConfig
        from jarvis.core.orchestration.integration_layer import initialize_orchestration
        
        # Initialize Jarvis
        print("🔧 Initializing Jarvis...")
        config = LLMConfig()
        agent = JarvisAgent(config)
        agent.initialize(tools=[])
        
        # Initialize orchestration
        orchestration_available = initialize_orchestration()
        print(f"🧠 Orchestration available: {orchestration_available}")
        
        # Process the prompt
        print(f"\n📝 Processing prompt: {prompt}")
        print("-" * 40)
        
        import time
        start_time = time.time()
        response = await agent.process_input(prompt)
        execution_time = time.time() - start_time
        
        # Analyze response
        orchestration_indicators = [
            "here's my plan", "i'll coordinate", "first, i'll use", "then, i'll",
            "let me start by", "workflow", "aider", "lavague", "open interpreter"
        ]
        
        response_lower = response.lower()
        orchestration_detected = any(indicator in response_lower for indicator in orchestration_indicators)
        found_indicators = [ind for ind in orchestration_indicators if ind in response_lower]
        
        # Display results
        print(f"⏱️  Execution time: {execution_time:.2f} seconds")
        print(f"🧠 Orchestration detected: {'✅ Yes' if orchestration_detected else '❌ No'}")
        
        if found_indicators:
            print(f"🎯 Orchestration indicators found: {', '.join(found_indicators)}")
        
        print(f"\n💬 Response:")
        print("-" * 40)
        print(response)
        
        if verbose:
            print(f"\n🔍 Detailed Analysis:")
            print(f"Response length: {len(response)} characters")
            print(f"Response contains 'plan': {'plan' in response_lower}")
            print(f"Response contains tool names: {any(tool in response_lower for tool in ['aider', 'lavague', 'interpreter'])}")
            print(f"Response structure: {'Structured' if any(word in response_lower for word in ['first', 'then', 'next']) else 'Unstructured'}")
        
    except Exception as e:
        print(f"❌ Error testing prompt: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
