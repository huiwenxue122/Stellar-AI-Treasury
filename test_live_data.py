#!/usr/bin/env python3
"""
测试真实市场数据连接
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_crypto_prices():
    """测试加密货币价格（CoinGecko）"""
    print("💰 测试加密货币价格（CoinGecko API）")
    print("=" * 60)
    
    from stellar.market_data import MarketDataProvider
    import yaml
    
    with open('app/config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    provider = MarketDataProvider(config)
    
    crypto_assets = ['BTC', 'ETH', 'XLM', 'USDC']
    
    for symbol in crypto_assets:
        try:
            data = await provider.get_crypto_price(symbol)
            if data:
                print(f"\n   {symbol}:")
                print(f"      价格:     ${data.price:,.2f}")
                print(f"      24h量:    ${data.volume_24h:,.0f}")
                print(f"      24h变化:  {data.change_24h:+.2f}%")
                print(f"      数据源:   {data.source}")
            else:
                print(f"\n   {symbol}: ❌ 无法获取价格")
        except Exception as e:
            print(f"\n   {symbol}: ❌ 错误 - {e}")
    
    return True

async def test_rwa_prices():
    """测试RWA价格（Yahoo Finance）"""
    print("\n🏢 测试RWA资产价格（Yahoo Finance API）")
    print("=" * 60)
    
    from stellar.market_data import MarketDataProvider
    import yaml
    
    with open('app/config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    provider = MarketDataProvider(config)
    
    rwa_assets = {
        'BOND': 'rwa_bond',
        'GOLD': 'rwa_commodity', 
        'REIT': 'rwa_real_estate'
    }
    
    for symbol, asset_type in rwa_assets.items():
        try:
            data = await provider.get_rwa_price(symbol, asset_type)
            if data:
                print(f"\n   {symbol}:")
                print(f"      价格:     ${data.price:,.2f}")
                print(f"      24h变化:  {data.change_24h:+.2f}%")
                print(f"      数据源:   {data.source}")
            else:
                print(f"\n   {symbol}: ❌ 无法获取价格")
        except Exception as e:
            print(f"\n   {symbol}: ❌ 错误 - {e}")
    
    return True

async def test_price_oracle():
    """测试价格预言机整合"""
    print("\n🔮 测试价格预言机（整合所有数据源）")
    print("=" * 60)
    
    from stellar.horizon import Horizon
    from stellar.price_oracle import PriceOracle
    import yaml
    
    with open('app/config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    # 启用实时数据
    config['market_data']['use_live_data'] = True
    
    horizon = Horizon(config['network']['horizon'])
    oracle = PriceOracle(horizon, config)
    
    print(f"\n   实时数据: {'✅ 启用' if oracle.use_live_data else '❌ 禁用'}")
    print("\n   获取所有资产价格...\n")
    
    asset_categories = {
        '🪙 Stablecoins': ['USDC', 'USDT'],
        '💰 Crypto': ['XLM', 'BTC', 'ETH'],
        '🏢 RWA': ['BOND', 'GOLD', 'REIT']
    }
    
    for category, assets in asset_categories.items():
        print(f"\n   {category}:")
        for asset_code in assets:
            try:
                price = await oracle.get_price(asset_code, 'USDC')
                
                # 检查缓存信息
                cache_key = f"{asset_code}_USDC"
                if cache_key in oracle.price_cache:
                    cached = oracle.price_cache[cache_key]
                    source = cached.source
                    confidence = cached.confidence
                else:
                    source = 'unknown'
                    confidence = 0.0
                
                print(f"      {asset_code:>6}: ${price:>12,.2f}  [{source:>15}] ({confidence:.0%})")
            except Exception as e:
                print(f"      {asset_code:>6}: ❌ {e}")
    
    return True

async def test_data_sources():
    """测试各个数据源的可用性"""
    print("\n🔍 测试数据源可用性")
    print("=" * 60)
    
    import aiohttp
    
    sources = {
        'CoinGecko API': 'https://api.coingecko.com/api/v3/ping',
        'Yahoo Finance': 'https://query1.finance.yahoo.com/v8/finance/chart/AAPL?interval=1d&range=1d'
    }
    
    for name, url in sources.items():
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                    if response.status == 200:
                        print(f"   ✅ {name}: 可用")
                    else:
                        print(f"   ⚠️  {name}: 返回 {response.status}")
        except Exception as e:
            print(f"   ❌ {name}: {e}")
    
    return True

async def main():
    """主测试函数"""
    print("🚀 测试真实市场数据连接")
    print("=" * 60)
    print("\n📡 数据源:")
    print("   • Stellar DEX (testnet)")
    print("   • CoinGecko API (免费)")
    print("   • Yahoo Finance API (免费)")
    print()
    
    try:
        # 测试数据源可用性
        await test_data_sources()
        
        # 测试加密货币价格
        await test_crypto_prices()
        
        # 测试RWA价格
        await test_rwa_prices()
        
        # 测试价格预言机
        await test_price_oracle()
        
        print("\n" + "=" * 60)
        print("🎉 数据连接测试完成！")
        print("\n✅ 已实现:")
        print("   • Crypto价格 - CoinGecko实时数据")
        print("   • RWA价格 - Yahoo Finance实时数据")
        print("   • Stellar DEX - testnet交易对")
        print("   • 自动降级到mock数据（备选）")
        print("\n💡 配置:")
        print("   在 config.yaml 中设置 market_data.use_live_data")
        print("   • true  = 使用真实在线数据")
        print("   • false = 使用mock数据（测试用）")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
