#!/usr/bin/env python3
"""
策略基础协议
统一所有策略的接口和输出格式
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional
import pandas as pd
import numpy as np
from abc import ABC, abstractmethod

@dataclass
class StrategyOutput:
    """策略输出统一格式"""
    signals: pd.Series        # +1/-1/0, index = prices.index
    positions: pd.Series       # 目标仓位(0..1)，经中间件处理
    meta: Dict[str, Any]      # {"name": str, "conf": float, "reason_tags": list[str]}

class Strategy(ABC):
    """策略基类"""
    
    def __init__(self, name: str, default_params: Optional[Dict[str, Any]] = None):
        self.name = name
        self.default_params = default_params or {}
    
    @abstractmethod
    def run(self, prices: pd.Series, features: pd.DataFrame, 
            params: Optional[Dict[str, Any]] = None) -> StrategyOutput:
        """
        运行策略
        
        Args:
            prices: 价格序列，index为时间
            features: 特征数据框，包含技术指标等
            params: 策略参数，会与default_params合并
            
        Returns:
            StrategyOutput: 包含信号、仓位和元数据
        """
        raise NotImplementedError
    
    def get_params(self, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """合并默认参数和传入参数"""
        merged_params = self.default_params.copy()
        if params:
            merged_params.update(params)
        return merged_params
    
    def validate_inputs(self, prices: pd.Series, features: pd.DataFrame) -> None:
        """验证输入数据"""
        if len(prices) == 0:
            raise ValueError("价格序列不能为空")
        
        if not isinstance(prices.index, pd.DatetimeIndex):
            raise ValueError("价格序列索引必须是DatetimeIndex")
        
        if len(features) != len(prices):
            raise ValueError("特征数据长度必须与价格序列一致")
        
        if not features.index.equals(prices.index):
            raise ValueError("特征数据索引必须与价格序列索引一致")

class BuyAndHoldStrategy(Strategy):
    """买入持有策略"""
    
    def __init__(self):
        super().__init__("buy_and_hold", {})
    
    def run(self, prices: pd.Series, features: pd.DataFrame, 
            params: Optional[Dict[str, Any]] = None) -> StrategyOutput:
        self.validate_inputs(prices, features)
        
        # 买入持有：始终持有
        signals = pd.Series(1, index=prices.index)
        positions = pd.Series(1.0, index=prices.index)
        
        return StrategyOutput(
            signals=signals,
            positions=positions,
            meta={
                "name": self.name,
                "conf": 1.0,
                "reason_tags": ["buy_and_hold", "long_term"]
            }
        )

class MACDStrategy(Strategy):
    """MACD策略"""
    
    def __init__(self):
        super().__init__("macd", {
            "fast_period": 12,
            "slow_period": 26,
            "signal_period": 9,
            "threshold": 0.0
        })
    
    def run(self, prices: pd.Series, features: pd.DataFrame, 
            params: Optional[Dict[str, Any]] = None) -> StrategyOutput:
        self.validate_inputs(prices, features)
        p = self.get_params(params)
        
        # 计算MACD
        ema_fast = prices.ewm(span=p["fast_period"]).mean()
        ema_slow = prices.ewm(span=p["slow_period"]).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=p["signal_period"]).mean()
        
        # 生成信号
        signals = pd.Series(0, index=prices.index)
        positions = pd.Series(0.0, index=prices.index)
        
        # MACD交叉信号
        macd_diff = macd_line - signal_line
        signals[macd_diff > p["threshold"]] = 1   # 买入
        signals[macd_diff < -p["threshold"]] = -1  # 卖出
        
        # 转换为仓位
        positions = signals.cumsum().clip(-1, 1)
        
        return StrategyOutput(
            signals=signals,
            positions=positions,
            meta={
                "name": self.name,
                "conf": 0.75,
                "reason_tags": ["macd", "trend_following"]
            }
        )

class RSIStrategy(Strategy):
    """RSI策略"""
    
    def __init__(self):
        super().__init__("rsi", {
            "period": 14,
            "oversold": 30,
            "overbought": 70
        })
    
    def run(self, prices: pd.Series, features: pd.DataFrame, 
            params: Optional[Dict[str, Any]] = None) -> StrategyOutput:
        self.validate_inputs(prices, features)
        p = self.get_params(params)
        
        # 计算RSI
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=p["period"]).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=p["period"]).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        # 生成信号
        signals = pd.Series(0, index=prices.index)
        positions = pd.Series(0.0, index=prices.index)
        
        # RSI超买超卖信号
        signals[rsi < p["oversold"]] = 1    # 超卖买入
        signals[rsi > p["overbought"]] = -1  # 超买卖出
        
        # 转换为仓位
        positions = signals.cumsum().clip(-1, 1)
        
        return StrategyOutput(
            signals=signals,
            positions=positions,
            meta={
                "name": self.name,
                "conf": 0.8,
                "reason_tags": ["rsi", "mean_reversion"]
            }
        )

class BollingerBandsStrategy(Strategy):
    """布林带策略"""
    
    def __init__(self):
        super().__init__("bollinger_bands", {
            "period": 20,
            "std_dev": 2.0,
            "threshold": 0.2
        })
    
    def run(self, prices: pd.Series, features: pd.DataFrame, 
            params: Optional[Dict[str, Any]] = None) -> StrategyOutput:
        self.validate_inputs(prices, features)
        p = self.get_params(params)
        
        # 计算布林带
        sma = prices.rolling(window=p["period"]).mean()
        std = prices.rolling(window=p["period"]).std()
        upper_band = sma + (p["std_dev"] * std)
        lower_band = sma - (p["std_dev"] * std)
        
        # 计算布林带位置
        bb_position = (prices - lower_band) / (upper_band - lower_band)
        
        # 生成信号
        signals = pd.Series(0, index=prices.index)
        positions = pd.Series(0.0, index=prices.index)
        
        # 布林带均值回归信号
        signals[bb_position < p["threshold"]] = 1      # 接近下轨买入
        signals[bb_position > (1 - p["threshold"])] = -1  # 接近上轨卖出
        
        # 转换为仓位
        positions = signals.cumsum().clip(-1, 1)
        
        return StrategyOutput(
            signals=signals,
            positions=positions,
            meta={
                "name": self.name,
                "conf": 0.7,
                "reason_tags": ["bollinger_bands", "mean_reversion"]
            }
        )

class MomentumStrategy(Strategy):
    """动量策略"""
    
    def __init__(self):
        super().__init__("momentum", {
            "short_period": 5,
            "long_period": 20,
            "threshold": 0.02
        })
    
    def run(self, prices: pd.Series, features: pd.DataFrame, 
            params: Optional[Dict[str, Any]] = None) -> StrategyOutput:
        self.validate_inputs(prices, features)
        p = self.get_params(params)
        
        # 计算动量
        short_ma = prices.rolling(window=p["short_period"]).mean()
        long_ma = prices.rolling(window=p["long_period"]).mean()
        momentum = (short_ma - long_ma) / long_ma
        
        # 生成信号
        signals = pd.Series(0, index=prices.index)
        positions = pd.Series(0.0, index=prices.index)
        
        # 动量信号
        signals[momentum > p["threshold"]] = 1     # 正动量买入
        signals[momentum < -p["threshold"]] = -1   # 负动量卖出
        
        # 转换为仓位
        positions = signals.cumsum().clip(-1, 1)
        
        return StrategyOutput(
            signals=signals,
            positions=positions,
            meta={
                "name": self.name,
                "conf": 0.65,
                "reason_tags": ["momentum", "trend_following"]
            }
        )

class MeanReversionStrategy(Strategy):
    """均值回归策略"""
    
    def __init__(self):
        super().__init__("mean_reversion", {
            "period": 20,
            "threshold": 2.0
        })
    
    def run(self, prices: pd.Series, features: pd.DataFrame, 
            params: Optional[Dict[str, Any]] = None) -> StrategyOutput:
        self.validate_inputs(prices, features)
        p = self.get_params(params)
        
        # 计算Z-score
        mean_price = prices.rolling(window=p["period"]).mean()
        std_price = prices.rolling(window=p["period"]).std()
        z_score = (prices - mean_price) / std_price
        
        # 生成信号
        signals = pd.Series(0, index=prices.index)
        positions = pd.Series(0.0, index=prices.index)
        
        # 均值回归信号
        signals[z_score < -p["threshold"]] = 1    # 低于均值买入
        signals[z_score > p["threshold"]] = -1     # 高于均值卖出
        
        # 转换为仓位
        positions = signals.cumsum().clip(-1, 1)
        
        return StrategyOutput(
            signals=signals,
            positions=positions,
            meta={
                "name": self.name,
                "conf": 0.8,
                "reason_tags": ["mean_reversion", "contrarian"]
            }
        )

class TrendFollowingStrategy(Strategy):
    """趋势跟踪策略"""
    
    def __init__(self):
        super().__init__("trend_following", {
            "short_period": 10,
            "long_period": 30,
            "threshold": 0.01
        })
    
    def run(self, prices: pd.Series, features: pd.DataFrame, 
            params: Optional[Dict[str, Any]] = None) -> StrategyOutput:
        self.validate_inputs(prices, features)
        p = self.get_params(params)
        
        # 计算移动平均
        short_ma = prices.rolling(window=p["short_period"]).mean()
        long_ma = prices.rolling(window=p["long_period"]).mean()
        
        # 计算趋势强度
        trend_strength = (short_ma - long_ma) / long_ma
        
        # 生成信号
        signals = pd.Series(0, index=prices.index)
        positions = pd.Series(0.0, index=prices.index)
        
        # 趋势跟踪信号
        signals[trend_strength > p["threshold"]] = 1     # 上升趋势买入
        signals[trend_strength < -p["threshold"]] = -1    # 下降趋势卖出
        
        # 转换为仓位
        positions = signals.cumsum().clip(-1, 1)
        
        return StrategyOutput(
            signals=signals,
            positions=positions,
            meta={
                "name": self.name,
                "conf": 0.7,
                "reason_tags": ["trend_following", "moving_average"]
            }
        )

class VolatilityBreakoutStrategy(Strategy):
    """波动率突破策略"""
    
    def __init__(self):
        super().__init__("volatility_breakout", {
            "period": 20,
            "threshold": 1.5
        })
    
    def run(self, prices: pd.Series, features: pd.DataFrame, 
            params: Optional[Dict[str, Any]] = None) -> StrategyOutput:
        self.validate_inputs(prices, features)
        p = self.get_params(params)
        
        # 计算波动率
        returns = prices.pct_change()
        volatility = returns.rolling(window=p["period"]).std()
        
        # 计算价格突破
        price_change = prices.pct_change()
        breakout = abs(price_change) > (volatility * p["threshold"])
        
        # 生成信号
        signals = pd.Series(0, index=prices.index)
        positions = pd.Series(0.0, index=prices.index)
        
        # 突破信号
        signals[breakout & (price_change > 0)] = 1   # 向上突破买入
        signals[breakout & (price_change < 0)] = -1  # 向下突破卖出
        
        # 转换为仓位
        positions = signals.cumsum().clip(-1, 1)
        
        return StrategyOutput(
            signals=signals,
            positions=positions,
            meta={
                "name": self.name,
                "conf": 0.6,
                "reason_tags": ["volatility_breakout", "momentum"]
            }
        )

class KDJStrategy(Strategy):
    """KDJ策略"""
    
    def __init__(self):
        super().__init__("kdj", {
            "period": 9,
            "k_period": 3,
            "d_period": 3,
            "oversold": 20,
            "overbought": 80
        })
    
    def run(self, prices: pd.Series, features: pd.DataFrame, 
            params: Optional[Dict[str, Any]] = None) -> StrategyOutput:
        self.validate_inputs(prices, features)
        p = self.get_params(params)
        
        # 计算KDJ
        low_min = prices.rolling(window=p["period"]).min()
        high_max = prices.rolling(window=p["period"]).max()
        rsv = (prices - low_min) / (high_max - low_min) * 100
        
        k = rsv.ewm(span=p["k_period"]).mean()
        d = k.ewm(span=p["d_period"]).mean()
        
        # 生成信号
        signals = pd.Series(0, index=prices.index)
        positions = pd.Series(0.0, index=prices.index)
        
        # KDJ超买超卖信号
        signals[(k < p["oversold"]) & (d < p["oversold"])] = 1    # 超卖买入
        signals[(k > p["overbought"]) & (d > p["overbought"])] = -1  # 超买卖出
        
        # 转换为仓位
        positions = signals.cumsum().clip(-1, 1)
        
        return StrategyOutput(
            signals=signals,
            positions=positions,
            meta={
                "name": self.name,
                "conf": 0.75,
                "reason_tags": ["kdj", "oscillator"]
            }
        )
