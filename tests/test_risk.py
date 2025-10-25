import pytest
import time
from agents.risk import RiskAgent, RiskLimits, TradingRecord

class TestRiskAgent:
    def setup_method(self):
        """Setup test fixtures"""
        self.config = {
            'risk': {
                'max_slippage_bps': 30,
                'min_pool_depth_usd': 50000,
                'pool_score_threshold': 0.6,
                'max_trade_usdc': 400,
                'pair_cooldown_sec': 60,
                'daily_max_trades_per_pair': 10
            }
        }
        self.risk_agent = RiskAgent(self.config)

    def test_pool_score_calculation(self):
        """Test pool score calculation"""
        depth_usd = 100000  # Above minimum
        impact_bps = 20     # Below maximum
        vol_z = 2.0         # Moderate volatility
        
        score = self.risk_agent.pool_score(depth_usd, impact_bps, vol_z)
        
        assert 0.0 <= score <= 1.0
        assert score > 0.5  # Should be good score

    def test_guard_function_ok(self):
        """Test guard function returns OK for good conditions"""
        pair = "XLM/USDC"
        planned_usdc = 200.0  # Below limit
        score = 0.8           # Above threshold
        
        action, limits = self.risk_agent.guard(pair, planned_usdc, score)
        
        assert action == "OK"
        assert isinstance(limits, RiskLimits)
        assert limits.max_trade_usdc == 400

    def test_guard_function_halt(self):
        """Test guard function returns HALT for poor conditions"""
        pair = "XLM/USDC"
        planned_usdc = 200.0
        score = 0.4  # Below threshold
        
        action, limits = self.risk_agent.guard(pair, planned_usdc, score)
        
        assert action == "HALT"

    def test_guard_function_reduce(self):
        """Test guard function returns REDUCE for oversized trades"""
        pair = "XLM/USDC"
        planned_usdc = 500.0  # Above limit
        score = 0.8
        
        action, limits = self.risk_agent.guard(pair, planned_usdc, score)
        
        assert action == "REDUCE"

    def test_receive_trading_profit(self):
        """Test receiving trading profit"""
        profit_usdc = 50.0
        trading_details = {
            'pair': 'XLM/USDC',
            'amount_usdc': 100.0,
            'risk_score': 0.5,
            'action': 'stablecoin_conversion'
        }
        
        result = self.risk_agent.receive_trading_profit(profit_usdc, trading_details)
        
        assert result['profit_received'] == 50.0
        assert result['total_profit_usdc'] == 50.0
        assert result['daily_trade_count'] == 1
        assert 'risk_assessment' in result
        assert 'recommendation' in result

    def test_risk_assessment_low_risk(self):
        """Test risk assessment for low risk scenario"""
        # Add some profitable trades
        for i in range(3):
            record = TradingRecord(
                timestamp=time.time() - i * 3600,  # Spread over 3 hours
                pair='XLM/USDC',
                amount_usdc=100.0,
                profit_usdc=10.0,  # Profitable
                risk_score=0.3,
                action='trade'
            )
            self.risk_agent.trading_history.append(record)
        
        assessment = self.risk_agent._assess_risk()
        
        assert assessment['risk_level'] == 'LOW'
        assert assessment['score'] < 0.3

    def test_risk_assessment_high_risk(self):
        """Test risk assessment for high risk scenario"""
        # Add many losing trades to exceed daily limit and create high risk
        for i in range(20):  # Exceed daily limit significantly
            record = TradingRecord(
                timestamp=time.time() - i * 100,
                pair='XLM/USDC',
                amount_usdc=100.0,
                profit_usdc=-5.0,  # Losing trades
                risk_score=0.8,
                action='trade'
            )
            self.risk_agent.trading_history.append(record)
        
        # Manually set daily trade count to exceed limit
        self.risk_agent.daily_trade_count = 15
        
        assessment = self.risk_agent._assess_risk()
        
        assert assessment['risk_level'] == 'HIGH'
        assert assessment['score'] >= 0.6

    def test_should_halt_trading(self):
        """Test trading halt decision"""
        # Initially should not halt
        assert not self.risk_agent.should_halt_trading()
        
        # Add high risk trades
        for i in range(20):
            record = TradingRecord(
                timestamp=time.time() - i * 100,
                pair='XLM/USDC',
                amount_usdc=100.0,
                profit_usdc=-5.0,
                risk_score=0.8,
                action='trade'
            )
            self.risk_agent.trading_history.append(record)
        
        # Manually set daily trade count to exceed limit
        self.risk_agent.daily_trade_count = 15
        
        # Now should halt
        assert self.risk_agent.should_halt_trading()

    def test_get_risk_summary(self):
        """Test comprehensive risk summary"""
        # Add some trading history
        record = TradingRecord(
            timestamp=time.time(),
            pair='XLM/USDC',
            amount_usdc=100.0,
            profit_usdc=10.0,
            risk_score=0.5,
            action='trade'
        )
        self.risk_agent.trading_history.append(record)
        
        summary = self.risk_agent.get_risk_summary()
        
        assert 'current_risk' in summary
        assert 'total_profit_usdc' in summary
        assert 'daily_trade_count' in summary
        assert 'trading_history_count' in summary
        assert 'should_halt' in summary
        assert 'recommendation' in summary

    def test_reset_daily_counters(self):
        """Test daily counter reset"""
        # Set some counters
        self.risk_agent.daily_trade_count = 5
        self.risk_agent.last_reset_date = "2023-01-01"
        
        # Reset counters
        self.risk_agent.reset_daily_counters()
        
        assert self.risk_agent.daily_trade_count == 0
        assert self.risk_agent.last_reset_date == time.strftime("%Y-%m-%d")

    def test_risk_recommendation(self):
        """Test risk recommendations"""
        # Test low risk recommendation
        low_risk_assessment = {'risk_level': 'LOW', 'score': 0.2}
        recommendation = self.risk_agent._get_risk_recommendation(low_risk_assessment)
        assert "Continue trading" in recommendation
        
        # Test medium risk recommendation
        medium_risk_assessment = {'risk_level': 'MEDIUM', 'score': 0.5}
        recommendation = self.risk_agent._get_risk_recommendation(medium_risk_assessment)
        assert "Consider reducing" in recommendation
        
        # Test high risk recommendation
        high_risk_assessment = {'risk_level': 'HIGH', 'score': 0.8}
        recommendation = self.risk_agent._get_risk_recommendation(high_risk_assessment)
        assert "HALT trading" in recommendation

if __name__ == "__main__":
    pytest.main([__file__])
