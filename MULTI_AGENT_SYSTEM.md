# 🤖 Multi-Agent协作系统

## 📋 系统架构

你的Stellar AI Treasury现在是一个真正的**Multi-Agent协作系统**，模拟顶级量化对冲基金的运作模式。

### 三个AI Agent协作流程

```
┌─────────────────────────────────────────────────────────────┐
│  Trading Agent - "James Simons"                             │
│  像文艺复兴基金创始人一样的量化研究员                         │
│                                                              │
│  任务: 分析市场数据，生成1-3个交易信号                        │
│  工具:                                                       │
│    • Momentum Strategy (动量策略)                            │
│    • Mean Reversion (均值回归)                               │
│    • Path Improvement (路径优化)                             │
│    • Stablecoin Strategy (稳定币策略)                        │
│    • Multi-Asset Rebalancing (多资产再平衡)                  │
│    • Multi-Asset Momentum (多资产动量)                       │
│                                                              │
│  输出: [Signal1, Signal2, Signal3] → 发送给Risk Agent       │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ↓ 生成的交易信号
┌─────────────────────────────────────────────────────────────┐
│  Risk Agent - "风险管理专家"                                 │
│  专业的风险评估和信号筛选                                     │
│                                                              │
│  任务: 评估每个信号的风险，选择最优的一个                     │
│  评估维度:                                                   │
│    • VaR (95% Value at Risk)                                │
│    • CVaR (Conditional VaR)                                 │
│    • Sharpe Ratio (夏普比率)                                │
│    • Max Drawdown (最大回撤)                                │
│    • Risk Score (综合风险评分)                              │
│                                                              │
│  选择逻辑:                                                   │
│    - 风险调整后收益最高                                      │
│    - 如果所有信号风险过高 → 拒绝全部                         │
│                                                              │
│  输出: BestSignal → 发送给Payment Agent                     │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ↓ 选中的最优信号
┌─────────────────────────────────────────────────────────────┐
│  Payment Agent - "交易执行专家"                              │
│  精确执行交易并结算为USDC                                    │
│                                                              │
│  任务: 执行选定的交易，将收益转换为USDC                       │
│  执行步骤:                                                   │
│    1. 分析交易信号                                           │
│    2. 使用Stellar Path Payment找到最优路径                   │
│    3. 执行交易（最小化滑点和成本）                            │
│    4. 将所有收益转换为USDC                                   │
│    5. 记录交易到Risk Agent                                   │
│                                                              │
│  结算原则:                                                   │
│    - 所有资产最终以USDC计价                                  │
│    - 类似Robinhood的美元结算模式                             │
│    - 交易者从XLM开始，最终获得USDC收益                        │
│                                                              │
│  输出: 执行结果 + USDC收益                                   │
└─────────────────────────────────────────────────────────────┘
```

## 🎯 为什么这样设计？

### 1. **专业化分工**
- **Trading Agent**: 专注策略研究和信号生成
- **Risk Agent**: 专注风险评估和信号筛选  
- **Payment Agent**: 专注交易执行和结算

### 2. **风险控制**
- 多个信号竞争，只执行风险最低的
- AI评估每个信号的多维度风险
- 自动拒绝高风险交易

### 3. **收益优化**
- 6种策略组合，捕捉不同市场机会
- 风险调整后收益（Risk-Adjusted Return）
- USDC结算，清晰的盈亏计算

## 🚀 如何使用

### 1. 启用Multi-Agent系统

编辑 `app/config.yaml`:

```yaml
agent_system:
  enabled: true  # ← 设置为true启用
  model: "gpt-4"  # 或 "gpt-4-turbo" / "gpt-3.5-turbo"
```

### 2. 设置OpenAI API Key

```bash
export OPENAI_API_KEY="sk-your-api-key-here"
```

或在 `.env` 文件中添加：
```
OPENAI_API_KEY=sk-your-api-key-here
```

### 3. 运行测试

```bash
python test_multi_agent.py
```

### 4. 启动Dashboard

```bash
python smart_start.py
```

点击 "Run Trading Cycle" 按钮，你会看到：

```
🤖 使用Multi-Agent协作系统...
==============================================================

1️⃣ Trading Agent: 分析市场并生成交易信号...
   ✅ 生成了 3 个交易信号
      1. BUY XLM - momentum_strategy
      2. CONVERT_TO_USDC BTC - stablecoin_strategy
      3. BUY ETH - multi_asset_momentum

2️⃣ Risk Agent: 评估每个信号的风险...
   ✅ 选择最优信号: BUY XLM
      风险评分: 0.35
      预期收益: 5.20%

3️⃣ Payment Agent: 执行交易并结算为USDC...
   📋 执行计划: 使用path payment优化路径
   ✅ 交易执行完成
      USDC收益: $125.50
```

## 📊 Agent配置详解

### Trading Agent配置

```yaml
trading_agent:
  personality: "James Simons"  # AI人格
  temperature: 0.7             # 创造性 (0=保守, 1=激进)
  max_signals: 3               # 最多生成3个信号
```

**温度建议**:
- `0.3-0.5`: 保守，适合牛市
- `0.6-0.8`: 平衡，适合大多数情况
- `0.8-1.0`: 激进，适合熊市寻找机会

### Risk Agent配置

```yaml
risk_agent:
  personality: "Risk Manager"
  temperature: 0.3             # 低温度=更保守
  max_risk_score: 0.7          # 最大可接受风险
```

**风险阈值**:
- `0.5`: 非常保守，只接受极低风险
- `0.7`: 平衡（推荐）
- `0.9`: 激进，接受较高风险

### Payment Agent配置

```yaml
payment_agent:
  personality: "Execution Specialist"
  temperature: 0.2             # 极低温度=精确执行
  always_settle_to_usdc: true  # 总是结算为USDC
```

## 🔄 完整流程示例

### 输入: 市场数据

```json
{
  "prices": [0.11, 0.115, 0.12, 0.125],
  "volatility_zscore": 1.8,
  "assets": {
    "XLM": {"price": 0.13, "change_24h": 8.3},
    "BTC": {"price": 109707, "change_24h": 1.34},
    "ETH": {"price": 3854, "change_24h": 1.15}
  }
}
```

### Step 1: Trading Agent生成信号

```json
{
  "signals": [
    {
      "action": "BUY",
      "asset": "XLM",
      "amount": 1000,
      "strategy": "momentum_strategy",
      "reason": "XLM显示强劲上涨趋势(+8.3%)，动量指标良好",
      "expected_return": 0.052,
      "confidence": 0.78
    },
    {
      "action": "CONVERT_TO_USDC",
      "asset": "BTC",
      "amount": 0.01,
      "strategy": "stablecoin_strategy",
      "reason": "市场波动率偏高，建议部分转为USDC避险",
      "expected_return": 0.0,
      "confidence": 0.65
    },
    {
      "action": "BUY",
      "asset": "ETH",
      "amount": 1.5,
      "strategy": "multi_asset_momentum",
      "reason": "ETH与BTC相关性低，分散投资风险",
      "expected_return": 0.032,
      "confidence": 0.62
    }
  ]
}
```

### Step 2: Risk Agent评估

```json
{
  "risk_analysis": {
    "signal_0": {
      "var_95": 0.045,
      "cvar_95": 0.062,
      "sharpe_ratio": 1.45,
      "max_drawdown": 0.08,
      "risk_score": 0.35,
      "risk_adjusted_return": 0.042
    },
    "signal_1": {
      "var_95": 0.012,
      "cvar_95": 0.015,
      "sharpe_ratio": 0.0,
      "max_drawdown": 0.02,
      "risk_score": 0.15,
      "risk_adjusted_return": 0.0
    },
    "signal_2": {
      "var_95": 0.055,
      "cvar_95": 0.075,
      "sharpe_ratio": 1.12,
      "max_drawdown": 0.12,
      "risk_score": 0.48,
      "risk_adjusted_return": 0.025
    }
  },
  "selected_signal_index": 0,
  "recommendation": "选择Signal 0 (BUY XLM)，因为风险调整后收益最高(4.2%)，且风险评分可接受(0.35)"
}
```

### Step 3: Payment Agent执行

```json
{
  "execution_plan": "使用Stellar path payment从USDC转换为XLM，预计路径成本18 bps",
  "estimated_usdc_profit": 125.50,
  "steps": [
    "1. 从钱包获取130 USDC",
    "2. 通过path payment转换为1000 XLM",
    "3. 执行后预期价值: 130 * 1.052 = 136.76 USDC",
    "4. 净收益: 136.76 - 130 = 6.76 USDC"
  ],
  "success": true,
  "usdc_profit": 6.76,
  "transaction_hash": "a1b2c3d4e5f6..."
}
```

### 输出: 最终结果

```json
{
  "status": "SUCCESS",
  "mode": "multi_agent",
  "trading_signals_generated": 3,
  "selected_signal": {
    "action": "BUY",
    "asset": "XLM",
    "strategy": "momentum_strategy",
    "risk_score": 0.35
  },
  "total_usdc_profit": 6.76,
  "portfolio_value_usd": 1536.76,
  "usdc_allocation": 45.2
}
```

## 💡 Agent人格特点

### Trading Agent: "James Simons"

**人格特征**:
- 数学/统计导向
- 多策略组合
- 数据驱动决策
- 不相信直觉，只相信数据

**Prompt示例**:
```
你是世界顶级量化研究员James Simons。
- 用数学和统计分析市场
- 组合使用多种策略
- 每个决策都有数据支撑
- 说明预期收益和信心度
```

### Risk Agent: "风险管理专家"

**人格特征**:
- 保守谨慎
- 全面风险评估
- 拒绝不确定性高的交易
- 优先保护本金

**Prompt示例**:
```
你是专业风险管理专家。
- 全面评估每个信号的风险
- 计算VaR, CVaR, Sharpe等指标
- 如果所有信号风险过高，勇于说"不"
- 优先考虑风险调整后收益
```

### Payment Agent: "执行专家"

**人格特征**:
- 精确执行
- 成本优化
- 不质疑决策
- 确保USDC结算

**Prompt示例**:
```
你是交易执行专家。
- 精确执行选定的交易
- 使用最优路径减少成本
- 将所有收益转换为USDC
- 记录完整交易细节
```

## 🎛️ 高级配置

### 启用/禁用Multi-Agent

```yaml
agent_system:
  enabled: true  # true=AI协作, false=传统规则
```

- `true`: 使用OpenAI Agent，会消耗API credits
- `false`: 使用传统规则系统，不调用OpenAI

### 选择AI模型

```yaml
agent_system:
  model: "gpt-4"  # 选项
```

**模型对比**:

| 模型 | 智能程度 | 速度 | 成本 | 推荐场景 |
|------|---------|------|------|---------|
| gpt-4 | ⭐⭐⭐⭐⭐ | 慢 | 高 | 生产环境 |
| gpt-4-turbo | ⭐⭐⭐⭐ | 快 | 中 | 推荐 |
| gpt-3.5-turbo | ⭐⭐⭐ | 很快 | 低 | 测试/开发 |

### 调整Agent温度

```yaml
trading_agent:
  temperature: 0.7  # 0.0 - 1.0

risk_agent:
  temperature: 0.3  # 建议保持低温度

payment_agent:
  temperature: 0.2  # 建议保持极低温度
```

**温度效果**:
- `0.0 - 0.3`: 确定性，重复性高
- `0.4 - 0.7`: 平衡，适度创新
- `0.8 - 1.0`: 创造性，变化多

## 📈 性能优化

### 减少API调用

如果OpenAI API成本是问题：

1. **使用备选逻辑**:
```python
# agent_system.py会自动fallback
# Trading Agent失败 → 使用传统策略
# Risk Agent失败 → 使用简单评分
# Payment Agent失败 → 直接执行
```

2. **调整调用频率**:
```yaml
auto_trading:
  interval_minutes: 60  # 增加间隔减少调用
```

3. **使用更便宜的模型**:
```yaml
agent_system:
  model: "gpt-3.5-turbo"  # 成本降低90%
```

### 提高决策质量

1. **提供更多市场数据**:
```python
market_data = {
    "prices": [...],  # 更多历史价格
    "volume": [...],  # 交易量数据
    "orderbook": {...},  # 订单簿深度
    "news_sentiment": 0.65  # 新闻情绪
}
```

2. **调整风险阈值**:
```yaml
risk_agent:
  max_risk_score: 0.5  # 更严格
```

3. **增加信号数量**:
```yaml
trading_agent:
  max_signals: 5  # 更多选择
```

## 🔍 监控和调试

### 查看Agent对话

```python
# 在test_multi_agent.py中启用详细日志
import logging
logging.basicConfig(level=logging.DEBUG)
```

### 查看API调用

检查OpenAI后台: https://platform.openai.com/usage

### 查看决策理由

每个Agent都会返回 `reason` 或 `recommendation`:

```json
{
  "selected_signal": {...},
  "risk_recommendation": "选择Signal 0因为..."
}
```

## 🚨 故障排除

### 问题1: OpenAI API调用失败

**症状**: 
```
⚠️  AI生成信号失败，使用备选方案
```

**解决**:
1. 检查API Key: `echo $OPENAI_API_KEY`
2. 检查余额: OpenAI后台
3. 检查网络: `curl https://api.openai.com`

**临时方案**: 系统会自动使用备选逻辑

### 问题2: Agent总是拒绝交易

**症状**:
```
⚠️  Risk Agent拒绝所有信号（风险过高）
```

**解决**:
降低风险阈值:
```yaml
risk_agent:
  max_risk_score: 0.8  # 从0.7增加到0.8
```

### 问题3: 执行成本过高

**症状**:
```
USDC收益: -$2.50  # 负收益
```

**解决**:
1. 增加交易量（减少相对成本）
2. 检查Stellar网络费用
3. 优化path payment路径

## 📚 下一步

### 1. 添加更多策略

在 `agents/trading.py` 中添加新策略工具。

### 2. 优化Agent Prompt

修改 `agents/agent_system.py` 中的 `system_prompt`。

### 3. 集成实时市场数据

使用 `stellar/market_data.py` 获取实时价格。

### 4. 添加回测功能

创建 `backtest.py` 测试历史表现。

### 5. 创建专业Dashboard

增强 `app/dashboard.py` 显示Agent对话。

## 🎉 总结

你现在拥有一个**真正的Multi-Agent AI交易系统**:

✅ **Trading Agent** 像James Simons一样生成信号  
✅ **Risk Agent** 专业评估风险并选择最优  
✅ **Payment Agent** 精确执行并结算为USDC  
✅ **完整流程** 从分析到执行的自动化  
✅ **风险控制** 多维度评估，自动拒绝高风险  
✅ **OpenAI驱动** 真正的AI决策（可选）  

这是一个**生产级**的AI交易系统！🚀
