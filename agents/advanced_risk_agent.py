"""
高级Risk Agent
- Portfolio风险计算
- 实时监控：滑点、流动性、异常行为
- 自动停止机制
"""

from dataclasses import dataclass
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import statistics
from agents.simple_risk_metrics import SimpleRiskAnalyzer, RiskMetrics

@dataclass
class SlippageMetrics:
    """滑点指标"""
    asset: str
    expected_price: float
    actual_price: float
    slippage_bps: float  # 基点
    timestamp: datetime
    is_acceptable: bool

@dataclass
class LiquidityMetrics:
    """流动性指标"""
    asset: str
    bid_depth_usd: float
    ask_depth_usd: float
    spread_bps: float
    volume_24h_usd: float
    liquidity_score: float  # 0-1
    timestamp: datetime

@dataclass
class AnomalyDetection:
    """异常检测"""
    type: str  # "price_spike", "volume_anomaly", "liquidity_drain"
    asset: str
    severity: str  # "LOW", "MEDIUM", "HIGH", "CRITICAL"
    description: str
    timestamp: datetime
    should_halt: bool

@dataclass
class PortfolioRiskMetrics:
    """投资组合风险指标"""
    # 传统风险指标
    var_95: float
    cvar_95: float
    var_99: float
    cvar_99: float
    sharpe_ratio: float
    sortino_ratio: float
    max_drawdown: float
    calmar_ratio: float
    
    # 投资组合特定指标
    portfolio_volatility: float
    correlation_risk: float
    concentration_risk: float
    diversification_ratio: float
    
    # 实时监控指标
    avg_slippage_bps: float
    max_slippage_bps: float
    liquidity_score: float
    anomaly_count: int
    
    # 综合评分
    overall_risk_score: float  # 0-1
    risk_level: str  # "LOW", "MEDIUM", "HIGH", "CRITICAL"

@dataclass
class RiskAlert:
    """风险警报"""
    level: str  # "INFO", "WARNING", "CRITICAL"
    category: str  # "SLIPPAGE", "LIQUIDITY", "ANOMALY", "PORTFOLIO"
    message: str
    timestamp: datetime
    should_halt_trading: bool

class AdvancedRiskAgent:
    """高级风险管理Agent"""
    
    def __init__(self, config: dict):
        self.config = config
        
        # 初始化基础风险分析器
        self.risk_analyzer = SimpleRiskAnalyzer()
        
        # 历史数据
        self.portfolio_history = []  # Portfolio价值历史
        self.slippage_history = []  # 滑点历史
        self.liquidity_history = []  # 流动性历史
        self.anomaly_history = []  # 异常历史
        self.alerts_history = []  # 警报历史
        
        # 风险阈值配置
        self.thresholds = {
            # 滑点阈值
            "max_slippage_bps": config.get("risk_management", {}).get("max_slippage_bps", 50),
            "warning_slippage_bps": config.get("risk_management", {}).get("warning_slippage_bps", 30),
            
            # 流动性阈值
            "min_liquidity_usd": config.get("risk_management", {}).get("min_liquidity_usd", 50000),
            "min_liquidity_score": config.get("risk_management", {}).get("min_liquidity_score", 0.5),
            
            # Portfolio风险阈值
            "max_var_95": config.get("risk_management", {}).get("max_var_95", 0.10),  # 10%
            "max_portfolio_risk": config.get("risk_management", {}).get("max_portfolio_risk", 0.75),
            "min_sharpe_ratio": config.get("risk_management", {}).get("min_sharpe_ratio", 0.5),
            
            # 异常检测阈值
            "price_spike_threshold": 0.15,  # 15%价格突变
            "volume_anomaly_multiplier": 3.0,  # 3倍正常交易量
        }
        
        # 交易暂停状态
        self.trading_halted = False
        self.halt_reason = None
        self.halt_timestamp = None
        
    async def assess_portfolio_risk(
        self,
        portfolio: Any,  # Portfolio object
        market_data: Dict[str, Any],
        current_positions: Dict[str, float]
    ) -> PortfolioRiskMetrics:
        """
        评估投资组合风险
        
        Args:
            portfolio: 投资组合对象
            market_data: 市场数据
            current_positions: 当前持仓 {asset: value_usd}
        
        Returns:
            PortfolioRiskMetrics: 完整风险指标
        """
        
        # 更新历史
        total_value = sum(current_positions.values())
        self.portfolio_history.append({
            "timestamp": datetime.now(),
            "value": total_value,
            "positions": current_positions.copy()
        })
        
        # 计算传统风险指标
        returns = self._calculate_portfolio_returns()
        
        if len(returns) >= 10:
            var_95 = self.risk_analyzer.calculate_var(returns, confidence=0.95)
            cvar_95 = self.risk_analyzer.calculate_cvar(returns, confidence=0.95)
            var_99 = self.risk_analyzer.calculate_var(returns, confidence=0.99)
            cvar_99 = self.risk_analyzer.calculate_cvar(returns, confidence=0.99)
            sharpe = self.risk_analyzer.calculate_sharpe_ratio(returns)
            sortino = self.risk_analyzer.calculate_sortino_ratio(returns)
            max_dd = self.risk_analyzer.calculate_max_drawdown(
                [h["value"] for h in self.portfolio_history]
            )
            calmar = self.risk_analyzer.calculate_calmar_ratio(returns)
        else:
            var_95 = cvar_95 = var_99 = cvar_99 = 0.0
            sharpe = sortino = calmar = 0.0
            max_dd = 0.0
        
        # 计算投资组合特定指标
        portfolio_vol = statistics.stdev(returns) if len(returns) > 1 else 0.0
        correlation_risk = self._calculate_correlation_risk(current_positions)
        concentration_risk = self._calculate_concentration_risk(current_positions)
        diversification_ratio = self._calculate_diversification_ratio(current_positions)
        
        # 实时监控指标
        avg_slippage = self._get_avg_slippage()
        max_slippage = self._get_max_slippage()
        liquidity_score = self._get_avg_liquidity_score()
        anomaly_count = len([a for a in self.anomaly_history 
                            if (datetime.now() - a.timestamp).seconds < 3600])
        
        # 计算综合风险评分
        overall_risk = self._calculate_overall_risk(
            var_95, portfolio_vol, max_slippage, liquidity_score,
            concentration_risk, anomaly_count
        )
        
        # 确定风险等级
        if overall_risk > 0.8:
            risk_level = "CRITICAL"
        elif overall_risk > 0.6:
            risk_level = "HIGH"
        elif overall_risk > 0.4:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"
        
        return PortfolioRiskMetrics(
            var_95=var_95,
            cvar_95=cvar_95,
            var_99=var_99,
            cvar_99=cvar_99,
            sharpe_ratio=sharpe,
            sortino_ratio=sortino,
            max_drawdown=max_dd,
            calmar_ratio=calmar,
            portfolio_volatility=portfolio_vol,
            correlation_risk=correlation_risk,
            concentration_risk=concentration_risk,
            diversification_ratio=diversification_ratio,
            avg_slippage_bps=avg_slippage,
            max_slippage_bps=max_slippage,
            liquidity_score=liquidity_score,
            anomaly_count=anomaly_count,
            overall_risk_score=overall_risk,
            risk_level=risk_level
        )
    
    async def monitor_slippage(
        self,
        asset: str,
        expected_price: float,
        actual_price: float
    ) -> SlippageMetrics:
        """
        监控滑点
        """
        
        # 计算滑点（基点）
        if expected_price == 0:
            slippage_bps = 0
        else:
            slippage_bps = abs(actual_price - expected_price) / expected_price * 10000
        
        is_acceptable = slippage_bps <= self.thresholds["max_slippage_bps"]
        
        metrics = SlippageMetrics(
            asset=asset,
            expected_price=expected_price,
            actual_price=actual_price,
            slippage_bps=slippage_bps,
            timestamp=datetime.now(),
            is_acceptable=is_acceptable
        )
        
        # 记录历史
        self.slippage_history.append(metrics)
        
        # 生成警报
        if slippage_bps > self.thresholds["max_slippage_bps"]:
            alert = RiskAlert(
                level="CRITICAL",
                category="SLIPPAGE",
                message=f"{asset}滑点过高: {slippage_bps:.1f} bps (限制: {self.thresholds['max_slippage_bps']} bps)",
                timestamp=datetime.now(),
                should_halt_trading=True
            )
            self.alerts_history.append(alert)
            await self._trigger_halt("高滑点风险")
            
        elif slippage_bps > self.thresholds["warning_slippage_bps"]:
            alert = RiskAlert(
                level="WARNING",
                category="SLIPPAGE",
                message=f"{asset}滑点警告: {slippage_bps:.1f} bps",
                timestamp=datetime.now(),
                should_halt_trading=False
            )
            self.alerts_history.append(alert)
        
        return metrics
    
    async def monitor_liquidity(
        self,
        asset: str,
        market_data: Dict[str, Any]
    ) -> LiquidityMetrics:
        """
        监控流动性
        """
        
        # 获取流动性数据
        orderbook = market_data.get("orderbook", {}).get(asset, {})
        bid_depth = orderbook.get("bid_depth_usd", 0)
        ask_depth = orderbook.get("ask_depth_usd", 0)
        spread_bps = orderbook.get("spread_bps", 0)
        volume_24h = market_data.get("volume_24h", {}).get(asset, 0)
        
        # 计算流动性评分 (0-1)
        depth_score = min((bid_depth + ask_depth) / 100000, 1.0)  # 10万USD为满分
        spread_score = max(1.0 - spread_bps / 100, 0.0)  # 100bps为0分
        volume_score = min(volume_24h / 1000000, 1.0)  # 100万USD为满分
        
        liquidity_score = (depth_score * 0.4 + spread_score * 0.3 + volume_score * 0.3)
        
        metrics = LiquidityMetrics(
            asset=asset,
            bid_depth_usd=bid_depth,
            ask_depth_usd=ask_depth,
            spread_bps=spread_bps,
            volume_24h_usd=volume_24h,
            liquidity_score=liquidity_score,
            timestamp=datetime.now()
        )
        
        # 记录历史
        self.liquidity_history.append(metrics)
        
        # 生成警报
        if liquidity_score < self.thresholds["min_liquidity_score"]:
            alert = RiskAlert(
                level="CRITICAL",
                category="LIQUIDITY",
                message=f"{asset}流动性不足: 评分{liquidity_score:.2f} (最低: {self.thresholds['min_liquidity_score']})",
                timestamp=datetime.now(),
                should_halt_trading=True
            )
            self.alerts_history.append(alert)
            await self._trigger_halt("流动性不足")
            
        elif liquidity_score < self.thresholds["min_liquidity_score"] + 0.1:
            alert = RiskAlert(
                level="WARNING",
                category="LIQUIDITY",
                message=f"{asset}流动性警告: 评分{liquidity_score:.2f}",
                timestamp=datetime.now(),
                should_halt_trading=False
            )
            self.alerts_history.append(alert)
        
        return metrics
    
    async def detect_anomalies(
        self,
        asset: str,
        current_price: float,
        market_data: Dict[str, Any]
    ) -> List[AnomalyDetection]:
        """
        检测异常行为
        """
        
        anomalies = []
        
        # 1. 价格突变检测
        prices = market_data.get("prices", [])
        if len(prices) >= 2:
            prev_price = prices[-2]
            price_change = abs(current_price - prev_price) / prev_price
            
            if price_change > self.thresholds["price_spike_threshold"]:
                anomaly = AnomalyDetection(
                    type="price_spike",
                    asset=asset,
                    severity="HIGH" if price_change > 0.25 else "MEDIUM",
                    description=f"价格突变{price_change*100:.1f}%: {prev_price:.2f} → {current_price:.2f}",
                    timestamp=datetime.now(),
                    should_halt=price_change > 0.25
                )
                anomalies.append(anomaly)
                self.anomaly_history.append(anomaly)
                
                if anomaly.should_halt:
                    await self._trigger_halt("价格异常波动")
        
        # 2. 交易量异常检测
        volume_24h = market_data.get("volume_24h", {}).get(asset, 0)
        avg_volume = self._get_avg_volume(asset)
        
        if avg_volume > 0:
            volume_ratio = volume_24h / avg_volume
            
            if volume_ratio > self.thresholds["volume_anomaly_multiplier"]:
                anomaly = AnomalyDetection(
                    type="volume_anomaly",
                    asset=asset,
                    severity="MEDIUM",
                    description=f"交易量异常: {volume_ratio:.1f}x正常值",
                    timestamp=datetime.now(),
                    should_halt=volume_ratio > 5.0
                )
                anomalies.append(anomaly)
                self.anomaly_history.append(anomaly)
                
                if anomaly.should_halt:
                    await self._trigger_halt("交易量异常")
        
        # 3. 流动性骤降检测
        current_liquidity = await self.monitor_liquidity(asset, market_data)
        recent_liquidity = [l for l in self.liquidity_history 
                          if l.asset == asset and 
                          (datetime.now() - l.timestamp).seconds < 3600]
        
        if len(recent_liquidity) >= 3:
            avg_recent_liquidity = statistics.mean([l.liquidity_score for l in recent_liquidity[:-1]])
            
            if current_liquidity.liquidity_score < avg_recent_liquidity * 0.5:
                anomaly = AnomalyDetection(
                    type="liquidity_drain",
                    asset=asset,
                    severity="HIGH",
                    description=f"流动性骤降: {current_liquidity.liquidity_score:.2f} vs {avg_recent_liquidity:.2f}",
                    timestamp=datetime.now(),
                    should_halt=True
                )
                anomalies.append(anomaly)
                self.anomaly_history.append(anomaly)
                await self._trigger_halt("流动性骤降")
        
        # 生成警报
        for anomaly in anomalies:
            alert = RiskAlert(
                level="CRITICAL" if anomaly.should_halt else "WARNING",
                category="ANOMALY",
                message=f"{anomaly.type}: {anomaly.description}",
                timestamp=datetime.now(),
                should_halt_trading=anomaly.should_halt
            )
            self.alerts_history.append(alert)
        
        return anomalies
    
    async def should_halt_trading(self) -> tuple[bool, Optional[str]]:
        """
        检查是否应该停止交易
        
        Returns:
            (should_halt, reason)
        """
        
        if self.trading_halted:
            return True, self.halt_reason
        
        # 检查最近的Critical警报
        recent_critical = [
            a for a in self.alerts_history
            if a.level == "CRITICAL" and 
            (datetime.now() - a.timestamp).seconds < 600  # 10分钟内
        ]
        
        if len(recent_critical) >= 3:
            await self._trigger_halt("连续Critical警报")
            return True, "连续Critical警报"
        
        return False, None
    
    async def _trigger_halt(self, reason: str):
        """触发交易暂停"""
        if not self.trading_halted:
            self.trading_halted = True
            self.halt_reason = reason
            self.halt_timestamp = datetime.now()
            
            print(f"\n🚨 TRADING HALTED: {reason}")
            print(f"   时间: {self.halt_timestamp}")
    
    def resume_trading(self):
        """恢复交易"""
        self.trading_halted = False
        self.halt_reason = None
        self.halt_timestamp = None
        print("\n✅ Trading resumed")
    
    def get_comprehensive_risk_report(self) -> Dict[str, Any]:
        """
        获取完整风险报告（用于前端展示）
        """
        
        # 最近滑点统计
        recent_slippage = [s for s in self.slippage_history 
                          if (datetime.now() - s.timestamp).seconds < 3600]
        
        slippage_stats = {
            "avg_bps": statistics.mean([s.slippage_bps for s in recent_slippage]) if recent_slippage else 0,
            "max_bps": max([s.slippage_bps for s in recent_slippage]) if recent_slippage else 0,
            "count": len(recent_slippage),
            "violations": len([s for s in recent_slippage if not s.is_acceptable])
        }
        
        # 流动性统计
        recent_liquidity = [l for l in self.liquidity_history 
                           if (datetime.now() - l.timestamp).seconds < 3600]
        
        liquidity_stats = {
            "avg_score": statistics.mean([l.liquidity_score for l in recent_liquidity]) if recent_liquidity else 0,
            "min_score": min([l.liquidity_score for l in recent_liquidity]) if recent_liquidity else 0,
            "assets_monitored": len(set(l.asset for l in recent_liquidity))
        }
        
        # 异常统计
        recent_anomalies = [a for a in self.anomaly_history 
                           if (datetime.now() - a.timestamp).seconds < 3600]
        
        anomaly_stats = {
            "total": len(recent_anomalies),
            "by_severity": {
                "CRITICAL": len([a for a in recent_anomalies if a.severity == "CRITICAL"]),
                "HIGH": len([a for a in recent_anomalies if a.severity == "HIGH"]),
                "MEDIUM": len([a for a in recent_anomalies if a.severity == "MEDIUM"]),
            },
            "by_type": {}
        }
        
        for anomaly_type in ["price_spike", "volume_anomaly", "liquidity_drain"]:
            anomaly_stats["by_type"][anomaly_type] = len([
                a for a in recent_anomalies if a.type == anomaly_type
            ])
        
        # 警报统计
        recent_alerts = [a for a in self.alerts_history 
                        if (datetime.now() - a.timestamp).seconds < 3600]
        
        alert_stats = {
            "total": len(recent_alerts),
            "by_level": {
                "CRITICAL": len([a for a in recent_alerts if a.level == "CRITICAL"]),
                "WARNING": len([a for a in recent_alerts if a.level == "WARNING"]),
                "INFO": len([a for a in recent_alerts if a.level == "INFO"]),
            },
            "by_category": {}
        }
        
        for category in ["SLIPPAGE", "LIQUIDITY", "ANOMALY", "PORTFOLIO"]:
            alert_stats["by_category"][category] = len([
                a for a in recent_alerts if a.category == category
            ])
        
        # Portfolio风险（如果有历史）
        portfolio_risk = None
        if self.portfolio_history:
            returns = self._calculate_portfolio_returns()
            if len(returns) >= 10:
                portfolio_risk = {
                    "var_95": self.risk_analyzer.calculate_var(returns, 0.95),
                    "cvar_95": self.risk_analyzer.calculate_cvar(returns, 0.95),
                    "sharpe_ratio": self.risk_analyzer.calculate_sharpe_ratio(returns),
                    "max_drawdown": self.risk_analyzer.calculate_max_drawdown(
                        [h["value"] for h in self.portfolio_history]
                    ),
                    "volatility": statistics.stdev(returns) if len(returns) > 1 else 0
                }
        
        return {
            "trading_status": {
                "halted": self.trading_halted,
                "halt_reason": self.halt_reason,
                "halt_time": self.halt_timestamp.isoformat() if self.halt_timestamp else None
            },
            "slippage": slippage_stats,
            "liquidity": liquidity_stats,
            "anomalies": anomaly_stats,
            "alerts": alert_stats,
            "portfolio_risk": portfolio_risk,
            "thresholds": self.thresholds,
            "timestamp": datetime.now().isoformat()
        }
    
    # ========== 辅助函数 ==========
    
    def _calculate_portfolio_returns(self) -> List[float]:
        """计算投资组合收益率"""
        if len(self.portfolio_history) < 2:
            return []
        
        returns = []
        for i in range(1, len(self.portfolio_history)):
            prev_value = self.portfolio_history[i-1]["value"]
            curr_value = self.portfolio_history[i]["value"]
            
            if prev_value > 0:
                ret = (curr_value - prev_value) / prev_value
                returns.append(ret)
        
        return returns
    
    def _calculate_correlation_risk(self, positions: Dict[str, float]) -> float:
        """计算相关性风险（简化版）"""
        # 高风险资产间的相关性
        high_risk_assets = ['BTC', 'ETH', 'SOL', 'FET']
        high_risk_weight = sum(
            positions.get(asset, 0) for asset in high_risk_assets
        ) / max(sum(positions.values()), 1)
        
        # 相关性风险 = 高风险资产集中度
        return min(high_risk_weight * 1.5, 1.0)
    
    def _calculate_concentration_risk(self, positions: Dict[str, float]) -> float:
        """计算集中度风险"""
        total = sum(positions.values())
        if total == 0:
            return 0
        
        weights = [v / total for v in positions.values()]
        
        # Herfindahl指数
        herfindahl = sum(w**2 for w in weights)
        
        # 归一化到0-1
        n = len(positions)
        min_h = 1 / n  # 完全分散
        max_h = 1.0    # 完全集中
        
        if max_h == min_h:
            return 0
        
        normalized = (herfindahl - min_h) / (max_h - min_h)
        return normalized
    
    def _calculate_diversification_ratio(self, positions: Dict[str, float]) -> float:
        """计算分散化比率"""
        n = len([v for v in positions.values() if v > 0])
        
        if n <= 1:
            return 0.0
        
        # 简化: 持有资产数量越多，分散化越好
        max_assets = 10
        return min(n / max_assets, 1.0)
    
    def _get_avg_slippage(self) -> float:
        """获取平均滑点"""
        recent = [s.slippage_bps for s in self.slippage_history 
                 if (datetime.now() - s.timestamp).seconds < 3600]
        return statistics.mean(recent) if recent else 0.0
    
    def _get_max_slippage(self) -> float:
        """获取最大滑点"""
        recent = [s.slippage_bps for s in self.slippage_history 
                 if (datetime.now() - s.timestamp).seconds < 3600]
        return max(recent) if recent else 0.0
    
    def _get_avg_liquidity_score(self) -> float:
        """获取平均流动性评分"""
        recent = [l.liquidity_score for l in self.liquidity_history 
                 if (datetime.now() - l.timestamp).seconds < 3600]
        return statistics.mean(recent) if recent else 0.0
    
    def _get_avg_volume(self, asset: str) -> float:
        """获取资产的平均交易量"""
        # 这里应该从历史数据计算，暂时返回固定值
        return 1000000.0  # 100万USD
    
    def _calculate_overall_risk(
        self,
        var_95: float,
        volatility: float,
        max_slippage: float,
        liquidity_score: float,
        concentration: float,
        anomaly_count: int
    ) -> float:
        """计算综合风险评分"""
        
        # 各因素权重
        var_score = min(var_95 / 0.15, 1.0) * 0.25  # VaR权重25%
        vol_score = min(volatility / 0.30, 1.0) * 0.20  # 波动率20%
        slippage_score = min(max_slippage / 100, 1.0) * 0.15  # 滑点15%
        liquidity_score_inv = (1 - liquidity_score) * 0.20  # 流动性20%
        concentration_score = concentration * 0.15  # 集中度15%
        anomaly_score = min(anomaly_count / 5, 1.0) * 0.05  # 异常5%
        
        overall = (var_score + vol_score + slippage_score + 
                  liquidity_score_inv + concentration_score + anomaly_score)
        
        return min(overall, 1.0)
