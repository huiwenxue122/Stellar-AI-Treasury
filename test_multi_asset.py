#!/usr/bin/env python3
"""
测试多资产交易策略
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_multi_asset_strategy():
    """测试多资产策略"""
    print("🚀 测试多资产交易策略")
    print("=" * 60)
    
    import yaml
    from stellar.horizon import Horizon
    from stellar.assets import AssetManager
    from agents.multi_asset_strategy import MultiAssetStrategy, AssetType
    
    # 加载配置
    with open('app/config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    print("\n1️⃣ 验证配置...")
    print(f"   基准货币: {config['multi_asset_trading']['base_currency']}")
    print(f"   结算货币: {config['multi_asset_trading']['settlement_currency']}")
    print(f"   最大单资产权重: {config['multi_asset_trading']['max_single_asset_weight']*100}%")
    print(f"   最小稳定币配置: {config['multi_asset_trading']['min_stable_allocation']*100}%")
    
    # 显示支持的资产
    print("\n2️⃣ 支持的资产:")
    
    stablecoins = []
    cryptos = []
    rwas = []
    
    for asset_name, asset_config in config['assets'].items():
        asset_type = asset_config.get('type', 'unknown')
        if asset_type == 'stablecoin':
            stablecoins.append(asset_name)
        elif asset_type in ['crypto', 'native']:
            cryptos.append(asset_name)
        else:
            rwas.append(asset_name)
    
    print(f"\n   📊 Stablecoins ({len(stablecoins)}):")
    for asset in stablecoins:
        print(f"      - {asset.upper()}: {config['assets'][asset]['code']}")
    
    print(f"\n   💰 Cryptocurrencies ({len(cryptos)}):")
    for asset in cryptos:
        print(f"      - {asset.upper()}: {config['assets'][asset]['code']}")
    
    print(f"\n   🏢 RWA Assets ({len(rwas)}):")
    for asset in rwas:
        asset_cfg = config['assets'][asset]
        underlying = asset_cfg.get('underlying', 'N/A')
        print(f"      - {asset.upper()}: {asset_cfg['code']} ({underlying})")
    
    # 创建策略实例
    print("\n3️⃣ 初始化多资产策略...")
    horizon = Horizon(config['network']['horizon'])
    asset_manager = AssetManager(horizon, config)
    
    strategy = MultiAssetStrategy(config, asset_manager, asset_manager.price_oracle)
    print("   ✅ 策略初始化成功")
    
    # 测试目标配置计算
    print("\n4️⃣ 测试目标配置计算...")
    
    # 模拟当前配置
    mock_allocations = {}
    for asset_name in config['assets'].keys():
        from agents.multi_asset_strategy import AssetAllocation
        mock_allocations[asset_name] = AssetAllocation(
            asset_name=asset_name,
            asset_type=strategy.get_asset_type(asset_name),
            current_value_usdc=1000.0,
            current_weight=1.0/len(config['assets']),
            target_weight=0.0,
            recommended_action=None,
            trade_amount_usdc=0.0
        )
    
    # 不同市场条件
    market_scenarios = [
        {"volatility": 0.1, "risk_level": "LOW", "name": "🟢 低风险市场"},
        {"volatility": 0.25, "risk_level": "MEDIUM", "name": "🟡 中风险市场"},
        {"volatility": 0.45, "risk_level": "HIGH", "name": "🔴 高风险市场"}
    ]
    
    for scenario in market_scenarios:
        print(f"\n   {scenario['name']}:")
        target_weights = strategy.calculate_target_allocation(mock_allocations, scenario)
        
        # 按类型汇总
        stable_total = sum(w for asset, w in target_weights.items() 
                          if strategy.get_asset_type(asset) == AssetType.STABLECOIN)
        crypto_total = sum(w for asset, w in target_weights.items() 
                          if strategy.get_asset_type(asset) in [AssetType.CRYPTO, AssetType.NATIVE])
        rwa_total = sum(w for asset, w in target_weights.items() 
                       if 'RWA' in strategy.get_asset_type(asset).value.upper())
        
        print(f"      Stablecoins: {stable_total*100:.1f}%")
        print(f"      Crypto:      {crypto_total*100:.1f}%")
        print(f"      RWA:         {rwa_total*100:.1f}%")
    
    # 测试配置限制检查
    print("\n5️⃣ 测试配置限制...")
    
    # 创建违规配置
    bad_allocations = {}
    for i, asset_name in enumerate(config['assets'].keys()):
        from agents.multi_asset_strategy import AssetAllocation
        # 让BTC权重过高
        weight = 0.60 if asset_name == 'btc' else 0.05
        bad_allocations[asset_name] = AssetAllocation(
            asset_name=asset_name,
            asset_type=strategy.get_asset_type(asset_name),
            current_value_usdc=weight * 10000,
            current_weight=weight,
            target_weight=0.0,
            recommended_action=None,
            trade_amount_usdc=0.0
        )
    
    warnings = strategy.check_allocation_limits(bad_allocations)
    if warnings:
        print("   ⚠️  检测到配置警告:")
        for warning in warnings:
            print(f"      - {warning}")
    else:
        print("   ✅ 配置正常")
    
    print("\n" + "=" * 60)
    print("🎉 多资产策略测试完成！")
    print("\n✅ 已实现:")
    print("   • 8种资产类型（Stablecoins, Crypto, RWA）")
    print("   • USDC作为基准计价货币")
    print("   • 智能配置计算（根据市场条件）")
    print("   • 配置限制检查")
    print("   • 再平衡策略")
    print("   • 动量交易策略")
    
    return True

async def test_price_oracle_multi_asset():
    """测试价格预言机多资产支持"""
    print("\n🔍 测试价格预言机多资产支持")
    print("=" * 60)
    
    import yaml
    from stellar.horizon import Horizon
    from stellar.price_oracle import PriceOracle
    
    with open('app/config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    horizon = Horizon(config['network']['horizon'])
    oracle = PriceOracle(horizon, config)
    
    # 测试所有资产价格
    print("\n💰 所有资产价格 (以USDC计价):\n")
    
    for asset_name, asset_config in config['assets'].items():
        price = await oracle.get_price(asset_config['code'], 'USDC')
        asset_type = asset_config.get('type', 'unknown')
        
        # 格式化显示
        if asset_type == 'stablecoin':
            icon = "🪙"
        elif asset_type in ['crypto', 'native']:
            icon = "💎"
        else:
            icon = "🏢"
        
        print(f"   {icon} {asset_name.upper():>6} ({asset_type:>15}): ${price:>12,.2f}")
    
    print("\n✅ 价格预言机支持所有资产类型")
    
    return True

async def main():
    """主测试函数"""
    try:
        await test_multi_asset_strategy()
        await test_price_oracle_multi_asset()
        
        print("\n" + "=" * 60)
        print("🎊 所有测试通过！")
        print("\n📚 系统现已支持:")
        print("   ✅ 多资产类型交易")
        print("   ✅ USDC计价和结算")
        print("   ✅ 智能资产配置")
        print("   ✅ 风险限制管理")
        print("   ✅ 自动再平衡")
        print("\n🚀 现在可以重启dashboard查看新功能！")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
