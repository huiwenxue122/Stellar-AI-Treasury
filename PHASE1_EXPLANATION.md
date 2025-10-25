# 📚 Phase 1 详细解释

## 🎯 目标：给 Trading Agent 添加基础的技术分析能力

---

## 1️⃣ Technical Indicators Module

### 这是什么？
技术指标 = 用数学公式分析历史价格，判断"该买还是该卖"

### 具体实现 4 个指标：

#### **A. SMA (Simple Moving Average) - 简单移动平均线**

**作用**: 平滑价格波动，看趋势方向

```python
# 例子：BTC 过去 50 天的平均价格
prices = [45000, 46000, 45500, 47000, ...]  # 50 天数据
SMA_50 = sum(prices) / 50 = 46000

# 如果当前价格 > SMA_50 → 上涨趋势 ✅
# 如果当前价格 < SMA_50 → 下跌趋势 ❌
```

**交易信号**:
- **Golden Cross**: SMA(50) 向上穿过 SMA(200) → **强烈买入信号** 🟢
- **Death Cross**: SMA(50) 向下穿过 SMA(200) → **强烈卖出信号** 🔴

**实现代码**:
```python
def calculate_sma(prices: list, period: int) -> float:
    """
    计算简单移动平均
    
    Args:
        prices: [45000, 46000, 45500, ...] 历史价格
        period: 50 或 200 天
    
    Returns:
        平均价格
    """
    if len(prices) < period:
        return None
    
    return sum(prices[-period:]) / period


def detect_golden_cross(prices: list) -> bool:
    """
    检测黄金交叉
    
    Golden Cross = SMA(50) > SMA(200) 且之前 < SMA(200)
    """
    sma_50 = calculate_sma(prices, 50)
    sma_200 = calculate_sma(prices, 200)
    
    # 也计算前一天的
    sma_50_prev = calculate_sma(prices[:-1], 50)
    sma_200_prev = calculate_sma(prices[:-1], 200)
    
    # 今天穿过了
    if sma_50 > sma_200 and sma_50_prev <= sma_200_prev:
        return True
    
    return False
```

---

#### **B. RSI (Relative Strength Index) - 相对强弱指数**

**作用**: 判断资产是否"超买"或"超卖"

```python
# RSI 范围: 0 - 100

RSI > 70  → 超买 (Overbought) → 可能下跌，别买 ⚠️
RSI < 30  → 超卖 (Oversold)   → 可能反弹，可以买 ✅
30-70     → 正常范围
```

**例子**:
```
BTC 价格连续上涨了 10 天:
$40,000 → $45,000 → $50,000 → $55,000

RSI 计算结果 = 85 (超买!)
→ 说明：涨太快了，可能要回调
→ 策略：暂时不买，等回调
```

**实现代码**:
```python
def calculate_rsi(prices: list, period: int = 14) -> float:
    """
    计算 RSI
    
    公式:
    1. 计算每天的涨跌
    2. 平均涨幅 vs 平均跌幅
    3. RSI = 100 - (100 / (1 + RS))
       RS = 平均涨幅 / 平均跌幅
    
    Args:
        prices: [45000, 46000, 45500, ...] 至少 15 天
        period: 通常用 14 天
    
    Returns:
        0-100 的值
    """
    if len(prices) < period + 1:
        return None
    
    # 计算每日价格变化
    deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
    
    # 分离涨和跌
    gains = [d if d > 0 else 0 for d in deltas]
    losses = [-d if d < 0 else 0 for d in deltas]
    
    # 计算平均
    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period
    
    # 避免除以 0
    if avg_loss == 0:
        return 100
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    return rsi


def is_overbought(prices: list) -> bool:
    """RSI > 70 = 超买"""
    rsi = calculate_rsi(prices)
    return rsi > 70 if rsi else False


def is_oversold(prices: list) -> bool:
    """RSI < 30 = 超卖"""
    rsi = calculate_rsi(prices)
    return rsi < 30 if rsi else False
```

---

#### **C. MACD (Moving Average Convergence Divergence)**

**作用**: 判断趋势强度和转折点

```python
# MACD 有 3 条线:
1. MACD Line   = EMA(12) - EMA(26)
2. Signal Line = EMA(MACD, 9)
3. Histogram   = MACD - Signal

# 交易信号:
MACD Line > Signal Line  → 买入信号 ✅
MACD Line < Signal Line  → 卖出信号 ❌
Histogram 增大          → 趋势加强
```

**例子**:
```
BTC 价格:
Day 1-10: $45,000 (横盘)
Day 11:   $46,000 (开始上涨)
Day 12:   $47,500
Day 13:   $49,000

MACD:
Day 1-10: MACD ≈ 0 (没趋势)
Day 11:   MACD 转正 (开始上涨趋势)
Day 12:   MACD > Signal (买入信号!) ✅
Day 13:   Histogram 增大 (趋势强劲)
```

**实现代码**:
```python
def calculate_ema(prices: list, period: int) -> float:
    """
    计算指数移动平均 (EMA)
    
    EMA 比 SMA 更重视近期价格
    """
    if len(prices) < period:
        return None
    
    multiplier = 2 / (period + 1)
    
    # 初始 EMA = SMA
    ema = sum(prices[:period]) / period
    
    # 逐日更新
    for price in prices[period:]:
        ema = (price - ema) * multiplier + ema
    
    return ema


def calculate_macd(prices: list):
    """
    计算 MACD 指标
    
    Returns:
        {
            'macd': MACD 值,
            'signal': Signal Line,
            'histogram': MACD - Signal,
            'trend': 'bullish' | 'bearish' | 'neutral'
        }
    """
    if len(prices) < 26:
        return None
    
    # 计算 EMA
    ema_12 = calculate_ema(prices, 12)
    ema_26 = calculate_ema(prices, 26)
    
    # MACD Line
    macd = ema_12 - ema_26
    
    # Signal Line (9天 EMA of MACD)
    # 简化: 这里需要历史 MACD 值，实际实现会用队列
    signal = macd * 0.9  # 简化示例
    
    # Histogram
    histogram = macd - signal
    
    # 判断趋势
    if macd > signal and histogram > 0:
        trend = 'bullish'   # 上涨
    elif macd < signal and histogram < 0:
        trend = 'bearish'  # 下跌
    else:
        trend = 'neutral'
    
    return {
        'macd': macd,
        'signal': signal,
        'histogram': histogram,
        'trend': trend
    }
```

---

#### **D. Volume Analysis - 成交量分析**

**作用**: 验证价格趋势的可靠性

```python
# 原理:
价格上涨 + 成交量大 → 真上涨 ✅ (Strong)
价格上涨 + 成交量小 → 假上涨 ⚠️ (Weak)
价格下跌 + 成交量大 → 真下跌 ❌ (Strong)
价格下跌 + 成交量小 → 可能反弹 (Weak)
```

**例子**:
```
BTC 价格:
Day 1: $45,000, Volume: 1M (正常)
Day 2: $47,000, Volume: 5M (暴涨!) ✅
→ 成交量确认上涨，可以买

BTC 价格:
Day 1: $45,000, Volume: 1M (正常)
Day 2: $47,000, Volume: 0.5M (量缩) ⚠️
→ 上涨不可靠，别买
```

**实现代码**:
```python
def analyze_volume(prices: list, volumes: list, window: int = 20):
    """
    分析成交量
    
    Args:
        prices: 价格历史
        volumes: 成交量历史
        window: 对比窗口
    
    Returns:
        {
            'current_volume': 当前成交量,
            'avg_volume': 平均成交量,
            'volume_ratio': 比率,
            'signal': 'strong' | 'weak' | 'normal'
        }
    """
    if len(volumes) < window:
        return None
    
    current_volume = volumes[-1]
    avg_volume = sum(volumes[-window:]) / window
    
    volume_ratio = current_volume / avg_volume
    
    # 判断强弱
    if volume_ratio > 1.5:
        signal = 'strong'   # 成交量大 1.5 倍
    elif volume_ratio < 0.5:
        signal = 'weak'     # 成交量小于一半
    else:
        signal = 'normal'
    
    return {
        'current_volume': current_volume,
        'avg_volume': avg_volume,
        'volume_ratio': volume_ratio,
        'signal': signal
    }
```

---

## 2️⃣ Rule-Based Strategy Module

### 这是什么？
把上面 4 个指标组合起来，形成一个**清晰的买卖规则**

### 策略逻辑：

```python
def rule_based_strategy(asset: str, market_data: dict) -> dict:
    """
    基于规则的交易策略
    
    买入条件 (ALL must be true):
    ✅ SMA(50) > SMA(200)        # 长期上涨趋势
    ✅ RSI < 70                  # 未超买
    ✅ MACD bullish              # MACD 确认上涨
    ✅ Volume strong or normal   # 成交量支持
    
    卖出条件 (ANY can trigger):
    ❌ SMA(50) < SMA(200)        # 趋势转跌
    ❌ RSI > 80                  # 严重超买
    ❌ MACD bearish              # MACD 转跌
    
    否则: HOLD
    """
    
    prices = market_data['prices']  # 历史价格
    volumes = market_data['volumes']  # 历史成交量
    
    # 1. 计算指标
    sma_50 = calculate_sma(prices, 50)
    sma_200 = calculate_sma(prices, 200)
    rsi = calculate_rsi(prices)
    macd = calculate_macd(prices)
    volume = analyze_volume(prices, volumes)
    
    # 2. 判断趋势
    trend_bullish = sma_50 > sma_200
    trend_bearish = sma_50 < sma_200
    
    # 3. 买入逻辑
    if (trend_bullish 
        and rsi < 70 
        and macd['trend'] == 'bullish'
        and volume['signal'] in ['strong', 'normal']):
        
        return {
            'signal': 'BUY',
            'confidence': 0.8,
            'reason': f'Golden trend + RSI={rsi:.1f} + MACD bullish',
            'indicators': {
                'sma_50': sma_50,
                'sma_200': sma_200,
                'rsi': rsi,
                'macd': macd['macd'],
                'volume_ratio': volume['volume_ratio']
            }
        }
    
    # 4. 卖出逻辑
    elif (trend_bearish 
          or rsi > 80 
          or macd['trend'] == 'bearish'):
        
        return {
            'signal': 'SELL',
            'confidence': 0.7,
            'reason': f'Bearish trend or RSI={rsi:.1f}',
            'indicators': {...}
        }
    
    # 5. 持有
    else:
        return {
            'signal': 'HOLD',
            'confidence': 0.5,
            'reason': 'No clear signal',
            'indicators': {...}
        }
```

### 实际例子：

#### **场景 1: 强烈买入信号**
```
BTC 市场数据:
- 当前价格: $48,000
- SMA(50): $47,000
- SMA(200): $45,000  ✅ Golden trend!
- RSI: 55            ✅ 未超买
- MACD: bullish      ✅ 上涨趋势
- Volume: 1.8x avg   ✅ 成交量强劲

→ 策略输出:
{
  'signal': 'BUY',
  'confidence': 0.85,
  'reason': 'Golden trend + RSI=55 + MACD bullish + Volume strong'
}
```

#### **场景 2: 卖出信号**
```
ETH 市场数据:
- 当前价格: $3,200
- SMA(50): $3,150
- SMA(200): $3,180  ❌ Death Cross (50 < 200)
- RSI: 75           ⚠️ 接近超买
- MACD: turning bearish

→ 策略输出:
{
  'signal': 'SELL',
  'confidence': 0.75,
  'reason': 'Death Cross detected + RSI high'
}
```

#### **场景 3: 持有**
```
SOL 市场数据:
- SMA(50): $105
- SMA(200): $103    (略微上涨，不明显)
- RSI: 50           (中性)
- MACD: neutral
- Volume: 0.9x avg  (正常)

→ 策略输出:
{
  'signal': 'HOLD',
  'confidence': 0.5,
  'reason': 'No clear signal, market consolidating'
}
```

---

## 3️⃣ Risk Agent Position Sizing Enhancement

### 这是什么？
让 Risk Agent **智能计算每个资产应该买多少**，而不是固定比例

### 当前问题：
```python
# 现在的方式 (固定)
BTC: 30% of portfolio
ETH: 25% of portfolio
SOL: 20% of portfolio

# 问题:
- BTC 波动很大时，30% 太危险 ⚠️
- ETH 和 BTC 高度相关，50% 都在类似资产上 ⚠️
- 负面新闻时，还是按 30% 买 ⚠️
```

### 改进后的动态计算：

```python
def calculate_position_size(asset, signal, portfolio):
    """
    动态计算仓位大小
    
    考虑因素:
    1. 用户层级限制 (Beginner: max 30%, Advanced: max 50%)
    2. 资产波动率 (波动大 → 仓位小)
    3. 当前组合风险 (VaR 余量)
    4. 资产相关性 (已有 BTC，减少 ETH 仓位)
    5. 新闻情绪 (负面 → 减仓)
    
    Returns:
        实际仓位百分比
    """
    
    # 1. 基础限制 (用户层级)
    base_limit = 0.30  # Beginner: 30%
    
    # 2. 波动率调整
    volatility = calculate_volatility(asset)
    if volatility > 0.5:  # 50% 日波动
        vol_factor = 0.5   # 减半仓位
    else:
        vol_factor = 1.0
    
    # 3. VaR 余量
    current_var = calculate_portfolio_var(portfolio)
    max_var = 0.02  # Beginner: 2%
    var_headroom = (max_var - current_var) / max_var
    # 如果 VaR 已经用了 80%，只能再用 20%
    
    # 4. 相关性惩罚
    if asset == 'ETH' and 'BTC' in portfolio:
        correlation_penalty = 0.3  # -30%
    else:
        correlation_penalty = 0
    
    # 5. 情绪调整
    sentiment = signal.get('sentiment', 'neutral')
    if sentiment == 'negative':
        sentiment_factor = 0.6  # -40%
    else:
        sentiment_factor = 1.0
    
    # 最终仓位
    position = (
        base_limit 
        * vol_factor 
        * var_headroom 
        * (1 - correlation_penalty)
        * sentiment_factor
    )
    
    return max(0.05, min(position, base_limit))
```

### 实际例子：

#### **例子 1: 正常情况**
```
Asset: BTC
User tier: Beginner (max 30%)
Volatility: 0.3 (30%)       → vol_factor = 1.0
Current VaR: 0.01 (1%)      → var_headroom = 0.5 (50% 余量)
Correlation: None           → penalty = 0
Sentiment: Positive         → factor = 1.0

Position = 0.30 × 1.0 × 0.5 × 1.0 × 1.0 = 15% ✅

→ 结果: 买 15% 的 BTC
```

#### **例子 2: 高波动 + 负面新闻**
```
Asset: FET (小币种)
User tier: Advanced (max 50%)
Volatility: 0.8 (80%!)      → vol_factor = 0.5 (减半!)
Current VaR: 0.08 (8%)      → var_headroom = 0.2 (只剩 20%)
Correlation: None
Sentiment: Negative         → factor = 0.6 (负面新闻!)

Position = 0.50 × 0.5 × 0.2 × 1.0 × 0.6 = 3% ✅

→ 结果: 只买 3% 的 FET (从 50% 降到 3%)
→ 原因: 波动太大 + 负面新闻，风险高
```

#### **例子 3: 已有相关资产**
```
Asset: ETH
Current Portfolio: 已有 30% BTC
User tier: Intermediate (max 40%)
Volatility: 0.35            → vol_factor = 1.0
Current VaR: 0.03 (3%)      → var_headroom = 0.4
Correlation: BTC-ETH 高相关 → penalty = 0.3 (减 30%)
Sentiment: Neutral          → factor = 1.0

Position = 0.40 × 1.0 × 0.4 × 0.7 × 1.0 = 11.2% ✅

→ 结果: 只买 11.2% 的 ETH
→ 原因: 已有 30% BTC，避免过度集中在相关资产
```

---

## 📊 Phase 1 完成后的效果

### 交易决策流程：

```
1. 获取 BTC 市场数据
   ↓
2. 计算技术指标
   - SMA(50) = $47,000
   - SMA(200) = $45,000  ✅ 上涨趋势
   - RSI = 55            ✅ 未超买
   - MACD = bullish      ✅
   ↓
3. Rule-based Strategy 判断
   → Signal: BUY, Confidence: 0.8
   ↓
4. Risk Agent 计算仓位
   - Base limit: 30% (Beginner)
   - Volatility: 0.4 → factor = 0.7
   - VaR headroom: 0.6
   - No correlation penalty
   - Sentiment: positive → 1.0
   → Position: 30% × 0.7 × 0.6 × 1.0 = 12.6%
   ↓
5. 最终决策
   ✅ BUY 12.6% BTC at $48,000
```

### Trading Agent 提示词更新：

```python
# 现在 Trading Agent 会收到这些工具:

tools = [
    {
        "name": "rule_based_strategy",
        "description": "Use technical indicators (SMA, RSI, MACD) to generate trading signal",
        "parameters": {
            "asset": "BTC",
            "prices": [45000, 46000, ...],
            "volumes": [1.2M, 1.5M, ...]
        }
    },
    # ... 原有的 10 个 ML/RL 策略
]

# Trading Agent 可以选择:
# - 只用 rule_based_strategy (快速、透明)
# - 或结合 LGBM, LSTM 等 (更复杂)
# - 或让 Risk Agent 最终决定仓位
```

---

## 🎯 总结 Phase 1

### 实现内容:
1. ✅ **4 个技术指标**: SMA, RSI, MACD, Volume
2. ✅ **1 个规则策略**: 组合指标生成 BUY/SELL/HOLD
3. ✅ **动态仓位计算**: 基于波动、VaR、相关性、情绪

### 时间估计:
- Technical indicators: 30-45 分钟
- Rule-based strategy: 30-45 分钟
- Position sizing: 30 分钟
- **总计: 1.5-2 小时**

### 价值:
- ✅ **可解释性**: 评委能看懂为什么买/卖
- ✅ **风险控制**: 动态仓位避免过度风险
- ✅ **专业性**: 展示量化交易知识
- ✅ **基准**: 为 ML 策略提供对比基准

---

## ❓ 你的问题

现在清楚了吗？简单说就是：

1. **造工具** (4 个技术指标)
2. **定规则** (什么时候买/卖)
3. **控风险** (该买多少)

要我开始实现吗？🚀

