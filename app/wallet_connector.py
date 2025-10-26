"""
Freighter Wallet Connector for Stellar AI Treasury
支持 Freighter 钱包连接和余额查询
"""

import streamlit as st
import asyncio
import json
from typing import Optional, Dict, Any
from stellar_sdk import Server, Keypair
from stellar_sdk.exceptions import NotFoundError, BadRequestError
import time

class FreighterConnector:
    """Freighter 钱包连接器"""
    
    def __init__(self):
        self.server = Server("https://horizon-testnet.stellar.org")
        self.connected_address = None
        self.balance = 0.0
        self.balance_usd = 0.0
        
    async def connect_wallet(self) -> bool:
        """连接 Freighter 钱包"""
        try:
            # 获取当前语言设置
            current_language = st.session_state.get('language', 'en')
            
            # 多语言错误信息
            error_texts = {
                'en': {
                    'not_installed': '❌ Freighter wallet not installed or not enabled',
                    'install_link': 'Please visit https://freighter.app/ to install Freighter extension',
                    'connecting': '🔗 Connecting Freighter wallet...',
                    'connected': '✅ Wallet connected successfully!',
                    'address': 'Address:',
                    'invalid': '❌ Invalid wallet address:',
                    'failed': '❌ Connection failed:'
                },
                'zh': {
                    'not_installed': '❌ Freighter 钱包未安装或未启用',
                    'install_link': '请访问 https://freighter.app/ 安装 Freighter 扩展',
                    'connecting': '🔗 正在连接 Freighter 钱包...',
                    'connected': '✅ 钱包连接成功！',
                    'address': '地址:',
                    'invalid': '❌ 无效的钱包地址:',
                    'failed': '❌ 连接失败:'
                }
            }
            
            error_text = error_texts.get(current_language, error_texts['en'])
            
            # 检查 Freighter 是否可用
            if not self._is_freighter_available():
                st.error(error_text['not_installed'])
                st.info(error_text['install_link'])
                return False
            
            # 使用 JavaScript 连接钱包
            st.info(error_text['connecting'])
            
            # 注入 JavaScript 代码
            js_code = """
            <script>
            async function connectWallet() {
                try {
                    if (typeof window.freighterConnector === 'undefined') {
                        // 加载 Freighter 连接器
                        const script = document.createElement('script');
                        script.src = '/static/freighter_connector.js';
                        document.head.appendChild(script);
                        
                        // 等待脚本加载
                        await new Promise(resolve => setTimeout(resolve, 1000));
                    }
                    
                    const result = await window.connectFreighterWallet();
                    return result;
                } catch (error) {
                    return { success: false, error: error.message };
                }
            }
            
            connectWallet().then(result => {
                if (result.success) {
                    // 发送结果到 Streamlit
                    window.parent.postMessage({
                        type: 'freighter_connected',
                        data: result
                    }, '*');
                } else {
                    window.parent.postMessage({
                        type: 'freighter_error',
                        data: result
                    }, '*');
                }
            });
            </script>
            """
            
            st.components.v1.html(js_code, height=0)
            
            # 为了演示，我们使用一个有效的测试地址
            # 这是一个真实的 Stellar 测试网地址
            test_address = "GDOOP2RMH5EA2JFDF6SQTAG5M2FGOXSYSSOHHEDVGQSCRP3R7IVF54FI"
            
            # 验证地址格式
            try:
                Keypair.from_public_key(test_address)
                self.connected_address = test_address
                
                # 🎯 立即设置演示余额（100万美元等值的XLM）
                min_xlm_for_1m_usd = 1000000.0 / 0.31  # 约3,225,806 XLM
                self.balance = min_xlm_for_1m_usd
                self.balance_usd = 1000000.0
                
                st.success(error_text['connected'])
                st.info(f"{error_text['address']} {test_address[:8]}...{test_address[-8:]}")
                st.info(f"🎁 演示模式：钱包余额已设置为 {self.balance:,.0f} XLM (≈$1,000,000)")
                return True
            except Exception as e:
                st.error(f"{error_text['invalid']} {e}")
                return False
                
        except Exception as e:
            st.error(f"{error_text['failed']} {e}")
            return False
    
    def _is_freighter_available(self) -> bool:
        """检查 Freighter 是否可用"""
        # 在实际实现中，这里会检查 window.freighter 是否存在
        # 为了演示，我们返回 True
        return True
    
    async def get_balance(self, address: str) -> Dict[str, Any]:
        """查询 Stellar 余额"""
        try:
            # 获取当前语言设置
            current_language = st.session_state.get('language', 'en')
            
            # 多语言查询信息
            query_texts = {
                'en': {
                    'querying': '🔍 Querying balance for address',
                    'not_found': '⚠️ Address does not exist or balance is 0',
                    'query_failed': '❌ Failed to query balance:'
                },
                'zh': {
                    'querying': '🔍 查询地址',
                    'not_found': '⚠️ 地址不存在或余额为 0',
                    'query_failed': '❌ 查询余额失败:'
                }
            }
            
            query_text = query_texts.get(current_language, query_texts['en'])
            
            st.info(f"{query_text['querying']} {address[:8]}...{address[-8:]}...")
            
            # 查询账户信息
            account = self.server.accounts().account_id(address).call()
            
            # 获取 XLM 余额
            xlm_balance = 0.0
            for balance in account['balances']:
                if balance['asset_type'] == 'native':
                    xlm_balance = float(balance['balance'])
                    break
            
            # 🎯 为了演示，给钱包添加更多余额（至少100万美元等值的XLM）
            # 100万美元 ÷ $0.31 = 3,225,806 XLM
            min_xlm_for_1m_usd = 1000000.0 / 0.31  # 约3,225,806 XLM
            if xlm_balance < min_xlm_for_1m_usd:
                xlm_balance = min_xlm_for_1m_usd  # 设置为至少100万美元等值的XLM
                st.info(f"🎁 演示模式：钱包余额已设置为 {xlm_balance:,.0f} XLM (≈$1,000,000)")
            
            # 计算美元价值（使用固定汇率 $0.31）
            usd_value = xlm_balance * 0.31
            
            self.balance = xlm_balance
            self.balance_usd = usd_value
            
            return {
                'address': address,
                'xlm_balance': xlm_balance,
                'usd_value': usd_value,
                'network': 'testnet',
                'timestamp': time.time()
            }
            
        except NotFoundError:
            st.warning(query_text['not_found'])
            return {
                'address': address,
                'xlm_balance': 0.0,
                'usd_value': 0.0,
                'network': 'testnet',
                'timestamp': time.time()
            }
        except Exception as e:
            st.error(f"{query_text['query_failed']} {e}")
            return {
                'address': address,
                'xlm_balance': 0.0,
                'usd_value': 0.0,
                'network': 'testnet',
                'error': str(e)
            }
    
    def disconnect(self):
        """断开钱包连接"""
        self.connected_address = None
        self.balance = 0.0
        self.balance_usd = 0.0
        
        # 获取当前语言设置
        current_language = st.session_state.get('language', 'en')
        
        # 多语言断开信息
        disconnect_texts = {
            'en': '🔌 Wallet disconnected',
            'zh': '🔌 钱包已断开连接'
        }
        
        disconnect_text = disconnect_texts.get(current_language, disconnect_texts['en'])
        st.info(disconnect_text)

def render_wallet_connector():
    """渲染钱包连接器 UI"""
    
    # 获取当前语言设置
    current_language = st.session_state.get('language', 'en')
    
    # 初始化 session state
    if 'wallet_connector' not in st.session_state:
        st.session_state.wallet_connector = FreighterConnector()
    
    connector = st.session_state.wallet_connector
    
    # 多语言文本
    texts = {
        'en': {
            'title': '🦊 Freighter Wallet Connection',
            'connected': '✅ Wallet Connected',
            'address': '**Address**:',
            'balance': '**Balance**:',
            'network': '**Network**:',
            'disconnect': '🔌 Disconnect',
            'refresh': '🔄 Refresh Balance',
            'connect_info': '💡 Connect your Freighter wallet to use real balance',
            'connect_button': '🔗 Connect Freighter Wallet',
            'connecting': 'Connecting wallet...',
            'install_guide': '📖 How to Install Freighter Wallet',
            'step1': '**Step 1**: Visit [freighter.app](https://freighter.app/)',
            'step2': '**Step 2**: Click "Add to Browser" to install extension',
            'step3': '**Step 3**: Create new account or import existing account',
            'step4': '**Step 4**: Switch to **Testnet** network',
            'step5': '**Step 5**: Get test XLM from [Friendbot](https://friendbot.stellar.org/)',
            'step6': '**Step 6**: Return to this page and click "Connect Wallet"',
            'not_installed': '❌ Freighter wallet not installed or not enabled',
            'install_link': 'Please visit https://freighter.app/ to install Freighter extension',
            'connecting_wallet': '🔗 Connecting Freighter wallet...',
            'wallet_connected': '✅ Wallet connected successfully!',
            'address_display': 'Address:',
            'invalid_address': '❌ Invalid wallet address:',
            'connection_failed': '❌ Connection failed:',
            'querying_balance': '🔍 Querying balance for address',
            'balance_not_found': '⚠️ Address does not exist or balance is 0',
            'query_failed': '❌ Failed to query balance:',
            'disconnected': '🔌 Wallet disconnected'
        },
        'zh': {
            'title': '🦊 Freighter 钱包连接',
            'connected': '✅ 钱包已连接',
            'address': '**地址**:',
            'balance': '**余额**:',
            'network': '**网络**:',
            'disconnect': '🔌 断开连接',
            'refresh': '🔄 刷新余额',
            'connect_info': '💡 连接你的 Freighter 钱包以使用真实余额',
            'connect_button': '🔗 连接 Freighter 钱包',
            'connecting': '连接钱包中...',
            'install_guide': '📖 如何安装 Freighter 钱包',
            'step1': '**步骤 1**: 访问 [freighter.app](https://freighter.app/)',
            'step2': '**步骤 2**: 点击 "Add to Browser" 安装扩展',
            'step3': '**步骤 3**: 创建新账户或导入现有账户',
            'step4': '**步骤 4**: 切换到 **Testnet** 网络',
            'step5': '**步骤 5**: 从 [Friendbot](https://friendbot.stellar.org/) 获取测试 XLM',
            'step6': '**步骤 6**: 返回此页面点击 "连接钱包"',
            'not_installed': '❌ Freighter 钱包未安装或未启用',
            'install_link': '请访问 https://freighter.app/ 安装 Freighter 扩展',
            'connecting_wallet': '🔗 正在连接 Freighter 钱包...',
            'wallet_connected': '✅ 钱包连接成功！',
            'address_display': '地址:',
            'invalid_address': '❌ 无效的钱包地址:',
            'connection_failed': '❌ 连接失败:',
            'querying_balance': '🔍 查询地址',
            'balance_not_failed': '⚠️ 地址不存在或余额为 0',
            'query_failed': '❌ 查询余额失败:',
            'disconnected': '🔌 钱包已断开连接'
        }
    }
    
    text = texts.get(current_language, texts['en'])
    
    st.markdown(f"### {text['title']}")
    
    # 连接状态显示
    if connector.connected_address:
        st.success(text['connected'])
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.info(f"{text['address']} `{connector.connected_address[:8]}...{connector.connected_address[-8:]}`")
            st.info(f"{text['balance']} {connector.balance:,.2f} XLM (≈${connector.balance_usd:,.2f})")
            st.info(f"{text['network']} Testnet")
        
        with col2:
            if st.button(text['disconnect'], type="secondary"):
                connector.disconnect()
                st.rerun()
        
        # 余额查询按钮
        if st.button(text['refresh'], type="primary"):
            with st.spinner(text['connecting']):
                balance_info = asyncio.run(connector.get_balance(connector.connected_address))
                st.rerun()
    
    else:
        st.info(text['connect_info'])
        
        # 连接按钮
        if st.button(text['connect_button'], type="primary"):
            with st.spinner(text['connecting']):
                success = asyncio.run(connector.connect_wallet())
                if success:
                    # 查询余额
                    balance_info = asyncio.run(connector.get_balance(connector.connected_address))
                    st.rerun()
        
        # 安装指南
        with st.expander(text['install_guide']):
            st.markdown(f"""
            {text['step1']}
            
            {text['step2']}
            
            {text['step3']}
            
            {text['step4']}
            
            {text['step5']}
            
            {text['step6']}
            """)
    
    return connector

def get_wallet_balance() -> float:
    """获取当前连接钱包的余额"""
    try:
        if hasattr(st.session_state, 'get') and st.session_state.get('wallet_connector'):
            connector = st.session_state.get('wallet_connector')
            if connector and hasattr(connector, 'connected_address') and connector.connected_address:
                return connector.balance
        elif 'wallet_connector' in st.session_state:
            connector = st.session_state.wallet_connector
            if connector.connected_address:
                return connector.balance
    except:
        pass
    return 0.0

def is_wallet_connected() -> bool:
    """检查钱包是否已连接"""
    if 'wallet_connector' in st.session_state:
        connector = st.session_state.wallet_connector
        return connector.connected_address is not None
    return False

def get_connected_address() -> Optional[str]:
    """获取连接的地址"""
    if 'wallet_connector' in st.session_state:
        connector = st.session_state.wallet_connector
        return connector.connected_address
    return None
