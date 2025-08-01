#!/usr/bin/env python3
"""
Performance Monitoring Manager - Handles performance tracking and optimization alerts.

SEPARATION OF CONCERNS:
- This module ONLY handles performance monitoring and metrics
- It does NOT handle query processing, memory, or tool selection
- It provides a clean interface for performance tracking operations

SINGLE RESPONSIBILITY: Performance monitoring, metrics collection, and optimization alerts
"""

import logging
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class PerformanceLevel(Enum):
    """Performance level indicators."""
    EXCELLENT = "excellent"
    GOOD = "good"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class PerformanceMetric:
    """Individual performance metric."""
    name: str
    value: float
    target: float
    unit: str
    level: PerformanceLevel
    suggestions: List[str]


@dataclass
class QueryPerformanceResult:
    """Performance result for a single query."""
    query_id: str
    processing_time_ms: float
    target_met: bool
    performance_level: PerformanceLevel
    metrics: List[PerformanceMetric]
    optimization_notes: List[str]


class PerformanceMonitoringManager:
    """
    Manages performance monitoring and optimization tracking.
    
    SINGLE RESPONSIBILITY: Performance monitoring and metrics only.
    
    Tracks response times, performance targets, and provides optimization suggestions.
    """
    
    def __init__(self):
        """Initialize performance monitoring manager."""
        # Performance targets (in milliseconds)
        self.performance_targets = {
            "instant": 50,      # Instant responses
            "simple": 1000,     # Simple queries  
            "complex": 5000     # Complex queries
        }
        
        # Session performance tracking
        self.session_metrics = {
            "queries_processed": 0,
            "total_response_time_ms": 0.0,
            "performance_targets_met": 0,
            "instant_responses": 0,
            "performance_violations": []
        }
        
        # Historical performance data
        self.performance_history = []
        
        logger.info("PerformanceMonitoringManager initialized")
    
    def start_performance_session(self) -> None:
        """Start new performance monitoring session."""
        self.session_metrics = {
            "queries_processed": 0,
            "total_response_time_ms": 0.0,
            "performance_targets_met": 0,
            "instant_responses": 0,
            "performance_violations": []
        }
        
        logger.info("🔍 Performance monitoring session started")
    
    def record_query_performance(self, 
                                query: str,
                                processing_time_ms: float,
                                query_complexity: str = "simple",
                                optimization_notes: Optional[List[str]] = None) -> QueryPerformanceResult:
        """
        Record performance for a single query.
        
        Args:
            query: The user query
            processing_time_ms: Processing time in milliseconds
            query_complexity: Query complexity level
            optimization_notes: Optional optimization notes
            
        Returns:
            QueryPerformanceResult with performance analysis
        """
        query_id = f"query_{int(time.time() * 1000)}"
        optimization_notes = optimization_notes or []
        
        # Determine target based on complexity
        target_ms = self.performance_targets.get(query_complexity, 1000)
        
        # Check if target was met
        target_met = processing_time_ms <= target_ms
        
        # Determine performance level
        performance_level = self._determine_performance_level(processing_time_ms, target_ms)
        
        # Create metrics
        metrics = [
            PerformanceMetric(
                name=f"{query_complexity.title()} Query Response Time",
                value=processing_time_ms,
                target=target_ms,
                unit="ms",
                level=performance_level,
                suggestions=self._get_performance_suggestions(performance_level, query_complexity)
            )
        ]
        
        # Update session metrics
        self._update_session_metrics(processing_time_ms, target_met, performance_level)
        
        # Create result
        result = QueryPerformanceResult(
            query_id=query_id,
            processing_time_ms=processing_time_ms,
            target_met=target_met,
            performance_level=performance_level,
            metrics=metrics,
            optimization_notes=optimization_notes
        )
        
        # Add to history
        self.performance_history.append(result)
        
        # Log performance alerts if needed
        self._log_performance_alerts(result, query)
        
        return result
    
    def _determine_performance_level(self, actual_ms: float, target_ms: float) -> PerformanceLevel:
        """Determine performance level based on actual vs target time."""
        ratio = actual_ms / target_ms
        
        if ratio <= 0.5:
            return PerformanceLevel.EXCELLENT
        elif ratio <= 1.0:
            return PerformanceLevel.GOOD
        elif ratio <= 2.0:
            return PerformanceLevel.WARNING
        else:
            return PerformanceLevel.CRITICAL
    
    def _get_performance_suggestions(self, level: PerformanceLevel, complexity: str) -> List[str]:
        """Get performance improvement suggestions based on level and complexity."""
        suggestions = []
        
        if level == PerformanceLevel.WARNING:
            if complexity == "instant":
                suggestions.extend(["Enable instant response caching", "Optimize pattern matching"])
            elif complexity == "simple":
                suggestions.extend(["Optimize context window", "Enable response caching"])
            else:
                suggestions.extend(["Reduce tool loading", "Implement parallel processing"])
        
        elif level == PerformanceLevel.CRITICAL:
            if complexity == "instant":
                suggestions.extend(["Fix instant handler", "Check pattern matching logic"])
            elif complexity == "simple":
                suggestions.extend(["Implement prompt caching", "Reduce tool loading"])
            else:
                suggestions.extend(["Enable tool selection optimization", "Implement query streaming"])
        
        return suggestions
    
    def _update_session_metrics(self, processing_time_ms: float, target_met: bool, level: PerformanceLevel) -> None:
        """Update session-level performance metrics."""
        self.session_metrics["queries_processed"] += 1
        self.session_metrics["total_response_time_ms"] += processing_time_ms
        
        if target_met:
            self.session_metrics["performance_targets_met"] += 1
        
        if processing_time_ms <= 50:  # Instant response threshold
            self.session_metrics["instant_responses"] += 1
        
        if level in [PerformanceLevel.WARNING, PerformanceLevel.CRITICAL]:
            self.session_metrics["performance_violations"].append({
                "time": time.time(),
                "processing_time_ms": processing_time_ms,
                "level": level.value
            })
    
    def _log_performance_alerts(self, result: QueryPerformanceResult, query: str) -> None:
        """Log performance alerts for warning/critical performance."""
        if result.performance_level == PerformanceLevel.WARNING:
            metric = result.metrics[0]
            logger.warning(f"Performance alert: {metric.name} is {metric.level.value}: "
                          f"{metric.value:.3f} {metric.unit} (target: {metric.target:.3f}). "
                          f"Suggestions: {', '.join(metric.suggestions)}")
        
        elif result.performance_level == PerformanceLevel.CRITICAL:
            metric = result.metrics[0]
            logger.warning(f"Performance alert: {metric.name} is {metric.level.value}: "
                          f"{metric.value:.3f} {metric.unit} (target: {metric.target:.3f}). "
                          f"Suggestions: {', '.join(metric.suggestions)}")
    
    def get_session_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary for current session."""
        queries = self.session_metrics["queries_processed"]
        
        if queries == 0:
            return {"error": "No queries processed in session"}
        
        avg_response_time = self.session_metrics["total_response_time_ms"] / queries
        performance_rate = self.session_metrics["performance_targets_met"] / queries
        instant_rate = self.session_metrics["instant_responses"] / queries
        
        return {
            "queries_processed": queries,
            "avg_response_time_ms": avg_response_time,
            "performance_targets_met_rate": performance_rate,
            "instant_response_rate": instant_rate,
            "optimization_success": performance_rate > 0.8,  # 80% target
            "performance_violations": len(self.session_metrics["performance_violations"]),
            "performance_level": self._get_overall_performance_level(performance_rate)
        }
    
    def _get_overall_performance_level(self, performance_rate: float) -> str:
        """Get overall performance level for session."""
        if performance_rate >= 0.9:
            return "excellent"
        elif performance_rate >= 0.8:
            return "good"
        elif performance_rate >= 0.6:
            return "warning"
        else:
            return "critical"
    
    def get_performance_history(self, limit: int = 10) -> List[QueryPerformanceResult]:
        """Get recent performance history."""
        return self.performance_history[-limit:]
    
    def clear_performance_history(self) -> None:
        """Clear performance history."""
        self.performance_history.clear()
        logger.info("Performance history cleared")
    
    def end_performance_session(self) -> Dict[str, Any]:
        """End performance monitoring session and return summary."""
        summary = self.get_session_performance_summary()
        
        # Reset session metrics
        self.session_metrics = {
            "queries_processed": 0,
            "total_response_time_ms": 0.0,
            "performance_targets_met": 0,
            "instant_responses": 0,
            "performance_violations": []
        }
        
        logger.info("🔍 Performance monitoring session ended")
        return summary


# Singleton instance for global access
_performance_monitoring_manager = None


def get_performance_monitoring_manager() -> PerformanceMonitoringManager:
    """
    Get singleton performance monitoring manager instance.
    
    Returns:
        PerformanceMonitoringManager instance
    """
    global _performance_monitoring_manager
    if _performance_monitoring_manager is None:
        _performance_monitoring_manager = PerformanceMonitoringManager()
    return _performance_monitoring_manager
