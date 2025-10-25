import pytest
import asyncio
from unittest.mock import Mock, AsyncMock
from agents.trading import TradingAgent, TradingSignal
from stellar.assets import AssetManager, AssetInfo
from agents.payment import PaymentAgent

class TestTradingRules:
    def setup_method(self):
        """Setup test fixtures"""
        self.config = {
            'strategy': {
                's1': {'ema_fast': 5, 'ema_slow': 20, 'vol_z_min': 1.0},
                's2': {'impact_gap_bps_in': 20},
                's3': {'path_improve_bps_min': 15}
            },
            'stablecoin': {
                'volatility_threshold_high': 0.3,
                'volatility_threshold_low': 0.15,
                'usdc_allocation_target': 30.0
            }
        }
        
        # Mock dependencies
        self.mock_asset_manager = Mock(spec=AssetManager)
        self.mock_payment_agent = Mock(spec=PaymentAgent)
        
        # Setup asset manager mock
        self.mock_asset_manager.assets = {
            'usdc': AssetInfo('USDC', 'issuer1', 1000.0, 1.0, 0.0),
            'xlm': AssetInfo('XLM', None, 1000.0, 0.1, 0.2),
            'eurc': AssetInfo('EURC', 'issuer2', 500.0, 1.1, 0.4)
        }
        self.mock_asset_manager.get_usdc_allocation.return_value = 50.0
        self.mock_asset_manager.should_convert_to_usdc.return_value = False
        self.mock_asset_manager.should_convert_from_usdc.return_value = False
        self.mock_asset_manager.get_asset_to_convert.return_value = None
        
        self.trading_agent = TradingAgent(
            self.config, 
            self.mock_asset_manager, 
            self.mock_payment_agent
        )

    def test_ema_calculation(self):
        """Test EMA calculation"""
        prices = [1.0, 1.1, 1.05, 1.2, 1.15]
        ema_5 = self.trading_agent.ema(prices, 5)
        assert ema_5 is not None
        assert ema_5 > 0

    def test_s1_momentum_strategy(self):
        """Test momentum strategy (S1)"""
        prices = [1.0, 1.01, 1.02, 1.03, 1.04, 1.05]  # Upward trend
        vol_z = 1.5  # Above threshold
        impact_bps = 20  # Below threshold
        
        result = self.trading_agent.s1_momentum(prices, vol_z, impact_bps)
        assert result is True

    def test_s2_revert_strategy(self):
        """Test mean reversion strategy (S2)"""
        impact_gap_bps = 25  # Above threshold
        depth_ok = True
        
        result = self.trading_agent.s2_revert(impact_gap_bps, depth_ok)
        assert result is True

    def test_s3_path_improve_strategy(self):
        """Test path improvement strategy (S3)"""
        better_bps = 20  # Above threshold
        
        result = self.trading_agent.s3_path_improve(better_bps)
        assert result is True

    def test_stablecoin_strategy_high_volatility(self):
        """Test conversion to USDC when volatility is high"""
        # Setup high volatility scenario
        self.mock_asset_manager.should_convert_to_usdc.return_value = True
        self.mock_asset_manager.get_asset_to_convert.return_value = 'eurc'
        self.mock_asset_manager.assets['eurc'].volatility = 0.4
        
        signal = self.trading_agent.analyze_stablecoin_strategy()
        
        assert signal is not None
        assert signal.action == "CONVERT_TO_USDC"
        assert signal.asset == "eurc"
        assert "High volatility" in signal.reason

    def test_stablecoin_strategy_low_volatility(self):
        """Test conversion from USDC when volatility is low"""
        # Setup low volatility scenario
        self.mock_asset_manager.should_convert_to_usdc.return_value = False
        self.mock_asset_manager.should_convert_from_usdc.return_value = True
        self.mock_asset_manager.get_usdc_allocation.return_value = 60.0  # Above target
        self.mock_asset_manager.assets['usdc'].balance = 1000.0
        
        # Mock the best asset selection
        self.trading_agent._find_best_asset_for_conversion = Mock(return_value='xlm')
        
        signal = self.trading_agent.analyze_stablecoin_strategy()
        
        assert signal is not None
        assert signal.action == "CONVERT_FROM_USDC"
        assert signal.asset == "xlm"
        assert signal.amount == 500.0  # 50% of USDC balance

    def test_generate_trading_signals(self):
        """Test signal generation with market data"""
        market_data = {
            'prices': [1.0, 1.01, 1.02, 1.03, 1.04],
            'volatility_zscore': 1.5,
            'impact_bps': 15.0,
            'impact_gap_bps': 25.0,
            'depth_ok': True,
            'better_bps': 20.0
        }
        
        signals = self.trading_agent.generate_trading_signals(market_data)
        
        assert isinstance(signals, list)
        # Should have at least one signal (momentum strategy should trigger)
        assert len(signals) >= 1

    @pytest.mark.asyncio
    async def test_execute_trading_signals(self):
        """Test signal execution"""
        # Mock payment agent responses
        self.mock_payment_agent.convert_to_usdc.return_value = {
            'success': True,
            'amount_received': '100.0'
        }
        
        signals = [
            TradingSignal(
                action="CONVERT_TO_USDC",
                asset="xlm",
                amount=100.0,
                reason="Test conversion",
                confidence=0.8
            )
        ]
        
        results = await self.trading_agent.execute_trading_signals(signals)
        
        assert results['total_profit_usdc'] == 100.0
        assert results['success_count'] == 1
        assert len(results['executed_signals']) == 1

    @pytest.mark.asyncio
    async def test_complete_trading_cycle(self):
        """Test complete trading cycle"""
        market_data = {
            'prices': [1.0, 1.01, 1.02, 1.03, 1.04],
            'volatility_zscore': 1.5,
            'impact_bps': 15.0,
            'impact_gap_bps': 25.0,
            'depth_ok': True,
            'better_bps': 20.0
        }
        
        # Mock the execute_trading_signals method
        self.trading_agent.execute_trading_signals = AsyncMock(return_value={
            'executed_signals': [],
            'total_profit_usdc': 50.0,
            'success_count': 1
        })
        
        results = await self.trading_agent.complete_trading_cycle(market_data)
        
        assert results['signals_generated'] >= 0
        assert results['final_usdc_profit'] == 50.0
        assert 'execution_results' in results

if __name__ == "__main__":
    pytest.main([__file__])
