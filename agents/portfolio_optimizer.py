"""
投资组合优化
使用USDC对冲高风险资产
"""

from dataclasses import dataclass
from typing import List, Dict, Any
import statistics

@dataclass
class PortfolioAllocation:
    """投资组合配置"""
    asset: str
    current_weight: float  # 当前权重
    target_weight: float   # 目标权重
    action: str  # "BUY", "SELL", "HOLD"
    amount: float  # 交易数量
    reasoning: str

@dataclass
class Portfolio:
    """完整的投资组合"""
    allocations: List[PortfolioAllocation]
    total_value_usd: float
    risk_score: float
    expected_return: float
    sharpe_ratio: float
    usdc_hedge_ratio: float  # USDC对冲比例

class PortfolioOptimizer:
    """投资组合优化器"""
    
    def __init__(self, config: dict):
        self.config = config
        
        # 风险等级定义
        self.high_risk_assets = ['BTC', 'ETH', 'SOL', 'FET']  # 高波动
        self.medium_risk_assets = ['LINK', 'AAVE', 'LDO', 'ARB']  # 中等波动
        self.low_risk_assets = ['USDT', 'USDC']  # 稳定币
        
    def optimize_portfolio(
        self,
        strategy_signals: Dict[str, List],  # {asset: [signal1, signal2, ...]}
        current_portfolio: Dict[str, float],  # {asset: balance}
        total_value_usd: float,
        risk_tolerance: float = 0.6  # 0-1, 越低越保守
    ) -> Portfolio:
        """
        优化投资组合
        
        Args:
            strategy_signals: 每个资产的所有策略信号
            current_portfolio: 当前持仓
            total_value_usd: 投资组合总价值
            risk_tolerance: 风险容忍度
        
        Returns:
            Portfolio: 优化后的投资组合
        """
        
        # Step 1: 聚合每个资产的策略信号
        aggregated_signals = self._aggregate_signals(strategy_signals)
        
        # Step 2: 计算每个资产的风险和预期收益
        asset_metrics = self._calculate_asset_metrics(aggregated_signals)
        
        # Step 3: 确定USDC对冲比例
        usdc_hedge_ratio = self._calculate_usdc_hedge(
            asset_metrics, risk_tolerance
        )
        
        # Step 4: 优化配置权重
        target_weights = self._optimize_weights(
            asset_metrics, usdc_hedge_ratio, risk_tolerance
        )
        
        # Step 5: 生成交易指令
        allocations = self._generate_allocations(
            target_weights, current_portfolio, total_value_usd
        )
        
        # Step 6: 计算投资组合指标
        portfolio_risk = self._calculate_portfolio_risk(target_weights, asset_metrics)
        portfolio_return = self._calculate_portfolio_return(target_weights, asset_metrics)
        sharpe = self._calculate_sharpe_ratio(portfolio_return, portfolio_risk)
        
        return Portfolio(
            allocations=allocations,
            total_value_usd=total_value_usd,
            risk_score=portfolio_risk,
            expected_return=portfolio_return,
            sharpe_ratio=sharpe,
            usdc_hedge_ratio=usdc_hedge_ratio
        )
    
    def _aggregate_signals(self, strategy_signals: Dict[str, List]) -> Dict[str, Dict]:
        """聚合每个资产的策略信号"""
        aggregated = {}
        
        for asset, signals in strategy_signals.items():
            if not signals:
                continue
            
            # 统计买卖信号
            buy_count = sum(1 for s in signals if s.action == "BUY")
            sell_count = sum(1 for s in signals if s.action == "SELL")
            hold_count = sum(1 for s in signals if s.action == "HOLD")
            
            # 平均信心度和强度
            avg_confidence = statistics.mean([s.confidence for s in signals])
            avg_strength = statistics.mean([s.strength for s in signals])
            avg_expected_return = statistics.mean([s.expected_return for s in signals])
            avg_risk = statistics.mean([s.risk_level for s in signals])
            
            # 综合信号
            total_signals = len(signals)
            buy_ratio = buy_count / total_signals
            sell_ratio = sell_count / total_signals
            
            if buy_ratio > 0.5:
                consensus_action = "BUY"
                consensus_strength = buy_ratio * avg_strength
            elif sell_ratio > 0.5:
                consensus_action = "SELL"
                consensus_strength = sell_ratio * avg_strength
            else:
                consensus_action = "HOLD"
                consensus_strength = 0.0
            
            aggregated[asset] = {
                "action": consensus_action,
                "confidence": avg_confidence,
                "strength": consensus_strength,
                "expected_return": avg_expected_return,
                "risk_level": avg_risk,
                "buy_count": buy_count,
                "sell_count": sell_count,
                "hold_count": hold_count
            }
        
        return aggregated
    
    def _calculate_asset_metrics(self, aggregated_signals: Dict) -> Dict[str, Dict]:
        """计算每个资产的风险和收益指标"""
        metrics = {}
        
        for asset, signal in aggregated_signals.items():
            # 基于资产类型调整风险
            if asset in self.high_risk_assets:
                risk_multiplier = 1.5
            elif asset in self.medium_risk_assets:
                risk_multiplier = 1.0
            else:  # low risk
                risk_multiplier = 0.3
            
            adjusted_risk = signal['risk_level'] * risk_multiplier
            
            metrics[asset] = {
                "expected_return": signal['expected_return'],
                "risk": adjusted_risk,
                "sharpe": signal['expected_return'] / max(adjusted_risk, 0.01),
                "action": signal['action'],
                "confidence": signal['confidence'],
                "strength": signal['strength']
            }
        
        return metrics
    
    def _calculate_usdc_hedge(
        self,
        asset_metrics: Dict[str, Dict],
        risk_tolerance: float
    ) -> float:
        """
        计算USDC对冲比例
        
        高风险资产比例越高，USDC对冲比例越高
        """
        # 计算高风险资产的总风险
        high_risk_total = sum(
            metrics['risk'] * metrics['confidence']
            for asset, metrics in asset_metrics.items()
            if asset in self.high_risk_assets
        )
        
        # 基础对冲比例
        base_hedge = 0.2  # 至少20% USDC
        
        # 根据风险调整
        risk_adjusted_hedge = base_hedge + (1 - risk_tolerance) * 0.3
        
        # 根据高风险资产风险调整
        if high_risk_total > 2.0:
            risk_adjusted_hedge += 0.15
        elif high_risk_total > 1.5:
            risk_adjusted_hedge += 0.10
        
        return min(risk_adjusted_hedge, 0.5)  # 最多50% USDC
    
    def _optimize_weights(
        self,
        asset_metrics: Dict[str, Dict],
        usdc_hedge_ratio: float,
        risk_tolerance: float
    ) -> Dict[str, float]:
        """
        优化投资组合权重
        
        目标：最大化风险调整后收益（Sharpe Ratio）
        """
        weights = {}
        
        # Step 1: USDC权重（对冲）
        weights['USDC'] = usdc_hedge_ratio
        remaining_weight = 1.0 - usdc_hedge_ratio
        
        # Step 2: 过滤掉SELL信号的资产
        investable_assets = {
            asset: metrics
            for asset, metrics in asset_metrics.items()
            if metrics['action'] != 'SELL' and asset != 'USDC'
        }
        
        if not investable_assets:
            # 如果没有可投资资产，全部USDC
            weights['USDC'] = 1.0
            return weights
        
        # Step 3: 按Sharpe Ratio排序
        sorted_assets = sorted(
            investable_assets.items(),
            key=lambda x: x[1]['sharpe'],
            reverse=True
        )
        
        # Step 4: 分配权重（Sharpe加权）
        total_sharpe = sum(metrics['sharpe'] for _, metrics in sorted_assets)
        
        for asset, metrics in sorted_assets:
            # 基于Sharpe的权重
            sharpe_weight = (metrics['sharpe'] / total_sharpe) * remaining_weight
            
            # 基于信号强度调整
            strength_adjusted = sharpe_weight * (0.5 + 0.5 * metrics['strength'])
            
            # 风险限制
            if asset in self.high_risk_assets:
                max_weight = 0.25 * risk_tolerance  # 高风险资产限制
            elif asset in self.medium_risk_assets:
                max_weight = 0.35
            else:
                max_weight = 0.4
            
            weights[asset] = min(strength_adjusted, max_weight)
        
        # Step 5: 归一化权重
        total_weight = sum(weights.values())
        if total_weight > 0:
            weights = {asset: w / total_weight for asset, w in weights.items()}
        
        return weights
    
    def _generate_allocations(
        self,
        target_weights: Dict[str, float],
        current_portfolio: Dict[str, float],
        total_value_usd: float
    ) -> List[PortfolioAllocation]:
        """生成交易指令"""
        allocations = []
        
        # 计算当前权重
        current_weights = self._calculate_current_weights(
            current_portfolio, total_value_usd
        )
        
        for asset, target_weight in target_weights.items():
            current_weight = current_weights.get(asset, 0.0)
            weight_diff = target_weight - current_weight
            
            # 确定动作
            if abs(weight_diff) < 0.02:  # 2%阈值
                action = "HOLD"
                amount = 0.0
                reasoning = f"Current {current_weight:.1%} ≈ Target {target_weight:.1%}"
            elif weight_diff > 0:
                action = "BUY"
                amount = weight_diff * total_value_usd
                reasoning = f"Increase from {current_weight:.1%} to {target_weight:.1%}"
            else:
                action = "SELL"
                amount = abs(weight_diff) * total_value_usd
                reasoning = f"Decrease from {current_weight:.1%} to {target_weight:.1%}"
            
            allocations.append(PortfolioAllocation(
                asset=asset,
                current_weight=current_weight,
                target_weight=target_weight,
                action=action,
                amount=amount,
                reasoning=reasoning
            ))
        
        # 添加当前持有但目标为0的资产
        for asset, weight in current_weights.items():
            if asset not in target_weights and weight > 0.01:
                allocations.append(PortfolioAllocation(
                    asset=asset,
                    current_weight=weight,
                    target_weight=0.0,
                    action="SELL",
                    amount=weight * total_value_usd,
                    reasoning=f"Exit position: {weight:.1%} → 0%"
                ))
        
        return allocations
    
    def _calculate_current_weights(
        self,
        current_portfolio: Dict[str, float],
        total_value_usd: float
    ) -> Dict[str, float]:
        """计算当前权重"""
        if total_value_usd == 0:
            return {}
        
        weights = {}
        for asset, value in current_portfolio.items():
            weights[asset] = value / total_value_usd
        
        return weights
    
    def _calculate_portfolio_risk(
        self,
        weights: Dict[str, float],
        asset_metrics: Dict[str, Dict]
    ) -> float:
        """计算投资组合风险"""
        total_risk = 0.0
        
        for asset, weight in weights.items():
            if asset in asset_metrics:
                asset_risk = asset_metrics[asset]['risk']
                total_risk += weight * asset_risk
        
        # USDC降低风险
        usdc_weight = weights.get('USDC', 0)
        total_risk = total_risk * (1 - usdc_weight * 0.5)
        
        return total_risk
    
    def _calculate_portfolio_return(
        self,
        weights: Dict[str, float],
        asset_metrics: Dict[str, Dict]
    ) -> float:
        """计算投资组合预期收益"""
        total_return = 0.0
        
        for asset, weight in weights.items():
            if asset in asset_metrics:
                asset_return = asset_metrics[asset]['expected_return']
                total_return += weight * asset_return
        
        return total_return
    
    def _calculate_sharpe_ratio(self, portfolio_return: float, portfolio_risk: float) -> float:
        """计算Sharpe Ratio"""
        if portfolio_risk == 0:
            return 0.0
        
        risk_free_rate = 0.02  # 假设无风险利率2%
        return (portfolio_return - risk_free_rate) / portfolio_risk
