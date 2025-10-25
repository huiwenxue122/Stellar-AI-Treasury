#!/usr/bin/env python3
"""
选择器训练器
离线训练和在线更新选择器状态
"""

import pandas as pd
import numpy as np
import argparse
import os
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

from strategies.library import get_strategy_library
from strategies.middleware import apply_middleware, calculate_trade_costs
from selector.context_features import build_regime_features
from selector.thompson_selector import create_selector, ThompsonSelectorConfig

@dataclass
class TrainingConfig:
    """训练配置"""
    train_start: str
    train_end: str
    selector_type: str = 'thompson'
    topk: int = 1
    save_path: str = 'artifacts/selector_state.pkl'
    data_path: str = './data'
    assets: List[str] = None
    reward_function: str = 'sharpe'  # 'sharpe', 'return', 'risk_adjusted'
    alpha_dd: float = 0.5  # 回撤惩罚系数
    alpha_vol: float = 0.3  # 波动率惩罚系数

class SelectorTrainer:
    """选择器训练器"""
    
    def __init__(self, config: TrainingConfig):
        self.config = config
        self.strategy_library = get_strategy_library()
        
        # 创建artifacts目录
        os.makedirs('artifacts', exist_ok=True)
        
        # 默认资产列表
        if config.assets is None:
            config.assets = ['BTC', 'ETH', 'SOL', 'ARB', 'LINK', 'AAVE', 'LDO', 'FET', 'XLM']
    
    def load_asset_data(self, asset: str) -> pd.DataFrame:
        """加载资产数据"""
        csv_path = os.path.join(self.config.data_path, f"stellar_ohlc_15m_{asset}.csv")
        
        if not os.path.exists(csv_path):
            print(f"⚠️  数据文件不存在: {csv_path}")
            return pd.DataFrame()
        
        df = pd.read_csv(csv_path)
        df['ts'] = pd.to_datetime(df['ts'])
        df = df.set_index('ts')
        
        # 时间过滤
        start_date = pd.to_datetime(self.config.train_start, utc=True)
        end_date = pd.to_datetime(self.config.train_end, utc=True)
        df = df[(df.index >= start_date) & (df.index <= end_date)]
        
        return df
    
    def calculate_reward(self, returns: pd.Series, positions: pd.Series, 
                        prices: pd.Series) -> float:
        """计算奖励"""
        if self.config.reward_function == 'sharpe':
            # 夏普比率
            if returns.std() == 0:
                return 0.0
            return returns.mean() / returns.std() * np.sqrt(252)
        
        elif self.config.reward_function == 'return':
            # 总收益
            return (1 + returns).prod() - 1
        
        elif self.config.reward_function == 'risk_adjusted':
            # 风险调整收益
            total_return = (1 + returns).prod() - 1
            
            # 计算回撤
            cumulative = (1 + returns).cumprod()
            running_max = cumulative.expanding().max()
            drawdown = (cumulative - running_max) / running_max
            max_drawdown = abs(drawdown.min())
            
            # 计算波动率
            volatility = returns.std() * np.sqrt(252)
            
            # 风险调整收益
            risk_adjusted_return = total_return - (self.config.alpha_dd * max_drawdown + self.config.alpha_vol * volatility)
            
            return risk_adjusted_return
        
        else:
            return 0.0
    
    def generate_training_samples(self, df: pd.DataFrame) -> List[Tuple[np.ndarray, int, float]]:
        """生成训练样本"""
        samples = []
        
        if df.empty:
            return samples
        
        prices = df['close']
        features_df = build_regime_features(prices)
        
        # 确保features是DataFrame格式
        if isinstance(features_df, pd.Series):
            features_df = features_df.to_frame().T
        
        # 为每个策略生成样本
        for strategy_name in self.strategy_library.get_strategy_names():
            try:
                strategy = self.strategy_library.get_strategy(strategy_name)
                if strategy is None:
                    continue
                
                # 运行策略
                output = strategy.run(prices, features_df)
                positions = output.positions
                
                # 计算收益
                returns = prices.pct_change()
                strategy_returns = positions.shift(1) * returns
                
                # 计算奖励
                reward = self.calculate_reward(strategy_returns, positions, prices)
                
                # 为每个时间点生成样本
                for i in range(20, len(features_df)):  # 跳过前20个数据点
                    # 获取数值特征
                    numeric_features = features_df.select_dtypes(include=[np.number])
                    if len(numeric_features.columns) > 0:
                        feature_vector = numeric_features.iloc[i].values
                    if len(feature_vector) > 0:
                        arm_idx = self.strategy_library.get_strategy_names().index(strategy_name)
                        samples.append((feature_vector, arm_idx, reward))
                
            except Exception as e:
                print(f"    策略 {strategy_name} 样本生成失败: {e}")
                continue
        
        return samples
    
    def train_selector(self) -> Any:
        """训练选择器"""
        print(f"🚀 开始训练选择器: {self.config.selector_type}")
        print(f"📅 训练时间: {self.config.train_start} 到 {self.config.train_end}")
        print(f"📊 资产列表: {self.config.assets}")
        
        # 创建选择器
        config = ThompsonSelectorConfig(
            n_arms=len(self.strategy_library.get_strategy_names()),
            n_features=50,  # 将根据实际特征调整
            alpha=1.0,
            beta=1.0
        )
        selector = create_selector(self.config.selector_type, config)
        
        # 收集所有训练样本
        all_samples = []
        
        for asset in self.config.assets:
            print(f"\n📈 处理资产: {asset}")
            
            # 加载数据
            df = self.load_asset_data(asset)
            if df.empty:
                print(f"    ⚠️  跳过 {asset}: 无数据")
                continue
            
            print(f"    📊 数据: {len(df)} 条记录")
            
            # 生成训练样本
            samples = self.generate_training_samples(df)
            print(f"    🔢 样本: {len(samples)} 个")
            
            all_samples.extend(samples)
        
        print(f"\n📊 总样本数: {len(all_samples)}")
        
        if not all_samples:
            print("❌ 没有训练样本，无法训练选择器")
            return None
        
        # 更新选择器特征维度
        feature_dim = len(all_samples[0][0])
        selector.n_features = feature_dim
        selector.config.n_features = feature_dim
        
        # 重新初始化选择器
        selector.mu = np.zeros((selector.n_arms, feature_dim))
        selector.Sigma = np.array([np.eye(feature_dim) for _ in range(selector.n_arms)])
        selector.b = np.zeros((selector.n_arms, feature_dim))
        selector.A = np.array([np.eye(feature_dim) for _ in range(selector.n_arms)])
        
        # 训练选择器
        print(f"🔄 训练选择器: {len(all_samples)} 个样本")
        
        for i, (feature_vector, arm_idx, reward) in enumerate(all_samples):
            selector.update(feature_vector, arm_idx, reward)
            
            if (i + 1) % 1000 == 0:
                print(f"    已处理: {i + 1}/{len(all_samples)} 样本")
        
        # 显示训练结果
        print(f"\n📊 训练结果:")
        stats = selector.get_arm_stats()
        for arm, stat in stats.items():
            strategy_name = self.strategy_library.get_strategy_names()[int(arm.split('_')[1])]
            print(f"    {strategy_name}: 拉动次数 {stat['n_pulls']}, 平均奖励 {stat['avg_reward']:.4f}")
        
        return selector
    
    def save_selector(self, selector: Any):
        """保存选择器状态"""
        if selector is None:
            print("❌ 选择器为空，无法保存")
            return
        
        try:
            selector.save_state(self.config.save_path)
            print(f"💾 选择器状态已保存: {self.config.save_path}")
        except Exception as e:
            print(f"❌ 保存失败: {e}")
    
    def load_selector(self) -> Any:
        """加载选择器状态"""
        if not os.path.exists(self.config.save_path):
            print(f"⚠️  状态文件不存在: {self.config.save_path}")
            return None
        
        try:
            config = ThompsonSelectorConfig(
                n_arms=len(self.strategy_library.get_strategy_names()),
                n_features=50
            )
            selector = create_selector(self.config.selector_type, config)
            selector.load_state(self.config.save_path)
            print(f"✅ 选择器状态已加载: {self.config.save_path}")
            return selector
        except Exception as e:
            print(f"❌ 加载失败: {e}")
            return None
    
    def update_selector(self, new_data: pd.DataFrame, asset: str):
        """在线更新选择器"""
        print(f"🔄 在线更新选择器: {asset}")
        
        # 加载现有选择器
        selector = self.load_selector()
        if selector is None:
            print("❌ 无法加载选择器，请先训练")
            return
        
        # 生成新样本
        samples = self.generate_training_samples(new_data)
        print(f"    📊 新样本: {len(samples)} 个")
        
        # 更新选择器
        for feature_vector, arm_idx, reward in samples:
            selector.update(feature_vector, arm_idx, reward)
        
        # 保存更新后的状态
        self.save_selector(selector)
        print(f"✅ 选择器已更新")
    
    def evaluate_selector(self, test_data: pd.DataFrame, asset: str) -> Dict[str, Any]:
        """评估选择器性能"""
        print(f"📊 评估选择器性能: {asset}")
        
        # 加载选择器
        selector = self.load_selector()
        if selector is None:
            print("❌ 无法加载选择器")
            return {}
        
        prices = test_data['close']
        features = build_regime_features(prices)
        
        # 测试选择器推荐
        feature_vector = features.iloc[-1].select_dtypes(include=[np.number]).values
        if len(feature_vector) == 0:
            print("❌ 无有效特征")
            return {}
        
        # 获取推荐策略
        selected_arms = selector.pick(feature_vector, self.config.topk)
        strategy_names = self.strategy_library.get_strategy_names()
        selected_strategies = [strategy_names[arm] for arm in selected_arms]
        
        print(f"    🎯 推荐策略: {selected_strategies}")
        
        # 测试推荐策略
        results = {}
        for strategy_name in selected_strategies:
            try:
                strategy = self.strategy_library.get_strategy(strategy_name)
                if strategy is None:
                    continue
                
                # 运行策略
                output = strategy.run(prices, features_df)
                positions = output.positions
                
                # 计算收益
                returns = prices.pct_change()
                strategy_returns = positions.shift(1) * returns
                
                # 计算指标
                total_return = (1 + strategy_returns).prod() - 1
                volatility = strategy_returns.std() * np.sqrt(252)
                sharpe = total_return / volatility if volatility > 0 else 0
                
                results[strategy_name] = {
                    'total_return': total_return,
                    'volatility': volatility,
                    'sharpe_ratio': sharpe
                }
                
            except Exception as e:
                print(f"    策略 {strategy_name} 评估失败: {e}")
                continue
        
        return results
    
    def run_training(self) -> Any:
        """运行训练"""
        print("🚀 选择器训练器")
        print("=" * 60)
        
        # 训练选择器
        selector = self.train_selector()
        
        if selector is not None:
            # 保存选择器
            self.save_selector(selector)
            
            # 显示选择器信息
            info = selector.get_info()
            print(f"\n📊 选择器信息:")
            print(f"    臂数: {info['n_arms']}")
            print(f"    特征维度: {info['n_features']}")
            print(f"    是否初始化: {info['is_initialized']}")
            print(f"    总拉动次数: {info['total_pulls']}")
            
            return selector
        else:
            print("❌ 训练失败")
            return None

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='选择器训练器')
    parser.add_argument('--train-start', type=str, default='2022-01-01', help='训练开始日期')
    parser.add_argument('--train-end', type=str, default='2024-06-30', help='训练结束日期')
    parser.add_argument('--selector', type=str, default='thompson', help='选择器类型')
    parser.add_argument('--topk', type=int, default=1, help='选择策略数量')
    parser.add_argument('--save', type=str, default='artifacts/selector_state.pkl', help='保存路径')
    parser.add_argument('--data-path', type=str, default='./data', help='数据路径')
    parser.add_argument('--assets', nargs='+', default=['BTC', 'ETH', 'SOL'], help='训练资产')
    parser.add_argument('--reward-function', type=str, default='sharpe', help='奖励函数')
    parser.add_argument('--alpha-dd', type=float, default=0.5, help='回撤惩罚系数')
    parser.add_argument('--alpha-vol', type=float, default=0.3, help='波动率惩罚系数')
    
    args = parser.parse_args()
    
    # 创建配置
    config = TrainingConfig(
        train_start=args.train_start,
        train_end=args.train_end,
        selector_type=args.selector,
        topk=args.topk,
        save_path=args.save,
        data_path=args.data_path,
        assets=args.assets,
        reward_function=args.reward_function,
        alpha_dd=args.alpha_dd,
        alpha_vol=args.alpha_vol
    )
    
    # 运行训练
    trainer = SelectorTrainer(config)
    selector = trainer.run_training()
    
    print("\n" + "=" * 60)
    print("🎉 训练完成！")

if __name__ == "__main__":
    main()