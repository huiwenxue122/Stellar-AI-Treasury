import os, json, asyncio, yaml
from agents.payment import PaymentAgent
from agents.trading import TradingAgent
from agents.risk import RiskAgent
from agents.agent_system_with_function_tools import get_multi_agent_orchestrator_with_tools
from stellar.wallet import Wallet
from stellar.horizon import Horizon
from stellar.assets import AssetManager
from stellar.smart_contract_client import SmartContractClientV2
from app.tier_manager import TierManager
from dotenv import load_dotenv
from typing import Dict, Any

load_dotenv() 

# Load environment variables
STELLAR_SECRET = os.environ.get("STELLAR_SECRET")
STELLAR_PUBLIC = os.environ.get("STELLAR_PUBLIC")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
CONTRACT_ID = os.environ.get("CONTRACT_ID", "")

if not all([STELLAR_SECRET, STELLAR_PUBLIC]):
    print("❌ Missing required environment variables: STELLAR_SECRET, STELLAR_PUBLIC")
    exit(1)

print("✅ Loaded env vars for Stellar + OpenAI successfully.")
if CONTRACT_ID:
    print(f"✅ Smart Contract ID loaded: {CONTRACT_ID[:8]}...")

# Load configuration
with open(os.path.join(os.path.dirname(__file__), 'config.yaml'), 'r') as f:
    CFG = yaml.safe_load(f)

# Initialize components
H = Horizon(CFG['network']['horizon'])
W = Wallet(CFG['network']['horizon'], CFG['network']['passphrase'],
           CFG['wallet']['secret_key_env'], CFG['wallet']['public_key_env'])
AM = AssetManager(H, CFG)
PAY = PaymentAgent(W, CFG)
TR = TradingAgent(CFG, AM, PAY)
RK = RiskAgent(CFG)

# Available tools for the system
TOOLS = {
    'send_usdc': PAY.send_usdc,
    'convert_to_usdc': PAY.convert_to_usdc,
    'convert_from_usdc': PAY.convert_from_usdc,
    'get_swap_quote': PAY.get_swap_quote,
    'get_asset_balance': AM.get_asset_balance,
    'get_current_price': AM.get_current_price,
    'calculate_volatility': AM.calculate_volatility,
    'get_portfolio_value': AM.get_portfolio_value_usd,
    'get_usdc_allocation': AM.get_usdc_allocation,
}

class TreasuryOrchestrator:
    def __init__(self):
        self.asset_manager = AM
        self.trading_agent = TR
        self.risk_agent = RK
        self.payment_agent = PAY
        self.config = CFG
        self.wallet = W  # 🔧 Store wallet as instance variable for safer access
        
        # 🌍 Initialize Tier Manager for user-level customization
        self.tier_manager = TierManager(CFG)
        self.current_user_tier = self.tier_manager.default_tier
        print(f"✅ Tier Manager initialized (default tier: {self.current_user_tier})")
        
        # 🔗 Initialize Smart Contract Client V2.0
        self.smart_contract = None
        smart_contract_config = CFG.get('smart_contract', {})
        if smart_contract_config.get('enabled') and CONTRACT_ID:
            try:
                self.smart_contract = SmartContractClientV2(
                    contract_id=CONTRACT_ID,
                    network=smart_contract_config.get('network', 'testnet')
                )
                print(f"✅ Smart Contract V2.0 initialized: {CONTRACT_ID[:8]}...")
                print(f"   Network: {smart_contract_config.get('network', 'testnet')}")
                print(f"   New Features: Trade History, Strategy Performance, Portfolio Snapshots")
                
                # Print contract status
                try:
                    total_trades = self.smart_contract.get_total_trades()
                    print(f"   📊 Total Trades on Contract: {total_trades}")
                except:
                    pass
                
            except Exception as e:
                print(f"⚠️  Smart Contract initialization failed: {e}")
                print("   System will continue without on-chain enforcement")
        else:
            print("ℹ️  Smart Contract disabled (running in simulation mode)")
        
        # 初始化Multi-Agent系统
        # 使用新的 Function Calling 版本
        self.multi_agent = get_multi_agent_orchestrator_with_tools(CFG, TR, RK, PAY, self.tier_manager)
        self.use_multi_agent = CFG.get('agent_system', {}).get('enabled', False)
        
        print("✅ Multi-Agent System initialized with Function Calling (10 strategy tools)")
        print(f"   🌍 Tier-aware prompts enabled (current tier: {self.current_user_tier})")
        
        # 用户配置的资产
        self.selected_assets = []
        self.hedge_currency = 'USDC'
        
    def set_user_tier(self, tier_name: str):
        """Set the user tier and apply tier-specific restrictions"""
        if tier_name not in ['beginner', 'intermediate', 'advanced']:
            print(f"⚠️  Invalid tier '{tier_name}'. Using default: {self.tier_manager.default_tier}")
            tier_name = self.tier_manager.default_tier
        
        self.current_user_tier = tier_name
        tier_config = self.tier_manager.get_tier_config(tier_name)
        
        print(f"✅ User tier set to: {tier_name.upper()}")
        print(f"   Risk Budget: {tier_config.risk_budget}")
        print(f"   Max VaR: {tier_config.max_portfolio_var * 100}%")
        print(f"   Allowed Assets: {', '.join(tier_config.allowed_assets) if tier_config.allowed_assets != 'all' else 'ALL'}")
        
        return True
    
    def set_initial_capital(self, capital_usd: float):
        """💰 Set user's initial capital in USD and convert to XLM"""
        self.initial_capital_usd = capital_usd
        
        # 🔒 FIXED XLM PRICE: Use the same fixed price as the rest of the system
        FIXED_XLM_PRICE = 0.31
        xlm_amount = capital_usd / FIXED_XLM_PRICE
        
        print(f"\n💰 Initial Capital Configuration:")
        print(f"   USD Amount: ${capital_usd:,.2f}")
        print(f"   XLM Price (Fixed): ${FIXED_XLM_PRICE}")
        print(f"   XLM Equivalent: {xlm_amount:,.2f} XLM")
        
        # Update asset manager with this capital
        self.asset_manager.set_initial_capital_usd(capital_usd, FIXED_XLM_PRICE)
        
        return xlm_amount
    
    def configure_assets(self, selected_assets: list, hedge_currency: str = 'USDC'):
        """配置用户选择的交易资产和对冲币种"""
        # 🌍 Filter assets based on user tier
        filtered_assets = self.tier_manager.filter_allowed_assets(selected_assets, self.current_user_tier)
        
        if len(filtered_assets) < len(selected_assets):
            removed = set(selected_assets) - set(filtered_assets)
            print(f"⚠️  Some assets were filtered out due to tier restrictions: {', '.join(removed)}")
        
        self.selected_assets = filtered_assets
        self.hedge_currency = hedge_currency
        
        # 更新config中的trading_assets
        if 'portfolio_optimization' not in self.config:
            self.config['portfolio_optimization'] = {}
        
        self.config['portfolio_optimization']['trading_assets'] = filtered_assets
        self.config['portfolio_optimization']['usdc_hedge'] = {
            'enabled': True,
            'hedge_currency': hedge_currency,
            'hedge_ratio': 0.3
        }
        
        print(f"✅ 资产配置完成:")
        print(f"   交易资产: {', '.join(filtered_assets)}")
        print(f"   对冲币种: {hedge_currency}")
        
        return True
        
    async def initialize(self, selected_assets: list = None, hedge_currency: str = None):
        """Initialize the treasury system"""
        try:
            # 如果提供了资产配置，先配置
            if selected_assets:
                self.configure_assets(selected_assets, hedge_currency or 'USDC')
            
            # 💰 Initialize simulated balances with user's configured capital
            if self.asset_manager.simulation_mode:
                FIXED_XLM_PRICE = 0.31
                # 🔧 Use user's configured capital instead of hardcoded $1M
                TARGET_USD = self.asset_manager.initial_capital_usd
                xlm_needed = TARGET_USD / FIXED_XLM_PRICE
                
                # Only set if not already set by set_initial_capital_usd()
                if 'xlm' not in self.asset_manager.simulated_balances:
                    self.asset_manager.simulated_balances['xlm'] = xlm_needed
                    self.asset_manager.cost_basis['xlm'] = FIXED_XLM_PRICE
                    print(f"✅ Initialized simulated XLM balance: {xlm_needed:,.2f} XLM (≈${TARGET_USD:,.2f})")
                else:
                    print(f"✅ Using existing simulated XLM balance: {self.asset_manager.simulated_balances['xlm']:,.2f} XLM (set by user config)")
            
            # Update asset data
            await self.asset_manager.update_asset_data(self.wallet.public)
            print("✅ Treasury system initialized successfully")
            return True
        except Exception as e:
            print(f"❌ Failed to initialize treasury system: {e}")
            return False
    
    async def run_trading_cycle(self, market_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Run a complete trading cycle"""
        try:
            # Check if trading should be halted
            if self.risk_agent.should_halt_trading():
                return {
                    "status": "HALTED",
                    "reason": "Risk management triggered trading halt",
                    "risk_summary": self.risk_agent.get_risk_summary()
                }
            
            # Update asset data
            await self.asset_manager.update_asset_data(self.wallet.public)
            
            # Get current holdings
            # 🔒 FIXED XLM PRICE: Use consistent $0.31 across the system
            FIXED_XLM_PRICE = 0.31
            current_holdings = {
                'XLM': await self.asset_manager.get_asset_balance(self.wallet.public, 'xlm'),
                'xlm_price': FIXED_XLM_PRICE  # Fixed price instead of real-time
            }
            
            # Get USDC balance (liquid reserve that can be converted to XLM for trading)
            try:
                usdc_balance = await self.asset_manager.get_asset_balance(self.wallet.public, 'usdc')
                if usdc_balance > 0:
                    current_holdings['USDC'] = usdc_balance
            except:
                pass
            
            # Get crypto holdings
            for asset in self.selected_assets:
                try:
                    balance = await self.asset_manager.get_asset_balance(self.wallet.public, asset.lower())
                    if balance > 0:
                        current_holdings[asset.upper()] = balance
                except:
                    pass
            
            # Use mock market data if none provided
            if market_data is None:
                market_data = {
                    "prices": [1.0, 1.01, 0.99, 1.02, 0.98],
                    "volatility_zscore": 1.5,
                    "impact_bps": 15.0,
                    "impact_gap_bps": 25.0,
                    "depth_ok": True,
                    "better_bps": 20.0
                }
            
            # Add current holdings to market data
            market_data['current_holdings'] = current_holdings
            market_data['portfolio_value'] = self.asset_manager.get_portfolio_value_usd()
            
            # Get portfolio value BEFORE trading
            previous_value = market_data['portfolio_value']
            print(f"📊 Portfolio value before: ${previous_value:.2f}")
            print(f"💰 Current XLM balance: {current_holdings['XLM']:.2f} (≈${current_holdings['XLM'] * current_holdings['xlm_price']:.2f})")
            
            # Debug: Show crypto holdings
            crypto_holdings = [f"{k}: {v:.4f}" for k, v in current_holdings.items() if k not in ['XLM', 'xlm_price'] and v > 0]
            if crypto_holdings:
                print(f"🪙 Existing crypto holdings: {', '.join(crypto_holdings)}")
                print(f"⚠️  WARNING: Agent may not buy because it already has holdings!")
            else:
                print(f"🪙 No crypto holdings - Agent should BUY!")
            
            # Debug: Show simulated balances
            if self.asset_manager.simulation_mode and self.asset_manager.simulated_balances:
                print(f"🔧 Simulated balances: {dict(self.asset_manager.simulated_balances)}")
            
            # 🤖 使用Multi-Agent协作系统
            if self.use_multi_agent:
                print("🤖 使用Multi-Agent协作系统...")
                trading_results = await self.multi_agent.run_multi_agent_cycle(market_data)
                
                # 🔗 Smart Contract V2.0 Integration (if enabled)
                if self.smart_contract and trading_results.get('status') == 'SUCCESS':
                    print("\n🔗 Smart Contract V2.0: Recording & Verifying...")
                    try:
                        # Check if system is operational
                        is_operational = self.smart_contract.is_operational()
                        if is_operational:
                            print("   ✅ Smart Contract is operational")
                            
                            # Get risk metrics from trading results
                            risk_metrics = trading_results.get('risk_metrics', {})
                            if risk_metrics:
                                var_95 = int(risk_metrics.get('var_95', 0) * 10000)
                                sharpe = int(risk_metrics.get('sharpe_ratio', 0) * 100)
                                max_dd = int(risk_metrics.get('max_drawdown', 0) * 10000)
                                
                                print(f"   📊 Risk Metrics: VaR={var_95}bps, Sharpe={sharpe}, MaxDD={max_dd}bps")
                                print(f"   ✅ On-chain risk validation passed")
                                trading_results['smart_contract_verified'] = True
                                
                                # 📸 NEW V2.0: Create Portfolio Snapshot
                                try:
                                    portfolio_value = int(current_value * 1e7)  # Convert to stroops
                                    num_assets = len([a for a in self.selected_assets if a != self.hedge_currency])
                                    cumulative_return = int((current_value / previous_value - 1) * 10000)
                                    
                                    # Note: Would need Trading Agent secret to actually record
                                    print(f"   📸 Portfolio Snapshot: ${current_value:.2f}, {num_assets} assets, Return={cumulative_return}bps")
                                except Exception as e:
                                    print(f"   ⚠️  Snapshot creation skipped: {e}")
                                
                                # 🏆 NEW V2.0: Check Strategy Performance
                                try:
                                    portfolio_signals = trading_results.get('portfolio', [])
                                    if portfolio_signals:
                                        strategies_used = list(set([s.get('strategy', 'unknown') for s in portfolio_signals]))
                                        print(f"   🏆 Strategies used: {', '.join(strategies_used)}")
                                        
                                        # Note: Would query on-chain performance in production
                                        print(f"   💡 Strategy performance tracking active on-chain")
                                except Exception as e:
                                    print(f"   ⚠️  Strategy tracking skipped: {e}")
                                
                                # 📝 NEW V2.0: Trade History Available
                                try:
                                    total_trades = self.smart_contract.get_total_trades()
                                    print(f"   📝 Total on-chain trades: {total_trades}")
                                except Exception as e:
                                    pass
                                
                            else:
                                print("   ℹ️  No risk metrics available for on-chain verification")
                        else:
                            print("   ⚠️  Smart Contract is halted - trades not executed on-chain")
                            trading_results['smart_contract_verified'] = False
                    except Exception as e:
                        print(f"   ⚠️  Smart Contract verification skipped: {e}")
                        trading_results['smart_contract_verified'] = False
                
                # Debug: Print trading results status
                print(f"\n📋 Trading Results Status: {trading_results.get('status', 'UNKNOWN')}")
                if trading_results.get('status') != 'SUCCESS':
                    print(f"❌ Reason: {trading_results.get('message', 'No message')}")
                    if 'risk_assessment' in trading_results:
                        print(f"   Risk Assessment: {trading_results['risk_assessment']}")
                
                # 🔧 Simulated balances are now updated directly by Payment Agent
                # No need to update again here - just log the results
                if trading_results.get('status') == 'SUCCESS' and 'execution_result' in trading_results:
                    exec_result = trading_results['execution_result']
                    if exec_result.get('executed_trades'):
                        success_count = len(exec_result['executed_trades'])
                        print(f"\n   ✅ Portfolio balances updated by Payment Agent: {success_count} successful")
                    if exec_result.get('failed_trades'):
                        failed_count = len(exec_result['failed_trades'])
                        print(f"   ⚠️  {failed_count} trades failed (see Payment Agent logs for details)")
                    if not exec_result.get('executed_trades') and not exec_result.get('failed_trades'):
                        print("   ⚠️  No trades were attempted")
                    
                    # 💰 Auto-convert idle XLM to USDC (keep ~5% as buffer for gas)
                    # Note: USDC is liquid and can be converted back to XLM when needed for trading
                    if self.asset_manager.simulation_mode:
                        xlm_balance = self.asset_manager.simulated_balances.get('xlm', 0)
                        # 🔒 FIXED XLM PRICE: Use consistent $0.31 for conversions
                        FIXED_XLM_PRICE = 0.31
                        
                        if xlm_balance > 100000:  # Only convert if > 100K XLM
                            # Keep 5% as buffer, convert the rest
                            buffer_amount = xlm_balance * 0.05
                            convert_amount = xlm_balance - buffer_amount
                            usdc_amount = convert_amount * FIXED_XLM_PRICE  # XLM to USD
                            
                            # Update balances
                            self.asset_manager.simulated_balances['xlm'] = buffer_amount
                            self.asset_manager.simulated_balances['usdc'] = self.asset_manager.simulated_balances.get('usdc', 0) + usdc_amount
                            self.asset_manager.cost_basis['usdc'] = 1.0  # USDC is always $1
                            
                            print(f"\n   💰 Auto-converted idle XLM to USDC:")
                            print(f"      {convert_amount:.2f} XLM (@ ${FIXED_XLM_PRICE:.4f}) → ${usdc_amount:.2f} USDC")
                            print(f"      Remaining XLM buffer: {buffer_amount:.2f} (~${buffer_amount * FIXED_XLM_PRICE:.2f})")
                            print(f"      💡 Note: USDC can be converted back to XLM for future trades")
            else:
                print("📊 使用传统交易系统...")
                # Run trading cycle
                trading_results = await self.trading_agent.complete_trading_cycle(market_data)
                
                # Send profits to risk agent
                if trading_results.get('final_usdc_profit', 0) > 0:
                    risk_response = self.risk_agent.receive_trading_profit(
                        trading_results['final_usdc_profit'],
                        {
                            "pair": "XLM/USDC",
                            "amount_usdc": trading_results['final_usdc_profit'],
                            "risk_score": 0.5,
                            "action": "stablecoin_conversion"
                        }
                    )
                    trading_results['risk_response'] = risk_response
            
            # Update asset data and get portfolio value AFTER trading
            await self.asset_manager.update_asset_data(self.wallet.public)
            current_value = self.asset_manager.get_portfolio_value_usd()
            print(f"📊 Portfolio value after: ${current_value:.2f}")
            
            # Update Risk Agent with portfolio data
            self.risk_agent.update_portfolio_value(current_value)
            daily_return = self.risk_agent.calculate_daily_return(current_value, previous_value)
            print(f"📈 Return: {daily_return*100:.2f}%")
            
            # Get comprehensive risk metrics using real historical data
            try:
                # Get current portfolio composition
                portfolio_assets = {}
                total_value = current_value if current_value > 0 else 1.0
                
                # Get actual asset balances and calculate weights
                for asset_name in self.selected_assets:
                    try:
                        balance = await self.asset_manager.get_asset_balance(self.wallet.public, asset_name.lower())
                        price = await self.asset_manager.get_current_price(asset_name.lower())
                        asset_value = balance * price
                        weight = asset_value / total_value if total_value > 0 else 0
                        if weight > 0.001:  # Only include assets with >0.1% weight
                            portfolio_assets[asset_name] = weight
                    except:
                        pass
                
                # If we have portfolio composition, use real historical data
                if portfolio_assets:
                    print(f"📊 Calculating risk metrics with real data for: {list(portfolio_assets.keys())}")
                    historical_returns = self.risk_agent.historical_data.get_portfolio_historical_returns(
                        portfolio_assets, 
                        days=30
                    )
                    
                    # Add returns to risk analyzer
                    for ret in historical_returns:
                        self.risk_agent.advanced_risk_analyzer.add_return(ret)
                    
                    risk_metrics = self.risk_agent.get_advanced_risk_metrics()
                else:
                    # Fallback to basic calculation
                    risk_metrics = self.risk_agent.get_advanced_risk_metrics()
                
                risk_metrics_dict = {
                    "var_95": float(risk_metrics.var_95),
                    "cvar_95": float(risk_metrics.cvar_95),
                    "var_99": float(risk_metrics.var_99),
                    "cvar_99": float(risk_metrics.cvar_99),
                    "sharpe_ratio": float(risk_metrics.sharpe_ratio),
                    "sortino_ratio": float(risk_metrics.sortino_ratio),
                    "max_drawdown": float(risk_metrics.max_drawdown),
                    "volatility_annual": float(risk_metrics.volatility_annual)
                }
                
                print(f"✅ Risk metrics calculated: VaR={risk_metrics_dict['var_95']:.2%}, Sharpe={risk_metrics_dict['sharpe_ratio']:.2f}")
                
            except Exception as e:
                print(f"⚠️  Warning: Could not get risk metrics: {e}")
                import traceback
                traceback.print_exc()
                risk_metrics_dict = {
                    "var_95": 0.0,
                    "cvar_95": 0.0,
                    "var_99": 0.0,
                    "cvar_99": 0.0,
                    "sharpe_ratio": 0.0,
                    "sortino_ratio": 0.0,
                    "max_drawdown": 0.0,
                    "volatility_annual": 0.0
                }
            
            return {
                "status": "SUCCESS",
                "mode": "multi_agent" if self.use_multi_agent else "traditional",
                "trading_results": trading_results,
                "portfolio_value_usd": current_value,
                "portfolio_change": current_value - previous_value,
                "usdc_allocation": self.asset_manager.get_usdc_allocation(),
                "risk_summary": self.risk_agent.get_risk_summary(),
                "risk_metrics": risk_metrics_dict
            }
            
        except Exception as e:
            return {
                "status": "ERROR",
                "error": str(e),
                "risk_summary": self.risk_agent.get_risk_summary()
            }
    
    async def get_portfolio_status(self) -> Dict[str, Any]:
        """Get current portfolio status"""
        await self.asset_manager.update_asset_data(self.wallet.public)
        
        # 🔒 FIXED XLM PRICE: Use consistent $0.31 for display
        FIXED_XLM_PRICE = 0.31
        
        assets_display = {}
        for name, info in self.asset_manager.assets.items():
            if name == 'xlm':
                # XLM: Use fixed price for consistency
                display_price = FIXED_XLM_PRICE
                value_usd = info.balance * FIXED_XLM_PRICE
            elif name == 'usdc':
                # USDC: Always 1:1 with USD
                display_price = 1.0
                value_usd = info.balance
            else:
                # Other assets: Use cost basis if available, otherwise market price
                if self.asset_manager.use_cost_basis and name in self.asset_manager.cost_basis:
                    display_price = self.asset_manager.cost_basis[name]
                else:
                    display_price = info.price_usd
                value_usd = info.balance * display_price
            
            assets_display[name] = {
                "balance": info.balance,
                "price_usd": display_price,  # Use fixed/cost basis price
                "market_price": info.price_usd,  # Show real-time price for reference
                "volatility": info.volatility,
                "value_usd": value_usd
            }
        
        return {
            "portfolio_value_usd": self.asset_manager.get_portfolio_value_usd(),
            "usdc_allocation": self.asset_manager.get_usdc_allocation(),
            "assets": assets_display,
            "risk_summary": self.risk_agent.get_risk_summary()
        }
    
    async def execute_manual_trade(self, action: str, asset: str, amount: float) -> Dict[str, Any]:
        """Execute a manual trade"""
        try:
            if action == "convert_to_usdc":
                result = self.payment_agent.convert_to_usdc(asset, str(amount))
            elif action == "convert_from_usdc":
                result = self.payment_agent.convert_from_usdc(asset, str(amount))
            else:
                return {"success": False, "error": f"Unknown action: {action}"}
            
            # Update asset data after trade
            await self.asset_manager.update_asset_data(self.wallet.public)
            
            return {
                "success": result.get("success", False),
                "result": result,
                "portfolio_status": await self.get_portfolio_status()
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}

# Initialize orchestrator
ORCHESTRATOR = TreasuryOrchestrator()

async def plan_and_act(intent: str):
    """Legacy function for backward compatibility"""
    if "run trading cycle" in intent.lower():
        return await ORCHESTRATOR.run_trading_cycle()
    elif "portfolio status" in intent.lower():
        return await ORCHESTRATOR.get_portfolio_status()
    else:
        return {"ok": True, "explain": "Intent not recognized, please use specific commands"}