#!/usr/bin/env python3
"""
测试 Freighter 钱包集成功能
"""

import sys
import os

# Add project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import asyncio
import streamlit as st
from app.wallet_connector import FreighterConnector

# 设置 session state 用于测试
class MockSessionState:
    def __init__(self):
        self.data = {}
    
    def get(self, key, default=None):
        return self.data.get(key, default)

# 模拟 session state
st.session_state = MockSessionState()
st.session_state.data['language'] = 'zh'

async def test_wallet_connector():
    """测试钱包连接器功能"""
    print("🧪 测试 Freighter 钱包连接器...")
    
    # 创建连接器实例
    connector = FreighterConnector()
    
    # 测试连接
    print("\n1. 测试钱包连接...")
    success = await connector.connect_wallet()
    print(f"   连接结果: {'✅ 成功' if success else '❌ 失败'}")
    
    if success:
        # 测试余额查询
        print("\n2. 测试余额查询...")
        balance_info = await connector.get_balance(connector.connected_address)
        print(f"   余额信息: {balance_info}")
        
        # 测试断开连接
        print("\n3. 测试断开连接...")
        connector.disconnect()
        print("   ✅ 已断开连接")
    
    print("\n🎉 测试完成！")

if __name__ == "__main__":
    asyncio.run(test_wallet_connector())
