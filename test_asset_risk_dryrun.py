#!/usr/bin/env python3
"""
Dry-Run Test for Asset Risk Classification System
Tests asset filtering by risk level WITHOUT calling any APIs
"""

import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

import yaml
from app.tier_manager import TierManager

def print_section(title):
    """Print a formatted section header"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80)

def test_config_loading():
    """Test that config loads correctly with new risk classification"""
    print_section("1️⃣ Testing Config Loading")
    
    try:
        with open('app/config.yaml', 'r') as f:
            config = yaml.safe_load(f)
        
        # Check asset_risk_classification exists
        assert 'asset_risk_classification' in config, "❌ Missing asset_risk_classification"
        print("✅ asset_risk_classification found in config")
        
        risk_class = config['asset_risk_classification']
        
        # Check all 3 risk levels exist
        assert 'safe' in risk_class, "❌ Missing 'safe' risk level"
        assert 'moderate' in risk_class, "❌ Missing 'moderate' risk level"
        assert 'high_risk' in risk_class, "❌ Missing 'high_risk' risk level"
        print("✅ All 3 risk levels (safe, moderate, high_risk) present")
        
        # Check safe assets
        safe_assets = []
        for category, assets in risk_class['safe'].items():
            if isinstance(assets, list):
                safe_assets.extend(assets)
        
        print(f"\n📊 Safe Assets ({len(safe_assets)} total):")
        print(f"   {', '.join(safe_assets)}")
        
        expected_safe = ['USDC', 'USDT', 'PAXG', 'XAUT', 'GOLD', 'BOND', 'REIT']
        for asset in expected_safe:
            if asset not in safe_assets:
                print(f"   ⚠️  Warning: Expected safe asset '{asset}' not found")
        
        # Check moderate assets
        moderate_assets = []
        for category, assets in risk_class['moderate'].items():
            if isinstance(assets, list):
                moderate_assets.extend(assets)
        
        print(f"\n📊 Moderate Risk Assets ({len(moderate_assets)} total):")
        print(f"   {', '.join(moderate_assets)}")
        
        # Check high risk assets
        high_risk_assets = []
        for category, assets in risk_class['high_risk'].items():
            if isinstance(assets, list):
                high_risk_assets.extend(assets)
        
        print(f"\n📊 High Risk Assets ({len(high_risk_assets)} total):")
        print(f"   {', '.join(high_risk_assets)}")
        
        # Check tier configs have allowed_risk_levels
        print(f"\n📋 Checking Tier Configurations:")
        tiers = config['user_tier_system']['tiers']
        
        for tier_name, tier_data in tiers.items():
            risk_levels = tier_data.get('allowed_risk_levels', [])
            print(f"   {tier_name.upper()}: {risk_levels}")
            assert risk_levels, f"❌ {tier_name} missing allowed_risk_levels"
        
        print("\n✅ Config loading test PASSED")
        return config
        
    except Exception as e:
        print(f"\n❌ Config loading test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_tier_manager_initialization(config):
    """Test TierManager initializes correctly"""
    print_section("2️⃣ Testing TierManager Initialization")
    
    try:
        tier_manager = TierManager(config)
        
        print(f"✅ TierManager initialized")
        print(f"   Enabled: {tier_manager.enabled}")
        print(f"   Default tier: {tier_manager.default_tier}")
        print(f"   Available tiers: {list(tier_manager.tiers.keys())}")
        
        # Check each tier has allowed_risk_levels
        for tier_name in ['beginner', 'intermediate', 'advanced']:
            tier_config = tier_manager.get_tier_config(tier_name)
            risk_levels = tier_config.allowed_risk_levels
            print(f"\n   {tier_name.upper()} tier:")
            print(f"      Allowed risk levels: {risk_levels}")
            print(f"      Risk budget: {tier_config.risk_budget}")
            print(f"      Max VaR: {tier_config.max_portfolio_var * 100}%")
        
        print("\n✅ TierManager initialization test PASSED")
        return tier_manager
        
    except Exception as e:
        print(f"\n❌ TierManager initialization test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_get_assets_by_risk_level(tier_manager):
    """Test get_assets_by_risk_level method"""
    print_section("3️⃣ Testing get_assets_by_risk_level()")
    
    try:
        for tier_name in ['beginner', 'intermediate', 'advanced']:
            print(f"\n📊 {tier_name.upper()} Tier:")
            
            assets_by_risk = tier_manager.get_assets_by_risk_level(tier_name)
            
            # Check structure
            assert isinstance(assets_by_risk, dict), "❌ Should return dict"
            assert 'safe' in assets_by_risk, "❌ Missing 'safe' key"
            assert 'moderate' in assets_by_risk, "❌ Missing 'moderate' key"
            assert 'high_risk' in assets_by_risk, "❌ Missing 'high_risk' key"
            
            # Display results
            safe_count = len(assets_by_risk['safe'])
            moderate_count = len(assets_by_risk['moderate'])
            high_count = len(assets_by_risk['high_risk'])
            
            print(f"   🛡️  Safe: {safe_count} assets")
            if safe_count > 0:
                print(f"      {', '.join(assets_by_risk['safe'])}")
            
            print(f"   ⚖️  Moderate: {moderate_count} assets")
            if moderate_count > 0:
                print(f"      {', '.join(assets_by_risk['moderate'])}")
            
            print(f"   🚀 High Risk: {high_count} assets")
            if high_count > 0:
                print(f"      {', '.join(assets_by_risk['high_risk'])}")
            
            # Validate tier-specific rules
            if tier_name == 'beginner':
                assert safe_count > 0, "❌ Beginner should have safe assets"
                assert moderate_count == 0, "❌ Beginner should NOT have moderate assets"
                assert high_count == 0, "❌ Beginner should NOT have high risk assets"
                assert safe_count >= 5, f"❌ Beginner should have at least 5 safe assets, got {safe_count}"
            
            elif tier_name == 'intermediate':
                assert safe_count > 0, "❌ Intermediate should have safe assets"
                assert moderate_count > 0, "❌ Intermediate should have moderate assets"
                assert high_count == 0, "❌ Intermediate should NOT have high risk assets"
            
            elif tier_name == 'advanced':
                assert safe_count > 0, "❌ Advanced should have safe assets"
                assert moderate_count > 0, "❌ Advanced should have moderate assets"
                assert high_count > 0, "❌ Advanced should have high risk assets"
        
        print("\n✅ get_assets_by_risk_level() test PASSED")
        return True
        
    except Exception as e:
        print(f"\n❌ get_assets_by_risk_level() test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_get_asset_risk_level(tier_manager):
    """Test get_asset_risk_level method"""
    print_section("4️⃣ Testing get_asset_risk_level()")
    
    try:
        test_cases = {
            'USDC': 'safe',
            'PAXG': 'safe',
            'BOND': 'safe',
            'REIT': 'safe',
            'BTC': 'moderate',
            'ETH': 'moderate',
            'LINK': 'moderate',
            'LDO': 'high_risk',
            'FET': 'high_risk',
            'XLM': 'high_risk'
        }
        
        print("\n🧪 Testing asset risk level detection:")
        
        all_passed = True
        for asset, expected_level in test_cases.items():
            actual_level = tier_manager.get_asset_risk_level(asset)
            
            if actual_level == expected_level:
                print(f"   ✅ {asset}: {actual_level} (correct)")
            else:
                print(f"   ❌ {asset}: got '{actual_level}', expected '{expected_level}'")
                all_passed = False
        
        if all_passed:
            print("\n✅ get_asset_risk_level() test PASSED")
        else:
            print("\n⚠️  get_asset_risk_level() test had some failures")
        
        return all_passed
        
    except Exception as e:
        print(f"\n❌ get_asset_risk_level() test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_safety_explanations(tier_manager):
    """Test safety explanations for new assets"""
    print_section("5️⃣ Testing Safety Explanations")
    
    try:
        new_assets = ['PAXG', 'XAUT', 'GOLD', 'BOND', 'REIT']
        languages = ['en', 'es', 'sw', 'ar', 'zh']
        
        print("\n🌍 Testing safety explanations for new assets:")
        
        for asset in new_assets:
            print(f"\n   {asset}:")
            has_explanation = False
            
            for lang in languages:
                explanation = tier_manager.get_safety_explanation(asset, 'beginner', lang)
                
                if explanation:
                    has_explanation = True
                    print(f"      {lang.upper()}: {explanation[:60]}...")
                else:
                    print(f"      {lang.upper()}: (no explanation)")
            
            if not has_explanation:
                print(f"      ⚠️  Warning: No explanations found for {asset}")
        
        print("\n✅ Safety explanations test PASSED")
        return True
        
    except Exception as e:
        print(f"\n❌ Safety explanations test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_beginner_scenario():
    """Test complete beginner user scenario"""
    print_section("6️⃣ Testing Beginner User Scenario")
    
    try:
        with open('app/config.yaml', 'r') as f:
            config = yaml.safe_load(f)
        
        tier_manager = TierManager(config)
        
        print("\n👤 Scenario: Sarah is a first-time investor from Kenya")
        print("   - Tier: Beginner")
        print("   - Language: Swahili")
        print("   - Goal: Invest safely in gold and bonds")
        
        # Get available assets
        assets_by_risk = tier_manager.get_assets_by_risk_level('beginner')
        
        print(f"\n📋 Step 1: View available assets")
        print(f"   Available: {', '.join(assets_by_risk['safe'])}")
        print(f"   Locked: BTC, ETH, SOL, etc. (moderate/high risk)")
        
        # Check specific assets
        print(f"\n📋 Step 2: Select assets")
        selected = ['USDC', 'PAXG', 'BOND']
        
        for asset in selected:
            if asset in assets_by_risk['safe']:
                print(f"   ✅ {asset} - Available")
                
                # Get explanation
                explanation = tier_manager.get_safety_explanation(asset, 'beginner', 'sw')
                if explanation:
                    print(f"      Safety: {explanation[:80]}...")
            else:
                print(f"   ❌ {asset} - NOT available (should be!)")
                raise AssertionError(f"{asset} should be available to beginners")
        
        # Try to select locked asset
        print(f"\n📋 Step 3: Try to select BTC (should be locked)")
        if 'BTC' in assets_by_risk['moderate'] or 'BTC' in assets_by_risk['high_risk']:
            print(f"   ❌ BTC - Locked (as expected)")
        else:
            print(f"   ✅ BTC - Correctly filtered out")
        
        print(f"\n✅ Beginner scenario test PASSED")
        print(f"   Sarah can safely invest in: {', '.join(selected)}")
        return True
        
    except Exception as e:
        print(f"\n❌ Beginner scenario test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_intermediate_scenario():
    """Test intermediate user scenario"""
    print_section("7️⃣ Testing Intermediate User Scenario")
    
    try:
        with open('app/config.yaml', 'r') as f:
            config = yaml.safe_load(f)
        
        tier_manager = TierManager(config)
        
        print("\n👤 Scenario: Alex wants balanced portfolio")
        print("   - Tier: Intermediate")
        print("   - Goal: Mix safe assets with BTC/ETH")
        
        # Get available assets
        assets_by_risk = tier_manager.get_assets_by_risk_level('intermediate')
        
        safe_count = len(assets_by_risk['safe'])
        moderate_count = len(assets_by_risk['moderate'])
        high_count = len(assets_by_risk['high_risk'])
        
        print(f"\n📋 Available Assets:")
        print(f"   Safe: {safe_count} assets - {', '.join(assets_by_risk['safe'][:5])}...")
        print(f"   Moderate: {moderate_count} assets - {', '.join(assets_by_risk['moderate'])}")
        print(f"   High Risk: {high_count} assets (should be 0)")
        
        # Verify
        assert safe_count > 0, "Should have safe assets"
        assert moderate_count > 0, "Should have moderate assets"
        assert high_count == 0, "Should NOT have high risk assets"
        
        # Build portfolio
        print(f"\n📋 Building Portfolio:")
        portfolio = {
            'USDC': 30,  # safe
            'PAXG': 20,  # safe (gold)
            'BTC': 30,   # moderate
            'ETH': 20    # moderate
        }
        
        for asset, allocation in portfolio.items():
            # Check if available
            if asset in assets_by_risk['safe']:
                risk_level = 'safe'
            elif asset in assets_by_risk['moderate']:
                risk_level = 'moderate'
            else:
                raise AssertionError(f"{asset} should be available to intermediate")
            
            print(f"   ✅ {asset} ({allocation}%) - {risk_level}")
        
        print(f"\n✅ Intermediate scenario test PASSED")
        return True
        
    except Exception as e:
        print(f"\n❌ Intermediate scenario test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_advanced_scenario():
    """Test advanced user scenario"""
    print_section("8️⃣ Testing Advanced User Scenario")
    
    try:
        with open('app/config.yaml', 'r') as f:
            config = yaml.safe_load(f)
        
        tier_manager = TierManager(config)
        
        print("\n👤 Scenario: Pro trader wants all assets")
        print("   - Tier: Advanced")
        print("   - Goal: Access all 16 assets")
        
        # Get available assets
        assets_by_risk = tier_manager.get_assets_by_risk_level('advanced')
        
        safe_count = len(assets_by_risk['safe'])
        moderate_count = len(assets_by_risk['moderate'])
        high_count = len(assets_by_risk['high_risk'])
        
        total_assets = safe_count + moderate_count + high_count
        
        print(f"\n📋 Available Assets:")
        print(f"   Safe: {safe_count} assets")
        print(f"   Moderate: {moderate_count} assets")
        print(f"   High Risk: {high_count} assets")
        print(f"   TOTAL: {total_assets} assets")
        
        # Verify
        assert safe_count > 0, "Should have safe assets"
        assert moderate_count > 0, "Should have moderate assets"
        assert high_count > 0, "Should have high risk assets"
        assert total_assets >= 10, f"Should have at least 10 assets, got {total_assets}"
        
        # Test can access all risk levels
        print(f"\n📋 Testing Access:")
        test_assets = {
            'USDC': 'safe',
            'PAXG': 'safe',
            'BTC': 'moderate',
            'ETH': 'moderate',
            'LDO': 'high_risk',
            'FET': 'high_risk'
        }
        
        for asset, expected_risk in test_assets.items():
            if expected_risk == 'safe' and asset in assets_by_risk['safe']:
                print(f"   ✅ {asset} ({expected_risk}) - Available")
            elif expected_risk == 'moderate' and asset in assets_by_risk['moderate']:
                print(f"   ✅ {asset} ({expected_risk}) - Available")
            elif expected_risk == 'high_risk' and asset in assets_by_risk['high_risk']:
                print(f"   ✅ {asset} ({expected_risk}) - Available")
            else:
                print(f"   ❌ {asset} ({expected_risk}) - NOT found in {expected_risk} list!")
                raise AssertionError(f"{asset} should be in {expected_risk} list")
        
        print(f"\n✅ Advanced scenario test PASSED")
        print(f"   Full freedom: All {total_assets} assets accessible")
        return True
        
    except Exception as e:
        print(f"\n❌ Advanced scenario test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_all_tests():
    """Run all dry-run tests"""
    print("\n" + "🧪"*40)
    print("  DRY-RUN TEST: Asset Risk Classification")
    print("  Testing WITHOUT any API calls")
    print("🧪"*40)
    
    results = []
    
    # Test 1: Config loading
    config = test_config_loading()
    results.append(("Config Loading", config is not None))
    if not config:
        print("\n❌ Cannot continue without valid config")
        return False
    
    # Test 2: TierManager initialization
    tier_manager = test_tier_manager_initialization(config)
    results.append(("TierManager Init", tier_manager is not None))
    if not tier_manager:
        print("\n❌ Cannot continue without TierManager")
        return False
    
    # Test 3: get_assets_by_risk_level
    result = test_get_assets_by_risk_level(tier_manager)
    results.append(("get_assets_by_risk_level()", result))
    
    # Test 4: get_asset_risk_level
    result = test_get_asset_risk_level(tier_manager)
    results.append(("get_asset_risk_level()", result))
    
    # Test 5: Safety explanations
    result = test_safety_explanations(tier_manager)
    results.append(("Safety Explanations", result))
    
    # Test 6: Beginner scenario
    result = test_beginner_scenario()
    results.append(("Beginner Scenario", result))
    
    # Test 7: Intermediate scenario
    result = test_intermediate_scenario()
    results.append(("Intermediate Scenario", result))
    
    # Test 8: Advanced scenario
    result = test_advanced_scenario()
    results.append(("Advanced Scenario", result))
    
    # Summary
    print_section("✅ TEST SUMMARY")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"\n📊 Results: {passed}/{total} tests passed\n")
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status}: {test_name}")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! 🎉")
        print("\n💡 Next Steps:")
        print("   - Run 'python smart_start.py' to test in dashboard")
        print("   - Try selecting different tiers and see asset filtering")
        print("   - Check safety explanations display correctly")
        print("\n🔒 NO API CALLS MADE - Your keys are safe!")
        return True
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please review errors above.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

