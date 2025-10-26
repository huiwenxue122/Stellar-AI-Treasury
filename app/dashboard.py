#!/usr/bin/env python3
"""
Enhanced Dashboard for Stellar AI Treasury System
A beautiful and functional web interface
"""

import sys
import os

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import streamlit as st
import asyncio
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import time
from datetime import datetime, timedelta
from app.orchestrator import ORCHESTRATOR
from app.agent_conversation_ui import render_agent_conversation, render_compact_agent_status
from app.localization import get_translation, get_tier_description, get_risk_explanation

# Page configuration
st.set_page_config(
    page_title="Stellar AI Treasury",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': "Stellar AI Treasury - Multi-Agent Trading System"
    }
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    
    .status-success {
        color: #28a745;
        font-weight: bold;
    }
    
    .status-warning {
        color: #ffc107;
        font-weight: bold;
    }
    
    .status-danger {
        color: #dc3545;
        font-weight: bold;
    }
    
    .signal-card {
        border-left: 4px solid #667eea;
        padding: 1rem;
        margin: 0.5rem 0;
        background-color: #f8f9fa;
        border-radius: 5px;
    }
    
    .trading-log {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        max-height: 400px;
        overflow-y: auto;
    }
</style>
""", unsafe_allow_html=True)

class TreasuryDashboard:
    def __init__(self):
        self.orchestrator = ORCHESTRATOR
        self.initialize_session_state()
    
    def initialize_session_state(self):
        """Initialize session state variables"""
        if 'initialized' not in st.session_state:
            st.session_state.initialized = False
        if 'trading_log' not in st.session_state:
            st.session_state.trading_log = []
        if 'portfolio_history' not in st.session_state:
            st.session_state.portfolio_history = []
        if 'auto_trading' not in st.session_state:
            st.session_state.auto_trading = False
        if 'selected_assets' not in st.session_state:
            st.session_state.selected_assets = ['BTC', 'ETH', 'SOL', 'ARB', 'LINK', 'AAVE', 'LDO', 'FET']
        if 'hedge_currency' not in st.session_state:
            st.session_state.hedge_currency = 'USDC'
        if 'xlm_balance' not in st.session_state:
            # 💰 Initialize with default - will be updated when user configures capital
            FIXED_XLM_PRICE = 0.31
            DEFAULT_USD = 1_000_000  # Default, will be replaced by user's capital choice
            st.session_state.xlm_balance = DEFAULT_USD / FIXED_XLM_PRICE  # Updated on config confirm
        if 'config_completed' not in st.session_state:
            st.session_state.config_completed = False
        
        # 🌍 Tier system and localization
        if 'user_tier' not in st.session_state:
            st.session_state.user_tier = 'beginner'
        if 'language' not in st.session_state:
            st.session_state.language = 'en'
        if 'latest_risk_metrics' not in st.session_state:
            st.session_state.latest_risk_metrics = None
    
    def add_to_log(self, message, level="info"):
        """Add message to trading log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        st.session_state.trading_log.append({
            "timestamp": timestamp,
            "message": message,
            "level": level
        })
        # Keep only last 50 entries
        if len(st.session_state.trading_log) > 50:
            st.session_state.trading_log = st.session_state.trading_log[-50:]
    
    def render_header(self):
        """Render the main header"""
        st.markdown('<h1 class="main-header">🏦 Stellar AI Treasury Dashboard</h1>', unsafe_allow_html=True)
        
        # Status indicator
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.session_state.initialized:
                st.success("🟢 System Online")
            else:
                st.error("🔴 System Offline")
    
    def render_asset_config(self):
        """Render asset configuration interface"""
        st.title("⚙️ Asset Configuration")
        
        st.markdown("""
        ### 👋 Welcome to Stellar AI Treasury
        
        Please configure your portfolio before starting:
        """)
        
        # 🌍 Tier Selection Section
        st.markdown("---")
        st.subheader("🎓 " + get_translation('select_tier', st.session_state.language))
        
        tier_col1, tier_col2 = st.columns([2, 1])
        
        with tier_col1:
            tier_options = {
                'beginner': get_translation('tier_beginner', st.session_state.language),
                'intermediate': get_translation('tier_intermediate', st.session_state.language),
                'advanced': get_translation('tier_advanced', st.session_state.language)
            }
            
            selected_tier = st.radio(
                "Your Experience Level:",
                options=list(tier_options.keys()),
                format_func=lambda x: tier_options[x],
                index=['beginner', 'intermediate', 'advanced'].index(st.session_state.user_tier)
            )
            
            st.session_state.user_tier = selected_tier
            
            # Show tier description
            st.markdown(get_tier_description(selected_tier, st.session_state.language))
        
        with tier_col2:
            # Language selection
            st.selectbox(
                "🌍 Language:",
                options=['en', 'es', 'sw', 'ar', 'zh'],
                format_func=lambda x: {
                    'en': '🇬🇧 English',
                    'es': '🇪🇸 Español',
                    'sw': '🇹🇿 Kiswahili',
                    'ar': '🇸🇦 العربية',
                    'zh': '🇨🇳 中文'
                }[x],
                key='language'
            )
            
            # Show risk budget info
            tier_config = self.orchestrator.tier_manager.get_tier_config(selected_tier)
            st.info(f"""
            **Risk Budget:**
            - Max Portfolio Risk: {tier_config.max_portfolio_var * 100}%
            - Max Single Asset: {tier_config.max_single_asset_percent}%
            """)
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("💰 Initial Asset")
            
            # Display XLM balance
            st.info("""
            Your wallet initial asset is **XLM (Stellar Native Coin)**
            
            System will use XLM for multi-asset trading
            """)
            
            # Display the configured capital (updated in real-time as user selects)
            if st.session_state.xlm_balance > 0:
                capital_usd = st.session_state.xlm_balance * 0.31
                st.metric(
                    "Configured Capital", 
                    f"{st.session_state.xlm_balance:.2f} XLM",
                    delta=f"≈ ${capital_usd:,.2f} USD"
                )
                st.caption("💡 This will update as you select your capital below")
            
            # Optional: Display actual testnet XLM balance
            with st.expander("🔍 Query Real Testnet Balance (Optional)"):
                if st.button("Query Testnet Balance"):
                    with st.spinner("Querying Stellar testnet..."):
                        try:
                            from stellar.wallet import Wallet
                            from dotenv import load_dotenv
                            load_dotenv()
                            wallet_public = os.environ.get("STELLAR_PUBLIC")
                            
                            if not wallet_public:
                                st.error("❌ STELLAR_PUBLIC not found in environment")
                            else:
                                real_xlm_balance = asyncio.run(
                                    self.orchestrator.asset_manager.get_asset_balance(wallet_public, 'xlm')
                                )
                                st.success(f"✅ Real Testnet Balance: {real_xlm_balance:.2f} XLM")
                                st.caption("Note: This is your actual testnet balance. We use simulated balance for trading.")
                        except Exception as e:
                            st.warning(f"Query failed: {e}")
        
        with col2:
            st.subheader("🎯 Hedge Currency")
            
            st.info("""
            Choose stablecoin for risk hedging and final settlement
            
            Like Robinhood, all profits will be denominated in stablecoin
            """)
            
            hedge_options = ['USDC', 'USDT']
            hedge_currency = st.selectbox(
                "Hedge Currency",
                hedge_options,
                index=hedge_options.index(st.session_state.hedge_currency)
            )
            st.session_state.hedge_currency = hedge_currency
            
            st.success(f"✅ Selected: {hedge_currency}")
            st.caption("All trades will be settled in this currency")
        
        st.markdown("---")
        
        # 💰 NEW: Initial Capital Configuration
        st.subheader("💰 Initial Capital Configuration")
        
        # 🦊 NEW: Wallet Connection Options
        st.markdown("### 💼 Choose Your Method")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # 多语言文本
            wallet_texts = {
                'en': {
                    'title': '🦊 **Connect Wallet** (Recommended)',
                    'caption': 'Use your real Stellar wallet balance',
                    'balance': '✅ Wallet Balance:',
                    'use_balance': '💰 Use Wallet Balance',
                    'using_balance': '✅ Using wallet balance:'
                },
                'zh': {
                    'title': '🦊 **连接钱包** (推荐)',
                    'caption': '使用你的真实 Stellar 钱包余额',
                    'balance': '✅ 钱包余额:',
                    'use_balance': '💰 使用钱包余额',
                    'using_balance': '✅ 使用钱包余额:'
                }
            }
            
            current_language = st.session_state.get('language', 'en')
            wallet_text = wallet_texts.get(current_language, wallet_texts['en'])
            
            st.info(wallet_text['title'])
            st.caption(wallet_text['caption'])
            
            # Import wallet connector
            from app.wallet_connector import render_wallet_connector, is_wallet_connected, get_wallet_balance
            
            # Render wallet connector
            wallet_connector = render_wallet_connector()
            
            # Check if wallet is connected
            wallet_connected = is_wallet_connected()
            if wallet_connected:
                wallet_balance = get_wallet_balance()
                st.success(f"{wallet_text['balance']} {wallet_balance:,.2f} XLM")
                
                # Option to use wallet balance
                if st.button(wallet_text['use_balance'], type="primary"):
                    # Convert XLM to USD (using fixed rate $0.31)
                    usd_equivalent = wallet_balance * 0.31
                    st.session_state.initial_capital_usd = usd_equivalent
                    st.session_state.xlm_balance = wallet_balance
                    st.session_state.use_wallet_balance = True
                    st.success(f"{wallet_text['using_balance']} {wallet_balance:,.2f} XLM (≈${usd_equivalent:,.2f})")
                    st.rerun()
        
        with col2:
            # 多语言文本
            manual_texts = {
                'en': {
                    'title': '💰 **Manual Input** (For Testing)',
                    'caption': 'Set custom amount for simulation'
                },
                'zh': {
                    'title': '💰 **手动输入** (测试用)',
                    'caption': '设置自定义金额进行模拟'
                }
            }
            
            manual_text = manual_texts.get(current_language, manual_texts['en'])
            
            st.info(manual_text['title'])
            st.caption(manual_text['caption'])
            
            # Tier-based recommendations
            tier = st.session_state.user_tier
            tier_recommendations = {
                'beginner': {
                    'min': 100.0,
                    'recommended': 1000.0,
                    'max': 10000.0,
                    'message': "🎓 For beginners: Start small to learn. We recommend $500-$5,000 to safely explore strategies."
                },
                'intermediate': {
                    'min': 1000.0,
                    'recommended': 25000.0,
                    'max': 100000.0,
                    'message': "📊 For intermediate users: Moderate capital allows better diversification. Recommended: $10K-$50K."
                },
                'advanced': {
                    'min': 10000.0,
                    'recommended': 250000.0,
                    'max': 1000000.0,  # 🎯 最大1M美元
                    'message': "🚀 For advanced users: Large capital enables full strategy deployment. Recommended: $100K+."
                }
            }
            
            rec = tier_recommendations[tier]
            
            # Display tier-specific guidance
            st.info(rec['message'])
            
            # Quick preset buttons
            st.markdown("**Quick Presets:**")
            preset_col1, preset_col2, preset_col3, preset_col4 = st.columns(4)
            
            # Define presets (use float for consistency with number_input)
            presets = [
                ("$1K", 1000.0),
                ("$10K", 10000.0),
                ("$100K", 100000.0),
                ("$1M", 1000000.0)
            ]
        
            # Display preset buttons
            for col, (label, amount) in zip([preset_col1, preset_col2, preset_col3, preset_col4], presets):
                with col:
                    # Check if amount is within tier limits
                    is_disabled = amount < rec['min'] or amount > rec['max']
                    button_label = f"{label} {'🔒' if is_disabled else ''}"
                    
                    if st.button(button_label, key=f"preset_{amount}", disabled=is_disabled):
                        # Only set temp_capital, number_input will use it via session state
                        st.session_state.temp_capital = amount
                        # Delete capital_input to force re-initialization with new value
                        if 'capital_input' in st.session_state:
                            del st.session_state.capital_input
                        st.rerun()
            
            # Show help for locked presets
            locked_presets = [label for label, amount in presets if amount < rec['min'] or amount > rec['max']]
            if locked_presets:
                st.caption(f"🔒 Locked presets are outside your tier's limits. Upgrade tier to unlock.")
            
            # Custom input with validation
            # Use session_state value if exists, otherwise use recommended
            if 'capital_input' not in st.session_state:
                # Initialize from temp_capital or recommended value
                default_capital = st.session_state.get('temp_capital', rec['recommended'])
                default_capital = float(default_capital)
                
                # Ensure default is within tier limits
                if default_capital < rec['min']:
                    default_capital = rec['min']
                elif default_capital > rec['max']:
                    default_capital = rec['max']
                
                st.session_state.capital_input = default_capital
            
            capital_usd = st.number_input(
                f"Enter your capital (${rec['min']:,.0f} - ${rec['max']:,.0f} USD):",
                min_value=rec['min'],
                max_value=rec['max'],
                step=1000.0,
                key='capital_input',
                help=f"This amount will be converted to XLM for simulated trading on Stellar testnet."
            )
            
            # Save to session state
            st.session_state.initial_capital_usd = capital_usd
            
            # Real-time conversion (using FIXED price $0.31)
            FIXED_XLM_PRICE = 0.31
            xlm_amount = capital_usd / FIXED_XLM_PRICE
            
            # 💰 IMPORTANT: Also update xlm_balance immediately for display purposes
            # This ensures the "Initial Asset" and "Configuration Summary" sections show the correct amount
            st.session_state.xlm_balance = xlm_amount
            
            st.markdown("---")
            st.markdown("### 💱 Conversion Preview")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("💵 USD Capital", f"${capital_usd:,.0f}")
            with col2:
                st.metric("💎 XLM Equivalent", f"{xlm_amount:,.0f} XLM")
            with col3:
                st.metric("📊 XLM Price (Fixed)", f"${FIXED_XLM_PRICE}")
            
            st.caption("🔒 This is **simulated capital** for testing strategies. No real funds required on Stellar testnet.")
            
            # Warning for mismatched tier/capital
            if tier == 'beginner' and capital_usd > 10000:
                st.warning("⚠️  You selected Beginner tier but large capital. Consider Intermediate tier for better risk management.")
            elif tier == 'advanced' and capital_usd < 10000:
                st.info("💡 Advanced tier with small capital? Most advanced strategies work better with larger amounts.")
        
        st.markdown("---")
        
        st.subheader("📊 Trading Assets Selection")
        
        st.markdown("""
        Select assets you want to trade. **Assets are grouped by risk level** based on your experience tier.
        - ✅ = Safe for beginners  |  ⚖️ = Moderate risk  |  🚀 = High risk
        """)
        
        # 🎯 Get assets grouped by risk level for current tier
        assets_by_risk = self.orchestrator.tier_manager.get_assets_by_risk_level(st.session_state.user_tier)
        
        selected_assets = []
        
        # 🛡️ SAFE ASSETS (Always shown if tier allows)
        if assets_by_risk['safe']:
            st.markdown("### 🛡️ Safe Assets (Recommended)")
            st.caption("Low risk, stable value. Good for capital preservation.")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("**💵 Stablecoins**")
                for asset in ['USDC', 'USDT']:
                    if asset in assets_by_risk['safe'] and asset != st.session_state.hedge_currency:
                        default = asset in st.session_state.selected_assets
                        if st.checkbox(f"{asset} ✅", value=default, key=f"asset_{asset}"):
                            selected_assets.append(asset)
                            # Show safety explanation
                            if st.session_state.user_tier == 'beginner':
                                safety_msg = self.orchestrator.tier_manager.get_safety_explanation(
                                    asset, st.session_state.user_tier, st.session_state.language
                                )
                                if safety_msg:
                                    st.caption(safety_msg[:100] + "...")
            
            with col2:
                st.markdown("**🏆 Gold-Backed**")
                for asset in ['PAXG', 'XAUT', 'GOLD']:
                    if asset in assets_by_risk['safe']:
                        default = asset in st.session_state.selected_assets
                        if st.checkbox(f"{asset} ✅", value=default, key=f"asset_{asset}"):
                            selected_assets.append(asset)
                            # Show safety explanation
                            if st.session_state.user_tier == 'beginner':
                                safety_msg = self.orchestrator.tier_manager.get_safety_explanation(
                                    asset, st.session_state.user_tier, st.session_state.language
                                )
                                if safety_msg:
                                    st.caption(safety_msg[:100] + "...")
            
            with col3:
                st.markdown("**📜 Tokenized Funds & Real Estate**")
                for asset in ['BENJI', 'REIT']:
                    if asset in assets_by_risk['safe']:
                        default = asset in st.session_state.selected_assets
                        if st.checkbox(f"{asset} ✅", value=default, key=f"asset_{asset}"):
                            selected_assets.append(asset)
                            # Show safety explanation
                            if st.session_state.user_tier == 'beginner':
                                safety_msg = self.orchestrator.tier_manager.get_safety_explanation(
                                    asset, st.session_state.user_tier, st.session_state.language
                                )
                                if safety_msg:
                                    st.caption(safety_msg[:100] + "...")
            
            st.markdown("---")
        
        # ⚖️ MODERATE RISK ASSETS (Intermediate+)
        if assets_by_risk['moderate']:
            st.markdown("### ⚖️ Moderate Risk Assets")
            st.caption("Higher potential returns, but with volatility. Requires some experience.")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**🪙 Major Cryptocurrencies**")
                for asset in ['BTC', 'ETH']:
                    if asset in assets_by_risk['moderate']:
                        default = asset in st.session_state.selected_assets
                        if st.checkbox(f"{asset} ⚖️", value=default, key=f"asset_{asset}"):
                            selected_assets.append(asset)
                            # Show warning
                            if st.session_state.user_tier in ['beginner', 'intermediate']:
                                safety_msg = self.orchestrator.tier_manager.get_safety_explanation(
                                    asset, 'beginner', st.session_state.language
                                )
                                if safety_msg:
                                    st.caption(safety_msg[:100] + "...")
            
            with col2:
                st.markdown("**🔗 DeFi & Layer 1/2**")
                for asset in ['SOL', 'ARB', 'LINK', 'AAVE']:
                    if asset in assets_by_risk['moderate']:
                        default = asset in st.session_state.selected_assets
                        if st.checkbox(f"{asset} ⚖️", value=default, key=f"asset_{asset}"):
                            selected_assets.append(asset)
            
            st.markdown("---")
        
        elif st.session_state.user_tier == 'beginner':
            # Show locked message for beginners
            st.markdown("### ⚖️ Moderate Risk Assets 🔒")
            st.info("🔒 **Upgrade to Intermediate** to access BTC, ETH, SOL, LINK, AAVE and more.")
            st.markdown("---")
        
        # 🚀 HIGH RISK ASSETS (Advanced only)
        if assets_by_risk['high_risk']:
            st.markdown("### 🚀 High Risk Assets")
            st.caption("Small-cap crypto with high volatility. For experienced traders only.")
            
            st.markdown("**💫 Small Cap & Emerging**")
            for asset in ['LDO', 'FET', 'XLM']:
                if asset in assets_by_risk['high_risk']:
                    default = asset in st.session_state.selected_assets
                    # XLM special handling (it's the native currency)
                    label = f"{asset} 🚀" if asset != 'XLM' else f"{asset} ⭐ (Native)"
                    if st.checkbox(label, value=default, key=f"asset_{asset}"):
                        selected_assets.append(asset)
            
            st.markdown("---")
        
        elif st.session_state.user_tier in ['beginner', 'intermediate']:
            # Show locked message
            st.markdown("### 🚀 High Risk Assets 🔒")
            st.info("🔒 **Upgrade to Advanced** to access small-cap cryptocurrencies like LDO, FET.")
            st.markdown("---")
        
        # Add hedge currency to selection list
        if st.session_state.hedge_currency not in selected_assets:
            selected_assets.append(st.session_state.hedge_currency)
        
        st.markdown("---")
        
        # Display selection summary
        st.subheader("📋 Configuration Summary")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Initial Asset:**")
            st.write(f"• XLM (Stellar Native Coin)")
            if st.session_state.xlm_balance > 0:
                st.write(f"  Balance: {st.session_state.xlm_balance:.2f} XLM")
        
        with col2:
            st.markdown("**Hedge Currency:**")
            st.write(f"• {st.session_state.hedge_currency}")
            st.caption("For risk hedging and final settlement")
        
        st.markdown("**Trading Assets:**")
        if selected_assets:
            assets_display = ", ".join(selected_assets)
            st.write(f"• {assets_display}")
            st.caption(f"Total {len(selected_assets)} assets")
        else:
            st.warning("⚠️ Please select at least one trading asset")
        
        st.markdown("---")
        
        # Confirm button
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            if st.button("✅ Confirm Configuration and Start", type="primary", disabled=len(selected_assets) == 0):
                st.session_state.selected_assets = selected_assets
                st.session_state.config_completed = True
                
                # Set user tier in orchestrator
                self.orchestrator.set_user_tier(st.session_state.user_tier)
                
                # 💰 Set initial capital (NEW)
                capital_usd = st.session_state.get('initial_capital_usd', 1000000.0)
                xlm_amount = self.orchestrator.set_initial_capital(capital_usd)
                
                # 💰 UPDATE: Also update xlm_balance in session_state for display
                st.session_state.xlm_balance = xlm_amount
                
                self.add_to_log(
                    f"Configuration completed: Tier={st.session_state.user_tier}, Capital=${capital_usd:,.0f} ({xlm_amount:,.0f} XLM), Assets={len(selected_assets)}, Hedge={st.session_state.hedge_currency}, Language={st.session_state.language}", 
                    "success"
                )
                st.success(f"✅ Configuration completed! Initial capital: ${capital_usd:,.0f} (≈ {xlm_amount:,.0f} XLM)")
                st.rerun()
        
        # Show instructions
        with st.expander("ℹ️ How to Use"):
            st.markdown("""
            ### Usage Flow
            
            1. **Query XLM Balance** (Optional)
               - Click "Query XLM Balance" to check wallet balance
            
            2. **Select Hedge Currency**
               - Recommended: USDC (best liquidity)
               - Alternative: USDT
            
            3. **Select Trading Assets**
               - Check assets you want to trade
               - Recommend selecting 5-10 assets for diversification
            
            4. **Confirm Configuration**
               - Check configuration summary
               - Click "Confirm Configuration and Start"
            
            5. **System Running**
               - Multi-Agent analyzes market
               - Builds portfolio
               - Executes trades
               - Settles to hedge currency
            
            ### Recommended Configurations
            
            **Conservative**:
            - Assets: BTC, ETH, USDC, BENJI
            - Hedge: USDC
            
            **Balanced**:
            - Assets: BTC, ETH, SOL, LINK, AAVE
            - Hedge: USDC
            
            **Aggressive**:
            - Assets: BTC, ETH, SOL, ARB, LINK, AAVE, LDO, FET
            - Hedge: USDC
            """)
    
    def render_sidebar(self):
        """Render the sidebar controls"""
        st.sidebar.title("🎛️ Control Panel")
        
        # Display current configuration
        if st.session_state.config_completed:
            st.sidebar.success("✅ Configuration Completed")
            
            with st.sidebar.expander("📋 Current Configuration"):
                st.write(f"**Hedge Currency**: {st.session_state.hedge_currency}")
                st.write(f"**Trading Assets**: {len(st.session_state.selected_assets)}")
                st.write(", ".join(st.session_state.selected_assets))
                
                if st.button("🔄 Reconfigure"):
                    st.session_state.config_completed = False
                    st.session_state.initialized = False
                    st.rerun()
        
        st.sidebar.markdown("---")
        
        # NEW: Agent Status
        with st.sidebar.expander("🤖 AI Agent Status", expanded=True):
            render_compact_agent_status()
        
        st.sidebar.markdown("---")
        
        # System controls
        st.sidebar.subheader("System Controls")
        
        # Reset Simulated Balances button
        if st.sidebar.button("🔄 Reset Simulated Balances"):
            try:
                self.orchestrator.asset_manager.reset_simulated_balances()
                self.add_to_log("Simulated balances reset to initial state", "success")
                st.success("✅ Balances reset! Refresh to see changes.")
                st.rerun()
            except Exception as e:
                st.error(f"Failed to reset: {e}")
        
        if not st.session_state.config_completed:
            st.sidebar.info("⚠️ Please complete asset configuration first")
            return
        
        if not st.session_state.initialized:
            if st.sidebar.button("🚀 Initialize System", type="primary"):
                with st.spinner("Initializing system with your configuration..."):
                    try:
                        # pass user-configured assets
                        success = asyncio.run(self.orchestrator.initialize(
                            selected_assets=st.session_state.selected_assets,
                            hedge_currency=st.session_state.hedge_currency
                        ))
                        if success:
                            st.session_state.initialized = True
                            self.add_to_log(
                                f"System initialized: {len(st.session_state.selected_assets)} assets, hedge: {st.session_state.hedge_currency}", 
                                "success"
                            )
                            st.success("✅ System initialized with your asset configuration!")
                        else:
                            self.add_to_log("System initialization failed", "error")
                            st.error("❌ Initialization failed")
                    except Exception as e:
                        self.add_to_log(f"Initialization error: {e}", "error")
                        st.error(f"❌ Error: {e}")
                st.rerun()
        else:
            if st.sidebar.button("🔄 Refresh Data"):
                st.rerun()
            
            if st.sidebar.button("🚀 Run Trading Cycle"):
                with st.spinner("Running trading cycle..."):
                    try:
                        self.add_to_log("Starting trading cycle...", "info")
                        st.info("🔄 Starting trading cycle with Multi-Agent system...")
                        
                        # Show configuration
                        st.write(f"**Selected Assets**: {', '.join(st.session_state.selected_assets)}")
                        st.write(f"**Hedge Currency**: {st.session_state.hedge_currency}")
                        
                        results = asyncio.run(self.orchestrator.run_trading_cycle())
                        
                        self.add_to_log(f"Trading cycle completed: {results['status']}", "info")
                        
                        # Save risk metrics to session state
                        if 'risk_metrics' in results:
                            st.session_state.latest_risk_metrics = results['risk_metrics']
                            self.add_to_log("Risk metrics updated", "info")
                        
                        if results.get('status') == 'SUCCESS':
                            portfolio_change = results.get('portfolio_change', 0)
                            
                            # Show execution summary
                            if 'trading_results' in results:
                                trading_res = results['trading_results']
                                
                                if 'execution_result' in trading_res:
                                    exec_res = trading_res['execution_result']
                                    trades_executed = exec_res.get('trades_executed', 0)
                                    total_xlm_spent = exec_res.get('total_xlm_spent', 0)
                                    
                                    st.success(f"✅ Trading cycle completed!")
                                    st.info(f"📊 Trades: {trades_executed} | XLM spent: {total_xlm_spent:.2f} XLM (≈${total_xlm_spent * 0.31:.2f})")
                                    
                                    # Show executed trades
                                    if exec_res.get('executed_trades'):
                                        with st.expander("💰 Executed Trades"):
                                            for trade in exec_res['executed_trades']:
                                                st.write(f"**{trade['action']} {trade['asset']}**: ${trade['usd_amount']:.2f} ({trade['xlm_spent']:.2f} XLM)")
                                                st.caption(f"Status: {trade['status']}")
                                    
                                    # Show note if simulated
                                    if exec_res.get('note'):
                                        st.warning(exec_res['note'])
                                        
                                elif 'final_usdc_profit' in trading_res:
                                    profit = trading_res['final_usdc_profit']
                                    self.add_to_log(f"Generated profit: ${profit:.2f} USDC", "success")
                                    st.success(f"✅ Trading cycle completed! Profit: ${profit:.2f} USDC | Portfolio change: ${portfolio_change:.2f}")
                                else:
                                    st.success(f"✅ Trading cycle completed! Portfolio change: ${portfolio_change:.2f}")
                            else:
                                st.success(f"✅ Trading cycle completed! Portfolio change: ${portfolio_change:.2f}")
                        elif results.get('status') == 'HALTED':
                            st.warning(f"⚠️ Trading halted: {results.get('reason', 'Unknown')}")
                        else:
                            st.info(f"ℹ️ Trading cycle status: {results.get('status', 'Unknown')}")
                            
                        # Show detailed results
                        with st.expander("📊 Detailed Results"):
                            st.json(results)
                            
                    except Exception as e:
                        import traceback
                        error_details = traceback.format_exc()
                        self.add_to_log(f"Trading cycle error: {e}", "error")
                        st.error(f"❌ Error: {e}")
                        with st.expander("🔍 Error Details"):
                            st.code(error_details)
                st.rerun()
        
        # Auto trading toggle
        st.sidebar.subheader("Auto Trading")
        auto_trading = st.sidebar.checkbox("Enable Auto Trading", value=st.session_state.auto_trading)
        if auto_trading != st.session_state.auto_trading:
            st.session_state.auto_trading = auto_trading
            if auto_trading:
                self.add_to_log("Auto trading enabled", "info")
            else:
                self.add_to_log("Auto trading disabled", "info")
        
        # Manual trading controls
        if st.session_state.initialized:
            st.sidebar.subheader("Manual Trading")
            
            with st.sidebar.form("manual_trade"):
                st.write("**Manual Trade**")
                action = st.selectbox("Action", ["convert_to_usdc", "convert_from_usdc"])
                asset = st.selectbox("Asset", ["XLM", "USDC", "EURC"])
                amount = st.number_input("Amount", min_value=0.01, value=10.0, step=0.01)
                
                if st.form_submit_button("Execute Trade"):
                    with st.spinner("Executing trade..."):
                        try:
                            result = asyncio.run(self.orchestrator.execute_manual_trade(action, asset, amount))
                            if result['success']:
                                self.add_to_log(f"Manual trade successful: {action} {amount} {asset}", "success")
                                st.success("Trade executed successfully!")
                            else:
                                self.add_to_log(f"Manual trade failed: {result.get('error', 'Unknown error')}", "error")
                                st.error(f"Trade failed: {result.get('error', 'Unknown error')}")
                        except Exception as e:
                            self.add_to_log(f"Manual trade error: {e}", "error")
                            st.error(f"Error: {e}")
                    st.rerun()
    
    def render_portfolio_overview(self):
        """Render portfolio overview section"""
        col_header, col_button = st.columns([3, 1])
        with col_header:
            st.header("📊 Portfolio Overview")
        with col_button:
            if st.button("🔄 Refresh Portfolio", key="refresh_portfolio"):
                st.rerun()
        
        if not st.session_state.initialized:
            st.warning("Please initialize the system first.")
            return
        
        try:
            status = asyncio.run(self.orchestrator.get_portfolio_status())
            
            # Main metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "Total Value",
                    f"${status['portfolio_value_usd']:.2f}",
                    delta=None
                )
            
            with col2:
                st.metric(
                    "USDC Allocation",
                    f"{status['usdc_allocation']:.1f}%",
                    delta=None
                )
            
            with col3:
                risk_level = status['risk_summary']['current_risk']['risk_level']
                risk_color = {"LOW": "🟢", "MEDIUM": "🟡", "HIGH": "🔴"}.get(risk_level, "⚪")
                st.metric(
                    "Risk Level",
                    f"{risk_color} {risk_level}",
                    delta=None
                )
            
            with col4:
                total_profit = status['risk_summary']['total_profit_usdc']
                st.metric(
                    "Total Profit",
                    f"${total_profit:.2f}",
                    delta=None
                )
            
            # Asset breakdown
            st.subheader("Asset Breakdown")
            
            # Debug: Show simulated balances if in simulation mode
            if self.orchestrator.asset_manager.simulation_mode:
                sim_balances = self.orchestrator.asset_manager.simulated_balances
                if sim_balances:
                    with st.expander("🔧 Debug: Simulated Balances"):
                        st.json(sim_balances)
                else:
                    st.info("ℹ️ Simulation mode active, but no simulated balances yet. Run a trading cycle to populate.")
            
            assets_data = []
            for asset_name, asset_info in status['assets'].items():
                assets_data.append({
                    'Asset': asset_name.upper(),
                    'Balance': asset_info['balance'],
                    'Value (USD)': asset_info['value_usd'],
                    'Volatility': asset_info['volatility'],
                    'Price (USD)': asset_info['price_usd']
                })
            
            df_assets = pd.DataFrame(assets_data)
            st.dataframe(df_assets, use_container_width=True)
            
            # Portfolio pie chart
            if status['portfolio_value_usd'] > 0:
                fig = px.pie(
                    df_assets, 
                    values='Value (USD)', 
                    names='Asset',
                    title="Portfolio Distribution",
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                st.plotly_chart(fig, use_container_width=True)
            
        except Exception as e:
            st.error(f"Error loading portfolio data: {e}")
    
    def render_trading_signals(self):
        """Render trading signals section"""
        st.header("📡 Trading Signals")
        
        if not st.session_state.initialized:
            st.warning("Please initialize the system first.")
            return
        
        try:
            # Mock market data for demonstration
            market_data = {
                "prices": [1.0, 1.02, 0.98, 1.05, 0.95, 1.08, 0.92],
                "volatility_zscore": 2.0,
                "impact_bps": 18.0,
                "impact_gap_bps": 28.0,
                "depth_ok": True,
                "better_bps": 22.0
            }
            
            signals = self.orchestrator.trading_agent.generate_trading_signals(market_data)
            
            if signals:
                st.success(f"Generated {len(signals)} trading signals")
                
                for i, signal in enumerate(signals, 1):
                    with st.expander(f"Signal {i}: {signal.action} {signal.asset}"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write(f"**Amount:** {signal.amount:.2f}")
                            st.write(f"**Reason:** {signal.reason}")
                        
                        with col2:
                            st.write(f"**Confidence:** {signal.confidence:.2f}")
                            
                            # Confidence bar
                            confidence_color = "green" if signal.confidence > 0.7 else "orange" if signal.confidence > 0.4 else "red"
                            st.markdown(f"""
                            <div style="background-color: {confidence_color}; height: 20px; width: {signal.confidence * 100}%; border-radius: 10px;"></div>
                            """, unsafe_allow_html=True)
            else:
                st.info("No trading signals at this time")
                
        except Exception as e:
            st.error(f"Error generating signals: {e}")
    
    def render_stablecoin_strategy(self):
        """Render stablecoin strategy section"""
        st.header("🪙 Stablecoin Strategy")
        
        if not st.session_state.initialized:
            st.warning("Please initialize the system first.")
            return
        
        try:
            asyncio.run(self.orchestrator.asset_manager.update_asset_data(self.orchestrator.payment_agent.w.public))
            
            should_convert_to_usdc = self.orchestrator.asset_manager.should_convert_to_usdc()
            should_convert_from_usdc = self.orchestrator.asset_manager.should_convert_from_usdc()
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Current Status")
                if should_convert_to_usdc:
                    target_asset = self.orchestrator.asset_manager.get_asset_to_convert()
                    st.warning(f"🔄 Should convert {target_asset.upper()} to USDC (high volatility)")
                elif should_convert_from_usdc:
                    st.info("🔄 Should convert USDC to assets (low volatility)")
                else:
                    st.success("😴 No stablecoin conversion needed")
            
            with col2:
                st.subheader("Strategy Parameters")
                col_a, col_b, col_c = st.columns(3)
                
                with col_a:
                    st.metric("USDC Target", f"{self.orchestrator.trading_agent.usdc_allocation_target}%")
                
                with col_b:
                    st.metric("High Vol Threshold", f"{self.orchestrator.trading_agent.volatility_threshold_high}")
                
                with col_c:
                    st.metric("Low Vol Threshold", f"{self.orchestrator.trading_agent.volatility_threshold_low}")
            
            # Volatility chart
            st.subheader("Asset Volatility")
            volatility_data = []
            for asset_name, asset_info in self.orchestrator.asset_manager.assets.items():
                if asset_name != 'usdc':
                    volatility_data.append({
                        'Asset': asset_name.upper(),
                        'Volatility': asset_info.volatility
                    })
            
            if volatility_data:
                df_vol = pd.DataFrame(volatility_data)
                fig = px.bar(
                    df_vol, 
                    x='Asset', 
                    y='Volatility',
                    title="Asset Volatility Levels",
                    color='Volatility',
                    color_continuous_scale='RdYlGn_r'
                )
                
                # Add threshold lines
                fig.add_hline(
                    y=self.orchestrator.trading_agent.volatility_threshold_high,
                    line_dash="dash",
                    line_color="red",
                    annotation_text="High Vol Threshold"
                )
                fig.add_hline(
                    y=self.orchestrator.trading_agent.volatility_threshold_low,
                    line_dash="dash",
                    line_color="green",
                    annotation_text="Low Vol Threshold"
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
        except Exception as e:
            st.error(f"Error checking stablecoin strategy: {e}")
    
    def render_risk_management(self):
        """Render comprehensive risk management section"""
        st.header("🛡️ Risk Management")
        
        if not st.session_state.initialized:
            st.warning("Please initialize the system first.")
            return
        
        # Check if using advanced Risk Agent
        risk_agent = self.orchestrator.risk_agent
        has_advanced_risk = hasattr(risk_agent, 'get_comprehensive_risk_report')
        
        # ===== Trading Status =====
        if has_advanced_risk:
            should_halt, reason = asyncio.run(risk_agent.should_halt_trading())
            
            if should_halt or getattr(risk_agent, 'trading_halted', False):
                st.error(f"""
                ### 🔴 Trading Halted
                **Reason**: {reason or risk_agent.halt_reason or 'Unknown'}
                **Time**: {getattr(risk_agent, 'halt_timestamp', 'Unknown')}
                """)
                
                if st.button("🟢 Resume Trading", type="primary"):
                    risk_agent.resume_trading()
                    st.success("✅ Trading resumed!")
                    st.rerun()
            else:
                st.success("### 🟢 Trading Active - System Running Normally")
        
        st.markdown("---")
        
        # ===== Risk Overview =====
        st.subheader("📊 Risk Overview")
        
        try:
            # Try to get risk metrics from latest trading cycle first
            portfolio_risk = st.session_state.latest_risk_metrics
            
            # Fallback to risk agent report if no trading cycle data
            if not portfolio_risk and has_advanced_risk:
                report = risk_agent.get_comprehensive_risk_report()
                portfolio_risk = report.get('portfolio_risk')
                
            if portfolio_risk:
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    overall_risk = portfolio_risk.get('overall_risk_score', 0.5)
                    risk_level = "MEDIUM" if overall_risk < 0.6 else "HIGH" if overall_risk < 0.8 else "CRITICAL"
                    risk_color = {"LOW": "🟢", "MEDIUM": "🟡", "HIGH": "🟠", "CRITICAL": "🔴"}.get(risk_level, "⚪")
                    st.metric("Overall Risk", f"{overall_risk:.2f}", delta=f"{risk_color} {risk_level}", delta_color="inverse")
                
                with col2:
                    var_95 = portfolio_risk.get('var_95', 0)
                    st.metric("VaR (95%)", f"{var_95*100:.2f}%", 
                            delta="✅" if var_95 < 0.10 else "⚠️", delta_color="off")
                
                with col3:
                    sharpe = portfolio_risk.get('sharpe_ratio', 0)
                    st.metric("Sharpe Ratio", f"{sharpe:.2f}",
                            delta="✅" if sharpe > 1.0 else "⚠️", delta_color="off")
                
                with col4:
                    cvar_95 = portfolio_risk.get('cvar_95', 0)
                    st.metric("CVaR (95%)", f"{cvar_95*100:.2f}%",
                            delta="✅" if cvar_95 < 0.15 else "⚠️", delta_color="off")
            else:
                st.warning("ℹ️ No risk metrics available yet. Please run a trading cycle to generate portfolio risk data.")
        
        except Exception as e:
            st.error(f"Error loading risk overview: {e}")
        
        st.markdown("---")
        
        # ===== Detailed Risk Metrics =====
        st.subheader("📈 Portfolio Risk Metrics")
        
        if has_advanced_risk and portfolio_risk:
            tab1, tab2, tab3 = st.tabs(["Traditional Metrics", "PortfolioSpecific", "Risk Score"])
            
            with tab1:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**VaR & CVaR**")
                    metrics_data = {
                        "Metric": ["VaR (95%)", "CVaR (95%)", "VaR (99%)", "CVaR (99%)"],
                        "Value": [
                            f"{portfolio_risk.get('var_95', 0)*100:.2f}%",
                            f"{portfolio_risk.get('cvar_95', 0)*100:.2f}%",
                            f"{portfolio_risk.get('var_99', 0)*100:.2f}%",
                            f"{portfolio_risk.get('cvar_99', 0)*100:.2f}%"
                        ],
                        "Status": [
                            "✅" if portfolio_risk.get('var_95', 0) < 0.10 else "⚠️",
                            "✅" if portfolio_risk.get('cvar_95', 0) < 0.12 else "⚠️",
                            "✅" if portfolio_risk.get('var_99', 0) < 0.15 else "⚠️",
                            "✅" if portfolio_risk.get('cvar_99', 0) < 0.18 else "⚠️"
                        ]
                    }
                    st.dataframe(pd.DataFrame(metrics_data), hide_index=True, use_container_width=True)
                
                with col2:
                    st.markdown("**Return Metrics**")
                    perf_data = {
                        "Metric": ["Sharpe Ratio", "Sortino Ratio", "Calmar Ratio"],
                        "Value": [
                            f"{portfolio_risk.get('sharpe_ratio', 0):.2f}",
                            f"{portfolio_risk.get('sortino_ratio', 0):.2f}",
                            f"{portfolio_risk.get('calmar_ratio', 0):.2f}"
                        ],
                        "Rating": [
                            "Excellent" if portfolio_risk.get('sharpe_ratio', 0) > 2 else "Good" if portfolio_risk.get('sharpe_ratio', 0) > 1 else "Fair",
                            "Excellent" if portfolio_risk.get('sortino_ratio', 0) > 2 else "Good" if portfolio_risk.get('sortino_ratio', 0) > 1 else "Fair",
                            "Excellent" if portfolio_risk.get('calmar_ratio', 0) > 3 else "Good" if portfolio_risk.get('calmar_ratio', 0) > 1 else "Fair"
                        ]
                    }
                    st.dataframe(pd.DataFrame(perf_data), hide_index=True, use_container_width=True)
            
            with tab2:
                portfolio_data = {
                    "Metric": [
                        "Portfolio Volatility",
                        "Correlation Risk",
                        "Concentration Risk",
                        "Diversification Ratio"
                    ],
                    "Value": [
                        f"{portfolio_risk.get('portfolio_volatility', 0)*100:.2f}%",
                        f"{portfolio_risk.get('correlation_risk', 0):.2f}",
                        f"{portfolio_risk.get('concentration_risk', 0):.2f}",
                        f"{portfolio_risk.get('diversification_ratio', 0):.2f}"
                    ],
                    "Status": [
                        "✅" if portfolio_risk.get('portfolio_volatility', 0) < 0.25 else "⚠️",
                        "✅" if portfolio_risk.get('correlation_risk', 0) < 0.6 else "⚠️",
                        "✅" if portfolio_risk.get('concentration_risk', 0) < 0.6 else "⚠️",
                        "✅" if portfolio_risk.get('diversification_ratio', 0) > 0.4 else "⚠️"
                    ]
                }
                st.dataframe(pd.DataFrame(portfolio_data), hide_index=True, use_container_width=True)
            
            with tab3:
                # Risk Score Visualization
                overall_risk = portfolio_risk.get('overall_risk_score', 0.5)
                
                fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=overall_risk * 100,
                    domain={'x': [0, 1], 'y': [0, 1]},
                    title={'text': "Overall Risk Score"},
                    gauge={
                        'axis': {'range': [0, 100]},
                        'bar': {'color': "darkblue"},
                        'steps': [
                            {'range': [0, 40], 'color': "lightgreen"},
                            {'range': [40, 60], 'color': "yellow"},
                            {'range': [60, 80], 'color': "orange"},
                            {'range': [80, 100], 'color': "red"}
                        ],
                        'threshold': {
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': 75
                        }
                    }
                ))
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("ℹ️ Use advanced Risk Agent to view detailed portfolio metrics")
        
        st.markdown("---")
        
        # ===== Real-time Monitoring =====
        if has_advanced_risk:
            st.subheader("⚡ Real-time Monitoring")
            
            report = risk_agent.get_comprehensive_risk_report()
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("**Slippage Monitoring**")
                slippage = report.get("slippage", {})
                avg_slip = slippage.get("avg_bps", 0)
                max_slip = slippage.get("max_bps", 0)
                violations = slippage.get("violations", 0)
                
                st.metric("Average Slippage", f"{avg_slip:.1f} bps",
                        delta="✅" if avg_slip < 30 else "⚠️", delta_color="off")
                st.metric("Max Slippage", f"{max_slip:.1f} bps",
                        delta="✅" if max_slip < 50 else "🚨", delta_color="off")
                st.metric("Violations", violations,
                        delta="✅" if violations == 0 else "⚠️", delta_color="off")
                st.progress(min(avg_slip / 50, 1.0))
            
            with col2:
                st.markdown("**Liquidity Monitoring**")
                liquidity = report.get("liquidity", {})
                avg_score = liquidity.get("avg_score", 0)
                min_score = liquidity.get("min_score", 0)
                
                st.metric("Average Score", f"{avg_score:.2f}",
                        delta="✅" if avg_score > 0.6 else "⚠️", delta_color="off")
                st.metric("Min Score", f"{min_score:.2f}",
                        delta="✅" if min_score > 0.5 else "🚨", delta_color="off")
                st.metric("Assets Monitored", liquidity.get("assets_monitored", 0))
                st.progress(avg_score)
            
            with col3:
                st.markdown("**Anomaly Detection**")
                anomalies = report.get("anomalies", {})
                total = anomalies.get("total", 0)
                by_severity = anomalies.get("by_severity", {})
                
                st.metric("Total", total)
                st.metric("Critical", by_severity.get("CRITICAL", 0),
                        delta="🚨" if by_severity.get("CRITICAL", 0) > 0 else "✅", delta_color="off")
                st.metric("High", by_severity.get("HIGH", 0),
                        delta="⚠️" if by_severity.get("HIGH", 0) > 0 else "✅", delta_color="off")
            
            st.markdown("---")
            
            # ===== Alert History =====
            st.subheader("🚨 Recent Alerts")
            
            alerts = report.get("alerts", {})
            total_alerts = alerts.get("total", 0)
            
            if total_alerts > 0:
                col1, col2 = st.columns(2)
                
                with col1:
                    by_level = alerts.get("by_level", {})
                    st.write(f"🚨 Critical: {by_level.get('CRITICAL', 0)}")
                    st.write(f"⚠️ Warning: {by_level.get('WARNING', 0)}")
                    st.write(f"ℹ️ Info: {by_level.get('INFO', 0)}")
                
                with col2:
                    by_category = alerts.get("by_category", {})
                    for category, count in by_category.items():
                        st.write(f"**{category}**: {count}")
                
                # Display recent alerts
                if hasattr(risk_agent, 'alerts_history') and risk_agent.alerts_history:
                    st.markdown("**Recent 5 Alerts**")
                    for alert in risk_agent.alerts_history[-5:]:
                        level_icon = {"CRITICAL": "🚨", "WARNING": "⚠️", "INFO": "ℹ️"}.get(alert.level, "📢")
                        st.write(f"{level_icon} `{alert.timestamp.strftime('%H:%M:%S')}` - **{alert.category}**: {alert.message}")
            else:
                st.success("✅ No alerts")
        
        else:
            # Basic Risk Agent Recommendations
            try:
                risk_summary = risk_agent.get_risk_summary()
                st.subheader("💡 Risk Recommendations")
                recommendation = risk_summary.get('recommendation', '')
                
                if "Continue trading" in recommendation:
                    st.success(f"✅ {recommendation}")
                elif "Consider reducing" in recommendation:
                    st.warning(f"⚠️ {recommendation}")
                else:
                    st.error(f"🛑 {recommendation}")
            except:
                pass
    
    def render_trading_log(self):
        """Render trading log section"""
        st.header("📝 Trading Log")
        
        if st.session_state.trading_log:
            # Display log entries
            for entry in reversed(st.session_state.trading_log[-20:]):  # Show last 20 entries
                level_color = {
                    "success": "🟢",
                    "error": "🔴",
                    "warning": "🟡",
                    "info": "🔵"
                }.get(entry["level"], "⚪")
                
                st.write(f"{level_color} **{entry['timestamp']}** - {entry['message']}")
        else:
            st.info("No trading activity yet")
        
        # Clear log button
        if st.button("Clear Log"):
            st.session_state.trading_log = []
            st.rerun()
    
    def render_performance_chart(self):
        """Render performance chart"""
        st.header("📈 Performance Chart")
        
        if not st.session_state.initialized:
            st.warning("Please initialize the system first.")
            return
        
        try:
            # Generate mock performance data
            dates = pd.date_range(start=datetime.now() - timedelta(days=30), end=datetime.now(), freq='D')
            portfolio_values = [1000 + i * 10 + (i % 7) * 5 for i in range(len(dates))]
            
            df_performance = pd.DataFrame({
                'Date': dates,
                'Portfolio Value': portfolio_values
            })
            
            fig = px.line(
                df_performance,
                x='Date',
                y='Portfolio Value',
                title='Portfolio Performance (Last 30 Days)',
                markers=True
            )
            
            fig.update_layout(
                xaxis_title="Date",
                yaxis_title="Portfolio Value (USD)",
                hovermode='x unified'
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
        except Exception as e:
            st.error(f"Error loading performance data: {e}")
    
    def run(self):
        """Run the dashboard"""
        
        # If config not completed, show config interface
        if not st.session_state.config_completed:
            self.render_asset_config()
            return
        
        # Show normal dashboard after config completed
        self.render_header()
        self.render_sidebar()
        
        if st.session_state.initialized:
            # Main content tabs
            tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
                "📊 Portfolio", "📡 Signals", "🤖 AI Agents", "🪙 Stablecoin", "🛡️ Risk", "📝 Log", "📈 Performance"
            ])
            
            with tab1:
                self.render_portfolio_overview()
            
            with tab2:
                self.render_trading_signals()
            
            with tab3:
                # NEW: Real-time Agent Conversation
                render_agent_conversation()
            
            with tab4:
                self.render_stablecoin_strategy()
            
            with tab5:
                self.render_risk_management()
            
            with tab6:
                self.render_trading_log()
            
            with tab7:
                self.render_performance_chart()
        else:
            st.info("👆 Please initialize the system using the sidebar controls to begin.")
            
            # Display configuration summary
            st.markdown("---")
            st.subheader("📋 Current Configuration")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Trading Assets", f"{len(st.session_state.selected_assets)}")
                st.caption(", ".join(st.session_state.selected_assets[:5]))
                if len(st.session_state.selected_assets) > 5:
                    st.caption(f"...etc{len(st.session_state.selected_assets)}")
            
            with col2:
                st.metric("Hedge Currency", st.session_state.hedge_currency)
                st.caption("For risk management and settlement")
            
            with col3:
                st.metric("Initial Asset", "XLM")
                if st.session_state.xlm_balance > 0:
                    st.caption(f"Balance: {st.session_state.xlm_balance:.2f}")

# Run the dashboard
if __name__ == "__main__":
    dashboard = TreasuryDashboard()
    dashboard.run()
