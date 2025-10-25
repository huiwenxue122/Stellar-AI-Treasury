# 🚀 Trading System Enhancements - Implementation Plan

## 📋 Goals

1. **Rule-Based Trading Logic** (Trend + News Sentiment)
2. **Crypto News Sentiment Analysis** (RSS/Scraper with hourly updates)
3. **Risk Agent Position Sizing Cap** (Dynamic limits based on risk metrics)

---

## 🎯 Goal 1: Rule-Based Trading Logic

### 📊 Trend + Sentiment Strategy

#### Components:
```python
# Trend Detection (Technical)
- Moving Averages: SMA(50), SMA(200)
- RSI: Relative Strength Index
- MACD: Moving Average Convergence Divergence
- Volume: Trading volume analysis

# Sentiment Flag (Fundamental)
- News Sentiment: Positive/Negative/Neutral
- Social Media Sentiment (optional)
- Market Fear/Greed Index
```

#### Trading Rules:
```python
def rule_based_signal(asset, price_data, sentiment):
    """
    Combined trend + sentiment strategy
    
    BUY Conditions:
    - SMA(50) > SMA(200) (Golden Cross)
    - RSI < 70 (Not overbought)
    - Volume > Average
    - Sentiment: Positive or Neutral
    
    SELL Conditions:
    - SMA(50) < SMA(200) (Death Cross)
    - RSI > 80 (Overbought)
    - Sentiment: Negative
    
    HOLD Otherwise
    """
    
    # Calculate technical indicators
    trend = calculate_trend(price_data)
    rsi = calculate_rsi(price_data)
    volume_signal = analyze_volume(price_data)
    
    # Combine with sentiment
    if trend == 'bullish' and sentiment == 'positive' and rsi < 70:
        return {'signal': 'BUY', 'confidence': 0.8}
    elif trend == 'bearish' or sentiment == 'negative':
        return {'signal': 'SELL', 'confidence': 0.7}
    else:
        return {'signal': 'HOLD', 'confidence': 0.5}
```

#### Implementation File Structure:
```
agents/
├── trading_strategies/
│   ├── __init__.py
│   ├── rule_based_strategy.py     # NEW: Core rule-based logic
│   ├── technical_indicators.py    # NEW: SMA, RSI, MACD, etc.
│   └── sentiment_integration.py   # NEW: Combine tech + sentiment
```

#### Benefits:
- ✅ **Transparent**: Easy to understand and explain
- ✅ **Fast**: No ML training needed
- ✅ **Backtestable**: Clear rules for historical testing
- ✅ **Complementary**: Works alongside existing ML/RL strategies

---

## 🗞️ Goal 2: Crypto News Sentiment Analysis

### 📡 News Sources (Free APIs)

#### Recommended Sources:
1. **CryptoPanic API** (Free tier: 500 req/day)
   - URL: `https://cryptopanic.com/api/v1/posts/`
   - Features: Aggregated crypto news, social sentiment
   - Rate limit: Perfect for hourly updates

2. **CoinGecko News** (Already free)
   - URL: `https://api.coingecko.com/api/v3/news`
   - Features: Curated crypto news

3. **RSS Feeds** (No limits)
   - CoinDesk RSS: `https://www.coindesk.com/arc/outboundfeeds/rss/`
   - Cointelegraph RSS: `https://cointelegraph.com/rss`
   - Bitcoin Magazine: `https://bitcoinmagazine.com/feed`

#### Architecture:
```
┌─────────────────────────────────────────────────────┐
│           News Sentiment Pipeline                    │
└─────────────────────────────────────────────────────┘
                      ↓
    ┌─────────────────────────────────┐
    │  1. News Fetcher (Hourly Cron)  │
    │  - Fetch from CryptoPanic/RSS   │
    │  - Filter by asset keywords     │
    └─────────────────────────────────┘
                      ↓
    ┌─────────────────────────────────┐
    │  2. Sentiment Analyzer          │
    │  - Use OpenAI GPT-4 (few-shot)  │
    │  - OR TextBlob (free, offline)  │
    │  - Output: pos/neg/neutral      │
    └─────────────────────────────────┘
                      ↓
    ┌─────────────────────────────────┐
    │  3. Sentiment Aggregator        │
    │  - Aggregate by asset           │
    │  - Weight by source credibility │
    │  - Cache for 1 hour             │
    └─────────────────────────────────┘
                      ↓
    ┌─────────────────────────────────┐
    │  4. Expose to Trading Agent     │
    │  - market_data['sentiment']     │
    │  - Use in rule-based strategy   │
    └─────────────────────────────────┘
```

#### Implementation:

##### File Structure:
```
news/
├── __init__.py
├── news_fetcher.py           # NEW: Fetch from APIs/RSS
├── sentiment_analyzer.py     # NEW: Analyze sentiment
├── sentiment_cache.py        # NEW: Cache results (1 hour TTL)
└── config.py                 # NEW: API keys, RSS URLs
```

##### Code Sketch:

```python
# news/news_fetcher.py
import feedparser
import requests
from datetime import datetime, timedelta

class CryptoNewsFetcher:
    def __init__(self):
        self.sources = {
            'cryptopanic': 'https://cryptopanic.com/api/v1/posts/',
            'coindesk_rss': 'https://www.coindesk.com/arc/outboundfeeds/rss/',
            'cointelegraph_rss': 'https://cointelegraph.com/rss'
        }
        self.asset_keywords = {
            'BTC': ['bitcoin', 'btc'],
            'ETH': ['ethereum', 'eth'],
            'SOL': ['solana', 'sol'],
            # ... more assets
        }
    
    def fetch_news(self, asset, hours=1):
        """Fetch news for asset from last N hours"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        news_items = []
        
        # Fetch from CryptoPanic API
        news_items.extend(self._fetch_cryptopanic(asset))
        
        # Fetch from RSS feeds
        news_items.extend(self._fetch_rss_feeds(asset))
        
        # Filter by time
        recent_news = [
            item for item in news_items 
            if item['published'] > cutoff_time
        ]
        
        return recent_news
    
    def _fetch_cryptopanic(self, asset):
        """Fetch from CryptoPanic API"""
        params = {
            'auth_token': 'YOUR_FREE_TOKEN',  # Get from cryptopanic.com
            'currencies': asset,
            'kind': 'news'
        }
        response = requests.get(self.sources['cryptopanic'], params=params)
        # Parse and return
        return response.json().get('results', [])
    
    def _fetch_rss_feeds(self, asset):
        """Fetch from RSS feeds and filter by keywords"""
        keywords = self.asset_keywords.get(asset, [])
        news_items = []
        
        for source_name, rss_url in self.sources.items():
            if 'rss' in source_name:
                feed = feedparser.parse(rss_url)
                for entry in feed.entries:
                    # Check if asset mentioned in title/summary
                    text = (entry.title + ' ' + entry.summary).lower()
                    if any(kw in text for kw in keywords):
                        news_items.append({
                            'title': entry.title,
                            'summary': entry.summary,
                            'published': entry.published_parsed,
                            'source': source_name
                        })
        
        return news_items
```

```python
# news/sentiment_analyzer.py
from textblob import TextBlob  # Free, no API needed
import openai

class SentimentAnalyzer:
    def __init__(self, method='textblob'):
        """
        method: 'textblob' (free, fast) or 'openai' (better, costs $)
        """
        self.method = method
    
    def analyze(self, text):
        """Analyze sentiment of text
        
        Returns:
            {
                'sentiment': 'positive' | 'negative' | 'neutral',
                'score': -1.0 to 1.0,
                'confidence': 0.0 to 1.0
            }
        """
        if self.method == 'textblob':
            return self._analyze_textblob(text)
        elif self.method == 'openai':
            return self._analyze_openai(text)
    
    def _analyze_textblob(self, text):
        """Free sentiment analysis using TextBlob"""
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity  # -1 to 1
        
        if polarity > 0.1:
            sentiment = 'positive'
        elif polarity < -0.1:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
        
        return {
            'sentiment': sentiment,
            'score': polarity,
            'confidence': abs(polarity)
        }
    
    def _analyze_openai(self, text):
        """Better sentiment using OpenAI (costs ~$0.001 per analysis)"""
        prompt = f"""Analyze the sentiment of this crypto news:

"{text}"

Is it POSITIVE, NEGATIVE, or NEUTRAL for the asset's price?
Answer in one word only."""
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=10
        )
        
        sentiment = response.choices[0].message.content.strip().lower()
        
        return {
            'sentiment': sentiment,
            'score': 0.5 if sentiment == 'positive' else -0.5 if sentiment == 'negative' else 0,
            'confidence': 0.8
        }
    
    def aggregate_sentiment(self, news_items):
        """Aggregate sentiment from multiple news items"""
        if not news_items:
            return {'sentiment': 'neutral', 'score': 0, 'confidence': 0}
        
        sentiments = []
        for item in news_items:
            text = item['title'] + ' ' + item.get('summary', '')
            result = self.analyze(text)
            sentiments.append(result)
        
        # Calculate weighted average
        avg_score = sum(s['score'] for s in sentiments) / len(sentiments)
        
        if avg_score > 0.1:
            overall = 'positive'
        elif avg_score < -0.1:
            overall = 'negative'
        else:
            overall = 'neutral'
        
        return {
            'sentiment': overall,
            'score': avg_score,
            'confidence': sum(s['confidence'] for s in sentiments) / len(sentiments),
            'news_count': len(news_items)
        }
```

```python
# news/sentiment_cache.py
from datetime import datetime, timedelta
from typing import Dict, Optional

class SentimentCache:
    """Cache sentiment results for 1 hour to avoid redundant API calls"""
    
    def __init__(self, ttl_minutes=60):
        self.cache: Dict[str, dict] = {}
        self.ttl = timedelta(minutes=ttl_minutes)
    
    def get(self, asset: str) -> Optional[dict]:
        """Get cached sentiment for asset"""
        if asset in self.cache:
            entry = self.cache[asset]
            if datetime.now() - entry['timestamp'] < self.ttl:
                return entry['sentiment']
            else:
                # Expired, remove
                del self.cache[asset]
        return None
    
    def set(self, asset: str, sentiment: dict):
        """Cache sentiment result"""
        self.cache[asset] = {
            'sentiment': sentiment,
            'timestamp': datetime.now()
        }
    
    def clear_expired(self):
        """Clear all expired entries"""
        now = datetime.now()
        expired = [
            asset for asset, entry in self.cache.items()
            if now - entry['timestamp'] >= self.ttl
        ]
        for asset in expired:
            del self.cache[asset]
```

#### Integration with Trading System:

```python
# agents/trading.py (update)

from news.news_fetcher import CryptoNewsFetcher
from news.sentiment_analyzer import SentimentAnalyzer
from news.sentiment_cache import SentimentCache

class TradingAgent:
    def __init__(self, config):
        # ... existing code ...
        
        # NEW: News sentiment system
        self.news_fetcher = CryptoNewsFetcher()
        self.sentiment_analyzer = SentimentAnalyzer(method='textblob')  # Free
        self.sentiment_cache = SentimentCache(ttl_minutes=60)
    
    def get_market_sentiment(self, asset: str) -> dict:
        """Get current market sentiment for asset"""
        
        # Check cache first
        cached = self.sentiment_cache.get(asset)
        if cached:
            return cached
        
        # Fetch news
        news = self.news_fetcher.fetch_news(asset, hours=1)
        
        # Analyze sentiment
        sentiment = self.sentiment_analyzer.aggregate_sentiment(news)
        
        # Cache result
        self.sentiment_cache.set(asset, sentiment)
        
        return sentiment
    
    async def generate_signal(self, asset: str, market_data: dict):
        """Generate trading signal with sentiment"""
        
        # Get sentiment
        sentiment = self.get_market_sentiment(asset)
        
        # Add to market data
        market_data['sentiment'] = sentiment
        
        # Use in rule-based strategy
        signal = self.rule_based_strategy(asset, market_data)
        
        return signal
```

#### Cost Estimate:
- **TextBlob (Free)**: $0/month, offline, decent accuracy
- **CryptoPanic API (Free tier)**: 500 requests/day = enough for hourly updates on 20 assets
- **OpenAI Sentiment (Optional)**: ~$0.001 per analysis × 24 hours × 10 assets = $0.24/day = **$7/month**

**Recommendation**: Start with **TextBlob (free)**, upgrade to OpenAI if needed.

---

## 🛡️ Goal 3: Risk Agent Position Sizing Cap

### 📊 Dynamic Position Limits

#### Current vs Enhanced:

| Feature | Current | Enhanced |
|---------|---------|----------|
| Max single asset | Fixed 30-50% | Dynamic based on volatility |
| Total exposure | Fixed 80% | Adjusted by VaR |
| Stop loss | None | Asset-specific |
| Correlation | Not considered | Reduce correlated positions |

#### Implementation:

```python
# agents/risk.py (enhance existing)

class RiskAgent:
    def calculate_position_size(self, asset: str, signal: dict, portfolio: dict) -> float:
        """
        Calculate maximum position size for asset based on risk metrics
        
        Factors:
        1. Asset volatility (higher vol = smaller position)
        2. Current portfolio VaR
        3. Correlation with existing positions
        4. User tier limits
        5. Sentiment risk (negative news = reduce size)
        
        Returns:
            position_size: Percentage of portfolio (0.0 to 1.0)
        """
        
        # 1. Get tier-based max
        tier_config = self.tier_manager.get_tier_config(self.current_tier)
        max_allowed = tier_config.max_single_asset_percent / 100  # 30% → 0.3
        
        # 2. Adjust for volatility
        volatility = self.calculate_volatility(asset)
        vol_adjustment = self._volatility_scaling(volatility)
        
        # 3. Adjust for current portfolio VaR
        current_var = self.calculate_portfolio_var(portfolio)
        target_var = tier_config.max_portfolio_var
        var_headroom = max(0, (target_var - current_var) / target_var)
        
        # 4. Adjust for correlation (reduce if highly correlated)
        correlation_penalty = self._calculate_correlation_penalty(asset, portfolio)
        
        # 5. Adjust for sentiment (reduce if negative news)
        sentiment = signal.get('sentiment', {})
        sentiment_adjustment = self._sentiment_scaling(sentiment)
        
        # Calculate final position size
        position_size = (
            max_allowed 
            * vol_adjustment 
            * var_headroom 
            * (1 - correlation_penalty)
            * sentiment_adjustment
        )
        
        # Enforce minimum (if too small, don't trade)
        if position_size < 0.05:  # Less than 5%
            return 0
        
        return min(position_size, max_allowed)
    
    def _volatility_scaling(self, volatility: float) -> float:
        """Scale position size inversely with volatility
        
        Low volatility (0.1): 100% of max
        Medium volatility (0.3): 70% of max
        High volatility (0.5+): 50% of max
        """
        if volatility < 0.2:
            return 1.0
        elif volatility < 0.4:
            return 0.7
        else:
            return 0.5
    
    def _calculate_correlation_penalty(self, asset: str, portfolio: dict) -> float:
        """Reduce position if highly correlated with existing holdings
        
        Example: If portfolio has 40% BTC, reduce ETH position (highly correlated)
        """
        # Get correlations (from historical data or config)
        high_correlation_pairs = {
            ('BTC', 'ETH'): 0.8,
            ('ETH', 'LINK'): 0.7,
            ('SOL', 'FET'): 0.6,
        }
        
        penalty = 0
        for existing_asset, weight in portfolio.items():
            pair = tuple(sorted([asset, existing_asset]))
            correlation = high_correlation_pairs.get(pair, 0)
            
            if correlation > 0.6:
                # Penalize based on correlation and existing weight
                penalty += correlation * weight
        
        return min(penalty, 0.5)  # Cap penalty at 50%
    
    def _sentiment_scaling(self, sentiment: dict) -> float:
        """Reduce position size if negative sentiment
        
        Positive: 100% of calculated size
        Neutral: 90%
        Negative: 60%
        """
        sentiment_type = sentiment.get('sentiment', 'neutral')
        
        if sentiment_type == 'positive':
            return 1.0
        elif sentiment_type == 'neutral':
            return 0.9
        else:  # negative
            return 0.6
    
    def enforce_position_limits(self, proposed_trades: list) -> list:
        """Enforce position size limits on proposed trades
        
        This is called BEFORE execution to cap any oversized positions
        """
        capped_trades = []
        
        for trade in proposed_trades:
            asset = trade['asset']
            proposed_size = trade['position_size']
            
            # Calculate max allowed
            max_size = self.calculate_position_size(
                asset=asset,
                signal=trade.get('signal', {}),
                portfolio=self.get_current_portfolio()
            )
            
            if proposed_size > max_size:
                print(f"⚠️  Capping {asset} position: {proposed_size:.1%} → {max_size:.1%}")
                trade['position_size'] = max_size
                trade['capped'] = True
            
            capped_trades.append(trade)
        
        return capped_trades
```

#### Integration with Multi-Agent System:

```python
# agents/agent_system_with_function_tools.py (update)

class MultiAgentOrchestratorWithTools:
    
    async def run_multi_agent_cycle(self):
        """Enhanced with position sizing caps"""
        
        # 1. Trading Agent generates signals
        portfolio = await self._trading_agent_with_tools(market_data)
        
        # 2. Risk Agent evaluates AND CAPS positions
        risk_evaluation = await self._risk_agent_evaluate_portfolio(portfolio, market_data)
        
        if risk_evaluation['approved']:
            # 3. BEFORE payment agent executes, enforce position limits
            capped_portfolio = self.risk_agent.enforce_position_limits(portfolio)
            
            # 4. Payment Agent executes with capped positions
            execution_result = await self._payment_agent_execute(capped_portfolio)
            
            return execution_result
        else:
            return {'status': 'REJECTED', 'reason': risk_evaluation['reason']}
```

---

## 📊 Complete Flow Diagram

```
┌─────────────────────────────────────────────────────┐
│              Enhanced Trading Cycle                  │
└─────────────────────────────────────────────────────┘
                      ↓
    ┌─────────────────────────────────┐
    │  1. Fetch Market Data           │
    │  - Price, volume, technical     │
    └─────────────────────────────────┘
                      ↓
    ┌─────────────────────────────────┐
    │  2. Fetch News Sentiment (NEW)  │ ← Hourly cache
    │  - CryptoPanic API              │
    │  - RSS feeds                    │
    │  - TextBlob sentiment           │
    └─────────────────────────────────┘
                      ↓
    ┌─────────────────────────────────┐
    │  3. Rule-Based Strategy (NEW)   │
    │  - Trend: SMA, RSI, MACD        │
    │  - Sentiment: pos/neg/neutral   │
    │  - Signal: BUY/SELL/HOLD        │
    └─────────────────────────────────┘
                      ↓
    ┌─────────────────────────────────┐
    │  4. ML/RL Strategies            │
    │  - Existing 10 strategies       │
    │  - Function calling tools       │
    └─────────────────────────────────┘
                      ↓
    ┌─────────────────────────────────┐
    │  5. Portfolio Optimization      │
    │  - Combine signals              │
    │  - Propose positions            │
    └─────────────────────────────────┘
                      ↓
    ┌─────────────────────────────────┐
    │  6. Risk Agent Position Cap (NEW)│
    │  - Calculate max position size  │
    │  - Consider:                    │
    │    • Volatility                 │
    │    • Current VaR                │
    │    • Correlation                │
    │    • Sentiment                  │
    │  - Cap oversized positions      │
    └─────────────────────────────────┘
                      ↓
    ┌─────────────────────────────────┐
    │  7. Risk Evaluation             │
    │  - Check portfolio metrics      │
    │  - Approve/Reject               │
    └─────────────────────────────────┘
                      ↓
    ┌─────────────────────────────────┐
    │  8. Payment Agent Execution     │
    │  - Execute capped trades        │
    │  - Settle to USDC               │
    └─────────────────────────────────┘
```

---

## 🎯 Implementation Priority

### Phase 1: Foundation (1-2 days)
1. ✅ Technical indicators module (`technical_indicators.py`)
   - SMA, RSI, MACD, Volume
2. ✅ Rule-based strategy (`rule_based_strategy.py`)
   - Trend + basic logic
3. ✅ Position sizing in Risk Agent
   - Volatility-based scaling

### Phase 2: News Integration (2-3 days)
1. ✅ News fetcher (`news_fetcher.py`)
   - CryptoPanic API
   - RSS feeds
2. ✅ Sentiment analyzer (`sentiment_analyzer.py`)
   - TextBlob (free)
3. ✅ Sentiment cache (`sentiment_cache.py`)
4. ✅ Integrate with rule-based strategy

### Phase 3: Advanced Risk (1-2 days)
1. ✅ Correlation analysis
2. ✅ Sentiment-based position adjustment
3. ✅ Dynamic VaR-based limits
4. ✅ Dashboard display of position caps

### Phase 4: Testing & Tuning (1-2 days)
1. ✅ Backtest rule-based strategy
2. ✅ Test news sentiment accuracy
3. ✅ Verify position caps work correctly
4. ✅ Dashboard visualization

**Total Time**: ~1 week

---

## 💰 Cost Analysis

| Component | Cost | Notes |
|-----------|------|-------|
| **Technical Indicators** | $0 | Pure calculation |
| **CryptoPanic API** | $0 | Free tier (500/day) |
| **RSS Feeds** | $0 | Unlimited |
| **TextBlob Sentiment** | $0 | Offline library |
| **OpenAI Sentiment (optional)** | ~$7/month | If you want better accuracy |
| **Total** | **$0-7/month** | Start free, upgrade if needed |

---

## 📈 Expected Benefits

### 1. Rule-Based Strategy
- ✅ **Transparency**: Easy to explain to judges
- ✅ **Reliability**: Proven technical indicators
- ✅ **Speed**: Real-time decisions without ML inference
- ✅ **Baseline**: Compare ML strategies against this baseline

### 2. News Sentiment
- ✅ **Fundamental Analysis**: Complement technical analysis
- ✅ **Real-World Integration**: Show awareness of market events
- ✅ **Risk Awareness**: Avoid trading during negative news
- ✅ **Competitive Edge**: Most competitors don't have this

### 3. Position Sizing Cap
- ✅ **Risk Control**: Prevent oversized risky positions
- ✅ **Dynamic**: Adapts to market conditions
- ✅ **Professional**: Shows sophisticated risk management
- ✅ **User Safety**: Especially important for beginner tier

---

## 🚀 Quick Start

Want me to implement this? I can start with:

1. **Technical Indicators Module** (30 min)
   - Clean, well-tested functions
   - SMA, RSI, MACD, Volume

2. **Rule-Based Strategy** (1 hour)
   - Combine indicators
   - Add as OpenAI Function Tool
   - Integrate with Trading Agent

3. **News Sentiment (Basic)** (2 hours)
   - CryptoPanic API integration
   - TextBlob sentiment
   - Hourly cache

4. **Position Sizing** (1 hour)
   - Enhance Risk Agent
   - Volatility-based caps
   - Sentiment adjustment

**Total**: ~4-5 hours of implementation

---

## 🤔 Questions for You

1. **Priority**: Which goal is most important? (I suggest: 3 → 1 → 2)
2. **Sentiment Method**: Start with free TextBlob or pay for OpenAI?
3. **News Sources**: CryptoPanic only, or add RSS too?
4. **Dashboard**: Do you want to display sentiment scores in UI?

Let me know and I'll start coding! 🚀

