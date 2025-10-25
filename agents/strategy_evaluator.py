#!/usr/bin/env python3
"""
严格策略评估框架
Walk-forward + 成本/滑点 + baselines + bootstrap 置信区间
"""

import pandas as pd
import numpy as np
import argparse
import json
import os
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

from strategies.library import get_strategy_library
from strategies.middleware import apply_middleware, calculate_trade_costs
from selector.context_features import build_regime_features
from selector.thompson_selector import create_selector, ThompsonSelectorConfig

@dataclass
class EvaluationConfig:
    """评估配置"""
    asset: str
    start_date: str
    end_date: str
    wf_train_days: int = 180
    wf_test_days: int = 30
    selector_type: str = 'thompson'
    topk: int = 1
    fee_bps: float = 5.0
    slip_k: float = 0.1
    target_vol: float = 0.15
    take_profit: float = 0.02
    stop_loss: float = 0.01
    use_selector: bool = True
    bootstrap_samples: int = 1000
    confidence_level: float = 0.95

@dataclass
class EvaluationResult:
    """评估结果"""
    strategy_name: str
    cagr: float
    sharpe_ratio: float
    sortino_ratio: float
    calmar_ratio: float
    max_drawdown: float
    profit_factor: float
    hit_rate: float
    avg_win: float
    avg_loss: float
    turnover: float
    cvar_95: float
    recovery_time: float
    total_trades: int
    bootstrap_ci: Dict[str, Tuple[float, float]]

class StrictStrategyEvaluator:
    """严格策略评估器"""
    
    def __init__(self, config: EvaluationConfig):
        self.config = config
        self.strategy_library = get_strategy_library()
        self.results = []
        
        # 创建artifacts目录
        os.makedirs('artifacts', exist_ok=True)
        os.makedirs('reports', exist_ok=True)
    
    def load_data(self, data_path: str = "./data") -> pd.DataFrame:
        """加载数据"""
        csv_path = os.path.join(data_path, f"stellar_ohlc_15m_{self.config.asset}.csv")
        
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"数据文件不存在: {csv_path}")
        
        df = pd.read_csv(csv_path)
        df['ts'] = pd.to_datetime(df['ts'])
        df = df.set_index('ts')
        
        # 时间过滤
        start_date = pd.to_datetime(self.config.start_date, utc=True)
        end_date = pd.to_datetime(self.config.end_date, utc=True)
        df = df[(df.index >= start_date) & (df.index <= end_date)]
        
        return df
    
    def walk_forward_evaluation(self, df: pd.DataFrame) -> Dict[str, List[Dict]]:
        """Walk-forward评估"""
        print(f"🔄 Walk-forward评估: 训练期 {self.config.wf_train_days} 天, 测试期 {self.config.wf_test_days} 天")
        
        results = {}
        
        # 计算时间窗口
        total_days = (df.index[-1] - df.index[0]).days
        step_days = self.config.wf_test_days
        
        for start_idx in range(0, len(df), step_days * 24 * 4):  # 15分钟数据
            if start_idx + (self.config.wf_train_days + self.config.wf_test_days) * 24 * 4 >= len(df):
                break
            
            # 训练期
            train_start = start_idx
            train_end = start_idx + self.config.wf_train_days * 24 * 4
            train_data = df.iloc[train_start:train_end]
            
            # 测试期
            test_start = train_end
            test_end = test_start + self.config.wf_test_days * 24 * 4
            test_data = df.iloc[test_start:test_end]
            
            if len(train_data) < 100 or len(test_data) < 100:
                continue
            
            print(f"  训练期: {train_data.index[0]} 到 {train_data.index[-1]}")
            print(f"  测试期: {test_data.index[0]} 到 {test_data.index[-1]}")
            
            # 训练选择器
            if self.config.use_selector:
                selector = self._train_selector(train_data)
            else:
                selector = None
            
            # 测试策略
            period_results = self._test_strategies(test_data, selector)
            
            for strategy_name, result in period_results.items():
                if strategy_name not in results:
                    results[strategy_name] = []
                results[strategy_name].append(result)
        
        return results
    
    def _train_selector(self, train_data: pd.DataFrame) -> Any:
        """训练选择器"""
        try:
            # 创建选择器
            config = ThompsonSelectorConfig(
                n_arms=len(self.strategy_library.get_strategy_names()),
                n_features=50
            )
            selector = create_selector(self.config.selector_type, config)
            
            # 训练数据
            prices = train_data['close']
            features = build_regime_features(prices)
            
            # 为每个策略生成训练样本
            for strategy_name in self.strategy_library.get_strategy_names():
                strategy = self.strategy_library.get_strategy(strategy_name)
                if strategy is None:
                    continue
                
                # 运行策略
                try:
                    output = strategy.run(prices, features)
                    positions = output.positions
                    
                    # 计算奖励
                    returns = prices.pct_change()
                    strategy_returns = positions.shift(1) * returns
                    cumulative_returns = (1 + strategy_returns).cumprod()
                    
                    # 计算奖励（简化）
                    total_return = cumulative_returns.iloc[-1] - 1
                    volatility = strategy_returns.std() * np.sqrt(252)
                    sharpe = total_return / volatility if volatility > 0 else 0
                    
                    reward = sharpe  # 使用夏普比率作为奖励
                    
                    # 更新选择器
                    for i in range(len(features)):
                        if i < 20:  # 跳过前20个数据点
                            continue
                        
                        feature_vector = features.iloc[i].select_dtypes(include=[np.number]).values
                        if len(feature_vector) > 0:
                            arm_idx = self.strategy_library.get_strategy_names().index(strategy_name)
                            selector.update(feature_vector, arm_idx, reward)
                
                except Exception as e:
                    print(f"    策略 {strategy_name} 训练失败: {e}")
                    continue
            
            return selector
            
        except Exception as e:
            print(f"    选择器训练失败: {e}")
            return None
    
    def _test_strategies(self, test_data: pd.DataFrame, selector: Any = None) -> Dict[str, Dict]:
        """测试策略"""
        results = {}
        prices = test_data['close']
        features = build_regime_features(prices)
        
        # 选择要测试的策略
        if selector is not None and self.config.use_selector:
            # 使用选择器推荐策略
            feature_vector = features.iloc[-1].select_dtypes(include=[np.number]).values
            if len(feature_vector) > 0:
                selected_arms = selector.pick(feature_vector, self.config.topk)
                strategy_names = self.strategy_library.get_strategy_names()
                selected_strategies = [strategy_names[arm] for arm in selected_arms]
            else:
                selected_strategies = self.strategy_library.get_strategy_names()[:3]
        else:
            # 测试所有策略
            selected_strategies = self.strategy_library.get_strategy_names()
        
        print(f"    测试策略: {selected_strategies}")
        
        for strategy_name in selected_strategies:
            try:
                strategy = self.strategy_library.get_strategy(strategy_name)
                if strategy is None:
                    continue
                
                # 运行策略
                output = strategy.run(prices, features)
                positions = output.positions
                
                # 应用中间件
                middleware_config = {
                    "vol_target": {"enabled": True, "target_vol": self.config.target_vol},
                    "tp_sl": {"enabled": True, "take_profit": self.config.take_profit, "stop_loss": self.config.stop_loss},
                    "position_sizing": {"enabled": True, "max_position": 1.0}
                }
                
                adjusted_positions = apply_middleware(positions, prices, middleware_config)
                
                # 计算交易成本
                fee_costs, slippage, total_costs = calculate_trade_costs(adjusted_positions, prices, {
                    "fee_bps": self.config.fee_bps,
                    "slip_k": self.config.slip_k
                })
                
                # 计算收益
                returns = prices.pct_change()
                strategy_returns = adjusted_positions.shift(1) * returns
                net_returns = strategy_returns - total_costs
                
                # 计算指标
                metrics = self._calculate_metrics(net_returns, prices)
                metrics['strategy_name'] = strategy_name
                metrics['total_trades'] = len(adjusted_positions.diff().abs()[adjusted_positions.diff().abs() > 0])
                
                results[strategy_name] = metrics
                
            except Exception as e:
                print(f"    策略 {strategy_name} 测试失败: {e}")
                continue
        
        return results
    
    def _calculate_metrics(self, returns: pd.Series, prices: pd.Series) -> Dict[str, float]:
        """计算评估指标"""
        # 基本指标
        total_return = (1 + returns).prod() - 1
        cagr = (1 + total_return) ** (252 / len(returns)) - 1
        
        # 风险指标
        volatility = returns.std() * np.sqrt(252)
        sharpe_ratio = cagr / volatility if volatility > 0 else 0
        
        # Sortino比率
        downside_returns = returns[returns < 0]
        downside_vol = downside_returns.std() * np.sqrt(252) if len(downside_returns) > 0 else 0
        sortino_ratio = cagr / downside_vol if downside_vol > 0 else 0
        
        # 最大回撤
        cumulative = (1 + returns).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = drawdown.min()
        
        # 卡玛比率
        calmar_ratio = cagr / abs(max_drawdown) if max_drawdown != 0 else 0
        
        # 盈亏比
        winning_trades = returns[returns > 0]
        losing_trades = returns[returns < 0]
        profit_factor = abs(winning_trades.sum() / losing_trades.sum()) if len(losing_trades) > 0 else float('inf')
        
        # 胜率
        hit_rate = len(winning_trades) / len(returns) if len(returns) > 0 else 0
        
        # 平均盈亏
        avg_win = winning_trades.mean() if len(winning_trades) > 0 else 0
        avg_loss = losing_trades.mean() if len(losing_trades) > 0 else 0
        
        # 换手率
        turnover = returns.abs().sum()
        
        # CVaR
        cvar_95 = returns.quantile(0.05) if len(returns) > 0 else 0
        
        # 恢复时间
        recovery_time = self._calculate_recovery_time(cumulative)
        
        return {
            'cagr': cagr,
            'sharpe_ratio': sharpe_ratio,
            'sortino_ratio': sortino_ratio,
            'calmar_ratio': calmar_ratio,
            'max_drawdown': max_drawdown,
            'profit_factor': profit_factor,
            'hit_rate': hit_rate,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'turnover': turnover,
            'cvar_95': cvar_95,
            'recovery_time': recovery_time
        }
    
    def _calculate_recovery_time(self, cumulative: pd.Series) -> float:
        """计算恢复时间"""
        max_dd_periods = 0
        current_dd_periods = 0
        
        for i, value in enumerate(cumulative):
            if i == 0:
                continue
            
            if value < cumulative.iloc[:i+1].max():
                current_dd_periods += 1
                max_dd_periods = max(max_dd_periods, current_dd_periods)
            else:
                current_dd_periods = 0
        
        return max_dd_periods / (24 * 4)  # 转换为天数
    
    def bootstrap_confidence_intervals(self, results: Dict[str, List[Dict]]) -> Dict[str, Dict[str, Tuple[float, float]]]:
        """Bootstrap置信区间"""
        print(f"🔄 Bootstrap置信区间: {self.config.bootstrap_samples} 样本")
        
        bootstrap_results = {}
        
        for strategy_name, period_results in results.items():
            if not period_results:
                continue
            
            # 提取指标
            metrics = ['cagr', 'sharpe_ratio', 'sortino_ratio', 'calmar_ratio', 'max_drawdown']
            bootstrap_values = {metric: [] for metric in metrics}
            
            # Bootstrap采样
            for _ in range(self.config.bootstrap_samples):
                # 按月采样
                monthly_samples = []
                for result in period_results:
                    if 'month' in result:
                        monthly_samples.append(result)
                
                if not monthly_samples:
                    continue
                
                # 随机采样
                sample = np.random.choice(monthly_samples, size=len(monthly_samples), replace=True)
                
                # 计算平均指标
                for metric in metrics:
                    values = [r.get(metric, 0) for r in sample]
                    bootstrap_values[metric].append(np.mean(values))
            
            # 计算置信区间
            ci_results = {}
            alpha = 1 - self.config.confidence_level
            for metric in metrics:
                if bootstrap_values[metric]:
                    lower = np.percentile(bootstrap_values[metric], (alpha/2) * 100)
                    upper = np.percentile(bootstrap_values[metric], (1 - alpha/2) * 100)
                    ci_results[metric] = (lower, upper)
            
            bootstrap_results[strategy_name] = ci_results
        
        return bootstrap_results
    
    def evaluate_baselines(self, df: pd.DataFrame) -> Dict[str, Dict]:
        """评估基准策略"""
        print("📊 评估基准策略")
        
        baselines = {}
        prices = df['close']
        
        # Buy & Hold
        returns = prices.pct_change()
        metrics = self._calculate_metrics(returns, prices)
        metrics['strategy_name'] = 'Buy & Hold'
        baselines['Buy & Hold'] = metrics
        
        # 等权重组合
        strategy_returns = []
        for strategy_name in self.strategy_library.get_strategy_names():
            try:
                strategy = self.strategy_library.get_strategy(strategy_name)
                if strategy is None:
                    continue
                
                features = build_regime_features(prices)
                output = strategy.run(prices, features)
                positions = output.positions
                
                strategy_returns.append(positions.shift(1) * returns)
                
            except Exception as e:
                print(f"    策略 {strategy_name} 失败: {e}")
                continue
        
        if strategy_returns:
            # 等权重组合
            equal_weight_returns = pd.concat(strategy_returns, axis=1).mean(axis=1)
            metrics = self._calculate_metrics(equal_weight_returns, prices)
            metrics['strategy_name'] = 'Equal Weight'
            baselines['Equal Weight'] = metrics
        
        return baselines
    
    def generate_report(self, results: Dict[str, List[Dict]], baselines: Dict[str, Dict], 
                       bootstrap_ci: Dict[str, Dict[str, Tuple[float, float]]]) -> str:
        """生成评估报告"""
        print("📄 生成评估报告")
        
        # 计算平均指标
        avg_results = {}
        for strategy_name, period_results in results.items():
            if not period_results:
                continue
            
            avg_metrics = {}
            for metric in ['cagr', 'sharpe_ratio', 'sortino_ratio', 'calmar_ratio', 'max_drawdown', 'profit_factor', 'hit_rate']:
                values = [r.get(metric, 0) for r in period_results]
                avg_metrics[metric] = np.mean(values)
            
            avg_results[strategy_name] = avg_metrics
        
        # 生成Markdown报告
        report = f"""# 策略评估报告

## 评估配置
- **资产**: {self.config.asset}
- **时间范围**: {self.config.start_date} 到 {self.config.end_date}
- **Walk-forward**: 训练期 {self.config.wf_train_days} 天, 测试期 {self.config.wf_test_days} 天
- **选择器**: {self.config.selector_type} (topk={self.config.topk})
- **成本**: 手续费 {self.config.fee_bps}bps, 滑点 {self.config.slip_k}
- **风险管理**: 目标波动率 {self.config.target_vol}, 止盈 {self.config.take_profit}, 止损 {self.config.stop_loss}

## 策略表现

### 主要指标
| 策略 | CAGR | Sharpe | Sortino | Calmar | Max DD | Profit Factor | Hit Rate |
|------|------|--------|---------|--------|--------|---------------|----------|
"""
        
        # 添加基准策略
        for name, metrics in baselines.items():
            report += f"| {name} | {metrics['cagr']:.2%} | {metrics['sharpe_ratio']:.2f} | {metrics['sortino_ratio']:.2f} | {metrics['calmar_ratio']:.2f} | {metrics['max_drawdown']:.2%} | {metrics['profit_factor']:.2f} | {metrics['hit_rate']:.2%} |\n"
        
        # 添加评估策略
        for name, metrics in avg_results.items():
            report += f"| {name} | {metrics['cagr']:.2%} | {metrics['sharpe_ratio']:.2f} | {metrics['sortino_ratio']:.2f} | {metrics['calmar_ratio']:.2f} | {metrics['max_drawdown']:.2%} | {metrics['profit_factor']:.2f} | {metrics['hit_rate']:.2%} |\n"
        
        # 添加Bootstrap置信区间
        report += "\n## Bootstrap置信区间\n"
        for strategy_name, ci in bootstrap_ci.items():
            report += f"\n### {strategy_name}\n"
            for metric, (lower, upper) in ci.items():
                report += f"- **{metric}**: [{lower:.3f}, {upper:.3f}]\n"
        
        # 保存报告
        report_path = f"reports/strategy_evaluation_{self.config.asset}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"📄 报告已保存: {report_path}")
        return report_path
    
    def run_evaluation(self) -> Dict[str, Any]:
        """运行完整评估"""
        print("🚀 开始严格策略评估")
        print("=" * 60)
        
        # 加载数据
        df = self.load_data()
        print(f"📊 数据加载: {len(df)} 条记录")
        print(f"📅 时间范围: {df.index[0]} 到 {df.index[-1]}")
        
        # Walk-forward评估
        results = self.walk_forward_evaluation(df)
        
        # 评估基准策略
        baselines = self.evaluate_baselines(df)
        
        # Bootstrap置信区间
        bootstrap_ci = self.bootstrap_confidence_intervals(results)
        
        # 生成报告
        report_path = self.generate_report(results, baselines, bootstrap_ci)
        
        return {
            "results": results,
            "baselines": baselines,
            "bootstrap_ci": bootstrap_ci,
            "report_path": report_path
        }

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='严格策略评估')
    parser.add_argument('--asset', type=str, default='BTC', help='资产符号')
    parser.add_argument('--start', type=str, default='2022-01-01', help='开始日期')
    parser.add_argument('--end', type=str, default='2024-12-31', help='结束日期')
    parser.add_argument('--wf-train', type=int, default=180, help='训练期天数')
    parser.add_argument('--wf-test', type=int, default=30, help='测试期天数')
    parser.add_argument('--selector', type=str, default='thompson', help='选择器类型')
    parser.add_argument('--topk', type=int, default=1, help='选择策略数量')
    parser.add_argument('--fee-bps', type=float, default=5.0, help='手续费(基点)')
    parser.add_argument('--slip-k', type=float, default=0.1, help='滑点系数')
    parser.add_argument('--target-vol', type=float, default=0.15, help='目标波动率')
    parser.add_argument('--tp', type=float, default=0.02, help='止盈比例')
    parser.add_argument('--sl', type=float, default=0.01, help='止损比例')
    parser.add_argument('--use-selector', action='store_true', help='使用选择器')
    
    args = parser.parse_args()
    
    # 创建配置
    config = EvaluationConfig(
        asset=args.asset,
        start_date=args.start,
        end_date=args.end,
        wf_train_days=args.wf_train,
        wf_test_days=args.wf_test,
        selector_type=args.selector,
        topk=args.topk,
        fee_bps=args.fee_bps,
        slip_k=args.slip_k,
        target_vol=args.target_vol,
        take_profit=args.tp,
        stop_loss=args.sl,
        use_selector=args.use_selector
    )
    
    # 运行评估
    evaluator = StrictStrategyEvaluator(config)
    results = evaluator.run_evaluation()
    
    print("\n" + "=" * 60)
    print("🎉 评估完成！")

if __name__ == "__main__":
    main()