"""
Crypto News Fetcher
Fetches cryptocurrency news from multiple free sources
"""

import requests
import feedparser
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import time


class CryptoNewsFetcher:
    """Fetch crypto news from free APIs and RSS feeds"""
    
    def __init__(self, cryptopanic_token: Optional[str] = None):
        """
        Initialize news fetcher
        
        Args:
            cryptopanic_token: Optional CryptoPanic API token (free tier: 500/day)
                              Get from: https://cryptopanic.com/developers/api/
        """
        self.cryptopanic_token = cryptopanic_token
        
        # Free RSS feeds (no authentication needed)
        self.rss_feeds = {
            'coindesk': 'https://www.coindesk.com/arc/outboundfeeds/rss/',
            'cointelegraph': 'https://cointelegraph.com/rss',
            'bitcoinmagazine': 'https://bitcoinmagazine.com/feed',
            'decrypt': 'https://decrypt.co/feed'
        }
        
        # Asset keywords for filtering
        self.asset_keywords = {
            'BTC': ['bitcoin', 'btc'],
            'ETH': ['ethereum', 'eth', 'ether'],
            'SOL': ['solana', 'sol'],
            'XLM': ['stellar', 'xlm', 'lumens'],
            'ARB': ['arbitrum', 'arb'],
            'LINK': ['chainlink', 'link'],
            'AAVE': ['aave'],
            'LDO': ['lido', 'ldo'],
            'FET': ['fetch', 'fetch.ai', 'fet'],
            'USDC': ['usdc', 'circle'],
            'USDT': ['tether', 'usdt']
        }
    
    def fetch_news(self, asset: str, hours: int = 1) -> List[Dict]:
        """
        Fetch news for a specific asset from the last N hours
        
        Args:
            asset: Asset symbol (BTC, ETH, etc.)
            hours: Number of hours to look back
        
        Returns:
            List of news items with title, summary, source, published time
        """
        cutoff_time = datetime.now() - timedelta(hours=hours)
        all_news = []
        
        # Fetch from CryptoPanic if token available
        if self.cryptopanic_token:
            try:
                panic_news = self._fetch_cryptopanic(asset)
                all_news.extend(panic_news)
            except Exception as e:
                print(f"⚠️  CryptoPanic fetch failed: {e}")
        
        # Fetch from RSS feeds
        try:
            rss_news = self._fetch_rss_feeds(asset)
            all_news.extend(rss_news)
        except Exception as e:
            print(f"⚠️  RSS fetch failed: {e}")
        
        # Filter by time
        recent_news = [
            item for item in all_news
            if item.get('published') and item['published'] > cutoff_time
        ]
        
        # Deduplicate by title
        seen_titles = set()
        unique_news = []
        for item in recent_news:
            title_lower = item['title'].lower()
            if title_lower not in seen_titles:
                seen_titles.add(title_lower)
                unique_news.append(item)
        
        return unique_news
    
    def _fetch_cryptopanic(self, asset: str) -> List[Dict]:
        """Fetch from CryptoPanic API"""
        if not self.cryptopanic_token:
            return []
        
        url = 'https://cryptopanic.com/api/v1/posts/'
        params = {
            'auth_token': self.cryptopanic_token,
            'currencies': asset,
            'kind': 'news',
            'filter': 'important'  # Only important news
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            news_items = []
            for post in data.get('results', []):
                news_items.append({
                    'title': post.get('title', ''),
                    'summary': post.get('title', ''),  # CryptoPanic doesn't have summary
                    'source': 'CryptoPanic',
                    'url': post.get('url', ''),
                    'published': datetime.fromisoformat(post.get('published_at', '').replace('Z', '+00:00'))
                })
            
            return news_items
        
        except Exception as e:
            print(f"CryptoPanic error: {e}")
            return []
    
    def _fetch_rss_feeds(self, asset: str) -> List[Dict]:
        """Fetch from RSS feeds and filter by asset keywords"""
        keywords = self.asset_keywords.get(asset.upper(), [asset.lower()])
        news_items = []
        
        for source_name, feed_url in self.rss_feeds.items():
            try:
                feed = feedparser.parse(feed_url)
                
                for entry in feed.entries[:50]:  # Check latest 50 entries
                    # Check if asset mentioned in title or summary
                    text = (entry.get('title', '') + ' ' + entry.get('summary', '')).lower()
                    
                    if any(keyword in text for keyword in keywords):
                        # Parse published time
                        published = None
                        if hasattr(entry, 'published_parsed') and entry.published_parsed:
                            published = datetime(*entry.published_parsed[:6])
                        else:
                            published = datetime.now()
                        
                        news_items.append({
                            'title': entry.get('title', ''),
                            'summary': entry.get('summary', entry.get('title', ''))[:500],  # Limit length
                            'source': source_name,
                            'url': entry.get('link', ''),
                            'published': published
                        })
                
                # Rate limiting for RSS (be nice to servers)
                time.sleep(0.5)
            
            except Exception as e:
                print(f"RSS fetch error for {source_name}: {e}")
                continue
        
        return news_items
    
    def fetch_market_wide_news(self, hours: int = 1) -> List[Dict]:
        """
        Fetch general crypto market news (not asset-specific)
        
        Useful for detecting market-wide sentiment (e.g., regulation news)
        """
        news_items = []
        
        for source_name, feed_url in self.rss_feeds.items():
            try:
                feed = feedparser.parse(feed_url)
                cutoff_time = datetime.now() - timedelta(hours=hours)
                
                for entry in feed.entries[:20]:  # Latest 20 from each
                    published = None
                    if hasattr(entry, 'published_parsed') and entry.published_parsed:
                        published = datetime(*entry.published_parsed[:6])
                    else:
                        published = datetime.now()
                    
                    if published > cutoff_time:
                        news_items.append({
                            'title': entry.get('title', ''),
                            'summary': entry.get('summary', entry.get('title', ''))[:500],
                            'source': source_name,
                            'url': entry.get('link', ''),
                            'published': published
                        })
                
                time.sleep(0.5)
            
            except Exception as e:
                print(f"Market-wide fetch error for {source_name}: {e}")
                continue
        
        return news_items


# Example usage
if __name__ == "__main__":
    fetcher = CryptoNewsFetcher()
    
    print("🗞️  Fetching BTC news from last hour...")
    btc_news = fetcher.fetch_news('BTC', hours=1)
    
    print(f"\n📊 Found {len(btc_news)} BTC news articles:\n")
    for item in btc_news[:5]:  # Show first 5
        print(f"📰 {item['title']}")
        print(f"   Source: {item['source']} | {item['published'].strftime('%Y-%m-%d %H:%M')}")
        print(f"   {item['summary'][:100]}...")
        print()

