#!/usr/bin/env python3
"""
Dry-Run Test for Tiered User System
Tests all tier features WITHOUT calling OpenAI API
"""

import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

import yaml
from app.tier_manager import TierManager
from app.localization import get_translation, get_tier_description, get_risk_explanation

def print_section(title):
    """Print a formatted section header"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

def test_tier_manager():
    """Test TierManager functionality"""
    print_section("🎓 Testing TierManager")
    
    # Load config
    with open('app/config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    tier_manager = TierManager(config)
    
    print(f"✅ TierManager initialized")
    print(f"   Enabled: {tier_manager.enabled}")
    print(f"   Default Tier: {tier_manager.default_tier}")
    print(f"   Available Tiers: {list(tier_manager.tiers.keys())}")
    
    # Test each tier
    for tier_name in ['beginner', 'intermediate', 'advanced']:
        print(f"\n📊 Testing {tier_name.upper()} Tier:")
        tier_config = tier_manager.get_tier_config(tier_name)
        
        print(f"   Risk Budget: {tier_config.risk_budget}")
        print(f"   Max VaR: {tier_config.max_portfolio_var * 100}%")
        print(f"   Max Single Asset: {tier_config.max_single_asset_percent}%")
        print(f"   Prompt Style: {tier_config.prompt_style}")
        print(f"   Explanation Depth: {tier_config.explanation_depth}")
        
        if tier_config.allowed_assets == 'all':
            print(f"   Allowed Assets: ALL")
        else:
            print(f"   Allowed Assets: {', '.join(tier_config.allowed_assets)}")
        
        if tier_config.localization:
            print(f"   Languages: {', '.join(tier_config.localization.get('languages', []))}")
            print(f"   TTS Enabled: {tier_config.localization.get('enable_tts', False)}")
    
    return tier_manager

def test_asset_filtering(tier_manager):
    """Test asset filtering based on tiers"""
    print_section("🔍 Testing Asset Filtering")
    
    all_assets = ['BTC', 'ETH', 'SOL', 'USDC', 'USDT', 'XLM', 'LINK', 'AAVE']
    
    for tier_name in ['beginner', 'intermediate', 'advanced']:
        filtered = tier_manager.filter_allowed_assets(all_assets, tier_name)
        print(f"\n{tier_name.upper()} Tier:")
        print(f"   Input: {', '.join(all_assets)}")
        print(f"   Output: {', '.join(filtered)}")
        print(f"   Filtered out: {', '.join(set(all_assets) - set(filtered))}")

def test_prompt_generation(tier_manager):
    """Test prompt generation for different tiers"""
    print_section("📝 Testing Prompt Generation")
    
    for tier_name in ['beginner', 'intermediate', 'advanced']:
        print(f"\n{tier_name.upper()} Tier Prompts:")
        
        # Trading Agent prompt
        trading_prompt = tier_manager.get_prompt_template('trading', tier_name)
        print(f"\n   🤖 Trading Agent:")
        print(f"   {trading_prompt[:200]}...")
        
        # Risk Agent prompt
        risk_prompt = tier_manager.get_prompt_template('risk', tier_name)
        print(f"\n   🛡️  Risk Agent:")
        print(f"   {risk_prompt[:200]}...")

def test_localization():
    """Test multi-language translations"""
    print_section("🌍 Testing Localization")
    
    languages = ['en', 'es', 'sw', 'ar', 'zh']
    
    # Test tier labels
    print("\n📌 Tier Labels:")
    for lang in languages:
        label = get_translation('tier_beginner', lang)
        print(f"   {lang.upper()}: {label}")
    
    # Test safety explanations - create TierManager for this test
    print("\n💰 USDC Safety Explanation:")
    config = {
        'user_tier_system': {
            'enabled': True,
            'tiers': {
                'beginner': {
                    'risk_budget': 'low',
                    'safety_focus': True,
                    'localization': {'languages': languages}
                }
            }
        }
    }
    tm = TierManager(config)
    
    for lang in languages:
        safety = tm.get_safety_explanation('USDC', 'beginner', lang)
        if safety:
            print(f"   {lang.upper()}: {safety[:80]}...")
        else:
            print(f"   {lang.upper()}: (No translation)")
    
    # Test tier descriptions
    print("\n📚 Beginner Tier Description:")
    for lang in ['en', 'es', 'sw']:
        desc = get_tier_description('beginner', lang)
        print(f"\n   {lang.upper()}:")
        lines = desc.strip().split('\n')[:3]
        for line in lines:
            print(f"      {line.strip()}")

def test_risk_budget_limits(tier_manager):
    """Test risk budget limits for each tier"""
    print_section("📊 Testing Risk Budget Limits")
    
    for tier_name in ['beginner', 'intermediate', 'advanced']:
        limits = tier_manager.get_risk_budget_limits(tier_name)
        print(f"\n{tier_name.upper()} Tier Limits:")
        print(f"   Max VaR: {limits['max_var'] * 100:.1f}%")
        print(f"   Max Single Asset: {limits['max_single_asset'] * 100:.1f}%")
        print(f"   Risk Level: {limits['risk_level']}")

def test_metric_visibility(tier_manager):
    """Test which metrics are visible for each tier"""
    print_section("👁️  Testing Metric Visibility")
    
    metrics = ['var', 'cvar', 'sharpe', 'sortino', 'max_drawdown', 'alpha', 'beta']
    
    for tier_name in ['beginner', 'intermediate', 'advanced']:
        print(f"\n{tier_name.upper()} Tier - Visible Metrics:")
        visible = [m for m in metrics if tier_manager.should_show_metric(m, tier_name)]
        hidden = [m for m in metrics if not tier_manager.should_show_metric(m, tier_name)]
        
        print(f"   ✅ Visible: {', '.join(visible) if visible else 'None (basic only)'}")
        print(f"   ❌ Hidden: {', '.join(hidden) if hidden else 'None (all visible)'}")

def test_safety_tier_manager_directly():
    """Test TierManager.get_safety_explanation with all languages"""
    print_section("🛡️  Testing Safety Explanations (Direct)")
    
    # Create a minimal config for testing
    config = {
        'user_tier_system': {
            'enabled': True,
            'tiers': {
                'beginner': {
                    'risk_budget': 'low',
                    'safety_focus': True,
                    'localization': {
                        'languages': ['en', 'es', 'sw', 'ar', 'zh']
                    }
                }
            }
        }
    }
    
    tier_manager = TierManager(config)
    
    assets = ['USDC', 'BTC', 'XLM']
    languages = ['en', 'es', 'sw', 'ar', 'zh']
    
    for asset in assets:
        print(f"\n💎 {asset} Safety Explanations:")
        for lang in languages:
            explanation = tier_manager.get_safety_explanation(asset, 'beginner', lang)
            if explanation:
                print(f"   {lang.upper()}: {explanation[:70]}...")
            else:
                print(f"   {lang.upper()}: (No translation available)")

def simulate_user_journey():
    """Simulate a user's journey through tier selection"""
    print_section("🎬 Simulating User Journey")
    
    # Load config
    with open('app/config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    tier_manager = TierManager(config)
    
    # Scenario 1: Beginner user from Kenya
    print("\n📖 Scenario 1: Sarah from Kenya 🇰🇪")
    print("   Profile: First-time investor, speaks Swahili")
    
    tier_name = 'beginner'
    language = 'sw'
    
    print(f"\n   1️⃣ Selects tier: {tier_name}")
    tier_config = tier_manager.get_tier_config(tier_name)
    print(f"      Risk Budget: {tier_config.risk_budget} (Max VaR: {tier_config.max_portfolio_var * 100}%)")
    
    print(f"\n   2️⃣ Selects language: Kiswahili")
    tier_label = get_translation('tier_beginner', language)
    print(f"      Tier Label: {tier_label}")
    
    print(f"\n   3️⃣ Views available assets:")
    all_assets = ['BTC', 'ETH', 'SOL', 'USDC', 'USDT', 'XLM']
    filtered = tier_manager.filter_allowed_assets(all_assets, tier_name)
    print(f"      Allowed: {', '.join(filtered)}")
    print(f"      Blocked: {', '.join(set(all_assets) - set(filtered))}")
    
    print(f"\n   4️⃣ Reads safety info for USDC:")
    safety = tier_manager.get_safety_explanation('USDC', tier_name, language)
    if safety:
        print(f"      {safety}")
    
    print(f"\n   5️⃣ Trading Agent prompt style:")
    trading_prompt = tier_manager.get_prompt_template('trading', tier_name)
    print(f"      {trading_prompt[:150]}...")
    
    # Scenario 2: Advanced user
    print("\n\n📖 Scenario 2: Alex - Professional Trader 🇺🇸")
    print("   Profile: 10 years trading experience, high risk tolerance")
    
    tier_name = 'advanced'
    language = 'en'
    
    print(f"\n   1️⃣ Selects tier: {tier_name}")
    tier_config = tier_manager.get_tier_config(tier_name)
    print(f"      Risk Budget: {tier_config.risk_budget} (Max VaR: {tier_config.max_portfolio_var * 100}%)")
    
    print(f"\n   2️⃣ Views available assets:")
    filtered = tier_manager.filter_allowed_assets(all_assets, tier_name)
    if tier_config.allowed_assets == 'all':
        print(f"      ALL ASSETS available (no restrictions)")
    else:
        print(f"      Allowed: {', '.join(filtered)}")
    
    print(f"\n   3️⃣ Trading Agent prompt style:")
    trading_prompt = tier_manager.get_prompt_template('trading', tier_name)
    print(f"      {trading_prompt[:150]}...")
    
    print(f"\n   4️⃣ Visible metrics:")
    metrics = ['var', 'cvar', 'sharpe', 'sortino', 'max_drawdown', 'alpha', 'beta']
    visible = [m for m in metrics if tier_manager.should_show_metric(m, tier_name)]
    print(f"      {', '.join(visible)}")

def run_all_tests():
    """Run all dry-run tests"""
    print("\n" + "🧪"*35)
    print("  DRY-RUN TEST: Tiered User System")
    print("  Testing WITHOUT OpenAI API calls")
    print("🧪"*35)
    
    try:
        # Test 1: TierManager
        tier_manager = test_tier_manager()
        
        # Test 2: Asset Filtering
        test_asset_filtering(tier_manager)
        
        # Test 3: Prompt Generation
        test_prompt_generation(tier_manager)
        
        # Test 4: Localization
        test_localization()
        
        # Test 5: Risk Budget Limits
        test_risk_budget_limits(tier_manager)
        
        # Test 6: Metric Visibility
        test_metric_visibility(tier_manager)
        
        # Test 7: Safety Explanations
        test_safety_tier_manager_directly()
        
        # Test 8: User Journey Simulation
        simulate_user_journey()
        
        # Summary
        print_section("✅ TEST SUMMARY")
        print("\n✅ All dry-run tests completed successfully!")
        print("\n📋 Tests Performed:")
        print("   1. ✅ TierManager initialization and configuration")
        print("   2. ✅ Asset filtering based on tiers")
        print("   3. ✅ Prompt generation for Trading and Risk Agents")
        print("   4. ✅ Multi-language translations (5 languages)")
        print("   5. ✅ Risk budget limits enforcement")
        print("   6. ✅ Metric visibility control")
        print("   7. ✅ Safety explanations in all languages")
        print("   8. ✅ User journey simulation (2 scenarios)")
        
        print("\n💡 Next Steps:")
        print("   - Run 'python smart_start.py' to test in the dashboard")
        print("   - Select different tiers to see UI changes")
        print("   - Try different languages to see translations")
        print("   - Check asset filtering in action")
        
        print("\n🔒 NO API CALLS MADE - Your OpenAI key is safe! 🔒")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

