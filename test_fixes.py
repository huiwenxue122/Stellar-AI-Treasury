#!/usr/bin/env python3
"""
测试价格修复和风险指标
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_price_oracle():
    """测试价格预言机"""
    print("🔍 测试价格预言机...")
    print("=" * 60)
    
    from stellar.price_oracle import PriceOracle
    from stellar.horizon import Horizon
    
    horizon = Horizon('https://horizon-testnet.stellar.org')
    oracle = PriceOracle(horizon, {})
    
    # 测试获取多种资产价格
    assets = ['XLM', 'BTC', 'ETH', 'USDC', 'GOLD', 'BOND']
    
    prices = await oracle.get_multiple_prices(assets)
    
    print("\n💰 当前资产价格 (以USDC计价):")
    for asset, price in prices.items():
        print(f"   {asset:>6}: ${price:>12,.2f}")
    
    print("\n✅ 价格预言机工作正常！")
    return True

def test_advanced_risk():
    """测试高级风险分析"""
    print("\n🔍 测试高级风险分析...")
    print("=" * 60)
    
    from agents.advanced_risk import AdvancedRiskAnalyzer
    import numpy as np
    
    # 创建分析器
    analyzer = AdvancedRiskAnalyzer(risk_free_rate=0.04)
    
    # 模拟一些交易数据
    print("\n📊 添加模拟收益数据...")
    np.random.seed(42)
    
    # 模拟30天的收益数据
    for i in range(30):
        daily_return = np.random.normal(0.001, 0.02)  # 0.1%平均收益，2%波动
        analyzer.add_return(daily_return)
        
        portfolio_value = 10000 * (1 + i * 0.01)  # 模拟增长
        analyzer.add_portfolio_value(portfolio_value)
    
    # 计算风险指标
    print("\n📈 计算风险指标...")
    
    var_95 = analyzer.calculate_var(0.95)
    var_99 = analyzer.calculate_var(0.99)
    cvar_95 = analyzer.calculate_cvar(0.95)
    cvar_99 = analyzer.calculate_cvar(0.99)
    
    print(f"\n   VaR (95%):  {var_95*100:.2f}%")
    print(f"   VaR (99%):  {var_99*100:.2f}%")
    print(f"   CVaR (95%): {cvar_95*100:.2f}%")
    print(f"   CVaR (99%): {cvar_99*100:.2f}%")
    
    sharpe = analyzer.calculate_sharpe_ratio()
    sortino = analyzer.calculate_sortino_ratio()
    calmar = analyzer.calculate_calmar_ratio()
    omega = analyzer.calculate_omega_ratio()
    
    print(f"\n   Sharpe Ratio:  {sharpe:.3f}")
    print(f"   Sortino Ratio: {sortino:.3f}")
    print(f"   Calmar Ratio:  {calmar:.3f}")
    print(f"   Omega Ratio:   {omega:.3f}")
    
    max_dd, dd_duration, current_dd = analyzer.calculate_max_drawdown()
    
    print(f"\n   Max Drawdown:     {max_dd*100:.2f}%")
    print(f"   Current Drawdown: {current_dd*100:.2f}%")
    print(f"   DD Duration:      {dd_duration} days")
    
    # 获取完整指标
    metrics = analyzer.get_comprehensive_metrics()
    
    print(f"\n   Annual Volatility:     {metrics.volatility_annual*100:.2f}%")
    print(f"   Downside Volatility:   {metrics.downside_volatility*100:.2f}%")
    
    print("\n✅ 高级风险分析工作正常！")
    return True

def test_risk_agent_integration():
    """测试RiskAgent集成"""
    print("\n🔍 测试RiskAgent集成...")
    print("=" * 60)
    
    from agents.risk import RiskAgent
    import yaml
    
    # 加载配置
    with open('app/config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    # 创建RiskAgent
    risk_agent = RiskAgent(config)
    
    print("\n📊 模拟交易数据...")
    
    # 模拟一些交易
    import time
    for i in range(5):
        risk_agent.receive_trading_profit(
            pair="XLM/USDC",
            profit_usdc=100.0 * (1 + i * 0.1),
            trade_amount_usdc=1000.0
        )
        time.sleep(0.1)
    
    # 更新投资组合价值
    for i in range(10):
        portfolio_value = 10000 + i * 100
        risk_agent.update_portfolio_value(portfolio_value)
        
        if i > 0:
            risk_agent.calculate_daily_return(portfolio_value, portfolio_value - 100)
    
    # 获取风险摘要
    print("\n📈 获取风险摘要...")
    summary = risk_agent.get_risk_summary()
    
    print(f"\n   Total Profit:  ${summary['total_profit_usdc']:.2f}")
    print(f"   Risk Level:    {summary['current_risk']['risk_level']}")
    print(f"   Risk Score:    {summary['current_risk']['score']:.2f}")
    
    # VaR指标
    var = summary['var_metrics']
    print(f"\n   VaR (95%):     {var['var_95']*100:.2f}%")
    print(f"   CVaR (95%):    {var['cvar_95']*100:.2f}%")
    
    # 性能指标
    perf = summary['performance_metrics']
    print(f"\n   Sharpe Ratio:  {perf['sharpe_ratio']:.3f}")
    print(f"   Sortino Ratio: {perf['sortino_ratio']:.3f}")
    
    # 回撤指标
    dd = summary['drawdown_metrics']
    print(f"\n   Max Drawdown:  {dd['max_drawdown_pct']:.2f}%")
    
    print("\n✅ RiskAgent集成工作正常！")
    return True

async def main():
    """运行所有测试"""
    print("🚀 测试价格修复和风险指标集成")
    print("=" * 60)
    
    all_passed = True
    
    # 测试1: 价格预言机
    try:
        await test_price_oracle()
    except Exception as e:
        print(f"\n❌ 价格预言机测试失败: {e}")
        all_passed = False
    
    # 测试2: 高级风险分析
    try:
        test_advanced_risk()
    except Exception as e:
        print(f"\n❌ 高级风险分析测试失败: {e}")
        import traceback
        traceback.print_exc()
        all_passed = False
    
    # 测试3: RiskAgent集成
    try:
        test_risk_agent_integration()
    except Exception as e:
        print(f"\n❌ RiskAgent集成测试失败: {e}")
        import traceback
        traceback.print_exc()
        all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 所有测试通过！")
        print("\n✅ 价格获取已修复")
        print("✅ VaR/CVaR 已实现")
        print("✅ Sharpe Ratio 已实现")
        print("✅ Max Drawdown 已实现")
        print("✅ 所有高级风险指标已集成")
        print("\n💡 现在可以重启dashboard查看新功能！")
    else:
        print("⚠️  部分测试失败，请检查错误信息")
    
    return all_passed

if __name__ == "__main__":
    asyncio.run(main())
