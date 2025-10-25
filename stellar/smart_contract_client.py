"""
Stellar Smart Contract Client for AI Treasury Vault

Provides Python interface to interact with the deployed Soroban smart contract.
"""

import subprocess
import json
import os
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class TradingSignal:
    """Trading signal data structure"""
    signal_id: int
    from_asset: str
    to_asset: str
    amount: int
    expected_return: float
    risk_score: float
    strategy: str
    approved: bool


@dataclass
class RiskMetrics:
    """Risk metrics data structure"""
    var_95: float
    sharpe_ratio: float
    max_drawdown: float
    total_trades: int
    successful_trades: int


class SmartContractClient:
    """
    Client for interacting with AI Treasury Vault smart contract on Stellar
    
    This client provides methods to:
    - Submit trading signals from Trading Agent
    - Approve trades from Risk Agent
    - Execute trades from Payment Agent
    - Query contract state and risk metrics
    - Manage emergency halt mechanism
    """
    
    def __init__(self, contract_id: str, network: str = "testnet"):
        """
        Initialize smart contract client
        
        Args:
            contract_id: Deployed contract ID on Stellar
            network: Network to use (testnet, futurenet, or mainnet)
        """
        self.contract_id = contract_id
        self.network = network
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
                raise RuntimeError("stellar-cli not found. Please install: cargo install stellar-cli")
        except FileNotFoundError:
            raise RuntimeError("stellar-cli not found. Please install: cargo install stellar-cli")
    
    def _run_contract_command(
        self,
        function_name: str,
        args: list,
        signer_secret: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Run a smart contract command
        
        Args:
            function_name: Contract function to call
            args: List of arguments for the function
            signer_secret: Stellar secret key for signing (if needed)
        
        Returns:
            Dict with success status and output
        """
        cmd = [
            "stellar", "contract", "invoke",
            "--id", self.contract_id,
            "--network", self.network
        ]
        
        if signer_secret:
            cmd.extend(["--source", signer_secret])
        
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
            return {
                "success": False,
                "error": "Command timeout"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    # ========================================================================
    # Trading Agent Functions
    # ========================================================================
    
    def submit_trading_signal(
        self,
        from_asset: str,
        to_asset: str,
        amount: int,
        expected_return: float,
        risk_score: float,
        strategy: str,
        signer_secret: str
    ) -> Dict[str, Any]:
        """
        Submit a trading signal to the smart contract
        
        Args:
            from_asset: Source asset code (e.g., "BTC")
            to_asset: Destination asset code (e.g., "USDC")
            amount: Amount to trade (in stroops/smallest unit)
            expected_return: Expected return as decimal (e.g., 0.05 for 5%)
            risk_score: Risk score as decimal (e.g., 0.3 for 30%)
            strategy: Strategy name (e.g., "MACD", "LSTM")
            signer_secret: Trading Agent's secret key
        
        Returns:
            Dict with success status and signal_id
        """
        # Convert floats to fixed-point integers (6 decimals)
        expected_return_fixed = int(expected_return * 1_000_000)
        risk_score_fixed = int(risk_score * 1_000_000)
        
        args = [
            "--from_asset", from_asset,
            "--to_asset", to_asset,
            "--amount", str(amount),
            "--expected_return", str(expected_return_fixed),
            "--risk_score", str(risk_score_fixed),
            "--strategy", strategy
        ]
        
        result = self._run_contract_command(
            "submit_trading_signal",
            args,
            signer_secret
        )
        
        if result["success"]:
            print(f"✅ Trading signal submitted: {from_asset} → {to_asset}")
        else:
            print(f"❌ Failed to submit signal: {result.get('error')}")
        
        return result
    
    # ========================================================================
    # Risk Agent Functions
    # ========================================================================
    
    def approve_trade(
        self,
        signal_id: int,
        var_95: float,
        sharpe_ratio: float,
        max_dd: float,
        signer_secret: str
    ) -> Dict[str, Any]:
        """
        Risk Agent approves a trading signal
        
        Args:
            signal_id: ID of the signal to approve
            var_95: Value at Risk (95% confidence)
            sharpe_ratio: Sharpe Ratio of the portfolio
            max_dd: Maximum Drawdown
            signer_secret: Risk Agent's secret key
        
        Returns:
            Dict with success status
        """
        # Convert to fixed-point
        var_95_fixed = int(abs(var_95) * 1_000_000)
        sharpe_fixed = int(sharpe_ratio * 1_000_000)
        max_dd_fixed = int(abs(max_dd) * 1_000_000)
        
        args = [
            "--signal_id", str(signal_id),
            "--var_95", str(var_95_fixed),
            "--sharpe_ratio", str(sharpe_fixed),
            "--max_dd", str(max_dd_fixed)
        ]
        
        result = self._run_contract_command(
            "approve_trade",
            args,
            signer_secret
        )
        
        if result["success"]:
            print(f"✅ Trade {signal_id} approved by Risk Agent")
        else:
            print(f"❌ Failed to approve trade: {result.get('error')}")
        
        return result
    
    # ========================================================================
    # Payment Agent Functions
    # ========================================================================
    
    def execute_trade(
        self,
        signal_id: int,
        signer_secret: str
    ) -> Dict[str, Any]:
        """
        Payment Agent executes an approved trade
        
        Args:
            signal_id: ID of the approved signal to execute
            signer_secret: Payment Agent's secret key
        
        Returns:
            Dict with success status
        """
        args = ["--signal_id", str(signal_id)]
        
        result = self._run_contract_command(
            "execute_trade",
            args,
            signer_secret
        )
        
        if result["success"]:
            print(f"✅ Trade {signal_id} executed by Payment Agent")
        else:
            print(f"❌ Failed to execute trade: {result.get('error')}")
        
        return result
    
    # ========================================================================
    # Risk Management Functions
    # ========================================================================
    
    def emergency_halt(self, signer_secret: str) -> Dict[str, Any]:
        """
        Emergency halt all trading (Risk Agent or Admin)
        
        Args:
            signer_secret: Risk Agent or Admin secret key
        
        Returns:
            Dict with success status
        """
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
        """
        Resume trading after halt (Admin only)
        
        Args:
            signer_secret: Admin secret key
        
        Returns:
            Dict with success status
        """
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
    
    def update_risk_limits(
        self,
        max_var_95: float,
        min_sharpe_ratio: float,
        max_drawdown: float,
        signer_secret: str
    ) -> Dict[str, Any]:
        """
        Update risk limits (Admin only)
        
        Args:
            max_var_95: Maximum allowed VaR (95%)
            min_sharpe_ratio: Minimum required Sharpe Ratio
            max_drawdown: Maximum allowed drawdown
            signer_secret: Admin secret key
        
        Returns:
            Dict with success status
        """
        args = [
            "--max_var_95", str(int(abs(max_var_95) * 1_000_000)),
            "--min_sharpe_ratio", str(int(min_sharpe_ratio * 1_000_000)),
            "--max_drawdown", str(int(abs(max_drawdown) * 1_000_000))
        ]
        
        result = self._run_contract_command(
            "update_risk_limits",
            args,
            signer_secret
        )
        
        if result["success"]:
            print("✅ Risk limits updated")
        else:
            print(f"❌ Failed to update limits: {result.get('error')}")
        
        return result
    
    # ========================================================================
    # Query Functions
    # ========================================================================
    
    def get_config(self) -> Dict[str, Any]:
        """Get contract configuration"""
        result = self._run_contract_command("get_config", [])
        
        if result["success"]:
            try:
                return json.loads(result["output"])
            except json.JSONDecodeError:
                return {"raw": result["output"]}
        return {}
    
    def get_risk_metrics(self) -> Optional[RiskMetrics]:
        """Get current risk metrics from contract"""
        result = self._run_contract_command("get_risk_metrics", [])
        
        if result["success"]:
            try:
                data = json.loads(result["output"])
                return RiskMetrics(
                    var_95=data.get("var_95", 0) / 1_000_000,
                    sharpe_ratio=data.get("sharpe_ratio", 0) / 1_000_000,
                    max_drawdown=data.get("max_drawdown", 0) / 1_000_000,
                    total_trades=data.get("total_trades", 0),
                    successful_trades=data.get("successful_trades", 0)
                )
            except (json.JSONDecodeError, KeyError):
                return None
        return None
    
    def is_operational(self) -> bool:
        """Check if trading is operational (not halted)"""
        result = self._run_contract_command("is_operational", [])
        
        if result["success"]:
            return result["output"].lower() == "true"
        return False
    
    # ========================================================================
    # Utility Functions
    # ========================================================================
    
    def get_contract_url(self) -> str:
        """Get Stellar Explorer URL for this contract"""
        if self.network == "testnet":
            return f"https://stellar.expert/explorer/testnet/contract/{self.contract_id}"
        elif self.network == "mainnet":
            return f"https://stellar.expert/explorer/public/contract/{self.contract_id}"
        else:
            return f"https://stellar.expert/explorer/{self.network}/contract/{self.contract_id}"
    
    def print_status(self):
        """Print contract status"""
        print(f"\n{'='*60}")
        print(f"🔐 AI Treasury Vault Smart Contract")
        print(f"{'='*60}")
        print(f"Contract ID: {self.contract_id}")
        print(f"Network: {self.network}")
        print(f"Explorer: {self.get_contract_url()}")
        
        is_op = self.is_operational()
        status = "🟢 OPERATIONAL" if is_op else "🔴 HALTED"
        print(f"Status: {status}")
        
        metrics = self.get_risk_metrics()
        if metrics:
            print(f"\n📊 Risk Metrics:")
            print(f"  VaR (95%): {metrics.var_95:.4f}")
            print(f"  Sharpe Ratio: {metrics.sharpe_ratio:.4f}")
            print(f"  Max Drawdown: {metrics.max_drawdown:.4f}")
            print(f"  Total Trades: {metrics.total_trades}")
            print(f"  Success Rate: {metrics.successful_trades}/{metrics.total_trades}")
        
        print(f"{'='*60}\n")


# ============================================================================
# Example Usage
# ============================================================================

if __name__ == "__main__":
    # Initialize client
    client = SmartContractClient(
        contract_id=os.environ.get("CONTRACT_ID", "CXXXXXX"),
        network="testnet"
    )
    
    # Print status
    client.print_status()
    
    # Example: Submit a signal
    # result = client.submit_trading_signal(
    #     from_asset="BTC",
    #     to_asset="USDC",
    #     amount=1_000_000_000,  # 1000 units
    #     expected_return=0.05,   # 5% expected return
    #     risk_score=0.3,         # 30% risk
    #     strategy="MACD",
    #     signer_secret=os.environ["TRADING_AGENT_SECRET"]
    # )

