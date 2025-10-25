# 🚀 情境多臂老虎机策略选择系统

## 📋 **系统概述**

基于情境的多臂老虎机策略选择系统，集成到现有的MultiAgentOrchestratorWithTools中，通过Thompson采样或LinUCB算法智能选择最优交易策略。

## 🏗️ **系统架构**

### **核心组件**
1. **策略基础协议** (`strategies/base.py`) - 统一策略接口
2. **通用中间件** (`strategies/middleware.py`) - 波动率目标、止盈止损、成本滑点
3. **策略库** (`strategies/library.py`) - 注册和管理10个策略
4. **情境特征构建** (`selector/context_features.py`) - 构造regime特征
5. **Thompson采样选择器** (`selector/thompson_selector.py`) - 默认选择器
6. **严格评估框架** (`agents/strategy_evaluator.py`) - Walk-forward + Bootstrap
7. **选择器训练器** (`agents/strategy_optimizer.py`) - 离线训练和在线更新
8. **LLM解释器** (`reporting/explain_llm.py`) - 生成中英双语交易解释

### **集成方式**
- 不改变MultiAgentOrchestratorWithTools对外接口
- 新增`bandit_select_strategy` function tool
- GPT先调用选择器获取推荐策略，再测试候选策略
- 所有代码避免look-ahead，索引对齐

## 🚀 **快速开始**

### **1. 训练选择器**
```bash
# 训练Thompson采样选择器
python agents/strategy_optimizer.py \
  --train-start 2022-01-01 \
  --train-end 2024-06-30 \
  --selector thompson \
  --topk 1 \
  --save artifacts/selector_state.pkl
```

### **2. 严格评估**
```bash
# 评估选择器性能
python agents/strategy_evaluator.py \
  --asset BTC \
  --start 2022-01-01 \
  --end 2024-12-31 \
  --wf-train 180 \
  --wf-test 30 \
  --use-selector true \
  --topk 1 \
  --fee-bps 5 \
  --slip-k 0.1 \
  --target-vol 0.15 \
  --tp 0.02 \
  --sl 0.01
```

### **3. 正常运行**
```bash
# 多智能体系统（GPT会先调用bandit_select_strategy）
python run_multi_agent.py
```

## 📊 **系统工作流程**

### **GPT工作流程**
1. **策略选择**: 调用`bandit_select_strategy(asset)`获取推荐策略
2. **策略验证**: 仅对推荐策略调用现有策略工具
3. **组合投资**: 基于选择器推荐和风险预算构建投资组合

### **选择器工作流程**
1. **特征提取**: 从价格序列构建50+技术指标特征
2. **情境分析**: 识别市场regime（趋势、波动、情绪等）
3. **策略推荐**: 基于Thompson采样返回top-k策略
4. **在线学习**: 根据交易结果更新后验分布

## 🔧 **配置参数**

### **选择器配置**
```python
ThompsonSelectorConfig(
    n_arms=10,           # 策略数量
    n_features=50,       # 特征维度
    alpha=1.0,           # 噪声参数
    beta=1.0,            # 正则化参数
    warmup_samples=100   # 预热样本数
)
```

### **评估配置**
```python
EvaluationConfig(
    wf_train_days=180,   # 训练期天数
    wf_test_days=30,     # 测试期天数
    fee_bps=5.0,         # 手续费(基点)
    slip_k=0.1,          # 滑点系数
    target_vol=0.15,     # 目标波动率
    bootstrap_samples=1000  # Bootstrap样本数
)
```

## 📈 **评估指标**

### **核心指标**
- **CAGR**: 年化复合增长率
- **Sharpe Ratio**: 夏普比率
- **Sortino Ratio**: 索提诺比率
- **Calmar Ratio**: 卡玛比率
- **Max Drawdown**: 最大回撤
- **Profit Factor**: 盈亏比
- **Hit Rate**: 胜率

### **高级指标**
- **CVaR(0.95)**: 条件风险价值
- **Recovery Time**: 恢复时间
- **Turnover**: 换手率
- **Bootstrap置信区间**: 统计显著性

## 🎯 **基准对比**

### **基准策略**
1. **Buy & Hold**: 买入持有
2. **Equal Weight**: 等权重组合
3. **Best Single Strategy**: 最佳单策略

### **评估方法**
- **Walk-forward**: 滚动训练-测试
- **成本考虑**: 手续费和滑点
- **Bootstrap**: 置信区间
- **多资产**: 跨资产验证

## 📊 **预期效果**

### **性能提升**
- **Sharpe Ratio**: 从1.0提升到1.5+
- **Sortino Ratio**: 从1.2提升到1.8+
- **Calmar Ratio**: 从0.8提升到1.2+
- **Max Drawdown**: 控制在10%以内

### **选择器优势**
- **情境感知**: 根据市场环境选择策略
- **在线学习**: 持续优化策略选择
- **风险控制**: 平衡探索和利用
- **可解释性**: 提供决策推理

## 🛠️ **技术实现**

### **文件结构**
```
strategies/
├── base.py              # 策略基础协议
├── middleware.py         # 通用中间件
└── library.py           # 策略库

selector/
├── context_features.py   # 情境特征构建
└── thompson_selector.py # Thompson采样选择器

agents/
├── strategy_evaluator.py # 严格评估框架
└── strategy_optimizer.py # 选择器训练器

reporting/
└── explain_llm.py       # LLM解释器
```

### **关键特性**
- **无Look-ahead**: 严格避免未来信息泄露
- **索引对齐**: 确保时间序列一致性
- **状态持久化**: 保存/加载选择器状态
- **可配置性**: 支持参数调优

## 🔍 **验收标准**

### **功能验收**
1. **GPT工作流程**: 先调用`bandit_select_strategy`，再调用策略工具
2. **选择器性能**: 在Sharpe/Sortino/Calmar/MDD上优于基准
3. **状态管理**: `artifacts/selector_state.pkl`能保存/加载
4. **报告生成**: 清晰的markdown报告和图表

### **性能验收**
1. **选择器方案**: 优于Buy&Hold、等权重、最佳单策略
2. **统计显著性**: Bootstrap置信区间支持
3. **成本考虑**: 包含手续费和滑点
4. **多资产验证**: 跨资产稳定性

## 🚀 **运行指令**

### **完整流程**
```bash
# 1. 训练选择器
python agents/strategy_optimizer.py \
  --train-start 2022-01-01 \
  --train-end 2024-06-30 \
  --selector thompson \
  --topk 1

# 2. 严格评估
python agents/strategy_evaluator.py \
  --asset BTC \
  --start 2022-01-01 \
  --end 2024-12-31 \
  --wf-train 180 \
  --wf-test 30 \
  --use-selector true \
  --topk 1

# 3. 正常运行
python run_multi_agent.py
```

### **预期输出**
- **选择器状态**: `artifacts/selector_state.pkl`
- **评估报告**: `reports/strategy_evaluation_*.md`
- **交易解释**: `reports/trade_explanation_*.json`
- **汇总报告**: `reports/trading_summary_*.md`

## 🎉 **系统优势**

### **技术优势**
1. **情境感知**: 基于市场regime智能选择策略
2. **在线学习**: 持续优化策略选择
3. **风险控制**: 平衡探索和利用
4. **可解释性**: 提供决策推理

### **业务优势**
1. **性能提升**: 显著优于基准策略
2. **风险控制**: 有效控制回撤
3. **适应性**: 适应不同市场环境
4. **可扩展**: 易于添加新策略

**现在开始使用情境多臂老虎机策略选择系统，让AI交易更智能！** 🚀
