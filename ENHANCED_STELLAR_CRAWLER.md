# 🚀 增强版Stellar数据爬取器

## 📊 项目整理完成

### ✅ **保留的核心文件**

#### 🎯 **主要脚本**
- `enhanced_stellar_crawler.py` - **增强版Stellar数据爬取器**（推荐使用）
- `smart_start.py` - 智能启动脚本
- `cli_dashboard.py` - 命令行仪表板

#### 🤖 **AI代理系统**
- `agents/` - 完整的AI代理模块
- `app/` - Web应用模块
- `stellar/` - Stellar网络集成

#### 📊 **数据文件**
- `data/` - 爬取的真实Stellar数据（运行后生成）
- `stellar_enhanced_data.json` - 增强数据（技术指标+ML特征）

### 🗑️ **已删除的文件**

#### 旧的数据爬取文件
- `demo_stellar_crawler.py` - 旧的演示版爬取器
- `demo_stellar_data.json` - 旧的演示数据
- `use_stellar_data.py` - 旧的数据使用脚本
- `stellar_training_data.json` - 旧的训练数据

#### 重复的增强版文件
- `enhanced_stellar_crawler.py` - 重复的增强版文件

## 🎯 **增强版脚本特点**

### ✅ **真实数据源**
- **Stellar DEX真实数据** - 从Horizon主网API获取
- **15分钟K线数据** - 高精度市场数据
- **多资产支持** - BTC, ETH, SOL, ARB, LINK, AAVE, LDO, FET
- **智能资产解析** - 自动选择最活跃发行方

### ✅ **技术指标计算**
- **移动平均线** - SMA, EMA
- **动量指标** - RSI, MACD
- **波动率指标** - 日/周/月波动率
- **布林带** - 上轨、中轨、下轨
- **趋势指标** - 趋势强度和方向

### ✅ **ML/DL/RL特征**
- **机器学习特征** - 价格变化、技术指标特征
- **强化学习数据** - 状态-动作-奖励数据
- **监督学习标签** - 1天/3天/7天标签
- **特征工程** - 54种技术指标

### ✅ **生产级特性**
- **速率限制处理** - 避免API限制
- **重试机制** - 网络错误自动重试
- **容错机制** - USDC失败时回退XLM
- **多格式输出** - CSV, Parquet, JSON

## 🚀 **使用方法**

### 1. 运行增强版爬取器
```bash
python enhanced_stellar_crawler.py
```

### 2. 输出文件
- `data/stellar_ohlc_15m_{ASSET}.csv` - 每个资产的CSV文件
- `data/stellar_ohlc_15m_all.parquet` - 合并的Parquet文件
- `data/stellar_enhanced_data.json` - 增强数据JSON文件

### 3. 配置选项
```bash
# 环境变量配置
export HORIZON_URL="https://horizon.stellar.org"  # 主网
export OUT_DIR="./data"                           # 输出目录
export RESOLUTION_SEC=900                         # 15分钟
export LOOKBACK_DAYS=30                           # 30天
```

## 📊 **数据格式**

### CSV/Parquet格式
- `ts` - 时间戳
- `open, high, low, close` - OHLC价格
- `base_volume, counter_volume` - 成交量
- `num_trades` - 交易次数
- `base_code, base_issuer` - 基础资产信息
- `counter_code, counter_issuer` - 计价资产信息

### JSON格式（增强数据）
- **技术指标** - RSI, MACD, 布林带等
- **ML特征** - 价格变化、趋势、波动率等
- **RL数据** - 动作信号、奖励函数
- **标签数据** - 监督学习标签

## 🎯 **支持的资产**

### 加密货币
- **BTC** - Bitcoin
- **ETH** - Ethereum  
- **SOL** - Solana
- **ARB** - Arbitrum
- **LINK** - Chainlink
- **AAVE** - Aave
- **LDO** - Lido DAO
- **FET** - Fetch.ai

### 计价资产
- **USDC** - USD Coin（优先）
- **XLM** - Stellar Lumens（回退）

## 💡 **优势总结**

### 🥇 **最佳选择**
- **真实数据** + **完整特征工程**
- **生产级质量** + **ML/DL/RL优化**
- **多资产支持** + **技术指标计算**
- **即用性** + **准确性**

### 🎯 **适用场景**
- **机器学习模型训练**
- **深度学习模型微调**
- **强化学习策略优化**
- **量化交易策略开发**

## 📈 **预期结果**

运行后你将获得：
- **真实Stellar DEX数据**
- **54种技术指标**
- **ML特征工程**
- **RL训练数据**
- **多格式输出**

**现在你可以使用这个增强版脚本来获取高质量的Stellar数据了！** 🚀
