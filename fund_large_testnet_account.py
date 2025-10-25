#!/usr/bin/env python3
"""
Fund Stellar Testnet Account with Large Amount

Stellar friendbot gives 10,000 XLM per call.
This script calls it multiple times to accumulate ~$1M worth of XLM.

Target: $1,000,000 USD
XLM Price: ~$0.31 USD
Required XLM: ~3,225,806 XLM
Friendbot calls needed: ~323 calls (10,000 XLM each)
"""

import asyncio
import os
import time
from stellar_sdk import Server, Keypair, TransactionBuilder, Network, Asset
from stellar_sdk.exceptions import BadRequestError
from dotenv import load_dotenv, set_key
import requests

load_dotenv()

# Configuration
HORIZON_URL = "https://horizon-testnet.stellar.org"
FRIENDBOT_URL = "https://friendbot.stellar.org"
TARGET_USD = 1_000_000  # $1 million
XLM_PRICE_USD = 0.31  # Approximate XLM price
TARGET_XLM = TARGET_USD / XLM_PRICE_USD  # ~3.2M XLM
FRIENDBOT_AMOUNT = 10_000  # XLM per friendbot call
CALLS_NEEDED = int(TARGET_XLM / FRIENDBOT_AMOUNT) + 1

print("=" * 70)
print("💰 Stellar Testnet Large Account Funding")
print("=" * 70)
print(f"Target Amount: ${TARGET_USD:,} USD")
print(f"XLM Price: ${XLM_PRICE_USD}")
print(f"Target XLM: {TARGET_XLM:,.0f} XLM")
print(f"Friendbot calls needed: {CALLS_NEEDED}")
print("=" * 70)
print()

def fund_with_friendbot(public_key: str) -> bool:
    """Fund account using friendbot"""
    try:
        response = requests.get(f"{FRIENDBOT_URL}?addr={public_key}", timeout=10)
        if response.status_code == 200:
            return True
        else:
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def get_xlm_balance(public_key: str) -> float:
    """Get current XLM balance"""
    try:
        server = Server(HORIZON_URL)
        account = server.accounts().account_id(public_key).call()
        for balance in account['balances']:
            if balance['asset_type'] == 'native':
                return float(balance['balance'])
        return 0.0
    except Exception as e:
        print(f"   ❌ Error getting balance: {e}")
        return 0.0

async def fund_large_account():
    """Fund account with multiple friendbot calls"""
    
    # Check if we have existing account
    stellar_public = os.getenv("STELLAR_PUBLIC")
    stellar_secret = os.getenv("STELLAR_SECRET")
    
    if not stellar_public or not stellar_secret:
        print("❌ No account found in .env")
        print("Creating new account...")
        
        # Generate new keypair
        keypair = Keypair.random()
        stellar_public = keypair.public_key
        stellar_secret = keypair.secret
        
        # Save to .env
        env_file = ".env"
        set_key(env_file, "STELLAR_PUBLIC", stellar_public)
        set_key(env_file, "STELLAR_SECRET", stellar_secret)
        
        print(f"✅ New account created:")
        print(f"   Public: {stellar_public}")
        print(f"   (Secret saved to .env)")
        print()
    else:
        print(f"✅ Using existing account:")
        print(f"   Public: {stellar_public}")
        print()
    
    # Initial balance
    initial_balance = get_xlm_balance(stellar_public)
    print(f"💰 Current balance: {initial_balance:,.4f} XLM (${initial_balance * XLM_PRICE_USD:,.2f} USD)")
    print()
    
    if initial_balance >= TARGET_XLM:
        print(f"✅ Account already has enough XLM!")
        print(f"   Current: {initial_balance:,.0f} XLM")
        print(f"   Target: {TARGET_XLM:,.0f} XLM")
        return
    
    # Calculate remaining calls needed
    remaining_xlm = TARGET_XLM - initial_balance
    calls_needed = int(remaining_xlm / FRIENDBOT_AMOUNT) + 1
    
    print(f"🔄 Need {calls_needed} more friendbot calls to reach target")
    print(f"⏱️  Estimated time: ~{calls_needed * 3} seconds")
    print()
    
    confirm = input("Continue? (yes/no): ")
    if confirm.lower() not in ['yes', 'y']:
        print("❌ Cancelled")
        return
    
    print()
    print("🚀 Starting funding process...")
    print()
    
    success_count = 0
    fail_count = 0
    
    for i in range(calls_needed):
        print(f"📞 Call {i+1}/{calls_needed}...", end=" ", flush=True)
        
        success = fund_with_friendbot(stellar_public)
        
        if success:
            success_count += 1
            print("✅")
        else:
            fail_count += 1
            print("❌")
        
        # Show progress every 10 calls
        if (i + 1) % 10 == 0:
            current_balance = get_xlm_balance(stellar_public)
            current_usd = current_balance * XLM_PRICE_USD
            progress = (current_balance / TARGET_XLM) * 100
            print(f"   💰 Progress: {current_balance:,.0f} XLM (${current_usd:,.2f} USD) - {progress:.1f}%")
            print()
        
        # Rate limiting: wait 2-3 seconds between calls
        if i < calls_needed - 1:
            await asyncio.sleep(2.5)
    
    print()
    print("=" * 70)
    print("📊 Funding Complete!")
    print("=" * 70)
    
    # Final balance
    final_balance = get_xlm_balance(stellar_public)
    final_usd = final_balance * XLM_PRICE_USD
    
    print(f"Initial balance: {initial_balance:,.4f} XLM")
    print(f"Final balance:   {final_balance:,.4f} XLM")
    print(f"Added:           {final_balance - initial_balance:,.4f} XLM")
    print()
    print(f"💵 USD Value: ${final_usd:,.2f} USD")
    print()
    print(f"✅ Successful calls: {success_count}")
    print(f"❌ Failed calls: {fail_count}")
    print()
    
    if final_balance >= TARGET_XLM:
        print("🎉 Target reached!")
    else:
        shortfall = TARGET_XLM - final_balance
        print(f"⚠️  Short by {shortfall:,.0f} XLM (${shortfall * XLM_PRICE_USD:,.2f} USD)")
        print(f"   You can run this script again to add more.")
    
    print()
    print("📝 Account saved in .env file")
    print(f"   Public Key: {stellar_public}")
    print()
    print("🚀 You can now use this account in your trading system!")

if __name__ == "__main__":
    try:
        asyncio.run(fund_large_account())
    except KeyboardInterrupt:
        print("\n\n❌ Interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

