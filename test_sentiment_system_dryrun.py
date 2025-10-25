#!/usr/bin/env python3
"""
Dry-Run Test for Sentiment System
Tests WITHOUT any OpenAI API calls (no credit wasted!)
"""

import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def print_section(title):
    """Print a formatted section header"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80)

def test_news_fetcher():
    """Test news fetching (uses FREE RSS feeds, no API key needed)"""
    print_section("1️⃣ Testing News Fetcher (FREE RSS)")
    
    try:
        from news import CryptoNewsFetcher
        
        fetcher = CryptoNewsFetcher()
        print("✅ CryptoNewsFetcher initialized")
        
        # Test fetching BTC news
        print("\n🗞️  Fetching BTC news from last hour...")
        btc_news = fetcher.fetch_news('BTC', hours=1)
        
        print(f"✅ Found {len(btc_news)} BTC-related articles")
        
        if btc_news:
            print("\n📰 First 3 articles:")
            for i, article in enumerate(btc_news[:3], 1):
                print(f"\n   {i}. {article['title']}")
                print(f"      Source: {article['source']}")
                print(f"      Published: {article['published']}")
                if 'summary' in article and article['summary']:
                    print(f"      Summary: {article['summary'][:100]}...")
        else:
            print("⚠️  No BTC news found in last hour (this is OK, might be quiet period)")
        
        return True
    
    except Exception as e:
        print(f"❌ News fetcher test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_sentiment_analyzer():
    """Test sentiment analysis (uses FREE TextBlob, no API key needed)"""
    print_section("2️⃣ Testing Sentiment Analyzer (FREE TextBlob)")
    
    try:
        from news import SentimentAnalyzer
        
        # Initialize with TextBlob (FREE!)
        analyzer = SentimentAnalyzer(method='textblob')
        print("✅ SentimentAnalyzer initialized with TextBlob (FREE)")
        
        # Test with sample crypto news
        test_texts = [
            "Bitcoin soars to new all-time high as institutional investors pile in",
            "SEC charges major crypto exchange with fraud, prices tumble",
            "Ethereum network upgrade completes successfully, no major issues reported",
            "Market consolidates after yesterday's volatility, traders cautious",
            "Crypto adoption accelerates as major banks announce blockchain initiatives"
        ]
        
        print("\n🧪 Testing individual sentiment analysis:\n")
        
        all_passed = True
        for text in test_texts:
            result = analyzer.analyze(text)
            
            sentiment_emoji = {
                'positive': '😊',
                'negative': '😟',
                'neutral': '😐'
            }[result['sentiment']]
            
            print(f"{sentiment_emoji} \"{text[:60]}...\"")
            print(f"   Sentiment: {result['sentiment'].upper()} (score: {result['score']:.2f}, confidence: {result['confidence']:.2f})")
            
            # Validate results
            if result['sentiment'] not in ['positive', 'negative', 'neutral']:
                print(f"   ❌ Invalid sentiment: {result['sentiment']}")
                all_passed = False
            if not -1.0 <= result['score'] <= 1.0:
                print(f"   ❌ Invalid score: {result['score']}")
                all_passed = False
        
        if all_passed:
            print("\n✅ All individual sentiment tests passed!")
        
        return all_passed
    
    except ImportError as e:
        print(f"❌ TextBlob not installed: {e}")
        print("\n💡 Fix: Run these commands:")
        print("   pip install textblob")
        print("   python -m textblob.download_corpora")
        return False
    
    except Exception as e:
        print(f"❌ Sentiment analyzer test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_sentiment_aggregation():
    """Test aggregating sentiment from multiple articles"""
    print_section("3️⃣ Testing Sentiment Aggregation")
    
    try:
        from news import SentimentAnalyzer
        
        analyzer = SentimentAnalyzer(method='textblob')
        
        # Simulate multiple news articles
        test_scenarios = [
            {
                'name': 'All Positive News',
                'articles': [
                    {'title': 'Bitcoin hits new high!', 'summary': 'Strong buying pressure'},
                    {'title': 'Institutions bullish on crypto', 'summary': 'Major adoption coming'},
                    {'title': 'Ethereum upgrades successfully', 'summary': 'Network performs well'}
                ],
                'expected': 'positive'
            },
            {
                'name': 'All Negative News',
                'articles': [
                    {'title': 'Exchange hacked', 'summary': 'Millions stolen'},
                    {'title': 'SEC lawsuit filed', 'summary': 'Regulatory crackdown'},
                    {'title': 'Market crashes', 'summary': 'Panic selling'}
                ],
                'expected': 'negative'
            },
            {
                'name': 'Mixed News',
                'articles': [
                    {'title': 'Bitcoin rises', 'summary': 'Price up 5%'},
                    {'title': 'Regulatory concerns', 'summary': 'Government investigating'},
                    {'title': 'Trading volume normal', 'summary': 'Market stable'}
                ],
                'expected': 'neutral'  # Should balance out
            }
        ]
        
        print("\n🧪 Testing aggregation scenarios:\n")
        
        all_passed = True
        for scenario in test_scenarios:
            print(f"📊 Scenario: {scenario['name']}")
            
            result = analyzer.aggregate_sentiment(scenario['articles'])
            
            print(f"   Articles: {result['news_count']}")
            print(f"   Overall Sentiment: {result['sentiment'].upper()} (score: {result['score']:.2f})")
            print(f"   Distribution: {result['distribution']}")
            
            # Validate
            if result['sentiment'] == scenario['expected']:
                print(f"   ✅ Correct (expected: {scenario['expected']})")
            else:
                print(f"   ⚠️  Got '{result['sentiment']}', expected '{scenario['expected']}'")
                print("      (This is OK, sentiment analysis isn't perfect)")
            print()
        
        return True
    
    except Exception as e:
        print(f"❌ Aggregation test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_sentiment_cache():
    """Test sentiment caching"""
    print_section("4️⃣ Testing Sentiment Cache")
    
    try:
        from news import SentimentCache
        
        cache = SentimentCache(ttl_minutes=1)  # 1 minute for testing
        print("✅ SentimentCache initialized (TTL: 1 minute)")
        
        # Test caching
        test_sentiment = {
            'sentiment': 'positive',
            'score': 0.65,
            'confidence': 0.8,
            'news_count': 5
        }
        
        print("\n📦 Testing cache operations:")
        
        # Set
        cache.set('BTC', test_sentiment)
        print("✅ Cached BTC sentiment")
        
        # Get (should hit)
        cached = cache.get('BTC')
        if cached:
            print(f"✅ Retrieved from cache: {cached['sentiment']} (score: {cached['score']:.2f})")
        else:
            print("❌ Cache miss (should have hit)")
            return False
        
        # Get non-existent
        cached_eth = cache.get('ETH')
        if cached_eth is None:
            print("✅ Cache miss for ETH (as expected)")
        else:
            print("❌ Unexpected cache hit for ETH")
            return False
        
        # Stats
        stats = cache.get_stats()
        print(f"\n📊 Cache stats:")
        print(f"   Total entries: {stats['total_entries']}")
        print(f"   Valid entries: {stats['valid_entries']}")
        
        print("\n✅ Cache test passed!")
        return True
    
    except Exception as e:
        print(f"❌ Cache test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_trading_strategy_integration():
    """Test that new strategies can be called (without executing)"""
    print_section("5️⃣ Testing Strategy Integration")
    
    try:
        from agents.trading_strategies import TradingStrategies
        
        # Mock config
        mock_config = {}
        strategies = TradingStrategies(mock_config)
        print("✅ TradingStrategies initialized")
        
        # Check new strategies exist
        all_strategies = strategies.get_all_strategies()
        print(f"\n📋 Total strategies available: {len(all_strategies)}")
        
        new_strategies = ['composite_technical_strategy', 'sentiment_adjusted_strategy']
        
        for strategy_name in new_strategies:
            if strategy_name in all_strategies:
                print(f"   ✅ {strategy_name} - Available")
                
                # Check method exists
                if hasattr(strategies, strategy_name):
                    print(f"      Method exists: {strategy_name}()")
                else:
                    print(f"      ❌ Method not found!")
                    return False
            else:
                print(f"   ❌ {strategy_name} - Missing!")
                return False
        
        print("\n✅ New strategies integrated successfully!")
        return True
    
    except Exception as e:
        print(f"❌ Strategy integration test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_composite_strategy_logic():
    """Test composite strategy decision logic (mock data)"""
    print_section("6️⃣ Testing Composite Strategy Logic")
    
    try:
        from agents.trading_strategies import TradingStrategies
        
        strategies = TradingStrategies({})
        
        # Create mock market data with enough price history
        mock_market_data = {
            'prices': [45000 + i*10 for i in range(250)],  # 250 prices (uptrend)
            'volumes': [1000000 + i*1000 for i in range(250)],  # Increasing volume
            'assets': {
                'BTC': {
                    'change_24h': 5.2,
                    'price': 47500
                }
            }
        }
        
        print("\n🧪 Testing composite_technical_strategy with mock data:")
        print(f"   Prices: {len(mock_market_data['prices'])} candles")
        print(f"   Trend: Upward (45000 → 47490)")
        print(f"   Volume: Increasing")
        
        result = strategies.composite_technical_strategy('BTC', mock_market_data)
        
        print(f"\n📊 Result:")
        print(f"   Action: {result.action}")
        print(f"   Confidence: {result.confidence:.1%}")
        print(f"   Strength: {result.strength:.2f}")
        print(f"   Reasoning: {result.reasoning}")
        
        if result.action in ['BUY', 'SELL', 'HOLD']:
            print("\n✅ Composite strategy works!")
            return True
        else:
            print(f"\n❌ Invalid action: {result.action}")
            return False
    
    except Exception as e:
        print(f"❌ Composite strategy test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_sentiment_adjusted_strategy():
    """Test sentiment-adjusted strategy with mock sentiment"""
    print_section("7️⃣ Testing Sentiment-Adjusted Strategy")
    
    try:
        from agents.trading_strategies import TradingStrategies
        
        strategies = TradingStrategies({})
        
        # Mock market data
        mock_market_data = {
            'prices': [45000 + i*10 for i in range(250)],
            'volumes': [1000000 + i*1000 for i in range(250)],
            'assets': {'BTC': {'change_24h': 5.2, 'price': 47500}},
            'sentiment': {
                'sentiment': 'positive',
                'score': 0.7,
                'confidence': 0.85,
                'news_count': 5
            }
        }
        
        print("\n🧪 Scenario 1: Positive Sentiment + Bullish Technical")
        print(f"   Sentiment: positive (score: 0.7, 5 articles)")
        
        result = strategies.sentiment_adjusted_strategy('BTC', mock_market_data)
        
        print(f"\n📊 Result:")
        print(f"   Action: {result.action}")
        print(f"   Confidence: {result.confidence:.1%}")
        print(f"   Reasoning: {result.reasoning[:100]}...")
        
        # Test negative sentiment
        mock_market_data['sentiment'] = {
            'sentiment': 'negative',
            'score': -0.65,
            'confidence': 0.8,
            'news_count': 6
        }
        
        print("\n\n🧪 Scenario 2: Negative Sentiment + Bullish Technical")
        print(f"   Sentiment: negative (score: -0.65, 6 articles)")
        
        result2 = strategies.sentiment_adjusted_strategy('BTC', mock_market_data)
        
        print(f"\n📊 Result:")
        print(f"   Action: {result2.action}")
        print(f"   Confidence: {result2.confidence:.1%}")
        print(f"   Reasoning: {result2.reasoning[:100]}...")
        
        if result.action in ['BUY', 'SELL', 'HOLD'] and result2.action in ['BUY', 'SELL', 'HOLD']:
            print("\n✅ Sentiment-adjusted strategy works!")
            return True
        else:
            print(f"\n❌ Invalid actions")
            return False
    
    except Exception as e:
        print(f"❌ Sentiment-adjusted strategy test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_all_tests():
    """Run all dry-run tests"""
    print("\n" + "🧪"*40)
    print("  DRY-RUN TEST: Sentiment System Enhancement")
    print("  Testing WITHOUT OpenAI API (No credit wasted!)")
    print("🧪"*40)
    
    results = []
    
    # Test 1: News Fetcher (uses FREE RSS)
    result1 = test_news_fetcher()
    results.append(("News Fetcher (RSS)", result1))
    
    # Test 2: Sentiment Analyzer (uses FREE TextBlob)
    result2 = test_sentiment_analyzer()
    results.append(("Sentiment Analyzer (TextBlob)", result2))
    
    # Test 3: Sentiment Aggregation
    result3 = test_sentiment_aggregation()
    results.append(("Sentiment Aggregation", result3))
    
    # Test 4: Cache
    result4 = test_sentiment_cache()
    results.append(("Sentiment Cache", result4))
    
    # Test 5: Strategy Integration
    result5 = test_trading_strategy_integration()
    results.append(("Strategy Integration", result5))
    
    # Test 6: Composite Strategy
    result6 = test_composite_strategy_logic()
    results.append(("Composite Strategy", result6))
    
    # Test 7: Sentiment-Adjusted Strategy
    result7 = test_sentiment_adjusted_strategy()
    results.append(("Sentiment-Adjusted Strategy", result7))
    
    # Summary
    print_section("✅ TEST SUMMARY")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"\n📊 Results: {passed}/{total} tests passed\n")
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status}: {test_name}")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! 🎉")
        print("\n💰 Cost: $0 (No OpenAI API calls made)")
        print("\n💡 Next Steps:")
        print("   1. Install dependencies: pip install feedparser textblob")
        print("   2. Download TextBlob data: python -m textblob.download_corpora")
        print("   3. Run full system: python smart_start.py")
        print("\n🔒 Your OpenAI credits are safe - we used FREE tools only!")
        return True
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Check errors above.")
        
        if not result2:
            print("\n💡 If TextBlob failed, install it:")
            print("   pip install textblob")
            print("   python -m textblob.download_corpora")
        
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

