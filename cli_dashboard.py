#!/usr/bin/env python3
"""
Command Line Interface for Stellar AI Treasury System
A simple text-based dashboard for quick monitoring
"""

import asyncio
import os
import sys
from datetime import datetime
from app.orchestrator import ORCHESTRATOR

class CLIDashboard:
    def __init__(self):
        self.orchestrator = ORCHESTRATOR
        self.initialized = False
    
    def clear_screen(self):
        """Clear the terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_header(self):
        """Print the dashboard header"""
        print("=" * 80)
        print("🏦 STELLAR AI TREASURY - COMMAND LINE DASHBOARD")
        print("=" * 80)
        print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
    
    def print_menu(self):
        """Print the main menu"""
        print("\n📋 MAIN MENU:")
        print("1. 🚀 Initialize System")
        print("2. 📊 Portfolio Status")
        print("3. 📡 Trading Signals")
        print("4. 🪙 Stablecoin Strategy")
        print("5. ⚠️  Risk Management")
        print("6. 🔄 Run Trading Cycle")
        print("7. 💱 Manual Trade")
        print("8. 🌐 Launch Web Dashboard")
        print("9. ❌ Exit")
        print("-" * 80)
    
    async def initialize_system(self):
        """Initialize the treasury system"""
        print("🔧 Initializing system...")
        try:
            success = await self.orchestrator.initialize()
            if success:
                self.initialized = True
                print("✅ System initialized successfully!")
            else:
                print("❌ System initialization failed")
        except Exception as e:
            print(f"❌ Initialization error: {e}")
    
    async def show_portfolio_status(self):
        """Show portfolio status"""
        if not self.initialized:
            print("❌ Please initialize the system first")
            return
        
        print("📊 PORTFOLIO STATUS")
        print("-" * 40)
        
        try:
            status = await self.orchestrator.get_portfolio_status()
            
            print(f"💰 Total Portfolio Value: ${status['portfolio_value_usd']:.2f}")
            print(f"🪙 USDC Allocation: {status['usdc_allocation']:.1f}%")
            print()
            
            print("📈 Asset Breakdown:")
            for asset_name, asset_info in status['assets'].items():
                print(f"   {asset_name.upper():>6}: {asset_info['balance']:>10.2f} "
                      f"(${asset_info['value_usd']:>8.2f}) "
                      f"Vol: {asset_info['volatility']:.3f}")
            
            print()
            risk_summary = status['risk_summary']
            print(f"⚠️  Risk Level: {risk_summary['current_risk']['risk_level']}")
            print(f"📊 Risk Score: {risk_summary['current_risk']['score']:.2f}")
            print(f"💵 Total Profit: ${risk_summary['total_profit_usdc']:.2f}")
            
        except Exception as e:
            print(f"❌ Error getting portfolio status: {e}")
    
    async def show_trading_signals(self):
        """Show trading signals"""
        if not self.initialized:
            print("❌ Please initialize the system first")
            return
        
        print("📡 TRADING SIGNALS")
        print("-" * 40)
        
        try:
            # Mock market data
            market_data = {
                "prices": [1.0, 1.02, 0.98, 1.05, 0.95, 1.08, 0.92],
                "volatility_zscore": 2.0,
                "impact_bps": 18.0,
                "impact_gap_bps": 28.0,
                "depth_ok": True,
                "better_bps": 22.0
            }
            
            signals = self.orchestrator.trading_agent.generate_trading_signals(market_data)
            
            if signals:
                print(f"🎯 Generated {len(signals)} trading signals:")
                for i, signal in enumerate(signals, 1):
                    print(f"   {i}. {signal.action} {signal.asset} ({signal.amount:.2f})")
                    print(f"      Reason: {signal.reason}")
                    print(f"      Confidence: {signal.confidence:.2f}")
                    print()
            else:
                print("😴 No trading signals at this time")
                
        except Exception as e:
            print(f"❌ Error generating signals: {e}")
    
    async def show_stablecoin_strategy(self):
        """Show stablecoin strategy status"""
        if not self.initialized:
            print("❌ Please initialize the system first")
            return
        
        print("🪙 STABLECOIN STRATEGY")
        print("-" * 40)
        
        try:
            await self.orchestrator.asset_manager.update_asset_data(
                self.orchestrator.payment_agent.w.public
            )
            
            print("📊 Current Asset Volatilities:")
            for asset_name, asset_info in self.orchestrator.asset_manager.assets.items():
                if asset_name != 'usdc':
                    print(f"   {asset_name.upper()}: {asset_info.volatility:.3f}")
            
            print()
            
            should_convert_to_usdc = self.orchestrator.asset_manager.should_convert_to_usdc()
            should_convert_from_usdc = self.orchestrator.asset_manager.should_convert_from_usdc()
            
            if should_convert_to_usdc:
                target_asset = self.orchestrator.asset_manager.get_asset_to_convert()
                print(f"🔄 Should convert {target_asset.upper()} to USDC (high volatility)")
            elif should_convert_from_usdc:
                print("🔄 Should convert USDC to assets (low volatility)")
            else:
                print("😴 No stablecoin conversion needed at this time")
            
            print()
            print(f"🎯 USDC Target Allocation: {self.orchestrator.trading_agent.usdc_allocation_target}%")
            print(f"📈 High Volatility Threshold: {self.orchestrator.trading_agent.volatility_threshold_high}")
            print(f"📉 Low Volatility Threshold: {self.orchestrator.trading_agent.volatility_threshold_low}")
            
        except Exception as e:
            print(f"❌ Error checking stablecoin strategy: {e}")
    
    async def show_risk_management(self):
        """Show risk management status"""
        if not self.initialized:
            print("❌ Please initialize the system first")
            return
        
        print("⚠️  RISK MANAGEMENT")
        print("-" * 40)
        
        try:
            risk_summary = self.orchestrator.risk_agent.get_risk_summary()
            
            risk_level = risk_summary['current_risk']['risk_level']
            risk_score = risk_summary['current_risk']['score']
            
            print(f"📊 Risk Level: {risk_level}")
            print(f"📈 Risk Score: {risk_score:.2f}")
            print(f"💵 Total Profit: ${risk_summary['total_profit_usdc']:.2f}")
            print(f"🔄 Daily Trades: {risk_summary['daily_trade_count']}")
            print(f"📝 Trading History: {risk_summary['trading_history_count']}")
            print(f"🛑 Should Halt: {'Yes' if risk_summary['should_halt'] else 'No'}")
            print()
            print(f"💡 Recommendation: {risk_summary['recommendation']}")
            
        except Exception as e:
            print(f"❌ Error getting risk summary: {e}")
    
    async def run_trading_cycle(self):
        """Run a trading cycle"""
        if not self.initialized:
            print("❌ Please initialize the system first")
            return
        
        print("🔄 Running trading cycle...")
        
        try:
            results = await self.orchestrator.run_trading_cycle()
            
            print(f"📊 Status: {results['status']}")
            
            if results['status'] == 'SUCCESS':
                trading_results = results['trading_results']
                print(f"🎯 Signals Generated: {trading_results['signals_generated']}")
                print(f"💰 Final USDC Profit: ${trading_results['final_usdc_profit']:.2f}")
                
                if 'risk_response' in trading_results:
                    risk_response = trading_results['risk_response']
                    print(f"⚠️  Risk Assessment: {risk_response['risk_assessment']['risk_level']}")
                    print(f"💵 Total Profit: ${risk_response['total_profit_usdc']:.2f}")
            
            elif results['status'] == 'HALTED':
                print(f"🛑 Trading Halted: {results['reason']}")
            
            else:
                print(f"❌ Error: {results.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ Error running trading cycle: {e}")
    
    async def manual_trade(self):
        """Execute manual trade"""
        if not self.initialized:
            print("❌ Please initialize the system first")
            return
        
        print("💱 MANUAL TRADE")
        print("-" * 40)
        
        try:
            print("Available actions:")
            print("1. convert_to_usdc")
            print("2. convert_from_usdc")
            
            action = input("Enter action (1 or 2): ").strip()
            if action == "1":
                action = "convert_to_usdc"
            elif action == "2":
                action = "convert_from_usdc"
            else:
                print("❌ Invalid action")
                return
            
            print("Available assets: XLM, USDC, EURC")
            asset = input("Enter asset: ").strip().upper()
            
            amount = float(input("Enter amount: "))
            
            print("Executing trade...")
            result = await self.orchestrator.execute_manual_trade(action, asset, amount)
            
            if result['success']:
                print("✅ Trade executed successfully!")
                print(f"Transaction Hash: {result['result'].get('transaction_hash', 'N/A')}")
            else:
                print(f"❌ Trade failed: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ Error executing manual trade: {e}")
    
    def launch_web_dashboard(self):
        """Launch the web dashboard"""
        print("🌐 Launching web dashboard...")
        print("The dashboard will open in your browser at http://localhost:8501")
        
        try:
            import subprocess
            dashboard_path = os.path.join(os.path.dirname(__file__), "app", "dashboard.py")
            subprocess.Popen([
                sys.executable, "-m", "streamlit", "run", dashboard_path,
                "--server.port", "8501", "--server.address", "localhost"
            ])
            print("✅ Web dashboard launched successfully!")
        except Exception as e:
            print(f"❌ Error launching web dashboard: {e}")
    
    async def run(self):
        """Run the CLI dashboard"""
        while True:
            self.clear_screen()
            self.print_header()
            self.print_menu()
            
            try:
                choice = input("Select an option (1-9): ").strip()
                
                if choice == '1':
                    await self.initialize_system()
                elif choice == '2':
                    await self.show_portfolio_status()
                elif choice == '3':
                    await self.show_trading_signals()
                elif choice == '4':
                    await self.show_stablecoin_strategy()
                elif choice == '5':
                    await self.show_risk_management()
                elif choice == '6':
                    await self.run_trading_cycle()
                elif choice == '7':
                    await self.manual_trade()
                elif choice == '8':
                    self.launch_web_dashboard()
                elif choice == '9':
                    print("👋 Goodbye!")
                    break
                else:
                    print("❌ Invalid choice. Please select 1-9.")
                
                if choice != '8':  # Don't pause for web dashboard launch
                    input("\nPress Enter to continue...")
                    
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                input("\nPress Enter to continue...")

async def main():
    """Main function"""
    dashboard = CLIDashboard()
    await dashboard.run()

if __name__ == "__main__":
    asyncio.run(main())
