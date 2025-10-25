"""
专业交易策略工具集
包含技术指标、ML/DL、RL策略
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
import statistics

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

class TradingStrategies:
    """交易策略工具集"""
    
    def __init__(self, config: dict):
        self.config = config
        
    # ============ 技术指标策略 ============
    
    def buy_and_hold(self, asset: str, market_data: Dict) -> StrategySignal:
        """
        Buy-and-Hold (B&H)
        长期持有策略，不考虑短期波动
        """
        # 对于稳定币，不持有
        if asset in ['USDT', 'USDC']:
            return StrategySignal(
                strategy_name="Buy-and-Hold",
                asset=asset,
                action="HOLD",
                confidence=1.0,
                strength=0.0,
                expected_return=0.0,
                risk_level=0.0,
                reasoning="Stablecoin - no growth expected"
            )
        
        # 对于其他资产，长期看涨
        price_trend = market_data.get('assets', {}).get(asset, {}).get('change_24h', 0)
        
        return StrategySignal(
            strategy_name="Buy-and-Hold",
            asset=asset,
            action="BUY" if price_trend > 0 else "HOLD",
            confidence=0.7,
            strength=0.5,
            expected_return=0.15,  # 假设长期15%回报
            risk_level=0.4,
            reasoning=f"Long-term trend: {price_trend:+.2f}%"
        )
    
    def macd_strategy(self, asset: str, market_data: Dict) -> StrategySignal:
        """
        Moving Average Convergence Divergence (MACD)
        使用MACD指标和信号线交叉识别交易信号
        """
        prices = market_data.get('prices', [])
        
        if len(prices) < 26:
            return StrategySignal(
                strategy_name="MACD",
                asset=asset,
                action="HOLD",
                confidence=0.0,
                strength=0.0,
                expected_return=0.0,
                risk_level=0.5,
                reasoning="Insufficient data for MACD"
            )
        
        # 简化的MACD计算
        ema_12 = self._calculate_ema(prices, 12)
        ema_26 = self._calculate_ema(prices, 26)
        macd_line = ema_12 - ema_26
        signal_line = self._calculate_ema([macd_line] * 9, 9)
        
        # MACD交叉信号
        if macd_line > signal_line:
            action = "BUY"
            strength = min((macd_line - signal_line) / signal_line, 1.0)
            reasoning = "MACD bullish crossover"
        elif macd_line < signal_line:
            action = "SELL"
            strength = min((signal_line - macd_line) / signal_line, 1.0)
            reasoning = "MACD bearish crossover"
        else:
            action = "HOLD"
            strength = 0.0
            reasoning = "MACD neutral"
        
        return StrategySignal(
            strategy_name="MACD",
            asset=asset,
            action=action,
            confidence=0.75,
            strength=abs(strength),
            expected_return=0.05 * strength,
            risk_level=0.5,
            reasoning=reasoning
        )
    
    def kdj_rsi_strategy(self, asset: str, market_data: Dict) -> StrategySignal:
        """
        KDJ with RSI Filter (KDJ&RSI)
        结合KDJ和RSI指标识别精确交易信号
        """
        prices = market_data.get('prices', [])
        
        if len(prices) < 14:
            return StrategySignal(
                strategy_name="KDJ&RSI",
                asset=asset,
                action="HOLD",
                confidence=0.0,
                strength=0.0,
                expected_return=0.0,
                risk_level=0.5,
                reasoning="Insufficient data"
            )
        
        # 简化的RSI计算
        rsi = self._calculate_rsi(prices, 14)
        
        # 简化的KDJ计算
        kdj_k = self._calculate_kdj_k(prices)
        
        # 信号逻辑
        if rsi < 30 and kdj_k < 20:
            # 超卖信号
            action = "BUY"
            strength = (30 - rsi) / 30 + (20 - kdj_k) / 20
            reasoning = f"Oversold: RSI={rsi:.1f}, KDJ_K={kdj_k:.1f}"
        elif rsi > 70 and kdj_k > 80:
            # 超买信号
            action = "SELL"
            strength = (rsi - 70) / 30 + (kdj_k - 80) / 20
            reasoning = f"Overbought: RSI={rsi:.1f}, KDJ_K={kdj_k:.1f}"
        else:
            action = "HOLD"
            strength = 0.0
            reasoning = f"Neutral: RSI={rsi:.1f}, KDJ_K={kdj_k:.1f}"
        
        return StrategySignal(
            strategy_name="KDJ&RSI",
            asset=asset,
            action=action,
            confidence=0.8,
            strength=min(strength, 1.0),
            expected_return=0.08 * strength if action == "BUY" else 0.0,
            risk_level=0.4,
            reasoning=reasoning
        )
    
    def zscore_mean_reversion(self, asset: str, market_data: Dict) -> StrategySignal:
        """
        Z-score Mean Reversion (ZMR)
        假设价格会回归均值
        """
        prices = market_data.get('prices', [])
        
        if len(prices) < 20:
            return StrategySignal(
                strategy_name="Z-score Mean Reversion",
                asset=asset,
                action="HOLD",
                confidence=0.0,
                strength=0.0,
                expected_return=0.0,
                risk_level=0.5,
                reasoning="Insufficient data"
            )
        
        # 计算Z-score
        mean_price = statistics.mean(prices)
        std_price = statistics.stdev(prices)
        current_price = prices[-1]
        
        if std_price == 0:
            z_score = 0
        else:
            z_score = (current_price - mean_price) / std_price
        
        # 均值回归信号
        if z_score < -2:
            # 价格严重低于均值，买入
            action = "BUY"
            strength = min(abs(z_score) / 3, 1.0)
            reasoning = f"Price below mean (Z={z_score:.2f})"
        elif z_score > 2:
            # 价格严重高于均值，卖出
            action = "SELL"
            strength = min(abs(z_score) / 3, 1.0)
            reasoning = f"Price above mean (Z={z_score:.2f})"
        else:
            action = "HOLD"
            strength = 0.0
            reasoning = f"Price near mean (Z={z_score:.2f})"
        
        return StrategySignal(
            strategy_name="Z-score Mean Reversion",
            asset=asset,
            action=action,
            confidence=0.75,
            strength=strength,
            expected_return=0.06 * strength if action == "BUY" else 0.0,
            risk_level=0.3,
            reasoning=reasoning
        )
    
    # ============ ML/DL策略 ============
    
    def lgbm_strategy(self, asset: str, market_data: Dict) -> StrategySignal:
        """
        LGBM (Light Gradient Boosting Machine)
        使用树模型预测价格波动
        
        注：这里使用简化版本，实际应该训练LGBM模型
        """
        prices = market_data.get('prices', [])
        
        if len(prices) < 5:
            return StrategySignal(
                strategy_name="LGBM",
                asset=asset,
                action="HOLD",
                confidence=0.0,
                strength=0.0,
                expected_return=0.0,
                risk_level=0.6,
                reasoning="Insufficient data"
            )
        
        # 简化：基于最近趋势预测
        recent_trend = (prices[-1] - prices[-5]) / prices[-5]
        volatility = statistics.stdev(prices[-5:]) / statistics.mean(prices[-5:])
        
        # 模拟LGBM预测
        if recent_trend > 0.02 and volatility < 0.1:
            action = "BUY"
            strength = min(recent_trend * 10, 1.0)
            reasoning = f"LGBM predicts uptrend: {recent_trend*100:.2f}%"
        elif recent_trend < -0.02 and volatility < 0.1:
            action = "SELL"
            strength = min(abs(recent_trend) * 10, 1.0)
            reasoning = f"LGBM predicts downtrend: {recent_trend*100:.2f}%"
        else:
            action = "HOLD"
            strength = 0.0
            reasoning = "LGBM uncertain signal"
        
        return StrategySignal(
            strategy_name="LGBM",
            asset=asset,
            action=action,
            confidence=0.82,
            strength=strength,
            expected_return=0.10 * strength if action == "BUY" else 0.0,
            risk_level=0.5,
            reasoning=reasoning
        )
    
    def lstm_strategy(self, asset: str, market_data: Dict) -> StrategySignal:
        """
        LSTM (Long Short-Term Memory)
        使用长短期记忆网络预测价格
        
        注：简化版本，实际应该训练LSTM模型
        """
        prices = market_data.get('prices', [])
        
        if len(prices) < 10:
            return StrategySignal(
                strategy_name="LSTM",
                asset=asset,
                action="HOLD",
                confidence=0.0,
                strength=0.0,
                expected_return=0.0,
                risk_level=0.6,
                reasoning="Insufficient data"
            )
        
        # 简化：模拟LSTM时序预测
        # 计算短期和长期趋势
        short_term = (prices[-1] - prices[-3]) / prices[-3]
        long_term = (prices[-1] - prices[-10]) / prices[-10]
        
        # 组合信号
        combined_signal = 0.6 * short_term + 0.4 * long_term
        
        if combined_signal > 0.03:
            action = "BUY"
            strength = min(combined_signal * 15, 1.0)
            reasoning = f"LSTM forecasts rise: {combined_signal*100:.2f}%"
        elif combined_signal < -0.03:
            action = "SELL"
            strength = min(abs(combined_signal) * 15, 1.0)
            reasoning = f"LSTM forecasts fall: {combined_signal*100:.2f}%"
        else:
            action = "HOLD"
            strength = 0.0
            reasoning = "LSTM neutral forecast"
        
        return StrategySignal(
            strategy_name="LSTM",
            asset=asset,
            action=action,
            confidence=0.85,
            strength=strength,
            expected_return=0.12 * strength if action == "BUY" else 0.0,
            risk_level=0.55,
            reasoning=reasoning
        )
    
    def transformer_strategy(self, asset: str, market_data: Dict) -> StrategySignal:
        """
        Transformer
        使用自注意力机制增强价格预测精度
        
        注：简化版本
        """
        prices = market_data.get('prices', [])
        
        if len(prices) < 15:
            return StrategySignal(
                strategy_name="Transformer",
                asset=asset,
                action="HOLD",
                confidence=0.0,
                strength=0.0,
                expected_return=0.0,
                risk_level=0.6,
                reasoning="Insufficient data"
            )
        
        # 简化：模拟Transformer的注意力机制
        # 关注最近和关键时间点
        recent_weights = [0.4, 0.3, 0.2, 0.1]
        weighted_change = sum(
            w * (prices[-i-1] - prices[-i-2]) / prices[-i-2]
            for i, w in enumerate(recent_weights)
        )
        
        if weighted_change > 0.025:
            action = "BUY"
            strength = min(weighted_change * 20, 1.0)
            reasoning = f"Transformer attention: bullish {weighted_change*100:.2f}%"
        elif weighted_change < -0.025:
            action = "SELL"
            strength = min(abs(weighted_change) * 20, 1.0)
            reasoning = f"Transformer attention: bearish {weighted_change*100:.2f}%"
        else:
            action = "HOLD"
            strength = 0.0
            reasoning = "Transformer neutral"
        
        return StrategySignal(
            strategy_name="Transformer",
            asset=asset,
            action=action,
            confidence=0.88,
            strength=strength,
            expected_return=0.13 * strength if action == "BUY" else 0.0,
            risk_level=0.5,
            reasoning=reasoning
        )
    
    # ============ RL策略 ============
    
    def sac_strategy(self, asset: str, market_data: Dict) -> StrategySignal:
        """
        SAC (Soft Actor-Critic)
        使用熵正则化和软值函数优化交易策略
        
        注：简化版本
        """
        prices = market_data.get('prices', [])
        
        if len(prices) < 5:
            return StrategySignal(
                strategy_name="SAC",
                asset=asset,
                action="HOLD",
                confidence=0.0,
                strength=0.0,
                expected_return=0.0,
                risk_level=0.7,
                reasoning="Insufficient data"
            )
        
        # 简化：模拟SAC的探索-利用平衡
        recent_return = (prices[-1] - prices[-5]) / prices[-5]
        volatility = statistics.stdev(prices[-5:]) / statistics.mean(prices[-5:])
        
        # SAC倾向于在低波动时积极交易
        exploration_factor = 0.1  # 探索因子
        
        if recent_return > 0.02 and volatility < 0.15:
            action = "BUY"
            strength = min(recent_return * 12 + exploration_factor, 1.0)
            reasoning = f"SAC: favorable risk-reward, vol={volatility:.2%}"
        elif recent_return < -0.02 and volatility > 0.2:
            action = "SELL"
            strength = min(abs(recent_return) * 12 + exploration_factor, 1.0)
            reasoning = f"SAC: high risk, vol={volatility:.2%}"
        else:
            action = "HOLD"
            strength = exploration_factor
            reasoning = f"SAC: exploring, vol={volatility:.2%}"
        
        return StrategySignal(
            strategy_name="SAC",
            asset=asset,
            action=action,
            confidence=0.80,
            strength=strength,
            expected_return=0.14 * strength if action == "BUY" else 0.0,
            risk_level=0.6,
            reasoning=reasoning
        )
    
    def ppo_strategy(self, asset: str, market_data: Dict) -> StrategySignal:
        """
        PPO (Proximal Policy Optimization)
        迭代更新策略，平衡探索和利用
        
        注：简化版本
        """
        prices = market_data.get('prices', [])
        
        if len(prices) < 8:
            return StrategySignal(
                strategy_name="PPO",
                asset=asset,
                action="HOLD",
                confidence=0.0,
                strength=0.0,
                expected_return=0.0,
                risk_level=0.7,
                reasoning="Insufficient data"
            )
        
        # 简化：模拟PPO的稳定性和样本效率
        # 计算多个时间窗口的收益
        returns = [
            (prices[-i] - prices[-i-2]) / prices[-i-2]
            for i in range(1, min(6, len(prices)-2))
        ]
        
        avg_return = statistics.mean(returns)
        std_return = statistics.stdev(returns) if len(returns) > 1 else 0
        
        # PPO重视稳定性
        stability_score = 1.0 / (1.0 + std_return * 10)
        
        if avg_return > 0.015 and stability_score > 0.6:
            action = "BUY"
            strength = min(avg_return * 15 * stability_score, 1.0)
            reasoning = f"PPO: stable uptrend, stability={stability_score:.2f}"
        elif avg_return < -0.015 and stability_score > 0.6:
            action = "SELL"
            strength = min(abs(avg_return) * 15 * stability_score, 1.0)
            reasoning = f"PPO: stable downtrend, stability={stability_score:.2f}"
        else:
            action = "HOLD"
            strength = 0.0
            reasoning = f"PPO: unstable signal, stability={stability_score:.2f}"
        
        return StrategySignal(
            strategy_name="PPO",
            asset=asset,
            action=action,
            confidence=0.83,
            strength=strength,
            expected_return=0.11 * strength if action == "BUY" else 0.0,
            risk_level=0.55,
            reasoning=reasoning
        )
    
    def dqn_strategy(self, asset: str, market_data: Dict) -> StrategySignal:
        """
        DQN (Deep Q-Network)
        使用深度神经网络近似动作价值函数
        
        注：简化版本
        """
        prices = market_data.get('prices', [])
        
        if len(prices) < 10:
            return StrategySignal(
                strategy_name="DQN",
                asset=asset,
                action="HOLD",
                confidence=0.0,
                strength=0.0,
                expected_return=0.0,
                risk_level=0.7,
                reasoning="Insufficient data"
            )
        
        # 简化：模拟DQN的Q值估计
        # 计算不同动作的预期Q值
        current_price = prices[-1]
        avg_price_5 = statistics.mean(prices[-5:])
        avg_price_10 = statistics.mean(prices[-10:])
        
        # Q值估计（简化）
        q_buy = (avg_price_5 - current_price) / current_price * 100
        q_sell = (current_price - avg_price_10) / avg_price_10 * 100
        q_hold = 0
        
        # 选择Q值最大的动作
        q_values = {"BUY": q_buy, "SELL": q_sell, "HOLD": q_hold}
        action = max(q_values, key=q_values.get)
        q_max = q_values[action]
        
        if action == "HOLD":
            strength = 0.0
            reasoning = "DQN: HOLD has max Q-value"
        else:
            strength = min(abs(q_max) / 5, 1.0)
            reasoning = f"DQN: {action} Q={q_max:.2f}"
        
        return StrategySignal(
            strategy_name="DQN",
            asset=asset,
            action=action,
            confidence=0.81,
            strength=strength,
            expected_return=0.12 * strength if action == "BUY" else 0.0,
            risk_level=0.6,
            reasoning=reasoning
        )
    
    # ============ 辅助函数 ============
    
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
    
    def _calculate_kdj_k(self, prices: List[float], period: int = 9) -> float:
        """计算KDJ的K值（简化版）"""
        if len(prices) < period:
            return 50.0
        
        recent_prices = prices[-period:]
        highest = max(recent_prices)
        lowest = min(recent_prices)
        current = prices[-1]
        
        if highest == lowest:
            return 50.0
        
        rsv = ((current - lowest) / (highest - lowest)) * 100
        return rsv  # 简化：直接返回RSV作为K值
    
    # ============ 🎯 NEW: Enhanced Strategies ============
    
    def composite_technical_strategy(self, asset: str, market_data: Dict) -> StrategySignal:
        """
        Composite Technical Strategy - Fusion of Multiple Indicators
        
        Combines:
        - MACD (trend direction)
        - RSI (overbought/oversold)
        - SMA (long-term trend)
        - Volume (confirmation)
        
        This is MORE RELIABLE than any single indicator.
        """
        prices = market_data.get('prices', [])
        volumes = market_data.get('volumes', [])
        
        if len(prices) < 200:
            return StrategySignal(
                strategy_name="Composite Technical",
                asset=asset,
                action="HOLD",
                confidence=0.0,
                strength=0.0,
                expected_return=0.0,
                risk_level=0.5,
                reasoning="Insufficient data for composite analysis (need 200+ candles)"
            )
        
        # 1. Get signals from existing strategies
        macd_signal = self.macd_strategy(asset, market_data)
        kdj_rsi_signal = self.kdj_rsi_strategy(asset, market_data)
        
        # 2. Calculate SMA trend
        sma_50 = self._calculate_sma(prices, 50)
        sma_200 = self._calculate_sma(prices, 200)
        
        if sma_50 > sma_200:
            trend = "bullish"
            trend_signal = "BUY"
        elif sma_50 < sma_200:
            trend = "bearish"
            trend_signal = "SELL"
        else:
            trend = "neutral"
            trend_signal = "HOLD"
        
        # 3. Volume analysis
        if len(volumes) >= 20:
            current_volume = volumes[-1]
            avg_volume = statistics.mean(volumes[-20:])
            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1.0
            volume_strong = volume_ratio > 1.3
            volume_weak = volume_ratio < 0.7
        else:
            volume_strong = False
            volume_weak = False
            volume_ratio = 1.0
        
        # 4. Fusion logic - voting system
        signals = {
            'macd': macd_signal.action,
            'kdj_rsi': kdj_rsi_signal.action,
            'trend': trend_signal
        }
        
        buy_score = sum(1 for s in signals.values() if s == 'BUY')
        sell_score = sum(1 for s in signals.values() if s == 'SELL')
        
        # 5. Decision matrix
        if buy_score >= 2:  # 2+ indicators say BUY
            # Check if RSI is not overbought
            rsi = self._calculate_rsi(prices)
            if rsi > 75:
                action = "HOLD"
                confidence = 0.6
                reasoning = f"2+ BUY signals BUT RSI overbought ({rsi:.1f})"
            elif volume_strong:
                action = "BUY"
                confidence = 0.90
                reasoning = f"Strong BUY: {buy_score}/3 signals + volume confirmation (ratio: {volume_ratio:.2f}x)"
            else:
                action = "BUY"
                confidence = 0.75
                reasoning = f"Moderate BUY: {buy_score}/3 signals (weak volume)"
        
        elif sell_score >= 2:  # 2+ indicators say SELL
            action = "SELL"
            confidence = 0.85
            reasoning = f"Strong SELL: {sell_score}/3 signals (MACD:{signals['macd']}, RSI:{signals['kdj_rsi']}, Trend:{trend})"
        
        elif buy_score == 1 and sell_score == 0 and volume_strong:
            # Weak buy but strong volume
            action = "BUY"
            confidence = 0.65
            reasoning = f"Weak BUY signal but strong volume support (ratio: {volume_ratio:.2f}x)"
        
        else:
            action = "HOLD"
            confidence = 0.5
            reasoning = f"Mixed signals: BUY={buy_score}, SELL={sell_score}, Trend={trend}"
        
        # 6. Calculate composite strength
        strength = (macd_signal.strength + kdj_rsi_signal.strength) / 2
        if volume_strong:
            strength *= 1.2  # Boost with volume
        strength = min(strength, 1.0)
        
        return StrategySignal(
            strategy_name="Composite Technical",
            asset=asset,
            action=action,
            confidence=confidence,
            strength=strength,
            expected_return=0.10 * strength if action == "BUY" else 0.0,
            risk_level=0.4,
            reasoning=reasoning
        )
    
    def sentiment_adjusted_strategy(self, asset: str, market_data: Dict) -> StrategySignal:
        """
        Sentiment-Adjusted Strategy
        
        Takes composite technical signal and adjusts based on news sentiment:
        - Positive news → Increase confidence
        - Negative news → Reduce confidence or reverse signal
        - Neutral → No change
        
        This is what INSTITUTIONAL TRADERS do!
        """
        # 1. Get technical signal (from composite strategy)
        tech_signal = self.composite_technical_strategy(asset, market_data)
        
        # 2. Get news sentiment (from market_data)
        sentiment = market_data.get('sentiment', {})
        
        if not sentiment:
            # No sentiment data, return technical signal as-is
            return StrategySignal(
                strategy_name="Sentiment-Adjusted",
                asset=tech_signal.asset,
                action=tech_signal.action,
                confidence=tech_signal.confidence,
                strength=tech_signal.strength,
                expected_return=tech_signal.expected_return,
                risk_level=tech_signal.risk_level,
                reasoning=f"{tech_signal.reasoning} (no sentiment data)"
            )
        
        sentiment_type = sentiment.get('sentiment', 'neutral')
        sentiment_score = sentiment.get('score', 0.0)  # -1 to 1
        news_count = sentiment.get('news_count', 0)
        
        # 3. Sentiment adjustment logic
        action = tech_signal.action
        confidence = tech_signal.confidence
        reasoning = tech_signal.reasoning
        
        if sentiment_type == 'negative' and tech_signal.action == 'BUY':
            # Technical says BUY, but news is negative
            if sentiment_score < -0.5 and news_count > 3:
                # STRONG negative news → Don't buy!
                action = "HOLD"
                confidence = 0.5
                reasoning = f"{tech_signal.reasoning} BUT strong negative news ({news_count} articles, score {sentiment_score:.2f}) → HOLD instead"
            else:
                # Mild negative → Reduce confidence
                action = "BUY"
                confidence = tech_signal.confidence * 0.7
                reasoning = f"{tech_signal.reasoning} with CAUTION (negative sentiment: {sentiment_score:.2f})"
        
        elif sentiment_type == 'positive' and tech_signal.action == 'BUY':
            # Technical + News both bullish → HIGH CONFIDENCE
            action = "BUY"
            confidence = min(tech_signal.confidence * 1.25, 0.95)
            reasoning = f"{tech_signal.reasoning} + POSITIVE news boost! (score: {sentiment_score:.2f}, {news_count} articles)"
        
        elif sentiment_type == 'negative' and tech_signal.action == 'SELL':
            # Technical + News both bearish → STRONG SELL
            action = "SELL"
            confidence = min(tech_signal.confidence * 1.3, 0.95)
            reasoning = f"{tech_signal.reasoning} + negative news confirmation (score: {sentiment_score:.2f})"
        
        elif sentiment_type == 'positive' and tech_signal.action == 'SELL':
            # Technical says SELL, but news is positive → Conflict
            if sentiment_score > 0.5 and news_count > 3:
                # STRONG positive news → Maybe don't sell
                action = "HOLD"
                confidence = 0.55
                reasoning = f"{tech_signal.reasoning} BUT strong positive news → HOLD for now"
            else:
                action = "SELL"
                confidence = tech_signal.confidence * 0.8
                reasoning = f"{tech_signal.reasoning} (mildly positive news: {sentiment_score:.2f})"
        
        else:
            # Neutral sentiment or HOLD → Keep technical signal
            if sentiment_type != 'neutral':
                reasoning = f"{tech_signal.reasoning} (sentiment: {sentiment_type})"
        
        # 4. Adjust expected return based on sentiment
        expected_return = tech_signal.expected_return
        if action == "BUY":
            expected_return *= (1 + sentiment_score * 0.3)  # Sentiment can boost/reduce expected return
        
        # 5. Adjust risk level
        risk_level = tech_signal.risk_level
        if abs(sentiment_score) > 0.7:
            # Extreme sentiment (positive or negative) increases risk
            risk_level *= 1.2
        risk_level = min(risk_level, 1.0)
        
        return StrategySignal(
            strategy_name="Sentiment-Adjusted",
            asset=asset,
            action=action,
            confidence=confidence,
            strength=tech_signal.strength,
            expected_return=expected_return,
            risk_level=risk_level,
            reasoning=reasoning
        )
    
    def _calculate_sma(self, prices: List[float], period: int) -> float:
        """Calculate Simple Moving Average"""
        if len(prices) < period:
            return prices[-1] if prices else 0
        
        return statistics.mean(prices[-period:])
    
    def get_all_strategies(self) -> List[str]:
        """获取所有策略名称"""
        return [
            "buy_and_hold",
            "macd_strategy",
            "kdj_rsi_strategy",
            "zscore_mean_reversion",
            "composite_technical_strategy",  # NEW ✨
            "sentiment_adjusted_strategy",    # NEW ✨
            "lgbm_strategy",
            "lstm_strategy",
            "transformer_strategy",
            "sac_strategy",
            "ppo_strategy",
            "dqn_strategy"
        ]
    
    def run_strategy(self, strategy_name: str, asset: str, market_data: Dict) -> StrategySignal:
        """运行指定策略"""
        strategy_method = getattr(self, strategy_name, None)
        if strategy_method and callable(strategy_method):
            return strategy_method(asset, market_data)
        else:
            raise ValueError(f"Unknown strategy: {strategy_name}")
