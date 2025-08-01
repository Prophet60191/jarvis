"""
Performance Monitoring Framework for Jarvis Voice Assistant

Real-time performance monitoring with automatic optimization suggestions
and alerting for performance targets defined in the simplification plan.
"""

import time
import logging
import threading
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from collections import deque, defaultdict
from enum import Enum
import statistics

logger = logging.getLogger(__name__)


class PerformanceLevel(Enum):
    """Performance level indicators."""
    EXCELLENT = "excellent"    # Meeting or exceeding targets
    GOOD = "good"             # Within acceptable range
    WARNING = "warning"       # Approaching limits
    CRITICAL = "critical"     # Exceeding limits, action needed


@dataclass
class PerformanceTarget:
    """Performance target definition."""
    name: str
    target_value: float
    warning_threshold: float
    critical_threshold: float
    unit: str
    description: str


@dataclass
class PerformanceMetric:
    """Performance metric with history."""
    name: str
    current_value: float
    history: deque = field(default_factory=lambda: deque(maxlen=100))
    target: Optional[PerformanceTarget] = None
    last_updated: float = field(default_factory=time.time)
    
    def add_measurement(self, value: float) -> None:
        """Add new measurement to history."""
        self.current_value = value
        self.history.append((time.time(), value))
        self.last_updated = time.time()
    
    def get_average(self, window_seconds: int = 300) -> float:
        """Get average value over time window."""
        cutoff_time = time.time() - window_seconds
        recent_values = [value for timestamp, value in self.history if timestamp > cutoff_time]
        return statistics.mean(recent_values) if recent_values else self.current_value
    
    def get_performance_level(self) -> PerformanceLevel:
        """Get current performance level based on target."""
        if not self.target:
            return PerformanceLevel.GOOD
        
        if self.current_value <= self.target.target_value:
            return PerformanceLevel.EXCELLENT
        elif self.current_value <= self.target.warning_threshold:
            return PerformanceLevel.GOOD
        elif self.current_value <= self.target.critical_threshold:
            return PerformanceLevel.WARNING
        else:
            return PerformanceLevel.CRITICAL


@dataclass
class PerformanceAlert:
    """Performance alert notification."""
    metric_name: str
    level: PerformanceLevel
    current_value: float
    target_value: float
    message: str
    timestamp: float = field(default_factory=time.time)
    acknowledged: bool = False


class PerformanceMonitor:
    """
    Real-time performance monitoring system.
    
    Tracks key performance metrics against targets defined in the simplification plan:
    - Response times by query complexity
    - Cache hit rates
    - API call counts
    - Memory usage
    - Tool selection accuracy
    """
    
    def __init__(self):
        """Initialize performance monitor."""
        self.metrics: Dict[str, PerformanceMetric] = {}
        self.alerts: List[PerformanceAlert] = []
        self.alert_callbacks: List[Callable[[PerformanceAlert], None]] = []
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Performance targets from simplification plan
        self._initialize_targets()
        
        # Monitoring state
        self.monitoring_enabled = True
        self.alert_cooldown = 300  # 5 minutes between similar alerts
        self._last_alert_times: Dict[str, float] = {}
        
        logger.info("PerformanceMonitor initialized with targets")
    
    def _initialize_targets(self) -> None:
        """Initialize performance targets from simplification plan."""
        targets = {
            # Response time targets by complexity
            "response_time_instant": PerformanceTarget(
                name="Instant Query Response Time",
                target_value=0.05,  # 50ms
                warning_threshold=0.1,  # 100ms
                critical_threshold=0.5,  # 500ms
                unit="seconds",
                description="Response time for instant queries (greetings, simple acknowledgments)"
            ),
            "response_time_explicit_fact": PerformanceTarget(
                name="Explicit Fact Response Time",
                target_value=0.3,  # 300ms
                warning_threshold=0.5,  # 500ms
                critical_threshold=1.0,  # 1s
                unit="seconds",
                description="Response time for explicit fact queries (time, definitions)"
            ),
            "response_time_simple_reasoning": PerformanceTarget(
                name="Simple Reasoning Response Time",
                target_value=1.0,  # 1s
                warning_threshold=2.0,  # 2s
                critical_threshold=5.0,  # 5s
                unit="seconds",
                description="Response time for simple reasoning queries"
            ),
            "response_time_complex": PerformanceTarget(
                name="Complex Multi-Step Response Time",
                target_value=5.0,  # 5s
                warning_threshold=10.0,  # 10s
                critical_threshold=30.0,  # 30s
                unit="seconds",
                description="Response time for complex multi-step queries"
            ),
            
            # Cache performance targets
            "cache_hit_rate": PerformanceTarget(
                name="Cache Hit Rate",
                target_value=0.7,  # 70%
                warning_threshold=0.5,  # 50%
                critical_threshold=0.3,  # 30%
                unit="percentage",
                description="Overall cache hit rate across all tiers"
            ),
            
            # API call efficiency
            "api_calls_per_query": PerformanceTarget(
                name="API Calls Per Query",
                target_value=0.5,  # 0.5 average
                warning_threshold=1.0,  # 1 call
                critical_threshold=3.0,  # 3 calls
                unit="calls",
                description="Average API calls per query (target: 90% reduction from 6+)"
            ),
            
            # Memory usage
            "memory_usage_mb": PerformanceTarget(
                name="Memory Usage",
                target_value=200.0,  # 200MB
                warning_threshold=500.0,  # 500MB
                critical_threshold=1000.0,  # 1GB
                unit="MB",
                description="Total memory usage"
            ),
            
            # Tool selection accuracy
            "tool_selection_accuracy": PerformanceTarget(
                name="Tool Selection Accuracy",
                target_value=0.8,  # 80%
                warning_threshold=0.6,  # 60%
                critical_threshold=0.4,  # 40%
                unit="percentage",
                description="Accuracy of semantic tool selection (2-3 tools vs 60)"
            )
        }
        
        # Initialize metrics with targets
        for metric_name, target in targets.items():
            self.metrics[metric_name] = PerformanceMetric(
                name=metric_name,
                current_value=0.0,
                target=target
            )
    
    def record_metric(self, metric_name: str, value: float) -> None:
        """
        Record a performance metric measurement.
        
        Args:
            metric_name: Name of the metric
            value: Measured value
        """
        if not self.monitoring_enabled:
            return
        
        with self._lock:
            if metric_name not in self.metrics:
                # Create new metric without target
                self.metrics[metric_name] = PerformanceMetric(
                    name=metric_name,
                    current_value=value
                )
            else:
                self.metrics[metric_name].add_measurement(value)
            
            # Check for alerts
            self._check_alerts(metric_name)
            
            logger.debug(f"Recorded metric {metric_name}: {value}")
    
    def record_response_time(self, complexity: str, response_time: float) -> None:
        """Record response time for specific query complexity."""
        metric_name = f"response_time_{complexity}"
        self.record_metric(metric_name, response_time)
    
    def record_cache_performance(self, hits: int, total: int) -> None:
        """Record cache performance metrics."""
        if total > 0:
            hit_rate = hits / total
            self.record_metric("cache_hit_rate", hit_rate)
    
    def record_api_calls(self, query_id: str, call_count: int) -> None:
        """Record API call count for a query."""
        self.record_metric("api_calls_per_query", call_count)
    
    def record_memory_usage(self, memory_mb: float) -> None:
        """Record current memory usage."""
        self.record_metric("memory_usage_mb", memory_mb)
    
    def record_tool_selection(self, selected_correctly: bool) -> None:
        """Record tool selection accuracy."""
        accuracy = 1.0 if selected_correctly else 0.0
        self.record_metric("tool_selection_accuracy", accuracy)
    
    def _check_alerts(self, metric_name: str) -> None:
        """Check if metric triggers any alerts."""
        metric = self.metrics[metric_name]
        if not metric.target:
            return
        
        performance_level = metric.get_performance_level()
        
        # Only alert on warning or critical levels
        if performance_level in [PerformanceLevel.WARNING, PerformanceLevel.CRITICAL]:
            # Check cooldown
            last_alert_time = self._last_alert_times.get(metric_name, 0)
            if time.time() - last_alert_time < self.alert_cooldown:
                return
            
            # Create alert
            alert = PerformanceAlert(
                metric_name=metric_name,
                level=performance_level,
                current_value=metric.current_value,
                target_value=metric.target.target_value,
                message=self._generate_alert_message(metric, performance_level)
            )
            
            self.alerts.append(alert)
            self._last_alert_times[metric_name] = time.time()
            
            # Notify callbacks
            for callback in self.alert_callbacks:
                try:
                    callback(alert)
                except Exception as e:
                    logger.error(f"Error in alert callback: {e}")
            
            logger.warning(f"Performance alert: {alert.message}")
    
    def _generate_alert_message(self, metric: PerformanceMetric, level: PerformanceLevel) -> str:
        """Generate alert message with optimization suggestions."""
        target = metric.target
        current = metric.current_value
        
        base_message = (f"{target.name} is {level.value}: "
                       f"{current:.3f} {target.unit} (target: {target.target_value:.3f})")
        
        # Add optimization suggestions
        suggestions = self._get_optimization_suggestions(metric.name, current, target.target_value)
        if suggestions:
            base_message += f". Suggestions: {suggestions}"
        
        return base_message
    
    def _get_optimization_suggestions(self, metric_name: str, current: float, target: float) -> str:
        """Get optimization suggestions for specific metrics."""
        suggestions = {
            "response_time_instant": "Enable instant response cache, optimize pattern matching",
            "response_time_explicit_fact": "Implement prompt caching, reduce tool loading",
            "response_time_simple_reasoning": "Optimize context window, enable response caching",
            "response_time_complex": "Implement semantic tool selection, parallel execution",
            "cache_hit_rate": "Tune cache TTL settings, improve cache key generation",
            "api_calls_per_query": "Enable response caching, implement query classification",
            "memory_usage_mb": "Enable memory optimization, clear unused caches",
            "tool_selection_accuracy": "Improve semantic matching, update tool embeddings"
        }
        
        return suggestions.get(metric_name, "Review system configuration")
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary."""
        with self._lock:
            summary = {
                "overall_status": self._get_overall_status(),
                "metrics": {},
                "alerts": {
                    "active": len([a for a in self.alerts if not a.acknowledged]),
                    "total": len(self.alerts),
                    "recent": [a for a in self.alerts[-5:]]  # Last 5 alerts
                },
                "targets_met": 0,
                "total_targets": 0
            }
            
            for name, metric in self.metrics.items():
                if metric.target:
                    summary["total_targets"] += 1
                    if metric.get_performance_level() in [PerformanceLevel.EXCELLENT, PerformanceLevel.GOOD]:
                        summary["targets_met"] += 1
                
                summary["metrics"][name] = {
                    "current": metric.current_value,
                    "average_5min": metric.get_average(300),
                    "target": metric.target.target_value if metric.target else None,
                    "status": metric.get_performance_level().value,
                    "unit": metric.target.unit if metric.target else "units"
                }
            
            return summary
    
    def _get_overall_status(self) -> PerformanceLevel:
        """Get overall system performance status."""
        if not self.metrics:
            return PerformanceLevel.GOOD
        
        levels = [metric.get_performance_level() for metric in self.metrics.values() if metric.target]
        
        if not levels:
            return PerformanceLevel.GOOD
        
        # Overall status is the worst individual status
        if PerformanceLevel.CRITICAL in levels:
            return PerformanceLevel.CRITICAL
        elif PerformanceLevel.WARNING in levels:
            return PerformanceLevel.WARNING
        elif all(level == PerformanceLevel.EXCELLENT for level in levels):
            return PerformanceLevel.EXCELLENT
        else:
            return PerformanceLevel.GOOD
    
    def add_alert_callback(self, callback: Callable[[PerformanceAlert], None]) -> None:
        """Add callback for performance alerts."""
        self.alert_callbacks.append(callback)
    
    def acknowledge_alert(self, alert_index: int) -> bool:
        """Acknowledge a performance alert."""
        with self._lock:
            if 0 <= alert_index < len(self.alerts):
                self.alerts[alert_index].acknowledged = True
                return True
            return False
    
    def clear_alerts(self) -> None:
        """Clear all alerts."""
        with self._lock:
            self.alerts.clear()
            self._last_alert_times.clear()
    
    def enable_monitoring(self, enabled: bool = True) -> None:
        """Enable or disable performance monitoring."""
        self.monitoring_enabled = enabled
        logger.info(f"Performance monitoring {'enabled' if enabled else 'disabled'}")
    
    def reset_metrics(self) -> None:
        """Reset all metrics and history."""
        with self._lock:
            for metric in self.metrics.values():
                metric.current_value = 0.0
                metric.history.clear()
            self.clear_alerts()
            logger.info("Performance metrics reset")


# Global monitor instance
_monitor_instance = None


def get_performance_monitor() -> PerformanceMonitor:
    """Get the global performance monitor instance."""
    global _monitor_instance
    if _monitor_instance is None:
        _monitor_instance = PerformanceMonitor()
    return _monitor_instance


# Convenience functions for common measurements
def record_query_performance(complexity: str, response_time: float, api_calls: int) -> None:
    """Record performance for a complete query."""
    monitor = get_performance_monitor()
    monitor.record_response_time(complexity, response_time)
    monitor.record_api_calls("query", api_calls)
