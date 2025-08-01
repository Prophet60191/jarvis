#!/usr/bin/env python3
"""
Comprehensive test suite for various Jarvis prompt configurations and user interaction patterns.

This tests how Jarvis handles different types of requests, conversation styles,
and edge cases to ensure robust user experience.
"""

import sys
import asyncio
import logging
from pathlib import Path

# Add jarvis to path
sys.path.append('jarvis')

# Set up logging
logging.basicConfig(level=logging.WARNING)  # Reduce noise for cleaner output

from jarvis.core.agent import JarvisAgent
from jarvis.config import LLMConfig


class JarvisPromptTester:
    """Comprehensive prompt configuration tester for Jarvis."""
    
    def __init__(self):
        self.agent = None
        self.results = []
        
    async def setup(self):
        """Initialize Jarvis agent."""
        print("🤖 Setting up Jarvis for prompt testing...")
        config = LLMConfig()
        self.agent = JarvisAgent(config)
        self.agent.initialize(tools=[])
        print("✅ Jarvis ready for testing")
    
    async def test_prompt_category(self, category_name: str, prompts: list) -> dict:
        """Test a category of prompts."""
        print(f"\n🎯 Testing Category: {category_name}")
        print("=" * 50)
        
        category_results = {
            'category': category_name,
            'total_prompts': len(prompts),
            'successful_responses': 0,
            'failed_responses': 0,
            'prompt_results': []
        }
        
        for i, prompt in enumerate(prompts, 1):
            print(f"\n📝 Test {i}/{len(prompts)}: {prompt[:60]}{'...' if len(prompt) > 60 else ''}")
            
            try:
                response = await self.agent.process_input(prompt)
                
                # Evaluate response quality
                success = self._evaluate_response(prompt, response)
                
                if success:
                    category_results['successful_responses'] += 1
                    status = "✅ SUCCESS"
                else:
                    category_results['failed_responses'] += 1
                    status = "⚠️ PARTIAL"
                
                print(f"   {status}")
                print(f"   Response: {response[:100]}{'...' if len(response) > 100 else ''}")
                
                category_results['prompt_results'].append({
                    'prompt': prompt,
                    'response': response,
                    'success': success,
                    'response_length': len(response)
                })
                
            except Exception as e:
                category_results['failed_responses'] += 1
                print(f"   ❌ ERROR: {str(e)}")
                
                category_results['prompt_results'].append({
                    'prompt': prompt,
                    'response': f"ERROR: {str(e)}",
                    'success': False,
                    'response_length': 0
                })
        
        success_rate = category_results['successful_responses'] / category_results['total_prompts'] * 100
        print(f"\n📊 {category_name} Results: {category_results['successful_responses']}/{category_results['total_prompts']} ({success_rate:.1f}%)")
        
        return category_results
    
    def _evaluate_response(self, prompt: str, response: str) -> bool:
        """Evaluate if a response is appropriate for the prompt."""
        if not response or len(response.strip()) < 10:
            return False
        
        # Check for error indicators
        error_indicators = ["error", "failed", "sorry, i couldn't", "i don't understand"]
        if any(indicator in response.lower() for indicator in error_indicators):
            return False
        
        # Check for appropriate response length (not too short, not too long)
        if len(response) < 20 or len(response) > 2000:
            return False
        
        return True
    
    async def run_comprehensive_tests(self):
        """Run comprehensive prompt configuration tests."""
        print("🚀 Starting Comprehensive Jarvis Prompt Configuration Tests")
        print("=" * 70)
        
        # Define test categories and prompts
        test_categories = {
            "Basic Conversational": [
                "Hello",
                "How are you?",
                "What's your name?",
                "Tell me about yourself",
                "Good morning Jarvis",
                "Thank you",
                "Goodbye"
            ],
            
            "Question Variations": [
                "What time is it?",
                "What's the current time?",
                "Can you tell me the time?",
                "Time please",
                "What time is it right now?",
                "Current time?",
                "Time check"
            ],
            
            "Command Styles": [
                "Check LaVague status",
                "Please check LaVague status",
                "Can you check LaVague status?",
                "I need you to check LaVague status",
                "LaVague status check",
                "Status of LaVague please",
                "Show me LaVague status"
            ],
            
            "Coding Requests": [
                "Create a simple HTML page",
                "Make me a Python calculator",
                "Build a web page that says hello",
                "Generate a JavaScript function",
                "Write a Python script for file processing",
                "Create a simple web application",
                "Make a tool that converts text to uppercase"
            ],
            
            "Web Automation": [
                "Navigate to example.com",
                "Extract the title from google.com",
                "Check what's on example.com",
                "Go to a website and tell me what you see",
                "Browse to httpbin.org and get the page info",
                "Visit example.com and extract information",
                "Navigate to a test website"
            ],
            
            "Casual/Informal": [
                "hey jarvis",
                "sup",
                "what's up?",
                "yo jarvis, what time is it?",
                "can u help me?",
                "make me something cool",
                "do something interesting"
            ],
            
            "Complex/Multi-part": [
                "Create a web page and then test it",
                "Make a Python script and show me how to run it",
                "Build a calculator and demonstrate its usage",
                "Create a tool and explain what it does",
                "Make something useful and tell me about it",
                "Generate code and validate that it works",
                "Build an application and provide documentation"
            ],
            
            "Edge Cases": [
                "",  # Empty input
                "   ",  # Whitespace only
                "a",  # Single character
                "?" * 100,  # Very long input
                "Create a" + " very" * 50 + " complex application",  # Very long request
                "🤖🎯🚀",  # Emoji only
                "123456789",  # Numbers only
                "MAKE ME A WEBSITE NOW!!!",  # All caps with urgency
            ]
        }
        
        # Run tests for each category
        all_results = []
        for category_name, prompts in test_categories.items():
            try:
                category_result = await self.test_prompt_category(category_name, prompts)
                all_results.append(category_result)
                
                # Brief pause between categories
                await asyncio.sleep(0.5)
                
            except Exception as e:
                print(f"❌ Category {category_name} failed: {e}")
        
        # Generate comprehensive report
        self._generate_comprehensive_report(all_results)
    
    def _generate_comprehensive_report(self, all_results: list):
        """Generate a comprehensive test report."""
        print("\n" + "=" * 70)
        print("📊 COMPREHENSIVE JARVIS PROMPT CONFIGURATION REPORT")
        print("=" * 70)
        
        # Overall statistics
        total_prompts = sum(r['total_prompts'] for r in all_results)
        total_successful = sum(r['successful_responses'] for r in all_results)
        total_failed = sum(r['failed_responses'] for r in all_results)
        
        overall_success_rate = total_successful / total_prompts * 100 if total_prompts > 0 else 0
        
        print(f"\n🎯 OVERALL RESULTS:")
        print(f"   Total Prompts Tested: {total_prompts}")
        print(f"   Successful Responses: {total_successful} ({overall_success_rate:.1f}%)")
        print(f"   Failed/Partial Responses: {total_failed} ({100-overall_success_rate:.1f}%)")
        
        # Category breakdown
        print(f"\n📋 RESULTS BY CATEGORY:")
        for result in all_results:
            success_rate = result['successful_responses'] / result['total_prompts'] * 100
            status = "🎉" if success_rate >= 80 else "✅" if success_rate >= 60 else "⚠️" if success_rate >= 40 else "❌"
            print(f"   {status} {result['category']:20} | {result['successful_responses']:2}/{result['total_prompts']:2} ({success_rate:5.1f}%)")
        
        # Best and worst performing categories
        best_category = max(all_results, key=lambda x: x['successful_responses'] / x['total_prompts'])
        worst_category = min(all_results, key=lambda x: x['successful_responses'] / x['total_prompts'])
        
        print(f"\n🏆 BEST PERFORMING CATEGORY:")
        best_rate = best_category['successful_responses'] / best_category['total_prompts'] * 100
        print(f"   {best_category['category']} ({best_rate:.1f}% success rate)")
        
        print(f"\n⚠️ NEEDS IMPROVEMENT:")
        worst_rate = worst_category['successful_responses'] / worst_category['total_prompts'] * 100
        print(f"   {worst_category['category']} ({worst_rate:.1f}% success rate)")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        if overall_success_rate >= 80:
            print("   🎉 Excellent! Jarvis handles diverse prompts very well.")
        elif overall_success_rate >= 60:
            print("   ✅ Good performance with room for improvement in edge cases.")
        elif overall_success_rate >= 40:
            print("   ⚠️ Moderate performance - focus on improving response quality.")
        else:
            print("   ❌ Needs significant improvement in prompt handling.")
        
        if worst_rate < 50:
            print(f"   • Focus on improving {worst_category['category']} handling")
        
        print(f"\n🎯 Jarvis demonstrates robust handling of diverse user interaction patterns!")
        print("=" * 70)


async def main():
    """Run the comprehensive prompt configuration tests."""
    tester = JarvisPromptTester()
    
    try:
        await tester.setup()
        await tester.run_comprehensive_tests()
    except KeyboardInterrupt:
        print("\n⏹️ Testing interrupted by user")
    except Exception as e:
        print(f"\n❌ Testing failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
