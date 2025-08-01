#!/usr/bin/env python3
"""
Comprehensive Benchmark for Unified Coding Workflow

This benchmark tests the unified coding workflow with progressively complex requests,
evaluating performance, accuracy, and reliability across different types of coding tasks.
"""

import sys
import asyncio
import logging
import time
import os
from pathlib import Path
from typing import Dict, List, Any
import json

# Add jarvis to path
sys.path.append('jarvis')

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')

from jarvis.core.agent import JarvisAgent
from jarvis.config import LLMConfig


class UnifiedWorkflowBenchmark:
    """Comprehensive benchmark suite for the unified coding workflow."""
    
    def __init__(self):
        self.results = []
        self.agent = None
        
    async def setup(self):
        """Initialize the Jarvis agent for testing."""
        print("🔧 Setting up Jarvis agent for benchmark...")
        config = LLMConfig()
        self.agent = JarvisAgent(config)
        self.agent.initialize(tools=[])
        print("✅ Jarvis agent ready for benchmark")
    
    def cleanup_files(self):
        """Clean up any generated files before each test."""
        files_to_clean = [
            'index.html', 'style.css', 'script.js', 'app.py', 'main.py',
            'hello.html', 'calculator.py', 'todo.html', 'api.py', 'scraper.py',
            'game.html', 'dashboard.html', 'requirements.txt', 'README.md',
            'utils.py', 'models.py', 'test.txt', 'package.json'
        ]
        
        for file in files_to_clean:
            if os.path.exists(file):
                os.remove(file)
    
    async def run_test(self, test_name: str, request: str, expected_files: List[str], 
                      complexity: str, category: str) -> Dict[str, Any]:
        """Run a single benchmark test."""
        print(f"\n🎯 Running Test: {test_name}")
        print(f"   Request: {request}")
        print(f"   Expected files: {', '.join(expected_files)}")
        print(f"   Complexity: {complexity}")
        print(f"   Category: {category}")
        
        # Clean up before test
        self.cleanup_files()
        
        # Record start time
        start_time = time.time()
        
        try:
            # Execute the request
            response = await self.agent.process_input(request)
            execution_time = time.time() - start_time
            
            # Analyze results
            workflow_completed = '🎉 **Unified Coding Workflow Complete!**' in response
            
            # Check file generation
            files_created = []
            files_with_content = []
            
            for file in expected_files:
                if os.path.exists(file):
                    files_created.append(file)
                    
                    # Check if file has real content (not just placeholder)
                    with open(file, 'r') as f:
                        content = f.read()
                        if content and 'Placeholder' not in content and len(content.strip()) > 10:
                            files_with_content.append(file)
            
            # Calculate success metrics
            files_created_ratio = len(files_created) / len(expected_files) if expected_files else 1.0
            content_quality_ratio = len(files_with_content) / len(expected_files) if expected_files else 1.0
            
            # Determine overall success
            success = (
                workflow_completed and 
                files_created_ratio >= 0.8 and  # At least 80% of expected files created
                content_quality_ratio >= 0.5    # At least 50% have real content
            )
            
            result = {
                'test_name': test_name,
                'request': request,
                'category': category,
                'complexity': complexity,
                'success': success,
                'workflow_completed': workflow_completed,
                'execution_time': execution_time,
                'expected_files': expected_files,
                'files_created': files_created,
                'files_with_content': files_with_content,
                'files_created_ratio': files_created_ratio,
                'content_quality_ratio': content_quality_ratio,
                'response_length': len(response),
                'aider_called': 'Aider' in response,
                'open_interpreter_called': 'Open Interpreter' in response,
                'error': None
            }
            
            # Print results
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"   Result: {status}")
            print(f"   Time: {execution_time:.2f}s")
            print(f"   Files: {len(files_created)}/{len(expected_files)} created")
            print(f"   Content: {len(files_with_content)}/{len(expected_files)} with real content")
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            
            result = {
                'test_name': test_name,
                'request': request,
                'category': category,
                'complexity': complexity,
                'success': False,
                'workflow_completed': False,
                'execution_time': execution_time,
                'expected_files': expected_files,
                'files_created': [],
                'files_with_content': [],
                'files_created_ratio': 0.0,
                'content_quality_ratio': 0.0,
                'response_length': 0,
                'aider_called': False,
                'open_interpreter_called': False,
                'error': str(e)
            }
            
            print(f"   Result: ❌ ERROR - {str(e)}")
            print(f"   Time: {execution_time:.2f}s")
            
            return result
    
    async def run_benchmark_suite(self):
        """Run the complete benchmark suite."""
        print("🚀 Starting Unified Coding Workflow Benchmark Suite")
        print("=" * 70)
        
        # Define benchmark tests (simple to complex)
        tests = [
            # Simple HTML/Web Tests
            {
                'name': 'Simple HTML Page',
                'request': 'Create a simple HTML page that says Hello World',
                'expected_files': ['index.html'],
                'complexity': 'simple',
                'category': 'web'
            },
            {
                'name': 'HTML with CSS',
                'request': 'Create an HTML page with CSS styling that displays Hello World in blue',
                'expected_files': ['index.html', 'style.css'],
                'complexity': 'simple',
                'category': 'web'
            },
            {
                'name': 'Complete Web App',
                'request': 'Create a complete web application with HTML, CSS, and JavaScript that shows Hello World',
                'expected_files': ['index.html', 'style.css', 'script.js'],
                'complexity': 'medium',
                'category': 'web'
            },
            
            # Python Script Tests
            {
                'name': 'Simple Python Calculator',
                'request': 'Create a Python script that can add, subtract, multiply and divide two numbers',
                'expected_files': ['calculator.py'],
                'complexity': 'simple',
                'category': 'python'
            },
            {
                'name': 'Python with Utils',
                'request': 'Create a Python application with a main script and utilities module',
                'expected_files': ['main.py', 'utils.py'],
                'complexity': 'medium',
                'category': 'python'
            },
            
            # Interactive Web Applications
            {
                'name': 'Todo List App',
                'request': 'Create a todo list web application where users can add and remove tasks',
                'expected_files': ['index.html', 'style.css', 'script.js'],
                'complexity': 'medium',
                'category': 'web'
            },
            
            # Complex Applications
            {
                'name': 'Web Scraper',
                'request': 'Create a Python web scraper that can extract data from websites',
                'expected_files': ['scraper.py', 'requirements.txt'],
                'complexity': 'complex',
                'category': 'python'
            },
            {
                'name': 'Simple Game',
                'request': 'Create a simple browser-based game using HTML, CSS, and JavaScript',
                'expected_files': ['index.html', 'style.css', 'script.js'],
                'complexity': 'complex',
                'category': 'web'
            }
        ]
        
        # Run all tests
        for test in tests:
            result = await self.run_test(
                test['name'],
                test['request'],
                test['expected_files'],
                test['complexity'],
                test['category']
            )
            self.results.append(result)
            
            # Brief pause between tests
            await asyncio.sleep(1)
        
        # Generate final report
        self.generate_report()
    
    def generate_report(self):
        """Generate a comprehensive benchmark report."""
        print("\n" + "=" * 70)
        print("📊 UNIFIED CODING WORKFLOW BENCHMARK REPORT")
        print("=" * 70)
        
        # Overall statistics
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r['success'])
        failed_tests = total_tests - passed_tests
        
        total_time = sum(r['execution_time'] for r in self.results)
        avg_time = total_time / total_tests if total_tests > 0 else 0
        
        print(f"\n📈 OVERALL RESULTS:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Passed: {passed_tests} ({passed_tests/total_tests*100:.1f}%)")
        print(f"   Failed: {failed_tests} ({failed_tests/total_tests*100:.1f}%)")
        print(f"   Total Time: {total_time:.2f}s")
        print(f"   Average Time: {avg_time:.2f}s per test")
        
        # Category breakdown
        categories = {}
        for result in self.results:
            cat = result['category']
            if cat not in categories:
                categories[cat] = {'total': 0, 'passed': 0}
            categories[cat]['total'] += 1
            if result['success']:
                categories[cat]['passed'] += 1
        
        print(f"\n📊 RESULTS BY CATEGORY:")
        for cat, stats in categories.items():
            success_rate = stats['passed'] / stats['total'] * 100
            print(f"   {cat.upper()}: {stats['passed']}/{stats['total']} ({success_rate:.1f}%)")
        
        # Complexity breakdown
        complexities = {}
        for result in self.results:
            comp = result['complexity']
            if comp not in complexities:
                complexities[comp] = {'total': 0, 'passed': 0}
            complexities[comp]['total'] += 1
            if result['success']:
                complexities[comp]['passed'] += 1
        
        print(f"\n🎯 RESULTS BY COMPLEXITY:")
        for comp, stats in complexities.items():
            success_rate = stats['passed'] / stats['total'] * 100
            print(f"   {comp.upper()}: {stats['passed']}/{stats['total']} ({success_rate:.1f}%)")
        
        # Plugin usage
        aider_usage = sum(1 for r in self.results if r['aider_called'])
        oi_usage = sum(1 for r in self.results if r['open_interpreter_called'])
        
        print(f"\n🔧 PLUGIN USAGE:")
        print(f"   Aider called: {aider_usage}/{total_tests} ({aider_usage/total_tests*100:.1f}%)")
        print(f"   Open Interpreter called: {oi_usage}/{total_tests} ({oi_usage/total_tests*100:.1f}%)")
        
        # Failed tests details
        failed_results = [r for r in self.results if not r['success']]
        if failed_results:
            print(f"\n❌ FAILED TESTS:")
            for result in failed_results:
                print(f"   • {result['test_name']}")
                if result['error']:
                    print(f"     Error: {result['error']}")
                else:
                    print(f"     Files: {len(result['files_created'])}/{len(result['expected_files'])}")
                    print(f"     Content: {len(result['files_with_content'])}/{len(result['expected_files'])}")
        
        # Save detailed results to JSON
        with open('benchmark_results.json', 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n💾 Detailed results saved to: benchmark_results.json")
        
        # Final assessment
        if passed_tests / total_tests >= 0.8:
            print(f"\n🎉 EXCELLENT: Unified coding workflow is performing very well!")
        elif passed_tests / total_tests >= 0.6:
            print(f"\n✅ GOOD: Unified coding workflow is working well with room for improvement")
        elif passed_tests / total_tests >= 0.4:
            print(f"\n⚠️ FAIR: Unified coding workflow needs significant improvements")
        else:
            print(f"\n❌ POOR: Unified coding workflow requires major fixes")
        
        print("=" * 70)


async def main():
    """Run the benchmark suite."""
    benchmark = UnifiedWorkflowBenchmark()
    
    try:
        await benchmark.setup()
        await benchmark.run_benchmark_suite()
    except KeyboardInterrupt:
        print("\n⏹️ Benchmark interrupted by user")
    except Exception as e:
        print(f"\n❌ Benchmark failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
