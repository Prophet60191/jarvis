"""
Context Caching System

Provides high-performance caching for frequently accessed context data
with LRU eviction, cache warming, and performance monitoring.
"""

import time
import threading
from typing import Dict, Any, Optional, List, Tuple
from collections import OrderedDict
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)

@dataclass
class CacheStats:
    """Cache performance statistics."""
    hits: int = 0
    misses: int = 0
    evictions: int = 0
    total_requests: int = 0
    cache_size: int = 0
    hit_rate: float = 0.0
    avg_access_time_ms: float = 0.0
    last_updated: float = field(default_factory=time.time)
    
    def update_hit_rate(self):
        """Update hit rate calculation."""
        if self.total_requests > 0:
            self.hit_rate = (self.hits / self.total_requests) * 100
        self.last_updated = time.time()

@dataclass
class CacheEntry:
    """Individual cache entry with metadata."""
    data: Any
    created_at: float
    last_accessed: float
    access_count: int = 0
    size_bytes: int = 0
    
    def touch(self):
        """Update access metadata."""
        self.last_accessed = time.time()
        self.access_count += 1

class LRUContextCache:
    """
    High-performance LRU cache for context data with monitoring.
    
    Features:
    - Thread-safe operations
    - Performance monitoring
    - Cache warming
    - Size-based eviction
    - Access pattern analysis
    """
    
    def __init__(self, max_size: int = 1000, max_memory_mb: int = 100):
        """
        Initialize LRU cache.
        
        Args:
            max_size: Maximum number of entries
            max_memory_mb: Maximum memory usage in MB
        """
        self.max_size = max_size
        self.max_memory_bytes = max_memory_mb * 1024 * 1024
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._lock = threading.RLock()
        self._stats = CacheStats()
        
        # Performance tracking
        self._access_times: List[float] = []
        self._frequently_accessed: Dict[str, int] = {}
        
        logger.info(f"LRUContextCache initialized: max_size={max_size}, max_memory={max_memory_mb}MB")
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get item from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached data or None if not found
        """
        start_time = time.time()
        
        with self._lock:
            self._stats.total_requests += 1
            
            if key in self._cache:
                # Cache hit
                entry = self._cache[key]
                entry.touch()
                
                # Move to end (most recently used)
                self._cache.move_to_end(key)
                
                self._stats.hits += 1
                self._frequently_accessed[key] = self._frequently_accessed.get(key, 0) + 1
                
                access_time = (time.time() - start_time) * 1000
                self._access_times.append(access_time)
                if len(self._access_times) > 1000:
                    self._access_times = self._access_times[-500:]  # Keep recent times
                
                self._update_stats()
                
                logger.debug(f"Cache HIT for key: {key}")
                return entry.data
            else:
                # Cache miss
                self._stats.misses += 1
                self._update_stats()
                
                logger.debug(f"Cache MISS for key: {key}")
                return None
    
    def put(self, key: str, data: Any) -> None:
        """
        Put item in cache.
        
        Args:
            key: Cache key
            data: Data to cache
        """
        with self._lock:
            # Estimate size (rough approximation)
            size_bytes = self._estimate_size(data)
            
            # Create cache entry
            entry = CacheEntry(
                data=data,
                created_at=time.time(),
                last_accessed=time.time(),
                size_bytes=size_bytes
            )
            
            # Check if key already exists
            if key in self._cache:
                # Update existing entry
                old_entry = self._cache[key]
                self._cache[key] = entry
                self._cache.move_to_end(key)
            else:
                # Add new entry
                self._cache[key] = entry
                
                # Check size limits and evict if necessary
                self._evict_if_necessary()
            
            self._stats.cache_size = len(self._cache)
            logger.debug(f"Cache PUT for key: {key}, size: {size_bytes} bytes")
    
    def remove(self, key: str) -> bool:
        """
        Remove item from cache.
        
        Args:
            key: Cache key
            
        Returns:
            True if item was removed, False if not found
        """
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                self._stats.cache_size = len(self._cache)
                if key in self._frequently_accessed:
                    del self._frequently_accessed[key]
                logger.debug(f"Cache REMOVE for key: {key}")
                return True
            return False
    
    def clear(self) -> None:
        """Clear all cache entries."""
        with self._lock:
            self._cache.clear()
            self._frequently_accessed.clear()
            self._stats.cache_size = 0
            logger.info("Cache cleared")
    
    def get_stats(self) -> CacheStats:
        """Get cache performance statistics."""
        with self._lock:
            self._update_stats()
            return self._stats
    
    def get_frequently_accessed(self, limit: int = 10) -> List[Tuple[str, int]]:
        """
        Get most frequently accessed keys.
        
        Args:
            limit: Maximum number of keys to return
            
        Returns:
            List of (key, access_count) tuples
        """
        with self._lock:
            return sorted(
                self._frequently_accessed.items(),
                key=lambda x: x[1],
                reverse=True
            )[:limit]
    
    def warm_cache(self, keys_data: Dict[str, Any]) -> None:
        """
        Warm cache with frequently accessed data.
        
        Args:
            keys_data: Dictionary of key-value pairs to pre-load
        """
        logger.info(f"Warming cache with {len(keys_data)} entries")
        for key, data in keys_data.items():
            self.put(key, data)
        logger.info("Cache warming completed")
    
    def _evict_if_necessary(self) -> None:
        """Evict entries if cache exceeds limits."""
        # Check size limit
        while len(self._cache) > self.max_size:
            self._evict_lru()
        
        # Check memory limit (rough approximation)
        total_memory = sum(entry.size_bytes for entry in self._cache.values())
        while total_memory > self.max_memory_bytes and self._cache:
            self._evict_lru()
            total_memory = sum(entry.size_bytes for entry in self._cache.values())
    
    def _evict_lru(self) -> None:
        """Evict least recently used entry."""
        if self._cache:
            key, entry = self._cache.popitem(last=False)  # Remove first (oldest)
            if key in self._frequently_accessed:
                del self._frequently_accessed[key]
            self._stats.evictions += 1
            logger.debug(f"Cache EVICT for key: {key}")
    
    def _estimate_size(self, data: Any) -> int:
        """Rough estimation of data size in bytes."""
        try:
            import sys
            return sys.getsizeof(data)
        except:
            # Fallback estimation
            if isinstance(data, str):
                return len(data.encode('utf-8'))
            elif isinstance(data, (list, tuple)):
                return sum(self._estimate_size(item) for item in data)
            elif isinstance(data, dict):
                return sum(self._estimate_size(k) + self._estimate_size(v) 
                          for k, v in data.items())
            else:
                return 1024  # Default 1KB estimate
    
    def _update_stats(self) -> None:
        """Update cache statistics."""
        self._stats.cache_size = len(self._cache)
        self._stats.update_hit_rate()
        
        if self._access_times:
            self._stats.avg_access_time_ms = sum(self._access_times) / len(self._access_times)

class ContextCacheManager:
    """
    Manager for multiple context caches with different strategies.
    """
    
    def __init__(self):
        """Initialize cache manager."""
        self.caches: Dict[str, LRUContextCache] = {
            'session_context': LRUContextCache(max_size=500, max_memory_mb=50),
            'user_preferences': LRUContextCache(max_size=200, max_memory_mb=20),
            'conversation_state': LRUContextCache(max_size=300, max_memory_mb=30),
            'tool_results': LRUContextCache(max_size=1000, max_memory_mb=100)
        }
        
        logger.info("ContextCacheManager initialized with multiple cache types")
    
    def get_cache(self, cache_type: str) -> Optional[LRUContextCache]:
        """Get specific cache by type."""
        return self.caches.get(cache_type)
    
    def get_global_stats(self) -> Dict[str, CacheStats]:
        """Get statistics for all caches."""
        return {
            cache_type: cache.get_stats()
            for cache_type, cache in self.caches.items()
        }
    
    def clear_all_caches(self) -> None:
        """Clear all caches."""
        for cache in self.caches.values():
            cache.clear()
        logger.info("All caches cleared")
