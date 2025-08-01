#!/usr/bin/env python3
"""
Performance validation test for optimized Jarvis system.
Tests that performance targets are met after cleanup.
"""

import sys
import time
import asyncio
sys.path.append('jarvis')

from jarvis.core.integration.optimized_integration import get_optimized_integration

async def test_performance_targets():
    """Test that optimized system meets performance targets."""
    
    print("🚀 Testing Optimized Jarvis Performance")
    print("=" * 50)
    
    # Initialize optimized system
    integration = get_optimized_integration()
    
    # Test queries by complexity level
    test_cases = [
        # (query, expected_complexity, target_time_ms)
        ("hi", "instant", 50),
        ("hello", "instant", 50), 
        ("thanks", "instant", 50),
        ("what time is it", "explicit_fact", 300),
        ("what's the current time", "explicit_fact", 300),
        ("tell me about python", "simple_reasoning", 1000),
        ("explain machine learning", "simple_reasoning", 1000),
        ("create a web scraper", "complex_multi_step", 5000),
    ]
    
    results = []
    total_tests = len(test_cases)
    passed_tests = 0
    
    print(f"Running {total_tests} performance tests...\n")
    
    for i, (query, expected_complexity, target_ms) in enumerate(test_cases, 1):
        print(f"Test {i}/{total_tests}: '{query}' (target: {target_ms}ms)")
        
        start_time = time.time()
        try:
            response = await integration.process_command(query)
            processing_time_ms = (time.time() - start_time) * 1000
            
            # Check if target met
            target_met = processing_time_ms <= target_ms
            status = "✅ PASS" if target_met else "❌ FAIL"
            
            print(f"  {status} - {processing_time_ms:.1f}ms (target: {target_ms}ms)")
            print(f"  Response: {response[:60]}...")
            
            if target_met:
                passed_tests += 1
                
            results.append({
                "query": query,
                "expected_complexity": expected_complexity,
                "target_ms": target_ms,
                "actual_ms": processing_time_ms,
                "target_met": target_met,
                "response": response
            })
            
        except Exception as e:
            print(f"  ❌ ERROR - {str(e)}")
            results.append({
                "query": query,
                "expected_complexity": expected_complexity,
                "target_ms": target_ms,
                "actual_ms": float('inf'),
                "target_met": False,
                "error": str(e)
            })
        
        print()
    
    # Summary
    print("=" * 50)
    print("📊 PERFORMANCE TEST RESULTS")
    print("=" * 50)
    
    success_rate = (passed_tests / total_tests) * 100
    print(f"Tests passed: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
    
    # Performance by complexity
    complexity_results = {}
    for result in results:
        complexity = result["expected_complexity"]
        if complexity not in complexity_results:
            complexity_results[complexity] = []
        complexity_results[complexity].append(result)
    
    for complexity, tests in complexity_results.items():
        passed = sum(1 for t in tests if t["target_met"])
        total = len(tests)
        avg_time = sum(t["actual_ms"] for t in tests if t["actual_ms"] != float('inf')) / len([t for t in tests if t["actual_ms"] != float('inf')])
        
        print(f"\n{complexity.upper()}:")
        print(f"  Passed: {passed}/{total}")
        print(f"  Avg time: {avg_time:.1f}ms")
    
    # Overall assessment
    print(f"\n🎯 OVERALL PERFORMANCE:")
    if success_rate >= 75:
        print(f"✅ EXCELLENT - {success_rate:.1f}% success rate")
        print("🚀 Optimized system is performing as expected!")
    elif success_rate >= 50:
        print(f"⚠️  GOOD - {success_rate:.1f}% success rate")
        print("🔧 Some optimization may be needed")
    else:
        print(f"❌ NEEDS WORK - {success_rate:.1f}% success rate")
        print("🛠️  System needs further optimization")
    
    return results

if __name__ == "__main__":
    asyncio.run(test_performance_targets())
