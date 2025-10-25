#!/usr/bin/env python3
"""
Thompson采样选择器
基于线性高斯后验的Contextual Thompson Sampling
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional, Tuple
import pickle
import os
from dataclasses import dataclass
import warnings
warnings.filterwarnings('ignore')

@dataclass
class ThompsonSelectorConfig:
    """Thompson选择器配置"""
    alpha: float = 1.0          # 噪声参数
    beta: float = 1.0           # 正则化参数
    n_arms: int = 10           # 臂数（策略数）
    n_features: int = 50       # 特征维度
    warmup_samples: int = 100  # 预热样本数
    update_frequency: int = 10 # 更新频率

class ThompsonSelector:
    """Thompson采样选择器"""
    
    def __init__(self, config: ThompsonSelectorConfig):
        self.config = config
        self.n_arms = config.n_arms
        self.n_features = config.n_features
        
        # 初始化后验参数
        self.mu = np.zeros((self.n_arms, self.n_features))  # 均值
        self.Sigma = np.array([np.eye(self.n_features) for _ in range(self.n_arms)])  # 协方差
        self.b = np.zeros((self.n_arms, self.n_features))   # 累积奖励
        self.A = np.array([np.eye(self.n_features) for _ in range(self.n_arms)])  # 累积特征
        
        # 统计信息
        self.n_pulls = np.zeros(self.n_arms)  # 每个臂的拉动次数
        self.total_rewards = np.zeros(self.n_arms)  # 总奖励
        self.arm_rewards = [[] for _ in range(self.n_arms)]  # 每个臂的奖励历史
        
        # 状态
        self.is_initialized = False
        self.update_count = 0
    
    def pick(self, x: np.ndarray, topk: int = 2) -> List[int]:
        """
        选择top-k策略
        
        Args:
            x: 情境特征向量
            topk: 返回的策略数量
            
        Returns:
            选择的策略索引列表
        """
        if not self.is_initialized:
            # 如果未初始化，随机选择
            return np.random.choice(self.n_arms, size=min(topk, self.n_arms), replace=False).tolist()
        
        # 计算每个臂的采样值
        sampled_values = []
        for arm in range(self.n_arms):
            # 从后验分布采样
            theta = np.random.multivariate_normal(self.mu[arm], self.Sigma[arm])
            sampled_value = np.dot(theta, x)
            sampled_values.append(sampled_value)
        
        # 选择top-k
        top_arms = np.argsort(sampled_values)[-topk:][::-1]
        return top_arms.tolist()
    
    def update(self, x: np.ndarray, k: int, reward: float):
        """
        更新后验分布
        
        Args:
            x: 情境特征向量
            k: 选择的策略索引
            reward: 观察到的奖励
        """
        # 更新统计信息
        self.n_pulls[k] += 1
        self.total_rewards[k] += reward
        self.arm_rewards[k].append(reward)
        
        # 更新后验参数
        self.b[k] += reward * x
        self.A[k] += np.outer(x, x)
        
        # 更新协方差矩阵
        self.Sigma[k] = np.linalg.inv(self.A[k] + self.config.beta * np.eye(self.n_features))
        
        # 更新均值
        self.mu[k] = self.Sigma[k] @ self.b[k]
        
        self.update_count += 1
        
        # 检查是否初始化
        if not self.is_initialized and self.update_count >= self.config.warmup_samples:
            self.is_initialized = True
    
    def get_arm_stats(self) -> Dict[str, Any]:
        """获取臂统计信息"""
        stats = {}
        for arm in range(self.n_arms):
            if self.n_pulls[arm] > 0:
                stats[f'arm_{arm}'] = {
                    'n_pulls': self.n_pulls[arm],
                    'total_reward': self.total_rewards[arm],
                    'avg_reward': self.total_rewards[arm] / self.n_pulls[arm],
                    'reward_std': np.std(self.arm_rewards[arm]) if len(self.arm_rewards[arm]) > 1 else 0
                }
        return stats
    
    def get_confidence_bounds(self, x: np.ndarray, confidence: float = 0.95) -> Dict[int, Tuple[float, float]]:
        """
        获取置信区间
        
        Args:
            x: 情境特征向量
            confidence: 置信水平
            
        Returns:
            每个臂的置信区间
        """
        bounds = {}
        z_score = 1.96 if confidence == 0.95 else 2.576  # 95% or 99%
        
        for arm in range(self.n_arms):
            if self.n_pulls[arm] > 0:
                # 计算预测均值和方差
                mean_pred = np.dot(self.mu[arm], x)
                var_pred = np.dot(x, self.Sigma[arm] @ x)
                std_pred = np.sqrt(var_pred)
                
                # 置信区间
                lower = mean_pred - z_score * std_pred
                upper = mean_pred + z_score * std_pred
                
                bounds[arm] = (lower, upper)
        
        return bounds
    
    def get_expected_rewards(self, x: np.ndarray) -> Dict[int, float]:
        """
        获取期望奖励
        
        Args:
            x: 情境特征向量
            
        Returns:
            每个臂的期望奖励
        """
        expected_rewards = {}
        for arm in range(self.n_arms):
            if self.n_pulls[arm] > 0:
                expected_rewards[arm] = np.dot(self.mu[arm], x)
            else:
                expected_rewards[arm] = 0.0
        
        return expected_rewards
    
    def get_arm_rankings(self, x: np.ndarray) -> List[Tuple[int, float]]:
        """
        获取臂排名
        
        Args:
            x: 情境特征向量
            
        Returns:
            按期望奖励排序的臂列表
        """
        expected_rewards = self.get_expected_rewards(x)
        rankings = sorted(expected_rewards.items(), key=lambda x: x[1], reverse=True)
        return rankings
    
    def save_state(self, filepath: str):
        """保存状态"""
        state = {
            'config': self.config,
            'mu': self.mu,
            'Sigma': self.Sigma,
            'b': self.b,
            'A': self.A,
            'n_pulls': self.n_pulls,
            'total_rewards': self.total_rewards,
            'arm_rewards': self.arm_rewards,
            'is_initialized': self.is_initialized,
            'update_count': self.update_count
        }
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'wb') as f:
            pickle.dump(state, f)
    
    def load_state(self, filepath: str):
        """加载状态"""
        if os.path.exists(filepath):
            with open(filepath, 'rb') as f:
                state = pickle.load(f)
            
            self.config = state['config']
            self.mu = state['mu']
            self.Sigma = state['Sigma']
            self.b = state['b']
            self.A = state['A']
            self.n_pulls = state['n_pulls']
            self.total_rewards = state['total_rewards']
            self.arm_rewards = state['arm_rewards']
            self.is_initialized = state['is_initialized']
            self.update_count = state['update_count']
        else:
            print(f"状态文件不存在: {filepath}")
    
    def reset(self):
        """重置选择器"""
        self.mu = np.zeros((self.n_arms, self.n_features))
        self.Sigma = np.array([np.eye(self.n_features) for _ in range(self.n_arms)])
        self.b = np.zeros((self.n_arms, self.n_features))
        self.A = np.array([np.eye(self.n_features) for _ in range(self.n_arms)])
        self.n_pulls = np.zeros(self.n_arms)
        self.total_rewards = np.zeros(self.n_arms)
        self.arm_rewards = [[] for _ in range(self.n_arms)]
        self.is_initialized = False
        self.update_count = 0
    
    def get_info(self) -> Dict[str, Any]:
        """获取选择器信息"""
        return {
            'config': self.config,
            'n_arms': self.n_arms,
            'n_features': self.n_features,
            'is_initialized': self.is_initialized,
            'update_count': self.update_count,
            'total_pulls': np.sum(self.n_pulls),
            'arm_stats': self.get_arm_stats()
        }

class LinUCBSelector:
    """LinUCB选择器（作为对比）"""
    
    def __init__(self, config: ThompsonSelectorConfig):
        self.config = config
        self.n_arms = config.n_arms
        self.n_features = config.n_features
        
        # 初始化参数
        self.mu = np.zeros((self.n_arms, self.n_features))
        self.A = np.array([np.eye(self.n_features) for _ in range(self.n_arms)])
        self.b = np.zeros((self.n_arms, self.n_features))
        
        # 统计信息
        self.n_pulls = np.zeros(self.n_arms)
        self.total_rewards = np.zeros(self.n_arms)
    
    def pick(self, x: np.ndarray, topk: int = 2) -> List[int]:
        """选择top-k策略"""
        ucb_values = []
        
        for arm in range(self.n_arms):
            if self.n_pulls[arm] == 0:
                ucb_values.append(float('inf'))
            else:
                # 计算UCB值
                mean_pred = np.dot(self.mu[arm], x)
                var_pred = np.dot(x, self.A[arm] @ x)
                ucb_value = mean_pred + self.config.alpha * np.sqrt(var_pred)
                ucb_values.append(ucb_value)
        
        # 选择top-k
        top_arms = np.argsort(ucb_values)[-topk:][::-1]
        return top_arms.tolist()
    
    def update(self, x: np.ndarray, k: int, reward: float):
        """更新参数"""
        self.n_pulls[k] += 1
        self.total_rewards[k] += reward
        
        self.b[k] += reward * x
        self.A[k] += np.outer(x, x)
        
        # 更新均值
        self.mu[k] = np.linalg.solve(self.A[k], self.b[k])

def create_selector(selector_type: str = 'thompson', config: Optional[ThompsonSelectorConfig] = None) -> Any:
    """
    创建选择器
    
    Args:
        selector_type: 选择器类型 ('thompson' or 'linucb')
        config: 配置参数
        
    Returns:
        选择器实例
    """
    if config is None:
        config = ThompsonSelectorConfig()
    
    if selector_type == 'thompson':
        return ThompsonSelector(config)
    elif selector_type == 'linucb':
        return LinUCBSelector(config)
    else:
        raise ValueError(f"未知的选择器类型: {selector_type}")

def main():
    """主函数 - 演示选择器"""
    print("🚀 Thompson采样选择器演示")
    print("=" * 60)
    
    # 创建配置
    config = ThompsonSelectorConfig(
        n_arms=5,
        n_features=10,
        alpha=1.0,
        beta=1.0
    )
    
    # 创建选择器
    selector = ThompsonSelector(config)
    
    print(f"📊 选择器配置:")
    print(f"  臂数: {config.n_arms}")
    print(f"  特征维度: {config.n_features}")
    print(f"  噪声参数: {config.alpha}")
    print(f"  正则化参数: {config.beta}")
    
    # 模拟数据
    np.random.seed(42)
    n_samples = 1000
    
    print(f"\n🔄 模拟训练: {n_samples} 个样本")
    
    for i in range(n_samples):
        # 生成随机特征
        x = np.random.randn(config.n_features)
        
        # 选择策略
        if i < 50:  # 前50个样本随机选择
            k = np.random.randint(0, config.n_arms)
        else:
            selected_arms = selector.pick(x, topk=1)
            k = selected_arms[0]
        
        # 生成奖励
        true_reward = np.dot(x[:3], [1, -0.5, 0.3]) + np.random.normal(0, 0.1)
        reward = true_reward + np.random.normal(0, 0.05)
        
        # 更新选择器
        selector.update(x, k, reward)
        
        if i % 100 == 0:
            print(f"  样本 {i}: 选择臂 {k}, 奖励 {reward:.3f}")
    
    # 显示结果
    print(f"\n📊 训练结果:")
    stats = selector.get_arm_stats()
    for arm, stat in stats.items():
        print(f"  {arm}: 拉动次数 {stat['n_pulls']}, 平均奖励 {stat['avg_reward']:.3f}")
    
    # 测试选择
    print(f"\n🎯 测试选择:")
    test_x = np.random.randn(config.n_features)
    selected_arms = selector.pick(test_x, topk=3)
    print(f"  特征向量: {test_x[:5]}...")
    print(f"  选择的臂: {selected_arms}")
    
    # 获取期望奖励
    expected_rewards = selector.get_expected_rewards(test_x)
    print(f"  期望奖励: {expected_rewards}")
    
    # 获取臂排名
    rankings = selector.get_arm_rankings(test_x)
    print(f"  臂排名: {rankings}")
    
    # 保存状态
    selector.save_state('artifacts/selector_state.pkl')
    print(f"\n💾 状态已保存: artifacts/selector_state.pkl")
    
    # 加载状态测试
    new_selector = ThompsonSelector(config)
    new_selector.load_state('artifacts/selector_state.pkl')
    print(f"✅ 状态加载成功")
    
    print("\n" + "=" * 60)
    print("🎉 选择器演示完成！")

if __name__ == "__main__":
    main()
