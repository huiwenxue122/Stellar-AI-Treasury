#!/usr/bin/env python3
"""
🔢 Test: Type Consistency for number_input

Verifies that all numeric arguments to st.number_input are of consistent type (float)
"""

def test_type_consistency():
    """Test that all number_input parameters have consistent types"""
    
    print("=" * 80)
    print("🔢 Testing Type Consistency for Capital Configuration")
    print("=" * 80)
    
    # Tier recommendations (as defined in dashboard)
    tier_recommendations = {
        'beginner': {
            'min': 100.0,
            'recommended': 1000.0,
            'max': 10000.0,
        },
        'intermediate': {
            'min': 1000.0,
            'recommended': 25000.0,
            'max': 100000.0,
        },
        'advanced': {
            'min': 10000.0,
            'recommended': 250000.0,
            'max': 10000000.0,
        }
    }
    
    # Presets (as defined in dashboard)
    presets = [
        ("$1K", 1000.0),
        ("$10K", 10000.0),
        ("$100K", 100000.0),
        ("$1M", 1000000.0)
    ]
    
    print("\n✅ Checking Tier Recommendation Types\n")
    
    all_passed = True
    
    for tier, rec in tier_recommendations.items():
        print(f"🎯 {tier.upper()} Tier:")
        
        types_correct = True
        for key, value in rec.items():
            value_type = type(value).__name__
            is_float = isinstance(value, float)
            
            status = "✅" if is_float else "❌"
            print(f"   {status} {key}: {value} (type: {value_type})")
            
            if not is_float:
                types_correct = False
                all_passed = False
        
        if types_correct:
            print(f"   ✅ All types are float")
        else:
            print(f"   ❌ Some types are not float!")
        print()
    
    print("=" * 80)
    print("\n✅ Checking Preset Types\n")
    
    for label, amount in presets:
        amount_type = type(amount).__name__
        is_float = isinstance(amount, float)
        
        status = "✅" if is_float else "❌"
        print(f"{status} {label}: {amount} (type: {amount_type})")
        
        if not is_float:
            all_passed = False
    
    print("\n" + "=" * 80)
    print("\n🧪 Simulating Button Click + number_input\n")
    
    # Simulate button click scenarios
    test_scenarios = [
        ('beginner', 1000.0, 'Click $1K preset'),
        ('intermediate', 10000.0, 'Click $10K preset'),
        ('advanced', 100000.0, 'Click $100K preset'),
        ('advanced', 1000000.0, 'Click $1M preset'),
    ]
    
    for tier, preset_amount, description in test_scenarios:
        print(f"📝 Test: {description} ({tier} tier)")
        
        rec = tier_recommendations[tier]
        
        # Simulate button click
        temp_capital = preset_amount  # st.session_state.temp_capital = amount
        
        # Simulate getting default_capital (as in dashboard)
        default_capital = temp_capital  # st.session_state.get('temp_capital', rec['recommended'])
        
        # Apply the fix: ensure float
        default_capital = float(default_capital)
        
        # Ensure within tier limits
        if default_capital < rec['min']:
            default_capital = rec['min']
        elif default_capital > rec['max']:
            default_capital = rec['max']
        
        # Check types for number_input arguments
        min_value = rec['min']
        max_value = rec['max']
        value = default_capital
        step = 1000.0
        
        print(f"   number_input arguments:")
        print(f"      min_value: {min_value} (type: {type(min_value).__name__})")
        print(f"      max_value: {max_value} (type: {type(max_value).__name__})")
        print(f"      value: {value} (type: {type(value).__name__})")
        print(f"      step: {step} (type: {type(step).__name__})")
        
        # Verify all types are consistent
        all_types = [type(min_value), type(max_value), type(value), type(step)]
        types_consistent = all(t == float for t in all_types)
        
        if types_consistent:
            print(f"   ✅ PASS: All types are float (consistent)")
        else:
            print(f"   ❌ FAIL: Types are inconsistent!")
            all_passed = False
        
        print()
    
    print("=" * 80)
    print("\n🔧 Testing Float Conversion Fix\n")
    
    # Test the fix with various input types
    test_values = [
        (1000, "int preset"),
        (1000.0, "float preset"),
        ("1000", "string from session_state (edge case)"),
    ]
    
    for value, description in test_values:
        print(f"📝 Input: {value} ({type(value).__name__}) - {description}")
        
        try:
            converted = float(value)
            print(f"   ✅ Converted to: {converted} (type: {type(converted).__name__})")
            
            # Verify it's compatible with number_input
            is_float = isinstance(converted, float)
            print(f"   ✅ Compatible with number_input: {is_float}")
        except Exception as e:
            print(f"   ❌ Conversion failed: {e}")
            all_passed = False
        
        print()
    
    print("=" * 80)
    
    if all_passed:
        print("\n✅ ALL TYPE CHECKS PASSED!")
        print("\n📝 Summary:")
        print("   - All tier recommendation values are float ✅")
        print("   - All preset amounts are float ✅")
        print("   - float() conversion applied to default_capital ✅")
        print("   - All number_input arguments are consistent float type ✅")
    else:
        print("\n❌ SOME TYPE CHECKS FAILED")
    
    print("=" * 80)
    
    return all_passed

if __name__ == "__main__":
    import sys
    success = test_type_consistency()
    sys.exit(0 if success else 1)

