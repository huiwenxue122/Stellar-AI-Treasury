# 🌟 Stellar AI Treasury

**AI-Powered Multi-Agent Quantitative Trading System on Stellar Blockchain**

> An autonomous quantitative trading platform that combines **GPT-4o AI agents** with **Stellar Soroban smart contracts** to deliver transparent, secure, and intelligent portfolio management. Three specialized AI agents (Trading, Risk, Payment) collaborate in real-time, executing 10 advanced strategies while a custom Rust smart contract enforces risk limits on-chain. V2.0 features include on-chain trade history, strategy performance tracking, and portfolio snapshots—creating a complete audit trail on Stellar testnet.
One link for demo you can quick visit demo:https://abc123.ngrok.io 
[![Stellar](https://img.shields.io/badge/Stellar-Soroban-blue)](https://stellar.org)
[![Python](https://img.shields.io/badge/Python-3.11-green)](https://python.org)
[![Rust](https://img.shields.io/badge/Rust-Soroban-orange)](https://rust-lang.org)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o-purple)](https://openai.com)

[![Live on Testnet](https://img.shields.io/badge/Testnet-Live-success)](https://stellar.expert/explorer/testnet/contract/CCK3NFUGKRJIE242FXHE2HHPI6AB2HQS6DUDYCWQIVUBSWCBGGGAQ6UJ)
[![Contract V2.0](https://img.shields.io/badge/Contract-V2.0-brightgreen)]()
[![Lines of Code](https://img.shields.io/badge/Smart%20Contract-570%2B%20lines-orange)]()

---

## 📖 Overview

Stellar AI Treasury combines **AI multi-agent systems** with **Stellar smart contracts** to create a transparent, secure, and automated quantitative trading platform.

### The Problem
- Traditional quantitative trading systems are **black boxes**
- Centralized systems lack **transparency**
- Risk management happens **after the fact**

### Our Solution
**AI + Blockchain Integration**

- **AI Agents (GPT-4o)**: Generate intelligent trading signals using OpenAI's latest model
- **Stellar Smart Contract V2.0**: Enforce risk limits & record performance on-chain
- **Multi-Agent Collaboration**: Trading + Risk + Payment agents working together
- **Real-time Transparency**: Watch AI decision-making process live in the dashboard

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                 📊 Dashboard (Streamlit)                 │
│  • Real-time Agent Conversation UI                      │
│  • Portfolio Visualization & P&L Tracking               │
│  • 20+ Risk Metrics Display (VaR, Sharpe, Drawdown)     │
│  • Multi-language Support (EN/中文)                      │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│      🤖 Multi-Agent AI System (Python + GPT-4o)         │
│                                                          │
│  ┌──────────────┐   ┌───────────┐   ┌──────────────┐   │
│  │   Trading    │ → │   Risk    │ → │   Payment    │   │
│  │    Agent     │   │   Agent   │   │    Agent     │   │
│  ├──────────────┤   ├───────────┤   ├──────────────┤   │
│  │ 10 Strategies│   │ 20+ Metrics│   │ Stellar SDK  │   │
│  │ • LSTM, DQN  │   │ • VaR      │   │ • Path Pay   │   │
│  │ • MACD, PPO  │   │ • Sharpe   │   │ • USDC       │   │
│  │ • SAC, B&H   │   │ • MaxDD    │   │              │   │
│  └──────────────┘   └───────────┘   └──────────────┘   │
│                                                          │
│  📡 OpenAI Function Calling for Strategy Selection      │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│       🔐 Soroban Smart Contract V2.0 (Rust)             │
│                                                          │
│  ✅ Multi-Agent Authorization (3 signatures)            │
│  ✅ Risk Enforcement (VaR, Sharpe, Drawdown)            │
│  ✅ Emergency Halt & Dynamic Stop-Loss                  │
│  📝 On-Chain Trade History (NEW V2.0)                   │
│  🏆 Strategy Performance Tracking (NEW V2.0)            │
│  📸 Portfolio Snapshots (NEW V2.0)                      │
│                                                          │
│  Contract ID: CCK3NF...GGAQ6UJ (570+ lines custom)      │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│              🌐 Stellar Testnet                         │
│  • Horizon API (Real-time Market Data)                  │
│  • Stellar DEX (Historical OHLCV Data)                  │
│  • Path Payments (Optimal Asset Conversion)             │
│  • USDC Settlement                                      │
└─────────────────────────────────────────────────────────┘
```

---

## ✨ Key Features

### 🤖 AI Multi-Agent System
- **Trading Agent** (James Simons personality)
  - 10 quantitative strategies (LSTM, DQN, MACD, PPO, etc.)
  - OpenAI Function Calling for intelligent strategy selection
  - Portfolio optimization with risk-reward balance

- **Risk Agent**
  - 20+ risk metrics (VaR, CVaR, Sharpe Ratio, Max Drawdown)
  - Real-time monitoring (slippage, liquidity, anomalies)
  - Automatic trading halt on risk threshold breach

- **Payment Agent**
  - Stellar SDK integration
  - Path payment optimization
  - USDC settlement

### 🛡️ Custom Smart Contract V2.0 (Soroban) - NOT Boilerplate!

**Deployed Contract ID**: `CCK3NFUGKRJIE242FXHE2HHPI6AB2HQS6DUDYCWQIVUBSWCBGGGAQ6UJ`  
**Version**: 2.0 (Enhanced - October 2024)  
**Network**: Stellar Testnet  
**[View on Stellar Expert](https://stellar.expert/explorer/testnet/contract/CCK3NFUGKRJIE242FXHE2HHPI6AB2HQS6DUDYCWQIVUBSWCBGGGAQ6UJ)**

**✨ NEW V2.0 Features** (October 26, 2024):
- 📝 **On-Chain Trade History**: Permanent audit trail of all executed trades
- 🏆 **Strategy Performance Tracking**: Win rate, profit, Sharpe ratio per AI strategy
- 📸 **Portfolio Snapshots**: Historical portfolio value and ROI tracking
- 🛑 **Dynamic Stop-Loss**: AI-triggered position protection

**Custom Features** (NOT found in any boilerplate/template contracts):

1. **Multi-Agent Signature Verification** 🤖
   ```rust
   // THREE separate AI agents must sign SEQUENTIALLY
   trading_agent.require_auth();  // 1️⃣ Generate trading signal
   risk_agent.require_auth();     // 2️⃣ Approve risk assessment
   payment_agent.require_auth();  // 3️⃣ Execute payment
   // This enforces a complete AI agent workflow on-chain!
   ```

2. **Quantitative Risk Limits Enforcement** 📊
   ```rust
   // On-chain enforcement of advanced quant metrics
   if risk_metrics.var_95 > config.max_var_95 { return false; }
   if risk_metrics.sharpe_ratio < config.min_sharpe_ratio { return false; }
   if risk_metrics.max_drawdown < -2000 { return false; }  // -20%
   // Prevents any trade that violates quantitative risk thresholds
   ```

3. **AI Strategy Recording & Confidence Tracking** 🧠
   ```rust
   pub struct TradingSignal {
       asset: String,
       action: String,        // "BUY", "SELL", "HOLD"
       strategy: String,      // "LSTM", "DQN", "MACD", "SAC", "PPO", etc.
       confidence: u32,       // AI confidence score (0-100)
       expected_return: i32,  // Expected return in basis points
   }
   // Records WHICH AI strategy made the decision - full transparency!
   ```

4. **AI-Triggered Circuit Breaker** 🚨
   ```rust
   pub fn emergency_halt(env: Env) {
       config.risk_agent.require_auth();  // Risk Agent can halt
       config.halted = true;              // Stop all trading
   }
   // Risk Agent AI can autonomously halt trading on anomaly detection
   ```

5. **Dynamic Risk Parameter Updates** ⚙️
   ```rust
   pub fn update_risk_limits(
       env: Env,
       max_var_95: i32,      // Adjustable VaR limit
       min_sharpe_ratio: i32 // Adjustable Sharpe requirement
   ) {
       config.admin.require_auth();
       // Admin can tune risk parameters based on market conditions
   }
   ```

6. **🆕 On-Chain Trade History** 📝
   ```rust
   pub struct TradeRecord {
       trade_id: u64,
       asset: String,
       strategy: String,     // Which AI strategy executed this
       executed_at: u64,     // Timestamp
       profit_loss: i128,    // Realized P&L
   }
   pub fn get_trade(env: Env, trade_id: u64) -> TradeRecord
   // Permanent audit trail - every trade recorded on-chain!
   ```

7. **🆕 Strategy Performance Tracking** 🏆
   ```rust
   pub struct StrategyPerformance {
       strategy_name: String,  // "LSTM", "DQN", "MACD", etc.
       total_trades: u32,
       winning_trades: u32,    // Win rate calculation
       total_profit: i128,     // Cumulative profit
       sharpe_ratio: i32,      // Strategy-specific Sharpe
   }
   pub fn get_strategy_performance(env: Env, strategy: String) -> StrategyPerformance
   // Track which AI strategies perform best on-chain!
   ```

8. **🆕 Portfolio Snapshots** 📸
   ```rust
   pub struct PortfolioSnapshot {
       timestamp: u64,
       total_value: i128,         // Portfolio value at snapshot
       cumulative_return: i32,    // Total ROI since inception
       total_trades: u64,         // Number of trades executed
   }
   pub fn create_snapshot(...) -> u64
   pub fn get_latest_snapshot(env: Env) -> PortfolioSnapshot
   // Historical portfolio tracking on-chain!
   ```

9. **🆕 Dynamic Stop-Loss** 🛑
   ```rust
   pub struct RiskMetrics {
       stop_loss_level: i32,  // Current stop-loss level (basis points)
   }
   pub fn set_dynamic_stop_loss(env: Env, enabled: bool)
   // AI can dynamically adjust stop-loss based on market conditions!
   ```

**Why This is Custom, Not Boilerplate:**
- ✅ Designed specifically for AI multi-agent trading systems
- ✅ Integrates quantitative finance risk metrics (VaR, Sharpe, Drawdown)
- ✅ Records AI strategy names, confidence scores, AND performance
- ✅ Three-layer agent authorization (not standard wallet signing)
- ✅ AI-triggered emergency halt mechanism
- ✅ On-chain trade history with permanent audit trail
- ✅ Strategy performance tracking (win rate, profit per strategy)
- ✅ Portfolio snapshots for historical ROI tracking
- ✅ **570+ lines of custom Rust code** (V2.0, not a template)
- ✅ Deployed and operational on Stellar testnet
- ✅ **Implemented October 26, 2024** (latest version)

**Contract Functions** (17 custom functions in V2.0):
```
✅ Core: initialize(), get_config(), is_operational()
✅ Trading: submit_trading_signal(), approve_trade(), execute_trade()
✅ Risk: emergency_halt(), resume_trading(), update_risk_limits(), set_dynamic_stop_loss()
✅ History: get_trade(), get_total_trades() [NEW]
✅ Analytics: get_strategy_performance() [NEW]
✅ Snapshots: create_snapshot(), get_latest_snapshot() [NEW]
Plus internal helper functions
```

### 🌐 Stellar Integration
- Horizon API for real-time data
- Historical trade data from Stellar DEX
- Path payment for optimal asset conversion
- USDC settlement for all trades

---

## 🛠️ Tech Stack

### Frontend
- **Streamlit** - Interactive web dashboard
- **Plotly** - Data visualization
- **Pandas** - Data manipulation

### AI & Machine Learning
- **OpenAI GPT-4o** - Multi-agent decision making
- **LightGBM, LSTM, Transformers** - ML/DL strategies
- **Reinforcement Learning** - SAC, PPO, DQN algorithms
- **Thompson Sampling** - Strategy selection

### Blockchain
- **Stellar Network** - Testnet for development
- **Soroban Smart Contracts** - Custom Rust contracts
- **Horizon API** - Real-time blockchain data
- **Stellar SDK (Python)** - Transaction management

### Risk & Analytics
- **NumPy, SciPy** - Quantitative calculations
- **Custom Risk Engine** - VaR, CVaR, Sharpe, Drawdown
- **Real-time Monitoring** - Anomaly detection

### Data & Sentiment
- **News API** - Market sentiment analysis
- **Sentiment Cache** - Performance optimization
- **Historical OHLCV** - 15-minute candlestick data

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Rust (for smart contract)
- Stellar CLI
- OpenAI API key

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/stellar-ai-treasury.git
   cd stellar-ai-treasury
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your keys:
   # - STELLAR_SECRET
   # - STELLAR_PUBLIC
   # - OPENAI_API_KEY
   ```

4. **Build the smart contract**
   ```bash
   cd contracts/ai_treasury_vault
   stellar contract build
   ```

5. **Run the dashboard**
   ```bash
   python smart_start.py
   ```

### Usage

1. **Configure Assets**: Select trading assets (BTC, ETH, SOL, etc.)
2. **Initialize System**: Connect to Stellar testnet
3. **Run Trading Cycle**: Watch AI agents collaborate in real-time
4. **Monitor**: View live agent conversations in "🤖 AI Agents" tab

---

## 📊 Trading Strategies

### Technical Indicators
- **Buy-and-Hold (B&H)**: Long-term appreciation strategy
- **MACD**: Moving Average Convergence Divergence
- **KDJ & RSI**: Momentum extremes detection
- **Z-score Mean Reversion**: Statistical arbitrage

### Machine Learning / Deep Learning
- **LGBM**: Light Gradient Boosting Machine
- **LSTM**: Long Short-Term Memory networks
- **Transformer**: Self-attention mechanisms

### Reinforcement Learning
- **SAC**: Soft Actor-Critic
- **PPO**: Proximal Policy Optimization
- **DQN**: Deep Q-Network

---

## 🛡️ Risk Management

### Portfolio Risk Metrics
- Value at Risk (VaR) - 95%, 99%
- Conditional VaR (CVaR)
- Sharpe Ratio
- Sortino Ratio
- Maximum Drawdown
- Portfolio Volatility
- Alpha & Beta
- Calmar Ratio

### Real-time Monitoring
- Slippage tracking
- Liquidity depth analysis
- Anomaly detection (price spikes, volume anomalies)
- Automatic trading halt on risk breach

---

## 📁 Project Structure

```
stellar-ai-treasury_v2/
├── 📱 app/                                      # Frontend Application
│   ├── dashboard.py                            # Main Streamlit UI
│   ├── orchestrator.py                         # System coordinator
│   ├── agent_conversation_ui.py                # Real-time AI chat UI
│   ├── localization.py                         # Multi-language support
│   ├── tier_manager.py                         # User tier system
│   ├── wallet_connector.py                     # Freighter wallet integration
│   ├── config.yaml                             # System configuration
│   └── assets_config.yaml                      # Asset definitions
│
├── 🤖 agents/                                   # AI Agent System
│   ├── agent_system_with_function_tools.py     # Multi-agent orchestrator
│   ├── trading_strategies.py                   # 10 quantitative strategies
│   ├── enhanced_trading_strategies.py          # Advanced ML/DL strategies
│   ├── risk.py                                 # 20+ risk metrics
│   ├── advanced_risk_agent.py                  # Deep risk analysis
│   ├── payment.py                              # Stellar payment execution
│   ├── portfolio_optimizer.py                  # Portfolio optimization
│   └── agent_conversation_logger.py            # Conversation tracking
│
├── 🔐 contracts/                                # Smart Contracts ⭐
│   └── ai_treasury_vault/
│       ├── Cargo.toml                          # Rust dependencies
│       └── src/
│           └── lib.rs                          # V2.0 Contract (570+ lines)
│
├── 🌐 stellar/                                  # Stellar Integration
│   ├── smart_contract_client.py                # V2.0 contract client
│   ├── wallet.py                               # Wallet management
│   ├── horizon.py                              # Horizon API client
│   ├── historical_data.py                      # OHLCV data fetcher
│   ├── market_data.py                          # Real-time market data
│   ├── price_oracle.py                         # Price aggregation
│   └── assets.py                               # Asset definitions
│
├── 📊 data/                                     # Market Data
│   ├── stellar_ohlc_15m_BTC.csv               # Bitcoin historical data
│   ├── stellar_ohlc_15m_ETH.csv               # Ethereum historical data
│   ├── stellar_ohlc_15m_SOL.csv               # Solana historical data
│   └── ...                                     # Other crypto assets
│
├── 📰 news/                                     # Sentiment Analysis
│   ├── news_fetcher.py                         # News API integration
│   ├── sentiment_analyzer.py                   # AI sentiment analysis
│   └── sentiment_cache.py                      # Sentiment caching
│
├── 🎯 selector/                                 # Strategy Selection
│   ├── thompson_selector.py                    # Thompson Sampling
│   └── context_features.py                     # Contextual features
│
├── 📈 strategies/                               # Strategy Framework
│   ├── base.py                                 # Base strategy class
│   ├── library.py                              # Strategy library
│   └── middleware.py                           # Strategy middleware
│
├── 🧪 tests/                                    # Unit Tests
│   ├── test_payment.py
│   ├── test_risk.py
│   └── test_trading_rules.py
│
├── 📚 docs/                                     # Documentation
│   ├── architecture.md                         # System architecture
│   └── metrics.md                              # Risk metrics guide
│
├── 🚀 smart_start.py                            # Main entry point
├── 📋 requirements.txt                          # Python dependencies
├── 📖 README.md                                 # This file
├── 📝 PROJECT_SUMMARY.md                        # Detailed project summary
├── 🔧 SETUP_GUIDE.md                            # Installation guide
├── 🛡️ SECURITY.md                              # Security practices
├── 📦 SMART_CONTRACT_MIGRATION_GUIDE.md        # Contract migration
└── ⚖️ RISK_MANAGEMENT_SYSTEM.md                # Risk system details
```

---

## 🧪 Testing

### Run Unit Tests
```bash
# Python tests
pytest tests/

# Smart contract tests
cd contracts/ai_treasury_vault
cargo test
```

### Test with Real Data
```bash
# Test function calling with live market data
python test_function_calling_with_real_data.py
```

---

## 🔗 Smart Contract Deployment

### Build
```bash
cd contracts/ai_treasury_vault
stellar contract build
```

### Deploy to Testnet
```bash
stellar contract deploy \
  --wasm target/wasm32-unknown-unknown/release/ai_treasury_vault.wasm \
  --source YOUR_SECRET_KEY \
  --network testnet
```

### Initialize Contract
```bash
stellar contract invoke \
  --id CONTRACT_ID \
  --network testnet \
  -- initialize \
  --admin ADMIN_ADDRESS \
  --trading_agent TRADING_AGENT_ADDRESS \
  --risk_agent RISK_AGENT_ADDRESS \
  --payment_agent PAYMENT_AGENT_ADDRESS \
  --max_single_trade 1000000
```

---

## 🎯 Stellar Requirements Compliance

### ✅ Built with smart contracts on Stellar
- **Contract ID**: `CCK3NFUGKRJIE242FXHE2HHPI6AB2HQS6DUDYCWQIVUBSWCBGGGAQ6UJ`
- **Network**: Stellar Testnet (verified on Stellar Explorer)
- **Status**: Deployed, initialized, and operational
- All AI trading decisions verified through smart contract
- Risk limits enforced on-chain before any trade execution
- Contract manages multi-agent treasury vault workflow

### ✅ Custom (not boilerplate) smart contract
**570+ lines of custom Rust code (V2.0)** designed specifically for AI trading:

**Unique Features NOT found in any template/boilerplate:**
- ✅ **Multi-Agent Sequential Authorization**: 3 separate AI agents must sign
- ✅ **Quantitative Risk Enforcement**: On-chain VaR, Sharpe, Drawdown checks
- ✅ **AI Strategy Recording**: Records which AI strategy (LSTM, DQN, etc.) made decision
- ✅ **AI-Triggered Circuit Breaker**: Risk Agent can autonomously halt system
- ✅ **Dynamic Risk Parameters**: Admin can adjust risk limits per market conditions
- ✅ **🆕 On-Chain Trade History**: Permanent audit trail with P&L tracking
- ✅ **🆕 Strategy Performance Analytics**: Win rate, profit, Sharpe per strategy
- ✅ **🆕 Portfolio Snapshots**: Historical value and ROI tracking
- ✅ **🆕 Dynamic Stop-Loss**: AI-adjustable position protection
- ✅ **17 Custom Functions** (V2.0): Far beyond standard token/payment contracts

**Source Code**: See `contracts/ai_treasury_vault/src/lib.rs` (committed to repo)
**Version**: 2.0 - Implemented October 26, 2024

### ✅ Fully-functioning (as evidenced in demo)
- ✅ **Compiles**: `cargo build --target wasm32-unknown-unknown --release`
- ✅ **Tests Pass**: `cargo test` (5 comprehensive tests in V2.0)
- ✅ **Deployed**: Live on Stellar testnet with Contract ID above
- ✅ **Callable**: Python backend calls contract via SmartContractClientV2
- ✅ **Integrated**: Trading cycle records history & tracks performance on-chain
- ✅ **Demo-Ready**: Watch V2.0 features (snapshots, strategy tracking) in logs

---

## 📖 Documentation

### Main Documentation
- **[📝 Project Summary](PROJECT_SUMMARY.md)** - Comprehensive project overview with tier system details
- **[🔧 Setup Guide](SETUP_GUIDE.md)** - Step-by-step installation instructions
- **[⚖️ Risk Management System](RISK_MANAGEMENT_SYSTEM.md)** - Detailed risk metrics and enforcement
- **[🛡️ Security](SECURITY.md)** - Security best practices and considerations
- **[📦 Smart Contract Migration Guide](SMART_CONTRACT_MIGRATION_GUIDE.md)** - How to deploy to other projects

### Architecture Documentation
- **[🏗️ Architecture](docs/architecture.md)** - System design and component interaction
- **[📊 Risk Metrics](docs/metrics.md)** - Complete risk metrics reference

### Smart Contract V2.0
- **[Contract Source Code](contracts/ai_treasury_vault/src/lib.rs)** - 570+ lines of custom Rust
- **[View on Stellar Expert](https://stellar.expert/explorer/testnet/contract/CCK3NFUGKRJIE242FXHE2HHPI6AB2HQS6DUDYCWQIVUBSWCBGGGAQ6UJ)** - Live testnet deployment

---

## 🎥 Demo Video

### 📹 Watch the Full System in Action

[![Watch Demo Video](https://img.shields.io/badge/▶️_Watch-Demo_Video-red?style=for-the-badge&logo=youtube)](https://youtu.be/bI2uUp7cqa8)

> **📺 [Click here to watch the full demo on YouTube](https://youtu.be/bI2uUp7cqa8)**  
> _Duration: ~5 minutes | Shows: AI agents, smart contract, risk management_

**How to create your demo video:**
1. Start the dashboard: `python smart_start.py`
2. Configure your portfolio (select BTC, ETH, SOL, etc.)
3. Set your tier (Beginner/Intermediate/Advanced) and initial capital
4. Click "🚀 Run Trading Cycle" and screen record the process
5. Switch to "🤖 AI Agents" tab to show real-time AI conversations
6. Show the "🛡️ Risk" tab displaying 20+ risk metrics
7. Demonstrate the Smart Contract verification in logs

**What to showcase in your video:**
- ✅ AI Multi-Agent collaboration (Trading, Risk, Payment)
- ✅ Real-time strategy selection (LSTM, DQN, MACD, etc.)
- ✅ Custom Smart Contract verification on Stellar
- ✅ Risk metrics calculation (VaR, Sharpe, CVaR)
- ✅ Portfolio execution and USDC settlement

### Live Demo: Watch AI Agents Work Together

Console output during a trading cycle:
```
🤖 Trading Agent: Calling 10 strategy tools...
   → lstm_strategy(BTC) → BUY (confidence: 0.85)
   → dqn_strategy(ETH) → BUY (confidence: 0.78)
   → macd_strategy(SOL) → HOLD (confidence: 0.62)
   
💡 Portfolio: Selected 5 assets with diversification

🛡️ Risk Agent: Evaluating portfolio risk...
   VaR(95%): 3.2% ✅ | Sharpe: 1.5 ✅ | MaxDD: -8% ✅
   ✅ APPROVED - Risk within limits

🔗 Smart Contract V2.0: Recording & Verifying...
   ✅ Smart Contract is operational
   📊 Risk Metrics: VaR=320bps, Sharpe=150, MaxDD=-800bps
   ✅ On-chain risk validation passed
   📸 Portfolio Snapshot: $100,000.00, 5 assets, Return=150bps
   🏆 Strategies used: LSTM, DQN, MACD
   💡 Strategy performance tracking active on-chain
   📝 Total on-chain trades: 15

💰 Payment Agent: Executing trades...
   ✅ BTC: Buy successful - $30,000
   ✅ ETH: Buy successful - $30,000
   ✅ SOL: Buy successful - $15,000
```

---

## 🆚 Why Choose Stellar AI Treasury?

### Comparison with Traditional Systems

| Feature | Traditional Trading Bots | Centralized Funds | **Stellar AI Treasury** |
|---------|-------------------------|-------------------|------------------------|
| **Transparency** | ❌ Black box | ❌ Limited reporting | ✅ Real-time AI conversation visible |
| **Risk Control** | ⚠️ After-the-fact | ⚠️ Manual intervention | ✅ On-chain enforcement before execution |
| **AI Integration** | ❌ Rule-based only | ⚠️ Basic algorithms | ✅ GPT-4o multi-agent system |
| **Blockchain** | ❌ Not on-chain | ❌ Centralized | ✅ Stellar smart contracts |
| **Audit Trail** | ⚠️ Can be altered | ⚠️ Internal logs | ✅ Permanent on-chain history |
| **Strategy Tracking** | ❌ No tracking | ⚠️ Aggregated only | ✅ Per-strategy performance on-chain |
| **Emergency Halt** | ⚠️ Manual only | ⚠️ Manual only | ✅ AI-triggered automatic halt |
| **Cost** | 💰 High fees | 💰💰 Management fees | 💚 Open source, minimal gas |
| **Customization** | ❌ Fixed strategies | ❌ No control | ✅ 10+ strategies, adaptive |
| **Multi-language** | ❌ English only | ❌ English only | ✅ English + 中文 |

### V2.0 Enhancements (October 2024)

| Feature | V1.0 | **V2.0 (Current)** |
|---------|------|-------------------|
| **Lines of Code** | ~250 lines | ✅ **570+ lines** |
| **Trade History** | ❌ Off-chain only | ✅ **Permanent on-chain audit trail** |
| **Strategy Analytics** | ❌ No tracking | ✅ **Win rate, profit, Sharpe per strategy** |
| **Portfolio Snapshots** | ❌ Not recorded | ✅ **Historical value & ROI on-chain** |
| **Dynamic Stop-Loss** | ❌ Static only | ✅ **AI-adjustable position protection** |
| **Functions** | 8 functions | ✅ **17 custom functions** |
| **Tests** | 3 basic tests | ✅ **5 comprehensive tests** |

---

## 🏆 Innovation Highlights

### 🚀 Technical Excellence
- **First-of-its-kind**: AI Multi-Agent + Stellar Soroban smart contract integration for quantitative trading
- **On-Chain Risk Enforcement**: Pre-execution risk validation using VaR, Sharpe, and Drawdown limits
- **GPT-4o Function Calling**: Advanced AI strategy selection with 10+ quantitative algorithms
- **Permanent Audit Trail**: Every trade recorded on Stellar blockchain (V2.0 feature)
- **Strategy Performance Tracking**: Win rate, profit, and Sharpe ratio per AI strategy on-chain
- **Multi-Agent Sequential Authorization**: Three AI agents must approve trades sequentially

### 💎 User Value
- **🔍 Transparency**: Watch AI agents collaborate in real-time through dashboard
- **🛡️ Security**: Smart contract enforces risk limits BEFORE any trade execution
- **🤖 Automation**: Fully automated portfolio optimization and trade execution
- **📊 Analytics**: Historical performance tracking with on-chain portfolio snapshots
- **🌐 Accessibility**: Multi-tier system (Beginner/Intermediate/Advanced)
- **🌍 Multi-language**: English and 中文 support
- **💰 Cost-Effective**: Open source, minimal blockchain fees, no management fees

### 🎯 Stellar Ecosystem Contribution
- Demonstrates advanced Soroban smart contract capabilities
- Showcases real-world AI + blockchain integration
- Provides open-source reference implementation for quantitative finance on Stellar
- Expands Stellar use cases beyond payments into algorithmic trading

---

## ❓ FAQ

### General Questions

**Q: Is this a real trading system or just a demo?**  
A: Currently deployed on Stellar **testnet** for demonstration and testing. The system is fully functional and can be adapted for mainnet deployment with proper risk management and auditing.

**Q: Do I need real money to try it?**  
A: No! The system runs on Stellar testnet with test XLM (free from Stellar Friendbot). No real funds required.

**Q: What's the difference between simulation mode and on-chain mode?**  
A: **Simulation mode** runs all AI logic locally without blockchain transactions (faster, free). **On-chain mode** records trades and risk validation to the Soroban smart contract (permanent audit trail).

### Technical Questions

**Q: How does the AI make trading decisions?**  
A: GPT-4o orchestrates three AI agents: Trading Agent runs 10 quantitative strategies (LSTM, DQN, MACD, etc.) via OpenAI Function Calling → Risk Agent validates with 20+ metrics → Payment Agent executes on Stellar.

**Q: What makes the smart contract "custom" and not boilerplate?**  
A: Our contract has **570+ lines** of custom Rust code with features NOT in any template:
- Multi-agent sequential authorization
- Quantitative risk enforcement (VaR, Sharpe, Drawdown)
- On-chain trade history & strategy performance tracking
- AI-triggered emergency halt
- Dynamic stop-loss mechanism

**Q: Can I add my own trading strategies?**  
A: Yes! Add strategies to `agents/trading_strategies.py` following the existing pattern. The OpenAI Function Calling system will automatically discover and use them.

**Q: What cryptocurrencies are supported?**  
A: BTC, ETH, SOL, XLM, LINK, ARB, AAVE, LDO, FET + stablecoins (USDC, USDT) and RWAs (EURC, PAX Gold). Configure in `app/assets_config.yaml`.

### Deployment Questions

**Q: How do I deploy my own smart contract?**  
A: Follow the deployment guide in [SMART_CONTRACT_MIGRATION_GUIDE.md](SMART_CONTRACT_MIGRATION_GUIDE.md). You'll need Rust, Stellar CLI, and a funded testnet account.

**Q: Can I use this on Stellar mainnet?**  
A: Technically yes, but **NOT RECOMMENDED** without:
- Comprehensive security audit
- Extended testnet validation
- Legal compliance review
- Professional risk management oversight

**Q: What are the system requirements?**  
A: Python 3.11+, 4GB+ RAM, OpenAI API key, Stellar CLI (for contract deployment). Works on macOS, Linux, and Windows WSL.

---

## 🤝 Contributing

We welcome contributions! Here's how you can help:

### Ways to Contribute
- 🐛 **Bug Reports**: Open an issue with detailed reproduction steps
- ✨ **Feature Requests**: Suggest new strategies, risk metrics, or UI improvements
- 📝 **Documentation**: Improve guides, add examples, fix typos
- 🔧 **Code**: Submit PRs for bug fixes or new features
- 🌍 **Translations**: Add support for more languages

### Development Setup
```bash
git clone https://github.com/YOUR_USERNAME/stellar-ai-treasury.git
cd stellar-ai-treasury
pip install -r requirements.txt
cp .env.example .env  # Add your API keys
python smart_start.py
```

### Pull Request Guidelines
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request with a clear description

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

**Disclaimer**: This is experimental software for educational purposes. NOT FINANCIAL ADVICE. Use at your own risk. The authors are not responsible for any financial losses.

---

## 🔗 Useful Links

### Stellar Ecosystem
- 🌐 **Stellar Network**: https://stellar.org
- 🦀 **Soroban Docs**: https://soroban.stellar.org
- 🔍 **Stellar Expert**: https://stellar.expert
- 💧 **Friendbot (Testnet XLM)**: https://laboratory.stellar.org/#account-creator

### AI & ML
- 🤖 **OpenAI Platform**: https://openai.com
- 📚 **GPT-4o API Docs**: https://platform.openai.com/docs

### Development Tools
- 🛠️ **Stellar CLI**: https://developers.stellar.org/docs/tools/developer-tools
- 🐍 **Stellar SDK Python**: https://github.com/StellarCN/py-stellar-base
- 🎨 **Streamlit**: https://streamlit.io

### Our Project
- 📦 **Live Smart Contract**: [View on Stellar Expert](https://stellar.expert/explorer/testnet/contract/CCK3NFUGKRJIE242FXHE2HHPI6AB2HQS6DUDYCWQIVUBSWCBGGGAQ6UJ)
- 📝 **Project Summary**: [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)
- 🔧 **Setup Guide**: [SETUP_GUIDE.md](SETUP_GUIDE.md)

---

## 📧 Contact & Support

### Get Help
- 💬 **GitHub Issues**: [Open an issue](https://github.com/YOUR_USERNAME/stellar-ai-treasury/issues) for bugs or questions
- 📖 **Documentation**: Check our comprehensive guides in the repo
- 💡 **Discussions**: Join GitHub Discussions for feature ideas

### Follow Updates
- ⭐ **Star this repo** to stay updated
- 👁️ **Watch** for new releases
- 🍴 **Fork** to customize for your use case

### Acknowledgments
Built for the **Stellar Hackoween Hackathon** 🎃  
Special thanks to the Stellar Development Foundation for creating an amazing blockchain ecosystem!

---

**Built with ❤️ for the Stellar ecosystem**

*Combining the power of AI and blockchain for transparent, secure, and intelligent trading*
