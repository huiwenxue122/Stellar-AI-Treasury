"""
纯Python实现的风险指标计算
不依赖numpy和scipy，避免版本冲突
"""

import math
from typing import Dict, List, Tuple
from dataclasses import dataclass

@dataclass
class RiskMetrics:
    # Value at Risk
    var_95: float  # 95% VaR
    var_99: float  # 99% VaR
    
    # Conditional VaR (Expected Shortfall)
    cvar_95: float
    cvar_99: float
    
    # 性能指标
    sharpe_ratio: float
    sortino_ratio: float
    information_ratio: float
    
    # 回撤指标
    max_drawdown: float
    current_drawdown: float
    drawdown_duration_days: int
    
    # 波动率指标
    volatility_annual: float
    downside_volatility: float
    
    # 其他风险指标
    beta: float
    alpha: float
    
    # 风险调整收益
    calmar_ratio: float
    omega_ratio: float

class SimpleRiskAnalyzer:
    """简单风险分析器 - 纯Python实现"""
    
    def __init__(self, risk_free_rate: float = 0.04):
        self.risk_free_rate = risk_free_rate
        self.returns_history: List[float] = []
        self.portfolio_values: List[float] = []
    
    def add_return(self, daily_return: float):
        """添加每日收益率"""
        self.returns_history.append(daily_return)
        if len(self.returns_history) > 252:
            self.returns_history = self.returns_history[-252:]
    
    def add_portfolio_value(self, value: float):
        """添加投资组合价值"""
        self.portfolio_values.append(value)
        if len(self.portfolio_values) > 252:
            self.portfolio_values = self.portfolio_values[-252:]
    
    def _mean(self, data: List[float]) -> float:
        """计算平均值"""
        if not data:
            return 0.0
        return sum(data) / len(data)
    
    def _std(self, data: List[float]) -> float:
        """计算标准差"""
        if len(data) < 2:
            return 0.0
        mean = self._mean(data)
        variance = sum((x - mean) ** 2 for x in data) / (len(data) - 1)
        return math.sqrt(variance)
    
    def _percentile(self, data: List[float], percentile: float) -> float:
        """计算百分位数"""
        if not data:
            return 0.0
        sorted_data = sorted(data)
        index = int(len(sorted_data) * percentile)
        index = max(0, min(index, len(sorted_data) - 1))
        return sorted_data[index]
    
    def calculate_var(self, confidence_level: float = 0.95, 
                     time_horizon_days: int = 1) -> float:
        """计算 Value at Risk"""
        if len(self.returns_history) < 30:
            return 0.0
        
        # 历史模拟法
        var = self._percentile(self.returns_history, 1 - confidence_level)
        
        # 调整时间跨度
        var_adjusted = var * math.sqrt(time_horizon_days)
        
        return var_adjusted
    
    def calculate_cvar(self, confidence_level: float = 0.95) -> float:
        """计算 Conditional VaR"""
        if len(self.returns_history) < 30:
            return 0.0
        
        var = self.calculate_var(confidence_level)
        
        # CVaR是低于VaR的所有收益的平均值
        tail_returns = [r for r in self.returns_history if r <= var]
        
        if not tail_returns:
            return var
        
        return self._mean(tail_returns)
    
    def calculate_sharpe_ratio(self) -> float:
        """计算 Sharpe Ratio"""
        if len(self.returns_history) < 30:
            return 0.0
        
        # 年化收益率
        annual_return = self._mean(self.returns_history) * 252
        
        # 年化波动率
        annual_volatility = self._std(self.returns_history) * math.sqrt(252)
        
        if annual_volatility == 0:
            return 0.0
        
        sharpe = (annual_return - self.risk_free_rate) / annual_volatility
        
        return sharpe
    
    def calculate_sortino_ratio(self, target_return: float = 0.0) -> float:
        """计算 Sortino Ratio"""
        if len(self.returns_history) < 30:
            return 0.0
        
        # 年化收益率
        annual_return = self._mean(self.returns_history) * 252
        
        # 下行偏差
        downside_returns = [r for r in self.returns_history if r < target_return]
        
        if not downside_returns:
            return float('inf')
        
        downside_deviation = self._std(downside_returns) * math.sqrt(252)
        
        if downside_deviation == 0:
            return float('inf')
        
        sortino = (annual_return - self.risk_free_rate) / downside_deviation
        
        return sortino
    
    def calculate_max_drawdown(self) -> Tuple[float, int, float]:
        """计算最大回撤"""
        if len(self.portfolio_values) < 2:
            return 0.0, 0, 0.0
        
        values = self.portfolio_values
        
        # 计算累积最大值
        cummax = []
        current_max = values[0]
        for v in values:
            current_max = max(current_max, v)
            cummax.append(current_max)
        
        # 计算回撤
        drawdowns = [(values[i] - cummax[i]) / cummax[i] 
                     for i in range(len(values)) if cummax[i] > 0]
        
        if not drawdowns:
            return 0.0, 0, 0.0
        
        # 最大回撤
        max_dd = abs(min(drawdowns))
        
        # 当前回撤
        current_dd = abs(drawdowns[-1])
        
        # 回撤持续时间
        max_dd_idx = drawdowns.index(min(drawdowns))
        peak_idx = 0
        for i in range(max_dd_idx, -1, -1):
            if values[i] == cummax[max_dd_idx]:
                peak_idx = i
                break
        
        dd_duration = max_dd_idx - peak_idx
        
        return max_dd, dd_duration, current_dd
    
    def calculate_calmar_ratio(self) -> float:
        """计算 Calmar Ratio"""
        if len(self.returns_history) < 30:
            return 0.0
        
        annual_return = self._mean(self.returns_history) * 252
        max_dd, _, _ = self.calculate_max_drawdown()
        
        if max_dd == 0:
            return float('inf')
        
        return annual_return / max_dd
    
    def calculate_omega_ratio(self, threshold: float = 0.0) -> float:
        """计算 Omega Ratio"""
        if len(self.returns_history) < 30:
            return 1.0
        
        gains = [r - threshold for r in self.returns_history if r > threshold]
        losses = [threshold - r for r in self.returns_history if r <= threshold]
        
        if not losses:
            return float('inf')
        
        gain_sum = sum(gains) if gains else 0
        loss_sum = sum(losses)
        
        if loss_sum == 0:
            return float('inf')
        
        return gain_sum / loss_sum
    
    def calculate_information_ratio(self, benchmark_returns: List[float]) -> float:
        """计算 Information Ratio"""
        if len(self.returns_history) < 30 or len(benchmark_returns) < 30:
            return 0.0
        
        min_len = min(len(self.returns_history), len(benchmark_returns))
        portfolio_returns = self.returns_history[-min_len:]
        benchmark_returns = benchmark_returns[-min_len:]
        
        # 超额收益
        excess_returns = [portfolio_returns[i] - benchmark_returns[i] 
                         for i in range(min_len)]
        
        # 跟踪误差
        tracking_error = self._std(excess_returns) * math.sqrt(252)
        
        if tracking_error == 0:
            return 0.0
        
        # 年化超额收益
        annual_excess_return = self._mean(excess_returns) * 252
        
        return annual_excess_return / tracking_error
    
    def calculate_beta_alpha(self, market_returns: List[float]) -> Tuple[float, float]:
        """计算 Beta 和 Alpha"""
        if len(self.returns_history) < 30 or len(market_returns) < 30:
            return 1.0, 0.0
        
        min_len = min(len(self.returns_history), len(market_returns))
        portfolio_returns = self.returns_history[-min_len:]
        market_returns = market_returns[-min_len:]
        
        # 计算协方差和方差
        mean_portfolio = self._mean(portfolio_returns)
        mean_market = self._mean(market_returns)
        
        covariance = sum((portfolio_returns[i] - mean_portfolio) * 
                        (market_returns[i] - mean_market) 
                        for i in range(min_len)) / (min_len - 1)
        
        market_variance = self._std(market_returns) ** 2
        
        if market_variance == 0:
            return 1.0, 0.0
        
        # Beta
        beta = covariance / market_variance
        
        # Alpha
        portfolio_return = mean_portfolio * 252
        market_return = mean_market * 252
        alpha = portfolio_return - (self.risk_free_rate + beta * (market_return - self.risk_free_rate))
        
        return beta, alpha
    
    def get_comprehensive_metrics(self, market_returns: List[float] = None) -> RiskMetrics:
        """获取完整的风险指标"""
        # VaR
        var_95 = self.calculate_var(0.95)
        var_99 = self.calculate_var(0.99)
        
        # CVaR
        cvar_95 = self.calculate_cvar(0.95)
        cvar_99 = self.calculate_cvar(0.99)
        
        # 性能比率
        sharpe = self.calculate_sharpe_ratio()
        sortino = self.calculate_sortino_ratio()
        
        # 回撤
        max_dd, dd_duration, current_dd = self.calculate_max_drawdown()
        
        # 波动率
        volatility = self._std(self.returns_history) * math.sqrt(252) if self.returns_history else 0.0
        downside_returns = [r for r in self.returns_history if r < 0]
        downside_vol = self._std(downside_returns) * math.sqrt(252) if downside_returns else 0.0
        
        # Beta和Alpha
        if market_returns:
            beta, alpha = self.calculate_beta_alpha(market_returns)
            info_ratio = self.calculate_information_ratio(market_returns)
        else:
            beta, alpha, info_ratio = 1.0, 0.0, 0.0
        
        # 其他指标
        calmar = self.calculate_calmar_ratio()
        omega = self.calculate_omega_ratio()
        
        return RiskMetrics(
            var_95=var_95,
            var_99=var_99,
            cvar_95=cvar_95,
            cvar_99=cvar_99,
            sharpe_ratio=sharpe,
            sortino_ratio=sortino,
            information_ratio=info_ratio,
            max_drawdown=max_dd,
            current_drawdown=current_dd,
            drawdown_duration_days=dd_duration,
            volatility_annual=volatility,
            downside_volatility=downside_vol,
            beta=beta,
            alpha=alpha,
            calmar_ratio=calmar,
            omega_ratio=omega
        )
