from stellar_sdk import TransactionBuilder, Network, Asset, LiquidityPoolAsset, Operation
from stellar.wallet import Wallet
from typing import Optional, Dict, Any
import asyncio

class PaymentAgent:
    def __init__(self, wallet: Wallet, config: dict):
        self.w = wallet
        self.config = config

    def send_usdc(self, to: str, amount: str, memo: str | None = None):
        acct = self.w.server.load_account(self.w.public)
        usdc_asset = self.w.asset("USDC", self.config['assets']['usdc']['issuer'])
        tx = (TransactionBuilder(
                source_account=acct, network_passphrase=self.w.passphrase, base_fee=100)
              .append_payment_op(destination=to, amount=amount, asset=usdc_asset)
              .add_text_memo(memo or "")
              .set_timeout(120)
              .build())
        tx.sign(self.w.kp)
        return self.w.server.submit_transaction(tx)

    def swap_via_amm(self, from_asset: str, to_asset: str, amount: str, 
                     min_amount: str, pool_id: str) -> Dict[str, Any]:
        """Swap assets via AMM liquidity pool"""
        try:
            acct = self.w.server.load_account(self.w.public)
            
            # Create liquidity pool asset
            pool_asset = LiquidityPoolAsset.from_xdr(pool_id)
            
            # Create swap operation
            swap_op = Operation.liquidity_pool_withdraw(
                liquidity_pool_id=pool_id,
                amount=amount,
                min_amount_a=min_amount,
                min_amount_b="0"
            )
            
            tx = (TransactionBuilder(
                    source_account=acct, 
                    network_passphrase=self.w.passphrase, 
                    base_fee=100)
                  .append_operation(swap_op)
                  .set_timeout(120)
                  .build())
            
            tx.sign(self.w.kp)
            result = self.w.server.submit_transaction(tx)
            
            return {
                "success": True,
                "transaction_hash": result.get("hash"),
                "amount_out": min_amount,
                "pool_id": pool_id
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "amount_out": "0"
            }

    def path_payment(self, send_asset: str, send_amount: str, 
                    dest_asset: str, dest_amount: str, 
                    destination: str, path: list = None) -> Dict[str, Any]:
        """Execute path payment for optimal routing"""
        try:
            acct = self.w.server.load_account(self.w.public)
            
            # Convert asset strings to Asset objects
            send_asset_obj = self._get_asset_from_string(send_asset)
            dest_asset_obj = self._get_asset_from_string(dest_asset)
            
            # Build path if provided
            path_assets = []
            if path:
                for asset_str in path:
                    path_assets.append(self._get_asset_from_string(asset_str))
            
            tx = (TransactionBuilder(
                    source_account=acct, 
                    network_passphrase=self.w.passphrase, 
                    base_fee=100)
                  .append_path_payment_strict_send_op(
                      destination=destination,
                      send_asset=send_asset_obj,
                      send_amount=send_amount,
                      dest_asset=dest_asset_obj,
                      dest_min=dest_amount,
                      path=path_assets
                  )
                  .set_timeout(120)
                  .build())
            
            tx.sign(self.w.kp)
            result = self.w.server.submit_transaction(tx)
            
            return {
                "success": True,
                "transaction_hash": result.get("hash"),
                "amount_sent": send_amount,
                "amount_received": dest_amount if dest_amount != "0" else send_amount
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "amount_received": "0"
            }

    def _get_asset_from_string(self, asset_str: str) -> Asset:
        """Convert asset string to Asset object"""
        if asset_str == "XLM":
            return Asset.native()
        elif asset_str == "USDC":
            return Asset("USDC", self.config['assets']['usdc']['issuer'])
        elif asset_str == "EURC":
            return Asset("EURC", self.config['assets']['eurc']['issuer'])
        else:
            raise ValueError(f"Unknown asset: {asset_str}")

    async def get_swap_quote(self, from_asset: str, to_asset: str, 
                           amount: str) -> Dict[str, Any]:
        """Get quote for asset swap"""
        try:
            # This would typically query AMM pools or order books
            # For now, return a simple mock quote
            return {
                "success": True,
                "from_asset": from_asset,
                "to_asset": to_asset,
                "amount_in": amount,
                "amount_out": amount,  # Mock 1:1 ratio
                "price_impact": 0.001,  # 0.1% impact
                "slippage": 0.002  # 0.2% slippage
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def convert_to_usdc(self, from_asset: str, amount: str) -> Dict[str, Any]:
        """Convert any asset to USDC"""
        return self.path_payment(
            send_asset=from_asset,
            send_amount=amount,
            dest_asset="USDC",
            dest_amount="0",  # Will be calculated by the network
            destination=self.w.public
        )

    def convert_from_usdc(self, to_asset: str, usdc_amount: str) -> Dict[str, Any]:
        """Convert USDC to any asset"""
        return self.path_payment(
            send_asset="USDC",
            send_amount=usdc_amount,
            dest_asset=to_asset,
            dest_amount="0",  # Will be calculated by the network
            destination=self.w.public
        )