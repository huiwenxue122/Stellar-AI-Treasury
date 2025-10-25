#!/usr/bin/env python3
"""
情境特征构建
构造regime特征（趋势、波动、%b、ATR、成交量代理、情绪分等）
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')

# 导入新闻情感分析
try:
    from news import SentimentAnalyzer, get_global_cache
    NEWS_AVAILABLE = True
except ImportError:
    NEWS_AVAILABLE = False

def build_regime_features(prices: pd.Series, vol_lookback: int = 20, 
                         additional_features: Optional[pd.DataFrame] = None) -> pd.DataFrame:
    """
    构建regime特征
    
    Args:
        prices: 价格序列
        vol_lookback: 波动率回望期
        additional_features: 额外特征数据框
        
    Returns:
        特征数据框，索引与价格对齐
    """
    features = pd.DataFrame(index=prices.index)
    
    # 基础价格特征
    features['price'] = prices
    features['returns'] = prices.pct_change()
    features['log_returns'] = np.log(prices / prices.shift(1))
    
    # 趋势特征
    features.update(_build_trend_features(prices))
    
    # 波动率特征
    features.update(_build_volatility_features(prices, vol_lookback))
    
    # 布林带特征
    features.update(_build_bollinger_features(prices))
    
    # ATR特征
    features.update(_build_atr_features(prices))
    
    # 成交量代理特征
    features.update(_build_volume_proxy_features(prices))
    
    # 情绪特征
    features.update(_build_sentiment_features(prices))
    
    # 市场状态特征
    features.update(_build_market_state_features(prices))
    
    # 技术指标特征
    features.update(_build_technical_features(prices))
    
    # 📰 新闻情感特征
    if NEWS_AVAILABLE:
        features.update(_build_news_sentiment_features(prices))
    
    # 合并额外特征
    if additional_features is not None:
        features = pd.concat([features, additional_features], axis=1)
    
    # 清理数据
    features = features.fillna(method='ffill').fillna(0)
    
    return features

def _build_trend_features(prices: pd.Series) -> Dict[str, pd.Series]:
    """构建趋势特征"""
    features = {}
    
    # 移动平均线
    features['sma_5'] = prices.rolling(5).mean()
    features['sma_10'] = prices.rolling(10).mean()
    features['sma_20'] = prices.rolling(20).mean()
    features['sma_50'] = prices.rolling(50).mean()
    
    # 指数移动平均线
    features['ema_12'] = prices.ewm(span=12).mean()
    features['ema_26'] = prices.ewm(span=26).mean()
    
    # 趋势强度
    features['trend_strength_5'] = (prices - features['sma_5']) / features['sma_5']
    features['trend_strength_20'] = (prices - features['sma_20']) / features['sma_20']
    features['trend_strength_50'] = (prices - features['sma_50']) / features['sma_50']
    
    # 趋势方向
    features['trend_direction_5'] = np.where(features['trend_strength_5'] > 0, 1, -1)
    features['trend_direction_20'] = np.where(features['trend_strength_20'] > 0, 1, -1)
    features['trend_direction_50'] = np.where(features['trend_strength_50'] > 0, 1, -1)
    
    # 趋势一致性
    features['trend_consistency'] = (
        features['trend_direction_5'] + 
        features['trend_direction_20'] + 
        features['trend_direction_50']
    ) / 3
    
    return features

def _build_volatility_features(prices: pd.Series, lookback: int) -> Dict[str, pd.Series]:
    """构建波动率特征"""
    features = {}
    
    returns = prices.pct_change()
    
    # 滚动波动率
    features['volatility_5'] = returns.rolling(5).std() * np.sqrt(252)
    features['volatility_10'] = returns.rolling(10).std() * np.sqrt(252)
    features['volatility_20'] = returns.rolling(20).std() * np.sqrt(252)
    features['volatility_50'] = returns.rolling(50).std() * np.sqrt(252)
    
    # 波动率比率
    features['vol_ratio_5_20'] = features['volatility_5'] / features['volatility_20']
    features['vol_ratio_10_50'] = features['volatility_10'] / features['volatility_50']
    
    # 波动率趋势
    features['vol_trend_5'] = features['volatility_5'].pct_change(5)
    features['vol_trend_20'] = features['volatility_20'].pct_change(20)
    
    # 波动率状态 - 使用简单阈值
    vol_median = features['volatility_20'].median()
    features['vol_state'] = np.where(features['volatility_20'] < vol_median, 'low', 'high')
    
    return features

def _build_bollinger_features(prices: pd.Series) -> Dict[str, pd.Series]:
    """构建布林带特征"""
    features = {}
    
    # 布林带
    sma_20 = prices.rolling(20).mean()
    std_20 = prices.rolling(20).std()
    features['bb_upper'] = sma_20 + (2 * std_20)
    features['bb_lower'] = sma_20 - (2 * std_20)
    features['bb_middle'] = sma_20
    features['bb_width'] = (features['bb_upper'] - features['bb_lower']) / features['bb_middle']
    
    # 布林带位置
    features['bb_position'] = (prices - features['bb_lower']) / (features['bb_upper'] - features['bb_lower'])
    
    # 布林带状态
    features['bb_state'] = pd.cut(
        features['bb_position'],
        bins=[0, 0.2, 0.8, 1.0],
        labels=['oversold', 'neutral', 'overbought']
    )
    
    return features

def _build_atr_features(prices: pd.Series) -> Dict[str, pd.Series]:
    """构建ATR特征"""
    features = {}
    
    # 简化的ATR计算（使用价格变化作为代理）
    high = prices.rolling(2).max()
    low = prices.rolling(2).min()
    close_prev = prices.shift(1)
    
    tr1 = high - low
    tr2 = np.abs(high - close_prev)
    tr3 = np.abs(low - close_prev)
    
    true_range = np.maximum(tr1, np.maximum(tr2, tr3))
    features['atr_14'] = true_range.rolling(14).mean()
    features['atr_21'] = true_range.rolling(21).mean()
    
    # ATR比率
    features['atr_ratio'] = features['atr_14'] / features['atr_21']
    
    # ATR状态 - 使用简单阈值
    atr_median = features['atr_14'].median()
    features['atr_state'] = np.where(features['atr_14'] < atr_median, 'low', 'high')
    
    return features

def _build_volume_proxy_features(prices: pd.Series) -> Dict[str, pd.Series]:
    """构建成交量代理特征"""
    features = {}
    
    # 价格变化幅度作为成交量代理
    features['price_change_abs'] = np.abs(prices.pct_change())
    features['price_change_5'] = prices.pct_change(5)
    features['price_change_10'] = prices.pct_change(10)
    
    # 成交量代理指标
    features['volume_proxy_5'] = features['price_change_abs'].rolling(5).mean()
    features['volume_proxy_20'] = features['price_change_abs'].rolling(20).mean()
    
    # 成交量比率
    features['volume_ratio'] = features['volume_proxy_5'] / features['volume_proxy_20']
    
    # 成交量状态 - 使用简单阈值
    vol_median = features['volume_proxy_20'].median()
    features['volume_state'] = np.where(features['volume_proxy_20'] < vol_median, 'low', 'high')
    
    return features

def _build_sentiment_features(prices: pd.Series) -> Dict[str, pd.Series]:
    """构建情绪特征"""
    features = {}
    
    # RSI作为情绪指标
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss
    features['rsi'] = 100 - (100 / (1 + rs))
    
    # 情绪状态
    features['sentiment_state'] = pd.cut(
        features['rsi'],
        bins=[0, 30, 70, 100],
        labels=['bearish', 'neutral', 'bullish']
    )
    
    # 情绪强度
    features['sentiment_strength'] = np.abs(features['rsi'] - 50) / 50
    
    # 情绪趋势
    features['sentiment_trend'] = features['rsi'].pct_change(5)
    
    return features

def _build_market_state_features(prices: pd.Series) -> Dict[str, pd.Series]:
    """构建市场状态特征"""
    features = {}
    
    # 市场状态分类
    returns = prices.pct_change()
    
    # 趋势状态
    sma_20 = prices.rolling(20).mean()
    sma_50 = prices.rolling(50).mean()
    features['market_trend'] = np.where(sma_20 > sma_50, 1, -1)
    
    # 波动状态 - 使用简单阈值
    volatility = returns.rolling(20).std()
    vol_median = volatility.median()
    features['market_volatility'] = np.where(volatility < vol_median, 'low', 'high')
    
    # 市场状态组合
    features['market_state'] = features['market_trend'].astype(str) + '_' + features['market_volatility'].astype(str)
    
    return features

def _build_technical_features(prices: pd.Series) -> Dict[str, pd.Series]:
    """构建技术指标特征"""
    features = {}
    
    # MACD
    ema_12 = prices.ewm(span=12).mean()
    ema_26 = prices.ewm(span=26).mean()
    features['macd'] = ema_12 - ema_26
    features['macd_signal'] = features['macd'].ewm(span=9).mean()
    features['macd_histogram'] = features['macd'] - features['macd_signal']
    
    # MACD状态
    features['macd_state'] = np.where(features['macd'] > features['macd_signal'], 1, -1)
    
    # 动量指标
    features['momentum_5'] = prices.pct_change(5)
    features['momentum_10'] = prices.pct_change(10)
    features['momentum_20'] = prices.pct_change(20)
    
    # 动量状态
    features['momentum_state'] = np.where(features['momentum_20'] > 0, 1, -1)
    
    return features

def get_feature_names() -> list:
    """获取所有特征名称"""
    # 这里返回所有可能的特征名称
    return [
        'price', 'returns', 'log_returns',
        'sma_5', 'sma_10', 'sma_20', 'sma_50',
        'ema_12', 'ema_26',
        'trend_strength_5', 'trend_strength_20', 'trend_strength_50',
        'trend_direction_5', 'trend_direction_20', 'trend_direction_50',
        'trend_consistency',
        'volatility_5', 'volatility_10', 'volatility_20', 'volatility_50',
        'vol_ratio_5_20', 'vol_ratio_10_50',
        'vol_trend_5', 'vol_trend_20',
        'bb_upper', 'bb_lower', 'bb_middle', 'bb_width', 'bb_position',
        'atr_14', 'atr_21', 'atr_ratio',
        'price_change_abs', 'price_change_5', 'price_change_10',
        'volume_proxy_5', 'volume_proxy_20', 'volume_ratio',
        'rsi', 'sentiment_strength', 'sentiment_trend',
        'market_trend', 'market_volatility', 'market_state',
        'macd', 'macd_signal', 'macd_histogram', 'macd_state',
        'momentum_5', 'momentum_10', 'momentum_20', 'momentum_state'
    ]

def select_features(features: pd.DataFrame, feature_selection: str = 'all') -> pd.DataFrame:
    """
    特征选择
    
    Args:
        features: 特征数据框
        feature_selection: 特征选择方法 ('all', 'trend', 'volatility', 'technical')
        
    Returns:
        选择后的特征数据框
    """
    if feature_selection == 'all':
        return features
    
    elif feature_selection == 'trend':
        trend_cols = [col for col in features.columns if 'trend' in col or 'sma' in col or 'ema' in col]
        return features[trend_cols]
    
    elif feature_selection == 'volatility':
        vol_cols = [col for col in features.columns if 'vol' in col or 'atr' in col]
        return features[vol_cols]
    
    elif feature_selection == 'technical':
        tech_cols = [col for col in features.columns if 'macd' in col or 'rsi' in col or 'momentum' in col]
        return features[tech_cols]
    
    else:
        return features

def normalize_features(features: pd.DataFrame, method: str = 'zscore') -> pd.DataFrame:
    """
    特征标准化
    
    Args:
        features: 特征数据框
        method: 标准化方法 ('zscore', 'minmax', 'robust')
        
    Returns:
        标准化后的特征数据框
    """
    normalized_features = features.copy()
    
    # 只对数值列进行标准化
    numeric_cols = normalized_features.select_dtypes(include=[np.number]).columns
    
    if method == 'zscore':
        normalized_features[numeric_cols] = (normalized_features[numeric_cols] - 
                                           normalized_features[numeric_cols].mean()) / normalized_features[numeric_cols].std()
    
    elif method == 'minmax':
        normalized_features[numeric_cols] = (normalized_features[numeric_cols] - 
                                           normalized_features[numeric_cols].min()) / (normalized_features[numeric_cols].max() - normalized_features[numeric_cols].min())
    
    elif method == 'robust':
        median = normalized_features[numeric_cols].median()
        mad = np.median(np.abs(normalized_features[numeric_cols] - median))
        normalized_features[numeric_cols] = (normalized_features[numeric_cols] - median) / mad
    
    return normalized_features

def main():
    """主函数 - 演示特征构建"""
    print("🚀 情境特征构建演示")
    print("=" * 60)
    
    # 生成模拟价格数据
    np.random.seed(42)
    dates = pd.date_range('2023-01-01', periods=1000, freq='D')
    prices = pd.Series(100 * np.cumprod(1 + np.random.normal(0, 0.02, 1000)), index=dates)
    
    print(f"📊 价格数据: {len(prices)} 条记录")
    print(f"📅 时间范围: {prices.index[0]} 到 {prices.index[-1]}")
    
    # 构建特征
    features = build_regime_features(prices)
    
    print(f"\n🔧 构建特征: {features.shape[1]} 个特征")
    print(f"📋 特征列表: {list(features.columns)}")
    
    # 特征选择
    trend_features = select_features(features, 'trend')
    print(f"\n📈 趋势特征: {trend_features.shape[1]} 个")
    
    vol_features = select_features(features, 'volatility')
    print(f"📊 波动率特征: {vol_features.shape[1]} 个")
    
    tech_features = select_features(features, 'technical')
    print(f"🔧 技术特征: {tech_features.shape[1]} 个")
    
    # 特征标准化
    normalized_features = normalize_features(features, 'zscore')
    print(f"\n📏 标准化特征: {normalized_features.shape[1]} 个")
    
    # 显示特征统计
    print(f"\n📊 特征统计:")
    print(features.describe())
    
    print("\n" + "=" * 60)
    print("🎉 特征构建演示完成！")

def _build_news_sentiment_features(prices: pd.Series) -> Dict[str, pd.Series]:
    """构建新闻情感特征"""
    features = {}
    
    try:
        # 获取新闻情感分析器
        sentiment_analyzer = SentimentAnalyzer()
        cache = get_global_cache()
        
        # 为每个时间点计算情感分数
        sentiment_scores = []
        for timestamp in prices.index:
            # 获取该时间点的新闻情感
            sentiment = cache.get_sentiment_for_asset('BTC', timestamp)  # 使用BTC作为基准
            if sentiment:
                sentiment_scores.append(sentiment.get('score', 0.0))
            else:
                sentiment_scores.append(0.0)
        
        # 创建情感特征
        features['news_sentiment'] = pd.Series(sentiment_scores, index=prices.index)
        features['news_sentiment_ma5'] = features['news_sentiment'].rolling(5).mean()
        features['news_sentiment_ma20'] = features['news_sentiment'].rolling(20).mean()
        features['news_sentiment_trend'] = features['news_sentiment_ma5'] - features['news_sentiment_ma20']
        
        # 情感状态
        sentiment_median = features['news_sentiment'].median()
        features['news_sentiment_state'] = np.where(
            features['news_sentiment'] > sentiment_median, 'positive', 'negative'
        )
        
    except Exception as e:
        print(f"⚠️  新闻情感特征构建失败: {e}")
        # 使用默认值
        features['news_sentiment'] = pd.Series(0.0, index=prices.index)
        features['news_sentiment_ma5'] = pd.Series(0.0, index=prices.index)
        features['news_sentiment_ma20'] = pd.Series(0.0, index=prices.index)
        features['news_sentiment_trend'] = pd.Series(0.0, index=prices.index)
        features['news_sentiment_state'] = pd.Series('neutral', index=prices.index)
    
    return features

if __name__ == "__main__":
    main()
