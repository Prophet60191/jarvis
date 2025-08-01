#!/usr/bin/env python3
"""
Golden Dataset Test Runner

Runs comprehensive quality evaluation tests using the golden dataset
to measure RAG system performance and accuracy.
"""

import sys
import json
import time
import asyncio
from pathlib import Path
from typing import Dict, List, Any, Tuple

# Add jarvis to path
sys.path.append(str(Path(__file__).parent / "jarvis"))


class GoldenDatasetEvaluator:
    """Evaluates RAG system quality using golden dataset."""
    
    def __init__(self, rag_service, golden_dataset_path: str):
        """
        Initialize evaluator.
        
        Args:
            rag_service: RAG service instance
            golden_dataset_path: Path to golden dataset JSON file
        """
        self.rag_service = rag_service
        self.golden_dataset = self.load_golden_dataset(golden_dataset_path)
        self.results = []
        
    def load_golden_dataset(self, dataset_path: str) -> Dict[str, Any]:
        """Load golden dataset from JSON file."""
        with open(dataset_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def evaluate_answer_quality(self, test_case: Dict[str, Any], 
                               actual_answer: str, response_time: float) -> Dict[str, Any]:
        """
        Evaluate the quality of an answer against golden dataset criteria.
        
        Args:
            test_case: Golden dataset test case
            actual_answer: RAG system's actual answer
            response_time: Time taken to generate response
            
        Returns:
            dict: Evaluation results
        """
        criteria = test_case.get('evaluation_criteria', {})
        actual_lower = actual_answer.lower()
        
        evaluation = {
            "test_id": test_case['id'],
            "category": test_case['category'],
            "difficulty": test_case['difficulty'],
            "question": test_case['question'],
            "expected_answer": test_case['expected_answer'],
            "actual_answer": actual_answer,
            "response_time": response_time,
            "scores": {},
            "passed": True,
            "issues": []
        }
        
        # Check must_contain criteria
        must_contain = criteria.get('must_contain', [])
        must_contain_score = 0
        for term in must_contain:
            if term.lower() in actual_lower:
                must_contain_score += 1
            else:
                evaluation["issues"].append(f"Missing required term: '{term}'")
                evaluation["passed"] = False
        
        evaluation["scores"]["must_contain"] = must_contain_score / len(must_contain) if must_contain else 1.0
        
        # Check should_contain criteria
        should_contain = criteria.get('should_contain', [])
        should_contain_score = 0
        for term in should_contain:
            if term.lower() in actual_lower:
                should_contain_score += 1
        
        evaluation["scores"]["should_contain"] = should_contain_score / len(should_contain) if should_contain else 1.0
        
        # Check should_not_contain criteria
        should_not_contain = criteria.get('should_not_contain', [])
        should_not_contain_score = 1.0
        for term in should_not_contain:
            if term.lower() in actual_lower:
                should_not_contain_score = 0
                evaluation["issues"].append(f"Contains forbidden term: '{term}'")
                evaluation["passed"] = False
                break
        
        evaluation["scores"]["should_not_contain"] = should_not_contain_score
        
        # Check response time
        max_response_time = self.golden_dataset.get('evaluation_metrics', {}).get('response_time_threshold', 5.0)
        if response_time > max_response_time:
            evaluation["issues"].append(f"Response too slow: {response_time:.2f}s > {max_response_time}s")
            evaluation["passed"] = False
        
        evaluation["scores"]["response_time"] = min(1.0, max_response_time / response_time) if response_time > 0 else 1.0
        
        # Calculate overall score
        weights = {
            "must_contain": 0.5,
            "should_contain": 0.3,
            "should_not_contain": 0.2
        }
        
        overall_score = sum(
            evaluation["scores"][metric] * weight 
            for metric, weight in weights.items()
        )
        
        evaluation["scores"]["overall"] = overall_score
        
        # Check if meets minimum confidence threshold
        min_confidence = criteria.get('min_confidence', 0.7)
        if overall_score < min_confidence:
            evaluation["issues"].append(f"Overall score {overall_score:.2f} below threshold {min_confidence}")
            evaluation["passed"] = False
        
        return evaluation
    
    async def run_single_test(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run a single test case.
        
        Args:
            test_case: Golden dataset test case
            
        Returns:
            dict: Test results
        """
        print(f"  Running {test_case['id']}: {test_case['question'][:50]}...")
        
        start_time = time.time()
        
        try:
            # Query RAG system
            search_result = await self.rag_service.intelligent_search(
                test_case['question'], 
                max_results=3
            )
            
            end_time = time.time()
            response_time = end_time - start_time
            
            # Extract answer
            synthesis = search_result.get('synthesis', {})
            actual_answer = synthesis.get('synthesized_answer', 'No answer generated')
            
            # Evaluate quality
            evaluation = self.evaluate_answer_quality(test_case, actual_answer, response_time)
            
            # Add additional metadata
            evaluation["retrieved_documents_count"] = len(search_result.get('retrieved_documents', []))
            evaluation["confidence_score"] = synthesis.get('confidence_score', 0.0)
            evaluation["source_citations"] = synthesis.get('source_citations', [])
            
            return evaluation
            
        except Exception as e:
            return {
                "test_id": test_case['id'],
                "category": test_case['category'],
                "question": test_case['question'],
                "error": str(e),
                "passed": False,
                "scores": {"overall": 0.0},
                "response_time": time.time() - start_time
            }
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """
        Run all golden dataset tests.
        
        Returns:
            dict: Complete evaluation results
        """
        test_cases = self.golden_dataset['test_cases']
        print(f"🧪 Running {len(test_cases)} golden dataset tests...")
        
        # Setup test data if needed
        await self.setup_test_data()
        
        # Run tests
        for test_case in test_cases:
            result = await self.run_single_test(test_case)
            self.results.append(result)
        
        # Calculate summary statistics
        summary = self.calculate_summary_statistics()
        
        return {
            "metadata": self.golden_dataset['metadata'],
            "test_results": self.results,
            "summary": summary
        }
    
    async def setup_test_data(self):
        """Setup required test data in RAG system."""
        setup_data = self.golden_dataset.get('test_data_setup', {})
        
        # Add required memories
        required_memories = setup_data.get('required_memories', [])
        for memory in required_memories:
            try:
                self.rag_service.add_conversational_memory(memory)
            except Exception as e:
                print(f"⚠️ Failed to add test memory: {e}")
        
        if required_memories:
            print(f"✅ Added {len(required_memories)} test memories")
    
    def calculate_summary_statistics(self) -> Dict[str, Any]:
        """Calculate summary statistics from test results."""
        if not self.results:
            return {}
        
        # Basic statistics
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r.get('passed', False))
        failed_tests = total_tests - passed_tests
        
        # Score statistics
        overall_scores = [r.get('scores', {}).get('overall', 0.0) for r in self.results]
        avg_score = sum(overall_scores) / len(overall_scores) if overall_scores else 0.0
        
        # Response time statistics
        response_times = [r.get('response_time', 0.0) for r in self.results]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0.0
        
        # Category breakdown
        category_stats = {}
        for result in self.results:
            category = result.get('category', 'unknown')
            if category not in category_stats:
                category_stats[category] = {'total': 0, 'passed': 0, 'scores': []}
            
            category_stats[category]['total'] += 1
            if result.get('passed', False):
                category_stats[category]['passed'] += 1
            category_stats[category]['scores'].append(result.get('scores', {}).get('overall', 0.0))
        
        # Calculate category averages
        for category, stats in category_stats.items():
            stats['pass_rate'] = stats['passed'] / stats['total'] if stats['total'] > 0 else 0.0
            stats['avg_score'] = sum(stats['scores']) / len(stats['scores']) if stats['scores'] else 0.0
        
        # Difficulty breakdown
        difficulty_stats = {}
        for result in self.results:
            difficulty = result.get('difficulty', 'unknown')
            if difficulty not in difficulty_stats:
                difficulty_stats[difficulty] = {'total': 0, 'passed': 0, 'avg_score': 0.0}
            
            difficulty_stats[difficulty]['total'] += 1
            if result.get('passed', False):
                difficulty_stats[difficulty]['passed'] += 1
        
        for difficulty, stats in difficulty_stats.items():
            stats['pass_rate'] = stats['passed'] / stats['total'] if stats['total'] > 0 else 0.0
            difficulty_scores = [r.get('scores', {}).get('overall', 0.0) 
                               for r in self.results if r.get('difficulty') == difficulty]
            stats['avg_score'] = sum(difficulty_scores) / len(difficulty_scores) if difficulty_scores else 0.0
        
        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "pass_rate": passed_tests / total_tests if total_tests > 0 else 0.0,
            "average_score": avg_score,
            "average_response_time": avg_response_time,
            "category_breakdown": category_stats,
            "difficulty_breakdown": difficulty_stats,
            "evaluation_thresholds": self.golden_dataset.get('evaluation_metrics', {})
        }
    
    def generate_report(self, results: Dict[str, Any]) -> str:
        """Generate a human-readable test report."""
        summary = results['summary']
        
        report = f"""
🧪 RAG System Golden Dataset Evaluation Report
{'=' * 60}

📊 Overall Results:
  Total Tests: {summary['total_tests']}
  Passed: {summary['passed_tests']} ({summary['pass_rate']*100:.1f}%)
  Failed: {summary['failed_tests']}
  Average Score: {summary['average_score']:.3f}
  Average Response Time: {summary['average_response_time']:.2f}s

📋 Category Breakdown:
"""
        
        for category, stats in summary['category_breakdown'].items():
            report += f"  {category}: {stats['passed']}/{stats['total']} ({stats['pass_rate']*100:.1f}%) - Avg Score: {stats['avg_score']:.3f}\n"
        
        report += f"\n🎯 Difficulty Breakdown:\n"
        for difficulty, stats in summary['difficulty_breakdown'].items():
            report += f"  {difficulty}: {stats['passed']}/{stats['total']} ({stats['pass_rate']*100:.1f}%) - Avg Score: {stats['avg_score']:.3f}\n"
        
        # Failed tests details
        failed_tests = [r for r in results['test_results'] if not r.get('passed', False)]
        if failed_tests:
            report += f"\n❌ Failed Tests:\n"
            for test in failed_tests[:5]:  # Show first 5 failures
                report += f"  {test['test_id']}: {test.get('question', 'Unknown')[:50]}...\n"
                for issue in test.get('issues', []):
                    report += f"    - {issue}\n"
        
        # Quality assessment
        if summary['pass_rate'] >= 0.9:
            report += f"\n🎉 EXCELLENT: RAG system performing exceptionally well!"
        elif summary['pass_rate'] >= 0.8:
            report += f"\n✅ GOOD: RAG system performing well with minor issues."
        elif summary['pass_rate'] >= 0.7:
            report += f"\n⚠️ FAIR: RAG system needs improvement in some areas."
        else:
            report += f"\n❌ POOR: RAG system requires significant improvements."
        
        return report


async def main():
    """Main test function."""
    print("🚀 Golden Dataset Evaluation Suite")
    print("=" * 50)
    
    try:
        # Initialize RAG service
        from jarvis.config import get_config
        from jarvis.tools.rag_service import RAGService
        
        config = get_config()
        rag_service = RAGService(config)
        
        # Initialize evaluator
        dataset_path = "tests/golden_dataset.json"
        evaluator = GoldenDatasetEvaluator(rag_service, dataset_path)
        
        # Run evaluation
        results = await evaluator.run_all_tests()
        
        # Generate and display report
        report = evaluator.generate_report(results)
        print(report)
        
        # Save detailed results
        output_path = f"test_results_golden_dataset_{int(time.time())}.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 Detailed results saved to: {output_path}")
        
        # Return success if pass rate is acceptable
        return results['summary']['pass_rate'] >= 0.8
        
    except Exception as e:
        print(f"❌ Golden dataset evaluation failed: {e}")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
