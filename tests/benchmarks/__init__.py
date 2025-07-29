"""
Benchmark Testing Framework for Enhanced Jarvis Features

This package provides comprehensive performance benchmarking for:
- Enhanced Plugin Registry performance
- Context Management system performance  
- Smart Tool Orchestration performance
- Source Code Consciousness performance

Benchmark Categories:
- Latency benchmarks: Response time measurements
- Throughput benchmarks: Operations per second
- Memory benchmarks: Memory usage patterns
- Scalability benchmarks: Performance under load
- Regression benchmarks: Performance comparison over time
"""

import pytest
import time
import psutil
import statistics
from typing import Dict, List, Any, Callable
from dataclasses import dataclass
from pathlib import Path
import json
import logging

logger = logging.getLogger(__name__)

@dataclass
class BenchmarkResult:
    """Container for benchmark results."""
    name: str
    mean_time: float
    median_time: float
    std_dev: float
    min_time: float
    max_time: float
    iterations: int
    memory_usage_mb: float
    cpu_usage_percent: float
    passed_threshold: bool
    threshold_ms: float

@dataclass
class BenchmarkThresholds:
    """Performance thresholds for different operations."""
    registry_query_ms: float = 50.0
    context_retrieval_ms: float = 20.0
    orchestration_decision_ms: float = 150.0
    code_query_ms: float = 500.0
    plugin_loading_ms: float = 100.0
    memory_limit_mb: float = 1000.0
    cpu_limit_percent: float = 80.0

class BenchmarkRunner:
    """Advanced benchmark runner with resource monitoring."""
    
    def __init__(self, thresholds: BenchmarkThresholds = None):
        self.thresholds = thresholds or BenchmarkThresholds()
        self.results: List[BenchmarkResult] = []
        self.baseline_results: Dict[str, BenchmarkResult] = {}
        
    def run_benchmark(self, 
                     name: str, 
                     func: Callable, 
                     iterations: int = 100,
                     warmup_iterations: int = 10,
                     threshold_ms: float = None) -> BenchmarkResult:
        """
        Run a comprehensive benchmark with resource monitoring.
        
        Args:
            name: Benchmark name
            func: Function to benchmark
            iterations: Number of iterations to run
            warmup_iterations: Number of warmup iterations
            threshold_ms: Performance threshold in milliseconds
            
        Returns:
            BenchmarkResult with detailed performance metrics
        """
        # Determine threshold
        if threshold_ms is None:
            threshold_ms = self._get_default_threshold(name)
        
        # Warmup
        logger.info(f"Running warmup for {name} ({warmup_iterations} iterations)")
        for _ in range(warmup_iterations):
            func()
        
        # Collect baseline resource usage
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Run benchmark
        logger.info(f"Running benchmark {name} ({iterations} iterations)")
        times = []
        cpu_samples = []
        
        for i in range(iterations):
            # Monitor CPU before execution
            cpu_before = process.cpu_percent()
            
            # Execute and time
            start_time = time.perf_counter()
            func()
            end_time = time.perf_counter()
            
            execution_time = (end_time - start_time) * 1000  # Convert to ms
            times.append(execution_time)
            
            # Monitor CPU after execution
            cpu_after = process.cpu_percent()
            cpu_samples.append(max(cpu_before, cpu_after))
            
            # Progress logging
            if (i + 1) % (iterations // 10) == 0:
                logger.debug(f"Completed {i + 1}/{iterations} iterations")
        
        # Collect final resource usage
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_usage = final_memory - initial_memory
        avg_cpu_usage = statistics.mean(cpu_samples) if cpu_samples else 0.0
        
        # Calculate statistics
        mean_time = statistics.mean(times)
        median_time = statistics.median(times)
        std_dev = statistics.stdev(times) if len(times) > 1 else 0.0
        min_time = min(times)
        max_time = max(times)
        
        # Check if threshold was met
        passed_threshold = mean_time <= threshold_ms
        
        result = BenchmarkResult(
            name=name,
            mean_time=mean_time,
            median_time=median_time,
            std_dev=std_dev,
            min_time=min_time,
            max_time=max_time,
            iterations=iterations,
            memory_usage_mb=memory_usage,
            cpu_usage_percent=avg_cpu_usage,
            passed_threshold=passed_threshold,
            threshold_ms=threshold_ms
        )
        
        self.results.append(result)
        
        # Log results
        logger.info(f"Benchmark {name} completed:")
        logger.info(f"  Mean: {mean_time:.2f}ms (threshold: {threshold_ms}ms)")
        logger.info(f"  Median: {median_time:.2f}ms")
        logger.info(f"  Std Dev: {std_dev:.2f}ms")
        logger.info(f"  Range: {min_time:.2f}ms - {max_time:.2f}ms")
        logger.info(f"  Memory: {memory_usage:.2f}MB")
        logger.info(f"  CPU: {avg_cpu_usage:.1f}%")
        logger.info(f"  Passed: {'✅' if passed_threshold else '❌'}")
        
        return result
    
    def _get_default_threshold(self, benchmark_name: str) -> float:
        """Get default threshold based on benchmark name."""
        name_lower = benchmark_name.lower()
        
        if 'registry' in name_lower or 'plugin' in name_lower:
            return self.thresholds.registry_query_ms
        elif 'context' in name_lower:
            return self.thresholds.context_retrieval_ms
        elif 'orchestration' in name_lower or 'orchestrator' in name_lower:
            return self.thresholds.orchestration_decision_ms
        elif 'code' in name_lower or 'consciousness' in name_lower:
            return self.thresholds.code_query_ms
        else:
            return 100.0  # Default threshold
    
    def run_load_test(self, 
                     name: str, 
                     func: Callable, 
                     concurrent_users: int = 10,
                     duration_seconds: int = 30) -> Dict[str, Any]:
        """
        Run a load test with multiple concurrent operations.
        
        Args:
            name: Load test name
            func: Function to test under load
            concurrent_users: Number of concurrent operations
            duration_seconds: Test duration in seconds
            
        Returns:
            Load test results
        """
        import threading
        import queue
        
        logger.info(f"Running load test {name} ({concurrent_users} concurrent, {duration_seconds}s)")
        
        results_queue = queue.Queue()
        start_time = time.time()
        end_time = start_time + duration_seconds
        
        def worker():
            """Worker function for load testing."""
            while time.time() < end_time:
                try:
                    operation_start = time.perf_counter()
                    func()
                    operation_end = time.perf_counter()
                    
                    execution_time = (operation_end - operation_start) * 1000
                    results_queue.put({
                        'success': True,
                        'execution_time': execution_time,
                        'timestamp': time.time()
                    })
                except Exception as e:
                    results_queue.put({
                        'success': False,
                        'error': str(e),
                        'timestamp': time.time()
                    })
        
        # Start worker threads
        threads = []
        for _ in range(concurrent_users):
            thread = threading.Thread(target=worker)
            thread.start()
            threads.append(thread)
        
        # Monitor resources during load test
        process = psutil.Process()
        resource_samples = []
        
        while time.time() < end_time:
            resource_samples.append({
                'timestamp': time.time(),
                'memory_mb': process.memory_info().rss / 1024 / 1024,
                'cpu_percent': process.cpu_percent()
            })
            time.sleep(1)
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Collect results
        operation_results = []
        while not results_queue.empty():
            operation_results.append(results_queue.get())
        
        # Calculate statistics
        successful_operations = [r for r in operation_results if r['success']]
        failed_operations = [r for r in operation_results if not r['success']]
        
        if successful_operations:
            execution_times = [r['execution_time'] for r in successful_operations]
            mean_response_time = statistics.mean(execution_times)
            median_response_time = statistics.median(execution_times)
            p95_response_time = sorted(execution_times)[int(len(execution_times) * 0.95)]
        else:
            mean_response_time = median_response_time = p95_response_time = 0
        
        total_operations = len(operation_results)
        success_rate = len(successful_operations) / total_operations if total_operations > 0 else 0
        throughput = total_operations / duration_seconds
        
        # Resource usage statistics
        if resource_samples:
            max_memory = max(s['memory_mb'] for s in resource_samples)
            avg_cpu = statistics.mean(s['cpu_percent'] for s in resource_samples)
        else:
            max_memory = avg_cpu = 0
        
        load_test_result = {
            'name': name,
            'concurrent_users': concurrent_users,
            'duration_seconds': duration_seconds,
            'total_operations': total_operations,
            'successful_operations': len(successful_operations),
            'failed_operations': len(failed_operations),
            'success_rate': success_rate,
            'throughput_ops_per_sec': throughput,
            'mean_response_time_ms': mean_response_time,
            'median_response_time_ms': median_response_time,
            'p95_response_time_ms': p95_response_time,
            'max_memory_mb': max_memory,
            'avg_cpu_percent': avg_cpu
        }
        
        logger.info(f"Load test {name} completed:")
        logger.info(f"  Operations: {total_operations} ({len(successful_operations)} successful)")
        logger.info(f"  Success rate: {success_rate:.1%}")
        logger.info(f"  Throughput: {throughput:.1f} ops/sec")
        logger.info(f"  Response time: {mean_response_time:.1f}ms mean, {p95_response_time:.1f}ms P95")
        logger.info(f"  Resources: {max_memory:.1f}MB max memory, {avg_cpu:.1f}% avg CPU")
        
        return load_test_result
    
    def save_results(self, filepath: Path) -> None:
        """Save benchmark results to file."""
        results_data = {
            'timestamp': time.time(),
            'thresholds': {
                'registry_query_ms': self.thresholds.registry_query_ms,
                'context_retrieval_ms': self.thresholds.context_retrieval_ms,
                'orchestration_decision_ms': self.thresholds.orchestration_decision_ms,
                'code_query_ms': self.thresholds.code_query_ms
            },
            'results': [
                {
                    'name': r.name,
                    'mean_time': r.mean_time,
                    'median_time': r.median_time,
                    'std_dev': r.std_dev,
                    'min_time': r.min_time,
                    'max_time': r.max_time,
                    'iterations': r.iterations,
                    'memory_usage_mb': r.memory_usage_mb,
                    'cpu_usage_percent': r.cpu_usage_percent,
                    'passed_threshold': r.passed_threshold,
                    'threshold_ms': r.threshold_ms
                }
                for r in self.results
            ]
        }
        
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump(results_data, f, indent=2)
        
        logger.info(f"Benchmark results saved to {filepath}")
    
    def load_baseline(self, filepath: Path) -> None:
        """Load baseline results for comparison."""
        if not filepath.exists():
            logger.warning(f"Baseline file not found: {filepath}")
            return
        
        with open(filepath, 'r') as f:
            baseline_data = json.load(f)
        
        for result_data in baseline_data.get('results', []):
            result = BenchmarkResult(
                name=result_data['name'],
                mean_time=result_data['mean_time'],
                median_time=result_data['median_time'],
                std_dev=result_data['std_dev'],
                min_time=result_data['min_time'],
                max_time=result_data['max_time'],
                iterations=result_data['iterations'],
                memory_usage_mb=result_data['memory_usage_mb'],
                cpu_usage_percent=result_data['cpu_usage_percent'],
                passed_threshold=result_data['passed_threshold'],
                threshold_ms=result_data['threshold_ms']
            )
            self.baseline_results[result.name] = result
        
        logger.info(f"Loaded {len(self.baseline_results)} baseline results")
    
    def compare_with_baseline(self) -> Dict[str, Dict[str, Any]]:
        """Compare current results with baseline."""
        comparisons = {}
        
        for result in self.results:
            if result.name in self.baseline_results:
                baseline = self.baseline_results[result.name]
                
                time_change_percent = ((result.mean_time - baseline.mean_time) / baseline.mean_time) * 100
                memory_change_percent = ((result.memory_usage_mb - baseline.memory_usage_mb) / 
                                       max(baseline.memory_usage_mb, 0.1)) * 100
                
                comparisons[result.name] = {
                    'current_mean_time': result.mean_time,
                    'baseline_mean_time': baseline.mean_time,
                    'time_change_percent': time_change_percent,
                    'current_memory_mb': result.memory_usage_mb,
                    'baseline_memory_mb': baseline.memory_usage_mb,
                    'memory_change_percent': memory_change_percent,
                    'regression_detected': time_change_percent > 15.0,  # 15% threshold
                    'improvement_detected': time_change_percent < -10.0  # 10% improvement
                }
        
        return comparisons
    
    def generate_report(self) -> str:
        """Generate a comprehensive benchmark report."""
        report_lines = [
            "# Benchmark Report",
            f"Generated at: {time.strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## Summary",
            f"Total benchmarks: {len(self.results)}",
            f"Passed thresholds: {sum(1 for r in self.results if r.passed_threshold)}",
            f"Failed thresholds: {sum(1 for r in self.results if not r.passed_threshold)}",
            ""
        ]
        
        # Individual results
        report_lines.append("## Individual Results")
        for result in self.results:
            status = "✅ PASS" if result.passed_threshold else "❌ FAIL"
            report_lines.extend([
                f"### {result.name} - {status}",
                f"- Mean time: {result.mean_time:.2f}ms (threshold: {result.threshold_ms}ms)",
                f"- Median time: {result.median_time:.2f}ms",
                f"- Standard deviation: {result.std_dev:.2f}ms",
                f"- Range: {result.min_time:.2f}ms - {result.max_time:.2f}ms",
                f"- Memory usage: {result.memory_usage_mb:.2f}MB",
                f"- CPU usage: {result.cpu_usage_percent:.1f}%",
                f"- Iterations: {result.iterations}",
                ""
            ])
        
        # Baseline comparison if available
        if self.baseline_results:
            comparisons = self.compare_with_baseline()
            if comparisons:
                report_lines.append("## Baseline Comparison")
                for name, comparison in comparisons.items():
                    change_indicator = "📈" if comparison['time_change_percent'] > 0 else "📉"
                    report_lines.extend([
                        f"### {name}",
                        f"- Time change: {change_indicator} {comparison['time_change_percent']:+.1f}%",
                        f"- Memory change: {comparison['memory_change_percent']:+.1f}%",
                        f"- Regression: {'Yes' if comparison['regression_detected'] else 'No'}",
                        ""
                    ])
        
        return "\n".join(report_lines)

# Global benchmark runner instance
benchmark_runner = BenchmarkRunner()

# Pytest fixtures for benchmarking
@pytest.fixture
def benchmark_runner_fixture():
    """Provide benchmark runner for tests."""
    return benchmark_runner

@pytest.fixture
def performance_thresholds():
    """Provide performance thresholds for tests."""
    return BenchmarkThresholds()

# Export benchmark utilities
__all__ = [
    "BenchmarkResult",
    "BenchmarkThresholds", 
    "BenchmarkRunner",
    "benchmark_runner"
]
