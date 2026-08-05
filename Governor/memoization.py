"""
Action Result Memoization for Governor.py v1.5

This module provides memoization decorators for action results per v1.5 spec §12.8.
Memoization improves performance by caching action results for identical inputs.

Key Components:
- memoize_result: Decorator for action result caching with TTL
- Cache key generation: (action_name, tool_name, payload_hash)
- TTL-based invalidation: Default 60 seconds
- Cache statistics: Hit rate, miss rate, cache size

This implements the memoization specified in v1.5 spec §12.8.
"""

import hashlib
import time
from typing import Dict, Any, Callable
from functools import wraps

# Cache statistics
_cache_stats = {
    "hits": 0,
    "misses": 0,
    "evictions": 0
}


def memoize_result(ttl_seconds: int = 60):
    """
    Decorator for memoizing action results with TTL.
    
    This decorator caches action evaluation results based on:
    - Action name (self.name)
    - Tool name (context.tool_name if available)
    - Payload hash (SHA-256 of serialized payload)
    
    Args:
        ttl_seconds: Time-to-live for cache entries in seconds (default: 60)
        
    Returns:
        Decorator function
        
    Example:
        @memoize_result(ttl_seconds=120)
        def evaluate(self, payload, params, context):
            # Action logic
            return ActionResult(...)
    """
    def decorator(func: Callable) -> Callable:
        cache: Dict[str, Dict[str, Any]] = {}
        
        @wraps(func)
        def wrapper(self, payload: Dict[str, Any], params: Dict[str, Any], 
                   context: Any) -> Any:
            global _cache_stats
            
            # Generate cache key per spec §12.8
            payload_hash = hashlib.sha256(str(payload).encode()).hexdigest()
            
            # Get tool name from context if available
            tool_name = None
            if context and hasattr(context, 'tool_normalizer') and context.tool_normalizer:
                if 'tool' in payload:
                    try:
                        tool_name = context.tool_normalizer.normalize_tool_name(payload['tool'])
                    except Exception:
                        tool_name = payload.get('tool', 'unknown')
            elif 'tool' in payload:
                tool_name = payload['tool']
            
            key = (self.name, tool_name, payload_hash)
            
            # Check cache
            current_time = time.time()
            if key in cache:
                entry = cache[key]
                if current_time - entry['time'] < ttl_seconds:
                    # Cache hit
                    _cache_stats['hits'] += 1
                    return entry['result']
                else:
                    # Cache expired
                    del cache[key]
                    _cache_stats['evictions'] += 1
            
            # Cache miss - execute function
            _cache_stats['misses'] += 1
            result = func(self, payload, params, context)
            
            # Store in cache
            cache[key] = {
                'result': result,
                'time': current_time
            }
            
            return result
        
        # Add cache clearing method
        wrapper.clear_cache = lambda: cache.clear()
        
        # Add cache stats method
        wrapper.get_cache_stats = lambda: {
            'size': len(cache),
            'ttl_seconds': ttl_seconds,
            'stats': _cache_stats.copy()
        }
        
        return wrapper
    
    return decorator


def get_memoization_stats() -> Dict[str, Any]:
    """
    Get global memoization statistics.
    
    Returns:
        Dictionary with cache statistics
    """
    return _cache_stats.copy()


def reset_memoization_stats() -> None:
    """Reset memoization statistics."""
    global _cache_stats
    _cache_stats = {
        "hits": 0,
        "misses": 0,
        "evictions": 0
    }
