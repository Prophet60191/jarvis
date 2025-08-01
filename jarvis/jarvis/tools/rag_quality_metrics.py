#!/usr/bin/env python3
"""
RAG Quality Metrics System

Provides comprehensive quality measurement for RAG system including
retrieval accuracy, answer faithfulness, and source citation accuracy.
"""

import asyncio
import re
import time
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import json
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class QualityMetrics:
    """Container for quality measurement results."""
    retrieval_accuracy: float
    answer_faithfulness: float
    source_citation_accuracy: float
    response_time: float
    overall_score: float
    timestamp: str
    details: Dict[str, Any]


class RAGQualityEvaluator:
    """Evaluates RAG system quality across multiple dimensions."""
    
    def __init__(self, rag_service):
        """
        Initialize quality evaluator.
        
        Args:
            rag_service: RAG service instance to evaluate
        """
        self.rag_service = rag_service
        self.metrics_history: List[QualityMetrics] = []
        self.metrics_path = Path("data/quality_metrics")
        self.metrics_path.mkdir(parents=True, exist_ok=True)
    
    def evaluate_retrieval_accuracy(self, query: str, search_results: Dict[str, Any], 
                                  expected_sources: Optional[List[str]] = None) -> Tuple[float, Dict[str, Any]]:
        """
        Evaluate retrieval accuracy based on relevance and source quality.
        
        Args:
            query: Original search query
            search_results: RAG search results
            expected_sources: Optional list of expected source documents
            
        Returns:
            tuple: (accuracy_score, details)
        """
        details = {
            "query": query,
            "retrieved_count": 0,
            "relevant_count": 0,
            "source_diversity": 0,
            "expected_sources_found": 0
        }
        
        retrieved_docs = search_results.get('retrieved_documents', [])
        details["retrieved_count"] = len(retrieved_docs)
        
        if not retrieved_docs:
            return 0.0, details
        
        # Evaluate relevance based on content similarity
        query_terms = set(query.lower().split())
        relevant_count = 0
        
        for doc in retrieved_docs:
            content = doc.page_content.lower()
            # Simple relevance check: document contains query terms
            content_terms = set(content.split())
            overlap = len(query_terms.intersection(content_terms))
            
            if overlap >= max(1, len(query_terms) * 0.3):  # At least 30% term overlap
                relevant_count += 1
        
        details["relevant_count"] = relevant_count
        
        # Calculate source diversity
        sources = set()
        for doc in retrieved_docs:
            source = doc.metadata.get('source', 'unknown')
            sources.add(source)
        
        details["source_diversity"] = len(sources)
        
        # Check expected sources if provided
        if expected_sources:
            found_sources = 0
            for expected in expected_sources:
                for doc in retrieved_docs:
                    if expected.lower() in doc.metadata.get('source', '').lower():
                        found_sources += 1
                        break
            details["expected_sources_found"] = found_sources
        
        # Calculate accuracy score
        relevance_score = relevant_count / len(retrieved_docs) if retrieved_docs else 0
        diversity_bonus = min(0.2, len(sources) * 0.05)  # Bonus for source diversity
        expected_bonus = 0
        
        if expected_sources:
            expected_bonus = (details["expected_sources_found"] / len(expected_sources)) * 0.3
        
        accuracy_score = min(1.0, relevance_score + diversity_bonus + expected_bonus)
        
        return accuracy_score, details
    
    def evaluate_answer_faithfulness(self, query: str, answer: str, 
                                   retrieved_docs: List[Any]) -> Tuple[float, Dict[str, Any]]:
        """
        Evaluate how faithful the answer is to the retrieved documents.
        
        Args:
            query: Original query
            answer: Generated answer
            retrieved_docs: Retrieved documents used for answer
            
        Returns:
            tuple: (faithfulness_score, details)
        """
        details = {
            "query": query,
            "answer_length": len(answer),
            "source_content_overlap": 0,
            "hallucination_indicators": [],
            "factual_consistency": 0
        }
        
        if not answer or not retrieved_docs:
            return 0.0, details
        
        # Combine all retrieved content
        all_content = " ".join([doc.page_content for doc in retrieved_docs])
        
        # Calculate content overlap
        answer_words = set(answer.lower().split())
        content_words = set(all_content.lower().split())
        overlap = len(answer_words.intersection(content_words))
        
        details["source_content_overlap"] = overlap / len(answer_words) if answer_words else 0
        
        # Check for potential hallucination indicators
        hallucination_patterns = [
            r'\b(I think|I believe|probably|maybe|might be)\b',
            r'\b(according to my knowledge|as far as I know)\b',
            r'\b(generally|typically|usually)\b'
        ]
        
        for pattern in hallucination_patterns:
            matches = re.findall(pattern, answer, re.IGNORECASE)
            if matches:
                details["hallucination_indicators"].extend(matches)
        
        # Simple factual consistency check
        # Look for specific facts in answer that should be in source documents
        answer_sentences = answer.split('.')
        consistent_sentences = 0
        
        for sentence in answer_sentences:
            sentence = sentence.strip()
            if len(sentence) < 10:  # Skip very short sentences
                continue
            
            # Check if key terms from sentence appear in source content
            sentence_words = set(sentence.lower().split())
            if len(sentence_words.intersection(content_words)) >= len(sentence_words) * 0.4:
                consistent_sentences += 1
        
        details["factual_consistency"] = consistent_sentences / len(answer_sentences) if answer_sentences else 0
        
        # Calculate faithfulness score
        overlap_score = details["source_content_overlap"]
        consistency_score = details["factual_consistency"]
        hallucination_penalty = min(0.3, len(details["hallucination_indicators"]) * 0.1)
        
        faithfulness_score = max(0.0, (overlap_score * 0.6 + consistency_score * 0.4) - hallucination_penalty)
        
        return faithfulness_score, details
    
    def evaluate_source_citation_accuracy(self, answer: str, 
                                        retrieved_docs: List[Any]) -> Tuple[float, Dict[str, Any]]:
        """
        Evaluate accuracy of source citations in the answer.
        
        Args:
            answer: Generated answer with potential citations
            retrieved_docs: Retrieved documents that should be cited
            
        Returns:
            tuple: (citation_accuracy_score, details)
        """
        details = {
            "citations_found": 0,
            "valid_citations": 0,
            "missing_citations": 0,
            "citation_patterns": []
        }
        
        if not retrieved_docs:
            return 1.0, details  # No docs to cite
        
        # Extract source names from retrieved documents
        available_sources = set()
        for doc in retrieved_docs:
            source = doc.metadata.get('source', '')
            if source:
                # Extract filename without extension
                source_name = Path(source).stem
                available_sources.add(source_name.lower())
        
        # Look for citation patterns in answer
        citation_patterns = [
            r'according to ([^,\.\n]+)',
            r'based on ([^,\.\n]+)',
            r'from ([^,\.\n]+)',
            r'source: ([^,\.\n]+)',
            r'\[([^\]]+)\]',  # Bracketed citations
            r'in ([^,\.\n]+\.(?:pdf|txt|docx?))',  # File references
        ]
        
        found_citations = set()
        for pattern in citation_patterns:
            matches = re.findall(pattern, answer, re.IGNORECASE)
            for match in matches:
                citation = match.strip().lower()
                found_citations.add(citation)
                details["citation_patterns"].append(match)
        
        details["citations_found"] = len(found_citations)
        
        # Check validity of citations
        valid_citations = 0
        for citation in found_citations:
            for source in available_sources:
                if source in citation or citation in source:
                    valid_citations += 1
                    break
        
        details["valid_citations"] = valid_citations
        
        # Check for missing citations (sources used but not cited)
        cited_sources = set()
        for citation in found_citations:
            for source in available_sources:
                if source in citation or citation in source:
                    cited_sources.add(source)
        
        uncited_sources = available_sources - cited_sources
        details["missing_citations"] = len(uncited_sources)
        
        # Calculate citation accuracy
        if not available_sources:
            return 1.0, details
        
        citation_coverage = len(cited_sources) / len(available_sources)
        citation_precision = valid_citations / len(found_citations) if found_citations else 0
        
        citation_accuracy = (citation_coverage * 0.7 + citation_precision * 0.3)
        
        return citation_accuracy, details
    
    async def evaluate_query(self, query: str, expected_sources: Optional[List[str]] = None) -> QualityMetrics:
        """
        Perform comprehensive quality evaluation for a single query.
        
        Args:
            query: Query to evaluate
            expected_sources: Optional list of expected source documents
            
        Returns:
            QualityMetrics: Complete quality assessment
        """
        start_time = time.time()
        
        try:
            # Get RAG response
            search_results = await self.rag_service.intelligent_search(query)
            
            end_time = time.time()
            response_time = end_time - start_time
            
            # Extract components
            synthesis = search_results.get('synthesis', {})
            answer = synthesis.get('synthesized_answer', '')
            retrieved_docs = search_results.get('retrieved_documents', [])
            
            # Evaluate each dimension
            retrieval_accuracy, retrieval_details = self.evaluate_retrieval_accuracy(
                query, search_results, expected_sources
            )
            
            faithfulness_score, faithfulness_details = self.evaluate_answer_faithfulness(
                query, answer, retrieved_docs
            )
            
            citation_accuracy, citation_details = self.evaluate_source_citation_accuracy(
                answer, retrieved_docs
            )
            
            # Calculate overall score
            weights = {
                'retrieval': 0.4,
                'faithfulness': 0.4,
                'citation': 0.2
            }
            
            overall_score = (
                retrieval_accuracy * weights['retrieval'] +
                faithfulness_score * weights['faithfulness'] +
                citation_accuracy * weights['citation']
            )
            
            # Create metrics object
            metrics = QualityMetrics(
                retrieval_accuracy=retrieval_accuracy,
                answer_faithfulness=faithfulness_score,
                source_citation_accuracy=citation_accuracy,
                response_time=response_time,
                overall_score=overall_score,
                timestamp=datetime.now().isoformat(),
                details={
                    'query': query,
                    'answer': answer,
                    'retrieval': retrieval_details,
                    'faithfulness': faithfulness_details,
                    'citation': citation_details,
                    'weights': weights
                }
            )
            
            # Store metrics
            self.metrics_history.append(metrics)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Quality evaluation failed for query '{query}': {e}")
            
            # Return minimal metrics on error
            return QualityMetrics(
                retrieval_accuracy=0.0,
                answer_faithfulness=0.0,
                source_citation_accuracy=0.0,
                response_time=time.time() - start_time,
                overall_score=0.0,
                timestamp=datetime.now().isoformat(),
                details={'error': str(e), 'query': query}
            )
    
    def get_aggregate_metrics(self, recent_count: int = 10) -> Dict[str, Any]:
        """
        Get aggregate quality metrics from recent evaluations.
        
        Args:
            recent_count: Number of recent evaluations to include
            
        Returns:
            dict: Aggregate metrics summary
        """
        if not self.metrics_history:
            return {
                "status": "no_data",
                "message": "No quality metrics available"
            }
        
        recent_metrics = self.metrics_history[-recent_count:]
        
        # Calculate averages
        avg_retrieval = sum(m.retrieval_accuracy for m in recent_metrics) / len(recent_metrics)
        avg_faithfulness = sum(m.answer_faithfulness for m in recent_metrics) / len(recent_metrics)
        avg_citation = sum(m.source_citation_accuracy for m in recent_metrics) / len(recent_metrics)
        avg_response_time = sum(m.response_time for m in recent_metrics) / len(recent_metrics)
        avg_overall = sum(m.overall_score for m in recent_metrics) / len(recent_metrics)
        
        # Quality assessment
        quality_level = "excellent" if avg_overall >= 0.9 else \
                       "good" if avg_overall >= 0.8 else \
                       "fair" if avg_overall >= 0.7 else \
                       "poor"
        
        return {
            "status": "success",
            "evaluation_count": len(recent_metrics),
            "total_evaluations": len(self.metrics_history),
            "averages": {
                "retrieval_accuracy": round(avg_retrieval, 3),
                "answer_faithfulness": round(avg_faithfulness, 3),
                "source_citation_accuracy": round(avg_citation, 3),
                "response_time": round(avg_response_time, 2),
                "overall_score": round(avg_overall, 3)
            },
            "quality_level": quality_level,
            "timestamp": datetime.now().isoformat()
        }
    
    def save_metrics(self, filename: Optional[str] = None) -> str:
        """
        Save metrics history to file.
        
        Args:
            filename: Optional custom filename
            
        Returns:
            str: Path to saved file
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"quality_metrics_{timestamp}.json"
        
        filepath = self.metrics_path / filename
        
        # Convert metrics to serializable format
        metrics_data = []
        for metric in self.metrics_history:
            metrics_data.append({
                "retrieval_accuracy": metric.retrieval_accuracy,
                "answer_faithfulness": metric.answer_faithfulness,
                "source_citation_accuracy": metric.source_citation_accuracy,
                "response_time": metric.response_time,
                "overall_score": metric.overall_score,
                "timestamp": metric.timestamp,
                "details": metric.details
            })
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump({
                "metadata": {
                    "total_evaluations": len(metrics_data),
                    "created": datetime.now().isoformat(),
                    "version": "1.0"
                },
                "metrics": metrics_data
            }, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved {len(metrics_data)} quality metrics to {filepath}")
        return str(filepath)
    
    def load_metrics(self, filepath: str) -> int:
        """
        Load metrics history from file.
        
        Args:
            filepath: Path to metrics file
            
        Returns:
            int: Number of metrics loaded
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            metrics_data = data.get('metrics', [])
            
            for metric_data in metrics_data:
                metric = QualityMetrics(
                    retrieval_accuracy=metric_data['retrieval_accuracy'],
                    answer_faithfulness=metric_data['answer_faithfulness'],
                    source_citation_accuracy=metric_data['source_citation_accuracy'],
                    response_time=metric_data['response_time'],
                    overall_score=metric_data['overall_score'],
                    timestamp=metric_data['timestamp'],
                    details=metric_data['details']
                )
                self.metrics_history.append(metric)
            
            logger.info(f"Loaded {len(metrics_data)} quality metrics from {filepath}")
            return len(metrics_data)
            
        except Exception as e:
            logger.error(f"Failed to load metrics from {filepath}: {e}")
            return 0
