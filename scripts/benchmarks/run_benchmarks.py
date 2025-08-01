#!/usr/bin/env python3
"""
Quick Benchmark Runner for Jarvis

Simple script to run benchmarks and guide optimization decisions.
"""

import asyncio
import sys
from pathlib import Path

# Add jarvis to path
jarvis_path = Path(__file__).parent / "jarvis"
sys.path.insert(0, str(jarvis_path))

async def main():
    """Main benchmark runner."""
    
    print("🎯 JARVIS PERFORMANCE BENCHMARKING SYSTEM")
    print("=" * 60)
    print("This system will help you systematically optimize Jarvis performance")
    print("through iterative testing and measurement.")
    print()
    
    # Import the benchmark system
    try:
        from benchmark_system import JarvisBenchmark
        print("✅ Benchmark system loaded")
    except ImportError as e:
        print(f"❌ Failed to import benchmark system: {e}")
        return
    
    # Initialize benchmark system
    benchmark = JarvisBenchmark()
    
    # Initialize Jarvis components
    print("\n🔧 Initializing Jarvis components...")
    if not await benchmark.initialize_jarvis():
        print("❌ Failed to initialize Jarvis. Please check your configuration.")
        return
    
    print("✅ Jarvis components ready for benchmarking")
    
    # Show available test suites
    print(f"\n📋 AVAILABLE TEST SUITES:")
    suite_descriptions = {
        "quick": "Fast 5-test suite for rapid iteration (recommended for optimization)",
        "comprehensive": "Complete 50+ test suite covering ALL Jarvis functionality",
        "tool_focused": "18-test suite focused on tool selection and execution",
        "performance": "7-test suite for performance stress testing",
        "rag_focused": "13-test suite focused on RAG and memory system",
        "integration": "11-test suite focused on multi-tool workflows",
        "stress": "17-test suite for stress testing and consistency",
        "progressive": "30-test suite building from simple to complex (RECOMMENDED)"
    }
    
    for suite, description in suite_descriptions.items():
        print(f"  {suite}: {description}")
    
    # Interactive menu
    while True:
        print(f"\n🎯 BENCHMARK OPTIONS:")
        print("1. Run Quick Benchmark (5 tests - rapid iteration)")
        print("2. Run Progressive Benchmark (30 tests - builds complexity)")
        print("3. Run Comprehensive Benchmark (50+ tests - everything)")
        print("4. Run Tool-Focused Benchmark (18 tests - tool selection)")
        print("5. Run RAG-Focused Benchmark (13 tests - memory system)")
        print("6. Run Integration Benchmark (11 tests - workflows)")
        print("7. Run Stress Test (17 tests - performance consistency)")
        print("8. Run Performance Test (7 tests - speed testing)")
        print("9. Exit")
        
        try:
            choice = input("\nSelect option (1-9): ").strip()

            if choice == "9":
                print("👋 Goodbye!")
                break

            suite_map = {
                "1": "quick",
                "2": "progressive",
                "3": "comprehensive",
                "4": "tool_focused",
                "5": "rag_focused",
                "6": "integration",
                "7": "stress",
                "8": "performance"
            }
            
            if choice not in suite_map:
                print("❌ Invalid choice. Please select 1-9.")
                continue
            
            suite_name = suite_map[choice]
            
            print(f"\n🚀 Running {suite_name} benchmark suite...")
            print("This will test the current system performance and provide optimization suggestions.")
            
            # Run the benchmark
            results = await benchmark.run_test_suite(suite_name)
            
            # Generate and show optimization suggestions
            suggestions = benchmark.generate_optimization_suggestions(results)
            
            if suggestions:
                print(f"\n💡 OPTIMIZATION SUGGESTIONS:")
                print("Based on the benchmark results, here are specific improvements you can make:")
                for i, suggestion in enumerate(suggestions, 1):
                    print(f"  {i}. {suggestion}")
                
                print(f"\n🔄 OPTIMIZATION WORKFLOW:")
                print("1. Pick one suggestion to implement")
                print("2. Make the change to your code")
                print("3. Run the benchmark again")
                print("4. Compare results to see improvement")
                print("5. Repeat with next suggestion")
            else:
                print(f"\n🎉 EXCELLENT! No optimization suggestions.")
                print("Your system is performing well within all targets.")
            
            # Ask if they want to run another benchmark
            print(f"\nBenchmark results saved to: benchmark_results/")
            
        except KeyboardInterrupt:
            print(f"\n👋 Benchmark interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error during benchmarking: {e}")
            continue

def run_quick_benchmark():
    """Quick function to run just the quick benchmark."""
    asyncio.run(quick_benchmark())

async def quick_benchmark():
    """Run just the quick benchmark for rapid testing."""
    from benchmark_system import JarvisBenchmark
    
    benchmark = JarvisBenchmark()
    
    if not await benchmark.initialize_jarvis():
        print("❌ Failed to initialize Jarvis")
        return
    
    print("🚀 Running Quick Benchmark...")
    results = await benchmark.run_test_suite("quick")
    
    suggestions = benchmark.generate_optimization_suggestions(results)
    if suggestions:
        print(f"\n💡 OPTIMIZATION SUGGESTIONS:")
        for suggestion in suggestions:
            print(f"  {suggestion}")

if __name__ == "__main__":
    asyncio.run(main())
