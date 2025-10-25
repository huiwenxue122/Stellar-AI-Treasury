# 🚀 Stellar AI Treasury - 完整设置指南

## 📋 系统要求

### 必需软件
- **Python 3.11+** (推荐 3.11 或 3.12)
- **Git** (用于克隆项目)
- **Rust** (用于智能合约编译，可选)
- **Stellar CLI** (用于智能合约部署，可选)

### 操作系统支持
- ✅ **macOS** (推荐)
- ✅ **Linux** (Ubuntu 20.04+)
- ✅ **Windows** (WSL2 推荐)

---

## 🛠️ 快速开始 (推荐)

### 方法一：一键设置脚本

```bash
# 1. 克隆项目
git clone https://github.com/YOUR_USERNAME/stellar-ai-treasury.git
cd stellar-ai-treasury

# 2. 运行自动设置脚本
python setup.py
```

### 方法二：手动设置

#### 步骤 1: 创建虚拟环境

```bash
# 创建虚拟环境
python -m venv stellar-ai-env

# 激活虚拟环境
# macOS/Linux:
source stellar-ai-env/bin/activate
# Windows:
# stellar-ai-env\Scripts\activate
```

#### 步骤 2: 安装依赖

```bash
# 升级pip
pip install --upgrade pip

# 安装项目依赖
pip install -r requirements.txt
```

#### 步骤 3: 配置环境变量

```bash
# 创建.env文件
cp .env.example .env  # 如果存在
# 或手动创建.env文件
```

编辑 `.env` 文件：
```bash
# Stellar Testnet Configuration
STELLAR_SECRET=your_stellar_secret_key_here
STELLAR_PUBLIC=your_stellar_public_key_here

# OpenAI Configuration (可选)
OPENAI_API_KEY=your_openai_api_key_here
```

#### 步骤 4: 获取Stellar测试网账户

```bash
# 自动创建测试网账户
python create_testnet_account.py
```

#### 步骤 5: 启动项目

```bash
# 智能启动 (推荐)
python smart_start.py

# 或传统启动
python start.py

# 或命令行界面
python cli_dashboard.py
```

---

## 🔧 详细设置步骤

### 1. Python环境设置

#### 检查Python版本
```bash
python --version
# 应该显示 Python 3.11+ 或更高版本
```

#### 创建虚拟环境 (推荐)
```bash
# 使用venv创建虚拟环境
python -m venv stellar-ai-env

# 激活虚拟环境
# macOS/Linux:
source stellar-ai-env/bin/activate

# Windows:
# stellar-ai-env\Scripts\activate

# 验证虚拟环境
which python  # 应该指向虚拟环境中的python
```

#### 使用conda (可选)
```bash
# 创建conda环境
conda create -n stellar-ai python=3.11
conda activate stellar-ai
```

### 2. 安装项目依赖

```bash
# 确保在项目根目录
cd /path/to/stellar-ai-treasury

# 升级pip
pip install --upgrade pip

# 安装核心依赖
pip install -r requirements.txt

# 验证安装
python -c "import stellar_sdk, streamlit, plotly; print('✅ 核心依赖安装成功')"
```

### 3. 配置Stellar测试网

#### 方法A: 自动创建账户 (推荐)
```bash
python create_testnet_account.py
```

#### 方法B: 手动创建账户
1. 访问 [Stellar Laboratory](https://laboratory.stellar.org/#account-creator?network=test)
2. 点击 "Generate keypair"
3. 点击 "Fund account with friendbot"
4. 复制密钥到 `.env` 文件

#### 方法C: 使用现有账户
```bash
# 编辑.env文件
STELLAR_SECRET=SDXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
STELLAR_PUBLIC=GDXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

### 4. 智能合约设置 (可选)

#### 安装Rust和Stellar CLI
```bash
# 安装Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source ~/.cargo/env

# 安装Stellar CLI
cargo install stellar-cli
```

#### 部署智能合约
```bash
# 自动部署
python deploy_contract.py

# 或手动部署
cd contracts/ai_treasury_vault
stellar contract build
stellar contract deploy --wasm target/wasm32v1-none/release/ai_treasury_vault.wasm --source YOUR_SECRET --network testnet
```

### 5. 启动项目

#### 方法A: 智能启动 (推荐)
```bash
python smart_start.py
```
- 自动检查依赖
- 自动清理旧进程
- 自动寻找可用端口
- 自动打开浏览器

#### 方法B: 传统启动
```bash
python start.py
```

#### 方法C: 直接启动仪表板
```bash
python run_dashboard.py
```

#### 方法D: 命令行界面
```bash
python cli_dashboard.py
```

---

## 🧪 测试安装

### 运行系统测试
```bash
# 测试基本功能
python test_system.py

# 测试前端
python test_frontend.py

# 测试实时数据
python test_live_data.py
```

### 验证Stellar连接
```bash
# 测试Stellar连接
python -c "
from stellar.wallet import Wallet
from app.config import load_config
config = load_config()
wallet = Wallet(config['network']['horizon'], config['network']['passphrase'], 'STELLAR_SECRET', 'STELLAR_PUBLIC')
print('✅ Stellar连接成功')
"
```

---

## 🚨 常见问题解决

### 问题1: 模块导入错误
```bash
# 解决方案: 确保在项目根目录运行
cd /path/to/stellar-ai-treasury
export PYTHONPATH=$PWD:$PYTHONPATH
python smart_start.py
```

### 问题2: 端口被占用
```bash
# 解决方案: 智能启动脚本会自动寻找可用端口
python smart_start.py
# 或手动指定端口
python -m streamlit run app/dashboard.py --server.port 8502
```

### 问题3: Stellar连接失败
```bash
# 解决方案: 检查网络和密钥
python create_testnet_account.py  # 重新创建账户
```

### 问题4: 依赖安装失败
```bash
# 解决方案: 使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
```

### 问题5: 虚拟环境问题
```bash
# 解决方案: 重新创建虚拟环境
deactivate
rm -rf stellar-ai-env
python -m venv stellar-ai-env
source stellar-ai-env/bin/activate
pip install -r requirements.txt
```

---

## 📱 使用指南

### 1. 启动后操作
1. **打开浏览器** → `http://localhost:8501`
2. **配置资产** → 选择要交易的资产
3. **初始化系统** → 连接Stellar测试网
4. **运行交易周期** → 观看AI代理协作
5. **监控** → 查看"🤖 AI代理"标签页

### 2. 主要功能
- **📊 投资组合可视化** → 实时资产分布
- **🤖 AI代理对话** → 查看代理决策过程
- **📈 交易历史** → 查看所有交易记录
- **🛡️ 风险管理** → 实时风险指标监控

### 3. 配置选项
- **资产选择** → BTC, ETH, SOL, USDC等
- **交易策略** → 10种量化策略
- **风险参数** → VaR, Sharpe Ratio等
- **智能合约** → 链上风险控制

---

## 🔗 有用链接

- **Stellar Laboratory**: https://laboratory.stellar.org
- **Stellar Explorer**: https://stellar.expert
- **项目文档**: 查看 `docs/` 目录
- **智能合约**: 查看 `contracts/` 目录

---

## 📞 获取帮助

如果遇到问题：
1. 查看 `README.md` 文件
2. 运行 `python diagnose_frontend.py` 诊断
3. 检查 `.env` 文件配置
4. 确保所有依赖已正确安装

---

**🎉 设置完成！现在你可以开始使用Stellar AI Treasury系统了！**
