#!/usr/bin/env python3
"""
Rule cache accessor for other hooks to efficiently access cached governance rules.
Provides functions to load and use cached rules in other hooks.
"""

import json
import os
from pathlib import Path
from datetime import datetime

class RuleCacheAccessor:
    """Accessor for rule cache data."""
    
    def __init__(self):
        self.project_root = Path("C:/SovereignAI")
        self.cache_dir = self.project_root / ".devin" / "cache"
        self.cache_file = self.cache_dir / "rule_cache.json"
        self.config_dir = self.project_root / "Scripts" / "Governance" / "Config"
        
        self._cache = None
        self._cache_time = None
    
    def is_cache_available(self):
        """Check if rule cache is available and valid."""
        if not self.cache_file.exists():
            return False
        
        # Check cache age (reload if older than 1 hour)
        try:
            with open(self.cache_file) as f:
                cached_data = json.load(f)
            
            cache_time = datetime.fromisoformat(cached_data.get('cached_at', ''))
            age = (datetime.now() - cache_time).total_seconds()
            
            if age > 3600:  # 1 hour
                return False
            
            return True
        except Exception:
            return False
    
    def load_cache(self):
        """Load rules from cache."""
        if not self.is_cache_available():
            return None
        
        try:
            with open(self.cache_file) as f:
                self._cache = json.load(f)
                self._cache_time = datetime.fromisoformat(self._cache.get('cached_at', ''))
                return self._cache.get('rules', {})
        except Exception:
            return None
    
    def get_rules(self):
        """Get cached rules, loading if necessary."""
        if self._cache is None:
            self.load_cache()
        
        if self._cache:
            return self._cache.get('rules', {})
        return None
    
    def get_governance_rules(self):
        """Get governance rules from cache."""
        rules = self.get_rules()
        if rules:
            return rules.get('governance', {})
        return None
    
    def get_phase_permissions(self):
        """Get phase permissions from cache."""
        rules = self.get_rules()
        if rules:
            return rules.get('phases', {})
        return None
    
    def fallback_load_config(self):
        """Fallback to direct config loading if cache unavailable."""
        rules = {}
        
        # Load governance rules
        governance_file = self.config_dir / "governance_rules.json"
        if governance_file.exists():
            try:
                with open(governance_file) as f:
                    rules['governance'] = json.load(f)
            except Exception:
                pass
        
        # Load phase permissions
        phase_file = self.config_dir / "phase_permissions.json"
        if phase_file.exists():
            try:
                with open(phase_file) as f:
                    rules['phases'] = json.load(f)
            except Exception:
                pass
        
        return rules
    
    def get_governance_rules_safe(self):
        """Get governance rules with fallback to direct loading."""
        rules = self.get_governance_rules()
        if rules is None:
            full_rules = self.fallback_load_config()
            rules = full_rules.get('governance', {})
        return rules
    
    def get_phase_permissions_safe(self):
        """Get phase permissions with fallback to direct loading."""
        rules = self.get_phase_permissions()
        if rules is None:
            full_rules = self.fallback_load_config()
            rules = full_rules.get('phases', {})
        return rules

# Singleton instance for global access
_cache_accessor = None

def get_rule_cache_accessor():
    """Get the singleton rule cache accessor instance."""
    global _cache_accessor
    if _cache_accessor is None:
        _cache_accessor = RuleCacheAccessor()
    return _cache_accessor

def get_governance_rules():
    """Convenience function to get governance rules."""
    accessor = get_rule_cache_accessor()
    return accessor.get_governance_rules_safe()

def get_phase_permissions():
    """Convenience function to get phase permissions."""
    accessor = get_rule_cache_accessor()
    return accessor.get_phase_permissions_safe()

if __name__ == "__main__":
    # Test the accessor
    accessor = get_rule_cache_accessor()
    
    print("Testing Rule Cache Accessor")
    print(f"Cache available: {accessor.is_cache_available()}")
    
    governance_rules = accessor.get_governance_rules_safe()
    print(f"Governance rules loaded: {governance_rules is not None}")
    
    phase_permissions = accessor.get_phase_permissions_safe()
    print(f"Phase permissions loaded: {phase_permissions is not None}")
    
    if governance_rules:
        print(f"Governance keys: {list(governance_rules.keys())}")
    
    if phase_permissions:
        print(f"Phase keys: {list(phase_permissions.keys())}")