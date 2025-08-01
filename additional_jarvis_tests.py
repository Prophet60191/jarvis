#!/usr/bin/env python3
"""
Additional comprehensive test examples for Jarvis to validate various capabilities
and edge cases that weren't covered in the initial prompt configuration tests.
"""

import sys
import asyncio
import logging
from pathlib import Path

# Add jarvis to path
sys.path.append('jarvis')

# Set up logging
logging.basicConfig(level=logging.WARNING)  # Reduce noise

from jarvis.core.agent import JarvisAgent
from jarvis.config import LLMConfig


class AdditionalJarvisTests:
    """Additional comprehensive tests for Jarvis capabilities."""
    
    def __init__(self):
        self.agent = None
        self.results = []
        
    async def setup(self):
        """Initialize Jarvis agent."""
        print("🤖 Setting up Jarvis for additional testing...")
        config = LLMConfig()
        self.agent = JarvisAgent(config)
        self.agent.initialize(tools=[])
        print("✅ Jarvis ready for additional tests")
    
    async def test_category(self, category_name: str, tests: list) -> dict:
        """Test a category of examples."""
        print(f"\n🎯 Testing: {category_name}")
        print("=" * 50)
        
        results = {
            'category': category_name,
            'total_tests': len(tests),
            'successful': 0,
            'failed': 0,
            'test_results': []
        }
        
        for i, test in enumerate(tests, 1):
            print(f"\n📝 Test {i}/{len(tests)}: {test['name']}")
            print(f"   Input: {test['input']}")
            
            try:
                response = await self.agent.process_input(test['input'])
                
                # Evaluate response
                success = self._evaluate_response(test, response)
                
                if success:
                    results['successful'] += 1
                    status = "✅ SUCCESS"
                else:
                    results['failed'] += 1
                    status = "⚠️ PARTIAL"
                
                print(f"   {status}")
                print(f"   Response: {response[:80]}{'...' if len(response) > 80 else ''}")
                
                results['test_results'].append({
                    'test': test,
                    'response': response,
                    'success': success
                })
                
            except Exception as e:
                results['failed'] += 1
                print(f"   ❌ ERROR: {str(e)}")
                
                results['test_results'].append({
                    'test': test,
                    'response': f"ERROR: {str(e)}",
                    'success': False
                })
        
        success_rate = results['successful'] / results['total_tests'] * 100
        print(f"\n📊 {category_name}: {results['successful']}/{results['total_tests']} ({success_rate:.1f}%)")
        
        return results
    
    def _evaluate_response(self, test: dict, response: str) -> bool:
        """Evaluate if response meets test expectations."""
        if not response or len(response.strip()) < 10:
            return False
        
        # Check for expected keywords if specified
        if 'expected_keywords' in test:
            for keyword in test['expected_keywords']:
                if keyword.lower() not in response.lower():
                    return False
        
        # Check for error indicators
        error_indicators = ["error", "failed", "sorry, i couldn't", "i don't understand"]
        if any(indicator in response.lower() for indicator in error_indicators):
            return False
        
        return True
    
    async def run_additional_tests(self):
        """Run additional comprehensive tests."""
        print("🚀 Starting Additional Jarvis Test Suite")
        print("=" * 60)
        
        # Define additional test categories
        test_categories = {
            "Tool Integration Tests": [
                {
                    'name': 'LaVague Status Check',
                    'input': 'Check LaVague web automation status',
                    'expected_keywords': ['lavague', 'status']
                },
                {
                    'name': 'System Memory Check',
                    'input': 'Check system memory usage',
                    'expected_keywords': ['memory']
                },
                {
                    'name': 'List Files Request',
                    'input': 'List all files in the current directory',
                    'expected_keywords': ['files']
                }
            ],
            
            "Creative Coding Requests": [
                {
                    'name': 'Interactive Calculator',
                    'input': 'Create an interactive calculator with buttons',
                    'expected_keywords': ['calculator', 'interactive']
                },
                {
                    'name': 'Color Picker Tool',
                    'input': 'Make a color picker web application',
                    'expected_keywords': ['color', 'picker']
                },
                {
                    'name': 'Simple Game',
                    'input': 'Create a simple guessing game in HTML and JavaScript',
                    'expected_keywords': ['game', 'guessing']
                }
            ],
            
            "Data Processing Requests": [
                {
                    'name': 'JSON to CSV Converter',
                    'input': 'Create a tool that converts JSON files to CSV format',
                    'expected_keywords': ['json', 'csv', 'convert']
                },
                {
                    'name': 'Text File Processor',
                    'input': 'Make a Python script that processes text files and counts words',
                    'expected_keywords': ['text', 'process', 'count']
                },
                {
                    'name': 'Data Visualization',
                    'input': 'Create a simple chart visualization tool',
                    'expected_keywords': ['chart', 'visualization']
                }
            ],
            
            "Web Automation Tasks": [
                {
                    'name': 'Website Information Extraction',
                    'input': 'Navigate to example.com and extract the page title and main content',
                    'expected_keywords': ['navigate', 'extract', 'title']
                },
                {
                    'name': 'Form Filling Automation',
                    'input': 'Create a script that can fill out web forms automatically',
                    'expected_keywords': ['form', 'fill', 'automatic']
                },
                {
                    'name': 'Website Status Checker',
                    'input': 'Make a tool that checks if websites are online and measures response time',
                    'expected_keywords': ['website', 'status', 'response']
                }
            ],
            
            "Complex Multi-Step Tasks": [
                {
                    'name': 'Complete Web Application',
                    'input': 'Create a complete todo list web application with add, delete, and mark complete functionality',
                    'expected_keywords': ['todo', 'application', 'complete']
                },
                {
                    'name': 'API with Documentation',
                    'input': 'Build a simple REST API with documentation and example usage',
                    'expected_keywords': ['api', 'documentation', 'rest']
                },
                {
                    'name': 'Automated Testing Suite',
                    'input': 'Create a testing framework that can automatically test web applications',
                    'expected_keywords': ['testing', 'framework', 'automatic']
                }
            ],
            
            "Natural Language Variations": [
                {
                    'name': 'Casual Request',
                    'input': 'hey can you whip up a quick webpage for me?',
                    'expected_keywords': ['webpage']
                },
                {
                    'name': 'Formal Request',
                    'input': 'I would appreciate your assistance in developing a web-based application.',
                    'expected_keywords': ['application', 'web']
                },
                {
                    'name': 'Technical Jargon',
                    'input': 'Implement a DOM manipulation utility with event handling capabilities',
                    'expected_keywords': ['dom', 'manipulation', 'event']
                }
            ],
            
            "Error Handling and Edge Cases": [
                {
                    'name': 'Ambiguous Request',
                    'input': 'Make something cool',
                    'expected_keywords': ['create', 'build', 'make']
                },
                {
                    'name': 'Impossible Request',
                    'input': 'Create a time machine using HTML',
                    'expected_keywords': ['cannot', 'impossible', 'create']
                },
                {
                    'name': 'Conflicting Requirements',
                    'input': 'Make a simple complex advanced basic application',
                    'expected_keywords': ['application']
                }
            ]
        }
        
        # Run all test categories
        all_results = []
        for category_name, tests in test_categories.items():
            try:
                category_result = await self.test_category(category_name, tests)
                all_results.append(category_result)
                
                # Brief pause between categories
                await asyncio.sleep(0.5)
                
            except Exception as e:
                print(f"❌ Category {category_name} failed: {e}")
        
        # Generate comprehensive report
        self._generate_report(all_results)
    
    def _generate_report(self, all_results: list):
        """Generate comprehensive test report."""
        print("\n" + "=" * 70)
        print("📊 ADDITIONAL JARVIS CAPABILITIES TEST REPORT")
        print("=" * 70)
        
        # Overall statistics
        total_tests = sum(r['total_tests'] for r in all_results)
        total_successful = sum(r['successful'] for r in all_results)
        
        overall_success_rate = total_successful / total_tests * 100 if total_tests > 0 else 0
        
        print(f"\n🎯 OVERALL ADDITIONAL TEST RESULTS:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Successful: {total_successful} ({overall_success_rate:.1f}%)")
        print(f"   Failed: {total_tests - total_successful} ({100-overall_success_rate:.1f}%)")
        
        # Category breakdown
        print(f"\n📋 RESULTS BY CATEGORY:")
        for result in all_results:
            success_rate = result['successful'] / result['total_tests'] * 100
            status = "🎉" if success_rate >= 80 else "✅" if success_rate >= 60 else "⚠️" if success_rate >= 40 else "❌"
            print(f"   {status} {result['category']:25} | {result['successful']:2}/{result['total_tests']:2} ({success_rate:5.1f}%)")
        
        # Key insights
        print(f"\n💡 KEY INSIGHTS:")
        if overall_success_rate >= 80:
            print("   🎉 Excellent! Jarvis demonstrates robust capabilities across diverse scenarios.")
        elif overall_success_rate >= 60:
            print("   ✅ Good performance with strong foundational capabilities.")
        elif overall_success_rate >= 40:
            print("   ⚠️ Moderate performance - some areas need improvement.")
        else:
            print("   ❌ Significant improvements needed in core capabilities.")
        
        print(f"\n🎯 Jarvis shows strong adaptability to various user interaction patterns!")
        print("=" * 70)


async def main():
    """Run the additional test suite."""
    tester = AdditionalJarvisTests()
    
    try:
        await tester.setup()
        await tester.run_additional_tests()
    except KeyboardInterrupt:
        print("\n⏹️ Additional testing interrupted by user")
    except Exception as e:
        print(f"\n❌ Additional testing failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
