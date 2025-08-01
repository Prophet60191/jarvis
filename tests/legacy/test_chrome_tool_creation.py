#!/usr/bin/env python3
import sys
import json
import asyncio
from pathlib import Path
from typing import Dict, Any

# Add the jarvis package to the path
sys.path.insert(0, str(Path(__file__).parent / "jarvis"))

from jarvis.core.orchestration.enhanced_orchestrator import EnhancedJarvisOrchestrator
from jarvis.core.orchestration.analysis import TaskAnalysis
from jarvis.core.context.context_manager import Context, ContextManager
from jarvis.core.orchestration.orchestrator import SystemOrchestrator, OrchestrationPlan, OrchestrationResult, OrchestrationStrategy

# Test prompts for tool creation
TOOL_CREATION_TESTS = [
    # Test prompts from simple to complex
    {
        "prompt": "Create a tool to list all files in a directory"
    },
    {
        "prompt": "Create a tool to monitor system memory usage and alert if it exceeds a threshold"
    },
    {
        "prompt": "Create a tool to check if a website is up and measure its response time"
    },
    {
        "prompt": "Create a tool that converts JSON files to CSV format"
    }
]

class ChromeToolTest:
    """Test Jarvis's ability to create a Chrome launcher tool."""
    
    def __init__(self):
        self.test_result = None
        context_manager = ContextManager()
        base_orchestrator = SystemOrchestrator(context_manager)
        self.orchestrator = EnhancedJarvisOrchestrator(base_orchestrator)
        
    async def run_tool_creation_test(self):
        """Run the tool creation test."""
        print("🛠️  Testing Tool Creation")
        print("=" * 50)
        print("Testing whether Jarvis can create tools from prompts...\n")

        print("📑 Prompts:")
        for test in TOOL_CREATION_TESTS:
            print(f"• {test['prompt']}")
        print("\n" + "-" * 40 + "\n")
        
        # Run the tests
        self.test_result = await self.test_tool_creation()
        
        # Print analysis
        self.analyze_result()
        

            
    async def test_tool_creation(self):
        """Test the Chrome tool creation scenario."""
        try:
            results = []
            
            for test in TOOL_CREATION_TESTS:
                print(f"\nℹ️ Testing prompt: {test['prompt']}")
                
                # Create context and analysis for each test
                context = Context(session_id="test_session")
                analysis = TaskAnalysis(
                    requires_tool_creation=True,
                    tool_specs={},  # Let Jarvis figure out the specs
                    workflow=[],    # Let Jarvis determine the workflow
                    complexity="medium",
                )
                result = await self.orchestrator._handle_tool_creation(
                    user_request=test["prompt"],
                    context=context,
                    analysis=analysis,
                    explanation=""
                )

                # Store test result
                results.append(result)

            return {
                "test_name": "Multiple Tool Creation Test",
                "prompts": [test["prompt"] for test in TOOL_CREATION_TESTS],
                "results": results
            }
            
        except Exception as e:
            print(f"❌ Test failed: {e}")
            return {
                "test_name": "Multiple Tool Creation Test",
                "prompts": [test["prompt"] for test in TOOL_CREATION_TESTS],
                "error": str(e),
                "success": False
            }
            
    def analyze_result(self):
        """Analyze the test result."""
        print("\n📈 Test Analysis:")
        print("=" * 50)
        
        # For each test result
        for i, result in enumerate(self.test_result["results"]):
            prompt = self.test_result["prompts"][i]
            print(f"\n💬 Test {i+1}: {prompt}")
            
            if not result.success:
                print(f"\n❌ Test failed: {result.errors[0] if result.errors else 'Unknown error'}")
                continue
            
            # Get the response from Jarvis
            response = result.results[0] if result.results else ""
            print(f"\n🤖 Response from Jarvis:")
            print(response)
            
            # Look for tool creation indicators in the response
            indicators = [
                "create",
                "new tool",
                "generate",
                "script",
                "tool",
                "success",
                "ready"
            ]
            
            found_indicators = []
            for indicator in indicators:
                if indicator.lower() in response.lower():
                    found_indicators.append(indicator)
            
            print(f"\n🔍 Analysis:")
            print(f"Found {len(found_indicators)} tool creation indicators:")
            for indicator in found_indicators:
                print(f"  ✓ '{indicator}'")
            
            if len(found_indicators) >= 5:
                print("\n✅ EXCELLENT - Jarvis shows strong tool creation understanding")
            elif len(found_indicators) >= 3:
                print("\n✅ GOOD - Jarvis demonstrates basic tool creation capability")
            else:
                print("\n⚠️ WEAK - Jarvis may need improvement in tool creation")

async def main():
    """Run the Chrome tool creation test."""
    tester = ChromeToolTest()
    await tester.run_tool_creation_test()

if __name__ == "__main__":
    asyncio.run(main())
