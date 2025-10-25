"""
市场数据获取模块
从多个真实数据源获取价格和市场数据
"""

import aiohttp
import asyncio
from typing import Dict, List, Optional
from dataclasses import dataclass
import time

@dataclass
class MarketData:
    symbol: str
    price: float
    volume_24h: float
    change_24h: float
    timestamp: float
    source: str

class MarketDataProvider:
    """市场数据提供者 - 整合多个数据源"""
    
    def __init__(self, config: dict):
        self.config = config
        self.cache = {}
        self.cache_ttl = 60  # 缓存60秒
        
    async def get_crypto_price(self, symbol: str) -> Optional[MarketData]:
        """
        获取加密货币价格
        优先级: Stellar DEX > CoinGecko
        """
        # 检查缓存
        cache_key = f"crypto_{symbol}"
        if cache_key in self.cache:
            cached_data = self.cache[cache_key]
            if time.time() - cached_data.timestamp < self.cache_ttl:
                return cached_data
        
        # 尝试从Stellar DEX获取
        stellar_price = await self._get_stellar_dex_price(symbol)
        if stellar_price:
            self.cache[cache_key] = stellar_price
            return stellar_price
        
        # 备选：从CoinGecko获取
        coingecko_price = await self._get_coingecko_price(symbol)
        if coingecko_price:
            self.cache[cache_key] = coingecko_price
            return coingecko_price
        
        return None
    
    async def _get_stellar_dex_price(self, symbol: str) -> Optional[MarketData]:
        """
        从Stellar DEX获取价格
        通过order book计算中间价
        """
        try:
            # Stellar Horizon API
            horizon_url = self.config['network']['horizon']
            
            # 资产映射到Stellar DEX交易对
            asset_mapping = {
                'XLM': ('native', None),
                'BTC': ('BTC', 'GAUTUYY2THLF7SGITDFMXJVYH3LHDSMGEAKSBU267M2K7A3W543CKUEF'),
                'ETH': ('ETH', 'GBDEVU63Y6NTHJQQZIKVTC23NWLQVP3WJ2RI2OTSJTNYOIGICST6DUXR'),
                'USDC': ('USDC', 'GBBD47IF6I2X6ZJMPRC7JIBMQJSQADPDA3BZX4A5QW4NRS6R6ZQBTNAE')
            }
            
            if symbol not in asset_mapping:
                return None
            
            selling_asset_code, selling_asset_issuer = asset_mapping.get(symbol, (None, None))
            buying_asset_code, buying_asset_issuer = asset_mapping.get('USDC', (None, None))
            
            if not selling_asset_code:
                return None
            
            # 构建order book查询URL
            if selling_asset_issuer:
                selling = f"selling_asset_type=credit_alphanum4&selling_asset_code={selling_asset_code}&selling_asset_issuer={selling_asset_issuer}"
            else:
                selling = "selling_asset_type=native"
            
            buying = f"buying_asset_type=credit_alphanum4&buying_asset_code={buying_asset_code}&buying_asset_issuer={buying_asset_issuer}"
            
            url = f"{horizon_url}/order_book?{selling}&{buying}&limit=5"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # 从order book计算价格
                        bids = data.get('bids', [])
                        asks = data.get('asks', [])
                        
                        if bids and asks:
                            best_bid = float(bids[0]['price'])
                            best_ask = float(asks[0]['price'])
                            mid_price = (best_bid + best_ask) / 2
                            
                            # 计算24小时交易量（近似）
                            volume = sum(float(bid.get('amount', 0)) for bid in bids[:5])
                            
                            return MarketData(
                                symbol=symbol,
                                price=mid_price,
                                volume_24h=volume,
                                change_24h=0.0,  # Stellar DEX不提供24h变化
                                timestamp=time.time(),
                                source='stellar_dex'
                            )
        except Exception as e:
            print(f"Stellar DEX error for {symbol}: {e}")
            return None
    
    async def _get_coingecko_price(self, symbol: str) -> Optional[MarketData]:
        """
        从CoinGecko获取加密货币价格
        免费API，无需key
        """
        try:
            # CoinGecko ID映射
            coingecko_ids = {
                'BTC': 'bitcoin',
                'ETH': 'ethereum',
                'XLM': 'stellar',
                'USDC': 'usd-coin',
                'USDT': 'tether'
            }
            
            coin_id = coingecko_ids.get(symbol)
            if not coin_id:
                return None
            
            url = f"https://api.coingecko.com/api/v3/simple/price"
            params = {
                'ids': coin_id,
                'vs_currencies': 'usd',
                'include_24hr_vol': 'true',
                'include_24hr_change': 'true'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if coin_id in data:
                            coin_data = data[coin_id]
                            
                            return MarketData(
                                symbol=symbol,
                                price=coin_data.get('usd', 0.0),
                                volume_24h=coin_data.get('usd_24h_vol', 0.0),
                                change_24h=coin_data.get('usd_24h_change', 0.0),
                                timestamp=time.time(),
                                source='coingecko'
                            )
        except Exception as e:
            print(f"CoinGecko error for {symbol}: {e}")
            return None
    
    async def get_rwa_price(self, symbol: str, asset_type: str) -> Optional[MarketData]:
        """
        获取RWA资产价格
        使用Yahoo Finance API
        """
        cache_key = f"rwa_{symbol}"
        if cache_key in self.cache:
            cached_data = self.cache[cache_key]
            if time.time() - cached_data.timestamp < self.cache_ttl:
                return cached_data
        
        # 尝试获取价格
        price_data = await self._get_yfinance_price(symbol, asset_type)
        
        if price_data:
            self.cache[cache_key] = price_data
            return price_data
        
        return None
    
    async def _get_yfinance_price(self, symbol: str, asset_type: str) -> Optional[MarketData]:
        """
        从Yahoo Finance获取RWA价格
        使用免费的Yahoo Finance API
        """
        try:
            # 映射到Yahoo Finance ticker
            ticker_mapping = {
                'BOND': 'TLT',      # iShares 20+ Year Treasury Bond ETF
                'GOLD': 'GLD',      # SPDR Gold Shares
                'REIT': 'VNQ'       # Vanguard Real Estate ETF
            }
            
            ticker = ticker_mapping.get(symbol)
            if not ticker:
                return None
            
            # 使用Yahoo Finance的免费API
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
            params = {
                'interval': '1d',
                'range': '1d'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        chart = data.get('chart', {})
                        result = chart.get('result', [{}])[0]
                        
                        if result:
                            meta = result.get('meta', {})
                            quote = result.get('indicators', {}).get('quote', [{}])[0]
                            
                            # 当前价格
                            current_price = meta.get('regularMarketPrice', 0.0)
                            
                            # 前一日收盘价
                            previous_close = meta.get('previousClose', current_price)
                            
                            # 计算24小时变化
                            change_24h = ((current_price - previous_close) / previous_close * 100) if previous_close > 0 else 0.0
                            
                            # 交易量
                            volume = quote.get('volume', [0])[0] if quote.get('volume') else 0
                            
                            return MarketData(
                                symbol=symbol,
                                price=current_price,
                                volume_24h=volume,
                                change_24h=change_24h,
                                timestamp=time.time(),
                                source='yahoo_finance'
                            )
        except Exception as e:
            print(f"Yahoo Finance error for {symbol}: {e}")
            return None
    
    async def get_all_prices(self, assets: Dict[str, dict]) -> Dict[str, MarketData]:
        """
        批量获取所有资产价格
        """
        results = {}
        tasks = []
        
        for asset_name, asset_config in assets.items():
            asset_type = asset_config.get('type', 'unknown')
            symbol = asset_config['code']
            
            if asset_type in ['crypto', 'native', 'stablecoin']:
                tasks.append((asset_name, self.get_crypto_price(symbol)))
            elif asset_type in ['rwa_bond', 'rwa_commodity', 'rwa_real_estate']:
                tasks.append((asset_name, self.get_rwa_price(symbol, asset_type)))
        
        # 并发获取所有价格
        for asset_name, task in tasks:
            try:
                result = await task
                if result:
                    results[asset_name] = result
            except Exception as e:
                print(f"Error getting price for {asset_name}: {e}")
        
        return results
    
    async def get_historical_data(self, symbol: str, days: int = 30) -> List[Dict]:
        """
        获取历史数据
        """
        try:
            # 对于crypto，使用CoinGecko
            coingecko_ids = {
                'BTC': 'bitcoin',
                'ETH': 'ethereum',
                'XLM': 'stellar',
                'USDC': 'usd-coin'
            }
            
            coin_id = coingecko_ids.get(symbol)
            if coin_id:
                url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
                params = {
                    'vs_currency': 'usd',
                    'days': str(days)
                }
                
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as response:
                        if response.status == 200:
                            data = await response.json()
                            prices = data.get('prices', [])
                            
                            return [
                                {
                                    'timestamp': price[0] / 1000,
                                    'price': price[1],
                                    'volume': 0
                                }
                                for price in prices
                            ]
            
            # 对于RWA，使用Yahoo Finance
            ticker_mapping = {
                'BOND': 'TLT',
                'GOLD': 'GLD',
                'REIT': 'VNQ'
            }
            
            ticker = ticker_mapping.get(symbol)
            if ticker:
                # Yahoo Finance历史数据需要更复杂的处理
                # 这里返回空列表，可以后续扩展
                return []
            
        except Exception as e:
            print(f"Error getting historical data for {symbol}: {e}")
        
        return []
