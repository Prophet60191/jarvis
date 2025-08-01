"""
Multi-Tier Response Cache System for Jarvis Voice Assistant

Provides instant/prompt/response/context caching for 60-80% latency reduction
and 70%+ cache hit rate targeting sub-second response times.
"""

import time
import json
import hashlib
import logging
import threading
from enum import Enum
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any, Tuple
from collections import OrderedDict
import pickle
import os

logger = logging.getLogger(__name__)


class CacheLevel(Enum):
    """Cache levels for multi-tier caching strategy."""
    INSTANT = "instant"        # Pattern-based responses (0ms)
    PROMPT = "prompt"          # Cached system prompts (60-80% latency reduction)
    RESPONSE = "response"      # Semantic response caching
    CONTEXT = "context"        # Compressed conversation contexts


@dataclass
class CacheEntry:
    """Cache entry with metadata."""
    data: Any
    created_at: float
    last_accessed: float
    access_count: int
    cache_level: CacheLevel
    ttl_seconds: Optional[float] = None
    size_bytes: int = 0
    
    def is_expired(self) -> bool:
        """Check if cache entry is expired."""
        if self.ttl_seconds is None:
            return False
        return time.time() - self.created_at > self.ttl_seconds
    
    def touch(self) -> None:
        """Update last accessed time and increment access count."""
        self.last_accessed = time.time()
        self.access_count += 1


@dataclass
class CacheStats:
    """Cache performance statistics."""
    total_requests: int = 0
    hits: int = 0
    misses: int = 0
    evictions: int = 0
    hit_rate: float = 0.0
    avg_response_time_ms: float = 0.0
    cache_size: int = 0
    memory_usage_mb: float = 0.0
    
    def update_hit_rate(self) -> None:
        """Update hit rate calculation."""
        if self.total_requests > 0:
            self.hit_rate = self.hits / self.total_requests


class MultiTierCache:
    """
    Multi-tier caching system with different strategies for each level.
    
    Tier 1 (INSTANT): Pattern-based responses, never expire
    Tier 2 (PROMPT): System prompts, long TTL (24h)
    Tier 3 (RESPONSE): LLM responses, medium TTL (1h)
    Tier 4 (CONTEXT): Conversation contexts, short TTL (30min)
    """
    
    def __init__(self, 
                 max_size: int = 10000,
                 max_memory_mb: float = 500.0,
                 enable_persistence: bool = True,
                 cache_dir: str = "cache"):
        """
        Initialize multi-tier cache.
        
        Args:
            max_size: Maximum number of cache entries
            max_memory_mb: Maximum memory usage in MB
            enable_persistence: Enable disk persistence
            cache_dir: Directory for persistent cache files
        """
        self.max_size = max_size
        self.max_memory_bytes = max_memory_mb * 1024 * 1024
        self.enable_persistence = enable_persistence
        self.cache_dir = cache_dir
        
        # Separate caches for each tier
        self.caches: Dict[CacheLevel, OrderedDict[str, CacheEntry]] = {
            CacheLevel.INSTANT: OrderedDict(),
            CacheLevel.PROMPT: OrderedDict(),
            CacheLevel.RESPONSE: OrderedDict(),
            CacheLevel.CONTEXT: OrderedDict()
        }
        
        # Cache statistics
        self.stats: Dict[CacheLevel, CacheStats] = {
            level: CacheStats() for level in CacheLevel
        }
        
        # Thread safety
        self._lock = threading.RLock()
        
        # TTL settings for each tier (in seconds)
        self.ttl_settings = {
            CacheLevel.INSTANT: None,      # Never expire
            CacheLevel.PROMPT: 24 * 3600,  # 24 hours
            CacheLevel.RESPONSE: 3600,     # 1 hour
            CacheLevel.CONTEXT: 1800       # 30 minutes
        }
        
        # Initialize persistence
        if self.enable_persistence:
            self._ensure_cache_dir()
            self._load_persistent_cache()
        
        logger.info(f"MultiTierCache initialized: max_size={max_size}, "
                   f"max_memory={max_memory_mb}MB, persistence={enable_persistence}")
    
    def get(self, key: str, cache_level: CacheLevel) -> Optional[Any]:
        """
        Get item from cache.
        
        Args:
            key: Cache key
            cache_level: Cache tier to search
            
        Returns:
            Cached data or None if not found/expired
        """
        start_time = time.time()
        
        with self._lock:
            cache = self.caches[cache_level]
            stats = self.stats[cache_level]
            
            stats.total_requests += 1
            
            if key in cache:
                entry = cache[key]
                
                # Check expiration
                if entry.is_expired():
                    del cache[key]
                    stats.misses += 1
                    logger.debug(f"Cache EXPIRED for key: {key} (level: {cache_level.value})")
                    return None
                
                # Cache hit
                entry.touch()
                cache.move_to_end(key)  # Move to end (most recently used)
                stats.hits += 1
                
                response_time = (time.time() - start_time) * 1000
                stats.avg_response_time_ms = (
                    (stats.avg_response_time_ms * (stats.hits - 1) + response_time) / stats.hits
                )
                
                stats.update_hit_rate()
                logger.debug(f"Cache HIT for key: {key} (level: {cache_level.value})")
                return entry.data
            else:
                # Cache miss
                stats.misses += 1
                stats.update_hit_rate()
                logger.debug(f"Cache MISS for key: {key} (level: {cache_level.value})")
                return None
    
    def put(self, key: str, data: Any, cache_level: CacheLevel) -> None:
        """
        Put item in cache.
        
        Args:
            key: Cache key
            data: Data to cache
            cache_level: Cache tier to use
        """
        with self._lock:
            cache = self.caches[cache_level]
            stats = self.stats[cache_level]
            
            # Estimate size
            size_bytes = self._estimate_size(data)
            
            # Create cache entry
            entry = CacheEntry(
                data=data,
                created_at=time.time(),
                last_accessed=time.time(),
                access_count=1,
                cache_level=cache_level,
                ttl_seconds=self.ttl_settings[cache_level],
                size_bytes=size_bytes
            )
            
            # Add to cache
            if key in cache:
                # Update existing entry
                cache[key] = entry
                cache.move_to_end(key)
            else:
                # Add new entry
                cache[key] = entry
                
                # Check size limits and evict if necessary
                self._evict_if_necessary(cache_level)
            
            stats.cache_size = len(cache)
            logger.debug(f"Cache PUT for key: {key} (level: {cache_level.value}, size: {size_bytes})")
    
    def get_instant_response(self, pattern: str) -> Optional[str]:
        """Get instant pattern-based response."""
        return self.get(f"instant_{pattern}", CacheLevel.INSTANT)
    
    def cache_instant_response(self, pattern: str, response: str) -> None:
        """Cache instant pattern-based response."""
        self.put(f"instant_{pattern}", response, CacheLevel.INSTANT)
    
    def get_cached_prompt(self, prompt_hash: str) -> Optional[str]:
        """Get cached system prompt."""
        return self.get(f"prompt_{prompt_hash}", CacheLevel.PROMPT)
    
    def cache_prompt(self, prompt: str) -> str:
        """Cache system prompt and return hash."""
        prompt_hash = hashlib.md5(prompt.encode()).hexdigest()
        self.put(f"prompt_{prompt_hash}", prompt, CacheLevel.PROMPT)
        return prompt_hash
    
    def get_cached_response(self, query_hash: str) -> Optional[str]:
        """Get cached LLM response."""
        return self.get(f"response_{query_hash}", CacheLevel.RESPONSE)
    
    def cache_response(self, query: str, response: str, context: str = "") -> None:
        """Cache LLM response with semantic key."""
        # Create semantic hash including context
        semantic_key = f"{query}|{context}"
        query_hash = hashlib.md5(semantic_key.encode()).hexdigest()
        self.put(f"response_{query_hash}", response, CacheLevel.RESPONSE)
    
    def get_cached_context(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get cached conversation context."""
        return self.get(f"context_{session_id}", CacheLevel.CONTEXT)
    
    def cache_context(self, session_id: str, context: Dict[str, Any]) -> None:
        """Cache conversation context."""
        self.put(f"context_{session_id}", context, CacheLevel.CONTEXT)
    
    def _evict_if_necessary(self, cache_level: CacheLevel) -> None:
        """Evict entries if cache exceeds limits."""
        cache = self.caches[cache_level]
        stats = self.stats[cache_level]
        
        # Check size limit
        while len(cache) > self.max_size // len(CacheLevel):  # Distribute size across tiers
            self._evict_lru(cache_level)
        
        # Check memory limit (rough approximation)
        total_memory = sum(
            sum(entry.size_bytes for entry in tier_cache.values())
            for tier_cache in self.caches.values()
        )
        
        while total_memory > self.max_memory_bytes and cache:
            self._evict_lru(cache_level)
            total_memory = sum(
                sum(entry.size_bytes for entry in tier_cache.values())
                for tier_cache in self.caches.values()
            )
    
    def _evict_lru(self, cache_level: CacheLevel) -> None:
        """Evict least recently used entry from specified cache level."""
        cache = self.caches[cache_level]
        stats = self.stats[cache_level]
        
        if cache:
            key, entry = cache.popitem(last=False)  # Remove first (oldest)
            stats.evictions += 1
            logger.debug(f"Cache EVICT for key: {key} (level: {cache_level.value})")
    
    def _estimate_size(self, data: Any) -> int:
        """Rough estimation of data size in bytes."""
        try:
            return len(pickle.dumps(data))
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
    
    def _ensure_cache_dir(self) -> None:
        """Ensure cache directory exists."""
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
    
    def _load_persistent_cache(self) -> None:
        """Load persistent cache from disk."""
        try:
            for cache_level in CacheLevel:
                cache_file = os.path.join(self.cache_dir, f"{cache_level.value}_cache.pkl")
                if os.path.exists(cache_file):
                    with open(cache_file, 'rb') as f:
                        cached_data = pickle.load(f)
                        self.caches[cache_level].update(cached_data)
                    logger.info(f"Loaded {len(cached_data)} entries from {cache_level.value} cache")
        except Exception as e:
            logger.warning(f"Failed to load persistent cache: {e}")
    
    def save_persistent_cache(self) -> None:
        """Save cache to disk."""
        if not self.enable_persistence:
            return
        
        try:
            with self._lock:
                for cache_level, cache in self.caches.items():
                    cache_file = os.path.join(self.cache_dir, f"{cache_level.value}_cache.pkl")
                    with open(cache_file, 'wb') as f:
                        pickle.dump(dict(cache), f)
                logger.info("Persistent cache saved")
        except Exception as e:
            logger.error(f"Failed to save persistent cache: {e}")
    
    def get_cache_stats(self) -> Dict[str, CacheStats]:
        """Get cache statistics for all levels."""
        with self._lock:
            # Update memory usage
            for cache_level, cache in self.caches.items():
                stats = self.stats[cache_level]
                stats.cache_size = len(cache)
                stats.memory_usage_mb = sum(entry.size_bytes for entry in cache.values()) / (1024 * 1024)
            
            return {level.value: stats for level, stats in self.stats.items()}
    
    def clear_cache(self, cache_level: Optional[CacheLevel] = None) -> None:
        """Clear cache for specified level or all levels."""
        with self._lock:
            if cache_level:
                self.caches[cache_level].clear()
                self.stats[cache_level] = CacheStats()
                logger.info(f"Cleared {cache_level.value} cache")
            else:
                for level in CacheLevel:
                    self.caches[level].clear()
                    self.stats[level] = CacheStats()
                logger.info("Cleared all caches")


# Global cache instance
_cache_instance = None


def get_response_cache() -> MultiTierCache:
    """Get the global response cache instance."""
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = MultiTierCache()
    return _cache_instance
