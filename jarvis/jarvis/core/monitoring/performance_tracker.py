"""
Performance Monitoring System

Tracks system performance metrics, resource usage, and provides
real-time monitoring capabilities for the enhanced Jarvis system.
"""

import time
import threading
import psutil
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from collections import deque, defaultdict
import logging

logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetric:
    """Individual performance metric."""
    name: str
    value: float
    timestamp: float
    unit: str = ""
    category: str = "general"
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SystemResourceMetrics:
    """System resource usage metrics."""
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    memory_available_mb: float
    disk_usage_percent: float
    network_io_bytes: int
    timestamp: float = field(default_factory=time.time)

@dataclass
class OperationMetrics:
    """Metrics for specific operations."""
    operation_name: str
    execution_time_ms: float
    success: bool
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)

class PerformanceTracker:
    """
    Comprehensive performance tracking system.
    
    Features:
    - Real-time metric collection
    - Resource usage monitoring
    - Operation timing
    - Performance alerts
    - Historical data retention
    """
    
    def __init__(self, history_size: int = 1000, alert_thresholds: Dict[str, float] = None):
        """
        Initialize performance tracker.
        
        Args:
            history_size: Number of historical metrics to retain
            alert_thresholds: Performance alert thresholds
        """
        self.history_size = history_size
        self.alert_thresholds = alert_thresholds or {
            'cpu_percent': 80.0,
            'memory_percent': 85.0,
            'response_time_ms': 1000.0,
            'error_rate_percent': 5.0
        }
        
        # Metric storage
        self._metrics_history: deque = deque(maxlen=history_size)
        self._operation_metrics: deque = deque(maxlen=history_size)
        self._resource_metrics: deque = deque(maxlen=history_size)
        
        # Real-time tracking
        self._current_operations: Dict[str, float] = {}
        self._operation_counts: defaultdict = defaultdict(int)
        self._operation_times: defaultdict = defaultdict(list)
        self._error_counts: defaultdict = defaultdict(int)
        
        # Threading
        self._lock = threading.RLock()
        self._monitoring_active = False
        self._monitor_thread: Optional[threading.Thread] = None
        
        # Alert callbacks
        self._alert_callbacks: List[Callable] = []
        
        logger.info("PerformanceTracker initialized")
    
    def start_monitoring(self, interval_seconds: float = 5.0) -> None:
        """
        Start continuous performance monitoring.
        
        Args:
            interval_seconds: Monitoring interval in seconds
        """
        if self._monitoring_active:
            logger.warning("Performance monitoring already active")
            return
        
        self._monitoring_active = True
        self._monitor_thread = threading.Thread(
            target=self._monitor_loop,
            args=(interval_seconds,),
            daemon=True
        )
        self._monitor_thread.start()
        logger.info(f"Performance monitoring started (interval: {interval_seconds}s)")
    
    def stop_monitoring(self) -> None:
        """Stop continuous performance monitoring."""
        self._monitoring_active = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=1.0)
        logger.info("Performance monitoring stopped")
    
    def start_operation(self, operation_name: str) -> str:
        """
        Start timing an operation.
        
        Args:
            operation_name: Name of the operation
            
        Returns:
            Operation ID for tracking
        """
        operation_id = f"{operation_name}_{int(time.time() * 1000000)}"
        
        with self._lock:
            self._current_operations[operation_id] = time.time()
            self._operation_counts[operation_name] += 1
        
        return operation_id
    
    def end_operation(self, operation_id: str, success: bool = True, 
                     error_message: Optional[str] = None,
                     metadata: Dict[str, Any] = None) -> float:
        """
        End timing an operation.
        
        Args:
            operation_id: Operation ID from start_operation
            success: Whether operation succeeded
            error_message: Error message if failed
            metadata: Additional metadata
            
        Returns:
            Execution time in milliseconds
        """
        end_time = time.time()
        
        with self._lock:
            if operation_id not in self._current_operations:
                logger.warning(f"Unknown operation ID: {operation_id}")
                return 0.0
            
            start_time = self._current_operations.pop(operation_id)
            execution_time_ms = (end_time - start_time) * 1000
            
            # Extract operation name from ID
            operation_name = operation_id.rsplit('_', 1)[0]
            
            # Record metrics
            operation_metric = OperationMetrics(
                operation_name=operation_name,
                execution_time_ms=execution_time_ms,
                success=success,
                error_message=error_message,
                metadata=metadata or {},
                timestamp=end_time
            )
            
            self._operation_metrics.append(operation_metric)
            self._operation_times[operation_name].append(execution_time_ms)
            
            # Keep only recent times for each operation
            if len(self._operation_times[operation_name]) > 100:
                self._operation_times[operation_name] = self._operation_times[operation_name][-50:]
            
            if not success:
                self._error_counts[operation_name] += 1
            
            # Check for performance alerts
            self._check_performance_alerts(operation_name, execution_time_ms, success)
            
            logger.debug(f"Operation {operation_name} completed in {execution_time_ms:.2f}ms")
            return execution_time_ms
    
    def record_metric(self, name: str, value: float, unit: str = "", 
                     category: str = "general", metadata: Dict[str, Any] = None) -> None:
        """
        Record a custom performance metric.
        
        Args:
            name: Metric name
            value: Metric value
            unit: Unit of measurement
            category: Metric category
            metadata: Additional metadata
        """
        metric = PerformanceMetric(
            name=name,
            value=value,
            timestamp=time.time(),
            unit=unit,
            category=category,
            metadata=metadata or {}
        )
        
        with self._lock:
            self._metrics_history.append(metric)
        
        logger.debug(f"Recorded metric: {name} = {value} {unit}")
    
    def get_operation_stats(self, operation_name: str) -> Dict[str, Any]:
        """
        Get statistics for a specific operation.
        
        Args:
            operation_name: Name of the operation
            
        Returns:
            Operation statistics
        """
        with self._lock:
            times = self._operation_times.get(operation_name, [])
            total_count = self._operation_counts.get(operation_name, 0)
            error_count = self._error_counts.get(operation_name, 0)
            
            if not times:
                return {
                    'operation_name': operation_name,
                    'total_executions': total_count,
                    'error_count': error_count,
                    'success_rate': 0.0,
                    'avg_time_ms': 0.0,
                    'min_time_ms': 0.0,
                    'max_time_ms': 0.0,
                    'p95_time_ms': 0.0
                }
            
            success_rate = ((total_count - error_count) / total_count * 100) if total_count > 0 else 0.0
            avg_time = sum(times) / len(times)
            min_time = min(times)
            max_time = max(times)
            
            # Calculate 95th percentile
            sorted_times = sorted(times)
            p95_index = int(len(sorted_times) * 0.95)
            p95_time = sorted_times[p95_index] if sorted_times else 0.0
            
            return {
                'operation_name': operation_name,
                'total_executions': total_count,
                'error_count': error_count,
                'success_rate': success_rate,
                'avg_time_ms': avg_time,
                'min_time_ms': min_time,
                'max_time_ms': max_time,
                'p95_time_ms': p95_time
            }
    
    def get_system_metrics(self) -> SystemResourceMetrics:
        """Get current system resource metrics."""
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            network = psutil.net_io_counters()
            
            return SystemResourceMetrics(
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                memory_used_mb=memory.used / (1024 * 1024),
                memory_available_mb=memory.available / (1024 * 1024),
                disk_usage_percent=disk.percent,
                network_io_bytes=network.bytes_sent + network.bytes_recv
            )
        except Exception as e:
            logger.error(f"Failed to get system metrics: {e}")
            return SystemResourceMetrics(0, 0, 0, 0, 0, 0)
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary."""
        with self._lock:
            # System metrics
            system_metrics = self.get_system_metrics()
            
            # Operation summaries
            operation_summaries = {}
            for op_name in self._operation_counts.keys():
                operation_summaries[op_name] = self.get_operation_stats(op_name)
            
            # Recent metrics
            recent_metrics = list(self._metrics_history)[-50:]  # Last 50 metrics
            
            return {
                'timestamp': time.time(),
                'system_resources': system_metrics,
                'operations': operation_summaries,
                'recent_metrics': recent_metrics,
                'active_operations': len(self._current_operations),
                'total_operations': sum(self._operation_counts.values()),
                'total_errors': sum(self._error_counts.values())
            }
    
    def add_alert_callback(self, callback: Callable[[str, Dict[str, Any]], None]) -> None:
        """
        Add callback for performance alerts.
        
        Args:
            callback: Function to call when alert is triggered
        """
        self._alert_callbacks.append(callback)
    
    def _monitor_loop(self, interval_seconds: float) -> None:
        """Main monitoring loop."""
        while self._monitoring_active:
            try:
                # Collect system metrics
                system_metrics = self.get_system_metrics()
                
                with self._lock:
                    self._resource_metrics.append(system_metrics)
                
                # Check system resource alerts
                self._check_system_alerts(system_metrics)
                
                time.sleep(interval_seconds)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(interval_seconds)
    
    def _check_performance_alerts(self, operation_name: str, execution_time_ms: float, success: bool) -> None:
        """Check for performance alerts on operations."""
        # Check response time alert
        if execution_time_ms > self.alert_thresholds.get('response_time_ms', 1000.0):
            self._trigger_alert(
                'high_response_time',
                {
                    'operation': operation_name,
                    'execution_time_ms': execution_time_ms,
                    'threshold': self.alert_thresholds['response_time_ms']
                }
            )
        
        # Check error rate alert
        if not success:
            total_ops = self._operation_counts.get(operation_name, 0)
            error_ops = self._error_counts.get(operation_name, 0)
            error_rate = (error_ops / total_ops * 100) if total_ops > 0 else 0
            
            if error_rate > self.alert_thresholds.get('error_rate_percent', 5.0):
                self._trigger_alert(
                    'high_error_rate',
                    {
                        'operation': operation_name,
                        'error_rate': error_rate,
                        'threshold': self.alert_thresholds['error_rate_percent']
                    }
                )
    
    def _check_system_alerts(self, metrics: SystemResourceMetrics) -> None:
        """Check for system resource alerts."""
        if metrics.cpu_percent > self.alert_thresholds.get('cpu_percent', 80.0):
            self._trigger_alert(
                'high_cpu_usage',
                {
                    'cpu_percent': metrics.cpu_percent,
                    'threshold': self.alert_thresholds['cpu_percent']
                }
            )
        
        if metrics.memory_percent > self.alert_thresholds.get('memory_percent', 85.0):
            self._trigger_alert(
                'high_memory_usage',
                {
                    'memory_percent': metrics.memory_percent,
                    'threshold': self.alert_thresholds['memory_percent']
                }
            )
    
    def _trigger_alert(self, alert_type: str, data: Dict[str, Any]) -> None:
        """Trigger performance alert."""
        logger.warning(f"Performance alert: {alert_type} - {data}")
        
        for callback in self._alert_callbacks:
            try:
                callback(alert_type, data)
            except Exception as e:
                logger.error(f"Error in alert callback: {e}")

# Global performance tracker instance
performance_tracker = PerformanceTracker()

def track_operation(operation_name: str):
    """Decorator for tracking operation performance."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            op_id = performance_tracker.start_operation(operation_name)
            try:
                result = func(*args, **kwargs)
                performance_tracker.end_operation(op_id, success=True)
                return result
            except Exception as e:
                performance_tracker.end_operation(op_id, success=False, error_message=str(e))
                raise
        return wrapper
    return decorator
