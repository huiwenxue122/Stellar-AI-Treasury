"""
Sentiment Cache
Caches sentiment results for 1 hour to avoid redundant API calls and RSS fetches
"""

from datetime import datetime, timedelta
from typing import Dict, Optional


class SentimentCache:
    """Cache sentiment results with TTL (Time To Live)"""
    
    def __init__(self, ttl_minutes: int = 60):
        """
        Initialize cache
        
        Args:
            ttl_minutes: Time to live for cache entries (default: 60 minutes)
        """
        self.cache: Dict[str, Dict] = {}
        self.ttl = timedelta(minutes=ttl_minutes)
    
    def get(self, asset: str) -> Optional[Dict]:
        """
        Get cached sentiment for asset
        
        Args:
            asset: Asset symbol (BTC, ETH, etc.)
        
        Returns:
            Cached sentiment dict or None if not found/expired
        """
        asset_upper = asset.upper()
        
        if asset_upper in self.cache:
            entry = self.cache[asset_upper]
            
            # Check if expired
            if datetime.now() - entry['timestamp'] < self.ttl:
                return entry['sentiment']
            else:
                # Expired, remove
                del self.cache[asset_upper]
        
        return None
    
    def set(self, asset: str, sentiment: Dict):
        """
        Cache sentiment result
        
        Args:
            asset: Asset symbol
            sentiment: Sentiment analysis result
        """
        asset_upper = asset.upper()
        
        self.cache[asset_upper] = {
            'sentiment': sentiment,
            'timestamp': datetime.now()
        }
    
    def clear(self, asset: Optional[str] = None):
        """
        Clear cache
        
        Args:
            asset: Specific asset to clear, or None to clear all
        """
        if asset:
            asset_upper = asset.upper()
            if asset_upper in self.cache:
                del self.cache[asset_upper]
        else:
            self.cache.clear()
    
    def clear_expired(self):
        """Remove all expired entries"""
        now = datetime.now()
        expired = [
            asset for asset, entry in self.cache.items()
            if now - entry['timestamp'] >= self.ttl
        ]
        
        for asset in expired:
            del self.cache[asset]
    
    def get_stats(self) -> Dict:
        """Get cache statistics"""
        now = datetime.now()
        
        valid_entries = sum(
            1 for entry in self.cache.values()
            if now - entry['timestamp'] < self.ttl
        )
        
        expired_entries = len(self.cache) - valid_entries
        
        return {
            'total_entries': len(self.cache),
            'valid_entries': valid_entries,
            'expired_entries': expired_entries,
            'cache_hit_rate': 'N/A',  # Would need request tracking
            'oldest_entry': min(
                (entry['timestamp'] for entry in self.cache.values()),
                default=None
            ) if self.cache else None
        }
    
    def is_fresh(self, asset: str, max_age_minutes: int = None) -> bool:
        """
        Check if cached data is fresh enough
        
        Args:
            asset: Asset symbol
            max_age_minutes: Custom freshness threshold (default: use TTL)
        
        Returns:
            True if data exists and is fresh
        """
        asset_upper = asset.upper()
        
        if asset_upper not in self.cache:
            return False
        
        entry = self.cache[asset_upper]
        age = datetime.now() - entry['timestamp']
        
        threshold = timedelta(minutes=max_age_minutes) if max_age_minutes else self.ttl
        
        return age < threshold


# Singleton instance for global use
_global_cache = None

def get_global_cache(ttl_minutes: int = 60) -> SentimentCache:
    """Get or create global sentiment cache instance"""
    global _global_cache
    if _global_cache is None:
        _global_cache = SentimentCache(ttl_minutes=ttl_minutes)
    return _global_cache


# Example usage
if __name__ == "__main__":
    cache = SentimentCache(ttl_minutes=1)  # 1 minute for testing
    
    # Cache some sentiment
    test_sentiment = {
        'sentiment': 'positive',
        'score': 0.65,
        'confidence': 0.8,
        'news_count': 5
    }
    
    print("📦 Caching BTC sentiment...")
    cache.set('BTC', test_sentiment)
    
    # Retrieve immediately
    print("\n🔍 Retrieving BTC sentiment (should hit cache):")
    cached = cache.get('BTC')
    print(f"Cached data: {cached}")
    
    # Check stats
    print("\n📊 Cache stats:")
    stats = cache.get_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    # Wait for expiration (in real use, TTL is 60 minutes)
    print("\n⏳ Waiting for cache to expire (1 minute)...")
    import time
    time.sleep(61)
    
    # Try to retrieve expired
    print("\n🔍 Retrieving BTC sentiment (should be expired):")
    cached = cache.get('BTC')
    print(f"Cached data: {cached}")  # Should be None
    
    print("\n✅ Cache test complete!")

