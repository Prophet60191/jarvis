"""
Performance Service Layer - Clean abstraction for performance monitoring.

This service provides a unified interface for performance tracking and
optimization, following proper separation of concerns.
"""

import logging
import time
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class PerformanceLevel(Enum):
    """Performance levels for monitoring."""
    EXCELLENT = "excellent"
    GOOD = "good"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class PerformanceMetrics:
    """Performance metrics data."""
    response_time_ms: float
    level: PerformanceLevel
    suggestions: List[str]
    component_stats: Dict[str, Any]


class PerformanceService(ABC):
    """Abstract interface for performance operations."""
    
    @abstractmethod
    def start_query_tracking(self, query: str, complexity: str) -> str:
        """Start tracking a query's performance."""
        pass
    
    @abstractmethod
    def end_query_tracking(self, tracking_id: str) -> PerformanceMetrics:
        """End tracking and get performance metrics."""
        pass
    
    @abstractmethod
    def record_component_performance(self, component: str, duration_ms: float) -> None:
        """Record performance for a specific component."""
        pass
    
    @abstractmethod
    def get_session_summary(self) -> Dict[str, Any]:
        """Get performance summary for current session."""
        pass


class JarvisPerformanceService(PerformanceService):
    """
    Concrete implementation of performance service using existing
    performance monitoring systems.
    
    This maintains backward compatibility while providing clean abstraction.
    """
    
    def __init__(self):
        """Initialize performance service with lazy loading."""
        self._performance_manager = None
        self._performance_monitor = None
        self._initialized = False
        self._active_queries = {}
        
        logger.info("JarvisPerformanceService initialized with lazy loading")
    
    def _ensure_initialized(self):
        """Ensure performance managers are initialized (lazy loading)."""
        if self._initialized:
            return
        
        try:
            from .performance_monitoring_manager import get_performance_monitoring_manager
            from .performance_monitor import get_performance_monitor
            
            self._performance_manager = get_performance_monitoring_manager()
            self._performance_monitor = get_performance_monitor()
            
            self._initialized = True
            logger.info("Performance managers initialized successfully in performance service")
            
        except Exception as e:
            logger.error(f"Failed to initialize performance managers: {e}")
            # Continue without performance monitoring
            self._initialized = True
    
    def start_query_tracking(self, query: str, complexity: str) -> str:
        """Start tracking a query's performance."""
        try:
            self._ensure_initialized()
            
            tracking_id = f"query_{int(time.time() * 1000)}"
            start_time = time.time()
            
            self._active_queries[tracking_id] = {
                "query": query,
                "complexity": complexity,
                "start_time": start_time
            }
            
            # Use existing performance monitor if available
            if self._performance_monitor and hasattr(self._performance_monitor, 'start_query'):
                self._performance_monitor.start_query(tracking_id, query, complexity)
            
            return tracking_id
            
        except Exception as e:
            logger.error(f"Failed to start query tracking: {e}")
            return "error_tracking_id"
    
    def end_query_tracking(self, tracking_id: str) -> PerformanceMetrics:
        """End tracking and get performance metrics."""
        try:
            self._ensure_initialized()
            
            if tracking_id not in self._active_queries:
                return PerformanceMetrics(
                    response_time_ms=0.0,
                    level=PerformanceLevel.WARNING,
                    suggestions=["Query tracking not found"],
                    component_stats={}
                )
            
            query_info = self._active_queries.pop(tracking_id)
            end_time = time.time()
            duration_ms = (end_time - query_info["start_time"]) * 1000
            
            # Determine performance level
            if duration_ms < 500:
                level = PerformanceLevel.EXCELLENT
                suggestions = []
            elif duration_ms < 1000:
                level = PerformanceLevel.GOOD
                suggestions = []
            elif duration_ms < 3000:
                level = PerformanceLevel.WARNING
                suggestions = ["Consider query optimization", "Check tool selection"]
            else:
                level = PerformanceLevel.CRITICAL
                suggestions = ["Enable tool selection optimization", "Implement query streaming"]
            
            # Get component stats if available
            component_stats = {}
            if self._performance_manager and hasattr(self._performance_manager, 'get_component_stats'):
                try:
                    component_stats = self._performance_manager.get_component_stats()
                except Exception as e:
                    logger.warning(f"Failed to get component stats: {e}")
            
            # Record with existing performance monitor
            if self._performance_monitor and hasattr(self._performance_monitor, 'record_query_performance'):
                self._performance_monitor.record_query_performance(
                    query_info["query"], 
                    query_info["complexity"], 
                    duration_ms
                )
            
            return PerformanceMetrics(
                response_time_ms=duration_ms,
                level=level,
                suggestions=suggestions,
                component_stats=component_stats
            )
            
        except Exception as e:
            logger.error(f"Failed to end query tracking: {e}")
            return PerformanceMetrics(
                response_time_ms=0.0,
                level=PerformanceLevel.WARNING,
                suggestions=[f"Performance tracking error: {str(e)}"],
                component_stats={}
            )
    
    def record_component_performance(self, component: str, duration_ms: float) -> None:
        """Record performance for a specific component."""
        try:
            self._ensure_initialized()
            
            if self._performance_manager and hasattr(self._performance_manager, 'record_component_performance'):
                self._performance_manager.record_component_performance(component, duration_ms)
            
        except Exception as e:
            logger.error(f"Failed to record component performance: {e}")
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Get performance summary for current session."""
        try:
            self._ensure_initialized()
            
            if self._performance_manager and hasattr(self._performance_manager, 'get_session_performance_summary'):
                return self._performance_manager.get_session_performance_summary()
            else:
                return {
                    "active_queries": len(self._active_queries),
                    "status": "basic_tracking"
                }
                
        except Exception as e:
            logger.error(f"Failed to get session summary: {e}")
            return {"error": str(e)}


# Factory function for dependency injection
_performance_service_instance = None

def get_performance_service() -> PerformanceService:
    """Get the performance service instance (singleton)."""
    global _performance_service_instance
    if _performance_service_instance is None:
        _performance_service_instance = JarvisPerformanceService()
    return _performance_service_instance
