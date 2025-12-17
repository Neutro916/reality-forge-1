#!/usr/bin/env python3
"""
STATUS CACHE - High-Performance Status File Caching
C2 Architect Implementation - Priority Queue Item

Problem: Multiple components read hub status files repeatedly, causing:
- Disk I/O overhead
- JSON parsing overhead
- File locking contention

Solution: In-memory cache with:
- LRU eviction
- TTL-based expiration
- File modification tracking
- Thread-safe access

Usage:
    cache = StatusCache()

    # Instead of:
    with open('hub/WAKE_SIGNAL.json') as f:
        data = json.load(f)

    # Use:
    data = cache.get('hub/WAKE_SIGNAL.json')

    # Or with decorator:
    @cache.cached_read('hub/status.json')
    def get_status():
        return load_status_file()
"""

import json
import time
import threading
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Optional, Any, Callable
from dataclasses import dataclass
from functools import wraps
from collections import OrderedDict

# Paths
CONSCIOUSNESS = Path.home() / ".consciousness"
HUB = CONSCIOUSNESS / "hub"


@dataclass
class CacheEntry:
    """Single cache entry with metadata"""
    data: Any
    timestamp: float
    file_mtime: float
    access_count: int = 0
    last_access: float = 0


class StatusCache:
    """
    High-performance cache for hub status files.

    Features:
    - LRU eviction when max_size reached
    - TTL-based automatic expiration
    - File modification detection (cache invalidation)
    - Thread-safe with RLock
    - Statistics tracking
    """

    def __init__(self, max_size: int = 100, default_ttl: int = 30):
        """
        Initialize cache.

        Args:
            max_size: Maximum number of cached files
            default_ttl: Default time-to-live in seconds
        """
        self.max_size = max_size
        self.default_ttl = default_ttl

        # Cache storage (OrderedDict for LRU)
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._lock = threading.RLock()

        # Statistics
        self.stats = {
            'hits': 0,
            'misses': 0,
            'invalidations': 0,
            'evictions': 0
        }

        # Custom TTLs per file pattern
        self._ttl_patterns = {
            'WAKE_SIGNAL': 5,      # Wake signals need fresh data
            'STATUS': 30,          # Status files can be cached longer
            'HISTORY': 60,         # History rarely changes
            'METRICS': 15,         # Metrics need moderate freshness
            'PRIORITY': 120        # Priority queues change rarely
        }

    def _get_ttl(self, path: str) -> int:
        """Get TTL for a path based on patterns"""
        path_upper = Path(path).name.upper()
        for pattern, ttl in self._ttl_patterns.items():
            if pattern in path_upper:
                return ttl
        return self.default_ttl

    def _get_mtime(self, path: Path) -> float:
        """Get file modification time"""
        try:
            return path.stat().st_mtime
        except:
            return 0

    def _is_valid(self, entry: CacheEntry, path: Path) -> bool:
        """Check if cache entry is still valid"""
        # Check TTL
        ttl = self._get_ttl(str(path))
        if time.time() - entry.timestamp > ttl:
            return False

        # Check file modification
        current_mtime = self._get_mtime(path)
        if current_mtime != entry.file_mtime:
            return False

        return True

    def _evict_lru(self):
        """Evict least recently used entry"""
        if self._cache:
            # Find LRU (first item in OrderedDict is oldest)
            oldest_key = next(iter(self._cache))
            del self._cache[oldest_key]
            self.stats['evictions'] += 1

    def get(self, path: str, default: Any = None) -> Any:
        """
        Get cached file data.

        Args:
            path: Path to status file (absolute or relative to hub)
            default: Default value if file not found

        Returns:
            Parsed JSON data or default
        """
        # Normalize path
        file_path = Path(path)
        if not file_path.is_absolute():
            file_path = HUB / path

        cache_key = str(file_path)

        with self._lock:
            # Check cache
            if cache_key in self._cache:
                entry = self._cache[cache_key]

                if self._is_valid(entry, file_path):
                    # Cache hit - update access stats and move to end (most recent)
                    entry.access_count += 1
                    entry.last_access = time.time()
                    self._cache.move_to_end(cache_key)
                    self.stats['hits'] += 1
                    return entry.data
                else:
                    # Invalidate stale entry
                    del self._cache[cache_key]
                    self.stats['invalidations'] += 1

            # Cache miss - load from disk
            self.stats['misses'] += 1

            if not file_path.exists():
                return default

            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)

                # Add to cache
                if len(self._cache) >= self.max_size:
                    self._evict_lru()

                self._cache[cache_key] = CacheEntry(
                    data=data,
                    timestamp=time.time(),
                    file_mtime=self._get_mtime(file_path),
                    access_count=1,
                    last_access=time.time()
                )

                return data

            except (json.JSONDecodeError, IOError) as e:
                return default

    def set(self, path: str, data: Any):
        """
        Write data to file and update cache.

        Args:
            path: Path to status file
            data: Data to write (will be JSON serialized)
        """
        file_path = Path(path)
        if not file_path.is_absolute():
            file_path = HUB / path

        cache_key = str(file_path)

        with self._lock:
            # Write to disk
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)

            # Update cache
            self._cache[cache_key] = CacheEntry(
                data=data,
                timestamp=time.time(),
                file_mtime=self._get_mtime(file_path),
                access_count=1,
                last_access=time.time()
            )
            self._cache.move_to_end(cache_key)

    def invalidate(self, path: str = None):
        """
        Invalidate cache entry or entire cache.

        Args:
            path: Specific path to invalidate, or None for all
        """
        with self._lock:
            if path is None:
                self._cache.clear()
                self.stats['invalidations'] += 1
            else:
                file_path = Path(path)
                if not file_path.is_absolute():
                    file_path = HUB / path
                cache_key = str(file_path)

                if cache_key in self._cache:
                    del self._cache[cache_key]
                    self.stats['invalidations'] += 1

    def cached_read(self, path: str, ttl: int = None):
        """
        Decorator for cached file reads.

        Usage:
            @cache.cached_read('status.json')
            def get_status():
                # This will only be called on cache miss
                return process_status_data()
        """
        def decorator(func: Callable):
            @wraps(func)
            def wrapper(*args, **kwargs):
                data = self.get(path)
                if data is not None:
                    return data
                # Cache miss - call function
                result = func(*args, **kwargs)
                if result is not None:
                    self.set(path, result)
                return result
            return wrapper
        return decorator

    def get_stats(self) -> Dict:
        """Get cache statistics"""
        with self._lock:
            total = self.stats['hits'] + self.stats['misses']
            hit_rate = self.stats['hits'] / total if total > 0 else 0

            return {
                'hits': self.stats['hits'],
                'misses': self.stats['misses'],
                'hit_rate': f"{hit_rate:.1%}",
                'invalidations': self.stats['invalidations'],
                'evictions': self.stats['evictions'],
                'current_size': len(self._cache),
                'max_size': self.max_size
            }

    def get_cached_files(self) -> list:
        """Get list of currently cached files"""
        with self._lock:
            return list(self._cache.keys())


# Global cache instance
_global_cache = None

def get_cache() -> StatusCache:
    """Get global cache instance (singleton)"""
    global _global_cache
    if _global_cache is None:
        _global_cache = StatusCache()
    return _global_cache


def cached_status_read(path: str):
    """
    Convenience decorator using global cache.

    Usage:
        @cached_status_read('WAKE_SIGNAL.json')
        def check_wake():
            return {'status': 'ready'}
    """
    return get_cache().cached_read(path)


# Convenience functions
def read_status(path: str, default: Any = None) -> Any:
    """Read status file with caching"""
    return get_cache().get(path, default)

def write_status(path: str, data: Any):
    """Write status file and update cache"""
    get_cache().set(path, data)


def demo():
    """Demonstrate status cache"""
    print("="*60)
    print("STATUS CACHE DEMO")
    print("="*60)

    cache = StatusCache()

    # Test reading files
    test_files = [
        'WAKE_SIGNAL.json',
        'CYCLOTRON_STATUS.json',
        'CONVERGENCE_METRICS.json',
        'NERVE_CENTER_STATUS.json'
    ]

    print("\n--- First Read (Cache Miss) ---")
    for f in test_files:
        start = time.perf_counter()
        data = cache.get(f)
        elapsed = (time.perf_counter() - start) * 1000
        status = "FOUND" if data else "NOT FOUND"
        print(f"  {f}: {status} ({elapsed:.2f}ms)")

    print("\n--- Second Read (Cache Hit) ---")
    for f in test_files:
        start = time.perf_counter()
        data = cache.get(f)
        elapsed = (time.perf_counter() - start) * 1000
        status = "FOUND" if data else "NOT FOUND"
        print(f"  {f}: {status} ({elapsed:.3f}ms)")

    print("\n--- Cache Statistics ---")
    stats = cache.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")

    print("\n--- Cached Files ---")
    for f in cache.get_cached_files():
        print(f"  {Path(f).name}")

    # Benchmark
    print("\n--- Benchmark (100 reads) ---")

    # Without cache
    start = time.perf_counter()
    for _ in range(100):
        try:
            with open(HUB / 'WAKE_SIGNAL.json') as f:
                json.load(f)
        except:
            pass
    uncached_time = (time.perf_counter() - start) * 1000

    # With cache
    start = time.perf_counter()
    for _ in range(100):
        cache.get('WAKE_SIGNAL.json')
    cached_time = (time.perf_counter() - start) * 1000

    print(f"  Uncached: {uncached_time:.1f}ms")
    print(f"  Cached:   {cached_time:.1f}ms")
    print(f"  Speedup:  {uncached_time/max(cached_time, 0.1):.1f}x")


if __name__ == "__main__":
    demo()
