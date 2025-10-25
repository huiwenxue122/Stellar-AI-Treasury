from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from stellar.assets import AssetManager
from agents.payment import PaymentAgent
from agents.multi_asset_strategy import MultiAssetStrategy, TradeAction
from stellar.price_oracle import PriceOracle

@dataclass
class TradingSignal:
    action: str  # "BUY", "SELL", "CONVERT_TO_USDC", "CONVERT_FROM_USDC", "HOLD"
    asset: str
    amount: float
    reason: str
    confidence: float

class TradingAgent:
    def __init__(self, cfg: dict, asset_manager: AssetManager, payment_agent: PaymentAgent):
        self.cfg = cfg
        self.asset_manager = asset_manager
        self.payment_agent = payment_agent
        self.volatility_threshold_high = cfg.get('stablecoin', {}).get('volatility_threshold_high', 0.3)
        self.volatility_threshold_low = cfg.get('stablecoin', {}).get('volatility_threshold_low', 0.15)
        self.usdc_allocation_target = cfg.get('stablecoin', {}).get('usdc_allocation_target', 30.0)
        
        # 初始化多资产策略
        self.multi_asset_strategy = MultiAssetStrategy(cfg, asset_manager, asset_manager.price_oracle)

    def ema(self, arr, n):
        if not arr: return None
        k = 2/(n+1)
        v = arr[0]
        for x in arr[1:]: v = x*k + v*(1-k)
        return v

    def s1_momentum(self, prices: list[float], vol_z: float, impact_bps: float) -> bool:
        p_fast = self.ema(prices, self.cfg['strategy']['s1']['ema_fast'])
        p_slow = self.ema(prices, self.cfg['strategy']['s1']['ema_slow'])
        if p_fast is None or p_slow is None: return False
        cross = p_fast > p_slow
        return cross and vol_z > self.cfg['strategy']['s1']['vol_z_min'] and impact_bps < 25

    def s2_revert(self, impact_gap_bps: float, depth_ok: bool) -> bool:
        return depth_ok and impact_gap_bps > self.cfg['strategy']['s2']['impact_gap_bps_in']

    def s3_path_improve(self, better_bps: float) -> bool:
        return better_bps >= self.cfg['strategy']['s3']['path_improve_bps_min']

    def analyze_stablecoin_strategy(self) -> Optional[TradingSignal]:
        """Analyze if we should convert to/from USDC based on volatility"""
        current_usdc_allocation = self.asset_manager.get_usdc_allocation()
        
        # Check if we should convert to USDC (high volatility)
        if self.asset_manager.should_convert_to_usdc(self.volatility_threshold_high):
            target_asset = self.asset_manager.get_asset_to_convert()
            if target_asset and self.asset_manager.assets[target_asset].balance > 0:
                return TradingSignal(
                    action="CONVERT_TO_USDC",
                    asset=target_asset,
                    amount=self.asset_manager.assets[target_asset].balance,
                    reason=f"High volatility detected ({self.asset_manager.assets[target_asset].volatility:.3f})",
                    confidence=0.8
                )
        
        # Check if we should convert from USDC (low volatility)
        elif (self.asset_manager.should_convert_from_usdc(self.volatility_threshold_low) and 
              current_usdc_allocation > self.usdc_allocation_target):
            usdc_balance = self.asset_manager.assets['usdc'].balance
            if usdc_balance > 0:
                # Find the asset with lowest volatility to convert to
                best_asset = self._find_best_asset_for_conversion()
                if best_asset:
                    return TradingSignal(
                        action="CONVERT_FROM_USDC",
                        asset=best_asset,
                        amount=usdc_balance * 0.5,  # Convert 50% of USDC
                        reason=f"Low volatility environment, converting to {best_asset}",
                        confidence=0.7
                    )
        
        return None

    def _find_best_asset_for_conversion(self) -> Optional[str]:
        """Find the best asset to convert USDC to based on volatility and potential"""
        best_asset = None
        best_score = float('inf')
        
        for asset_name, asset_info in self.asset_manager.assets.items():
            if asset_name != 'usdc' and asset_info.price_usd > 0:
                # Score based on low volatility and reasonable price
                score = asset_info.volatility * 0.7 + (1.0 / asset_info.price_usd) * 0.3
                if score < best_score:
                    best_score = score
                    best_asset = asset_name
        
        return best_asset

    def generate_trading_signals(self, market_data: Dict[str, Any]) -> List[TradingSignal]:
        """Generate all trading signals including stablecoin strategy"""
        signals = []
        
        # First check stablecoin strategy
        stablecoin_signal = self.analyze_stablecoin_strategy()
        if stablecoin_signal:
            signals.append(stablecoin_signal)
        
        # Then check traditional trading strategies
        prices = market_data.get('prices', [])
        vol_z = market_data.get('volatility_zscore', 0.0)
        impact_bps = market_data.get('impact_bps', 0.0)
        impact_gap_bps = market_data.get('impact_gap_bps', 0.0)
        depth_ok = market_data.get('depth_ok', False)
        better_bps = market_data.get('better_bps', 0.0)
        
        # Strategy 1: Momentum
        if self.s1_momentum(prices, vol_z, impact_bps):
            signals.append(TradingSignal(
                action="BUY",
                asset="XLM",  # Default asset, should be configurable
                amount=100.0,  # Default amount, should be calculated
                reason="Momentum strategy triggered",
                confidence=0.6
            ))
        
        # Strategy 2: Mean reversion
        if self.s2_revert(impact_gap_bps, depth_ok):
            signals.append(TradingSignal(
                action="SELL",
                asset="XLM",
                amount=50.0,
                reason="Mean reversion strategy triggered",
                confidence=0.5
            ))
        
        # Strategy 3: Path improvement
        if self.s3_path_improve(better_bps):
            signals.append(TradingSignal(
                action="BUY",
                asset="XLM",
                amount=75.0,
                reason="Path improvement opportunity",
                confidence=0.4
            ))
        
        return signals

    async def execute_trading_signals(self, signals: List[TradingSignal]) -> Dict[str, Any]:
        """Execute trading signals and return results"""
        results = []
        total_profit_usdc = 0.0
        
        for signal in signals:
            try:
                if signal.action == "CONVERT_TO_USDC":
                    result = self.payment_agent.convert_to_usdc(
                        signal.asset, 
                        str(signal.amount)
                    )
                    if result['success']:
                        results.append({
                            "signal": signal,
                            "result": result,
                            "profit_usdc": float(result.get('amount_received', 0))
                        })
                        total_profit_usdc += float(result.get('amount_received', 0))
                
                elif signal.action == "CONVERT_FROM_USDC":
                    result = self.payment_agent.convert_from_usdc(
                        signal.asset,
                        str(signal.amount)
                    )
                    if result['success']:
                        results.append({
                            "signal": signal,
                            "result": result,
                            "profit_usdc": 0.0  # No immediate profit from conversion
                        })
                
                elif signal.action in ["BUY", "SELL"]:
                    # For traditional trading, we'll implement this later
                    # For now, just log the signal
                    results.append({
                        "signal": signal,
                        "result": {"success": True, "message": "Signal logged"},
                        "profit_usdc": 0.0
                    })
                
            except Exception as e:
                results.append({
                    "signal": signal,
                    "result": {"success": False, "error": str(e)},
                    "profit_usdc": 0.0
                })
        
        return {
            "executed_signals": results,
            "total_profit_usdc": total_profit_usdc,
            "success_count": len([r for r in results if r['result'].get('success', False)])
        }

    async def complete_trading_cycle(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Complete a full trading cycle: analyze, execute, convert profits to USDC"""
        # Generate signals
        signals = self.generate_trading_signals(market_data)
        
        # Execute signals
        execution_results = await self.execute_trading_signals(signals)
        
        # Convert any profits to USDC for risk management
        if execution_results['total_profit_usdc'] > 0:
            # The profits are already in USDC from the conversion operations
            pass
        
        return {
            "signals_generated": len(signals),
            "execution_results": execution_results,
            "final_usdc_profit": execution_results['total_profit_usdc']
        }
    
    async def run_multi_asset_strategy(self, account_address: str, 
                                      market_conditions: Dict[str, float]) -> Dict[str, Any]:
        """
        运行多资产交易策略
        包括再平衡和动量交易
        """
        all_signals = []
        
        # 1. 生成再平衡信号
        rebalance_signals = await self.multi_asset_strategy.generate_rebalance_signals(
            account_address, 
            market_conditions
        )
        all_signals.extend(rebalance_signals)
        
        # 2. 检查配置限制
        allocations, total_value = await self.multi_asset_strategy.calculate_portfolio_allocation(account_address)
        warnings = self.multi_asset_strategy.check_allocation_limits(allocations)
        
        # 3. 获取市场数据并生成动量信号
        market_data = {}
        for asset_name in self.cfg['assets'].keys():
            # 获取价格历史（模拟）
            asset_config = self.cfg['assets'][asset_name]
            prices = self.asset_manager.price_oracle.get_price_history(asset_config['code'], 30)
            if prices:
                market_data[asset_name] = [p['price'] for p in prices]
        
        if market_data:
            momentum_signals = await self.multi_asset_strategy.generate_momentum_signals(market_data)
            all_signals.extend(momentum_signals)
        
        # 4. 执行信号（转换为TradingSignal格式）
        trading_signals = []
        for signal in all_signals:
            ts = TradingSignal(
                action=signal.action.value.upper(),
                asset=signal.asset,
                amount=signal.amount_usdc / signal.price if signal.price > 0 else 0,
                reason=signal.reason,
                confidence=signal.confidence
            )
            trading_signals.append(ts)
        
        # 执行交易
        execution_results = await self.execute_trading_signals(trading_signals)
        
        return {
            "total_value_usdc": total_value,
            "allocations": {k: {
                "type": v.asset_type.value,
                "value_usdc": v.current_value_usdc,
                "weight": v.current_weight
            } for k, v in allocations.items()},
            "warnings": warnings,
            "signals_generated": len(all_signals),
            "rebalance_signals": len(rebalance_signals),
            "momentum_signals": len(all_signals) - len(rebalance_signals),
            "execution_results": execution_results,
            "profit_usdc": execution_results['total_profit_usdc']
        }
    
    async def get_portfolio_summary(self, account_address: str) -> Dict[str, Any]:
        """获取投资组合摘要（按资产类型分组）"""
        allocations, total_value = await self.multi_asset_strategy.calculate_portfolio_allocation(account_address)
        
        # 按类型分组
        by_type = {}
        for asset_name, alloc in allocations.items():
            asset_type = alloc.asset_type.value
            if asset_type not in by_type:
                by_type[asset_type] = {
                    "total_value": 0.0,
                    "total_weight": 0.0,
                    "assets": []
                }
            
            by_type[asset_type]["total_value"] += alloc.current_value_usdc
            by_type[asset_type]["total_weight"] += alloc.current_weight
            by_type[asset_type]["assets"].append({
                "name": asset_name,
                "value": alloc.current_value_usdc,
                "weight": alloc.current_weight
            })
        
        return {
            "total_value_usdc": total_value,
            "by_type": by_type,
            "asset_count": len(allocations)
        }