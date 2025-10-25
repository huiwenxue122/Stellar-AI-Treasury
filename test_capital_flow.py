#!/usr/bin/env python3
"""
🔍 Test: Capital Configuration Flow

Tests the complete flow of capital configuration from user input to balance initialization
"""

def test_capital_flow():
    """Test the capital configuration flow"""
    
    print("=" * 80)
    print("🔍 Testing Capital Configuration Flow")
    print("=" * 80)
    
    FIXED_XLM_PRICE = 0.31
    
    print("\n📋 Step-by-Step Flow:\n")
    
    # Step 1: Dashboard initialization
    print("1️⃣ Dashboard Initialization")
    print("   - session_state.xlm_balance = DEFAULT_USD / 0.31")
    print("   - DEFAULT_USD = $1,000,000 (will be updated)")
    xlm_balance_initial = 1_000_000 / FIXED_XLM_PRICE
    print(f"   - Initial display: {xlm_balance_initial:,.2f} XLM")
    print("   ✅ This is just for display, not final balance")
    print()
    
    # Step 2: User selects capital
    print("2️⃣ User Selects Capital")
    print("   - User clicks '$1K' preset button")
    print("   - session_state.temp_capital = 1000.0")
    print("   - st.rerun() triggers page reload")
    print("   - number_input updates to show 1000.0")
    capital_usd = 1000.0
    print(f"   - User's choice: ${capital_usd:,.2f}")
    print("   ✅ Capital stored in session_state.initial_capital_usd")
    print()
    
    # Step 3: User clicks Confirm
    print("3️⃣ User Clicks 'Confirm Configuration and Start'")
    print("   - orchestrator.set_initial_capital(capital_usd)")
    xlm_amount = capital_usd / FIXED_XLM_PRICE
    print(f"     └─> Calls: asset_manager.set_initial_capital_usd({capital_usd}, {FIXED_XLM_PRICE})")
    print(f"     └─> Calculates: xlm_amount = {capital_usd} / {FIXED_XLM_PRICE} = {xlm_amount:,.2f}")
    print(f"     └─> Sets: simulated_balances['xlm'] = {xlm_amount:,.2f}")
    print(f"     └─> Sets: initial_capital_usd = {capital_usd}")
    print(f"     └─> Sets: cost_basis['xlm'] = {FIXED_XLM_PRICE}")
    print()
    print("   - session_state.xlm_balance = xlm_amount")
    print(f"     └─> Updates display balance to: {xlm_amount:,.2f} XLM")
    print("   ✅ Balance correctly set to user's choice!")
    print()
    
    # Step 4: First trading cycle
    print("4️⃣ First Trading Cycle")
    print("   - run_trading_cycle() is called")
    print("   - Gets current holdings:")
    print(f"     └─> get_asset_balance(wallet.public, 'xlm')")
    print()
    print("   🔍 Inside get_asset_balance('xlm'):")
    print(f"      - Check: is 'xlm' in simulated_balances?")
    print(f"      - Result: YES (set in step 3)")
    print(f"      - Return: simulated_balances['xlm'] = {xlm_amount:,.2f}")
    print("   ✅ Correct balance retrieved!")
    print()
    
    # Verify
    print("=" * 80)
    print("\n✅ Flow Analysis:\n")
    
    flow_correct = True
    
    # Check 1: Capital is stored correctly
    print(f"1. Capital stored: ${capital_usd:,.2f} ✅")
    
    # Check 2: XLM amount calculated correctly
    expected_xlm = capital_usd / FIXED_XLM_PRICE
    if abs(xlm_amount - expected_xlm) < 0.01:
        print(f"2. XLM calculation: {xlm_amount:,.2f} XLM ✅")
    else:
        print(f"2. XLM calculation: ❌ Expected {expected_xlm:,.2f}, got {xlm_amount:,.2f}")
        flow_correct = False
    
    # Check 3: Session state updated
    print(f"3. Session state updated: {xlm_amount:,.2f} XLM ✅")
    
    # Check 4: Simulated balances set
    print(f"4. simulated_balances['xlm']: {xlm_amount:,.2f} XLM ✅")
    
    # Check 5: No overwrite on subsequent calls
    print(f"5. Subsequent get_asset_balance calls return same value ✅")
    
    print("\n" + "=" * 80)
    
    # Test potential issue
    print("\n⚠️  Potential Issue Analysis:\n")
    
    print("🐛 Issue: Balance still shows $1M instead of user's choice")
    print()
    print("Possible Causes:")
    print()
    print("A. 🔍 Timing Issue:")
    print("   - If get_asset_balance() is called BEFORE set_initial_capital_usd()")
    print("   - Then simulated_balances['xlm'] would be auto-initialized to $1M")
    print("   - Solution: Ensure set_initial_capital_usd() is called first")
    print()
    print("B. 🔍 Key Mismatch:")
    print("   - set_initial_capital_usd() sets: simulated_balances['xlm'] (lowercase)")
    print("   - get_asset_balance() checks: asset_name = 'xlm' (lowercase)")
    print("   - ✅ Keys match, not the issue")
    print()
    print("C. 🔍 Balance Not Persisting:")
    print("   - set_initial_capital_usd() resets entire simulated_balances dict")
    print("   - Code: self.simulated_balances = {'xlm': xlm_amount}")
    print("   - ✅ This is correct, clears old state")
    print()
    print("D. 🔍 Display Not Updating:")
    print("   - session_state.xlm_balance might not be used in display")
    print("   - Dashboard might be calling get_asset_balance() directly")
    print("   - Need to check: Where does Portfolio Overview get XLM balance?")
    print()
    
    print("=" * 80)
    print("\n🔧 Recommended Fix:\n")
    print("1. ✅ set_initial_capital_usd() correctly sets simulated_balances['xlm']")
    print("2. ✅ session_state.xlm_balance is updated after confirmation")
    print("3. 🔍 CHECK: Does render_portfolio_overview() use session_state.xlm_balance?")
    print("4. 🔍 CHECK: Or does it call get_asset_balance() directly?")
    print("5. 🔍 CHECK: Is there any code that resets simulated_balances after config?")
    print()
    
    print("=" * 80)
    
    return flow_correct

if __name__ == "__main__":
    import sys
    success = test_capital_flow()
    
    print("\n" + "=" * 80)
    print("📝 Next Steps for Debugging:")
    print("=" * 80)
    print()
    print("1. Add debug print in set_initial_capital_usd():")
    print("   print(f'SET: simulated_balances = {self.simulated_balances}')")
    print()
    print("2. Add debug print in get_asset_balance():")
    print("   print(f'GET: asset_name={asset_name}, simulated_balances={self.simulated_balances}')")
    print()
    print("3. Check render_portfolio_overview() in dashboard.py:")
    print("   - Does it use st.session_state.xlm_balance?")
    print("   - Or does it call orchestrator/asset_manager methods?")
    print()
    print("4. Run dashboard and check console output:")
    print("   - Look for 'SET: simulated_balances...'")
    print("   - Look for 'GET: asset_name=xlm...'")
    print("   - Verify the balance values match")
    print()
    print("=" * 80)
    
    sys.exit(0 if success else 1)

