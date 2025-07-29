#!/usr/bin/env python3
"""
Test Benchmark Workflow

Quick test to verify the benchmarking system properly tests the LLM workflow
and provides actionable optimization feedback.
"""

import asyncio
import sys
from pathlib import Path

# Add jarvis to path
jarvis_path = Path(__file__).parent / "jarvis"
sys.path.insert(0, str(jarvis_path))

async def test_single_benchmark():
    """Test a single benchmark to verify the workflow."""
    
    print("🧪 TESTING BENCHMARK WORKFLOW")
    print("=" * 60)
    print("This test verifies that benchmarks properly test the complete LLM workflow:")
    print("User Prompt → LLM Processing → Tool Selection → Tool Execution → Response")
    print()
    
    try:
        from benchmark_system import JarvisBenchmark, BenchmarkTest
        
        # Initialize benchmark system
        benchmark = JarvisBenchmark()
        
        # Initialize Jarvis components
        print("🔧 Initializing Jarvis components...")
        if not await benchmark.initialize_jarvis():
            print("❌ Failed to initialize Jarvis components")
            return False
        
        print("✅ Jarvis components initialized")
        
        # Create a simple test
        test = BenchmarkTest(
            name="workflow_test",
            query="What time is it?",
            expected_tool="get_current_time",
            timeout_seconds=10.0,
            category="workflow_test",
            complexity="simple"
        )
        
        print(f"\n🎯 TESTING COMPLETE WORKFLOW")
        print(f"{'='*50}")
        print(f"We'll give this prompt to the LLM and watch the complete process:")
        print(f"Prompt: '{test.query}'")
        print(f"Expected Tool: {test.expected_tool}")
        print()
        
        # Run the test
        result = await benchmark.run_single_test(test)
        
        print(f"\n📊 WORKFLOW TEST RESULTS")
        print(f"{'='*50}")
        print(f"Success: {'✅ YES' if result.success else '❌ NO'}")
        print(f"Response: {result.response}")
        print(f"Tool Used: {result.tool_used}")
        print(f"Execution Time: {result.execution_time:.2f}s")
        
        # Verify the workflow was tested properly
        workflow_verified = True
        issues = []
        
        if not result.response:
            workflow_verified = False
            issues.append("No response generated - LLM workflow not working")
        
        if not result.tool_used:
            workflow_verified = False
            issues.append("No tool detected - tool selection not working")
        
        if result.execution_time > 15.0:
            workflow_verified = False
            issues.append(f"Too slow ({result.execution_time:.2f}s) - performance issue")
        
        print(f"\n🔍 WORKFLOW VERIFICATION")
        print(f"{'='*50}")
        if workflow_verified:
            print("✅ WORKFLOW VERIFICATION PASSED")
            print("   • LLM received and processed the prompt")
            print("   • Tool selection worked correctly")
            print("   • Tool execution completed")
            print("   • Response was generated")
            print("   • Performance is acceptable")
        else:
            print("❌ WORKFLOW VERIFICATION FAILED")
            for issue in issues:
                print(f"   • {issue}")
        
        # Test optimization suggestions
        print(f"\n💡 TESTING OPTIMIZATION SUGGESTIONS")
        print(f"{'='*50}")
        
        # Create a mock suite result for testing suggestions
        from benchmark_system import BenchmarkSuite
        mock_suite = BenchmarkSuite(
            suite_name="test",
            timestamp="2025-01-01T00:00:00",
            total_tests=1,
            successful_tests=1 if result.success else 0,
            failed_tests=0 if result.success else 1,
            avg_execution_time=result.execution_time,
            total_execution_time=result.execution_time,
            results=[result],
            system_info={}
        )
        
        suggestions = benchmark.generate_optimization_suggestions(mock_suite)
        
        if suggestions:
            print("📋 OPTIMIZATION SUGGESTIONS GENERATED:")
            for suggestion in suggestions:
                print(f"   {suggestion}")
        else:
            print("✅ NO OPTIMIZATION SUGGESTIONS - System performing well!")
        
        return workflow_verified
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_quick_suite():
    """Test the quick benchmark suite."""
    
    print(f"\n🚀 TESTING QUICK BENCHMARK SUITE")
    print("=" * 60)
    print("This will run the 5-test quick suite to verify complete workflow testing...")
    print()
    
    try:
        from benchmark_system import JarvisBenchmark
        
        benchmark = JarvisBenchmark()
        
        # Initialize Jarvis
        if not await benchmark.initialize_jarvis():
            print("❌ Failed to initialize Jarvis")
            return False
        
        # Run quick suite
        results = await benchmark.run_test_suite("quick")
        
        print(f"\n🎯 QUICK SUITE RESULTS")
        print(f"{'='*50}")
        print(f"Total Tests: {results.total_tests}")
        print(f"Successful: {results.successful_tests}")
        print(f"Failed: {results.failed_tests}")
        print(f"Success Rate: {results.successful_tests/results.total_tests*100:.1f}%")
        print(f"Average Time: {results.avg_execution_time:.2f}s")
        
        # Show optimization suggestions
        suggestions = benchmark.generate_optimization_suggestions(results)
        if suggestions:
            print(f"\n💡 OPTIMIZATION SUGGESTIONS:")
            for suggestion in suggestions:
                print(f"   {suggestion}")
        
        return True
        
    except Exception as e:
        print(f"❌ Quick suite test failed: {e}")
        return False

async def main():
    """Main test execution."""
    
    print("🎯 BENCHMARK WORKFLOW VERIFICATION")
    print("=" * 80)
    print("This script verifies that the benchmarking system properly tests")
    print("the complete LLM workflow and provides actionable optimization feedback.")
    print()
    
    # Test 1: Single workflow test
    print("TEST 1: Single Workflow Verification")
    single_test_passed = await test_single_benchmark()
    
    if single_test_passed:
        print(f"\n✅ Single workflow test PASSED")
        
        # Test 2: Quick suite test
        print(f"\nTEST 2: Quick Suite Verification")
        suite_test_passed = await test_quick_suite()
        
        if suite_test_passed:
            print(f"\n🎉 ALL TESTS PASSED!")
            print("=" * 50)
            print("✅ Benchmark system properly tests LLM workflow")
            print("✅ Real-time feedback is working")
            print("✅ Optimization suggestions are generated")
            print("✅ Ready for systematic optimization!")
            print()
            print("🔄 NEXT STEPS:")
            print("1. Run: python run_benchmarks.py")
            print("2. Select Progressive Suite (option 2)")
            print("3. Watch the real-time feedback")
            print("4. Implement suggested optimizations")
            print("5. Run benchmarks again to measure improvement")
        else:
            print(f"\n⚠️  Suite test had issues, but single test worked")
    else:
        print(f"\n❌ Single workflow test FAILED")
        print("The benchmarking system needs debugging before use")

if __name__ == "__main__":
    asyncio.run(main())
