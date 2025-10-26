/**
 * Freighter Wallet Connector JavaScript
 * 处理 Freighter 钱包连接和余额查询
 */

class FreighterConnector {
    constructor() {
        this.isConnected = false;
        this.publicKey = null;
        this.network = 'testnet';
    }

    /**
     * 检查 Freighter 是否可用
     */
    isFreighterAvailable() {
        return typeof window.freighter !== 'undefined' && window.freighter.isConnected;
    }

    /**
     * 连接 Freighter 钱包
     */
    async connectWallet() {
        try {
            if (!this.isFreighterAvailable()) {
                throw new Error('Freighter 钱包未安装或未启用');
            }

            // 请求连接权限
            const result = await window.freighter.requestAccess();
            
            if (result.isConnected) {
                this.isConnected = true;
                this.publicKey = result.publicKey;
                return {
                    success: true,
                    publicKey: this.publicKey,
                    network: this.network
                };
            } else {
                throw new Error('用户拒绝了连接请求');
            }
        } catch (error) {
            console.error('连接钱包失败:', error);
            return {
                success: false,
                error: error.message
            };
        }
    }

    /**
     * 断开钱包连接
     */
    disconnect() {
        this.isConnected = false;
        this.publicKey = null;
        return {
            success: true,
            message: '钱包已断开连接'
        };
    }

    /**
     * 获取账户余额
     */
    async getBalance() {
        try {
            if (!this.isConnected || !this.publicKey) {
                throw new Error('钱包未连接');
            }

            // 查询 Stellar 网络余额
            const response = await fetch(`https://horizon-testnet.stellar.org/accounts/${this.publicKey}`);
            
            if (!response.ok) {
                throw new Error(`查询失败: ${response.status}`);
            }

            const account = await response.json();
            
            // 查找 XLM 余额
            let xlmBalance = 0;
            for (const balance of account.balances) {
                if (balance.asset_type === 'native') {
                    xlmBalance = parseFloat(balance.balance);
                    break;
                }
            }

            return {
                success: true,
                balance: xlmBalance,
                publicKey: this.publicKey,
                network: this.network
            };
        } catch (error) {
            console.error('查询余额失败:', error);
            return {
                success: false,
                error: error.message
            };
        }
    }

    /**
     * 获取连接状态
     */
    getConnectionStatus() {
        return {
            isConnected: this.isConnected,
            publicKey: this.publicKey,
            network: this.network
        };
    }
}

// 创建全局实例
window.freighterConnector = new FreighterConnector();

// 导出给 Streamlit 使用
window.connectFreighterWallet = async function() {
    return await window.freighterConnector.connectWallet();
};

window.disconnectFreighterWallet = function() {
    return window.freighterConnector.disconnect();
};

window.getFreighterBalance = async function() {
    return await window.freighterConnector.getBalance();
};

window.getFreighterStatus = function() {
    return window.freighterConnector.getConnectionStatus();
};
