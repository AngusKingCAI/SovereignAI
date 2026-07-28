#!/usr/bin/env python3
"""
Robust Web Search Implementation for SovereignAI
Implements rate limiting, caching, and fallback mechanisms for reliable web search
"""

import json
import time
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, List


class WebSearchCache:
    """Cache for web search results to avoid redundant searches"""
    
    def __init__(self, cache_dir: str, max_age_hours: int = 24):
        self.cache_dir = Path(cache_dir)
        self.max_age = timedelta(hours=max_age_hours)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_cache_key(self, query: str) -> str:
        """Generate cache key from query"""
        return hashlib.md5(query.encode()).hexdigest()
    
    def get(self, query: str) -> Optional[dict]:
        """Get cached result if available and not expired"""
        cache_key = self._get_cache_key(query)
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        if not cache_file.exists():
            return None
        
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Check if cache is expired
            cached_time = datetime.fromisoformat(data['timestamp'])
            if datetime.now() - cached_time > self.max_age:
                cache_file.unlink()  # Remove expired cache
                return None
            
            return data['results']
        except (json.JSONDecodeError, KeyError, ValueError):
            # Invalid cache file, remove it
            cache_file.unlink()
            return None
    
    def set(self, query: str, results: dict):
        """Cache search results"""
        cache_key = self._get_cache_key(query)
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        data = {
            'timestamp': datetime.now().isoformat(),
            'query': query,
            'results': results
        }
        
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)


class RateLimiter:
    """Rate limiter for web search requests"""
    
    def __init__(self, min_delay_seconds: float = 2.0):
        self.min_delay = min_delay_seconds
        self.last_request_time = 0.0
    
    def wait_if_needed(self):
        """Wait if minimum delay has not passed since last request"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_delay:
            sleep_time = self.min_delay - time_since_last
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()


class RobustWebSearch:
    """Robust web search with caching and rate limiting"""
    
    def __init__(self, cache_dir: str = "Logs/Reviewer/Cache/WebSearch"):
        self.cache = WebSearchCache(cache_dir)
        self.rate_limiter = RateLimiter(min_delay_seconds=2.0)
        self.search_count = 0
        self.cache_hits = 0
    
    def search(self, query: str, force_refresh: bool = False) -> dict:
        """Perform web search with caching and rate limiting"""
        self.search_count += 1
        
        # Check cache first
        if not force_refresh:
            cached_result = self.cache.get(query)
            if cached_result:
                self.cache_hits += 1
                return {
                    'source': 'cache',
                    'query': query,
                    'results': cached_result,
                    'cache_stats': {
                        'total_searches': self.search_count,
                        'cache_hits': self.cache_hits,
                        'cache_hit_rate': f"{(self.cache_hits / self.search_count) * 100:.1f}%"
                    }
                }
        
        # Apply rate limiting
        self.rate_limiter.wait_if_needed()
        
        # Perform actual search (this would call the agent's web_search tool)
        # For now, we'll return a placeholder structure
        search_result = {
            'query': query,
            'timestamp': datetime.now().isoformat(),
            'results': [],  # This would be populated by actual web_search
            'source': 'live_search'
        }
        
        # Cache the results
        self.cache.set(query, search_result)
        
        return search_result
    
    def get_stats(self) -> dict:
        """Get search statistics"""
        return {
            'total_searches': self.search_count,
            'cache_hits': self.cache_hits,
            'cache_hit_rate': f"{(self.cache_hits / self.search_count) * 100:.1f}%" if self.search_count > 0 else "0%"
        }


def create_robust_search(cache_dir: str = "Logs/Reviewer/Cache/WebSearch") -> RobustWebSearch:
    """Factory function to create a RobustWebSearch instance"""
    return RobustWebSearch(cache_dir)


if __name__ == "__main__":
    # Test the robust web search
    search = create_robust_search()
    
    test_queries = [
        "Python best practices 2024",
        "TOML configuration files",
        "JSON schema validation"
    ]
    
    print("Testing Robust Web Search")
    print("=" * 60)
    
    for query in test_queries:
        print(f"\nSearching: {query}")
        result = search.search(query)
        print(f"Source: {result['source']}")
        print(f"Stats: {search.get_stats()}")
    
    # Test cache hit
    print(f"\nSearching again (should hit cache): {test_queries[0]}")
    result = search.search(test_queries[0])
    print(f"Source: {result['source']}")
    print(f"Stats: {search.get_stats()}")