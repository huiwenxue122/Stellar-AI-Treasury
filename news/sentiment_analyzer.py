"""
Sentiment Analyzer for Crypto News
Uses TextBlob (free, offline) or OpenAI (better, costs $)
"""

from typing import Dict, List
from textblob import TextBlob


class SentimentAnalyzer:
    """Analyze sentiment of crypto news"""
    
    def __init__(self, method: str = 'textblob'):
        """
        Initialize sentiment analyzer
        
        Args:
            method: 'textblob' (free, fast, offline) or 'openai' (better, costs $)
        """
        self.method = method
        
        if method == 'openai':
            try:
                import openai
                self.openai = openai
            except ImportError:
                print("⚠️  OpenAI not installed, falling back to TextBlob")
                self.method = 'textblob'
    
    def analyze(self, text: str) -> Dict:
        """
        Analyze sentiment of a single text
        
        Args:
            text: News title or summary
        
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
    
    def _analyze_textblob(self, text: str) -> Dict:
        """
        Free sentiment analysis using TextBlob
        
        TextBlob polarity: -1 (negative) to +1 (positive)
        """
        try:
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity  # -1 to 1
            subjectivity = blob.sentiment.subjectivity  # 0 to 1
            
            # Classify sentiment
            if polarity > 0.1:
                sentiment = 'positive'
            elif polarity < -0.1:
                sentiment = 'negative'
            else:
                sentiment = 'neutral'
            
            # Confidence based on how far from neutral
            confidence = min(abs(polarity), 1.0)
            
            return {
                'sentiment': sentiment,
                'score': polarity,
                'confidence': confidence,
                'subjectivity': subjectivity
            }
        
        except Exception as e:
            print(f"TextBlob error: {e}")
            return {
                'sentiment': 'neutral',
                'score': 0.0,
                'confidence': 0.0,
                'subjectivity': 0.5
            }
    
    def _analyze_openai(self, text: str) -> Dict:
        """
        Better sentiment using OpenAI GPT
        
        Cost: ~$0.001 per analysis (very cheap)
        """
        try:
            prompt = f"""Analyze the sentiment of this cryptocurrency news for trading purposes:

"{text}"

Is the sentiment POSITIVE, NEGATIVE, or NEUTRAL for the asset's price?

Respond in this exact format:
Sentiment: [POSITIVE/NEGATIVE/NEUTRAL]
Score: [number from -1.0 to 1.0]
Confidence: [number from 0.0 to 1.0]
Reasoning: [one sentence]"""
            
            response = self.openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=100,
                temperature=0.3
            )
            
            result = response.choices[0].message.content.strip()
            
            # Parse response
            sentiment = 'neutral'
            score = 0.0
            confidence = 0.5
            
            for line in result.split('\n'):
                if 'Sentiment:' in line:
                    sentiment = line.split(':')[1].strip().lower()
                elif 'Score:' in line:
                    try:
                        score = float(line.split(':')[1].strip())
                    except:
                        pass
                elif 'Confidence:' in line:
                    try:
                        confidence = float(line.split(':')[1].strip())
                    except:
                        pass
            
            return {
                'sentiment': sentiment,
                'score': score,
                'confidence': confidence,
                'method': 'openai'
            }
        
        except Exception as e:
            print(f"OpenAI error: {e}, falling back to TextBlob")
            return self._analyze_textblob(text)
    
    def aggregate_sentiment(self, news_items: List[Dict]) -> Dict:
        """
        Aggregate sentiment from multiple news articles
        
        Args:
            news_items: List of news dicts with 'title' and 'summary'
        
        Returns:
            {
                'sentiment': 'positive' | 'negative' | 'neutral',
                'score': -1.0 to 1.0 (average),
                'confidence': 0.0 to 1.0,
                'news_count': int,
                'distribution': {'positive': N, 'negative': N, 'neutral': N}
            }
        """
        if not news_items:
            return {
                'sentiment': 'neutral',
                'score': 0.0,
                'confidence': 0.0,
                'news_count': 0,
                'distribution': {'positive': 0, 'negative': 0, 'neutral': 0}
            }
        
        sentiments = []
        distribution = {'positive': 0, 'negative': 0, 'neutral': 0}
        
        for item in news_items:
            # Combine title and summary for better analysis
            text = item.get('title', '') + '. ' + item.get('summary', '')
            
            result = self.analyze(text)
            sentiments.append(result)
            
            # Count distribution
            distribution[result['sentiment']] += 1
        
        # Calculate weighted average score
        # Weight by confidence (more confident predictions count more)
        total_weight = sum(s['confidence'] for s in sentiments)
        
        if total_weight > 0:
            weighted_score = sum(
                s['score'] * s['confidence'] for s in sentiments
            ) / total_weight
        else:
            weighted_score = sum(s['score'] for s in sentiments) / len(sentiments)
        
        # Determine overall sentiment
        if weighted_score > 0.15:
            overall = 'positive'
        elif weighted_score < -0.15:
            overall = 'negative'
        else:
            overall = 'neutral'
        
        # Average confidence
        avg_confidence = sum(s['confidence'] for s in sentiments) / len(sentiments)
        
        return {
            'sentiment': overall,
            'score': weighted_score,
            'confidence': avg_confidence,
            'news_count': len(news_items),
            'distribution': distribution,
            'details': sentiments  # Include individual sentiments for debugging
        }


# Example usage
if __name__ == "__main__":
    analyzer = SentimentAnalyzer(method='textblob')
    
    # Test individual texts
    test_texts = [
        "Bitcoin soars to new all-time high as institutions pile in",
        "SEC charges major exchange with fraud",
        "Ethereum upgrades successfully, network stable"
    ]
    
    print("📊 Testing individual sentiment analysis:\n")
    for text in test_texts:
        result = analyzer.analyze(text)
        print(f"Text: {text}")
        print(f"Sentiment: {result['sentiment']} (score: {result['score']:.2f}, confidence: {result['confidence']:.2f})")
        print()
    
    # Test aggregation
    print("\n📊 Testing sentiment aggregation:\n")
    news = [
        {'title': t, 'summary': ''} for t in test_texts
    ]
    
    agg_result = analyzer.aggregate_sentiment(news)
    print(f"Overall Sentiment: {agg_result['sentiment']}")
    print(f"Score: {agg_result['score']:.2f}")
    print(f"Confidence: {agg_result['confidence']:.2f}")
    print(f"News Count: {agg_result['news_count']}")
    print(f"Distribution: {agg_result['distribution']}")

