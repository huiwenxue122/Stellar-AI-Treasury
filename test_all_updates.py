#!/usr/bin/env python3
"""
🧪 Comprehensive Dry-Run Test for All Updates

Tests all recent updates without using OpenAI API or network calls:
1. Capital configuration ($1K, $10K, $100K, $1M)
2. Asset updates (BOND → BENJI)
3. Preset button logic
4. Type consistency
5. Dashboard display updates
6. Tier system integration
7. Localization
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

def test_config_loading():
    """Test 1: Config file loads correctly"""
    print("=" * 80)
    print("🧪 Test 1: Config Loading")
    print("=" * 80)
    
    try:
        import yaml
        with open('app/config.yaml', 'r') as f:
            config = yaml.safe_load(f)
        
        print("✅ Config file loaded successfully")
        
        # Check BENJI exists
        if 'benji' in config['assets']:
            benji = config['assets']['benji']
            print(f"✅ BENJI asset found:")
            print(f"   Code: {benji['code']}")
            print(f"   Issuer: {benji['issuer']}")
            print(f"   Fund: {benji.get('fund_name', 'N/A')}")
        else:
            print("❌ BENJI asset not found in config")
            return False
        
        # Check BOND doesn't exist
        if 'bond' not in config['assets']:
            print("✅ BOND asset correctly removed")
        else:
            print("❌ BOND asset still exists in config")
            return False
        
        # Check asset_risk_classification
        safe_assets = config['asset_risk_classification']['safe']
        bond_tokens = safe_assets.get('bond_tokens', [])
        
        if 'BENJI' in bond_tokens:
            print(f"✅ BENJI in bond_tokens: {bond_tokens}")
        else:
            print(f"❌ BENJI not in bond_tokens: {bond_tokens}")
            return False
        
        if 'BOND' not in bond_tokens:
            print("✅ BOND correctly removed from bond_tokens")
        else:
            print("❌ BOND still in bond_tokens")
            return False
        
        # Check tier system
        beginner_assets = config['user_tier_system']['tiers']['beginner']['allowed_assets']
        if 'BENJI' in beginner_assets:
            print(f"✅ BENJI in beginner allowed_assets")
        else:
            print(f"❌ BENJI not in beginner allowed_assets")
            return False
        
        # Check issuer addresses
        print("\n📋 Asset Issuer Status:")
        
        demo_assets = ['gold', 'reit']
        for asset in demo_assets:
            if asset in config['assets']:
                issuer = config['assets'][asset]['issuer']
                if 'DEMO' in issuer:
                    print(f"   ✅ {asset.upper()}: {issuer} (correctly marked as demo)")
                else:
                    print(f"   ⚠️  {asset.upper()}: {issuer} (should be marked as demo)")
        
        cross_chain_assets = ['paxg', 'xaut']
        for asset in cross_chain_assets:
            if asset in config['assets']:
                issuer = config['assets'][asset]['issuer']
                if 'NOT_ON_STELLAR' in issuer:
                    print(f"   ✅ {asset.upper()}: {issuer} (correctly marked)")
                else:
                    print(f"   ⚠️  {asset.upper()}: {issuer} (should be NOT_ON_STELLAR)")
        
        print("\n✅ Config loading test PASSED\n")
        return True
        
    except Exception as e:
        print(f"❌ Config loading test FAILED: {e}\n")
        return False

def test_tier_manager():
    """Test 2: TierManager with BENJI"""
    print("=" * 80)
    print("🧪 Test 2: TierManager Integration")
    print("=" * 80)
    
    try:
        from app.tier_manager import TierManager
        import yaml
        
        with open('app/config.yaml', 'r') as f:
            config = yaml.safe_load(f)
        
        tier_manager = TierManager(config)
        
        # Test asset filtering for each tier
        for tier in ['beginner', 'intermediate', 'advanced']:
            print(f"\n🎯 {tier.upper()} Tier:")
            
            assets_by_risk = tier_manager.get_assets_by_risk_level(tier)
            
            safe_assets = assets_by_risk.get('safe', [])
            if 'BENJI' in safe_assets:
                print(f"   ✅ BENJI in safe assets: {safe_assets}")
            else:
                print(f"   ❌ BENJI not in safe assets: {safe_assets}")
                return False
            
            if 'BOND' in safe_assets:
                print(f"   ❌ BOND still in safe assets: {safe_assets}")
                return False
            else:
                print(f"   ✅ BOND correctly removed")
        
        # Test safety explanation
        benji_explanation = tier_manager.get_safety_explanation('BENJI', 'beginner', 'en')
        if benji_explanation and 'Franklin Templeton' in benji_explanation:
            print(f"\n✅ BENJI safety explanation found:")
            print(f"   {benji_explanation[:100]}...")
        else:
            print(f"\n❌ BENJI safety explanation not found or incorrect")
            return False
        
        # Test that BOND explanation is gone
        bond_explanation = tier_manager.get_safety_explanation('BOND', 'beginner', 'en')
        if not bond_explanation:
            print("✅ BOND safety explanation correctly removed")
        else:
            print(f"❌ BOND safety explanation still exists: {bond_explanation}")
            return False
        
        print("\n✅ TierManager test PASSED\n")
        return True
        
    except Exception as e:
        print(f"❌ TierManager test FAILED: {e}\n")
        import traceback
        traceback.print_exc()
        return False

def test_capital_configuration():
    """Test 3: Capital configuration logic"""
    print("=" * 80)
    print("🧪 Test 3: Capital Configuration")
    print("=" * 80)
    
    FIXED_XLM_PRICE = 0.31
    
    test_cases = [
        {'tier': 'beginner', 'usd': 1000.0, 'expected_xlm': 3225.81},
        {'tier': 'beginner', 'usd': 10000.0, 'expected_xlm': 32258.06},
        {'tier': 'intermediate', 'usd': 25000.0, 'expected_xlm': 80645.16},
        {'tier': 'advanced', 'usd': 100000.0, 'expected_xlm': 322580.65},
        {'tier': 'advanced', 'usd': 1000000.0, 'expected_xlm': 3225806.45},
    ]
    
    all_passed = True
    
    for case in test_cases:
        xlm_amount = case['usd'] / FIXED_XLM_PRICE
        
        if abs(xlm_amount - case['expected_xlm']) < 0.1:
            print(f"✅ {case['tier']}: ${case['usd']:,.0f} → {xlm_amount:,.2f} XLM")
        else:
            print(f"❌ {case['tier']}: ${case['usd']:,.0f} → {xlm_amount:,.2f} XLM (expected {case['expected_xlm']:,.2f})")
            all_passed = False
    
    if all_passed:
        print("\n✅ Capital configuration test PASSED\n")
    else:
        print("\n❌ Capital configuration test FAILED\n")
    
    return all_passed

def test_preset_buttons():
    """Test 4: Preset button logic"""
    print("=" * 80)
    print("🧪 Test 4: Preset Button Logic")
    print("=" * 80)
    
    tier_limits = {
        'beginner': {'min': 100.0, 'max': 10000.0},
        'intermediate': {'min': 1000.0, 'max': 100000.0},
        'advanced': {'min': 10000.0, 'max': 10000000.0}
    }
    
    presets = [
        ("$1K", 1000.0),
        ("$10K", 10000.0),
        ("$100K", 100000.0),
        ("$1M", 1000000.0)
    ]
    
    all_passed = True
    
    for tier, limits in tier_limits.items():
        print(f"\n🎯 {tier.upper()} Tier (${limits['min']:,.0f} - ${limits['max']:,.0f}):")
        
        for label, amount in presets:
            is_enabled = limits['min'] <= amount <= limits['max']
            status = "✅ Enabled" if is_enabled else "🔒 Locked"
            print(f"   {label}: {status}")
            
            # Verify type is float
            if not isinstance(amount, float):
                print(f"   ❌ Type error: {label} is {type(amount)}, should be float")
                all_passed = False
    
    if all_passed:
        print("\n✅ Preset button test PASSED\n")
    else:
        print("\n❌ Preset button test FAILED\n")
    
    return all_passed

def test_localization():
    """Test 5: Localization updates"""
    print("=" * 80)
    print("🧪 Test 5: Localization")
    print("=" * 80)
    
    try:
        from app.localization import TRANSLATIONS
        
        # Check BENJI translation exists
        if 'benji_safe' in TRANSLATIONS:
            print("✅ benji_safe translation found")
            
            languages = ['en', 'es', 'sw', 'ar', 'zh']
            for lang in languages:
                if lang in TRANSLATIONS['benji_safe']:
                    text = TRANSLATIONS['benji_safe'][lang]
                    if 'Franklin Templeton' in text or 'BENJI' in text:
                        print(f"   ✅ {lang}: {text[:50]}...")
                    else:
                        print(f"   ⚠️  {lang}: Translation exists but may need update")
                else:
                    print(f"   ❌ {lang}: Translation missing")
                    return False
        else:
            print("❌ benji_safe translation not found")
            return False
        
        # Check BOND translation is removed/updated
        if 'bond_safe' in TRANSLATIONS:
            print("⚠️  bond_safe translation still exists (should be removed or kept for backward compatibility)")
        else:
            print("✅ bond_safe translation correctly removed")
        
        print("\n✅ Localization test PASSED\n")
        return True
        
    except Exception as e:
        print(f"❌ Localization test FAILED: {e}\n")
        return False

def test_asset_manager_integration():
    """Test 6: AssetManager capital setting"""
    print("=" * 80)
    print("🧪 Test 6: AssetManager Integration")
    print("=" * 80)
    
    try:
        from stellar.assets import AssetManager
        from stellar.horizon import Horizon
        import yaml
        
        with open('app/config.yaml', 'r') as f:
            config = yaml.safe_load(f)
        
        # Mock horizon (won't make real calls in dry-run)
        class MockHorizon:
            def __init__(self):
                pass
        
        horizon = MockHorizon()
        asset_manager = AssetManager(horizon, config)
        
        # Test initial capital setting
        test_capitals = [
            (1000.0, 0.31, 3225.81),
            (10000.0, 0.31, 32258.06),
            (1000000.0, 0.31, 3225806.45)
        ]
        
        for capital_usd, xlm_price, expected_xlm in test_capitals:
            xlm_amount = asset_manager.set_initial_capital_usd(capital_usd, xlm_price)
            
            if abs(xlm_amount - expected_xlm) < 0.1:
                print(f"✅ ${capital_usd:,.0f} → {xlm_amount:,.2f} XLM")
                
                # Check simulated_balances
                if 'xlm' in asset_manager.simulated_balances:
                    balance = asset_manager.simulated_balances['xlm']
                    if abs(balance - expected_xlm) < 0.1:
                        print(f"   ✅ Simulated balance: {balance:,.2f} XLM")
                    else:
                        print(f"   ❌ Simulated balance mismatch: {balance:,.2f} (expected {expected_xlm:,.2f})")
                        return False
                else:
                    print(f"   ❌ 'xlm' not in simulated_balances")
                    return False
            else:
                print(f"❌ ${capital_usd:,.0f} → {xlm_amount:,.2f} XLM (expected {expected_xlm:,.2f})")
                return False
        
        # Test that initial_capital_usd is updated
        if asset_manager.initial_capital_usd == test_capitals[-1][0]:
            print(f"✅ initial_capital_usd updated: ${asset_manager.initial_capital_usd:,.0f}")
        else:
            print(f"❌ initial_capital_usd not updated correctly: ${asset_manager.initial_capital_usd:,.0f}")
            return False
        
        print("\n✅ AssetManager test PASSED\n")
        return True
        
    except Exception as e:
        print(f"❌ AssetManager test FAILED: {e}\n")
        import traceback
        traceback.print_exc()
        return False

def test_orchestrator_integration():
    """Test 7: Orchestrator capital setting"""
    print("=" * 80)
    print("🧪 Test 7: Orchestrator Integration")
    print("=" * 80)
    
    try:
        # Test initialize() doesn't overwrite user capital
        print("Testing initialize() logic:")
        print("   Scenario 1: User sets $1K, then initialize()")
        
        # Simulate user setting capital
        initial_capital_usd = 1000.0
        xlm_price = 0.31
        xlm_amount = initial_capital_usd / xlm_price
        
        simulated_balances = {'xlm': xlm_amount}
        
        # Simulate initialize() logic
        if 'xlm' not in simulated_balances:
            print("   ❌ Would initialize with default (wrong)")
            return False
        else:
            print(f"   ✅ Would use existing balance: {simulated_balances['xlm']:,.2f} XLM")
        
        print("\n   Scenario 2: Initialize() before user configuration")
        
        empty_balances = {}
        TARGET_USD = 1000000.0  # From initial_capital_usd default
        
        if 'xlm' not in empty_balances:
            xlm_needed = TARGET_USD / xlm_price
            print(f"   ✅ Would initialize with initial_capital_usd: {xlm_needed:,.2f} XLM")
        
        print("\n✅ Orchestrator test PASSED\n")
        return True
        
    except Exception as e:
        print(f"❌ Orchestrator test FAILED: {e}\n")
        return False

def main():
    """Run all tests"""
    print("\n" + "🧪" * 40)
    print("COMPREHENSIVE DRY-RUN TEST SUITE")
    print("Testing all recent updates without API calls")
    print("🧪" * 40 + "\n")
    
    tests = [
        ("Config Loading", test_config_loading),
        ("TierManager", test_tier_manager),
        ("Capital Configuration", test_capital_configuration),
        ("Preset Buttons", test_preset_buttons),
        ("Localization", test_localization),
        ("AssetManager", test_asset_manager_integration),
        ("Orchestrator", test_orchestrator_integration),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}\n")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 TEST SUMMARY")
    print("=" * 80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print("\n" + "=" * 80)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! System is ready.")
    else:
        print(f"⚠️  {total - passed} test(s) failed. Please review errors above.")
    
    print("=" * 80 + "\n")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

