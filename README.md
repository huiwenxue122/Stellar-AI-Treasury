# 🌟 Stellar AI Treasury

**AI-Powered Multi-Agent Quantitative Trading System on Stellar Blockchain**

[![Stellar](https://img.shields.io/badge/Stellar-Soroban-blue)](https://stellar.org)
[![Python](https://img.shields.io/badge/Python-3.11-green)](https://python.org)
[![Rust](https://img.shields.io/badge/Rust-Soroban-orange)](https://rust-lang.org)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4-purple)](https://openai.com)

---

## 📖 Overview

Stellar AI Treasury combines **AI multi-agent systems** with **Stellar smart contracts** to create a transparent, secure, and automated quantitative trading platform.

### The Problem
- Traditional quantitative trading systems are **black boxes**
- Centralized systems lack **transparency**
- Risk management happens **after the fact**

### Our Solution
**AI + Blockchain Integration**

- **AI Agents (GPT-4)**: Generate intelligent trading signals
- **Stellar Smart Contract**: Enforce risk limits on-chain
- **Multi-Agent Collaboration**: Trading + Risk + Payment agents working together

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│  Dashboard (Streamlit)                  │
│  - Real-time Agent Conversation         │
│  - Portfolio Visualization              │
│  - Risk Metrics Display                 │
└─────────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────────┐
│  Multi-Agent AI System (Python + GPT-4) │
│                                          │
│  Trading Agent → Risk Agent → Payment   │
│  (10 Strategies)  (20+ Metrics)         │
└─────────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────────┐
│  Soroban Smart Contract (Rust)          │
│  - Multi-signature control              │
│  - Risk limits enforcement              │
│  - Emergency halt mechanism             │
└─────────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────────┐
│  Stellar Network                        │
│  - Token swaps & Path payments          │
│  - USDC settlement                      │
└─────────────────────────────────────────┘
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

### 🛡️ Custom Smart Contract (Soroban)
**Unique Features** (not found in boilerplate contracts):

1. **Multi-Agent Signature Verification**
   ```rust
   // Each agent must sign their actions
   trading_agent.require_auth();  // Generate signal
   risk_agent.require_auth();     // Approve risk
   payment_agent.require_auth();  // Execute trade
   ```

2. **Quantitative Risk Limits Enforcement**
   ```rust
   // On-chain risk checks
   if var_95 > max_var_95 { reject }
   if sharpe_ratio < min_sharpe { reject }
   if max_drawdown < -2000 { reject }
   ```

3. **AI Strategy Recording**
   ```rust
   // Record which AI strategy made the decision
   struct TradingSignal {
       strategy: String,  // "LSTM", "DQN", "MACD"
       confidence: u32,   // AI confidence score
   }
   ```

4. **AI-Triggered Circuit Breaker**
   ```rust
   // Risk Agent can halt system on anomaly detection
   emergency_halt()
   ```

### 🌐 Stellar Integration
- Horizon API for real-time data
- Historical trade data from Stellar DEX
- Path payment for optimal asset conversion
- USDC settlement for all trades

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
stellar-ai-treasury/
├── agents/                      # AI Agents
│   ├── agent_system_with_function_tools.py
│   ├── trading_strategies.py   # 10 strategies
│   ├── risk.py                 # Risk calculations
│   └── payment.py              # Stellar execution
│
├── contracts/                   # Smart Contracts ⭐
│   └── ai_treasury_vault/
│       ├── Cargo.toml
│       └── src/
│           └── lib.rs          # Main contract (400+ lines)
│
├── stellar/                     # Stellar Integration
│   ├── wallet.py
│   ├── horizon.py
│   ├── historical_data.py
│   └── market_data.py
│
├── app/                         # Frontend
│   ├── dashboard.py            # Streamlit UI
│   └── agent_conversation_ui.py
│
└── tests/                       # Tests
    ├── test_payment.py
    ├── test_risk.py
    └── test_trading_rules.py
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
- All trades go through Soroban smart contract
- Risk limits enforced on-chain
- Contract manages treasury vault

### ✅ Custom (not boilerplate) smart contract
**Unique Features**:
- Multi-agent signature logic
- Quantitative risk limit enforcement (VaR, Sharpe, Drawdown)
- AI strategy recording on-chain
- AI-triggered circuit breaker

### ✅ Fully-functioning
- ✅ Compiles: `stellar contract build`
- ✅ Tests pass: `cargo test`
- ✅ Deployable to testnet
- ✅ Callable from Python backend

---

## 📖 Documentation

- **[Project Summary](PROJECT_SUMMARY.md)** - Quick overview
- **[Smart Contract Integration](STELLAR_SMART_CONTRACT_INTEGRATION.md)** - Technical details
- **[Function Calling Guide](FUNCTION_CALLING_COMPLETE.md)** - AI agent architecture
- **[Agent Conversation Feature](TEST_AGENT_CONVERSATION.md)** - Real-time monitoring

---

## 🎥 Demo

### Watch AI Agents Work Together
1. Start dashboard: `python smart_start.py`
2. Configure assets (BTC, ETH, SOL)
3. Click "Run Trading Cycle"
4. Go to "🤖 AI Agents" tab
5. Watch real-time conversation:

```
Trading Agent: "Calling strategy: lstm_strategy(BTC)"
Strategy Tool: "Result: HOLD (confidence: 0.85)"
Trading Agent: "Decision: Selected BTC-LSTM for portfolio"
Risk Agent: "Evaluating risk... VaR: 3%, Sharpe: 1.5"
Risk Agent: "✅ APPROVED - Risk within limits"
Smart Contract: "Verifying signatures and risk limits..."
Payment Agent: "Executing trade, settling to USDC..."
```

---

## 🏆 Innovation Highlights

### Technical Excellence
- **First** AI Multi-Agent + Stellar smart contract integration
- **First** on-chain quantitative risk limit enforcement
- **First** GPT-4 Function Calling for trading strategies

### User Value
- **Transparency**: See AI decision-making process in real-time
- **Security**: Smart contract enforces risk limits
- **Automation**: Fully automated trading execution
- **Trust**: All decisions recorded on-chain

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

## 📄 License

This project is licensed under the MIT License.

---

## 🔗 Links

- **Stellar**: https://stellar.org
- **Soroban**: https://soroban.stellar.org
- **OpenAI**: https://openai.com

---

## 📧 Contact

For questions or support, please open an issue on GitHub.

---

**Built with ❤️ for the Stellar ecosystem**

*Combining the power of AI and blockchain for transparent, secure, and intelligent trading*
