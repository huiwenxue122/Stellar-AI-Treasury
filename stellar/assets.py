import asyncio
import statistics
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from stellar_sdk import Asset
from .horizon import Horizon
from .price_oracle import PriceOracle

@dataclass
class AssetInfo:
    code: str
    issuer: Optional[str]
    balance: float = 0.0
    price_usd: float = 0.0
    volatility: float = 0.0

class AssetManager:
    def __init__(self, horizon: Horizon, config: dict):
        self.horizon = horizon
        self.config = config
        self.assets: Dict[str, AssetInfo] = {}
        self.price_history: Dict[str, List[float]] = {}
        
        # 创建价格预言机
        self.price_oracle = PriceOracle(horizon, config)
        
        # 🔧 SIMULATION MODE: Track simulated balances
        self.simulated_balances: Dict[str, float] = {}
        self.simulation_mode = True  # Set to False to use only real chain data
        
        # 💰 COST BASIS TRACKING: Record purchase prices to avoid valuation bugs
        self.cost_basis: Dict[str, float] = {}  # {asset: average_cost_per_unit}
        self.use_cost_basis = True  # Use cost basis instead of market price for portfolio valuation
        
        # 💰 CAPITAL TRACKING: User's initial capital (default $1M, user-configurable)
        self.initial_capital_usd: float = 1000000.0
        
        self._initialize_assets()
    
    def set_initial_capital_usd(self, capital_usd: float, xlm_price: float):
        """💰 Set user's initial capital and reset balances accordingly"""
        self.initial_capital_usd = capital_usd
        
        # Calculate XLM amount at the given (fixed) price
        xlm_amount = capital_usd / xlm_price
        
        # 🔧 IMPORTANT: Clear ALL simulated balances and reset with new XLM amount
        # This ensures any previous initialization is overwritten
        self.simulated_balances.clear()  # Clear existing balances
        self.simulated_balances['xlm'] = xlm_amount  # Set new XLM balance
        
        # Also clear and reset cost basis
        self.cost_basis.clear()
        self.cost_basis['xlm'] = xlm_price
        
        print(f"✅ Initial capital set:")
        print(f"   ${capital_usd:,.2f} USD → {xlm_amount:,.2f} XLM @ ${xlm_price}")
        print(f"   Simulated balances reset: {self.simulated_balances}")
        
        return xlm_amount
    
    def reset_simulated_balances(self):
        """Reset all simulated balances to start fresh"""
        self.simulated_balances = {}
        print("✅ Simulated balances have been reset")
    
    def _initialize_assets(self):
        """Initialize asset configurations from config"""
        for asset_name, asset_config in self.config['assets'].items():
            self.assets[asset_name] = AssetInfo(
                code=asset_config['code'],
                issuer=asset_config.get('issuer'),
                balance=0.0,
                price_usd=0.0,
                volatility=0.0
            )
            self.price_history[asset_name] = []
    
    async def get_asset_balance(self, account_id: str, asset_name: str) -> float:
        """Get balance for a specific asset"""
        
        # 🔧 SIMULATION MODE: Return simulated balance if it exists
        if self.simulation_mode and asset_name in self.simulated_balances:
            return self.simulated_balances[asset_name]
        
        try:
            account = await self.horizon._get(f"/accounts/{account_id}")
            asset_info = self.assets[asset_name]
            
            # 🔧 NEW LOGIC: Calculate XLM needed based on user's configured capital
            # This makes the simulated balance realistic and user-configurable
            TARGET_USD = self.initial_capital_usd  # Use user's configured capital
            
            for balance in account.get('balances', []):
                if balance['asset_type'] == 'native' and asset_info.code == 'XLM':
                    actual_balance = float(balance['balance'])
                    
                    # Initialize simulated balance if not exists
                    if self.simulation_mode and asset_name not in self.simulated_balances:
                        # 🔒 FIXED XLM PRICE: Use consistent $0.31 for initialization
                        # This ensures portfolio value = user's target regardless of API price
                        FIXED_XLM_PRICE = 0.31
                        
                        # Calculate XLM needed for target USD at fixed price
                        xlm_needed = TARGET_USD / FIXED_XLM_PRICE
                        
                        # Store in simulated balances
                        self.simulated_balances[asset_name] = xlm_needed
                        
                        # Also set cost basis
                        self.cost_basis['xlm'] = FIXED_XLM_PRICE
                        
                        # Also get real-time price for information (not used in calculations)
                        try:
                            real_price = await self.get_current_price(asset_name, 'USDC')
                            if real_price <= 0:
                                real_price = FIXED_XLM_PRICE
                        except:
                            real_price = FIXED_XLM_PRICE
                        
                        print(f"✅ Initialized simulated XLM balance:")
                        print(f"   Real testnet balance: {actual_balance:.2f} XLM")
                        print(f"   Real-time XLM price: ${real_price:.4f} (for info only)")
                        print(f"   Fixed XLM price: ${FIXED_XLM_PRICE:.2f} (used for calculations)")
                        print(f"   Simulated balance: {xlm_needed:.2f} XLM (=${TARGET_USD:,.2f} @ ${FIXED_XLM_PRICE})")
                        
                        return xlm_needed
                    else:
                        return self.simulated_balances[asset_name]
                    
                elif (balance.get('asset_code') == asset_info.code and 
                      balance.get('asset_issuer') == asset_info.issuer):
                    return float(balance['balance'])
            
            return 0.0
        except Exception as e:
            print(f"Error getting balance for {asset_name}: {e}")
            return 0.0
    
    async def get_current_price(self, asset_name: str, base_asset: str = "USDC") -> float:
        """Get current price of asset in base currency"""
        try:
            asset_info = self.assets[asset_name]
            
            # 使用价格预言机获取价格
            price = await self.price_oracle.get_price(asset_info.code, base_asset)
            
            # Store price in history for volatility calculation
            if asset_name not in self.price_history:
                self.price_history[asset_name] = []
            
            if price > 0:
                self.price_history[asset_name].append(price)
                if len(self.price_history[asset_name]) > 100:  # Keep last 100 prices
                    self.price_history[asset_name] = self.price_history[asset_name][-100:]
            
            return price
        except Exception as e:
            print(f"Error getting price for {asset_name}: {e}")
            return 0.0
    
    def calculate_volatility(self, asset_name: str, window: int = 20) -> float:
        """Calculate volatility using standard deviation of returns"""
        prices = self.price_history.get(asset_name, [])
        if len(prices) < window:
            return 0.0
        
        recent_prices = prices[-window:]
        returns = []
        
        for i in range(1, len(recent_prices)):
            if recent_prices[i-1] != 0:
                ret = (recent_prices[i] - recent_prices[i-1]) / recent_prices[i-1]
                returns.append(ret)
        
        if len(returns) < 2:
            return 0.0
        
        return statistics.stdev(returns) * (252 ** 0.5)  # Annualized volatility
    
    def update_simulated_trade(self, asset: str, action: str, usd_amount: float, price: float):
        """Update simulated balances after a trade
        
        Args:
            asset: Asset code (e.g., 'BTC', 'ETH')
            action: 'BUY' or 'SELL'
            usd_amount: USD value of the trade
            price: Current price of the asset in USD
        """
        if not self.simulation_mode:
            return False
        
        try:
            # Ensure all numeric inputs are float
            usd_amount = float(usd_amount)
            price = float(price)
        except (TypeError, ValueError) as e:
            print(f"   ❌ Invalid trade parameters: usd_amount={usd_amount}, price={price}, error={e}")
            return False
        
        asset_lower = asset.lower()
        
        # Calculate asset amount
        asset_amount = usd_amount / price if price > 0 else 0
        
        # 🔒 FIXED XLM PRICE: Use the same fixed price as portfolio valuation
        # This ensures consistency across all calculations
        FIXED_XLM_PRICE = 0.31
        xlm_amount = usd_amount / FIXED_XLM_PRICE
        
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
        
        else:
            print(f"   ⚠️  Unknown action '{action}' for {asset} (only BUY/SELL supported in simulation)")
            return False
    
    async def update_asset_data(self, account_id: str):
        """Update all asset balances and prices"""
        for asset_name in self.assets:
            balance = await self.get_asset_balance(account_id, asset_name)
            price = await self.get_current_price(asset_name)
            volatility = self.calculate_volatility(asset_name)
            
            self.assets[asset_name].balance = balance
            self.assets[asset_name].price_usd = price
            self.assets[asset_name].volatility = volatility
    
    def get_portfolio_value_usd(self) -> float:
        """Calculate total portfolio value in USD
        
        NEW APPROACH:
        - XLM (cash): Always valued at FIXED $0.31 (prevents fluctuations)
        - Crypto assets: Valued at COST BASIS (what we paid, not current market price)
        - USDC: Always 1:1 with USD
        
        This ensures portfolio value ONLY changes when:
        1. We buy/sell assets (real trades)
        2. NOT when API returns different prices
        """
        total_value = 0.0
        
        if self.simulation_mode and self.use_cost_basis:
            # 🔒 FIXED XLM PRICE: Prevents portfolio value from jumping
            # This is the price used when initializing the simulated balance
            FIXED_XLM_PRICE = 0.31
            
            debug_values = []  # For tracking portfolio composition
            for asset_name, balance in self.simulated_balances.items():
                balance = float(balance)  # Ensure it's a number
                if balance > 0:
                    if asset_name == 'xlm':
                        # XLM is cash, valued at FIXED $0.31
                        # This ensures portfolio value doesn't fluctuate artificially
                        asset_value = balance * FIXED_XLM_PRICE
                        total_value += asset_value
                        debug_values.append(f"{asset_name.upper()}: {balance:.2f} @ ${FIXED_XLM_PRICE} = ${asset_value:.2f}")
                    elif asset_name == 'usdc':
                        # USDC is 1:1 with USD
                        asset_value = balance
                        total_value += asset_value
                        debug_values.append(f"{asset_name.upper()}: ${balance:.2f}")
                    else:
                        # Use cost basis (what we paid) not current market price
                        cost_price = float(self.cost_basis.get(asset_name, 0))
                        asset_value = balance * cost_price
                        total_value += asset_value
                        debug_values.append(f"{asset_name.upper()}: {balance:.6f} @ ${cost_price:.2f} = ${asset_value:.2f}")
            
            # Print debug info occasionally (every 10th call)
            import random
            if random.random() < 0.1 and debug_values:
                print(f"\n💰 Portfolio Composition:")
                for line in debug_values:
                    print(f"   {line}")
                print(f"   📊 Total: ${total_value:,.2f}\n")
        else:
            # Use real balances and market prices
            for asset_name, asset_info in self.assets.items():
                if asset_name == 'usdc':
                    total_value += asset_info.balance
                else:
                    total_value += asset_info.balance * asset_info.price_usd
        
        return total_value
    
    def get_usdc_allocation(self) -> float:
        """Get current USDC allocation percentage"""
        usdc_value = self.assets['usdc'].balance
        total_value = self.get_portfolio_value_usd()
        if total_value == 0:
            return 0.0
        return (usdc_value / total_value) * 100
    
    def should_convert_to_usdc(self, volatility_threshold: float = 0.3) -> bool:
        """Determine if portfolio should be converted to USDC based on volatility"""
        # Check if any non-USDC asset has high volatility
        for asset_name, asset_info in self.assets.items():
            if asset_name != 'usdc' and asset_info.volatility > volatility_threshold:
                return True
        return False
    
    def should_convert_from_usdc(self, volatility_threshold: float = 0.15) -> bool:
        """Determine if USDC should be converted back to assets based on low volatility"""
        # Check if all non-USDC assets have low volatility
        for asset_name, asset_info in self.assets.items():
            if asset_name != 'usdc' and asset_info.volatility > volatility_threshold:
                return False
        return True
    
    def get_asset_to_convert(self) -> Optional[str]:
        """Get the asset with highest volatility to convert to USDC"""
        max_vol = 0.0
        target_asset = None
        
        for asset_name, asset_info in self.assets.items():
            if (asset_name != 'usdc' and 
                asset_info.balance > 0 and 
                asset_info.volatility > max_vol):
                max_vol = asset_info.volatility
                target_asset = asset_name
        
        return target_asset
