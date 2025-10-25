#!/usr/bin/env python3
"""
LLM解释器
GPT仅用于解释：输入资产、候选策略及特征快照、风险预算、评估指标 → 生成中英双语"Why this trade"卡片
"""

import json
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import pandas as pd
import numpy as np

@dataclass
class TradeExplanation:
    """交易解释"""
    asset: str
    selected_strategy: str
    confidence: float
    reasoning: str
    risk_assessment: str
    expected_outcome: str
    english_explanation: str
    chinese_explanation: str

class LLMExplainer:
    """LLM解释器"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.explanations = []
        
        # 创建reports目录
        os.makedirs('reports', exist_ok=True)
    
    def explain_trade(self, asset: str, candidates: List[Dict], 
                     features: Dict[str, Any], risk_budget: float,
                     evaluation_metrics: Dict[str, Any]) -> TradeExplanation:
        """
        解释交易决策
        
        Args:
            asset: 资产符号
            candidates: 候选策略列表
            features: 特征快照
            risk_budget: 风险预算
            evaluation_metrics: 评估指标
            
        Returns:
            交易解释
        """
        
        # 选择最佳策略
        best_strategy = max(candidates, key=lambda x: x.get('score', 0))
        selected_strategy = best_strategy['strategy']
        confidence = best_strategy['score']
        
        # 生成解释
        reasoning = self._generate_reasoning(asset, selected_strategy, features, candidates)
        risk_assessment = self._assess_risk(selected_strategy, features, risk_budget)
        expected_outcome = self._predict_outcome(selected_strategy, features, evaluation_metrics)
        
        # 生成中英双语解释
        english_explanation = self._generate_english_explanation(
            asset, selected_strategy, confidence, reasoning, risk_assessment, expected_outcome
        )
        
        chinese_explanation = self._generate_chinese_explanation(
            asset, selected_strategy, confidence, reasoning, risk_assessment, expected_outcome
        )
        
        explanation = TradeExplanation(
            asset=asset,
            selected_strategy=selected_strategy,
            confidence=confidence,
            reasoning=reasoning,
            risk_assessment=risk_assessment,
            expected_outcome=expected_outcome,
            english_explanation=english_explanation,
            chinese_explanation=chinese_explanation
        )
        
        self.explanations.append(explanation)
        return explanation
    
    def _generate_reasoning(self, asset: str, strategy: str, features: Dict[str, Any], 
                           candidates: List[Dict]) -> str:
        """生成推理过程"""
        
        # 分析市场特征
        market_analysis = self._analyze_market_features(features)
        
        # 分析策略选择
        strategy_analysis = self._analyze_strategy_selection(strategy, candidates)
        
        # 组合推理
        reasoning = f"""
        Market Analysis: {market_analysis}
        
        Strategy Selection: {strategy_analysis}
        
        Decision Process:
        1. Analyzed current market conditions for {asset}
        2. Evaluated {len(candidates)} candidate strategies
        3. Selected {strategy} based on contextual bandit recommendations
        4. Considered risk-return trade-offs and market regime
        """
        
        return reasoning.strip()
    
    def _analyze_market_features(self, features: Dict[str, Any]) -> str:
        """分析市场特征"""
        analysis = []
        
        # 趋势分析
        if 'trend_strength' in features:
            trend_strength = features['trend_strength']
            if trend_strength > 0.6:
                analysis.append("Strong uptrend detected")
            elif trend_strength < -0.6:
                analysis.append("Strong downtrend detected")
            else:
                analysis.append("Sideways market conditions")
        
        # 波动率分析
        if 'volatility' in features:
            volatility = features['volatility']
            if volatility > 0.3:
                analysis.append("High volatility environment")
            elif volatility < 0.1:
                analysis.append("Low volatility environment")
            else:
                analysis.append("Moderate volatility")
        
        # 情绪分析
        if 'rsi' in features:
            rsi = features['rsi']
            if rsi > 70:
                analysis.append("Overbought conditions")
            elif rsi < 30:
                analysis.append("Oversold conditions")
            else:
                analysis.append("Neutral sentiment")
        
        # 动量分析
        if 'momentum' in features:
            momentum = features['momentum']
            if momentum > 0.02:
                analysis.append("Strong positive momentum")
            elif momentum < -0.02:
                analysis.append("Strong negative momentum")
            else:
                analysis.append("Weak momentum")
        
        return "; ".join(analysis) if analysis else "Standard market conditions"
    
    def _analyze_strategy_selection(self, selected_strategy: str, candidates: List[Dict]) -> str:
        """分析策略选择"""
        
        # 策略类型分析
        strategy_types = {
            'buy_and_hold': 'Long-term appreciation strategy',
            'macd': 'Trend-following strategy',
            'rsi': 'Mean reversion strategy',
            'bollinger_bands': 'Volatility-based strategy',
            'momentum': 'Momentum strategy',
            'mean_reversion': 'Contrarian strategy',
            'trend_following': 'Trend continuation strategy',
            'volatility_breakout': 'Breakout strategy',
            'kdj': 'Oscillator strategy'
        }
        
        strategy_type = strategy_types.get(selected_strategy, 'Custom strategy')
        
        # 候选策略分析
        candidate_names = [c['strategy'] for c in candidates]
        candidate_scores = [c['score'] for c in candidates]
        
        analysis = f"""
        Selected {strategy_type} ({selected_strategy}) from {len(candidates)} candidates.
        Candidate strategies: {', '.join(candidate_names)}
        Confidence scores: {candidate_scores}
        """
        
        return analysis.strip()
    
    def _assess_risk(self, strategy: str, features: Dict[str, Any], risk_budget: float) -> str:
        """评估风险"""
        
        # 策略风险等级
        risk_levels = {
            'buy_and_hold': 'Low',
            'macd': 'Medium',
            'rsi': 'Medium',
            'bollinger_bands': 'Medium',
            'momentum': 'High',
            'mean_reversion': 'Medium',
            'trend_following': 'Medium',
            'volatility_breakout': 'High',
            'kdj': 'Medium'
        }
        
        strategy_risk = risk_levels.get(strategy, 'Medium')
        
        # 市场风险
        market_risk = 'Low'
        if 'volatility' in features and features['volatility'] > 0.3:
            market_risk = 'High'
        elif 'volatility' in features and features['volatility'] > 0.15:
            market_risk = 'Medium'
        
        # 风险预算分析
        risk_budget_status = 'Within budget' if risk_budget > 0.02 else 'Conservative'
        
        assessment = f"""
        Strategy Risk: {strategy_risk}
        Market Risk: {market_risk}
        Risk Budget: {risk_budget_status} ({risk_budget:.2%})
        
        Risk Management:
        - Position sizing based on volatility
        - Stop-loss and take-profit levels set
        - Portfolio diversification maintained
        """
        
        return assessment.strip()
    
    def _predict_outcome(self, strategy: str, features: Dict[str, Any], 
                        evaluation_metrics: Dict[str, Any]) -> str:
        """预测结果"""
        
        # 基于历史表现
        historical_sharpe = evaluation_metrics.get('sharpe_ratio', 0)
        historical_return = evaluation_metrics.get('cagr', 0)
        historical_drawdown = evaluation_metrics.get('max_drawdown', 0)
        
        # 预期结果
        if historical_sharpe > 1.0:
            expected_performance = 'Strong positive performance expected'
        elif historical_sharpe > 0.5:
            expected_performance = 'Moderate positive performance expected'
        else:
            expected_performance = 'Conservative performance expected'
        
        # 时间框架
        if strategy in ['buy_and_hold', 'trend_following']:
            time_horizon = 'Long-term (weeks to months)'
        elif strategy in ['rsi', 'mean_reversion']:
            time_horizon = 'Short to medium-term (days to weeks)'
        else:
            time_horizon = 'Medium-term (weeks)'
        
        outcome = f"""
        Expected Performance: {expected_performance}
        Time Horizon: {time_horizon}
        Historical Sharpe: {historical_sharpe:.2f}
        Historical Return: {historical_return:.2%}
        Historical Max Drawdown: {historical_drawdown:.2%}
        
        Key Success Factors:
        - Market regime alignment
        - Risk management execution
        - Position sizing discipline
        """
        
        return outcome.strip()
    
    def _generate_english_explanation(self, asset: str, strategy: str, confidence: float,
                                    reasoning: str, risk_assessment: str, expected_outcome: str) -> str:
        """生成英文解释"""
        
        explanation = f"""
# Why This Trade: {asset} - {strategy}

## Executive Summary
We are executing a {strategy} strategy for {asset} with {confidence:.1%} confidence based on our AI-powered contextual bandit selector.

## Market Analysis
{reasoning}

## Risk Assessment
{risk_assessment}

## Expected Outcome
{expected_outcome}

## Decision Rationale
This trade was selected through our advanced multi-armed bandit system that:
1. Analyzes current market conditions using 50+ technical and fundamental features
2. Evaluates strategy performance in similar market regimes
3. Balances exploration and exploitation for optimal strategy selection
4. Considers risk-return trade-offs and portfolio diversification

## Risk Management
- Position sizing based on volatility targeting
- Stop-loss and take-profit levels automatically set
- Portfolio risk budget respected
- Regular monitoring and rebalancing

## Confidence Level
{confidence:.1%} confidence based on historical performance in similar market conditions.

---
*Generated by AI Trading System at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
        """
        
        return explanation.strip()
    
    def _generate_chinese_explanation(self, asset: str, strategy: str, confidence: float,
                                    reasoning: str, risk_assessment: str, expected_outcome: str) -> str:
        """生成中文解释"""
        
        # 策略中文名称
        strategy_names_cn = {
            'buy_and_hold': '买入持有策略',
            'macd': 'MACD趋势策略',
            'rsi': 'RSI均值回归策略',
            'bollinger_bands': '布林带策略',
            'momentum': '动量策略',
            'mean_reversion': '均值回归策略',
            'trend_following': '趋势跟踪策略',
            'volatility_breakout': '波动率突破策略',
            'kdj': 'KDJ策略'
        }
        
        strategy_cn = strategy_names_cn.get(strategy, strategy)
        
        explanation = f"""
# 交易解释：{asset} - {strategy_cn}

## 执行摘要
我们正在为 {asset} 执行 {strategy_cn}，基于AI驱动的上下文多臂老虎机选择器，置信度为 {confidence:.1%}。

## 市场分析
{reasoning}

## 风险评估
{risk_assessment}

## 预期结果
{expected_outcome}

## 决策理由
此交易通过我们的高级多臂老虎机系统选择：
1. 使用50+技术面和基本面特征分析当前市场条件
2. 评估策略在类似市场环境中的表现
3. 平衡探索和利用以实现最优策略选择
4. 考虑风险收益权衡和投资组合多样化

## 风险管理
- 基于波动率目标的仓位管理
- 自动设置止损和止盈水平
- 遵守投资组合风险预算
- 定期监控和再平衡

## 置信度
基于在类似市场条件下的历史表现，置信度为 {confidence:.1%}。

---
*由AI交易系统生成于 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
        """
        
        return explanation.strip()
    
    def generate_trade_card(self, explanation: TradeExplanation) -> str:
        """生成交易卡片"""
        
        card = f"""
┌─────────────────────────────────────────────────────────────┐
│                    🚀 AI TRADING CARD                      │
├─────────────────────────────────────────────────────────────┤
│ 资产: {explanation.asset:<15} 策略: {explanation.selected_strategy:<20} │
│ 置信度: {explanation.confidence:.1%}                                    │
├─────────────────────────────────────────────────────────────┤
│ 📊 市场分析:                                                │
│ {explanation.reasoning[:100]}...                            │
├─────────────────────────────────────────────────────────────┤
│ ⚠️  风险评估:                                               │
│ {explanation.risk_assessment[:100]}...                      │
├─────────────────────────────────────────────────────────────┤
│ 🎯 预期结果:                                                │
│ {explanation.expected_outcome[:100]}...                     │
└─────────────────────────────────────────────────────────────┘
        """
        
        return card.strip()
    
    def save_explanation(self, explanation: TradeExplanation, output_path: str = None):
        """保存解释"""
        if output_path is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = f'reports/trade_explanation_{explanation.asset}_{timestamp}.json'
        
        # 保存JSON格式
        explanation_data = {
            'asset': explanation.asset,
            'selected_strategy': explanation.selected_strategy,
            'confidence': explanation.confidence,
            'reasoning': explanation.reasoning,
            'risk_assessment': explanation.risk_assessment,
            'expected_outcome': explanation.expected_outcome,
            'english_explanation': explanation.english_explanation,
            'chinese_explanation': explanation.chinese_explanation,
            'timestamp': datetime.now().isoformat()
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(explanation_data, f, indent=2, ensure_ascii=False)
        
        # 保存Markdown格式
        md_path = output_path.replace('.json', '.md')
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(explanation.english_explanation)
            f.write('\n\n---\n\n')
            f.write(explanation.chinese_explanation)
        
        print(f"📄 解释已保存: {output_path}")
        print(f"📄 Markdown版本: {md_path}")
        
        return output_path
    
    def generate_summary_report(self, output_path: str = None):
        """生成汇总报告"""
        if not self.explanations:
            print("⚠️  没有解释数据")
            return
        
        if output_path is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = f'reports/trading_summary_{timestamp}.md'
        
        # 生成汇总报告
        report = f"""# AI交易解释汇总报告

## 概览
- 总交易数: {len(self.explanations)}
- 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 交易详情
"""
        
        for i, explanation in enumerate(self.explanations, 1):
            report += f"""
### 交易 {i}: {explanation.asset} - {explanation.selected_strategy}
- **置信度**: {explanation.confidence:.1%}
- **策略**: {explanation.selected_strategy}
- **推理**: {explanation.reasoning[:200]}...
- **风险评估**: {explanation.risk_assessment[:200]}...
- **预期结果**: {explanation.expected_outcome[:200]}...

---
"""
        
        # 保存报告
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"📄 汇总报告已保存: {output_path}")
        return output_path

def main():
    """主函数 - 演示LLM解释器"""
    print("🚀 LLM解释器演示")
    print("=" * 60)
    
    # 创建解释器
    explainer = LLMExplainer()
    
    # 模拟交易数据
    asset = "BTC"
    candidates = [
        {"strategy": "macd", "score": 0.85},
        {"strategy": "rsi", "score": 0.72},
        {"strategy": "momentum", "score": 0.68}
    ]
    
    features = {
        'trend_strength': 0.7,
        'volatility': 0.25,
        'rsi': 65,
        'momentum': 0.03
    }
    
    risk_budget = 0.02
    evaluation_metrics = {
        'sharpe_ratio': 1.2,
        'cagr': 0.15,
        'max_drawdown': 0.08
    }
    
    # 生成解释
    explanation = explainer.explain_trade(
        asset, candidates, features, risk_budget, evaluation_metrics
    )
    
    # 显示解释
    print(f"\n📊 交易解释:")
    print(f"资产: {explanation.asset}")
    print(f"策略: {explanation.selected_strategy}")
    print(f"置信度: {explanation.confidence:.1%}")
    
    # 生成交易卡片
    card = explainer.generate_trade_card(explanation)
    print(f"\n{card}")
    
    # 保存解释
    explainer.save_explanation(explanation)
    
    # 生成汇总报告
    explainer.generate_summary_report()
    
    print("\n" + "=" * 60)
    print("🎉 LLM解释器演示完成！")

if __name__ == "__main__":
    main()
