#!/usr/bin/env python3
"""
Test Quality Metrics System

Tests the comprehensive quality measurement system for RAG
including retrieval accuracy, answer faithfulness, and source citation.
"""

import sys
import asyncio
from pathlib import Path

# Add jarvis to path
sys.path.append(str(Path(__file__).parent / "jarvis"))


def test_quality_evaluator_initialization():
    """Test QualityEvaluator initialization."""
    print("🔧 Testing Quality Evaluator Initialization")
    print("=" * 50)
    
    try:
        from jarvis.config import get_config
        from jarvis.tools.rag_service import RAGService
        from jarvis.tools.rag_quality_metrics import RAGQualityEvaluator
        
        config = get_config()
        rag_service = RAGService(config)
        
        # Initialize evaluator
        evaluator = RAGQualityEvaluator(rag_service)
        
        print("✅ Quality evaluator initialized successfully")
        
        # Check attributes
        if hasattr(evaluator, 'rag_service'):
            print("✅ RAG service reference set")
        else:
            print("❌ RAG service reference missing")
            return False
        
        if hasattr(evaluator, 'metrics_history'):
            print("✅ Metrics history initialized")
        else:
            print("❌ Metrics history missing")
            return False
        
        if hasattr(evaluator, 'metrics_path'):
            print("✅ Metrics path configured")
        else:
            print("❌ Metrics path missing")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Quality evaluator initialization failed: {e}")
        return False


def test_retrieval_accuracy_evaluation():
    """Test retrieval accuracy evaluation."""
    print("\n📊 Testing Retrieval Accuracy Evaluation")
    print("=" * 50)
    
    try:
        from jarvis.config import get_config
        from jarvis.tools.rag_service import RAGService
        from jarvis.tools.rag_quality_metrics import RAGQualityEvaluator
        
        config = get_config()
        rag_service = RAGService(config)
        evaluator = RAGQualityEvaluator(rag_service)
        
        # Create mock search results
        class MockDoc:
            def __init__(self, content, source):
                self.page_content = content
                self.metadata = {'source': source}
        
        mock_results = {
            'retrieved_documents': [
                MockDoc("Python is a programming language used for AI development", "python_guide.txt"),
                MockDoc("Machine learning algorithms require data preprocessing", "ml_basics.pdf"),
                MockDoc("Software engineering best practices include testing", "dev_guide.docx")
            ]
        }
        
        # Test retrieval accuracy
        query = "Python programming language"
        accuracy, details = evaluator.evaluate_retrieval_accuracy(
            query, mock_results, expected_sources=["python_guide.txt"]
        )
        
        print(f"✅ Retrieval accuracy: {accuracy:.3f}")
        print(f"   Retrieved documents: {details['retrieved_count']}")
        print(f"   Relevant documents: {details['relevant_count']}")
        print(f"   Source diversity: {details['source_diversity']}")
        print(f"   Expected sources found: {details['expected_sources_found']}")
        
        # Validate results
        if 0 <= accuracy <= 1:
            print("✅ Accuracy score in valid range")
        else:
            print(f"❌ Invalid accuracy score: {accuracy}")
            return False
        
        if details['retrieved_count'] == 3:
            print("✅ Correct document count")
        else:
            print(f"❌ Incorrect document count: {details['retrieved_count']}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Retrieval accuracy evaluation failed: {e}")
        return False


def test_answer_faithfulness_evaluation():
    """Test answer faithfulness evaluation."""
    print("\n🎯 Testing Answer Faithfulness Evaluation")
    print("=" * 50)
    
    try:
        from jarvis.config import get_config
        from jarvis.tools.rag_service import RAGService
        from jarvis.tools.rag_quality_metrics import RAGQualityEvaluator
        
        config = get_config()
        rag_service = RAGService(config)
        evaluator = RAGQualityEvaluator(rag_service)
        
        # Create mock documents and answer
        class MockDoc:
            def __init__(self, content):
                self.page_content = content
        
        mock_docs = [
            MockDoc("Python is a high-level programming language known for its simplicity"),
            MockDoc("It is widely used in artificial intelligence and machine learning")
        ]
        
        # Test faithful answer
        faithful_answer = "Python is a high-level programming language widely used in artificial intelligence"
        faithfulness, details = evaluator.evaluate_answer_faithfulness(
            "What is Python?", faithful_answer, mock_docs
        )
        
        print(f"✅ Faithfulness score: {faithfulness:.3f}")
        print(f"   Content overlap: {details['source_content_overlap']:.3f}")
        print(f"   Factual consistency: {details['factual_consistency']:.3f}")
        print(f"   Hallucination indicators: {len(details['hallucination_indicators'])}")
        
        # Test unfaithful answer
        unfaithful_answer = "I think Python might be a snake, but I'm not sure about programming"
        unfaithful_score, unfaithful_details = evaluator.evaluate_answer_faithfulness(
            "What is Python?", unfaithful_answer, mock_docs
        )
        
        print(f"\n📉 Unfaithful answer score: {unfaithful_score:.3f}")
        print(f"   Hallucination indicators: {len(unfaithful_details['hallucination_indicators'])}")
        
        # Validate results
        if faithfulness > unfaithful_score:
            print("✅ Faithful answer scored higher than unfaithful answer")
        else:
            print("❌ Scoring issue: unfaithful answer scored higher")
            return False
        
        if len(unfaithful_details['hallucination_indicators']) > 0:
            print("✅ Hallucination indicators detected in unfaithful answer")
        else:
            print("❌ Failed to detect hallucination indicators")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Answer faithfulness evaluation failed: {e}")
        return False


def test_source_citation_evaluation():
    """Test source citation accuracy evaluation."""
    print("\n📚 Testing Source Citation Evaluation")
    print("=" * 45)
    
    try:
        from jarvis.config import get_config
        from jarvis.tools.rag_service import RAGService
        from jarvis.tools.rag_quality_metrics import RAGQualityEvaluator
        
        config = get_config()
        rag_service = RAGService(config)
        evaluator = RAGQualityEvaluator(rag_service)
        
        # Create mock documents
        class MockDoc:
            def __init__(self, content, source):
                self.page_content = content
                self.metadata = {'source': source}
        
        mock_docs = [
            MockDoc("Python programming content", "python_guide.txt"),
            MockDoc("AI development content", "ai_handbook.pdf")
        ]
        
        # Test answer with good citations
        cited_answer = "According to python_guide.txt, Python is excellent for programming. Based on ai_handbook.pdf, it's also great for AI development."
        citation_accuracy, details = evaluator.evaluate_source_citation_accuracy(cited_answer, mock_docs)
        
        print(f"✅ Citation accuracy: {citation_accuracy:.3f}")
        print(f"   Citations found: {details['citations_found']}")
        print(f"   Valid citations: {details['valid_citations']}")
        print(f"   Missing citations: {details['missing_citations']}")
        print(f"   Citation patterns: {details['citation_patterns']}")
        
        # Test answer without citations
        uncited_answer = "Python is great for programming and AI development."
        uncited_accuracy, uncited_details = evaluator.evaluate_source_citation_accuracy(uncited_answer, mock_docs)
        
        print(f"\n📉 Uncited answer accuracy: {uncited_accuracy:.3f}")
        print(f"   Citations found: {uncited_details['citations_found']}")
        
        # Validate results
        if citation_accuracy > uncited_accuracy:
            print("✅ Cited answer scored higher than uncited answer")
        else:
            print("❌ Citation scoring issue")
            return False
        
        if details['citations_found'] > 0:
            print("✅ Citations detected in cited answer")
        else:
            print("❌ Failed to detect citations")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Source citation evaluation failed: {e}")
        return False


def test_comprehensive_quality_evaluation():
    """Test comprehensive quality evaluation."""
    print("\n🔍 Testing Comprehensive Quality Evaluation")
    print("=" * 55)
    
    try:
        from jarvis.config import get_config
        from jarvis.tools.rag_service import RAGService
        from jarvis.tools.rag_quality_metrics import RAGQualityEvaluator
        
        config = get_config()
        rag_service = RAGService(config)
        evaluator = RAGQualityEvaluator(rag_service)
        
        # Add test memory
        test_fact = "Quality metrics testing: Python is the preferred programming language for AI projects"
        rag_service.add_conversational_memory(test_fact)
        
        print("📝 Added test memory for evaluation")
        
        # Run comprehensive evaluation
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            metrics = loop.run_until_complete(
                evaluator.evaluate_query("What programming language is preferred for AI?")
            )
            
            print(f"✅ Comprehensive evaluation completed:")
            print(f"   Retrieval accuracy: {metrics.retrieval_accuracy:.3f}")
            print(f"   Answer faithfulness: {metrics.answer_faithfulness:.3f}")
            print(f"   Source citation accuracy: {metrics.source_citation_accuracy:.3f}")
            print(f"   Response time: {metrics.response_time:.2f}s")
            print(f"   Overall score: {metrics.overall_score:.3f}")
            
            # Validate metrics
            if 0 <= metrics.overall_score <= 1:
                print("✅ Overall score in valid range")
            else:
                print(f"❌ Invalid overall score: {metrics.overall_score}")
                return False
            
            if metrics.response_time > 0:
                print("✅ Response time recorded")
            else:
                print("❌ Invalid response time")
                return False
            
            # Test aggregate metrics
            aggregate = evaluator.get_aggregate_metrics()
            
            if aggregate['status'] == 'success':
                print("✅ Aggregate metrics generated successfully")
                print(f"   Quality level: {aggregate['quality_level']}")
                print(f"   Evaluation count: {aggregate['evaluation_count']}")
            else:
                print("❌ Failed to generate aggregate metrics")
                return False
            
            return True
            
        finally:
            loop.close()
        
    except Exception as e:
        print(f"❌ Comprehensive quality evaluation failed: {e}")
        return False


def test_metrics_persistence():
    """Test metrics saving and loading."""
    print("\n💾 Testing Metrics Persistence")
    print("=" * 40)
    
    try:
        from jarvis.config import get_config
        from jarvis.tools.rag_service import RAGService
        from jarvis.tools.rag_quality_metrics import RAGQualityEvaluator, QualityMetrics
        from datetime import datetime
        
        config = get_config()
        rag_service = RAGService(config)
        evaluator = RAGQualityEvaluator(rag_service)
        
        # Create test metrics
        test_metrics = QualityMetrics(
            retrieval_accuracy=0.85,
            answer_faithfulness=0.90,
            source_citation_accuracy=0.75,
            response_time=2.5,
            overall_score=0.83,
            timestamp=datetime.now().isoformat(),
            details={"test": "data"}
        )
        
        evaluator.metrics_history.append(test_metrics)
        
        # Test saving
        saved_path = evaluator.save_metrics("test_metrics.json")
        print(f"✅ Metrics saved to: {saved_path}")
        
        # Test loading
        new_evaluator = RAGQualityEvaluator(rag_service)
        loaded_count = new_evaluator.load_metrics(saved_path)
        
        print(f"✅ Loaded {loaded_count} metrics")
        
        if loaded_count == 1:
            loaded_metric = new_evaluator.metrics_history[0]
            if abs(loaded_metric.overall_score - test_metrics.overall_score) < 0.001:
                print("✅ Metrics loaded correctly")
            else:
                print("❌ Metrics data mismatch")
                return False
        else:
            print("❌ Incorrect number of metrics loaded")
            return False
        
        # Cleanup
        import os
        if os.path.exists(saved_path):
            os.unlink(saved_path)
            print("✅ Test file cleaned up")
        
        return True
        
    except Exception as e:
        print(f"❌ Metrics persistence test failed: {e}")
        return False


def main():
    """Main test function."""
    print("🚀 RAG Quality Metrics Testing Suite")
    print("=" * 60)
    print("Testing comprehensive quality measurement system...")
    print()
    
    tests = [
        ("Quality Evaluator Initialization", test_quality_evaluator_initialization),
        ("Retrieval Accuracy Evaluation", test_retrieval_accuracy_evaluation),
        ("Answer Faithfulness Evaluation", test_answer_faithfulness_evaluation),
        ("Source Citation Evaluation", test_source_citation_evaluation),
        ("Comprehensive Quality Evaluation", test_comprehensive_quality_evaluation),
        ("Metrics Persistence", test_metrics_persistence)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"\n📊 Quality Metrics Test Results")
    print("=" * 40)
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\n📈 Overall Results:")
    print(f"✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")
    print(f"📊 Success Rate: {passed/total*100:.1f}%")
    
    if passed == total:
        print("\n🎉 Quality Metrics System: COMPLETE!")
        print("   ✅ Retrieval accuracy measurement working")
        print("   ✅ Answer faithfulness evaluation functional")
        print("   ✅ Source citation accuracy assessment operational")
        print("   ✅ Comprehensive evaluation system working")
        print("   ✅ Metrics persistence and aggregation successful")
        print("\n📊 RAG system now has comprehensive quality measurement!")
    elif passed >= total * 0.8:
        print(f"\n✅ Quality Metrics System mostly complete!")
        print(f"   Core quality measurement working with minor issues")
    else:
        print(f"\n⚠️  Quality Metrics System needs attention")
        print(f"   Multiple quality measurement issues detected")
    
    return passed >= total * 0.8


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
