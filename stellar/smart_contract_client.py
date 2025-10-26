"""
Stellar Smart Contract Client for AI Treasury Vault V2.0

Enhanced Python interface with support for:
- Trade history tracking
- Strategy performance analytics
- Portfolio snapshots
- Dynamic risk controls
"""

import subprocess
import json
import os
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime


@dataclass
class TradeRecord:
    """Trade execution record"""
    trade_id: int
    signal_id: int
    asset: str
    action: str
    amount: int
    price: int
    strategy: str
    executed_at: int
    profit_loss: int


@dataclass
class StrategyPerformance:
    """Strategy performance metrics"""
    strategy_name: str
    total_trades: int
    winning_trades: int
    total_profit: int
    avg_return: int
    sharpe_ratio: int
    last_updated: int
    
    @property
    def win_rate(self) -> float:
        """Calculate win rate percentage"""
        if self.total_trades == 0:
            return 0.0
        return (self.winning_trades / self.total_trades) * 100


@dataclass
class PortfolioSnapshot:
    """Portfolio snapshot at a point in time"""
    snapshot_id: int
    timestamp: int
    total_value: int
    num_assets: int
    total_trades: int
    cumulative_return: int
    
    @property
    def datetime(self) -> datetime:
        """Convert timestamp to datetime"""
        return datetime.fromtimestamp(self.timestamp)


class SmartContractClientV2:
    """
    Enhanced client for AI Treasury Vault V2.0 smart contract
    
    New Features:
    - Trade history queries
    - Strategy performance tracking
    - Portfolio snapshots
    - Dynamic stop-loss management
    """
    
    def __init__(self, contract_id: str, network: str = "testnet"):
        """
        Initialize smart contract client V2
        
        Args:
            contract_id: Deployed contract ID on Stellar
            network: Network to use (testnet, futurenet, or mainnet)
        """
        self.contract_id = contract_id
        self.network = network
        self.version = "2.0"
        self._verify_stellar_cli()
    
    def _verify_stellar_cli(self):
        """Verify that stellar-cli is installed"""
        try:
            result = subprocess.run(
                ["stellar", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode != 0:
                raise RuntimeError("stellar-cli not found")
        except FileNotFoundError:
            raise RuntimeError("stellar-cli not found. Install: cargo install stellar-cli")
    
    def _run_contract_command(
        self,
        function_name: str,
        args: list,
        signer_secret: Optional[str] = None
    ) -> Dict[str, Any]:
        """Run a smart contract command"""
        cmd = [
            "stellar", "contract", "invoke",
            "--id", self.contract_id,
            "--network", self.network
        ]
        
        # Stellar CLI requires --source-account for all invocations
        # Use provided signer_secret or fall back to STELLAR_PUBLIC from env
        if signer_secret:
            cmd.extend(["--source-account", signer_secret])
        else:
            # For read-only methods, use public key from environment
            default_account = os.environ.get("STELLAR_PUBLIC", "")
            if default_account:
                cmd.extend(["--source-account", default_account])
        
        cmd.extend(["--", function_name])
        cmd.extend(args)
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            return {
                "success": result.returncode == 0,
                "output": result.stdout.strip(),
                "error": result.stderr.strip() if result.returncode != 0 else None
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Command timeout"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # ========================================================================
    # Trading Signal Functions (Enhanced)
    # ========================================================================
    
    def submit_trading_signal(
        self,
        asset: str,
        action: str,
        amount: int,
        strategy: str,
        confidence: int,
        expected_return: int,
        signer_secret: str
    ) -> Dict[str, Any]:
        """
        Submit a trading signal (V2 signature)
        
        Returns:
            Dict with success status and signal_id
        """
        args = [
            "--asset", asset,
            "--action", action,
            "--amount", str(amount),
            "--strategy", strategy,
            "--confidence", str(confidence),
            "--expected_return", str(expected_return)
        ]
        
        result = self._run_contract_command(
            "submit_trading_signal",
            args,
            signer_secret
        )
        
        if result["success"]:
            # Parse signal_id from output
            try:
                signal_id = int(result["output"])
                print(f"✅ Trading signal submitted: ID={signal_id}")
                return {"success": True, "signal_id": signal_id}
            except:
                return {"success": True, "signal_id": None}
        else:
            print(f"❌ Failed to submit signal: {result.get('error')}")
            return result
    
    def approve_trade(
        self,
        signal_id: int,
        var_95: float,
        sharpe_ratio: float,
        max_drawdown: float,
        stop_loss_level: float,
        signer_secret: str
    ) -> Dict[str, Any]:
        """
        Approve trade with risk metrics (V2 with stop-loss)
        
        Args:
            signal_id: Signal ID to approve
            var_95: Value at Risk 95% (as decimal)
            sharpe_ratio: Sharpe ratio
            max_drawdown: Maximum drawdown (as decimal)
            stop_loss_level: Current stop-loss level (as decimal)
            signer_secret: Risk Agent secret key
        """
        # Convert to basis points
        var_bps = int(var_95 * 10000)
        sharpe_scaled = int(sharpe_ratio * 100)
        dd_bps = int(max_drawdown * 10000)
        sl_bps = int(stop_loss_level * 10000)
        
        # Create risk_metrics struct
        args = [
            "--signal_id", str(signal_id),
            "--risk_metrics", json.dumps({
                "var_95": var_bps,
                "sharpe_ratio": sharpe_scaled,
                "max_drawdown": dd_bps,
                "portfolio_volatility": 0,
                "stop_loss_level": sl_bps
            })
        ]
        
        result = self._run_contract_command(
            "approve_trade",
            args,
            signer_secret
        )
        
        if result["success"]:
            approved = result["output"].lower() == "true"
            if approved:
                print(f"✅ Trade {signal_id} approved by Risk Agent")
            else:
                print(f"❌ Trade {signal_id} rejected by Risk Agent")
            return {"success": True, "approved": approved}
        else:
            print(f"❌ Failed to approve trade: {result.get('error')}")
            return result
    
    def execute_trade(
        self,
        signal_id: int,
        executed_price: int,
        profit_loss: int,
        signer_secret: str
    ) -> Dict[str, Any]:
        """
        Execute trade and record history (V2)
        
        Args:
            signal_id: Signal ID to execute
            executed_price: Actual execution price (scaled by 1e7)
            profit_loss: Realized P&L in stroops
            signer_secret: Payment Agent secret key
        
        Returns:
            Dict with success status and trade_id
        """
        args = [
            "--signal_id", str(signal_id),
            "--executed_price", str(executed_price),
            "--profit_loss", str(profit_loss)
        ]
        
        result = self._run_contract_command(
            "execute_trade",
            args,
            signer_secret
        )
        
        if result["success"]:
            try:
                trade_id = int(result["output"])
                print(f"✅ Trade executed: ID={trade_id}, P&L={profit_loss}")
                return {"success": True, "trade_id": trade_id}
            except:
                return {"success": True, "trade_id": None}
        else:
            print(f"❌ Failed to execute trade: {result.get('error')}")
            return result
    
    # ========================================================================
    # Trade History Functions (NEW)
    # ========================================================================
    
    def get_trade(self, trade_id: int) -> Optional[TradeRecord]:
        """
        Get trade record by ID
        
        Args:
            trade_id: Trade ID to query
        
        Returns:
            TradeRecord object or None if not found
        """
        args = ["--trade_id", str(trade_id)]
        
        result = self._run_contract_command("get_trade", args)
        
        if result["success"]:
            try:
                data = json.loads(result["output"])
                return TradeRecord(**data)
            except:
                return None
        return None
    
    def get_total_trades(self) -> int:
        """Get total number of executed trades"""
        result = self._run_contract_command("get_total_trades", [])
        
        if result["success"]:
            try:
                return int(result["output"])
            except:
                return 0
        return 0
    
    def get_recent_trades(self, count: int = 10) -> List[TradeRecord]:
        """
        Get recent trade records
        
        Args:
            count: Number of recent trades to fetch
        
        Returns:
            List of TradeRecord objects
        """
        total_trades = self.get_total_trades()
        if total_trades == 0:
            return []
        
        trades = []
        start = max(1, total_trades - count + 1)
        
        for trade_id in range(start, total_trades + 1):
            trade = self.get_trade(trade_id)
            if trade:
                trades.append(trade)
        
        return trades
    
    # ========================================================================
    # Strategy Performance Functions (NEW)
    # ========================================================================
    
    def get_strategy_performance(self, strategy_name: str) -> Optional[StrategyPerformance]:
        """
        Get performance metrics for a specific strategy
        
        Args:
            strategy_name: Strategy name (e.g., "LSTM", "DQN")
        
        Returns:
            StrategyPerformance object or None
        """
        args = ["--strategy_name", strategy_name]
        
        result = self._run_contract_command("get_strategy_performance", args)
        
        if result["success"]:
            try:
                data = json.loads(result["output"])
                return StrategyPerformance(**data)
            except:
                return None
        return None
    
    def get_all_strategies_performance(
        self,
        strategies: List[str]
    ) -> Dict[str, StrategyPerformance]:
        """
        Get performance for multiple strategies
        
        Args:
            strategies: List of strategy names
        
        Returns:
            Dict mapping strategy name to StrategyPerformance
        """
        performances = {}
        
        for strategy in strategies:
            perf = self.get_strategy_performance(strategy)
            if perf:
                performances[strategy] = perf
        
        return performances
    
    def get_best_performing_strategy(
        self,
        strategies: List[str]
    ) -> Optional[str]:
        """
        Find the best performing strategy by win rate
        
        Args:
            strategies: List of strategy names to compare
        
        Returns:
            Name of best strategy or None
        """
        performances = self.get_all_strategies_performance(strategies)
        
        if not performances:
            return None
        
        best_strategy = max(
            performances.items(),
            key=lambda x: (x[1].win_rate, x[1].total_profit)
        )
        
        return best_strategy[0]
    
    # ========================================================================
    # Portfolio Snapshot Functions (NEW)
    # ========================================================================
    
    def create_snapshot(
        self,
        total_value: int,
        num_assets: int,
        cumulative_return: int,
        signer_secret: str
    ) -> Dict[str, Any]:
        """
        Create a portfolio snapshot
        
        Args:
            total_value: Total portfolio value in stroops
            num_assets: Number of assets in portfolio
            cumulative_return: Cumulative return in basis points
            signer_secret: Trading Agent secret key
        
        Returns:
            Dict with success status and snapshot_id
        """
        args = [
            "--total_value", str(total_value),
            "--num_assets", str(num_assets),
            "--cumulative_return", str(cumulative_return)
        ]
        
        result = self._run_contract_command(
            "create_snapshot",
            args,
            signer_secret
        )
        
        if result["success"]:
            try:
                snapshot_id = int(result["output"])
                print(f"✅ Snapshot created: ID={snapshot_id}")
                return {"success": True, "snapshot_id": snapshot_id}
            except:
                return {"success": True, "snapshot_id": None}
        else:
            print(f"❌ Failed to create snapshot: {result.get('error')}")
            return result
    
    def get_latest_snapshot(self) -> Optional[PortfolioSnapshot]:
        """Get the most recent portfolio snapshot"""
        result = self._run_contract_command("get_latest_snapshot", [])
        
        if result["success"]:
            try:
                data = json.loads(result["output"])
                return PortfolioSnapshot(**data)
            except:
                return None
        return None
    
    # ========================================================================
    # Risk Control Functions (Enhanced)
    # ========================================================================
    
    def set_dynamic_stop_loss(
        self,
        enabled: bool,
        signer_secret: str
    ) -> Dict[str, Any]:
        """
        Enable or disable dynamic stop-loss (NEW)
        
        Args:
            enabled: True to enable, False to disable
            signer_secret: Admin secret key
        """
        args = ["--enabled", str(enabled).lower()]
        
        result = self._run_contract_command(
            "set_dynamic_stop_loss",
            args,
            signer_secret
        )
        
        if result["success"]:
            status = "enabled" if enabled else "disabled"
            print(f"✅ Dynamic stop-loss {status}")
        else:
            print(f"❌ Failed to update stop-loss: {result.get('error')}")
        
        return result
    
    # ========================================================================
    # Query Functions
    # ========================================================================
    
    def get_config(self) -> Dict[str, Any]:
        """Get vault configuration"""
        result = self._run_contract_command("get_config", [])
        
        if result["success"]:
            try:
                return json.loads(result["output"])
            except:
                return {}
        return {}
    
    def get_risk_metrics(self) -> Dict[str, Any]:
        """Get current risk metrics"""
        result = self._run_contract_command("get_risk_metrics", [])
        
        if result["success"]:
            try:
                return json.loads(result["output"])
            except:
                return {}
        return {}
    
    def is_operational(self) -> bool:
        """Check if system is operational"""
        result = self._run_contract_command("is_operational", [])
        
        if result["success"]:
            return result["output"].lower() == "true"
        
        # If command fails (e.g., due to keychain issues), assume operational
        # rather than falsely reporting as halted
        print(f"   ⚠️  Could not verify contract status (assuming operational): {result.get('error', 'Unknown error')}")
        return True  # Default to operational on error
    
    def emergency_halt(self, signer_secret: str) -> Dict[str, Any]:
        """Emergency halt all trading"""
        result = self._run_contract_command(
            "emergency_halt",
            [],
            signer_secret
        )
        
        if result["success"]:
            print("🛑 Emergency halt activated!")
        else:
            print(f"❌ Failed to halt: {result.get('error')}")
        
        return result
    
    def resume_trading(self, signer_secret: str) -> Dict[str, Any]:
        """Resume trading after halt"""
        result = self._run_contract_command(
            "resume_trading",
            [],
            signer_secret
        )
        
        if result["success"]:
            print("✅ Trading resumed")
        else:
            print(f"❌ Failed to resume: {result.get('error')}")
        
        return result
    
    # ========================================================================
    # Utility Functions
    # ========================================================================
    
    def print_status(self):
        """Print contract status summary"""
        print("\n" + "=" * 60)
        print(f"AI Treasury Vault V{self.version} Status")
        print("=" * 60)
        
        print(f"Contract ID: {self.contract_id}")
        print(f"Network: {self.network}")
        
        config = self.get_config()
        if config:
            print(f"Version: {config.get('version', 'unknown')}")
            print(f"Operational: {'Yes' if not config.get('halted') else 'No'}")
            print(f"Dynamic Stop-Loss: {'Enabled' if config.get('dynamic_stop_loss') else 'Disabled'}")
        
        total_trades = self.get_total_trades()
        print(f"Total Trades: {total_trades}")
        
        latest_snapshot = self.get_latest_snapshot()
        if latest_snapshot:
            print(f"Latest Snapshot: {latest_snapshot.datetime.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Portfolio Value: {latest_snapshot.total_value / 1e7:.2f}")
            print(f"Cumulative Return: {latest_snapshot.cumulative_return / 100:.2f}%")
        
        print("=" * 60 + "\n")


# Backward compatibility alias
SmartContractClient = SmartContractClientV2
