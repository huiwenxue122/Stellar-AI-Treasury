"""
价格预言机 - 支持多种资产类型的价格获取
整合真实数据源：Stellar DEX, CoinGecko, Yahoo Finance
"""

import asyncio
from typing import Dict, Optional
from dataclasses import dataclass
import time
from stellar.market_data import MarketDataProvider

@dataclass
class PriceData:
    asset: str
    price_usd: float
    timestamp: float
    source: str
    confidence: float

class PriceOracle:
    def __init__(self, horizon, config):
        self.horizon = horizon
        self.config = config
        self.price_cache: Dict[str, PriceData] = {}
        self.cache_ttl = 60  # 缓存60秒
        
        # 初始化市场数据提供者
        self.market_data_provider = MarketDataProvider(config)
        
        # 使用真实数据源
        self.use_live_data = config.get('market_data', {}).get('use_live_data', True)
        
        # Mock prices 作为备选（当真实数据源不可用时）
        self.mock_prices = {
            'XLM': 0.12,    # Stellar Lumens
            'BTC': 43000.0, # Bitcoin
            'ETH': 2300.0,  # Ethereum
            'USDC': 1.0,    # USD Coin
            'USDT': 1.0,    # Tether
            'BOND': 98.5,   # US Treasury Bond ETF (TLT)
            'GOLD': 195.0,  # Gold ETF (GLD)
            'REIT': 85.0,   # Real Estate ETF (VNQ)
        }
    
    async def get_price(self, asset_code: str, base_currency: str = 'USDC') -> float:
        """获取资产价格（以base_currency计价）"""
        
        # 检查缓存
        cache_key = f"{asset_code}_{base_currency}"
        if cache_key in self.price_cache:
            cached = self.price_cache[cache_key]
            if time.time() - cached.timestamp < self.cache_ttl:
                return cached.price_usd
        
        # USDC价格总是1.0（基准货币）
        if asset_code == 'USDC':
            return 1.0
        
        # 如果启用实时数据，尝试从真实数据源获取
        if self.use_live_data:
            try:
                # 获取资产配置
                asset_config = None
                for name, cfg in self.config.get('assets', {}).items():
                    if cfg.get('code') == asset_code:
                        asset_config = cfg
                        break
                
                if asset_config:
                    asset_type = asset_config.get('type', 'unknown')
                    
                    # 根据资产类型选择数据源
                    if asset_type in ['crypto', 'native', 'stablecoin']:
                        # 加密货币：Stellar DEX > CoinGecko
                        market_data = await self.market_data_provider.get_crypto_price(asset_code)
                    elif asset_type in ['rwa_bond', 'rwa_commodity', 'rwa_real_estate']:
                        # RWA：Yahoo Finance
                        market_data = await self.market_data_provider.get_rwa_price(asset_code, asset_type)
                    else:
                        market_data = None
                    
                    if market_data and market_data.price > 0:
                        # 缓存真实价格
                        self.price_cache[cache_key] = PriceData(
                            asset=asset_code,
                            price_usd=market_data.price,
                            timestamp=market_data.timestamp,
                            source=market_data.source,
                            confidence=0.9 if market_data.source in ['stellar_dex', 'coingecko', 'yahoo_finance'] else 0.7
                        )
                        return market_data.price
            
            except Exception as e:
                print(f"Live data error for {asset_code}: {e}")
        
        # 备选：使用mock价格
        if asset_code in self.mock_prices:
            price = self.mock_prices[asset_code]
            
            self.price_cache[cache_key] = PriceData(
                asset=asset_code,
                price_usd=price,
                timestamp=time.time(),
                source='mock_fallback',
                confidence=0.5
            )
            
            return price
        
        # 如果没有价格数据，返回0
        return 0.0
    
    async def _get_dex_price(self, asset_code: str, base_currency: str) -> float:
        """从Stellar DEX获取价格"""
        try:
            # 这里应该查询Stellar DEX的order book
            # 由于testnet上可能没有真实交易对，我们使用mock数据
            return 0.0
        except Exception as e:
            return 0.0
    
    async def get_multiple_prices(self, asset_codes: list) -> Dict[str, float]:
        """批量获取多个资产价格"""
        prices = {}
        for asset_code in asset_codes:
            prices[asset_code] = await self.get_price(asset_code)
        return prices
    
    def update_mock_price(self, asset_code: str, price: float):
        """更新mock价格（用于测试）"""
        self.mock_prices[asset_code] = price
        # 清除缓存
        keys_to_remove = [k for k in self.price_cache.keys() if k.startswith(asset_code)]
        for key in keys_to_remove:
            del self.price_cache[key]
    
    def get_price_history(self, asset_code: str, days: int = 30) -> list:
        """获取历史价格（模拟数据）"""
        import random
        
        if asset_code not in self.mock_prices:
            return []
        
        base_price = self.mock_prices[asset_code]
        history = []
        
        for i in range(days):
            # 模拟价格波动
            volatility = 0.02 if asset_code in ['USDC', 'USDT'] else 0.05
            price_change = random.gauss(0, volatility)
            price = base_price * (1 + price_change)
            
            history.append({
                'date': time.time() - (days - i) * 86400,
                'price': price,
                'volume': random.uniform(1000, 100000)
            })
        
        return history
