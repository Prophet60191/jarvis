"""
Performance Optimization for Jarvis Voice Assistant TTS.

This module provides performance optimization features including audio caching,
model optimization, memory management, and efficient resource utilization
for faster TTS response times.
"""

import logging
import hashlib
import pickle
import time
import threading
from typing import Dict, Any, Optional, Tuple, List
from dataclasses import dataclass
from pathlib import Path
from collections import OrderedDict
import gc

try:
    import numpy as np
    import torch
except ImportError:
    np = None
    torch = None

from ..exceptions import TextToSpeechError


logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    """Cache entry for TTS audio."""
    audio_data: Any
    sample_rate: int
    timestamp: float
    access_count: int
    size_bytes: int
    voice_profile_id: str
    language: str


@dataclass
class PerformanceMetrics:
    """Performance metrics for TTS operations."""
    cache_hit_rate: float
    average_generation_time: float
    memory_usage_mb: float
    model_load_time: float
    total_requests: int
    cache_size_mb: float


@dataclass
class OptimizationConfig:
    """Configuration for performance optimization."""
    # Cache settings
    enable_audio_cache: bool = True
    max_cache_size_mb: int = 500  # Maximum cache size in MB
    max_cache_entries: int = 1000  # Maximum number of cached entries
    cache_ttl_hours: int = 24  # Time to live for cache entries
    
    # Model optimization
    enable_model_optimization: bool = True
    use_half_precision: bool = True  # Use FP16 for faster inference
    optimize_for_inference: bool = True
    
    # Memory management
    enable_memory_optimization: bool = True
    gc_frequency: int = 10  # Run garbage collection every N requests
    clear_cache_on_memory_pressure: bool = True
    
    # Performance monitoring
    enable_performance_monitoring: bool = True
    log_performance_metrics: bool = False


class AudioCache:
    """
    LRU cache for TTS audio with size and TTL management.
    """
    
    def __init__(self, max_size_mb: int = 500, max_entries: int = 1000, ttl_hours: int = 24):
        """
        Initialize the audio cache.
        
        Args:
            max_size_mb: Maximum cache size in MB
            max_entries: Maximum number of entries
            ttl_hours: Time to live in hours
        """
        self.max_size_mb = max_size_mb
        self.max_entries = max_entries
        self.ttl_seconds = ttl_hours * 3600
        
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._current_size_bytes = 0
        self._lock = threading.RLock()
        
        logger.info(f"AudioCache initialized: max_size={max_size_mb}MB, max_entries={max_entries}, ttl={ttl_hours}h")
    
    def _generate_cache_key(self, text: str, voice_profile_id: str, language: str, **kwargs) -> str:
        """Generate a cache key for the given parameters."""
        # Create a hash of all parameters that affect audio generation
        key_data = {
            'text': text,
            'voice_profile_id': voice_profile_id,
            'language': language,
            **kwargs
        }
        
        key_string = str(sorted(key_data.items()))
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def get(self, text: str, voice_profile_id: str, language: str, **kwargs) -> Optional[Tuple[Any, int]]:
        """
        Get cached audio data.
        
        Args:
            text: Text that was synthesized
            voice_profile_id: Voice profile ID used
            language: Language used
            **kwargs: Additional parameters
            
        Returns:
            Tuple of (audio_data, sample_rate) if found, None otherwise
        """
        cache_key = self._generate_cache_key(text, voice_profile_id, language, **kwargs)
        
        with self._lock:
            if cache_key not in self._cache:
                return None
            
            entry = self._cache[cache_key]
            
            # Check TTL
            if time.time() - entry.timestamp > self.ttl_seconds:
                self._remove_entry(cache_key)
                return None
            
            # Update access count and move to end (most recently used)
            entry.access_count += 1
            self._cache.move_to_end(cache_key)
            
            logger.debug(f"Cache hit for key: {cache_key[:8]}...")
            return entry.audio_data, entry.sample_rate
    
    def put(self, text: str, voice_profile_id: str, language: str, audio_data: Any, sample_rate: int, **kwargs) -> None:
        """
        Store audio data in cache.
        
        Args:
            text: Text that was synthesized
            voice_profile_id: Voice profile ID used
            language: Language used
            audio_data: Generated audio data
            sample_rate: Audio sample rate
            **kwargs: Additional parameters
        """
        cache_key = self._generate_cache_key(text, voice_profile_id, language, **kwargs)
        
        # Estimate size
        try:
            if hasattr(audio_data, 'nbytes'):
                size_bytes = audio_data.nbytes
            elif hasattr(audio_data, '__len__'):
                size_bytes = len(audio_data) * 4  # Assume float32
            else:
                size_bytes = len(pickle.dumps(audio_data))
        except Exception:
            size_bytes = 1024  # Default estimate
        
        with self._lock:
            # Remove existing entry if present
            if cache_key in self._cache:
                self._remove_entry(cache_key)
            
            # Check if we need to make space
            self._make_space_for_entry(size_bytes)
            
            # Add new entry
            entry = CacheEntry(
                audio_data=audio_data,
                sample_rate=sample_rate,
                timestamp=time.time(),
                access_count=1,
                size_bytes=size_bytes,
                voice_profile_id=voice_profile_id,
                language=language
            )
            
            self._cache[cache_key] = entry
            self._current_size_bytes += size_bytes
            
            logger.debug(f"Cached audio for key: {cache_key[:8]}... (size: {size_bytes} bytes)")
    
    def _remove_entry(self, cache_key: str) -> None:
        """Remove an entry from the cache."""
        if cache_key in self._cache:
            entry = self._cache.pop(cache_key)
            self._current_size_bytes -= entry.size_bytes
    
    def _make_space_for_entry(self, required_bytes: int) -> None:
        """Make space for a new entry by removing old entries."""
        # Check size limit
        while (self._current_size_bytes + required_bytes > self.max_size_mb * 1024 * 1024 or
               len(self._cache) >= self.max_entries):
            
            if not self._cache:
                break
            
            # Remove least recently used entry
            oldest_key = next(iter(self._cache))
            self._remove_entry(oldest_key)
    
    def clear(self) -> None:
        """Clear all cache entries."""
        with self._lock:
            self._cache.clear()
            self._current_size_bytes = 0
            logger.info("Audio cache cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self._lock:
            return {
                'entries': len(self._cache),
                'size_mb': self._current_size_bytes / (1024 * 1024),
                'max_size_mb': self.max_size_mb,
                'max_entries': self.max_entries,
                'utilization': len(self._cache) / self.max_entries if self.max_entries > 0 else 0
            }


class PerformanceOptimizer:
    """
    Manages performance optimization for TTS operations.
    
    This class provides comprehensive performance optimization including
    audio caching, model optimization, memory management, and monitoring.
    """
    
    def __init__(self, config: Optional[OptimizationConfig] = None):
        """
        Initialize the performance optimizer.
        
        Args:
            config: Optimization configuration
        """
        self.config = config or OptimizationConfig()
        
        # Initialize cache
        self.audio_cache = None
        if self.config.enable_audio_cache:
            self.audio_cache = AudioCache(
                max_size_mb=self.config.max_cache_size_mb,
                max_entries=self.config.max_cache_entries,
                ttl_hours=self.config.cache_ttl_hours
            )
        
        # Performance metrics
        self._metrics = {
            'total_requests': 0,
            'cache_hits': 0,
            'generation_times': [],
            'model_load_time': 0.0
        }
        
        self._lock = threading.RLock()
        
        logger.info(f"PerformanceOptimizer initialized with config: {self.config}")
    
    def optimize_model(self, model: Any) -> Any:
        """
        Optimize a TTS model for better performance.
        
        Args:
            model: TTS model to optimize
            
        Returns:
            Optimized model
        """
        if not self.config.enable_model_optimization:
            return model
        
        try:
            start_time = time.time()
            
            # Move to appropriate device
            if torch and hasattr(model, 'to'):
                if torch.cuda.is_available():
                    model = model.to('cuda')
                elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                    model = model.to('mps')
            
            # Enable half precision if supported
            if self.config.use_half_precision and torch and hasattr(model, 'half'):
                try:
                    model = model.half()
                    logger.debug("Enabled half precision for model")
                except Exception as e:
                    logger.warning(f"Failed to enable half precision: {e}")
            
            # Optimize for inference
            if self.config.optimize_for_inference and hasattr(model, 'eval'):
                model.eval()
                
                # Disable gradient computation
                if torch:
                    for param in model.parameters():
                        param.requires_grad = False
            
            load_time = time.time() - start_time
            self._metrics['model_load_time'] = load_time
            
            logger.info(f"Model optimization completed in {load_time:.2f}s")
            return model
            
        except Exception as e:
            logger.warning(f"Model optimization failed: {e}")
            return model
    
    def get_cached_audio(self, text: str, voice_profile_id: str, language: str, **kwargs) -> Optional[Tuple[Any, int]]:
        """
        Get cached audio if available.
        
        Args:
            text: Text to synthesize
            voice_profile_id: Voice profile ID
            language: Language
            **kwargs: Additional parameters
            
        Returns:
            Tuple of (audio_data, sample_rate) if cached, None otherwise
        """
        if not self.audio_cache:
            return None
        
        with self._lock:
            self._metrics['total_requests'] += 1
            
            result = self.audio_cache.get(text, voice_profile_id, language, **kwargs)
            
            if result is not None:
                self._metrics['cache_hits'] += 1
                logger.debug("Using cached audio")
            
            return result
    
    def cache_audio(self, text: str, voice_profile_id: str, language: str, audio_data: Any, sample_rate: int, **kwargs) -> None:
        """
        Cache generated audio.
        
        Args:
            text: Text that was synthesized
            voice_profile_id: Voice profile ID used
            language: Language used
            audio_data: Generated audio data
            sample_rate: Audio sample rate
            **kwargs: Additional parameters
        """
        if not self.audio_cache:
            return
        
        self.audio_cache.put(text, voice_profile_id, language, audio_data, sample_rate, **kwargs)
    
    def record_generation_time(self, generation_time: float) -> None:
        """Record TTS generation time for metrics."""
        with self._lock:
            self._metrics['generation_times'].append(generation_time)
            
            # Keep only recent times (last 100)
            if len(self._metrics['generation_times']) > 100:
                self._metrics['generation_times'] = self._metrics['generation_times'][-100:]
    
    def optimize_memory(self) -> None:
        """Perform memory optimization."""
        if not self.config.enable_memory_optimization:
            return
        
        try:
            # Run garbage collection
            gc.collect()
            
            # Clear PyTorch cache if available
            if torch and torch.cuda.is_available():
                torch.cuda.empty_cache()
            
            # Check memory pressure and clear cache if needed
            if self.config.clear_cache_on_memory_pressure:
                memory_usage = self._get_memory_usage_mb()
                if memory_usage > 1000:  # If using more than 1GB
                    if self.audio_cache:
                        self.audio_cache.clear()
                    logger.info(f"Cleared cache due to memory pressure: {memory_usage:.1f}MB")
            
        except Exception as e:
            logger.warning(f"Memory optimization failed: {e}")
    
    def _get_memory_usage_mb(self) -> float:
        """Get current memory usage in MB."""
        try:
            import psutil
            process = psutil.Process()
            return process.memory_info().rss / (1024 * 1024)
        except ImportError:
            return 0.0
        except Exception:
            return 0.0
    
    def get_performance_metrics(self) -> PerformanceMetrics:
        """
        Get current performance metrics.
        
        Returns:
            PerformanceMetrics with current statistics
        """
        with self._lock:
            total_requests = self._metrics['total_requests']
            cache_hits = self._metrics['cache_hits']
            generation_times = self._metrics['generation_times']
            
            cache_hit_rate = cache_hits / total_requests if total_requests > 0 else 0.0
            avg_generation_time = sum(generation_times) / len(generation_times) if generation_times else 0.0
            memory_usage = self._get_memory_usage_mb()
            
            cache_stats = self.audio_cache.get_stats() if self.audio_cache else {'size_mb': 0.0}
            
            return PerformanceMetrics(
                cache_hit_rate=cache_hit_rate,
                average_generation_time=avg_generation_time,
                memory_usage_mb=memory_usage,
                model_load_time=self._metrics['model_load_time'],
                total_requests=total_requests,
                cache_size_mb=cache_stats['size_mb']
            )
    
    def should_run_gc(self) -> bool:
        """Check if garbage collection should be run."""
        if not self.config.enable_memory_optimization:
            return False
        
        return self._metrics['total_requests'] % self.config.gc_frequency == 0
    
    def log_performance_metrics(self) -> None:
        """Log current performance metrics."""
        if not self.config.log_performance_metrics:
            return
        
        try:
            metrics = self.get_performance_metrics()
            
            logger.info("Performance Metrics:")
            logger.info(f"  Cache Hit Rate: {metrics.cache_hit_rate:.2%}")
            logger.info(f"  Avg Generation Time: {metrics.average_generation_time:.2f}s")
            logger.info(f"  Memory Usage: {metrics.memory_usage_mb:.1f}MB")
            logger.info(f"  Cache Size: {metrics.cache_size_mb:.1f}MB")
            logger.info(f"  Total Requests: {metrics.total_requests}")
            
        except Exception as e:
            logger.warning(f"Failed to log performance metrics: {e}")
    
    def clear_cache(self) -> None:
        """Clear the audio cache."""
        if self.audio_cache:
            self.audio_cache.clear()
    
    def cleanup(self) -> None:
        """Clean up optimizer resources."""
        self.clear_cache()
        self.optimize_memory()
        logger.info("Performance optimizer cleaned up")
