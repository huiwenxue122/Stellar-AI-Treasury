"""
多资产交易策略
支持crypto、RWA、stablecoins，USDC作为计价和结算货币
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from enum import Enum
import time

class AssetType(Enum):
    STABLECOIN = "stablecoin"
    CRYPTO = "crypto"
    RWA_BOND = "rwa_bond"
    RWA_COMMODITY = "rwa_commodity"
    RWA_REAL_ESTATE = "rwa_real_estate"
    NATIVE = "native"

class TradeAction(Enum):
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"
    REBALANCE = "rebalance"

@dataclass
class AssetAllocation:
    """资产配置"""
    asset_name: str
    asset_type: AssetType
    current_value_usdc: float
    current_weight: float
    target_weight: float
    recommended_action: TradeAction
    trade_amount_usdc: float

@dataclass
class TradeSignal:
    """交易信号"""
    asset: str
    action: TradeAction
    amount_usdc: float
    price: float
    reason: str
    confidence: float
    expected_return: float

class MultiAssetStrategy:
    """多资产交易策略"""
    
    def __init__(self, config: dict, asset_manager, price_oracle):
        self.config = config
        self.asset_manager = asset_manager
        self.price_oracle = price_oracle
        
        # 交易配置
        self.ma_config = config.get('multi_asset_trading', {})
        self.base_currency = self.ma_config.get('base_currency', 'usdc')
        
        # 权重限制
        self.max_single_weight = self.ma_config.get('max_single_asset_weight', 0.30)
        self.min_stable = self.ma_config.get('min_stable_allocation', 0.20)
        self.max_crypto = self.ma_config.get('max_crypto_allocation', 0.50)
        self.max_rwa = self.ma_config.get('max_rwa_allocation', 0.60)
        
        # 交易限制
        self.max_trade_size = self.ma_config.get('max_trade_size_usd', 1000)
        self.min_trade_size = self.ma_config.get('min_trade_size_usd', 10)
        
        # 再平衡参数
        self.rebalance_threshold = self.ma_config.get('rebalance_threshold', 0.05)
        
        # 上次再平衡时间
        self.last_rebalance_time = 0
    
    def get_asset_type(self, asset_name: str) -> AssetType:
        """获取资产类型"""
        asset_config = self.config['assets'].get(asset_name, {})
        asset_type_str = asset_config.get('type', 'native')
        
        type_mapping = {
            'stablecoin': AssetType.STABLECOIN,
            'crypto': AssetType.CRYPTO,
            'native': AssetType.NATIVE,
            'rwa_bond': AssetType.RWA_BOND,
            'rwa_commodity': AssetType.RWA_COMMODITY,
            'rwa_real_estate': AssetType.RWA_REAL_ESTATE
        }
        
        return type_mapping.get(asset_type_str, AssetType.NATIVE)
    
    async def calculate_portfolio_allocation(self, account_address: str) -> Dict[str, AssetAllocation]:
        """计算投资组合配置"""
        allocations = {}
        total_value = 0.0
        
        # 获取所有资产余额和价格
        for asset_name, asset_config in self.config['assets'].items():
            balance = await self.asset_manager.get_current_balance(account_address, asset_name)
            price = await self.price_oracle.get_price(asset_config['code'], self.base_currency)
            
            value_usdc = balance * price
            total_value += value_usdc
        
        # 计算权重
        for asset_name, asset_config in self.config['assets'].items():
            balance = await self.asset_manager.get_current_balance(account_address, asset_name)
            price = await self.price_oracle.get_price(asset_config['code'], self.base_currency)
            value_usdc = balance * price
            
            current_weight = value_usdc / total_value if total_value > 0 else 0
            
            allocations[asset_name] = AssetAllocation(
                asset_name=asset_name,
                asset_type=self.get_asset_type(asset_name),
                current_value_usdc=value_usdc,
                current_weight=current_weight,
                target_weight=0.0,  # 将在优化中计算
                recommended_action=TradeAction.HOLD,
                trade_amount_usdc=0.0
            )
        
        return allocations, total_value
    
    def calculate_target_allocation(self, allocations: Dict[str, AssetAllocation],
                                   market_conditions: Dict[str, float]) -> Dict[str, float]:
        """
        计算目标配置
        基于市场条件、风险偏好和资产类型
        """
        target_weights = {}
        
        # 获取资产分类
        stablecoins = []
        cryptos = []
        rwas = []
        
        for asset_name, alloc in allocations.items():
            if alloc.asset_type == AssetType.STABLECOIN:
                stablecoins.append(asset_name)
            elif alloc.asset_type in [AssetType.CRYPTO, AssetType.NATIVE]:
                cryptos.append(asset_name)
            else:
                rwas.append(asset_name)
        
        # 根据市场条件调整配置
        market_volatility = market_conditions.get('volatility', 0.2)
        risk_level = market_conditions.get('risk_level', 'MEDIUM')
        
        # 基础配置
        if risk_level == 'HIGH' or market_volatility > 0.4:
            # 高风险：增加稳定币，减少波动资产
            stable_target = 0.40
            crypto_target = 0.30
            rwa_target = 0.30
        elif risk_level == 'LOW' and market_volatility < 0.15:
            # 低风险：可以增加增长型资产
            stable_target = 0.20
            crypto_target = 0.45
            rwa_target = 0.35
        else:
            # 中等风险：平衡配置
            stable_target = 0.30
            crypto_target = 0.40
            rwa_target = 0.30
        
        # 分配稳定币权重
        if stablecoins:
            for asset in stablecoins:
                target_weights[asset] = stable_target / len(stablecoins)
        
        # 分配加密货币权重
        if cryptos:
            # 根据历史表现调整
            for asset in cryptos:
                base_weight = crypto_target / len(cryptos)
                # BTC/ETH可能有更高权重
                if asset in ['btc', 'eth']:
                    base_weight *= 1.2
                target_weights[asset] = min(base_weight, self.max_single_weight)
        
        # 分配RWA权重
        if rwas:
            for asset in rwas:
                target_weights[asset] = rwa_target / len(rwas)
        
        # 归一化权重
        total_weight = sum(target_weights.values())
        if total_weight > 0:
            target_weights = {k: v/total_weight for k, v in target_weights.items()}
        
        return target_weights
    
    async def generate_rebalance_signals(self, account_address: str,
                                        market_conditions: Dict[str, float]) -> List[TradeSignal]:
        """生成再平衡信号"""
        signals = []
        
        # 检查再平衡时间间隔
        rebalance_interval = self.ma_config.get('rebalance_interval_hours', 24) * 3600
        if time.time() - self.last_rebalance_time < rebalance_interval:
            return signals
        
        # 计算当前配置
        allocations, total_value = await self.calculate_portfolio_allocation(account_address)
        
        if total_value < self.min_trade_size:
            return signals
        
        # 计算目标配置
        target_weights = self.calculate_target_allocation(allocations, market_conditions)
        
        # 生成交易信号
        for asset_name, alloc in allocations.items():
            target_weight = target_weights.get(asset_name, 0.0)
            weight_diff = target_weight - alloc.current_weight
            
            # 检查是否需要再平衡
            if abs(weight_diff) > self.rebalance_threshold:
                trade_amount = abs(weight_diff * total_value)
                
                # 限制交易大小
                trade_amount = min(trade_amount, self.max_trade_size)
                
                if trade_amount >= self.min_trade_size:
                    action = TradeAction.BUY if weight_diff > 0 else TradeAction.SELL
                    
                    # 获取价格
                    asset_config = self.config['assets'][asset_name]
                    price = await self.price_oracle.get_price(asset_config['code'], self.base_currency)
                    
                    signal = TradeSignal(
                        asset=asset_name,
                        action=action,
                        amount_usdc=trade_amount,
                        price=price,
                        reason=f"Rebalance: {alloc.current_weight:.1%} -> {target_weight:.1%}",
                        confidence=0.8,
                        expected_return=0.0  # 再平衡不追求收益
                    )
                    signals.append(signal)
        
        if signals:
            self.last_rebalance_time = time.time()
        
        return signals
    
    async def generate_momentum_signals(self, market_data: Dict[str, List[float]]) -> List[TradeSignal]:
        """
        生成动量交易信号
        针对crypto和RWA资产
        """
        signals = []
        
        for asset_name, prices in market_data.items():
            if len(prices) < 20:
                continue
            
            asset_type = self.get_asset_type(asset_name)
            
            # 跳过稳定币
            if asset_type == AssetType.STABLECOIN:
                continue
            
            # 计算动量指标
            recent_return = (prices[-1] - prices[-10]) / prices[-10]
            volatility = self._calculate_volatility(prices)
            
            # 获取当前价格
            current_price = prices[-1]
            
            # 生成信号
            if asset_type in [AssetType.CRYPTO, AssetType.NATIVE]:
                # Crypto: 追求高增长
                if recent_return > 0.05 and volatility < 0.3:
                    # 上涨趋势，波动率可控
                    signal = TradeSignal(
                        asset=asset_name,
                        action=TradeAction.BUY,
                        amount_usdc=self.max_trade_size * 0.5,
                        price=current_price,
                        reason=f"Crypto momentum: {recent_return:.1%} return",
                        confidence=0.7,
                        expected_return=recent_return * 0.5
                    )
                    signals.append(signal)
                elif recent_return < -0.10:
                    # 下跌趋势，减仓
                    signal = TradeSignal(
                        asset=asset_name,
                        action=TradeAction.SELL,
                        amount_usdc=self.max_trade_size * 0.3,
                        price=current_price,
                        reason=f"Crypto risk: {recent_return:.1%} drop",
                        confidence=0.8,
                        expected_return=0.0
                    )
                    signals.append(signal)
            
            elif asset_type in [AssetType.RWA_BOND, AssetType.RWA_COMMODITY, AssetType.RWA_REAL_ESTATE]:
                # RWA: 追求稳定收益
                if recent_return > 0.02 and volatility < 0.15:
                    # 稳定增长
                    signal = TradeSignal(
                        asset=asset_name,
                        action=TradeAction.BUY,
                        amount_usdc=self.max_trade_size * 0.6,
                        price=current_price,
                        reason=f"RWA stable growth: {recent_return:.1%}",
                        confidence=0.85,
                        expected_return=0.04  # RWA期望年化4%
                    )
                    signals.append(signal)
        
        return signals
    
    def _calculate_volatility(self, prices: List[float]) -> float:
        """计算波动率"""
        if len(prices) < 2:
            return 0.0
        
        returns = [(prices[i] - prices[i-1]) / prices[i-1] for i in range(1, len(prices))]
        
        # 计算标准差
        mean_return = sum(returns) / len(returns)
        variance = sum((r - mean_return) ** 2 for r in returns) / len(returns)
        
        import math
        return math.sqrt(variance) * math.sqrt(252)  # 年化
    
    def check_allocation_limits(self, allocations: Dict[str, AssetAllocation]) -> List[str]:
        """检查配置限制"""
        warnings = []
        
        # 计算各类资产总权重
        stable_weight = sum(a.current_weight for a in allocations.values() 
                           if a.asset_type == AssetType.STABLECOIN)
        crypto_weight = sum(a.current_weight for a in allocations.values() 
                          if a.asset_type in [AssetType.CRYPTO, AssetType.NATIVE])
        rwa_weight = sum(a.current_weight for a in allocations.values() 
                        if 'RWA' in a.asset_type.value.upper())
        
        # 检查限制
        if stable_weight < self.min_stable:
            warnings.append(f"Stablecoin allocation too low: {stable_weight:.1%} < {self.min_stable:.1%}")
        
        if crypto_weight > self.max_crypto:
            warnings.append(f"Crypto allocation too high: {crypto_weight:.1%} > {self.max_crypto:.1%}")
        
        if rwa_weight > self.max_rwa:
            warnings.append(f"RWA allocation too high: {rwa_weight:.1%} > {self.max_rwa:.1%}")
        
        # 检查单个资产
        for asset_name, alloc in allocations.items():
            if alloc.current_weight > self.max_single_weight:
                warnings.append(f"{asset_name} weight too high: {alloc.current_weight:.1%} > {self.max_single_weight:.1%}")
        
        return warnings
