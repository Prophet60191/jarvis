"""
Plugin Usage Analytics

Tracks and analyzes plugin usage patterns, performance metrics,
and success rates to provide insights for optimization and recommendations.
"""

import time
import statistics
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from collections import defaultdict, deque
import threading
import json

logger = logging.getLogger(__name__)

@dataclass
class PerformanceProfile:
    """Performance profile for a plugin."""
    avg_execution_time: float = 0.0
    min_execution_time: float = float('inf')
    max_execution_time: float = 0.0
    memory_usage_mb: float = 0.0
    cpu_usage_percent: float = 0.0
    success_rate: float = 1.0
    error_patterns: List[str] = field(default_factory=list)
    last_updated: float = field(default_factory=time.time)

@dataclass
class UsageStats:
    """Usage statistics for a plugin."""
    total_executions: int = 0
    successful_executions: int = 0
    failed_executions: int = 0
    success_rate: float = 1.0
    average_rating: float = 0.0
    last_used: Optional[float] = None
    usage_frequency: float = 0.0  # executions per day
    common_contexts: List[str] = field(default_factory=list)
    peak_usage_hours: List[int] = field(default_factory=list)
    user_feedback_count: int = 0
    total_rating_sum: float = 0.0

@dataclass
class UsageEvent:
    """Individual usage event record."""
    plugin_name: str
    timestamp: float
    execution_time: float
    success: bool
    context: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None
    user_rating: Optional[float] = None
    memory_usage_mb: Optional[float] = None
    cpu_usage_percent: Optional[float] = None

class UsageAnalytics:
    """
    Tracks and analyzes plugin usage patterns and performance.
    
    This component provides insights into how plugins are used,
    their performance characteristics, and success patterns.
    """
    
    def __init__(self, max_events: int = 10000):
        """
        Initialize usage analytics.
        
        Args:
            max_events: Maximum number of events to keep in memory
        """
        self._usage_events: deque = deque(maxlen=max_events)
        self._plugin_stats: Dict[str, UsageStats] = {}
        self._performance_profiles: Dict[str, PerformanceProfile] = {}
        self._context_patterns: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
        self._lock = threading.RLock()
        
        # Configuration
        self.performance_window_hours = 24  # Hours to consider for performance metrics
        self.frequency_calculation_days = 7  # Days to consider for frequency calculation
        self.min_events_for_reliability = 5  # Minimum events needed for reliable stats
        
        logger.info("UsageAnalytics initialized")
    
    def record_usage(self, plugin_name: str, execution_time: float, 
                    success: bool, context: Optional[Dict[str, Any]] = None,
                    error_message: Optional[str] = None,
                    user_rating: Optional[float] = None,
                    memory_usage_mb: Optional[float] = None,
                    cpu_usage_percent: Optional[float] = None) -> None:
        """
        Record a plugin usage event.
        
        Args:
            plugin_name: Name of the plugin
            execution_time: Execution time in seconds
            success: Whether the execution was successful
            context: Optional execution context
            error_message: Optional error message if failed
            user_rating: Optional user rating (1-5 scale)
            memory_usage_mb: Optional memory usage in MB
            cpu_usage_percent: Optional CPU usage percentage
        """
        timestamp = time.time()
        
        with self._lock:
            # Create usage event
            event = UsageEvent(
                plugin_name=plugin_name,
                timestamp=timestamp,
                execution_time=execution_time,
                success=success,
                context=context or {},
                error_message=error_message,
                user_rating=user_rating,
                memory_usage_mb=memory_usage_mb,
                cpu_usage_percent=cpu_usage_percent
            )
            
            # Store event
            self._usage_events.append(event)
            
            # Update plugin statistics
            self._update_plugin_stats(event)
            
            # Update performance profile
            self._update_performance_profile(event)
            
            # Update context patterns
            self._update_context_patterns(event)
            
            logger.debug(f"Recorded usage for {plugin_name}: {execution_time:.3f}s, success={success}")
    
    def get_usage_statistics(self, plugin_name: str) -> Optional[UsageStats]:
        """
        Get usage statistics for a plugin.
        
        Args:
            plugin_name: Name of the plugin
            
        Returns:
            Optional[UsageStats]: Usage statistics or None if not found
        """
        with self._lock:
            return self._plugin_stats.get(plugin_name)
    
    def get_performance_profile(self, plugin_name: str) -> Optional[PerformanceProfile]:
        """
        Get performance profile for a plugin.
        
        Args:
            plugin_name: Name of the plugin
            
        Returns:
            Optional[PerformanceProfile]: Performance profile or None if not found
        """
        with self._lock:
            return self._performance_profiles.get(plugin_name)
    
    def get_top_plugins(self, metric: str = "usage_frequency", limit: int = 10) -> List[Tuple[str, float]]:
        """
        Get top plugins by a specific metric.
        
        Args:
            metric: Metric to sort by (usage_frequency, success_rate, average_rating)
            limit: Maximum number of plugins to return
            
        Returns:
            List[Tuple[str, float]]: List of (plugin_name, metric_value) tuples
        """
        with self._lock:
            plugin_metrics = []
            
            for plugin_name, stats in self._plugin_stats.items():
                if stats.total_executions < self.min_events_for_reliability:
                    continue
                
                if metric == "usage_frequency":
                    value = stats.usage_frequency
                elif metric == "success_rate":
                    value = stats.success_rate
                elif metric == "average_rating":
                    value = stats.average_rating
                elif metric == "total_executions":
                    value = float(stats.total_executions)
                else:
                    continue
                
                plugin_metrics.append((plugin_name, value))
            
            # Sort by metric value (descending)
            plugin_metrics.sort(key=lambda x: x[1], reverse=True)
            
            return plugin_metrics[:limit]
    
    def get_usage_trends(self, plugin_name: str, hours: int = 24) -> Dict[str, Any]:
        """
        Get usage trends for a plugin over time.
        
        Args:
            plugin_name: Name of the plugin
            hours: Number of hours to analyze
            
        Returns:
            Dict[str, Any]: Usage trend data
        """
        cutoff_time = time.time() - (hours * 3600)
        
        with self._lock:
            # Filter events for the plugin and time window
            plugin_events = [
                event for event in self._usage_events
                if event.plugin_name == plugin_name and event.timestamp >= cutoff_time
            ]
            
            if not plugin_events:
                return {"error": "No usage data found"}
            
            # Calculate hourly usage
            hourly_usage = defaultdict(int)
            hourly_success = defaultdict(int)
            hourly_avg_time = defaultdict(list)
            
            for event in plugin_events:
                hour = int((event.timestamp - cutoff_time) // 3600)
                hourly_usage[hour] += 1
                if event.success:
                    hourly_success[hour] += 1
                hourly_avg_time[hour].append(event.execution_time)
            
            # Prepare trend data
            trend_data = {
                "total_events": len(plugin_events),
                "time_window_hours": hours,
                "hourly_usage": dict(hourly_usage),
                "hourly_success_rate": {
                    hour: hourly_success[hour] / hourly_usage[hour] if hourly_usage[hour] > 0 else 0
                    for hour in hourly_usage
                },
                "hourly_avg_execution_time": {
                    hour: statistics.mean(times) if times else 0
                    for hour, times in hourly_avg_time.items()
                }
            }
            
            return trend_data
    
    def analyze_failure_patterns(self, plugin_name: str) -> Dict[str, Any]:
        """
        Analyze failure patterns for a plugin.
        
        Args:
            plugin_name: Name of the plugin
            
        Returns:
            Dict[str, Any]: Failure pattern analysis
        """
        with self._lock:
            # Get failed events for the plugin
            failed_events = [
                event for event in self._usage_events
                if event.plugin_name == plugin_name and not event.success
            ]
            
            if not failed_events:
                return {"error": "No failure data found"}
            
            # Analyze error messages
            error_patterns = defaultdict(int)
            context_patterns = defaultdict(int)
            time_patterns = defaultdict(int)
            
            for event in failed_events:
                # Error message patterns
                if event.error_message:
                    # Simple pattern extraction (first few words)
                    error_start = ' '.join(event.error_message.split()[:3])
                    error_patterns[error_start] += 1
                
                # Context patterns
                for key, value in event.context.items():
                    context_patterns[f"{key}={value}"] += 1
                
                # Time patterns (hour of day)
                hour = time.localtime(event.timestamp).tm_hour
                time_patterns[hour] += 1
            
            return {
                "total_failures": len(failed_events),
                "common_error_patterns": dict(sorted(error_patterns.items(), 
                                                   key=lambda x: x[1], reverse=True)[:5]),
                "failure_contexts": dict(sorted(context_patterns.items(),
                                              key=lambda x: x[1], reverse=True)[:5]),
                "failure_hours": dict(sorted(time_patterns.items(),
                                           key=lambda x: x[1], reverse=True)[:5])
            }
    
    def get_context_insights(self, plugin_name: str) -> Dict[str, Any]:
        """
        Get insights about plugin usage contexts.
        
        Args:
            plugin_name: Name of the plugin
            
        Returns:
            Dict[str, Any]: Context insights
        """
        with self._lock:
            if plugin_name not in self._context_patterns:
                return {"error": "No context data found"}
            
            context_data = self._context_patterns[plugin_name]
            total_contexts = sum(context_data.values())
            
            # Calculate context percentages
            context_percentages = {
                context: (count / total_contexts) * 100
                for context, count in context_data.items()
            }
            
            # Sort by frequency
            sorted_contexts = sorted(context_percentages.items(),
                                   key=lambda x: x[1], reverse=True)
            
            return {
                "total_context_observations": total_contexts,
                "most_common_contexts": sorted_contexts[:10],
                "context_diversity": len(context_data),
                "dominant_context": sorted_contexts[0] if sorted_contexts else None
            }
    
    def recommend_optimizations(self, plugin_name: str) -> List[str]:
        """
        Recommend optimizations based on usage patterns.
        
        Args:
            plugin_name: Name of the plugin
            
        Returns:
            List[str]: List of optimization recommendations
        """
        recommendations = []
        
        with self._lock:
            stats = self._plugin_stats.get(plugin_name)
            profile = self._performance_profiles.get(plugin_name)
            
            if not stats or not profile:
                return ["Insufficient data for recommendations"]
            
            # Performance recommendations
            if profile.avg_execution_time > 5.0:  # 5 seconds
                recommendations.append("Consider optimizing execution time - average is high")
            
            if profile.memory_usage_mb > 100:  # 100 MB
                recommendations.append("Consider optimizing memory usage - consumption is high")
            
            # Success rate recommendations
            if stats.success_rate < 0.9:  # Less than 90%
                recommendations.append("Improve error handling - success rate is below 90%")
            
            # Usage pattern recommendations
            if stats.usage_frequency < 0.1:  # Less than once per 10 days
                recommendations.append("Plugin is rarely used - consider deprecation or promotion")
            
            # Rating recommendations
            if stats.average_rating < 3.0 and stats.user_feedback_count > 5:
                recommendations.append("Address user feedback - average rating is low")
            
            # Context-based recommendations
            context_insights = self.get_context_insights(plugin_name)
            if not isinstance(context_insights, dict) or "error" in context_insights:
                pass  # No context data
            elif context_insights.get("context_diversity", 0) < 3:
                recommendations.append("Plugin usage is limited to few contexts - consider expanding capabilities")
        
        return recommendations if recommendations else ["Plugin performance is optimal"]
    
    def clear_plugin_data(self, plugin_name: str) -> None:
        """
        Clear all data for a plugin.
        
        Args:
            plugin_name: Name of the plugin
        """
        with self._lock:
            # Remove from stats and profiles
            self._plugin_stats.pop(plugin_name, None)
            self._performance_profiles.pop(plugin_name, None)
            self._context_patterns.pop(plugin_name, None)
            
            # Remove events (create new deque without the plugin's events)
            filtered_events = deque(
                (event for event in self._usage_events if event.plugin_name != plugin_name),
                maxlen=self._usage_events.maxlen
            )
            self._usage_events = filtered_events
            
            logger.debug(f"Cleared usage data for plugin: {plugin_name}")
    
    def export_analytics_data(self) -> Dict[str, Any]:
        """Export analytics data for persistence."""
        with self._lock:
            return {
                "plugin_stats": {
                    name: {
                        "total_executions": stats.total_executions,
                        "successful_executions": stats.successful_executions,
                        "failed_executions": stats.failed_executions,
                        "success_rate": stats.success_rate,
                        "average_rating": stats.average_rating,
                        "last_used": stats.last_used,
                        "usage_frequency": stats.usage_frequency,
                        "common_contexts": stats.common_contexts,
                        "peak_usage_hours": stats.peak_usage_hours,
                        "user_feedback_count": stats.user_feedback_count,
                        "total_rating_sum": stats.total_rating_sum
                    }
                    for name, stats in self._plugin_stats.items()
                },
                "performance_profiles": {
                    name: {
                        "avg_execution_time": profile.avg_execution_time,
                        "min_execution_time": profile.min_execution_time,
                        "max_execution_time": profile.max_execution_time,
                        "memory_usage_mb": profile.memory_usage_mb,
                        "cpu_usage_percent": profile.cpu_usage_percent,
                        "success_rate": profile.success_rate,
                        "error_patterns": profile.error_patterns,
                        "last_updated": profile.last_updated
                    }
                    for name, profile in self._performance_profiles.items()
                },
                "context_patterns": dict(self._context_patterns)
            }
    
    def load_analytics_data(self, data: Dict[str, Any]) -> None:
        """Load analytics data from persistence."""
        with self._lock:
            # Load plugin stats
            for name, stats_data in data.get("plugin_stats", {}).items():
                self._plugin_stats[name] = UsageStats(**stats_data)
            
            # Load performance profiles
            for name, profile_data in data.get("performance_profiles", {}).items():
                self._performance_profiles[name] = PerformanceProfile(**profile_data)
            
            # Load context patterns
            context_data = data.get("context_patterns", {})
            for plugin_name, patterns in context_data.items():
                self._context_patterns[plugin_name] = defaultdict(int, patterns)
    
    def _update_plugin_stats(self, event: UsageEvent) -> None:
        """Update plugin statistics with new event."""
        plugin_name = event.plugin_name
        
        if plugin_name not in self._plugin_stats:
            self._plugin_stats[plugin_name] = UsageStats()
        
        stats = self._plugin_stats[plugin_name]
        
        # Update counters
        stats.total_executions += 1
        if event.success:
            stats.successful_executions += 1
        else:
            stats.failed_executions += 1
        
        # Update success rate
        stats.success_rate = stats.successful_executions / stats.total_executions
        
        # Update last used
        stats.last_used = event.timestamp
        
        # Update usage frequency (executions per day)
        if stats.total_executions > 1:
            # Calculate time span and frequency
            oldest_event_time = min(e.timestamp for e in self._usage_events if e.plugin_name == plugin_name)
            time_span_days = (event.timestamp - oldest_event_time) / (24 * 3600)
            if time_span_days > 0:
                stats.usage_frequency = stats.total_executions / time_span_days
        
        # Update rating
        if event.user_rating is not None:
            stats.user_feedback_count += 1
            stats.total_rating_sum += event.user_rating
            stats.average_rating = stats.total_rating_sum / stats.user_feedback_count
        
        # Update peak usage hours
        hour = time.localtime(event.timestamp).tm_hour
        if hour not in stats.peak_usage_hours:
            # Simple approach: track hours with usage
            stats.peak_usage_hours.append(hour)
            # Keep only top 5 hours (this is simplified)
            if len(stats.peak_usage_hours) > 5:
                stats.peak_usage_hours = stats.peak_usage_hours[-5:]
    
    def _update_performance_profile(self, event: UsageEvent) -> None:
        """Update performance profile with new event."""
        plugin_name = event.plugin_name
        
        if plugin_name not in self._performance_profiles:
            self._performance_profiles[plugin_name] = PerformanceProfile()
        
        profile = self._performance_profiles[plugin_name]
        
        # Update execution time statistics
        if profile.avg_execution_time == 0.0:
            profile.avg_execution_time = event.execution_time
        else:
            # Running average
            total_events = self._plugin_stats[plugin_name].total_executions
            profile.avg_execution_time = (
                (profile.avg_execution_time * (total_events - 1) + event.execution_time) / total_events
            )
        
        profile.min_execution_time = min(profile.min_execution_time, event.execution_time)
        profile.max_execution_time = max(profile.max_execution_time, event.execution_time)
        
        # Update resource usage if provided
        if event.memory_usage_mb is not None:
            profile.memory_usage_mb = event.memory_usage_mb
        
        if event.cpu_usage_percent is not None:
            profile.cpu_usage_percent = event.cpu_usage_percent
        
        # Update success rate
        profile.success_rate = self._plugin_stats[plugin_name].success_rate
        
        # Update error patterns
        if not event.success and event.error_message:
            error_pattern = event.error_message.split(':')[0]  # First part of error
            if error_pattern not in profile.error_patterns:
                profile.error_patterns.append(error_pattern)
                # Keep only recent error patterns
                if len(profile.error_patterns) > 10:
                    profile.error_patterns = profile.error_patterns[-10:]
        
        profile.last_updated = event.timestamp
    
    def _update_context_patterns(self, event: UsageEvent) -> None:
        """Update context patterns with new event."""
        plugin_name = event.plugin_name
        
        for key, value in event.context.items():
            context_key = f"{key}={value}"
            self._context_patterns[plugin_name][context_key] += 1
