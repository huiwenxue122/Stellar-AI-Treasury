# 📊 Trading Agent 策略详解

## 🎯 策略总览

Trading Agent实现了**4大类策略**，共6个具体策略：

1. **Momentum Strategy (S1)** - 动量策略
2. **Mean Reversion Strategy (S2)** - 均值回归策略
3. **Path Improvement Strategy (S3)** - 路径优化策略
4. **Stablecoin Strategy** - 稳定币策略
5. **Multi-Asset Rebalancing** - 多资产再平衡
6. **Multi-Asset Momentum** - 多资产动量

---

## 📈 策略1: Momentum Strategy (动量策略)

### 核心思想
**"趋势是你的朋友"** - 当价格呈现明确的上涨趋势时买入

### 实现逻辑

```python
def s1_momentum(self, prices, vol_z, impact_bps) -> bool:
    # 1. 计算快速和慢速EMA
    p_fast = self.ema(prices, 5)   # 5期EMA
    p_slow = self.ema(prices, 20)  # 20期EMA
    
    # 2. 检查三个条件
    cross = p_fast > p_slow         # EMA金叉
    high_vol = vol_z > 1.0          # 波动率Z分数 > 1
    low_impact = impact_bps < 25    # 价格冲击 < 25基点
    
    return cross and high_vol and low_impact
```

### 详细解释

#### 指标1: EMA金叉
```
价格走势:
    ┌─────────────────────────────────────────┐
    │                                         │
    │         📈 快速EMA (5期)                │
    │        /                                │
    │       /    🔼 金叉点 (买入信号)         │
    │      /    /                             │
    │     /    /                              │
    │    /    /  📊 慢速EMA (20期)           │
    │   /    /  /                             │
    │  /    /  /                              │
    │ /    /  /                               │
    └─────────────────────────────────────────┘
```

- **快速EMA (5期)**: 对近期价格变化敏感
- **慢速EMA (20期)**: 反映长期趋势
- **金叉**: 当快速EMA上穿慢速EMA → 上涨趋势确认

#### 指标2: 波动率Z分数 (vol_z > 1.0)
```
波动率分布:
    正常波动 (-1 < z < 1)    高波动 (z > 1)
    ┌──────────────────┐     ┌──────────┐
    │        68%       │     │   16%    │
    │                  │     │  ⚡      │
    └──────────────────┘     └──────────┘
       平静市场                活跃市场
       ❌ 不交易              ✅ 可以交易
```

- **Z-score = (当前波动率 - 平均波动率) / 标准差**
- **Z > 1.0**: 市场活跃，有交易机会
- **Z < 1.0**: 市场平静，等待机会

#### 指标3: 价格冲击 (impact_bps < 25)
```
流动性检查:
    
    高流动性 (impact < 25 bps)     低流动性 (impact > 25 bps)
    ┌─────────────────────┐         ┌─────────────────────┐
    │ 买入100个XLM        │         │ 买入100个XLM        │
    │ 价格变化: 0.2%      │         │ 价格变化: 3.5%      │
    │ ✅ 可以大量交易     │         │ ❌ 滑点太高         │
    └─────────────────────┘         └─────────────────────┘
```

- **Price Impact**: 交易对价格的影响（滑点）
- **< 25 bps (0.25%)**: 流动性好，可以交易
- **> 25 bps**: 滑点太大，不交易

### 配置参数
```yaml
strategy:
  s1:
    ema_fast: 5           # 快速EMA周期
    ema_slow: 20          # 慢速EMA周期  
    vol_z_min: 1.0        # 最小波动率Z分数
    tp_pct: 0.006         # 止盈 0.6%
    sl_pct: 0.0035        # 止损 0.35%
```

### 适用场景
- ✅ 趋势明确的上涨市场
- ✅ 波动性增加时
- ✅ 流动性充足的资产
- ❌ 震荡市场（容易假突破）

---

## 🔄 策略2: Mean Reversion Strategy (均值回归策略)

### 核心思想
**"价格偏离太远会回归"** - 当价格异常偏离时做反向交易

### 实现逻辑

```python
def s2_revert(self, impact_gap_bps, depth_ok) -> bool:
    # 1. 检查买卖价差异常
    gap_threshold = 20  # 20基点
    
    # 2. 检查市场深度
    return (depth_ok and 
            impact_gap_bps > gap_threshold)
```

### 详细解释

#### 原理图
```
正常市场:
    卖出价: $100.10  ┐
                     ├─ 价差: 10 bps (0.1%)
    买入价: $100.00  ┘
    ✅ 正常，不交易

异常市场 (套利机会):
    卖出价: $100.30  ┐
                     ├─ 价差: 30 bps (0.3%)  ⚠️ 异常!
    买入价: $100.00  ┘
    🎯 做市机会: 在中间价格买入/卖出
```

#### Impact Gap (价格冲击差)
```
买卖双方的价格冲击差距:

    正常情况:
    买入冲击: 15 bps  ┐
                      ├─ gap = 5 bps  ✅ 正常
    卖出冲击: 10 bps  ┘

    异常情况 (均值回归机会):
    买入冲击: 30 bps  ┐
                      ├─ gap = 25 bps  🎯 回归机会!
    卖出冲击: 5 bps   ┘
```

#### Market Depth (市场深度检查)
```
订单簿深度:
    
    足够深度 (depth_ok = true):
    ┌──────────────────────────┐
    │ 卖3: 1000 XLM @ $0.122  │
    │ 卖2: 2000 XLM @ $0.121  │
    │ 卖1: 5000 XLM @ $0.120  │  ← 深度好
    ├──────────────────────────┤
    │ 买1: 5000 XLM @ $0.119  │
    │ 买2: 2000 XLM @ $0.118  │
    │ 买3: 1000 XLM @ $0.117  │
    └──────────────────────────┘
    ✅ 可以大单交易
    
    深度不足 (depth_ok = false):
    ┌──────────────────────────┐
    │ 卖1: 100 XLM @ $0.120   │  ← 深度差
    ├──────────────────────────┤
    │ 买1: 100 XLM @ $0.119   │
    └──────────────────────────┘
    ❌ 不适合交易
```

### 配置参数
```yaml
strategy:
  s2:
    impact_gap_bps_in: 20    # 进场阈值: 20基点
    exit_gap_bps: 10         # 出场阈值: 10基点
    timeout_sec: 60          # 超时时间: 60秒
```

### 交易流程
```
1. 检测异常价差 (> 20 bps)
   ↓
2. 确认市场深度充足
   ↓
3. 在中间价附近下单
   ↓
4. 等待价格回归
   ↓
5. 价差收窄到 < 10 bps时平仓
```

### 适用场景
- ✅ 短期价格偏离
- ✅ 高频交易
- ✅ 流动性好的市场
- ❌ 趋势市场（可能持续偏离）

---

## 🛤️ 策略3: Path Improvement Strategy (路径优化策略)

### 核心思想
**"找到更好的交易路径"** - 通过Stellar的path payment找到更优汇率

### 实现逻辑

```python
def s3_path_improve(self, better_bps) -> bool:
    # 检查路径是否比直接交易好至少15个基点
    return better_bps >= 15
```

### 详细解释

#### 直接交易 vs 路径交易
```
场景: 想用USDC买BTC

方案A - 直接交易:
    USDC ──────────────────► BTC
         汇率: 1 BTC = 43,100 USDC
         成本: 43,100 USDC
         
方案B - 多跳路径:
    USDC ──► XLM ──► BTC
         ↓        ↓
      1 XLM     180 XLM
      = 0.12    = 1 BTC
      USDC
      
    成本: 180 × 0.12 = 21.6 USDC
          实际汇率: 1 BTC = 21.6 USDC
          
    节省: 43,100 - 21,600 = 21,500 USDC (49.9%!)
    ✅ better_bps = 4990 bps (远超15 bps阈值)
```

#### Stellar Path Payment原理
```
Stellar DEX图:
    
    ┌──────┐         ┌──────┐         ┌──────┐
    │ USDC │────0.5──►│ XLM  │────2.0──►│ BTC  │
    └──────┘         └──────┘         └──────┘
        │                                  ▲
        │                                  │
        └────────────1.2───────────────────┘
        
    直接路径: USDC → BTC (汇率: 1.2)
    间接路径: USDC → XLM → BTC (汇率: 0.5 × 2.0 = 1.0)
    
    改进: (1.2 - 1.0) / 1.2 = 16.7%
    better_bps = 1670 bps ✅ > 15 bps
```

#### 实际应用
```python
# Stellar会自动查找最优路径
path_result = stellar.path_payment(
    source_asset=USDC,
    dest_asset=BTC,
    dest_amount="1.0"  # 想要1个BTC
)

# 可能的路径:
路径1: USDC → BTC (直接)
       cost: 43,100 USDC
       
路径2: USDC → XLM → BTC
       cost: 42,950 USDC
       better_bps = 35 ✅
       
路径3: USDC → ETH → BTC
       cost: 43,080 USDC
       better_bps = 5 ❌ (不够好)
       
选择: 路径2 (最优)
```

### 配置参数
```yaml
strategy:
  s3:
    path_improve_bps_min: 15  # 最小改进: 15基点 (0.15%)
    split_trades: 2           # 拆分交易数量
```

### 适用场景
- ✅ 大额交易（改进更明显）
- ✅ Stellar生态内的跨资产交易
- ✅ 流动性分散的市场
- ❌ 小额交易（gas费可能抵消收益）

---

## 🪙 策略4: Stablecoin Strategy (稳定币策略)

### 核心思想
**"高风险时保守，低风险时进攻"** - 动态调整稳定币配置

### 实现逻辑

```python
def analyze_stablecoin_strategy():
    # 1. 检查波动率
    if asset.volatility > threshold_high (0.3):
        # 波动率过高 → 转换为USDC
        return CONVERT_TO_USDC
        
    elif asset.volatility < threshold_low (0.15):
        # 波动率很低 → 从USDC转出
        if usdc_allocation > target (30%):
            return CONVERT_FROM_USDC
    
    return HOLD
```

### 详细解释

#### 波动率阈值设计
```
波动率水平:
    
    极低风险 (< 15%)          中等风险 (15-30%)         高风险 (> 30%)
    ┌──────────────┐          ┌──────────────┐          ┌──────────────┐
    │ 稳定市场     │          │ 正常波动     │          │ 剧烈波动     │
    │ USDC太多了   │          │ 保持平衡     │          │ 需要避险     │
    │              │          │              │          │              │
    │ 🟢 买入资产  │          │ 🟡 观望      │          │ 🔴 卖出资产  │
    │ (从USDC转出) │          │ (不动)       │          │ (转为USDC)   │
    └──────────────┘          └──────────────┘          └──────────────┘
      ↓                         ↓                         ↓
    增加风险资产              保持配置                  增加稳定币
```

#### 动态配置调整
```
示例场景:

初始状态:
    BTC: 40% ($4,000)
    ETH: 30% ($3,000)
    USDC: 30% ($3,000)
    ✅ 平衡配置

市场暴跌，波动率飙升:
    BTC波动率: 15% → 45% 🔴 超过阈值(30%)
    
    策略触发:
    1. 将BTC转换为USDC
    2. 转换比例: 50% (配置中的conversion_amount_ratio)
    3. 转换量: $2,000
    
    调整后:
    BTC: 20% ($2,000)  ← 减少
    ETH: 30% ($3,000)
    USDC: 50% ($5,000) ← 增加
    ✅ 降低风险敞口

市场稳定，波动率下降:
    BTC波动率: 45% → 12% 🟢 低于阈值(15%)
    USDC配置: 50% > 目标(30%)
    
    策略触发:
    1. 将USDC转回BTC
    2. 选择波动率最低的资产
    3. 转换量: 部分USDC
    
    调整后:
    BTC: 35% ($3,500)  ← 增加
    ETH: 30% ($3,000)
    USDC: 35% ($3,500) ← 减少
    ✅ 恢复增长配置
```

#### 资产选择逻辑
```python
# 转换为USDC时 - 选择波动率最高的资产
def get_asset_to_convert():
    assets_by_volatility = sorted(assets, 
                                   key=lambda x: x.volatility,
                                   reverse=True)
    return assets_by_volatility[0]  # 最高波动率

# 从USDC转出时 - 选择波动率最低的资产  
def find_best_asset_for_conversion():
    score = volatility * 0.7 + (1/price) * 0.3
    return min_score_asset  # 最稳定的资产
```

### 配置参数
```yaml
stablecoin:
  volatility_threshold_high: 0.3   # 高波动阈值: 30%
  volatility_threshold_low: 0.15   # 低波动阈值: 15%
  usdc_allocation_target: 30.0     # 目标USDC配置: 30%
  conversion_amount_ratio: 0.5     # 每次转换比例: 50%
  price_history_window: 20         # 波动率计算窗口: 20期
```

### 风险管理
```
最小USDC配置: 20%  (多资产交易配置)
最大USDC配置: 无限制 (可以100%避险)

保护机制:
    1. 渐进式转换 (每次50%)
    2. 防止频繁交易 (价格窗口)
    3. 双阈值设计 (避免震荡)
```

### 适用场景
- ✅ 市场波动加剧时
- ✅ 长期持仓策略
- ✅ 风险厌恶型投资者
- ❌ 短线交易（可能错过机会）

---

## 🔄 策略5: Multi-Asset Rebalancing (多资产再平衡)

### 核心思想
**"保持目标配置"** - 定期调整投资组合回到理想状态

### 实现逻辑
```python
async def generate_rebalance_signals(account, market_conditions):
    # 1. 计算当前配置
    current_weights = calculate_current_allocation()
    
    # 2. 根据市场条件计算目标配置
    target_weights = calculate_target_allocation(market_conditions)
    
    # 3. 生成再平衡信号
    for asset in assets:
        weight_diff = target - current
        if abs(weight_diff) > threshold (5%):
            generate_signal(BUY or SELL, amount)
```

### 详细解释

#### 再平衡触发条件
```
当前配置 vs 目标配置:

    资产        当前权重    目标权重    偏差      操作
    ─────────────────────────────────────────────
    BTC         35%        25%        +10%     🔴 卖出
    ETH         20%        25%        -5%      🟢 买入
    USDC        25%        30%        -5%      🟢 买入
    GOLD        20%        20%        0%       ⚪ 持有
    
    触发阈值: 5%
    BTC偏差10% > 5% ✅ 触发
    ETH偏差5% = 5% ✅ 触发
    GOLD偏差0% < 5% ❌ 不触发
```

#### 目标配置计算（根据市场条件）
```python
# 低风险市场
if risk_level == 'LOW' and volatility < 0.15:
    stable_target = 20%   # 减少稳定币
    crypto_target = 45%   # 增加加密货币
    rwa_target = 35%      # 增加RWA

# 中风险市场  
elif risk_level == 'MEDIUM':
    stable_target = 30%   # 平衡配置
    crypto_target = 40%
    rwa_target = 30%

# 高风险市场
elif risk_level == 'HIGH' or volatility > 0.4:
    stable_target = 40%   # 增加稳定币
    crypto_target = 30%   # 减少加密货币
    rwa_target = 30%      # 保持RWA
```

### 配置参数
```yaml
multi_asset_trading:
  rebalance_threshold: 0.05         # 5%偏差触发
  rebalance_interval_hours: 24      # 至少24小时一次
  max_single_asset_weight: 0.30     # 单资产最大30%
  min_stable_allocation: 0.20       # 最小稳定币20%
```

### 适用场景
- ✅ 长期投资策略
- ✅ 风险控制
- ✅ 自动化管理
- ❌ 高波动市场（频繁触发）

---

## 📈 策略6: Multi-Asset Momentum (多资产动量)

### 核心思想
**"不同资产类型用不同策略"** - Crypto追求增长，RWA追求稳定

### Crypto动量策略
```python
# 加密货币 - 追求高增长
if recent_return > 5% and volatility < 30%:
    # 上涨趋势 + 可控波动 → 买入
    signal = BUY
    confidence = 0.7
    
elif recent_return < -10%:
    # 下跌超过10% → 止损
    signal = SELL
    confidence = 0.8
```

### RWA稳定策略
```python
# RWA - 追求稳定收益
if recent_return > 2% and volatility < 15%:
    # 稳定增长 → 买入
    signal = BUY
    confidence = 0.85
    expected_return = 4%  # 年化
```

---

## 🎯 策略组合使用

### 完整交易周期
```
1. 风险检查
   └─> 如果高风险 → 暂停交易

2. 稳定币策略
   └─> 调整USDC配置

3. 多资产再平衡
   └─> 每24小时检查一次

4. 传统策略
   ├─> 动量策略 (趋势跟随)
   ├─> 均值回归 (套利)
   └─> 路径优化 (成本节省)

5. 多资产动量
   ├─> Crypto策略
   └─> RWA策略

6. 执行交易
   └─> 所有信号统一执行

7. 利润结算
   └─> 转换为USDC

8. 风险更新
   └─> 更新VaR/Sharpe等指标
```

### 策略优先级
```
优先级1: 风险控制
  - 高风险时停止交易
  - 强制USDC转换

优先级2: 稳定币策略
  - 动态风险调整

优先级3: 再平衡
  - 保持目标配置

优先级4: 主动策略
  - 动量/均值回归/路径优化
```

## 📊 总结对比

| 策略 | 收益潜力 | 风险级别 | 交易频率 | 适用市场 |
|------|---------|---------|---------|---------|
| 动量 | 高 🟢 | 高 🔴 | 中 | 趋势市场 |
| 均值回归 | 中 🟡 | 中 🟡 | 高 | 震荡市场 |
| 路径优化 | 低 🟡 | 低 🟢 | 低 | 任何市场 |
| 稳定币 | 低 🟢 | 低 🟢 | 低 | 波动市场 |
| 再平衡 | 中 🟡 | 低 🟢 | 低 | 长期持有 |
| 多资产动量 | 高 🟢 | 中 🟡 | 中 | 分化市场 |

这就是Trading Agent的完整策略体系！有什么想深入了解的吗？
