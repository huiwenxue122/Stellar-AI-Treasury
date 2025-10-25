"""
News Sentiment Module
Provides crypto news fetching and sentiment analysis
"""

from .news_fetcher import CryptoNewsFetcher
from .sentiment_analyzer import SentimentAnalyzer
from .sentiment_cache import SentimentCache, get_global_cache

__all__ = [
    'CryptoNewsFetcher',
    'SentimentAnalyzer',
    'SentimentCache',
    'get_global_cache'
]

