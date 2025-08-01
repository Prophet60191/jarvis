#!/usr/bin/env python3
"""
Real-World Orchestration Testing Suite

Tests the enhanced Jarvis orchestration system with actual user prompts
to validate orchestration detection, tool selection, and learning capabilities.
"""

import sys
import asyncio
import time
import json
from pathlib import Path
from typing import List, Dict, Any

# Add the jarvis package to the path
sys.path.insert(0, str(Path(__file__).parent / "jarvis"))

# Test prompts organized by complexity and expected orchestration behavior
TEST_PROMPTS = {
    "simple_direct_knowledge": [
        "What is the capital of France?",
        "Explain how photosynthesis works",
        "Tell me about electric cars",
        "What's the difference between Python and JavaScript?",
        "How does machine learning work?"
    ],
    
    "simple_single_tool": [
        "What time is it?",
        "Remember that I prefer Python for data analysis",
        "Search my memory for information about my last project",
        "What did I tell you about my coding preferences?",
        "Find information about machine learning in my documents"
    ],
    
    "medium_website_extraction": [
        "Extract the product information from https://example-store.com",
        "Scrape the latest news headlines from a tech news website",
        "Get the pricing information from https://competitor-site.com",
        "Extract all the job listings from a careers page",
        "Pull the contact information from a company's about page"
    ],
    
    "medium_code_development": [
        "Create a Python script that monitors my system's CPU usage",
        "Build a web scraper for collecting stock prices",
        "Write a script that organizes my Downloads folder by file type",
        "Create a tool that backs up my important files automatically",
        "Build a simple REST API for managing a todo list"
    ],
    
    "medium_research_analysis": [
        "Analyze the current trends in renewable energy adoption",
        "Research the latest developments in artificial intelligence",
        "Compare the market performance of electric vehicle companies",
        "Study the impact of remote work on productivity",
        "Investigate the growth of cryptocurrency adoption"
    ],
    
    "complex_multi_agent": [
        "Extract data from https://tech-company.com, analyze their product offerings, and create a competitive analysis report",
        "Build a monitoring system for my server, test it thoroughly, and create documentation",
        "Research the latest AI trends, create a summary report, and build a tool to track ongoing developments",
        "Scrape job listings from multiple sites, analyze salary trends, and create a dashboard to visualize the data",
        "Create a comprehensive backup system, test it with my files, and set up automated scheduling"
    ],
    
    "complex_with_learning": [
        "Help me automate my daily workflow - analyze what I do repeatedly and create tools to streamline it",
        "Build a personal assistant system that learns my preferences and helps with task management",
        "Create a smart home automation system that adapts to my usage patterns",
        "Develop a content creation workflow that uses my writing style and preferences",
        "Build an intelligent file organization system that learns from how I categorize things"
    ]
}

class RealWorldOrchestrationTester:
    """Tests Jarvis orchestration with real user prompts and monitors learning."""
    
    def __init__(self):
        self.test_results = []
        self.orchestration_responses = []
        self.learning_data = []
        
    async def run_comprehensive_test(self):
        """Run comprehensive orchestration testing with real prompts."""
        print("🚀 Starting Real-World Orchestration Testing")
        print("=" * 60)
        
        # Initialize Jarvis
        jarvis_agent = await self.initialize_jarvis()
        if not jarvis_agent:
            print("❌ Failed to initialize Jarvis - cannot proceed with testing")
            return
        
        # Test each category
        for category, prompts in TEST_PROMPTS.items():
            print(f"\n🧪 Testing Category: {category.upper()}")
            print("-" * 40)
            
            category_results = []
            for i, prompt in enumerate(prompts, 1):
                print(f"\n📝 Test {i}/{len(prompts)}: {prompt}")
                
                result = await self.test_single_prompt(jarvis_agent, prompt, category)
                category_results.append(result)
                
                # Brief pause between tests
                await asyncio.sleep(1)
            
            # Analyze category results
            self.analyze_category_results(category, category_results)
        
        # Generate comprehensive report
        self.generate_final_report()
    
    async def initialize_jarvis(self):
        """Initialize Jarvis with orchestration capabilities."""
        try:
            from jarvis.core.agent import JarvisAgent
            from jarvis.config import LLMConfig
            from jarvis.core.orchestration.integration_layer import initialize_orchestration
            
            # Create Jarvis agent
            config = LLMConfig()
            agent = JarvisAgent(config)
            
            # Initialize with minimal tools for testing
            agent.initialize(tools=[])
            
            # Initialize orchestration system
            orchestration_available = initialize_orchestration()
            
            print(f"✅ Jarvis initialized successfully")
            print(f"✅ Orchestration available: {orchestration_available}")
            
            return agent
            
        except Exception as e:
            print(f"❌ Failed to initialize Jarvis: {e}")
            return None
    
    async def test_single_prompt(self, agent, prompt: str, category: str) -> Dict[str, Any]:
        """Test a single prompt and analyze the response."""
        start_time = time.time()
        
        try:
            # Send prompt to Jarvis
            response = await agent.process_input(prompt)
            execution_time = time.time() - start_time
            
            # Analyze the response for orchestration intelligence
            analysis = self.analyze_response(prompt, response, category, execution_time)
            
            print(f"⏱️  Response time: {execution_time:.2f}s")
            print(f"🎯 Orchestration detected: {analysis['orchestration_detected']}")
            print(f"🧠 Intelligence level: {analysis['intelligence_level']}")
            print(f"📊 Expected complexity: {analysis['expected_complexity']}")
            
            # Show first 200 chars of response
            response_preview = response[:200] + "..." if len(response) > 200 else response
            print(f"💬 Response preview: {response_preview}")
            
            return analysis
            
        except Exception as e:
            execution_time = time.time() - start_time
            print(f"❌ Error processing prompt: {e}")
            
            return {
                'prompt': prompt,
                'category': category,
                'success': False,
                'error': str(e),
                'execution_time': execution_time,
                'orchestration_detected': False,
                'intelligence_level': 'error'
            }
    
    def analyze_response(self, prompt: str, response: str, category: str, execution_time: float) -> Dict[str, Any]:
        """Analyze Jarvis response for orchestration intelligence."""
        
        # Check for orchestration indicators
        orchestration_indicators = [
            "here's my plan",
            "i'll coordinate",
            "first, i'll use",
            "then, i'll",
            "let me start by",
            "workflow",
            "step by step",
            "aider",
            "lavague",
            "open interpreter",
            "rag",
            "robot framework"
        ]
        
        response_lower = response.lower()
        orchestration_detected = any(indicator in response_lower for indicator in orchestration_indicators)
        
        # Determine intelligence level
        if "here's my plan" in response_lower and any(tool in response_lower for tool in ["aider", "lavague", "interpreter"]):
            intelligence_level = "high_orchestration"
        elif any(indicator in response_lower for indicator in ["i'll use", "coordinate", "workflow"]):
            intelligence_level = "medium_orchestration"
        elif orchestration_detected:
            intelligence_level = "basic_orchestration"
        else:
            intelligence_level = "no_orchestration"
        
        # Expected complexity based on category
        complexity_mapping = {
            "simple_direct_knowledge": "simple",
            "simple_single_tool": "simple",
            "medium_website_extraction": "medium",
            "medium_code_development": "medium", 
            "medium_research_analysis": "medium",
            "complex_multi_agent": "complex",
            "complex_with_learning": "complex"
        }
        
        expected_complexity = complexity_mapping.get(category, "unknown")
        
        # Check if response matches expected complexity
        complexity_match = self.check_complexity_match(intelligence_level, expected_complexity)
        
        return {
            'prompt': prompt,
            'response': response,
            'category': category,
            'success': True,
            'execution_time': execution_time,
            'orchestration_detected': orchestration_detected,
            'intelligence_level': intelligence_level,
            'expected_complexity': expected_complexity,
            'complexity_match': complexity_match,
            'orchestration_indicators_found': [ind for ind in orchestration_indicators if ind in response_lower],
            'response_length': len(response),
            'timestamp': time.time()
        }
    
    def check_complexity_match(self, intelligence_level: str, expected_complexity: str) -> bool:
        """Check if the intelligence level matches expected complexity."""
        if expected_complexity == "simple":
            return intelligence_level in ["no_orchestration", "basic_orchestration"]
        elif expected_complexity == "medium":
            return intelligence_level in ["medium_orchestration", "high_orchestration"]
        elif expected_complexity == "complex":
            return intelligence_level == "high_orchestration"
        return False
    
    def analyze_category_results(self, category: str, results: List[Dict[str, Any]]):
        """Analyze results for a specific category."""
        successful_tests = [r for r in results if r['success']]
        orchestration_detected = [r for r in results if r['orchestration_detected']]
        complexity_matches = [r for r in results if r.get('complexity_match', False)]
        
        print(f"\n📊 Category Analysis: {category}")
        print(f"✅ Successful tests: {len(successful_tests)}/{len(results)}")
        print(f"🧠 Orchestration detected: {len(orchestration_detected)}/{len(results)}")
        print(f"🎯 Complexity matches: {len(complexity_matches)}/{len(results)}")
        
        if successful_tests:
            avg_time = sum(r['execution_time'] for r in successful_tests) / len(successful_tests)
            print(f"⏱️  Average response time: {avg_time:.2f}s")
        
        # Store category results
        self.test_results.append({
            'category': category,
            'total_tests': len(results),
            'successful_tests': len(successful_tests),
            'orchestration_detected': len(orchestration_detected),
            'complexity_matches': len(complexity_matches),
            'results': results
        })
    
    def generate_final_report(self):
        """Generate comprehensive final report."""
        print("\n" + "=" * 60)
        print("📋 COMPREHENSIVE ORCHESTRATION TEST REPORT")
        print("=" * 60)
        
        total_tests = sum(cat['total_tests'] for cat in self.test_results)
        total_successful = sum(cat['successful_tests'] for cat in self.test_results)
        total_orchestration = sum(cat['orchestration_detected'] for cat in self.test_results)
        total_complexity_matches = sum(cat['complexity_matches'] for cat in self.test_results)
        
        print(f"\n🎯 OVERALL RESULTS:")
        print(f"Total tests run: {total_tests}")
        print(f"Successful responses: {total_successful}/{total_tests} ({total_successful/total_tests*100:.1f}%)")
        print(f"Orchestration detected: {total_orchestration}/{total_tests} ({total_orchestration/total_tests*100:.1f}%)")
        print(f"Complexity matches: {total_complexity_matches}/{total_tests} ({total_complexity_matches/total_tests*100:.1f}%)")
        
        print(f"\n📊 CATEGORY BREAKDOWN:")
        for cat in self.test_results:
            success_rate = cat['successful_tests'] / cat['total_tests'] * 100
            orchestration_rate = cat['orchestration_detected'] / cat['total_tests'] * 100
            complexity_rate = cat['complexity_matches'] / cat['total_tests'] * 100
            
            print(f"\n{cat['category'].upper()}:")
            print(f"  Success: {success_rate:.1f}% ({cat['successful_tests']}/{cat['total_tests']})")
            print(f"  Orchestration: {orchestration_rate:.1f}% ({cat['orchestration_detected']}/{cat['total_tests']})")
            print(f"  Complexity Match: {complexity_rate:.1f}% ({cat['complexity_matches']}/{cat['total_tests']})")
        
        # Identify areas for improvement
        print(f"\n🔍 AREAS FOR IMPROVEMENT:")
        for cat in self.test_results:
            if cat['orchestration_detected'] / cat['total_tests'] < 0.8:
                print(f"- {cat['category']}: Low orchestration detection rate")
            if cat['complexity_matches'] / cat['total_tests'] < 0.7:
                print(f"- {cat['category']}: Complexity matching needs improvement")
        
        # Save detailed results
        self.save_detailed_results()
        
        print(f"\n✅ Testing complete! Detailed results saved to orchestration_test_results.json")
    
    def save_detailed_results(self):
        """Save detailed test results to file."""
        results_data = {
            'test_summary': {
                'total_tests': sum(cat['total_tests'] for cat in self.test_results),
                'successful_tests': sum(cat['successful_tests'] for cat in self.test_results),
                'orchestration_detected': sum(cat['orchestration_detected'] for cat in self.test_results),
                'complexity_matches': sum(cat['complexity_matches'] for cat in self.test_results),
                'test_timestamp': time.time()
            },
            'category_results': self.test_results,
            'test_prompts': TEST_PROMPTS
        }
        
        with open('orchestration_test_results.json', 'w') as f:
            json.dump(results_data, f, indent=2, default=str)

async def main():
    """Run the real-world orchestration testing."""
    tester = RealWorldOrchestrationTester()
    await tester.run_comprehensive_test()

if __name__ == "__main__":
    asyncio.run(main())
