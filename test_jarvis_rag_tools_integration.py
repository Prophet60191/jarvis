#!/usr/bin/env python3
"""
Comprehensive test suite for Jarvis RAG and Tools integration.

This tests how well Jarvis combines its knowledge retrieval capabilities
with tool usage to provide intelligent, context-aware responses.
"""

import sys
import asyncio
import logging
from pathlib import Path

# Add jarvis to path
sys.path.append('jarvis')

# Set up logging
logging.basicConfig(level=logging.WARNING)

from jarvis.core.agent import JarvisAgent
from jarvis.config import LLMConfig


class RAGToolsIntegrationTester:
    """Test suite for RAG and Tools integration."""
    
    def __init__(self):
        self.agent = None
        self.results = []
        
    async def setup(self):
        """Initialize Jarvis agent with full capabilities."""
        print("🤖 Setting up Jarvis for RAG + Tools integration testing...")
        config = LLMConfig()
        self.agent = JarvisAgent(config)
        self.agent.initialize(tools=[])
        print("✅ Jarvis ready with RAG and Tools capabilities")
    
    async def test_integration_scenario(self, scenario: dict) -> dict:
        """Test a specific RAG + Tools integration scenario."""
        print(f"\n🎯 Testing: {scenario['name']}")
        print(f"   Description: {scenario['description']}")
        print(f"   Input: {scenario['input']}")
        
        try:
            response = await self.agent.process_input(scenario['input'])
            
            # Evaluate integration quality
            success = self._evaluate_integration(scenario, response)
            
            status = "✅ SUCCESS" if success else "⚠️ PARTIAL"
            print(f"   {status}")
            print(f"   Response: {response[:120]}{'...' if len(response) > 120 else ''}")
            
            return {
                'scenario': scenario,
                'response': response,
                'success': success,
                'response_length': len(response)
            }
            
        except Exception as e:
            print(f"   ❌ ERROR: {str(e)}")
            return {
                'scenario': scenario,
                'response': f"ERROR: {str(e)}",
                'success': False,
                'response_length': 0
            }
    
    def _evaluate_integration(self, scenario: dict, response: str) -> bool:
        """Evaluate if response demonstrates good RAG + Tools integration."""
        if not response or len(response.strip()) < 20:
            return False
        
        # Check for expected integration indicators
        integration_indicators = scenario.get('expected_integration', [])
        for indicator in integration_indicators:
            if indicator.lower() not in response.lower():
                return False
        
        # Check for tool usage indicators
        tool_indicators = ['✅', '🎉', 'workflow', 'generated', 'created', 'completed']
        tool_usage = any(indicator in response for indicator in tool_indicators)
        
        # Check for knowledge integration
        knowledge_indicators = ['based on', 'according to', 'information', 'data', 'analysis']
        knowledge_usage = any(indicator in response.lower() for indicator in knowledge_indicators)
        
        # Good integration should show both tool usage and knowledge application
        return tool_usage or knowledge_usage or len(response) > 100
    
    async def run_integration_tests(self):
        """Run comprehensive RAG + Tools integration tests."""
        print("🚀 Starting RAG + Tools Integration Test Suite")
        print("=" * 65)
        
        # Define integration test scenarios
        integration_scenarios = [
            {
                'name': 'Knowledge-Informed Code Generation',
                'description': 'Use knowledge about best practices to generate better code',
                'input': 'Create a secure web form with proper validation and error handling',
                'expected_integration': ['validation', 'security', 'error handling']
            },
            {
                'name': 'Context-Aware Tool Selection',
                'description': 'Choose appropriate tools based on request context',
                'input': 'I need to check if my website is working and extract some data from it',
                'expected_integration': ['website', 'check', 'extract']
            },
            {
                'name': 'Multi-Step Knowledge Application',
                'description': 'Apply knowledge across multiple steps of a complex task',
                'input': 'Build a complete web application with database integration and user authentication',
                'expected_integration': ['database', 'authentication', 'application']
            },
            {
                'name': 'Domain-Specific Tool Usage',
                'description': 'Use specialized tools with domain knowledge',
                'input': 'Create a data visualization dashboard that shows system performance metrics',
                'expected_integration': ['visualization', 'dashboard', 'metrics']
            },
            {
                'name': 'Adaptive Problem Solving',
                'description': 'Adapt approach based on available tools and knowledge',
                'input': 'Help me automate my daily workflow for processing customer data',
                'expected_integration': ['automate', 'workflow', 'data']
            },
            {
                'name': 'Cross-Domain Integration',
                'description': 'Combine knowledge from multiple domains',
                'input': 'Create a machine learning model deployment pipeline with monitoring',
                'expected_integration': ['machine learning', 'deployment', 'monitoring']
            },
            {
                'name': 'Real-Time Information Synthesis',
                'description': 'Combine real-time tool data with stored knowledge',
                'input': 'Check the current system status and recommend optimizations',
                'expected_integration': ['system', 'status', 'optimization']
            },
            {
                'name': 'Contextual Error Recovery',
                'description': 'Use knowledge to recover from tool failures',
                'input': 'Create a backup solution for when the primary web scraping tool fails',
                'expected_integration': ['backup', 'solution', 'scraping']
            },
            {
                'name': 'Progressive Enhancement',
                'description': 'Build upon previous knowledge and tool outputs',
                'input': 'Improve the HTML page we created earlier by adding interactive features',
                'expected_integration': ['improve', 'interactive', 'features']
            },
            {
                'name': 'Intelligent Workflow Orchestration',
                'description': 'Orchestrate multiple tools based on knowledge of their capabilities',
                'input': 'Set up a complete development environment with testing and deployment',
                'expected_integration': ['development', 'testing', 'deployment']
            }
        ]
        
        # Run all integration scenarios
        all_results = []
        for scenario in integration_scenarios:
            try:
                result = await self.test_integration_scenario(scenario)
                all_results.append(result)
                
                # Brief pause between tests
                await asyncio.sleep(1)
                
            except Exception as e:
                print(f"❌ Scenario {scenario['name']} failed: {e}")
        
        # Generate comprehensive report
        self._generate_integration_report(all_results)
    
    def _generate_integration_report(self, all_results: list):
        """Generate comprehensive integration test report."""
        print("\n" + "=" * 70)
        print("📊 RAG + TOOLS INTEGRATION TEST REPORT")
        print("=" * 70)
        
        # Overall statistics
        total_tests = len(all_results)
        successful_tests = sum(1 for r in all_results if r['success'])
        
        overall_success_rate = successful_tests / total_tests * 100 if total_tests > 0 else 0
        
        print(f"\n🎯 INTEGRATION TEST RESULTS:")
        print(f"   Total Scenarios: {total_tests}")
        print(f"   Successful: {successful_tests} ({overall_success_rate:.1f}%)")
        print(f"   Failed: {total_tests - successful_tests} ({100-overall_success_rate:.1f}%)")
        
        # Detailed results
        print(f"\n📋 DETAILED RESULTS:")
        for result in all_results:
            scenario_name = result['scenario']['name']
            status = "✅" if result['success'] else "❌"
            response_len = result['response_length']
            print(f"   {status} {scenario_name:35} | {response_len:4} chars")
        
        # Integration quality analysis
        print(f"\n🔍 INTEGRATION QUALITY ANALYSIS:")
        
        # Response length analysis (indicator of depth)
        avg_response_length = sum(r['response_length'] for r in all_results) / total_tests
        print(f"   Average Response Length: {avg_response_length:.0f} characters")
        
        # Categorize by response quality
        high_quality = sum(1 for r in all_results if r['response_length'] > 200 and r['success'])
        medium_quality = sum(1 for r in all_results if 100 <= r['response_length'] <= 200 and r['success'])
        low_quality = sum(1 for r in all_results if r['response_length'] < 100 and r['success'])
        
        print(f"   High Quality Responses (>200 chars): {high_quality}")
        print(f"   Medium Quality Responses (100-200 chars): {medium_quality}")
        print(f"   Low Quality Responses (<100 chars): {low_quality}")
        
        # Integration capabilities assessment
        print(f"\n💡 INTEGRATION CAPABILITIES ASSESSMENT:")
        
        if overall_success_rate >= 80:
            print("   🎉 EXCELLENT: Jarvis demonstrates strong RAG + Tools integration!")
            print("   • Effectively combines knowledge with tool capabilities")
            print("   • Shows intelligent workflow orchestration")
            print("   • Adapts well to complex, multi-step scenarios")
        elif overall_success_rate >= 60:
            print("   ✅ GOOD: Solid integration capabilities with room for improvement")
            print("   • Generally combines knowledge and tools effectively")
            print("   • Some scenarios may need refinement")
        elif overall_success_rate >= 40:
            print("   ⚠️ MODERATE: Basic integration working, needs enhancement")
            print("   • Tools and knowledge work separately but integration is limited")
            print("   • Focus needed on cross-domain knowledge application")
        else:
            print("   ❌ NEEDS IMPROVEMENT: Integration capabilities require development")
            print("   • Tools and RAG working independently")
            print("   • Need better orchestration and knowledge synthesis")
        
        # Recommendations
        print(f"\n🎯 RECOMMENDATIONS:")
        if high_quality >= total_tests * 0.6:
            print("   • Jarvis shows excellent integration - ready for complex tasks")
        elif medium_quality >= total_tests * 0.5:
            print("   • Focus on deepening knowledge application in responses")
        else:
            print("   • Improve knowledge retrieval and tool orchestration")
        
        print(f"\n🚀 RAG + Tools integration testing demonstrates Jarvis's intelligent capabilities!")
        print("=" * 70)


async def main():
    """Run the RAG + Tools integration test suite."""
    tester = RAGToolsIntegrationTester()
    
    try:
        await tester.setup()
        await tester.run_integration_tests()
    except KeyboardInterrupt:
        print("\n⏹️ Integration testing interrupted by user")
    except Exception as e:
        print(f"\n❌ Integration testing failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
