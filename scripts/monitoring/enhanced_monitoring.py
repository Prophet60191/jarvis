#!/usr/bin/env python3
"""
Enhanced Monitoring System for Jarvis System Integration

This module provides comprehensive monitoring and analytics for:
- Enhanced Plugin Registry performance
- Context Management system metrics
- Smart Tool Orchestration analytics
- Source Code Consciousness usage
- System resource utilization
- Performance regression detection
"""

import time
import psutil
import logging
import json
import threading
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from collections import defaultdict, deque
import statistics

logger = logging.getLogger(__name__)

@dataclass
class MetricPoint:
    """Single metric data point."""
    timestamp: float
    value: float
    tags: Dict[str, str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = {}

@dataclass
class SystemMetrics:
    """System resource metrics."""
    timestamp: float
    cpu_percent: float
    memory_mb: float
    memory_percent: float
    disk_usage_percent: float
    network_bytes_sent: int
    network_bytes_recv: int

@dataclass
class PerformanceMetrics:
    """Performance metrics for enhanced features."""
    timestamp: float
    component: str
    operation: str
    duration_ms: float
    success: bool
    error_message: Optional[str] = None
    context: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.context is None:
            self.context = {}

class MetricsCollector:
    """Collects and stores metrics from various system components."""
    
    def __init__(self, max_points: int = 10000):
        self.max_points = max_points
        self.metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=max_points))
        self.performance_metrics: deque = deque(maxlen=max_points)
        self.system_metrics: deque = deque(maxlen=max_points)
        self._lock = threading.Lock()
        
        # Performance thresholds
        self.thresholds = {
            'registry_query_ms': 50.0,
            'context_retrieval_ms': 20.0,
            'orchestration_decision_ms': 150.0,
            'code_query_ms': 500.0,
            'memory_usage_mb': 1000.0,
            'cpu_usage_percent': 80.0
        }
        
        # Alert callbacks
        self.alert_callbacks: List[Callable] = []
    
    def record_metric(self, name: str, value: float, tags: Dict[str, str] = None) -> None:
        """Record a generic metric."""
        with self._lock:
            metric_point = MetricPoint(
                timestamp=time.time(),
                value=value,
                tags=tags or {}
            )
            self.metrics[name].append(metric_point)
    
    def record_performance_metric(self, 
                                component: str, 
                                operation: str, 
                                duration_ms: float,
                                success: bool = True,
                                error_message: str = None,
                                context: Dict[str, Any] = None) -> None:
        """Record a performance metric."""
        with self._lock:
            perf_metric = PerformanceMetrics(
                timestamp=time.time(),
                component=component,
                operation=operation,
                duration_ms=duration_ms,
                success=success,
                error_message=error_message,
                context=context or {}
            )
            self.performance_metrics.append(perf_metric)
            
            # Check thresholds and trigger alerts
            self._check_performance_threshold(perf_metric)
    
    def record_system_metrics(self) -> None:
        """Record current system resource metrics."""
        try:
            # Get system metrics
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            network = psutil.net_io_counters()
            
            with self._lock:
                sys_metric = SystemMetrics(
                    timestamp=time.time(),
                    cpu_percent=cpu_percent,
                    memory_mb=memory.used / 1024 / 1024,
                    memory_percent=memory.percent,
                    disk_usage_percent=disk.percent,
                    network_bytes_sent=network.bytes_sent,
                    network_bytes_recv=network.bytes_recv
                )
                self.system_metrics.append(sys_metric)
                
                # Check system thresholds
                self._check_system_thresholds(sys_metric)
                
        except Exception as e:
            logger.error(f"Failed to collect system metrics: {e}")
    
    def _check_performance_threshold(self, metric: PerformanceMetrics) -> None:
        """Check if performance metric exceeds threshold."""
        threshold_key = f"{metric.component.lower()}_{metric.operation.lower()}_ms"
        threshold = self.thresholds.get(threshold_key)
        
        if threshold and metric.duration_ms > threshold:
            alert = {
                'type': 'performance_threshold_exceeded',
                'component': metric.component,
                'operation': metric.operation,
                'duration_ms': metric.duration_ms,
                'threshold_ms': threshold,
                'timestamp': metric.timestamp
            }
            self._trigger_alert(alert)
    
    def _check_system_thresholds(self, metric: SystemMetrics) -> None:
        """Check if system metrics exceed thresholds."""
        alerts = []
        
        if metric.memory_mb > self.thresholds['memory_usage_mb']:
            alerts.append({
                'type': 'high_memory_usage',
                'value': metric.memory_mb,
                'threshold': self.thresholds['memory_usage_mb'],
                'timestamp': metric.timestamp
            })
        
        if metric.cpu_percent > self.thresholds['cpu_usage_percent']:
            alerts.append({
                'type': 'high_cpu_usage',
                'value': metric.cpu_percent,
                'threshold': self.thresholds['cpu_usage_percent'],
                'timestamp': metric.timestamp
            })
        
        for alert in alerts:
            self._trigger_alert(alert)
    
    def _trigger_alert(self, alert: Dict[str, Any]) -> None:
        """Trigger alert callbacks."""
        for callback in self.alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                logger.error(f"Alert callback failed: {e}")
    
    def add_alert_callback(self, callback: Callable[[Dict[str, Any]], None]) -> None:
        """Add an alert callback function."""
        self.alert_callbacks.append(callback)
    
    def get_metrics_summary(self, component: str = None, 
                          time_window_minutes: int = 60) -> Dict[str, Any]:
        """Get summary statistics for metrics."""
        cutoff_time = time.time() - (time_window_minutes * 60)
        
        with self._lock:
            # Filter performance metrics
            if component:
                perf_metrics = [m for m in self.performance_metrics 
                              if m.component == component and m.timestamp >= cutoff_time]
            else:
                perf_metrics = [m for m in self.performance_metrics 
                              if m.timestamp >= cutoff_time]
            
            # Calculate statistics
            if perf_metrics:
                durations = [m.duration_ms for m in perf_metrics]
                success_count = sum(1 for m in perf_metrics if m.success)
                
                summary = {
                    'total_operations': len(perf_metrics),
                    'successful_operations': success_count,
                    'success_rate': success_count / len(perf_metrics),
                    'mean_duration_ms': statistics.mean(durations),
                    'median_duration_ms': statistics.median(durations),
                    'p95_duration_ms': sorted(durations)[int(len(durations) * 0.95)] if durations else 0,
                    'min_duration_ms': min(durations),
                    'max_duration_ms': max(durations),
                    'time_window_minutes': time_window_minutes
                }
            else:
                summary = {
                    'total_operations': 0,
                    'successful_operations': 0,
                    'success_rate': 0.0,
                    'mean_duration_ms': 0.0,
                    'median_duration_ms': 0.0,
                    'p95_duration_ms': 0.0,
                    'min_duration_ms': 0.0,
                    'max_duration_ms': 0.0,
                    'time_window_minutes': time_window_minutes
                }
            
            return summary
    
    def export_metrics(self, filepath: Path, time_window_hours: int = 24) -> None:
        """Export metrics to JSON file."""
        cutoff_time = time.time() - (time_window_hours * 3600)
        
        with self._lock:
            # Filter metrics by time window
            filtered_performance = [
                asdict(m) for m in self.performance_metrics 
                if m.timestamp >= cutoff_time
            ]
            
            filtered_system = [
                asdict(m) for m in self.system_metrics 
                if m.timestamp >= cutoff_time
            ]
            
            filtered_generic = {}
            for name, metrics in self.metrics.items():
                filtered_generic[name] = [
                    asdict(m) for m in metrics 
                    if m.timestamp >= cutoff_time
                ]
            
            export_data = {
                'export_timestamp': time.time(),
                'time_window_hours': time_window_hours,
                'performance_metrics': filtered_performance,
                'system_metrics': filtered_system,
                'generic_metrics': filtered_generic,
                'thresholds': self.thresholds
            }
        
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        logger.info(f"Metrics exported to {filepath}")

class PerformanceMonitor:
    """Context manager for monitoring performance of code blocks."""
    
    def __init__(self, collector: MetricsCollector, component: str, operation: str):
        self.collector = collector
        self.component = component
        self.operation = operation
        self.start_time = None
        self.context = {}
    
    def __enter__(self):
        self.start_time = time.perf_counter()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        end_time = time.perf_counter()
        duration_ms = (end_time - self.start_time) * 1000
        
        success = exc_type is None
        error_message = str(exc_val) if exc_val else None
        
        self.collector.record_performance_metric(
            component=self.component,
            operation=self.operation,
            duration_ms=duration_ms,
            success=success,
            error_message=error_message,
            context=self.context
        )
    
    def add_context(self, key: str, value: Any) -> None:
        """Add context information to the performance metric."""
        self.context[key] = value

class EnhancedMonitoringSystem:
    """Main monitoring system for enhanced Jarvis features."""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.collector = MetricsCollector()
        self.monitoring_thread = None
        self.running = False
        
        # Set up default alert handlers
        self.collector.add_alert_callback(self._log_alert)
        
        # Configure monitoring intervals
        self.system_metrics_interval = self.config.get('system_metrics_interval', 30)  # seconds
        self.export_interval = self.config.get('export_interval', 3600)  # 1 hour
        
        # Export directory
        self.export_dir = Path(self.config.get('export_dir', 'data/monitoring'))
        self.export_dir.mkdir(parents=True, exist_ok=True)
    
    def start_monitoring(self) -> None:
        """Start the monitoring system."""
        if self.running:
            logger.warning("Monitoring system is already running")
            return
        
        self.running = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        
        logger.info("Enhanced monitoring system started")
    
    def stop_monitoring(self) -> None:
        """Stop the monitoring system."""
        self.running = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        
        logger.info("Enhanced monitoring system stopped")
    
    def _monitoring_loop(self) -> None:
        """Main monitoring loop."""
        last_export = time.time()
        
        while self.running:
            try:
                # Collect system metrics
                self.collector.record_system_metrics()
                
                # Export metrics periodically
                if time.time() - last_export >= self.export_interval:
                    self._export_metrics()
                    last_export = time.time()
                
                time.sleep(self.system_metrics_interval)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(5)  # Brief pause before retrying
    
    def _export_metrics(self) -> None:
        """Export metrics to file."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        export_file = self.export_dir / f"metrics_{timestamp}.json"
        
        try:
            self.collector.export_metrics(export_file)
        except Exception as e:
            logger.error(f"Failed to export metrics: {e}")
    
    def _log_alert(self, alert: Dict[str, Any]) -> None:
        """Default alert handler that logs alerts."""
        alert_type = alert.get('type', 'unknown')
        timestamp = datetime.fromtimestamp(alert.get('timestamp', time.time()))
        
        if alert_type == 'performance_threshold_exceeded':
            logger.warning(
                f"Performance threshold exceeded: {alert['component']}.{alert['operation']} "
                f"took {alert['duration_ms']:.1f}ms (threshold: {alert['threshold_ms']:.1f}ms) "
                f"at {timestamp}"
            )
        elif alert_type == 'high_memory_usage':
            logger.warning(
                f"High memory usage: {alert['value']:.1f}MB "
                f"(threshold: {alert['threshold']:.1f}MB) at {timestamp}"
            )
        elif alert_type == 'high_cpu_usage':
            logger.warning(
                f"High CPU usage: {alert['value']:.1f}% "
                f"(threshold: {alert['threshold']:.1f}%) at {timestamp}"
            )
        else:
            logger.warning(f"Alert: {alert}")
    
    def monitor_performance(self, component: str, operation: str) -> PerformanceMonitor:
        """Create a performance monitor context manager."""
        return PerformanceMonitor(self.collector, component, operation)
    
    def record_metric(self, name: str, value: float, tags: Dict[str, str] = None) -> None:
        """Record a custom metric."""
        self.collector.record_metric(name, value, tags)
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get data for monitoring dashboard."""
        # Get summaries for different components
        registry_summary = self.collector.get_metrics_summary('PluginRegistry')
        context_summary = self.collector.get_metrics_summary('ContextManager')
        orchestration_summary = self.collector.get_metrics_summary('Orchestrator')
        consciousness_summary = self.collector.get_metrics_summary('CodeConsciousness')
        
        # Get recent system metrics
        recent_system_metrics = []
        cutoff_time = time.time() - 3600  # Last hour
        
        with self.collector._lock:
            recent_system_metrics = [
                asdict(m) for m in self.collector.system_metrics 
                if m.timestamp >= cutoff_time
            ]
        
        return {
            'timestamp': time.time(),
            'component_summaries': {
                'plugin_registry': registry_summary,
                'context_manager': context_summary,
                'orchestrator': orchestration_summary,
                'code_consciousness': consciousness_summary
            },
            'system_metrics': recent_system_metrics,
            'thresholds': self.collector.thresholds
        }
    
    def generate_health_report(self) -> Dict[str, Any]:
        """Generate a comprehensive health report."""
        dashboard_data = self.get_dashboard_data()
        
        # Analyze health status
        health_status = 'healthy'
        issues = []
        
        for component, summary in dashboard_data['component_summaries'].items():
            if summary['success_rate'] < 0.95:  # Less than 95% success rate
                health_status = 'degraded'
                issues.append(f"{component} has low success rate: {summary['success_rate']:.1%}")
            
            # Check if any operations are consistently slow
            if summary['p95_duration_ms'] > 0:
                threshold_key = f"{component.lower()}_ms"
                threshold = self.collector.thresholds.get(threshold_key, float('inf'))
                
                if summary['p95_duration_ms'] > threshold * 1.5:  # 50% above threshold
                    health_status = 'degraded'
                    issues.append(f"{component} P95 latency is high: {summary['p95_duration_ms']:.1f}ms")
        
        # Check system resources
        if dashboard_data['system_metrics']:
            latest_system = dashboard_data['system_metrics'][-1]
            
            if latest_system['memory_percent'] > 85:
                health_status = 'critical' if latest_system['memory_percent'] > 95 else 'degraded'
                issues.append(f"High memory usage: {latest_system['memory_percent']:.1f}%")
            
            if latest_system['cpu_percent'] > 80:
                health_status = 'critical' if latest_system['cpu_percent'] > 95 else 'degraded'
                issues.append(f"High CPU usage: {latest_system['cpu_percent']:.1f}%")
        
        return {
            'timestamp': time.time(),
            'health_status': health_status,
            'issues': issues,
            'summary': dashboard_data
        }

# Global monitoring system instance
monitoring_system = EnhancedMonitoringSystem()

# Convenience functions
def start_monitoring(config: Dict[str, Any] = None) -> None:
    """Start the global monitoring system."""
    if config:
        global monitoring_system
        monitoring_system = EnhancedMonitoringSystem(config)
    monitoring_system.start_monitoring()

def stop_monitoring() -> None:
    """Stop the global monitoring system."""
    monitoring_system.stop_monitoring()

def monitor_performance(component: str, operation: str) -> PerformanceMonitor:
    """Create a performance monitor for the global system."""
    return monitoring_system.monitor_performance(component, operation)

def record_metric(name: str, value: float, tags: Dict[str, str] = None) -> None:
    """Record a metric in the global system."""
    monitoring_system.record_metric(name, value, tags)

# Export monitoring utilities
__all__ = [
    "EnhancedMonitoringSystem",
    "PerformanceMonitor", 
    "MetricsCollector",
    "monitoring_system",
    "start_monitoring",
    "stop_monitoring",
    "monitor_performance",
    "record_metric"
]
