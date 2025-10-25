#!/usr/bin/env python3
"""
增强版交易策略
专注于3个核心策略：趋势跟踪、均值回归、动量策略
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
import statistics
import numpy as np

@dataclass
class StrategySignal:
    """策略信号"""
    strategy_name: str
    asset: str
    action: str  # "BUY", "SELL", "HOLD"
    confidence: float  # 0-1
    strength: float  # 信号强度
    expected_return: float
    risk_level: float  # 0-1
    reasoning: str
    technical_indicators: Dict[str, float]  # 技术指标值

class EnhancedTradingStrategies:
    """增强版交易策略"""
    
    def __init__(self, config: dict):
        self.config = config
        
    # ============ 核心策略1: 趋势跟踪策略 ============
    
    def trend_following_strategy(self, asset: str, market_data: Dict) -> StrategySignal:
        """
        趋势跟踪策略 (Trend Following)
        基于移动平均线、MACD和趋势强度的综合判断
        """
        prices = market_data.get('prices', [])
        
        if len(prices) < 50:
            return StrategySignal(
                strategy_name="Trend Following",
                asset=asset,
                action="HOLD",
                confidence=0.0,
                strength=0.0,
                expected_return=0.0,
                risk_level=0.5,
                reasoning="Insufficient data for trend analysis",
                technical_indicators={}
            )
        
        # 计算技术指标
        sma_20 = self._calculate_sma(prices, 20)
        sma_50 = self._calculate_sma(prices, 50)
        ema_12 = self._calculate_ema(prices, 12)
        ema_26 = self._calculate_ema(prices, 26)
        macd = ema_12 - ema_26
        rsi = self._calculate_rsi(prices, 14)
        
        # 趋势强度计算
        trend_strength = self._calculate_trend_strength(prices)
        
        # 信号逻辑
        bullish_signals = 0
        bearish_signals = 0
        reasoning_parts = []
        
        # 移动平均线信号
        if sma_20 > sma_50:
            bullish_signals += 1
            reasoning_parts.append(f"SMA20({sma_20:.2f}) > SMA50({sma_50:.2f})")
        else:
            bearish_signals += 1
            reasoning_parts.append(f"SMA20({sma_20:.2f}) < SMA50({sma_50:.2f})")
        
        # MACD信号
        if macd > 0:
            bullish_signals += 1
            reasoning_parts.append(f"MACD({macd:.4f}) > 0")
        else:
            bearish_signals += 1
            reasoning_parts.append(f"MACD({macd:.4f}) < 0")
        
        # RSI过滤
        if rsi > 70:
            bearish_signals += 1
            reasoning_parts.append(f"RSI({rsi:.1f}) overbought")
        elif rsi < 30:
            bullish_signals += 1
            reasoning_parts.append(f"RSI({rsi:.1f}) oversold")
        
        # 趋势强度过滤
        if trend_strength > 0.6:
            if bullish_signals > bearish_signals:
                action = "BUY"
                strength = min((bullish_signals - bearish_signals) / 3, 1.0)
                confidence = 0.85
            else:
                action = "SELL"
                strength = min((bearish_signals - bullish_signals) / 3, 1.0)
                confidence = 0.85
        else:
            action = "HOLD"
            strength = 0.0
            confidence = 0.3
            reasoning_parts.append(f"Weak trend strength: {trend_strength:.2f}")
        
        reasoning = " | ".join(reasoning_parts)
        
        return StrategySignal(
            strategy_name="Trend Following",
            asset=asset,
            action=action,
            confidence=confidence,
            strength=strength,
            expected_return=0.08 * strength if action == "BUY" else 0.0,
            risk_level=0.4,
            reasoning=reasoning,
            technical_indicators={
                "SMA_20": sma_20,
                "SMA_50": sma_50,
                "MACD": macd,
                "RSI": rsi,
                "Trend_Strength": trend_strength
            }
        )
    
    # ============ 核心策略2: 均值回归策略 ============
    
    def mean_reversion_strategy(self, asset: str, market_data: Dict) -> StrategySignal:
        """
        均值回归策略 (Mean Reversion)
        基于布林带、Z-score和RSI的超买超卖判断
        """
        prices = market_data.get('prices', [])
        
        if len(prices) < 30:
            return StrategySignal(
                strategy_name="Mean Reversion",
                asset=asset,
                action="HOLD",
                confidence=0.0,
                strength=0.0,
                expected_return=0.0,
                risk_level=0.5,
                reasoning="Insufficient data for mean reversion",
                technical_indicators={}
            )
        
        # 计算技术指标
        sma_20 = self._calculate_sma(prices, 20)
        std_20 = self._calculate_std(prices, 20)
        rsi = self._calculate_rsi(prices, 14)
        current_price = prices[-1]
        
        # 布林带
        bb_upper = sma_20 + (2 * std_20)
        bb_lower = sma_20 - (2 * std_20)
        bb_position = (current_price - bb_lower) / (bb_upper - bb_lower) if bb_upper != bb_lower else 0.5
        
        # Z-score
        z_score = (current_price - sma_20) / std_20 if std_20 > 0 else 0
        
        # 信号逻辑
        reasoning_parts = []
        
        # 超卖信号 (买入)
        if (bb_position < 0.2 or z_score < -1.5) and rsi < 35:
            action = "BUY"
            strength = min((0.2 - bb_position) * 5 + (35 - rsi) / 35, 1.0)
            confidence = 0.8
            reasoning_parts.append(f"Oversold: BB={bb_position:.2f}, Z={z_score:.2f}, RSI={rsi:.1f}")
        
        # 超买信号 (卖出)
        elif (bb_position > 0.8 or z_score > 1.5) and rsi > 65:
            action = "SELL"
            strength = min((bb_position - 0.8) * 5 + (rsi - 65) / 35, 1.0)
            confidence = 0.8
            reasoning_parts.append(f"Overbought: BB={bb_position:.2f}, Z={z_score:.2f}, RSI={rsi:.1f}")
        
        # 中性信号
        else:
            action = "HOLD"
            strength = 0.0
            confidence = 0.3
            reasoning_parts.append(f"Neutral: BB={bb_position:.2f}, Z={z_score:.2f}, RSI={rsi:.1f}")
        
        reasoning = " | ".join(reasoning_parts)
        
        return StrategySignal(
            strategy_name="Mean Reversion",
            asset=asset,
            action=action,
            confidence=confidence,
            strength=strength,
            expected_return=0.06 * strength if action == "BUY" else 0.0,
            risk_level=0.3,
            reasoning=reasoning,
            technical_indicators={
                "BB_Upper": bb_upper,
                "BB_Lower": bb_lower,
                "BB_Position": bb_position,
                "Z_Score": z_score,
                "RSI": rsi
            }
        )
    
    # ============ 核心策略3: 动量策略 ============
    
    def momentum_strategy(self, asset: str, market_data: Dict) -> StrategySignal:
        """
        动量策略 (Momentum)
        基于价格动量、成交量动量和波动率突破
        """
        prices = market_data.get('prices', [])
        volumes = market_data.get('volumes', [])
        
        if len(prices) < 20:
            return StrategySignal(
                strategy_name="Momentum",
                asset=asset,
                action="HOLD",
                confidence=0.0,
                strength=0.0,
                expected_return=0.0,
                risk_level=0.5,
                reasoning="Insufficient data for momentum analysis",
                technical_indicators={}
            )
        
        # 计算技术指标
        price_momentum_5 = (prices[-1] - prices[-6]) / prices[-6] if len(prices) >= 6 else 0
        price_momentum_10 = (prices[-1] - prices[-11]) / prices[-11] if len(prices) >= 11 else 0
        price_momentum_20 = (prices[-1] - prices[-21]) / prices[-21] if len(prices) >= 21 else 0
        
        # 成交量动量
        volume_momentum = 0
        if len(volumes) >= 10:
            avg_volume_5 = np.mean(volumes[-5:])
            avg_volume_10 = np.mean(volumes[-10:])
            volume_momentum = (avg_volume_5 - avg_volume_10) / avg_volume_10 if avg_volume_10 > 0 else 0
        
        # 波动率
        volatility = self._calculate_volatility(prices, 20)
        
        # RSI
        rsi = self._calculate_rsi(prices, 14)
        
        # 动量强度
        momentum_strength = (price_momentum_5 * 0.5 + price_momentum_10 * 0.3 + price_momentum_20 * 0.2)
        
        # 信号逻辑
        reasoning_parts = []
        
        # 强动量买入信号
        if (momentum_strength > 0.03 and 
            volume_momentum > 0.2 and 
            rsi < 75 and 
            volatility < 0.05):
            action = "BUY"
            strength = min(momentum_strength * 20 + volume_momentum * 0.5, 1.0)
            confidence = 0.9
            reasoning_parts.append(f"Strong momentum: {momentum_strength:.3f}, Volume: {volume_momentum:.2f}")
        
        # 强动量卖出信号
        elif (momentum_strength < -0.03 and 
              volume_momentum > 0.2 and 
              rsi > 25 and 
              volatility < 0.05):
            action = "SELL"
            strength = min(abs(momentum_strength) * 20 + volume_momentum * 0.5, 1.0)
            confidence = 0.9
            reasoning_parts.append(f"Strong negative momentum: {momentum_strength:.3f}, Volume: {volume_momentum:.2f}")
        
        # 弱动量信号
        elif abs(momentum_strength) > 0.01:
            if momentum_strength > 0:
                action = "BUY"
                strength = min(momentum_strength * 15, 0.6)
                confidence = 0.6
            else:
                action = "SELL"
                strength = min(abs(momentum_strength) * 15, 0.6)
                confidence = 0.6
            reasoning_parts.append(f"Weak momentum: {momentum_strength:.3f}")
        
        # 无动量信号
        else:
            action = "HOLD"
            strength = 0.0
            confidence = 0.3
            reasoning_parts.append(f"No momentum: {momentum_strength:.3f}")
        
        reasoning = " | ".join(reasoning_parts)
        
        return StrategySignal(
            strategy_name="Momentum",
            asset=asset,
            action=action,
            confidence=confidence,
            strength=strength,
            expected_return=0.10 * strength if action == "BUY" else 0.0,
            risk_level=0.5,
            reasoning=reasoning,
            technical_indicators={
                "Momentum_5": price_momentum_5,
                "Momentum_10": price_momentum_10,
                "Momentum_20": price_momentum_20,
                "Volume_Momentum": volume_momentum,
                "Volatility": volatility,
                "RSI": rsi
            }
        )
    
    # ============ 辅助函数 ============
    
    def _calculate_sma(self, prices: List[float], period: int) -> float:
        """计算简单移动平均"""
        if len(prices) < period:
            return prices[-1] if prices else 0
        return sum(prices[-period:]) / period
    
    def _calculate_ema(self, prices: List[float], period: int) -> float:
        """计算指数移动平均"""
        if len(prices) < period:
            return prices[-1] if prices else 0
        
        multiplier = 2 / (period + 1)
        ema = prices[0]
        
        for price in prices[1:]:
            ema = (price * multiplier) + (ema * (1 - multiplier))
        
        return ema
    
    def _calculate_rsi(self, prices: List[float], period: int = 14) -> float:
        """计算RSI指标"""
        if len(prices) < period + 1:
            return 50.0
        
        gains = []
        losses = []
        
        for i in range(1, len(prices)):
            change = prices[i] - prices[i-1]
            if change > 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(change))
        
        avg_gain = statistics.mean(gains[-period:])
        avg_loss = statistics.mean(losses[-period:])
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def _calculate_std(self, prices: List[float], period: int) -> float:
        """计算标准差"""
        if len(prices) < period:
            return 0
        return statistics.stdev(prices[-period:])
    
    def _calculate_trend_strength(self, prices: List[float]) -> float:
        """计算趋势强度"""
        if len(prices) < 20:
            return 0.0
        
        # 计算线性回归斜率
        x = np.arange(len(prices[-20:]))
        y = np.array(prices[-20:])
        
        # 线性回归
        slope, _ = np.polyfit(x, y, 1)
        
        # 标准化斜率
        price_range = max(y) - min(y)
        if price_range > 0:
            normalized_slope = abs(slope) / price_range
            return min(normalized_slope * 20, 1.0)  # 放大并限制在0-1
        
        return 0.0
    
    def _calculate_volatility(self, prices: List[float], period: int) -> float:
        """计算波动率"""
        if len(prices) < period + 1:
            return 0.0
        
        returns = []
        for i in range(1, len(prices)):
            if prices[i-1] != 0:
                returns.append((prices[i] - prices[i-1]) / prices[i-1])
        
        if len(returns) < period:
            return 0.0
        
        return statistics.stdev(returns[-period:])
    
    def get_core_strategies(self) -> List[str]:
        """获取核心策略名称"""
        return [
            "trend_following_strategy",
            "mean_reversion_strategy", 
            "momentum_strategy"
        ]
    
    def run_strategy(self, strategy_name: str, asset: str, market_data: Dict) -> StrategySignal:
        """运行指定策略"""
        strategy_method = getattr(self, strategy_name, None)
        if strategy_method and callable(strategy_method):
            return strategy_method(asset, market_data)
        else:
            raise ValueError(f"Unknown strategy: {strategy_name}")

def main():
    """主函数 - 演示策略"""
    print("🚀 增强版交易策略")
    print("=" * 60)
    
    # 模拟市场数据
    np.random.seed(42)
    prices = [100 + i * 0.1 + np.random.normal(0, 0.5) for i in range(100)]
    volumes = [1000 + np.random.normal(0, 100) for _ in range(100)]
    
    market_data = {
        'prices': prices,
        'volumes': volumes
    }
    
    strategies = EnhancedTradingStrategies({})
    
    # 测试核心策略
    core_strategies = strategies.get_core_strategies()
    
    for strategy_name in core_strategies:
        print(f"\n📊 测试策略: {strategy_name}")
        signal = strategies.run_strategy(strategy_name, "BTC", market_data)
        
        print(f"  动作: {signal.action}")
        print(f"  置信度: {signal.confidence:.2f}")
        print(f"  强度: {signal.strength:.2f}")
        print(f"  预期收益: {signal.expected_return:.2%}")
        print(f"  风险等级: {signal.risk_level:.2f}")
        print(f"  推理: {signal.reasoning}")
        print(f"  技术指标: {signal.technical_indicators}")
    
    print("\n" + "=" * 60)
    print("🎉 策略测试完成！")

if __name__ == "__main__":
    main()
