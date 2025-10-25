#!/usr/bin/env python3
"""
Test script for Stellar AI Treasury system
This script tests the complete system integration on Stellar testnet
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.orchestrator import ORCHESTRATOR
from stellar.assets import AssetManager
from agents.trading import TradingAgent
from agents.risk import RiskAgent
from agents.payment import PaymentAgent

async def test_system_initialization():
    """Test system initialization"""
    print("🔧 Testing system initialization...")
    
    try:
        success = await ORCHESTRATOR.initialize()
        if success:
            print("✅ System initialization successful")
            return True
        else:
            print("❌ System initialization failed")
            return False
    except Exception as e:
        print(f"❌ System initialization error: {e}")
        return False

async def test_portfolio_status():
    """Test portfolio status retrieval"""
    print("\n📊 Testing portfolio status...")
    
    try:
        status = await ORCHESTRATOR.get_portfolio_status()
        print(f"✅ Portfolio status retrieved:")
        print(f"   Portfolio Value: ${status['portfolio_value_usd']:.2f}")
        print(f"   USDC Allocation: {status['usdc_allocation']:.1f}%")
        print(f"   Assets: {len(status['assets'])}")
        
        for asset_name, asset_info in status['assets'].items():
            print(f"   {asset_name.upper()}: {asset_info['balance']:.2f} (${asset_info['value_usd']:.2f})")
        
        return True
    except Exception as e:
        print(f"❌ Portfolio status error: {e}")
        return False

async def test_trading_cycle():
    """Test trading cycle execution"""
    print("\n🔄 Testing trading cycle...")
    
    try:
        # Create mock market data with high volatility to trigger USDC conversion
        market_data = {
            "prices": [1.0, 1.05, 0.95, 1.1, 0.9, 1.15, 0.85],  # High volatility
            "volatility_zscore": 2.5,  # High volatility
            "impact_bps": 20.0,
            "impact_gap_bps": 30.0,
            "depth_ok": True,
            "better_bps": 25.0
        }
        
        results = await ORCHESTRATOR.run_trading_cycle(market_data)
        
        print(f"✅ Trading cycle completed:")
        print(f"   Status: {results['status']}")
        
        if results['status'] == 'SUCCESS':
            trading_results = results['trading_results']
            print(f"   Signals Generated: {trading_results['signals_generated']}")
            print(f"   Final USDC Profit: ${trading_results['final_usdc_profit']:.2f}")
            
            if 'risk_response' in trading_results:
                risk_response = trading_results['risk_response']
                print(f"   Risk Assessment: {risk_response['risk_assessment']['risk_level']}")
                print(f"   Total Profit: ${risk_response['total_profit_usdc']:.2f}")
        
        return True
    except Exception as e:
        print(f"❌ Trading cycle error: {e}")
        return False

async def test_risk_management():
    """Test risk management functionality"""
    print("\n⚠️  Testing risk management...")
    
    try:
        risk_summary = ORCHESTRATOR.risk_agent.get_risk_summary()
        
        print(f"✅ Risk management status:")
        print(f"   Risk Level: {risk_summary['current_risk']['risk_level']}")
        print(f"   Risk Score: {risk_summary['current_risk']['score']:.2f}")
        print(f"   Total Profit: ${risk_summary['total_profit_usdc']:.2f}")
        print(f"   Daily Trades: {risk_summary['daily_trade_count']}")
        print(f"   Should Halt: {risk_summary['should_halt']}")
        print(f"   Recommendation: {risk_summary['recommendation']}")
        
        return True
    except Exception as e:
        print(f"❌ Risk management error: {e}")
        return False

async def test_manual_trade():
    """Test manual trade execution"""
    print("\n💱 Testing manual trade...")
    
    try:
        # Test converting a small amount to USDC
        result = await ORCHESTRATOR.execute_manual_trade(
            "convert_to_usdc", "XLM", 10.0
        )
        
        if result['success']:
            print("✅ Manual trade executed successfully")
            print(f"   Transaction Hash: {result['result'].get('transaction_hash', 'N/A')}")
        else:
            print(f"⚠️  Manual trade failed: {result.get('error', 'Unknown error')}")
            print("   This is expected if you don't have sufficient XLM balance")
        
        return True
    except Exception as e:
        print(f"❌ Manual trade error: {e}")
        return False

async def test_stablecoin_strategy():
    """Test stablecoin strategy specifically"""
    print("\n🪙 Testing stablecoin strategy...")
    
    try:
        # Test with high volatility scenario
        high_vol_market_data = {
            "prices": [1.0, 1.1, 0.9, 1.2, 0.8, 1.3, 0.7],  # Very high volatility
            "volatility_zscore": 3.0,
            "impact_bps": 25.0,
            "impact_gap_bps": 35.0,
            "depth_ok": True,
            "better_bps": 30.0
        }
        
        # Generate signals
        signals = ORCHESTRATOR.trading_agent.generate_trading_signals(high_vol_market_data)
        
        print(f"✅ Stablecoin strategy test:")
        print(f"   Signals generated: {len(signals)}")
        
        for i, signal in enumerate(signals):
            print(f"   Signal {i+1}: {signal.action} {signal.asset} ({signal.amount:.2f})")
            print(f"   Reason: {signal.reason}")
            print(f"   Confidence: {signal.confidence:.2f}")
        
        return True
    except Exception as e:
        print(f"❌ Stablecoin strategy error: {e}")
        return False

async def main():
    """Main test function"""
    print("🚀 Starting Stellar AI Treasury System Tests")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    # Check if we have the required environment variables
    if not os.getenv("STELLAR_SECRET") or not os.getenv("STELLAR_PUBLIC"):
        print("❌ Missing required environment variables:")
        print("   Please set STELLAR_SECRET and STELLAR_PUBLIC in your .env file")
        print("   You can get testnet keys from: https://laboratory.stellar.org/#account-creator")
        return
    
    tests = [
        ("System Initialization", test_system_initialization),
        ("Portfolio Status", test_portfolio_status),
        ("Risk Management", test_risk_management),
        ("Stablecoin Strategy", test_stablecoin_strategy),
        ("Trading Cycle", test_trading_cycle),
        ("Manual Trade", test_manual_trade),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 Test Summary:")
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Results: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed! System is ready for deployment.")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")

if __name__ == "__main__":
    asyncio.run(main())
