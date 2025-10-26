#![no_std]

//! AI Treasury Vault Smart Contract V2.0 - Enhanced Edition
//! 
//! A custom Soroban smart contract with advanced features:
//! - Multi-agent controlled treasury vault
//! - On-chain trade history and audit trail
//! - AI strategy performance tracking
//! - Portfolio snapshots and ROI calculation
//! - Risk-based trading limits with dynamic controls
//! - Emergency halt mechanism

use soroban_sdk::{
    contract, contractimpl, contracttype, token, Address, Env, String, Vec, Map,
};

// ============================================================================
// Data Structures
// ============================================================================

#[derive(Clone)]
#[contracttype]
pub struct TradingSignal {
    pub signal_id: u64,
    pub asset: String,
    pub action: String,  // "BUY", "SELL", "HOLD"
    pub amount: i128,
    pub strategy: String,  // "LSTM", "DQN", "MACD", etc.
    pub confidence: u32,  // 0-100
    pub expected_return: i32,  // basis points
    pub timestamp: u64,
}

#[derive(Clone)]
#[contracttype]
pub struct TradeRecord {
    pub trade_id: u64,
    pub signal_id: u64,
    pub asset: String,
    pub action: String,
    pub amount: i128,
    pub price: i128,  // Price at execution (scaled by 1e7)
    pub strategy: String,
    pub executed_at: u64,
    pub profit_loss: i128,  // Realized P&L in stroops
}

#[derive(Clone)]
#[contracttype]
pub struct StrategyPerformance {
    pub strategy_name: String,
    pub total_trades: u32,
    pub winning_trades: u32,
    pub total_profit: i128,
    pub avg_return: i32,  // basis points
    pub sharpe_ratio: i32,
    pub last_updated: u64,
}

#[derive(Clone)]
#[contracttype]
pub struct PortfolioSnapshot {
    pub snapshot_id: u64,
    pub timestamp: u64,
    pub total_value: i128,  // Total portfolio value in stroops
    pub num_assets: u32,
    pub total_trades: u64,
    pub cumulative_return: i32,  // basis points since inception
}

#[derive(Clone)]
#[contracttype]
pub struct RiskMetrics {
    pub var_95: i32,  // basis points
    pub sharpe_ratio: i32,  // scaled by 100
    pub max_drawdown: i32,  // basis points
    pub portfolio_volatility: u32,
    pub stop_loss_level: i32,  // Dynamic stop-loss (basis points)
}

#[derive(Clone)]
#[contracttype]
pub struct VaultConfig {
    pub admin: Address,
    pub trading_agent: Address,
    pub risk_agent: Address,
    pub payment_agent: Address,
    pub max_single_trade: i128,
    pub max_var_95: i32,
    pub min_sharpe_ratio: i32,
    pub dynamic_stop_loss: bool,  // Enable dynamic stop-loss
    pub halted: bool,
    pub created_at: u64,
    pub version: u32,  // Contract version
}

#[derive(Clone)]
#[contracttype]
pub enum DataKey {
    Config,
    TradeCounter,
    SignalCounter,
    SnapshotCounter,
    Trade(u64),  // trade_id
    Signal(u64),  // signal_id
    Strategy(String),  // strategy_name
    Snapshot(u64),  // snapshot_id
    RiskMetrics,
    LatestSnapshot,
}

// ============================================================================
// Smart Contract V2.0
// ============================================================================

#[contract]
pub struct AITreasuryVaultV2;

#[contractimpl]
impl AITreasuryVaultV2 {
    
    /// Initialize the AI Treasury Vault V2
    pub fn initialize(
        env: Env,
        admin: Address,
        trading_agent: Address,
        risk_agent: Address,
        payment_agent: Address,
        max_single_trade: i128,
    ) {
        admin.require_auth();
        
        let config = VaultConfig {
            admin: admin.clone(),
            trading_agent,
            risk_agent,
            payment_agent,
            max_single_trade,
            max_var_95: 500,  // 5% max VaR
            min_sharpe_ratio: 100,  // 1.0 min Sharpe
            dynamic_stop_loss: true,
            halted: false,
            created_at: env.ledger().timestamp(),
            version: 2,  // V2.0
        };
        
        env.storage().instance().set(&DataKey::Config, &config);
        env.storage().instance().set(&DataKey::TradeCounter, &0u64);
        env.storage().instance().set(&DataKey::SignalCounter, &0u64);
        env.storage().instance().set(&DataKey::SnapshotCounter, &0u64);
    }
    
    /// Submit a trading signal from Trading Agent
    pub fn submit_trading_signal(
        env: Env,
        asset: String,
        action: String,
        amount: i128,
        strategy: String,
        confidence: u32,
        expected_return: i32,
    ) -> u64 {
        let config: VaultConfig = env.storage().instance().get(&DataKey::Config).unwrap();
        config.trading_agent.require_auth();
        
        if config.halted {
            panic!("System is halted");
        }
        
        if amount > config.max_single_trade {
            panic!("Trade amount exceeds limit");
        }
        
        // Increment signal counter
        let mut signal_counter: u64 = env.storage().instance()
            .get(&DataKey::SignalCounter).unwrap_or(0);
        signal_counter += 1;
        
        let signal = TradingSignal {
            signal_id: signal_counter,
            asset,
            action,
            amount,
            strategy,
            confidence,
            expected_return,
            timestamp: env.ledger().timestamp(),
        };
        
        env.storage().instance().set(&DataKey::SignalCounter, &signal_counter);
        env.storage().temporary().set(&DataKey::Signal(signal_counter), &signal);
        
        signal_counter
    }
    
    /// Risk Agent evaluates and approves/rejects the trading signal
    pub fn approve_trade(
        env: Env,
        signal_id: u64,
        risk_metrics: RiskMetrics,
    ) -> bool {
        let config: VaultConfig = env.storage().instance().get(&DataKey::Config).unwrap();
        config.risk_agent.require_auth();
        
        // Check risk limits
        if risk_metrics.var_95 > config.max_var_95 {
            return false;
        }
        
        if risk_metrics.sharpe_ratio < config.min_sharpe_ratio {
            return false;
        }
        
        if risk_metrics.max_drawdown < -2000 {  // -20%
            return false;
        }
        
        // NEW: Dynamic stop-loss check
        if config.dynamic_stop_loss && risk_metrics.stop_loss_level < -1500 {
            return false;  // Stop-loss triggered at -15%
        }
        
        env.storage().instance().set(&DataKey::RiskMetrics, &risk_metrics);
        
        true
    }
    
    /// Execute approved trade and record history
    pub fn execute_trade(
        env: Env,
        signal_id: u64,
        executed_price: i128,
        profit_loss: i128,
    ) -> u64 {
        let config: VaultConfig = env.storage().instance().get(&DataKey::Config).unwrap();
        config.payment_agent.require_auth();
        
        // Get the signal
        let signal: TradingSignal = env.storage().temporary()
            .get(&DataKey::Signal(signal_id))
            .unwrap();
        
        // Increment trade counter
        let mut trade_counter: u64 = env.storage().instance()
            .get(&DataKey::TradeCounter).unwrap_or(0);
        trade_counter += 1;
        
        // Create trade record
        let trade_record = TradeRecord {
            trade_id: trade_counter,
            signal_id,
            asset: signal.asset.clone(),
            action: signal.action.clone(),
            amount: signal.amount,
            price: executed_price,
            strategy: signal.strategy.clone(),
            executed_at: env.ledger().timestamp(),
            profit_loss,
        };
        
        // Store trade record permanently
        env.storage().instance().set(&DataKey::Trade(trade_counter), &trade_record);
        env.storage().instance().set(&DataKey::TradeCounter, &trade_counter);
        
        // Update strategy performance
        Self::update_strategy_performance(
            env.clone(),
            signal.strategy.clone(),
            profit_loss,
            signal.expected_return,
        );
        
        trade_counter
    }
    
    /// Update strategy performance metrics
    fn update_strategy_performance(
        env: Env,
        strategy_name: String,
        profit_loss: i128,
        expected_return: i32,
    ) {
        let key = DataKey::Strategy(strategy_name.clone());
        
        let mut perf: StrategyPerformance = env.storage().instance()
            .get(&key)
            .unwrap_or(StrategyPerformance {
                strategy_name: strategy_name.clone(),
                total_trades: 0,
                winning_trades: 0,
                total_profit: 0,
                avg_return: 0,
                sharpe_ratio: 0,
                last_updated: 0,
            });
        
        perf.total_trades += 1;
        if profit_loss > 0 {
            perf.winning_trades += 1;
        }
        perf.total_profit += profit_loss;
        
        // Update average return
        if perf.total_trades > 0 {
            perf.avg_return = (perf.total_profit as i32) / (perf.total_trades as i32);
        }
        
        perf.last_updated = env.ledger().timestamp();
        
        env.storage().instance().set(&key, &perf);
    }
    
    /// Create a portfolio snapshot
    pub fn create_snapshot(
        env: Env,
        total_value: i128,
        num_assets: u32,
        cumulative_return: i32,
    ) -> u64 {
        let config: VaultConfig = env.storage().instance().get(&DataKey::Config).unwrap();
        config.trading_agent.require_auth();
        
        let mut snapshot_counter: u64 = env.storage().instance()
            .get(&DataKey::SnapshotCounter).unwrap_or(0);
        snapshot_counter += 1;
        
        let trade_counter: u64 = env.storage().instance()
            .get(&DataKey::TradeCounter).unwrap_or(0);
        
        let snapshot = PortfolioSnapshot {
            snapshot_id: snapshot_counter,
            timestamp: env.ledger().timestamp(),
            total_value,
            num_assets,
            total_trades: trade_counter,
            cumulative_return,
        };
        
        env.storage().instance().set(&DataKey::Snapshot(snapshot_counter), &snapshot);
        env.storage().instance().set(&DataKey::SnapshotCounter, &snapshot_counter);
        env.storage().instance().set(&DataKey::LatestSnapshot, &snapshot);
        
        snapshot_counter
    }
    
    /// Get strategy performance
    pub fn get_strategy_performance(env: Env, strategy_name: String) -> StrategyPerformance {
        env.storage().instance()
            .get(&DataKey::Strategy(strategy_name.clone()))
            .unwrap_or(StrategyPerformance {
                strategy_name,
                total_trades: 0,
                winning_trades: 0,
                total_profit: 0,
                avg_return: 0,
                sharpe_ratio: 0,
                last_updated: 0,
            })
    }
    
    /// Get trade record by ID
    pub fn get_trade(env: Env, trade_id: u64) -> TradeRecord {
        env.storage().instance()
            .get(&DataKey::Trade(trade_id))
            .unwrap()
    }
    
    /// Get latest portfolio snapshot
    pub fn get_latest_snapshot(env: Env) -> PortfolioSnapshot {
        env.storage().instance()
            .get(&DataKey::LatestSnapshot)
            .unwrap_or(PortfolioSnapshot {
                snapshot_id: 0,
                timestamp: 0,
                total_value: 0,
                num_assets: 0,
                total_trades: 0,
                cumulative_return: 0,
            })
    }
    
    /// Get total number of trades
    pub fn get_total_trades(env: Env) -> u64 {
        env.storage().instance()
            .get(&DataKey::TradeCounter)
            .unwrap_or(0)
    }
    
    /// Emergency halt
    pub fn emergency_halt(env: Env) {
        let mut config: VaultConfig = env.storage().instance().get(&DataKey::Config).unwrap();
        config.admin.require_auth();
        
        config.halted = true;
        env.storage().instance().set(&DataKey::Config, &config);
    }
    
    /// Resume trading
    pub fn resume_trading(env: Env) {
        let mut config: VaultConfig = env.storage().instance().get(&DataKey::Config).unwrap();
        config.admin.require_auth();
        
        config.halted = false;
        env.storage().instance().set(&DataKey::Config, &config);
    }
    
    /// Get vault configuration
    pub fn get_config(env: Env) -> VaultConfig {
        env.storage().instance().get(&DataKey::Config).unwrap()
    }
    
    /// Get current risk metrics
    pub fn get_risk_metrics(env: Env) -> RiskMetrics {
        env.storage().instance().get(&DataKey::RiskMetrics).unwrap_or(RiskMetrics {
            var_95: 0,
            sharpe_ratio: 0,
            max_drawdown: 0,
            portfolio_volatility: 0,
            stop_loss_level: 0,
        })
    }
    
    /// Check if system is operational
    pub fn is_operational(env: Env) -> bool {
        let config: VaultConfig = env.storage().instance().get(&DataKey::Config).unwrap();
        !config.halted
    }
    
    /// Update risk limits
    pub fn update_risk_limits(
        env: Env,
        max_var_95: i32,
        min_sharpe_ratio: i32,
    ) {
        let mut config: VaultConfig = env.storage().instance().get(&DataKey::Config).unwrap();
        config.admin.require_auth();
        
        config.max_var_95 = max_var_95;
        config.min_sharpe_ratio = min_sharpe_ratio;
        
        env.storage().instance().set(&DataKey::Config, &config);
    }
    
    /// Enable/disable dynamic stop-loss
    pub fn set_dynamic_stop_loss(env: Env, enabled: bool) {
        let mut config: VaultConfig = env.storage().instance().get(&DataKey::Config).unwrap();
        config.admin.require_auth();
        
        config.dynamic_stop_loss = enabled;
        env.storage().instance().set(&DataKey::Config, &config);
    }
}

// ============================================================================
// Tests
// ============================================================================

#[cfg(test)]
mod test {
    use super::*;
    use soroban_sdk::{testutils::Address as _, Env};

    #[test]
    fn test_initialize_v2() {
        let env = Env::default();
        let contract_id = env.register_contract(None, AITreasuryVaultV2);
        let client = AITreasuryVaultV2Client::new(&env, &contract_id);
        
        let admin = Address::generate(&env);
        let trading_agent = Address::generate(&env);
        let risk_agent = Address::generate(&env);
        let payment_agent = Address::generate(&env);
        
        env.mock_all_auths();
        
        client.initialize(
            &admin,
            &trading_agent,
            &risk_agent,
            &payment_agent,
            &1000000,
        );
        
        let config = client.get_config();
        assert_eq!(config.version, 2);
        assert_eq!(config.dynamic_stop_loss, true);
    }
    
    #[test]
    fn test_trade_history() {
        let env = Env::default();
        let contract_id = env.register_contract(None, AITreasuryVaultV2);
        let client = AITreasuryVaultV2Client::new(&env, &contract_id);
        
        let admin = Address::generate(&env);
        let trading_agent = Address::generate(&env);
        let risk_agent = Address::generate(&env);
        let payment_agent = Address::generate(&env);
        
        env.mock_all_auths();
        
        client.initialize(&admin, &trading_agent, &risk_agent, &payment_agent, &1000000);
        
        // Submit signal
        let signal_id = client.submit_trading_signal(
            &String::from_str(&env, "BTC"),
            &String::from_str(&env, "BUY"),
            &100000,
            &String::from_str(&env, "LSTM"),
            &85,
            &250,
        );
        
        assert_eq!(signal_id, 1);
        
        // Execute trade
        let trade_id = client.execute_trade(&signal_id, &45000_0000000, &5000);
        assert_eq!(trade_id, 1);
        
        // Check total trades
        let total_trades = client.get_total_trades();
        assert_eq!(total_trades, 1);
        
        // Get trade record
        let trade = client.get_trade(&trade_id);
        assert_eq!(trade.strategy, String::from_str(&env, "LSTM"));
        assert_eq!(trade.profit_loss, 5000);
    }
    
    #[test]
    fn test_strategy_performance() {
        let env = Env::default();
        let contract_id = env.register_contract(None, AITreasuryVaultV2);
        let client = AITreasuryVaultV2Client::new(&env, &contract_id);
        
        let admin = Address::generate(&env);
        let trading_agent = Address::generate(&env);
        let risk_agent = Address::generate(&env);
        let payment_agent = Address::generate(&env);
        
        env.mock_all_auths();
        
        client.initialize(&admin, &trading_agent, &risk_agent, &payment_agent, &1000000);
        
        // Execute multiple trades
        let signal_id = client.submit_trading_signal(
            &String::from_str(&env, "BTC"),
            &String::from_str(&env, "BUY"),
            &100000,
            &String::from_str(&env, "LSTM"),
            &85,
            &250,
        );
        
        client.execute_trade(&signal_id, &45000_0000000, &5000);
        
        // Check strategy performance
        let perf = client.get_strategy_performance(&String::from_str(&env, "LSTM"));
        assert_eq!(perf.total_trades, 1);
        assert_eq!(perf.winning_trades, 1);
        assert_eq!(perf.total_profit, 5000);
    }
    
    #[test]
    fn test_portfolio_snapshot() {
        let env = Env::default();
        let contract_id = env.register_contract(None, AITreasuryVaultV2);
        let client = AITreasuryVaultV2Client::new(&env, &contract_id);
        
        let admin = Address::generate(&env);
        let trading_agent = Address::generate(&env);
        let risk_agent = Address::generate(&env);
        let payment_agent = Address::generate(&env);
        
        env.mock_all_auths();
        
        client.initialize(&admin, &trading_agent, &risk_agent, &payment_agent, &1000000);
        
        // Create snapshot
        let snapshot_id = client.create_snapshot(&1000000_0000000, &5, &1500);
        assert_eq!(snapshot_id, 1);
        
        // Get latest snapshot
        let snapshot = client.get_latest_snapshot();
        assert_eq!(snapshot.num_assets, 5);
        assert_eq!(snapshot.cumulative_return, 1500);
    }
    
    #[test]
    fn test_dynamic_stop_loss() {
        let env = Env::default();
        let contract_id = env.register_contract(None, AITreasuryVaultV2);
        let client = AITreasuryVaultV2Client::new(&env, &contract_id);
        
        let admin = Address::generate(&env);
        let trading_agent = Address::generate(&env);
        let risk_agent = Address::generate(&env);
        let payment_agent = Address::generate(&env);
        
        env.mock_all_auths();
        
        client.initialize(&admin, &trading_agent, &risk_agent, &payment_agent, &1000000);
        
        // Test with stop-loss triggered
        let risk_metrics = RiskMetrics {
            var_95: 300,
            sharpe_ratio: 150,
            max_drawdown: -1000,
            portfolio_volatility: 20,
            stop_loss_level: -1600,  // Below -15% threshold
        };
        
        let approved = client.approve_trade(&1, &risk_metrics);
        assert_eq!(approved, false);  // Should reject due to stop-loss
    }
}
