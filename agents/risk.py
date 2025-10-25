from dataclasses import dataclass
from typing import Dict, Any, List
import time
import sys
import os

# 添加项目路径以导入simple_risk_metrics模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.simple_risk_metrics import SimpleRiskAnalyzer, RiskMetrics

@dataclass
class RiskLimits:
    max_trade_usdc: float
    max_slippage_bps: int

@dataclass
class TradingRecord:
    timestamp: float
    pair: str
    amount_usdc: float
    profit_usdc: float
    risk_score: float
    action: str

class RiskAgent:
    def __init__(self, cfg: dict):
        self.cfg = cfg
        self.trading_history: List[TradingRecord] = []
        self.total_profit_usdc = 0.0
        self.daily_trade_count = 0
        self.last_reset_date = time.strftime("%Y-%m-%d")
        
        # 简单风险分析器（纯Python实现，避免numpy/scipy版本冲突）
        risk_free_rate = cfg.get('risk_parameters', {}).get('sharpe_risk_free_rate', 0.04)
        self.advanced_risk_analyzer = SimpleRiskAnalyzer(risk_free_rate)
        
        # 历史数据提供器（用于获取真实市场数据）
        from stellar.historical_data import HistoricalDataProvider
        self.historical_data = HistoricalDataProvider(cfg)
    
    def calculate_sentiment_adjusted_position_size(self, asset: str, base_position: float, sentiment: Dict) -> float:
        """
        🎯 NEW: Calculate position size adjusted for news sentiment
        
        Args:
            asset: Asset symbol
            base_position: Base position size (0.0 to 1.0)
            sentiment: Sentiment data with 'sentiment', 'score', 'news_count'
        
        Returns:
            Adjusted position size (0.0 to 1.0)
        """
        if not sentiment or sentiment.get('news_count', 0) == 0:
            # No sentiment data, return base position
            return base_position
        
        sentiment_type = sentiment.get('sentiment', 'neutral')
        sentiment_score = sentiment.get('score', 0.0)  # -1 to 1
        news_count = sentiment.get('news_count', 0)
        
        # Calculate sentiment adjustment factor
        if sentiment_type == 'negative':
            # Negative news → Reduce position
            if sentiment_score < -0.5 and news_count > 3:
                # STRONG negative → Reduce by 50-70%
                adjustment = 0.3 + (1 + sentiment_score) * 0.2  # 0.3 to 0.4
            else:
                # Mild negative → Reduce by 20-40%
                adjustment = 0.6 + (1 + sentiment_score) * 0.2  # 0.6 to 0.8
        
        elif sentiment_type == 'positive':
            # Positive news → Can slightly increase (but cautiously)
            if sentiment_score > 0.5 and news_count > 3:
                # STRONG positive → Increase by 10-20%
                adjustment = 1.0 + sentiment_score * 0.2  # 1.1 to 1.2
            else:
                # Mild positive → Increase by 5-10%
                adjustment = 1.0 + sentiment_score * 0.1  # 1.0 to 1.1
        
        else:
            # Neutral → No adjustment
            adjustment = 1.0
        
        # Apply adjustment
        adjusted_position = base_position * adjustment
        
        # Ensure within bounds [0, 1]
        adjusted_position = max(0.0, min(adjusted_position, 1.0))
        
        print(f"📊 Position sizing for {asset}:")
        print(f"   Base: {base_position:.1%}")
        print(f"   Sentiment: {sentiment_type} (score: {sentiment_score:.2f}, {news_count} articles)")
        print(f"   Adjustment: ×{adjustment:.2f}")
        print(f"   Final: {adjusted_position:.1%}")
        
        return adjusted_position

    def pool_score(self, depth_usd: float, impact_bps: float, vol_z: float) -> float:
        # simple weighted score 0..1
        s = 0.0
        s += min(depth_usd / self.cfg["risk"]["min_pool_depth_usd"], 1.0) * 0.5
        s += max(0, 1 - impact_bps / self.cfg["risk"]["max_slippage_bps"]) * 0.3
        s += min(max(vol_z / 3.0, 0), 1.0) * 0.2
        return max(0.0, min(1.0, s))

    def guard(self, pair: str, planned_usdc: float, score: float) -> tuple[str, RiskLimits]:
        lim = RiskLimits(self.cfg["risk"]["max_trade_usdc"], self.cfg["risk"]["max_slippage_bps"])
        if score < self.cfg["risk"]["pool_score_threshold"]:
            return ("HALT", lim)
        if planned_usdc > lim.max_trade_usdc:
            return ("REDUCE", lim)
        return ("OK", lim)

    def receive_trading_profit(self, profit_usdc: float, trading_details: Dict[str, Any]) -> Dict[str, Any]:
        """Receive USDC profit from trading agent and perform risk assessment"""
        current_date = time.strftime("%Y-%m-%d")
        
        # Reset daily counter if new day
        if current_date != self.last_reset_date:
            self.daily_trade_count = 0
            self.last_reset_date = current_date
        
        # Record the trading activity
        record = TradingRecord(
            timestamp=time.time(),
            pair=trading_details.get('pair', 'unknown'),
            amount_usdc=trading_details.get('amount_usdc', 0.0),
            profit_usdc=profit_usdc,
            risk_score=trading_details.get('risk_score', 0.0),
            action=trading_details.get('action', 'unknown')
        )
        self.trading_history.append(record)
        
        # Update total profit
        self.total_profit_usdc += profit_usdc
        self.daily_trade_count += 1
        
        # Risk assessment
        risk_assessment = self._assess_risk()
        
        return {
            "profit_received": profit_usdc,
            "total_profit_usdc": self.total_profit_usdc,
            "daily_trade_count": self.daily_trade_count,
            "risk_assessment": risk_assessment,
            "recommendation": self._get_risk_recommendation(risk_assessment)
        }

    def _assess_risk(self) -> Dict[str, Any]:
        """Assess current risk level based on trading history"""
        if not self.trading_history:
            return {"risk_level": "LOW", "score": 0.0}
        
        recent_trades = [t for t in self.trading_history if time.time() - t.timestamp < 3600]  # Last hour
        daily_trades = [t for t in self.trading_history if time.strftime("%Y-%m-%d", time.localtime(t.timestamp)) == time.strftime("%Y-%m-%d")]
        
        # Calculate risk metrics
        total_volume_24h = sum(t.amount_usdc for t in daily_trades)
        avg_profit_per_trade = sum(t.profit_usdc for t in recent_trades) / max(len(recent_trades), 1)
        win_rate = len([t for t in recent_trades if t.profit_usdc > 0]) / max(len(recent_trades), 1)
        
        # Risk score calculation
        risk_score = 0.0
        
        # Volume risk (higher volume = higher risk)
        if total_volume_24h > self.cfg["risk"]["max_trade_usdc"] * 5:
            risk_score += 0.3
        
        # Frequency risk (too many trades = higher risk)
        if self.daily_trade_count > self.cfg["risk"]["daily_max_trades_per_pair"]:
            risk_score += 0.4
        
        # Profit consistency risk
        if win_rate < 0.5:
            risk_score += 0.2
        
        # Recent loss streak
        recent_losses = len([t for t in recent_trades[-5:] if t.profit_usdc < 0])
        if recent_losses >= 3:
            risk_score += 0.3
        
        # Determine risk level
        if risk_score < 0.3:
            risk_level = "LOW"
        elif risk_score < 0.6:
            risk_level = "MEDIUM"
        else:
            risk_level = "HIGH"
        
        return {
            "risk_level": risk_level,
            "score": risk_score,
            "total_volume_24h": total_volume_24h,
            "avg_profit_per_trade": avg_profit_per_trade,
            "win_rate": win_rate,
            "recent_trades_count": len(recent_trades)
        }

    def _get_risk_recommendation(self, risk_assessment: Dict[str, Any]) -> str:
        """Get risk management recommendation based on assessment"""
        risk_level = risk_assessment["risk_level"]
        risk_score = risk_assessment["score"]
        
        if risk_level == "LOW":
            return "Continue trading with current parameters"
        elif risk_level == "MEDIUM":
            return "Consider reducing position sizes or taking a break"
        else:  # HIGH
            return "HALT trading until risk conditions improve"

    def should_halt_trading(self) -> bool:
        """Determine if trading should be halted based on risk assessment"""
        risk_assessment = self._assess_risk()
        return risk_assessment["risk_level"] == "HIGH"

    def get_risk_summary(self) -> Dict[str, Any]:
        """Get comprehensive risk summary"""
        risk_assessment = self._assess_risk()
        
        # 获取高级风险指标
        var_metrics = self.get_var_metrics()
        performance_metrics = self.get_performance_metrics()
        drawdown_metrics = self.get_drawdown_metrics()
        
        return {
            "current_risk": risk_assessment,
            "total_profit_usdc": self.total_profit_usdc,
            "daily_trade_count": self.daily_trade_count,
            "trading_history_count": len(self.trading_history),
            "should_halt": self.should_halt_trading(),
            "recommendation": self._get_risk_recommendation(risk_assessment),
            
            # 高级风险指标
            "var_metrics": var_metrics,
            "performance_metrics": performance_metrics,
            "drawdown_metrics": drawdown_metrics
        }

    def reset_daily_counters(self):
        """Reset daily trading counters (called at start of new day)"""
        self.daily_trade_count = 0
        self.last_reset_date = time.strftime("%Y-%m-%d")
    
    def update_portfolio_value(self, portfolio_value: float):
        """更新投资组合价值（用于计算收益和回撤）"""
        self.advanced_risk_analyzer.add_portfolio_value(portfolio_value)
    
    def calculate_daily_return(self, current_value: float, previous_value: float) -> float:
        """计算并记录日收益率"""
        if previous_value > 0:
            daily_return = (current_value - previous_value) / previous_value
            self.advanced_risk_analyzer.add_return(daily_return)
            return daily_return
        return 0.0
    
    def get_advanced_risk_metrics(self, market_returns: List[float] = None) -> RiskMetrics:
        """获取完整的高级风险指标"""
        return self.advanced_risk_analyzer.get_comprehensive_metrics(market_returns)
    
    def get_var_metrics(self) -> Dict[str, float]:
        """获取VaR和CVaR指标"""
        return {
            'var_95': self.advanced_risk_analyzer.calculate_var(0.95),
            'var_99': self.advanced_risk_analyzer.calculate_var(0.99),
            'cvar_95': self.advanced_risk_analyzer.calculate_cvar(0.95),
            'cvar_99': self.advanced_risk_analyzer.calculate_cvar(0.99)
        }
    
    def get_performance_metrics(self) -> Dict[str, float]:
        """获取性能指标"""
        return {
            'sharpe_ratio': self.advanced_risk_analyzer.calculate_sharpe_ratio(),
            'sortino_ratio': self.advanced_risk_analyzer.calculate_sortino_ratio(),
            'calmar_ratio': self.advanced_risk_analyzer.calculate_calmar_ratio(),
            'omega_ratio': self.advanced_risk_analyzer.calculate_omega_ratio()
        }
    
    def get_drawdown_metrics(self) -> Dict[str, Any]:
        """获取回撤指标"""
        max_dd, dd_duration, current_dd = self.advanced_risk_analyzer.calculate_max_drawdown()
        return {
            'max_drawdown': max_dd,
            'max_drawdown_pct': max_dd * 100,
            'current_drawdown': current_dd,
            'current_drawdown_pct': current_dd * 100,
            'drawdown_duration_days': dd_duration
        }