"""
Multi-Agent System with OpenAI Function Calling
Trading strategies as tools for AI agents to use
"""

import asyncio
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import json
from openai import AsyncOpenAI
import os
from agents.trading_strategies import TradingStrategies
from agents.agent_conversation_logger import get_conversation_logger
from news import CryptoNewsFetcher, SentimentAnalyzer, get_global_cache

@dataclass
class TradingSignalWithRisk:
    """Trading signal with risk assessment"""
    signal_id: str
    action: str
    asset: str
    amount: float
    reason: str
    confidence: float
    strategy: str
    var_95: float = 0.0
    cvar_95: float = 0.0
    sharpe_ratio: float = 0.0
    max_drawdown: float = 0.0
    risk_score: float = 0.0
    expected_return: float = 0.0
    risk_adjusted_return: float = 0.0

class MultiAgentOrchestratorWithTools:
    """Multi-Agent Orchestrator using Function Calling"""
    
    def __init__(self, config: dict, trading_agent, risk_agent, payment_agent, tier_manager=None):
        self.config = config
        self.trading_agent = trading_agent
        self.risk_agent = risk_agent
        self.payment_agent = payment_agent
        
        # 🌍 Tier Manager for user-level customization
        self.tier_manager = tier_manager
        self.current_user_tier = tier_manager.default_tier if tier_manager else 'intermediate'
        
        # Initialize OpenAI client
        self.openai_client = AsyncOpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.model = config.get('agent_system', {}).get('model', 'gpt-4-turbo-preview')
        
        # Initialize 10 trading strategies
        self.trading_strategies = TradingStrategies(config)
        
        # Define strategy tools for OpenAI Function Calling
        self.strategy_tools = self._create_strategy_tools()
        
        # 📰 NEW: Initialize news sentiment system
        self.news_fetcher = CryptoNewsFetcher()
        self.sentiment_analyzer = SentimentAnalyzer(method='textblob')  # Free, no API key needed
        self.sentiment_cache = get_global_cache(ttl_minutes=60)  # Cache for 1 hour
        
        # Conversation logger for real-time display
        self.logger = get_conversation_logger()
    
    def get_market_sentiment(self, asset: str) -> Dict:
        """
        Get current market sentiment for asset
        
        Returns cached sentiment or fetches new if expired
        """
        # Check cache first
        cached = self.sentiment_cache.get(asset)
        if cached:
            print(f"📦 Using cached sentiment for {asset}")
            return cached
        
        print(f"🗞️  Fetching news sentiment for {asset}...")
        
        try:
            # Fetch news from last hour
            news = self.news_fetcher.fetch_news(asset, hours=1)
            
            if not news:
                print(f"   No news found for {asset}")
                return {
                    'sentiment': 'neutral',
                    'score': 0.0,
                    'confidence': 0.0,
                    'news_count': 0
                }
            
            # Analyze sentiment
            sentiment = self.sentiment_analyzer.aggregate_sentiment(news)
            
            print(f"   Found {sentiment['news_count']} articles: {sentiment['sentiment']} (score: {sentiment['score']:.2f})")
            
            # Cache result
            self.sentiment_cache.set(asset, sentiment)
            
            return sentiment
        
        except Exception as e:
            print(f"⚠️  Sentiment fetch error for {asset}: {e}")
            return {
                'sentiment': 'neutral',
                'score': 0.0,
                'confidence': 0.0,
                'news_count': 0,
                'error': str(e)
            }
        
    def _create_strategy_tools(self) -> List[Dict]:
        """Create OpenAI function tools from trading strategies"""
        
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "buy_and_hold_strategy",
                    "description": "Long-term buy and hold strategy. Assumes assets will appreciate over time regardless of short-term fluctuations.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "asset": {
                                "type": "string",
                                "description": "Asset symbol (e.g., BTC, ETH, SOL)"
                            }
                        },
                        "required": ["asset"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "macd_strategy",
                    "description": "MACD (Moving Average Convergence Divergence) technical indicator strategy. Identifies trend changes and momentum.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "asset": {
                                "type": "string",
                                "description": "Asset symbol"
                            }
                        },
                        "required": ["asset"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "kdj_rsi_strategy",
                    "description": "KDJ with RSI filter strategy. Combines KDJ and RSI indicators to identify overbought/oversold conditions.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "asset": {
                                "type": "string",
                                "description": "Asset symbol"
                            }
                        },
                        "required": ["asset"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "zscore_mean_reversion",
                    "description": "Z-score mean reversion strategy. Assumes price will revert to mean when deviation is significant.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "asset": {
                                "type": "string",
                                "description": "Asset symbol"
                            }
                        },
                        "required": ["asset"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "lgbm_strategy",
                    "description": "LGBM (Light Gradient Boosting Machine) ML strategy. Uses tree-based models to predict price movements.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "asset": {
                                "type": "string",
                                "description": "Asset symbol"
                            }
                        },
                        "required": ["asset"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "lstm_strategy",
                    "description": "LSTM (Long Short-Term Memory) deep learning strategy. Uses recurrent neural networks for time-series prediction.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "asset": {
                                "type": "string",
                                "description": "Asset symbol"
                            }
                        },
                        "required": ["asset"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "transformer_strategy",
                    "description": "Transformer deep learning strategy. Uses self-attention mechanisms for enhanced price prediction accuracy.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "asset": {
                                "type": "string",
                                "description": "Asset symbol"
                            }
                        },
                        "required": ["asset"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "sac_strategy",
                    "description": "SAC (Soft Actor-Critic) reinforcement learning strategy. Optimizes trading using entropy regularization and soft value functions.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "asset": {
                                "type": "string",
                                "description": "Asset symbol"
                            }
                        },
                        "required": ["asset"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "ppo_strategy",
                    "description": "PPO (Proximal Policy Optimization) RL strategy. Balances exploration and exploitation with stable policy updates.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "asset": {
                                "type": "string",
                                "description": "Asset symbol"
                            }
                        },
                        "required": ["asset"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "dqn_strategy",
                    "description": "DQN (Deep Q-Network) RL strategy. Uses deep neural networks to approximate action-value functions for trading decisions.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "asset": {
                                "type": "string",
                                "description": "Asset symbol"
                            }
                        },
                        "required": ["asset"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "composite_technical_strategy",
                    "description": "🎯 COMPOSITE Technical Strategy (RECOMMENDED). Fuses MACD, RSI, SMA trends, and volume analysis for high-confidence signals. More reliable than individual indicators.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "asset": {
                                "type": "string",
                                "description": "Asset symbol"
                            }
                        },
                        "required": ["asset"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "sentiment_adjusted_strategy",
                    "description": "⭐ SENTIMENT-ADJUSTED Strategy (MOST ADVANCED). Combines composite technical analysis with real-time crypto news sentiment. Adjusts signals based on market news (positive/negative). Use this for best risk-adjusted returns.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "asset": {
                                "type": "string",
                                "description": "Asset symbol"
                            }
                        },
                        "required": ["asset"]
                    }
                }
            }
        ]
        
        return tools
    
    async def _execute_strategy_tool(self, function_name: str, arguments: Dict, market_data: Dict) -> Dict:
        """Execute a strategy tool and return the signal"""
        
        asset = arguments.get('asset', '').upper()
        
        # 📰 NEW: Add sentiment data to market_data for sentiment-adjusted strategies
        if 'sentiment' not in market_data:
            sentiment = self.get_market_sentiment(asset)
            market_data['sentiment'] = sentiment
        
        # Map function names to strategy method names
        strategy_map = {
            'buy_and_hold_strategy': 'buy_and_hold',
            'macd_strategy': 'macd_strategy',
            'kdj_rsi_strategy': 'kdj_rsi_strategy',
            'zscore_mean_reversion': 'zscore_mean_reversion',
            'composite_technical_strategy': 'composite_technical_strategy',  # NEW ✨
            'sentiment_adjusted_strategy': 'sentiment_adjusted_strategy',    # NEW ✨
            'lgbm_strategy': 'lgbm_strategy',
            'lstm_strategy': 'lstm_strategy',
            'transformer_strategy': 'transformer_strategy',
            'sac_strategy': 'sac_strategy',
            'ppo_strategy': 'ppo_strategy',
            'dqn_strategy': 'dqn_strategy'
        }
        
        strategy_method = strategy_map.get(function_name)
        
        if not strategy_method:
            return {"error": f"Unknown strategy: {function_name}"}
        
        try:
            signal = self.trading_strategies.run_strategy(strategy_method, asset, market_data)
            
            return {
                "asset": signal.asset,
                "action": signal.action,
                "strategy": signal.strategy_name,
                "confidence": signal.confidence,
                "strength": signal.strength,
                "expected_return": signal.expected_return,
                "risk_level": signal.risk_level,
                "reasoning": signal.reasoning
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def run_multi_agent_cycle(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run complete Multi-Agent cycle with Function Calling
        1. Trading Agent uses strategy tools to analyze each asset
        2. Trading Agent builds optimal portfolio
        3. Risk Agent evaluates portfolio risk
        4. Payment Agent executes trades
        """
        
        # Start logging
        import uuid
        cycle_id = f"cycle-{uuid.uuid4().hex[:8]}"
        self.logger.start_cycle(cycle_id)
        
        print("\n🤖 Multi-Agent System with Function Tools")
        print("=" * 60)
        
        # Step 1: Trading Agent analyzes market using strategy tools
        print("\n1️⃣ Trading Agent: Analyzing assets using strategy tools...")
        self.logger.log_trading_agent_thought(
            "Analyzing market data to identify trading opportunities across all assets..."
        )
        
        portfolio_signals = await self._trading_agent_with_tools(market_data)
        
        if not portfolio_signals:
            return {
                "status": "NO_SIGNALS",
                "message": "Trading Agent generated no signals"
            }
        
        print(f"   ✅ Generated portfolio with {len(portfolio_signals)} asset signals")
        for sig in portfolio_signals:
            print(f"      {sig['action']} {sig['asset']} - {sig['strategy']} (confidence: {sig.get('confidence', 0):.2f})")
        
        # Step 2: Risk Agent evaluates portfolio
        print("\n2️⃣ Risk Agent: Evaluating portfolio risk...")
        risk_assessment = await self._risk_agent_evaluate_portfolio(portfolio_signals, market_data)
        
        if not risk_assessment.get('approved'):
            return {
                "status": "HIGH_RISK",
                "message": risk_assessment.get('reason', 'Portfolio rejected due to high risk'),
                "risk_assessment": risk_assessment
            }
        
        print(f"   ✅ Portfolio approved with risk score: {risk_assessment.get('risk_score', 0):.2f}")
        
        # Step 3: Payment Agent executes portfolio
        print("\n3️⃣ Payment Agent: Executing portfolio trades...")
        execution_result = await self._payment_agent_execute_portfolio(portfolio_signals, market_data)
        
        print(f"   ✅ Portfolio executed, USDC profit: ${execution_result.get('usdc_profit', 0):.2f}")
        
        return {
            "status": "SUCCESS",
            "portfolio": portfolio_signals,
            "risk_assessment": risk_assessment,
            "execution_result": execution_result,
            "total_usdc_profit": execution_result.get('usdc_profit', 0)
        }
    
    async def _trading_agent_with_tools(self, market_data: Dict) -> List[Dict]:
        """
        Trading Agent uses strategy tools via Function Calling
        Agent decides which strategies to use for each asset
        """
        
        assets = list(market_data.get('assets', {}).keys())
        if not assets:
            assets = self.config.get('portfolio_optimization', {}).get('trading_assets', ['BTC', 'ETH', 'SOL'])
        
        # Filter out USDC (settlement currency)
        assets = [a for a in assets if a.upper() != 'USDC']
        
        # 🌍 Get tier-specific prompt if TierManager is available
        if self.tier_manager:
            base_prompt = self.tier_manager.get_prompt_template('trading', self.current_user_tier)
        else:
            base_prompt = """You are James Simons, founder of Renaissance Technologies, one of the most successful quantitative hedge funds."""
        
        system_prompt = base_prompt + """

Your mission:
1. Analyze each tradable asset in the portfolio
2. For each asset, select and test the most appropriate trading strategies from your toolkit
3. Choose the best strategy for each asset based on current market conditions
4. Construct an optimal portfolio with risk-reward balance

Available strategy tools:
- buy_and_hold_strategy: Long-term appreciation (low risk)
- macd_strategy: Trend following (medium risk)
- kdj_rsi_strategy: Momentum extremes (medium risk)
- zscore_mean_reversion: Mean reversion (low-medium risk)
- lgbm_strategy: ML prediction (medium risk)
- lstm_strategy: Deep learning time-series (medium-high risk)
- transformer_strategy: Advanced DL (medium-high risk)
- sac_strategy: RL exploration-exploitation (high risk)
- ppo_strategy: RL stable learning (medium-high risk)
- dqn_strategy: RL Q-learning (high risk)

Strategy:
1. For volatile assets (BTC, ETH): Test RL and DL strategies
2. For stable growth (SOL, LINK): Test technical indicators
3. For risk management: Include mean reversion strategies
4. Diversify: Don't use same strategy for all assets
5. Build portfolio: Select 1-4 best signals across different assets

Trading Frequency: DAY TRADE MODE
- Minimum holding period: 24 hours (NO intraday trading)
- Rebalance: Daily (check once per day)
- Max trades per day: 5
- Focus on positions that hold for at least 1 full day

Call strategy tools to test each asset, then decide final portfolio composition."""

        # Get current holdings
        current_holdings = market_data.get('current_holdings', {})
        xlm_balance = current_holdings.get('XLM', 0)
        usdc_balance = current_holdings.get('USDC', 0)
        xlm_price = current_holdings.get('xlm_price', 0.31)
        
        # Total available cash = XLM + USDC (USDC can be converted to XLM instantly)
        xlm_value = xlm_balance * xlm_price
        total_cash_available = xlm_value + usdc_balance
        
        holdings_summary = []
        for asset, balance in current_holdings.items():
            if asset not in ['XLM', 'USDC', 'xlm_price'] and balance > 0:
                holdings_summary.append(f"{asset}: {balance:.4f}")
        
        if not holdings_summary:
            if usdc_balance > 0:
                holdings_text = f"""NO CRYPTO HOLDINGS
XLM Balance: {xlm_balance:.2f} (≈${xlm_value:.2f})
USDC Reserve: ${usdc_balance:.2f} (can be converted to XLM for trading)
💰 Total Available Cash: ${total_cash_available:.2f}"""
            else:
                holdings_text = f"NO CRYPTO HOLDINGS - Only XLM: {xlm_balance:.2f} (≈${total_cash_available:.2f} USD cash)"
        else:
            holdings_text = f"""Current Holdings: {', '.join(holdings_summary)}
XLM Balance: {xlm_balance:.2f} (≈${xlm_value:.2f})
USDC Reserve: ${usdc_balance:.2f}
💰 Total Available Cash: ${total_cash_available:.2f}"""
        
        # Update cash_available to include USDC
        cash_available = total_cash_available

        user_prompt = f"""Market Data:
Portfolio Value: ${market_data.get('portfolio_value', 0):,.2f}

**CURRENT HOLDINGS**:
{holdings_text}

⚠️ IMPORTANT: You currently hold NO crypto assets (only cash in XLM/USDC).
💡 NOTE: USDC is a liquid stablecoin that can be instantly converted to XLM for trading.
   Your TOTAL available buying power = XLM + USDC
Action Required: You must BUY assets to enter positions. HOLD is only valid if you already own the asset.

Available Assets for Trading: {', '.join(assets)}

Asset Prices and Data:
{json.dumps(market_data.get('assets', {}), indent=2)}

Task:
1. For each asset, call 2-3 relevant strategy tools to test different approaches
2. Compare strategy results for each asset
3. Select 3-5 assets to BUY for proper diversification
4. Build a well-diversified portfolio considering:
   
   📊 **PORTFOLIO REQUIREMENTS**:
   - **Number of Assets**: 3-5 different cryptocurrencies (NOT just 1-2!)
   - **Capital Utilization**: Allocate 80-95% of ${cash_available:.2f} (NOT just 10-20%!)
   - **Diversification**: Mix large-cap (BTC, ETH) with mid-cap assets
   - **Strategy Diversity**: Use different strategies across assets
   - **Risk Balance**: Blend high-confidence and medium-confidence opportunities
   
   💡 **ALLOCATION EXAMPLE**:
   - Large cap (BTC, ETH): 30-40% each
   - Mid cap (SOL, LINK, AAVE, etc.): 10-20% each
   - Total: Minimum 3 assets, aim for 90%+ capital utilization

Note: 
- You MUST use BUY action (not HOLD) since you have no existing positions
- Diversification is CRITICAL - don't put all eggs in one basket!
- Utilize most of your capital - $1M sitting idle is a waste!

Start by calling strategy tools to analyze which assets to BUY."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        # Allow multiple rounds of tool calls
        max_rounds = 5
        all_tool_results = []
        
        for round_num in range(max_rounds):
            response = await self.openai_client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=self.strategy_tools,
                tool_choice="auto",
                temperature=0.7
            )
            
            assistant_message = response.choices[0].message
            messages.append(assistant_message)
            
            # Check if agent wants to call tools
            if assistant_message.tool_calls:
                print(f"   🔧 Round {round_num + 1}: Agent calling {len(assistant_message.tool_calls)} strategy tools...")
                
                for tool_call in assistant_message.tool_calls:
                    function_name = tool_call.function.name
                    arguments = json.loads(tool_call.function.arguments)
                    
                    print(f"      → {function_name}({arguments.get('asset', 'N/A')})")
                    
                    # Log tool call
                    self.logger.log_trading_agent_tool_call(function_name, arguments)
                    
                    # Execute the strategy tool
                    result = await self._execute_strategy_tool(function_name, arguments, market_data)
                    all_tool_results.append(result)
                    
                    # Log tool result
                    if 'error' not in result:
                        self.logger.log_tool_result(function_name, result)
                    
                    # Add tool result to conversation
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(result)
                    })
            else:
                # Agent finished calling tools, get final decision
                break
        
        # Get final portfolio decision
        final_prompt = f"""Based on the strategy tool results, provide your final portfolio decision.

REMINDER - YOUR CURRENT SITUATION:
{holdings_text}
Available Cash: ${cash_available:.2f}

⚠️ CRITICAL MANDATE - READ CAREFULLY:
1. You have NO crypto holdings (only cash in XLM)
2. You MUST recommend at least 3-5 BUY actions for DIVERSIFICATION
3. You CANNOT return an empty portfolio or all HOLD/SELL actions
4. Even if strategies show mixed signals, you MUST pick the best opportunities and BUY
5. Your job is to INVEST the available cash, not sit idle!

🚫 FORBIDDEN RESPONSES:
- "no actionable BUY signals" ← NOT ACCEPTABLE
- "preserve capital and avoid entering positions" ← NOT YOUR JOB
- "awaiting clearer signals" ← NOT ALLOWED when you have $1M cash
- Empty portfolio [] ← WILL BE REJECTED
- Only 1-2 assets in portfolio ← INSUFFICIENT DIVERSIFICATION

✅ REQUIRED ACTION - PORTFOLIO CONSTRUCTION RULES:
1. **DIVERSIFICATION**: Select 3-5 different assets (not just 1-2!)
2. **CAPITAL UTILIZATION**: Allocate 80-95% of available cash (not just 10-20%!)
3. **RISK BALANCE**: Mix high-confidence assets (BTC, ETH) with medium-cap opportunities
4. **STRATEGY DIVERSITY**: Use different strategies across assets (not all SAC)
5. **ALLOCATION GUIDELINES**:
   - Primary assets (BTC, ETH): 30-40% each
   - Secondary assets (SOL, LINK, etc.): 10-20% each
   - Minimum 3 assets, maximum 5 assets

💡 EXAMPLE GOOD PORTFOLIO:
- BTC (35%, SAC strategy) - Large cap, stable
- ETH (30%, DQN strategy) - Large cap, growth
- SOL (15%, MACD strategy) - Mid cap, momentum
- LINK (10%, LGBM strategy) - Mid cap, diversification
- AAVE (10%, Transformer) - DeFi exposure
Total: 5 assets, 100% capital utilized, well-diversified

All Strategy Results:
{json.dumps(all_tool_results, indent=2)}

REQUIRED: Return JSON with at least 1 BUY action:
{{
    "portfolio": [
        {{
            "asset": "ASSET_CODE",
            "action": "BUY",  ← MUST be BUY since you have no holdings
            "strategy": "strategy_name",
            "amount": dollar_amount_to_invest,
            "asset_price": current_price_in_usd,
            "confidence": 0.0-1.0,
            "expected_return": percentage,
            "risk_score": 0-10,
            "reasoning": "why this asset and strategy"
        }}
    ],
    "portfolio_reasoning": "overall portfolio construction logic"
}}

Example valid portfolio (use actual prices from market data):
{{
    "portfolio": [
        {{"asset": "BTC", "action": "BUY", "amount": 1500, "asset_price": 45000, "confidence": 0.8, "risk_score": 6}},
        {{"asset": "ETH", "action": "BUY", "amount": 1000, "asset_price": 2500, "confidence": 0.75, "risk_score": 5}}
    ]
}}

INVALID portfolios (will fail execution):
- action="HOLD" ← You don't own anything to hold!
- action="SELL" ← You don't own anything to sell!"""

        messages.append({"role": "user", "content": final_prompt})
        
        final_response = await self.openai_client.chat.completions.create(
            model=self.model,
            messages=messages,
            response_format={"type": "json_object"},
            temperature=0.7
        )
        
        final_content = final_response.choices[0].message.content
        final_decision = json.loads(final_content)
        
        portfolio = final_decision.get('portfolio', [])
        reasoning = final_decision.get('portfolio_reasoning', '')
        
        # 🔧 FIX: Ensure all portfolio signals have asset_price with fallback from market_data
        for signal in portfolio:
            if 'asset_price' not in signal or signal['asset_price'] is None or signal['asset_price'] == 0:
                asset = signal.get('asset', '').upper()
                # Try to get price from market_data
                asset_price_data = market_data.get('assets', {}).get(asset.lower(), {})
                signal['asset_price'] = asset_price_data.get('price', 50000.0)  # Fallback to 50K
                print(f"   🔧 Added missing asset_price for {asset}: ${signal['asset_price']:.2f}")
        
        if reasoning:
            print(f"\n   💡 Portfolio Logic: {reasoning[:150]}...")
            self.logger.log_trading_agent_decision(reasoning, portfolio)
        
        return portfolio
    
    async def _risk_agent_evaluate_portfolio(self, portfolio: List[Dict], market_data: Dict) -> Dict:
        """Risk Agent evaluates the entire portfolio"""
        
        self.logger.log_risk_agent_thought(
            "Evaluating portfolio risk metrics: concentration, diversification, strategy balance..."
        )
        
        # 🌍 Get tier-specific prompt if TierManager is available
        if self.tier_manager:
            base_prompt = self.tier_manager.get_prompt_template('risk', self.current_user_tier)
        else:
            base_prompt = """You are a professional Risk Manager at a top-tier hedge fund."""
        
        system_prompt = base_prompt + """

Your responsibility:
1. Evaluate portfolio-level risk metrics
2. Check for concentration risk
3. Assess strategy diversification
4. Ensure risk limits are not breached
5. Approve or reject the portfolio

Risk Limits:
- Min diversification: 3-5 assets (portfolios should be diversified)
- Max single asset: 50% of portfolio (no over-concentration)
- Max high-risk strategies (RL/DL): 60% of portfolio
- Max portfolio risk score: 8.0/10
- Capital utilization: 80-95% of available cash should be allocated
- IMPORTANT: APPROVE well-diversified portfolios (3+ assets) even if individual risk scores are medium
- TRADING INTENT: BUY actions with clear diversification are EXCELLENT
- REJECT: Portfolios with only 1-2 assets or < 50% capital utilization"""

        user_prompt = f"""Portfolio to Evaluate:
{json.dumps(portfolio, indent=2)}

Market Data:
Portfolio Value: ${market_data.get('portfolio_value', 0):,.2f}

Evaluate:
1. Position sizing and concentration
2. Strategy type diversification
3. Overall risk-reward profile
4. Compliance with risk limits

**IMPORTANT**: Be pragmatic and approve portfolios that:
- Have reasonable strategy logic (even single asset is OK)
- Stay within the relaxed risk limits above
- Show trading intent: BUY or SELL (single HOLD is acceptable if confidence is high)
- Have risk scores under 9.0/10
- NOTE: Single-asset focused strategies are VALID for concentrated trading approaches

Return JSON:
{{
    "approved": true/false,
    "risk_score": 0-10,
    "concentration_check": "pass/fail",
    "diversification_check": "pass/fail",
    "strategy_balance": "analysis",
    "reason": "approval/rejection reason",
    "recommendations": ["list of suggestions"]
}}"""

        response = await self.openai_client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.3
        )
        
        content = response.choices[0].message.content
        result = json.loads(content)
        
        # Log detailed risk analysis before decision
        risk_details = f"""
📊 Risk Analysis Details:
- Risk Score: {result.get('risk_score', 0):.2f}/10
- Concentration Check: {result.get('concentration_check', 'N/A')}
- Diversification Check: {result.get('diversification_check', 'N/A')}
- Strategy Balance: {result.get('strategy_balance', 'N/A')}
- Portfolio Size: {len(portfolio)} assets
- Recommendations: {', '.join(result.get('recommendations', []))}
"""
        self.logger.log_risk_agent_thought(risk_details.strip())
        
        # Log final decision
        self.logger.log_risk_agent_decision(
            result.get('approved', False),
            result.get('reason', ''),
            result.get('risk_score', 0)
        )
        
        return result
    
    async def _payment_agent_execute_portfolio(self, portfolio: List[Dict], market_data: Dict) -> Dict:
        """Payment Agent executes portfolio trades"""
        
        print("\n   💰 Payment Agent: Executing trades on Stellar...")
        self.logger.log_payment_agent_action(
            f"Starting execution of {len(portfolio)} trades"
        )
        
        executed_trades = []
        failed_trades = []
        total_xlm_spent = 0
        
        for signal in portfolio:
            try:
                asset = signal.get('asset', '').upper()
                action = signal.get('action', '').upper()
                amount_usd = float(signal.get('amount', 0))
                
                if action == 'BUY' and amount_usd > 0:
                    print(f"      🔄 Attempting to buy {asset} worth ${amount_usd:.2f}...")
                    self.logger.log_payment_agent_action(
                        f"Executing BUY {asset} for ${amount_usd:.2f}"
                    )
                    
                    # Get real-time XLM price from market data (ensure it's a float)
                    xlm_price = float(market_data.get('current_holdings', {}).get('xlm_price', 0.31))
                    xlm_amount = amount_usd / xlm_price
                    
                    # Get asset price for simulation update
                    asset_price = signal.get('asset_price', 50000.0)  # fallback price
                    
                    # Try to update simulated balance IMMEDIATELY to check if we have enough
                    try:
                        # Access AssetManager from trading agent (passed via config)
                        # This is a workaround - in production, Payment Agent should have its own balance check
                        from stellar.assets import AssetManager
                        asset_manager = self.trading_agent.asset_manager if hasattr(self.trading_agent, 'asset_manager') else None
                        
                        if asset_manager and asset_manager.simulation_mode:
                            # 💰 AUTO-CONVERT USDC TO XLM IF NEEDED
                            current_xlm = float(asset_manager.simulated_balances.get('xlm', 0))
                            current_usdc = float(asset_manager.simulated_balances.get('usdc', 0))
                            
                            if current_xlm < xlm_amount:
                                # Need more XLM - convert USDC
                                xlm_deficit = xlm_amount - current_xlm
                                usd_deficit = xlm_deficit * xlm_price
                                
                                if current_usdc >= usd_deficit:
                                    # Convert USDC to XLM
                                    print(f"      💱 Converting ${usd_deficit:.2f} USDC → {xlm_deficit:.2f} XLM for trade")
                                    # Ensure keys exist before modifying
                                    if 'usdc' not in asset_manager.simulated_balances:
                                        asset_manager.simulated_balances['usdc'] = 0.0
                                    if 'xlm' not in asset_manager.simulated_balances:
                                        asset_manager.simulated_balances['xlm'] = 3200000.0
                                    asset_manager.simulated_balances['usdc'] = float(asset_manager.simulated_balances['usdc']) - usd_deficit
                                    asset_manager.simulated_balances['xlm'] = float(asset_manager.simulated_balances['xlm']) + xlm_deficit
                                    self.logger.log_payment_agent_action(
                                        f"💱 Converted ${usd_deficit:.2f} USDC → {xlm_deficit:.2f} XLM"
                                    )
                                else:
                                    print(f"      ⚠️  Warning: Insufficient funds (XLM: {current_xlm:.2f}, USDC: ${current_usdc:.2f})")
                            
                            # Try to update balance - returns True/False
                            success = asset_manager.update_simulated_trade(
                                asset=asset,
                                action=action,
                                usd_amount=amount_usd,
                                price=asset_price
                            )
                            
                            if success:
                                executed_trades.append({
                                    "asset": asset,
                                    "action": action,
                                    "usd_amount": amount_usd,
                                    "xlm_spent": xlm_amount,
                                    "asset_price": asset_price,
                                    "status": "SIMULATED_SUCCESS",
                                    "message": f"Successfully bought {asset} for {xlm_amount:.2f} XLM"
                                })
                                total_xlm_spent += xlm_amount
                                print(f"      ✅ {asset}: Buy successful - ${amount_usd:.2f} ({xlm_amount:.2f} XLM)")
                                self.logger.log_payment_agent_action(
                                    f"✅ SUCCESS: Bought {asset} for ${amount_usd:.2f}"
                                )
                            else:
                                # Insufficient balance
                                failed_trades.append({
                                    "asset": asset,
                                    "action": action,
                                    "usd_amount": amount_usd,
                                    "reason": "Insufficient XLM balance"
                                })
                                print(f"      ❌ {asset}: Buy FAILED - Insufficient XLM!")
                                self.logger.log_payment_agent_action(
                                    f"❌ FAILED: {asset} buy rejected (insufficient XLM)"
                                )
                        else:
                            # No asset manager available - just record
                            executed_trades.append({
                                "asset": asset,
                                "action": action,
                                "usd_amount": amount_usd,
                                "xlm_spent": xlm_amount,
                                "asset_price": asset_price,
                                "status": "SIMULATED",
                                "message": f"Simulated: Would buy {asset} for {xlm_amount:.2f} XLM"
                            })
                            total_xlm_spent += xlm_amount
                            print(f"      ✅ {asset}: Simulated buy of ${amount_usd:.2f} ({xlm_amount:.2f} XLM)")
                            self.logger.log_payment_agent_action(
                                f"✅ SIMULATED: Bought {asset} for ${amount_usd:.2f}"
                            )
                    except Exception as e:
                        print(f"      ⚠️  {asset}: Error during trade execution: {e}")
                        failed_trades.append({
                            "asset": asset,
                            "action": action,
                            "usd_amount": amount_usd,
                            "reason": str(e)
                        })
                        self.logger.log_payment_agent_action(
                            f"❌ ERROR: {asset} trade failed: {e}"
                        )
                    
                elif action == 'SELL' and amount_usd > 0:
                    print(f"      🔄 Selling {asset} worth ${amount_usd:.2f}...")
                    # Similar logic for SELL
                    executed_trades.append({
                        "asset": asset,
                        "action": action,
                        "usd_amount": amount_usd,
                        "status": "SIMULATED",
                        "message": f"Simulated: Would sell {asset}"
                    })
                    print(f"      ✅ {asset}: Simulated sell")
                    
                else:
                    # HOLD or invalid action
                    print(f"      ⏸️  {asset}: {action} - No execution needed")
                    
            except Exception as e:
                print(f"      ❌ {signal.get('asset', 'Unknown')}: Error - {e}")
                failed_trades.append({
                    "asset": signal.get('asset', 'Unknown'),
                    "error": str(e)
                })
                self.logger.log_payment_agent_action(
                    f"❌ Failed to execute {signal.get('asset', 'Unknown')}: {e}"
                )
        
        result = {
            "success": len(executed_trades) > 0,
            "trades_executed": len(executed_trades),
            "trades_failed": len(failed_trades),
            "executed_trades": executed_trades,
            "failed_trades": failed_trades,
            "total_xlm_spent": total_xlm_spent,
            "usdc_profit": 0,  # Will be calculated after trades settle
            "note": "⚠️ SIMULATED EXECUTION - Real Stellar transactions not yet implemented"
        }
        
        print(f"\n   📊 Execution Summary:")
        print(f"      ✅ Successful: {len(executed_trades)}")
        print(f"      ❌ Failed: {len(failed_trades)}")
        print(f"      💸 Total XLM to spend: {total_xlm_spent:.2f} XLM (≈${total_xlm_spent * 0.31:.2f})")
        print(f"      ⚠️  Note: Transactions are SIMULATED (not executed on chain)")
        
        return result


def get_multi_agent_orchestrator_with_tools(config: dict, trading_agent, risk_agent, payment_agent, tier_manager=None):
    """Factory function to create orchestrator with function tools"""
    return MultiAgentOrchestratorWithTools(config, trading_agent, risk_agent, payment_agent, tier_manager)

