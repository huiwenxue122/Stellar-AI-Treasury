#!/usr/bin/env python3
"""
策略中间件
实现波动率目标、止盈止损、成本滑点等通用功能
"""

import pandas as pd
import numpy as np
from typing import Tuple, Optional, Dict, Any
from dataclasses import dataclass

@dataclass
class Trade:
    """交易记录"""
    timestamp: pd.Timestamp
    price: float
    quantity: float
    side: str  # 'buy' or 'sell'
    cost: float = 0.0
    slippage: float = 0.0

def vol_target(positions: pd.Series, prices: pd.Series, 
               lookback: int = 20, target_vol: float = 0.15) -> pd.Series:
    """
    波动率目标调整
    
    Args:
        positions: 原始仓位序列
        prices: 价格序列
        lookback: 回望期
        target_vol: 目标波动率
        
    Returns:
        调整后的仓位序列
    """
    # 计算历史波动率
    returns = prices.pct_change()
    realized_vol = returns.rolling(window=lookback).std() * np.sqrt(252)
    
    # 计算调整因子
    vol_ratio = target_vol / realized_vol
    vol_ratio = vol_ratio.fillna(1.0)  # 填充NaN
    vol_ratio = vol_ratio.clip(0.1, 2.0)  # 限制调整范围
    
    # 调整仓位
    adjusted_positions = positions * vol_ratio
    
    return adjusted_positions

def apply_tp_sl(prices: pd.Series, positions: pd.Series, 
                take_profit: float = 0.02, stop_loss: float = 0.01) -> pd.Series:
    """
    应用止盈止损
    
    Args:
        prices: 价格序列
        positions: 仓位序列
        take_profit: 止盈比例
        stop_loss: 止损比例
        
    Returns:
        应用止盈止损后的仓位序列
    """
    adjusted_positions = positions.copy()
    
    # 计算价格变化
    price_changes = prices.pct_change()
    
    # 止盈逻辑
    profit_condition = (positions > 0) & (price_changes > take_profit)
    adjusted_positions[profit_condition] = 0
    
    # 止损逻辑
    loss_condition = (positions > 0) & (price_changes < -stop_loss)
    adjusted_positions[loss_condition] = 0
    
    # 空头止盈止损
    profit_condition_short = (positions < 0) & (price_changes < -take_profit)
    adjusted_positions[profit_condition_short] = 0
    
    loss_condition_short = (positions < 0) & (price_changes > stop_loss)
    adjusted_positions[loss_condition_short] = 0
    
    return adjusted_positions

def exec_costs_and_slippage(trades: pd.Series, prices: pd.Series, 
                           fee_bps: float = 5, slip_k: float = 0.1, 
                           vol: Optional[pd.Series] = None) -> Tuple[pd.Series, pd.Series]:
    """
    计算交易成本和滑点
    
    Args:
        trades: 交易信号序列
        prices: 价格序列
        fee_bps: 手续费（基点）
        slip_k: 滑点系数
        vol: 波动率序列（可选）
        
    Returns:
        (成本序列, 滑点序列)
    """
    # 计算交易量
    trade_volume = trades.abs()
    
    # 手续费成本
    fee_costs = trade_volume * (fee_bps / 10000)
    
    # 滑点成本
    if vol is not None:
        # 基于波动率的滑点
        slippage = trade_volume * vol * slip_k
    else:
        # 固定滑点
        slippage = trade_volume * slip_k * 0.001  # 0.1% 基础滑点
    
    return fee_costs, slippage

def position_sizing(positions: pd.Series, prices: pd.Series, 
                   max_position: float = 1.0, min_position: float = 0.0) -> pd.Series:
    """
    仓位大小调整
    
    Args:
        positions: 原始仓位序列
        prices: 价格序列
        max_position: 最大仓位
        min_position: 最小仓位
        
    Returns:
        调整后的仓位序列
    """
    # 限制仓位范围
    adjusted_positions = positions.clip(min_position, max_position)
    
    return adjusted_positions

def risk_budget(positions: pd.Series, prices: pd.Series, 
                risk_budget: float = 0.02, lookback: int = 20) -> pd.Series:
    """
    风险预算调整
    
    Args:
        positions: 原始仓位序列
        prices: 价格序列
        risk_budget: 风险预算
        lookback: 回望期
        
    Returns:
        调整后的仓位序列
    """
    # 计算历史波动率
    returns = prices.pct_change()
    realized_vol = returns.rolling(window=lookback).std()
    
    # 计算风险调整因子
    risk_factor = risk_budget / (realized_vol * np.sqrt(252))
    risk_factor = risk_factor.fillna(1.0)
    risk_factor = risk_factor.clip(0.1, 2.0)
    
    # 调整仓位
    adjusted_positions = positions * risk_factor
    
    return adjusted_positions

def drawdown_control(positions: pd.Series, prices: pd.Series, 
                     max_drawdown: float = 0.1, lookback: int = 20) -> pd.Series:
    """
    回撤控制
    
    Args:
        positions: 原始仓位序列
        prices: 价格序列
        max_drawdown: 最大回撤限制
        lookback: 回望期
        
    Returns:
        调整后的仓位序列
    """
    # 计算累计收益
    returns = prices.pct_change()
    cumulative_returns = (1 + returns).cumprod()
    
    # 计算回撤
    rolling_max = cumulative_returns.rolling(window=lookback).max()
    drawdown = (cumulative_returns - rolling_max) / rolling_max
    
    # 回撤控制
    adjusted_positions = positions.copy()
    high_drawdown = drawdown < -max_drawdown
    adjusted_positions[high_drawdown] = 0
    
    return adjusted_positions

def momentum_filter(positions: pd.Series, prices: pd.Series, 
                   momentum_threshold: float = 0.01, lookback: int = 10) -> pd.Series:
    """
    动量过滤
    
    Args:
        positions: 原始仓位序列
        prices: 价格序列
        momentum_threshold: 动量阈值
        lookback: 回望期
        
    Returns:
        调整后的仓位序列
    """
    # 计算动量
    momentum = prices.pct_change(periods=lookback)
    
    # 动量过滤
    adjusted_positions = positions.copy()
    
    # 只有在动量方向与仓位方向一致时才保持仓位
    long_condition = (positions > 0) & (momentum > momentum_threshold)
    short_condition = (positions < 0) & (momentum < -momentum_threshold)
    
    adjusted_positions[~(long_condition | short_condition)] = 0
    
    return adjusted_positions

def volatility_filter(positions: pd.Series, prices: pd.Series, 
                     vol_threshold: float = 0.3, lookback: int = 20) -> pd.Series:
    """
    波动率过滤
    
    Args:
        positions: 原始仓位序列
        prices: 价格序列
        vol_threshold: 波动率阈值
        lookback: 回望期
        
    Returns:
        调整后的仓位序列
    """
    # 计算波动率
    returns = prices.pct_change()
    volatility = returns.rolling(window=lookback).std() * np.sqrt(252)
    
    # 波动率过滤
    adjusted_positions = positions.copy()
    high_vol = volatility > vol_threshold
    adjusted_positions[high_vol] = 0
    
    return adjusted_positions

def apply_middleware(positions: pd.Series, prices: pd.Series, 
                    config: Dict[str, Any]) -> pd.Series:
    """
    应用所有中间件
    
    Args:
        positions: 原始仓位序列
        prices: 价格序列
        config: 中间件配置
        
    Returns:
        最终调整后的仓位序列
    """
    adjusted_positions = positions.copy()
    
    # 波动率目标
    if config.get("vol_target", {}).get("enabled", False):
        vol_config = config["vol_target"]
        adjusted_positions = vol_target(
            adjusted_positions, prices,
            lookback=vol_config.get("lookback", 20),
            target_vol=vol_config.get("target_vol", 0.15)
        )
    
    # 止盈止损
    if config.get("tp_sl", {}).get("enabled", False):
        tp_sl_config = config["tp_sl"]
        adjusted_positions = apply_tp_sl(
            prices, adjusted_positions,
            take_profit=tp_sl_config.get("take_profit", 0.02),
            stop_loss=tp_sl_config.get("stop_loss", 0.01)
        )
    
    # 仓位大小调整
    if config.get("position_sizing", {}).get("enabled", False):
        sizing_config = config["position_sizing"]
        adjusted_positions = position_sizing(
            adjusted_positions, prices,
            max_position=sizing_config.get("max_position", 1.0),
            min_position=sizing_config.get("min_position", 0.0)
        )
    
    # 风险预算
    if config.get("risk_budget", {}).get("enabled", False):
        risk_config = config["risk_budget"]
        adjusted_positions = risk_budget(
            adjusted_positions, prices,
            risk_budget=risk_config.get("risk_budget", 0.02),
            lookback=risk_config.get("lookback", 20)
        )
    
    # 回撤控制
    if config.get("drawdown_control", {}).get("enabled", False):
        dd_config = config["drawdown_control"]
        adjusted_positions = drawdown_control(
            adjusted_positions, prices,
            max_drawdown=dd_config.get("max_drawdown", 0.1),
            lookback=dd_config.get("lookback", 20)
        )
    
    # 动量过滤
    if config.get("momentum_filter", {}).get("enabled", False):
        mom_config = config["momentum_filter"]
        adjusted_positions = momentum_filter(
            adjusted_positions, prices,
            momentum_threshold=mom_config.get("momentum_threshold", 0.01),
            lookback=mom_config.get("lookback", 10)
        )
    
    # 波动率过滤
    if config.get("volatility_filter", {}).get("enabled", False):
        vol_config = config["volatility_filter"]
        adjusted_positions = volatility_filter(
            adjusted_positions, prices,
            vol_threshold=vol_config.get("vol_threshold", 0.3),
            lookback=vol_config.get("lookback", 20)
        )
    
    return adjusted_positions

def calculate_trade_costs(positions: pd.Series, prices: pd.Series, 
                         config: Dict[str, Any]) -> Tuple[pd.Series, pd.Series, pd.Series]:
    """
    计算交易成本
    
    Args:
        positions: 仓位序列
        prices: 价格序列
        config: 成本配置
        
    Returns:
        (手续费, 滑点, 总成本)
    """
    # 计算交易信号
    trades = positions.diff().fillna(0)
    
    # 计算波动率（用于滑点计算）
    returns = prices.pct_change()
    volatility = returns.rolling(window=20).std()
    
    # 计算成本和滑点
    fee_costs, slippage = exec_costs_and_slippage(
        trades, prices,
        fee_bps=config.get("fee_bps", 5),
        slip_k=config.get("slip_k", 0.1),
        vol=volatility
    )
    
    # 总成本
    total_costs = fee_costs + slippage
    
    return fee_costs, slippage, total_costs
