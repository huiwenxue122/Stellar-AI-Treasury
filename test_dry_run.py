#!/usr/bin/env python3
"""
Dry-run test to debug trading issues without calling OpenAI API
"""
import asyncio
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from stellar.assets import AssetManager
from stellar.horizon import Horizon
import yaml

async def test_simulated_trading():
    """Test simulated trading without API calls"""
    
    print("=" * 60)
    print("🧪 DRY-RUN TEST: Simulated Trading")
    print("=" * 60)
    
    # Create a minimal AssetManager for testing
    class MockAssetManager:
        def __init__(self):
            self.simulation_mode = True
            self.simulated_balances = {}
            self.cost_basis = {}
            self.assets = {}
        
        def update_simulated_trade(self, asset: str, action: str, usd_amount: float, price: float) -> bool:
            """Simplified version of update_simulated_trade for testing"""
            if not self.simulation_mode:
                return False
            
            # Ensure all numeric inputs are float
            usd_amount = float(usd_amount)
            price = float(price)
            
            asset_lower = asset.lower()
            
            # Calculate asset amount
            asset_amount = usd_amount / price if price > 0 else 0
            
            # Get XLM price
            xlm_price = 0.31
            xlm_amount = usd_amount / xlm_price
            
            # Initialize balances if needed
            if 'xlm' not in self.simulated_balances:
                self.simulated_balances['xlm'] = 3200000  # Start with $1M worth
            if asset_lower not in self.simulated_balances:
                self.simulated_balances[asset_lower] = 0.0
            
            if action == 'BUY':
                # Check if we have enough XLM (ensure types are float)
                xlm_balance = float(self.simulated_balances['xlm'])
                if xlm_balance < xlm_amount:
                    print(f"   ❌ Insufficient XLM! Need {xlm_amount:.2f}, have {xlm_balance:.2f}")
                    return False
                
                # Update cost basis (weighted average)
                old_quantity = float(self.simulated_balances[asset_lower])
                old_cost = float(self.cost_basis.get(asset_lower, price))
                new_quantity = old_quantity + asset_amount
                
                # Weighted average cost = (old_cost * old_qty + new_cost * new_qty) / total_qty
                if new_quantity > 0:
                    self.cost_basis[asset_lower] = (old_cost * old_quantity + price * asset_amount) / new_quantity
                
                # Decrease XLM (cash)
                self.simulated_balances['xlm'] -= xlm_amount
                # Increase asset
                self.simulated_balances[asset_lower] = new_quantity
                
                print(f"   📊 Simulated: XLM -{xlm_amount:.2f} | {asset} +{asset_amount:.4f}")
                print(f"      Cost Basis: ${self.cost_basis[asset_lower]:.2f} | Remaining XLM: {self.simulated_balances['xlm']:.2f}")
                return True
                
            elif action == 'SELL':
                # Check if we have enough of the asset (ensure types are float)
                asset_balance = float(self.simulated_balances[asset_lower])
                if asset_balance < asset_amount:
                    print(f"   ❌ Insufficient {asset}! Need {asset_amount:.4f}, have {asset_balance:.4f}")
                    return False
                
                # Increase XLM (cash)
                self.simulated_balances['xlm'] += xlm_amount
                # Decrease asset
                self.simulated_balances[asset_lower] -= asset_amount
                print(f"   📊 Simulated: XLM +{xlm_amount:.2f} | {asset} -{asset_amount:.4f}")
                print(f"      New XLM: {self.simulated_balances['xlm']:.2f}")
                return True
            
            return False
    
    asset_manager = MockAssetManager()
    
    print("\n1️⃣ Testing initial balance setup...")
    print(f"   Simulated balances: {asset_manager.simulated_balances}")
    
    # Test BUY BTC
    print("\n2️⃣ Testing BUY BTC for $100,000...")
    result = asset_manager.update_simulated_trade(
        asset='BTC',
        action='BUY',
        usd_amount=100000.0,
        price=97500.0
    )
    print(f"   Result: {result}")
    print(f"   Simulated balances: {asset_manager.simulated_balances}")
    
    # Test BUY ETH
    print("\n3️⃣ Testing BUY ETH for $50,000...")
    result = asset_manager.update_simulated_trade(
        asset='ETH',
        action='BUY',
        usd_amount=50000.0,
        price=3500.0
    )
    print(f"   Result: {result}")
    print(f"   Simulated balances: {asset_manager.simulated_balances}")
    
    # Test insufficient funds
    print("\n4️⃣ Testing insufficient funds (buy $10M BTC)...")
    result = asset_manager.update_simulated_trade(
        asset='BTC',
        action='BUY',
        usd_amount=10000000.0,
        price=97500.0
    )
    print(f"   Result: {result}")
    print(f"   Simulated balances: {asset_manager.simulated_balances}")
    
    # Test SELL
    print("\n5️⃣ Testing SELL 0.5 BTC...")
    result = asset_manager.update_simulated_trade(
        asset='BTC',
        action='SELL',
        usd_amount=48750.0,  # 0.5 BTC at $97,500
        price=97500.0
    )
    print(f"   Result: {result}")
    print(f"   Simulated balances: {asset_manager.simulated_balances}")
    
    print("\n" + "=" * 60)
    print("✅ DRY-RUN TEST COMPLETED")
    print("=" * 60)

if __name__ == '__main__':
    asyncio.run(test_simulated_trading())

