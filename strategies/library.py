#!/usr/bin/env python3
"""
策略库
注册和管理所有策略
"""

from typing import List, Dict, Any, Optional
from strategies.base import Strategy, BuyAndHoldStrategy, MACDStrategy, RSIStrategy, \
    BollingerBandsStrategy, MomentumStrategy, MeanReversionStrategy, \
    TrendFollowingStrategy, VolatilityBreakoutStrategy, KDJStrategy

class StrategyLibrary:
    """策略库管理器"""
    
    def __init__(self):
        self._strategies: Dict[str, Strategy] = {}
        self._register_default_strategies()
    
    def _register_default_strategies(self):
        """注册默认策略"""
        # 注册所有策略
        strategies = [
            BuyAndHoldStrategy(),
            MACDStrategy(),
            RSIStrategy(),
            BollingerBandsStrategy(),
            MomentumStrategy(),
            MeanReversionStrategy(),
            TrendFollowingStrategy(),
            VolatilityBreakoutStrategy(),
            KDJStrategy()
        ]
        
        for strategy in strategies:
            self._strategies[strategy.name] = strategy
    
    def register_strategy(self, strategy: Strategy) -> None:
        """注册新策略"""
        self._strategies[strategy.name] = strategy
    
    def get_strategy(self, name: str) -> Optional[Strategy]:
        """获取策略"""
        return self._strategies.get(name)
    
    def get_all_strategies(self) -> List[Strategy]:
        """获取所有策略"""
        return list(self._strategies.values())
    
    def get_strategy_names(self) -> List[str]:
        """获取所有策略名称"""
        return list(self._strategies.keys())
    
    def get_strategies_by_tag(self, tag: str) -> List[Strategy]:
        """根据标签获取策略"""
        matching_strategies = []
        for strategy in self._strategies.values():
            if hasattr(strategy, 'meta') and 'reason_tags' in strategy.meta:
                if tag in strategy.meta['reason_tags']:
                    matching_strategies.append(strategy)
        return matching_strategies
    
    def get_strategies_by_confidence(self, min_confidence: float) -> List[Strategy]:
        """根据置信度获取策略"""
        matching_strategies = []
        for strategy in self._strategies.values():
            if hasattr(strategy, 'meta') and 'conf' in strategy.meta:
                if strategy.meta['conf'] >= min_confidence:
                    matching_strategies.append(strategy)
        return matching_strategies
    
    def get_strategy_info(self, name: str) -> Optional[Dict[str, Any]]:
        """获取策略信息"""
        strategy = self.get_strategy(name)
        if strategy is None:
            return None
        
        return {
            "name": strategy.name,
            "default_params": strategy.default_params,
            "description": getattr(strategy, '__doc__', ''),
            "tags": getattr(strategy, 'meta', {}).get('reason_tags', [])
        }
    
    def get_all_strategy_info(self) -> Dict[str, Dict[str, Any]]:
        """获取所有策略信息"""
        info = {}
        for name in self._strategies.keys():
            info[name] = self.get_strategy_info(name)
        return info
    
    def validate_strategy(self, name: str) -> bool:
        """验证策略是否存在"""
        return name in self._strategies
    
    def get_strategy_count(self) -> int:
        """获取策略数量"""
        return len(self._strategies)
    
    def clear_strategies(self) -> None:
        """清空所有策略"""
        self._strategies.clear()
    
    def remove_strategy(self, name: str) -> bool:
        """移除策略"""
        if name in self._strategies:
            del self._strategies[name]
            return True
        return False

# 全局策略库实例
_strategy_library = None

def get_strategy_library() -> StrategyLibrary:
    """获取全局策略库实例"""
    global _strategy_library
    if _strategy_library is None:
        _strategy_library = StrategyLibrary()
    return _strategy_library

def get_all_strategies() -> List[Strategy]:
    """获取所有策略"""
    return get_strategy_library().get_all_strategies()

def get_strategy_by_name(name: str) -> Optional[Strategy]:
    """根据名称获取策略"""
    return get_strategy_library().get_strategy(name)

def register_strategy(strategy: Strategy) -> None:
    """注册策略"""
    get_strategy_library().register_strategy(strategy)

def get_strategy_names() -> List[str]:
    """获取所有策略名称"""
    return get_strategy_library().get_strategy_names()

def get_strategies_by_tag(tag: str) -> List[Strategy]:
    """根据标签获取策略"""
    return get_strategy_library().get_strategies_by_tag(tag)

def get_strategies_by_confidence(min_confidence: float) -> List[Strategy]:
    """根据置信度获取策略"""
    return get_strategy_library().get_strategies_by_confidence(min_confidence)

def get_strategy_info(name: str) -> Optional[Dict[str, Any]]:
    """获取策略信息"""
    return get_strategy_library().get_strategy_info(name)

def get_all_strategy_info() -> Dict[str, Dict[str, Any]]:
    """获取所有策略信息"""
    return get_strategy_library().get_all_strategy_info()

def validate_strategy(name: str) -> bool:
    """验证策略是否存在"""
    return get_strategy_library().validate_strategy(name)

def get_strategy_count() -> int:
    """获取策略数量"""
    return get_strategy_library().get_strategy_count()

# 便捷函数
def list_strategies() -> None:
    """列出所有策略"""
    library = get_strategy_library()
    print("可用策略:")
    print("=" * 50)
    
    for strategy in library.get_all_strategies():
        info = library.get_strategy_info(strategy.name)
        print(f"名称: {info['name']}")
        print(f"描述: {info['description']}")
        print(f"标签: {', '.join(info['tags'])}")
        print(f"默认参数: {info['default_params']}")
        print("-" * 30)

def search_strategies(keyword: str) -> List[Strategy]:
    """搜索策略"""
    library = get_strategy_library()
    matching_strategies = []
    
    for strategy in library.get_all_strategies():
        # 在名称中搜索
        if keyword.lower() in strategy.name.lower():
            matching_strategies.append(strategy)
            continue
        
        # 在标签中搜索
        if hasattr(strategy, 'meta') and 'reason_tags' in strategy.meta:
            for tag in strategy.meta['reason_tags']:
                if keyword.lower() in tag.lower():
                    matching_strategies.append(strategy)
                    break
    
    return matching_strategies

def get_strategy_categories() -> Dict[str, List[str]]:
    """获取策略分类"""
    library = get_strategy_library()
    categories = {}
    
    for strategy in library.get_all_strategies():
        if hasattr(strategy, 'meta') and 'reason_tags' in strategy.meta:
            for tag in strategy.meta['reason_tags']:
                if tag not in categories:
                    categories[tag] = []
                categories[tag].append(strategy.name)
    
    return categories

def main():
    """主函数 - 演示策略库"""
    print("🚀 策略库演示")
    print("=" * 60)
    
    # 获取策略库
    library = get_strategy_library()
    
    # 显示所有策略
    print(f"📊 策略总数: {library.get_strategy_count()}")
    print(f"📋 策略名称: {library.get_strategy_names()}")
    
    # 显示策略信息
    print("\n📈 策略详情:")
    for name in library.get_strategy_names():
        info = library.get_strategy_info(name)
        print(f"\n🎯 {info['name']}:")
        print(f"  描述: {info['description']}")
        print(f"  标签: {', '.join(info['tags'])}")
        print(f"  参数: {info['default_params']}")
    
    # 按标签搜索
    print("\n🔍 按标签搜索:")
    trend_strategies = library.get_strategies_by_tag("trend_following")
    print(f"趋势跟踪策略: {[s.name for s in trend_strategies]}")
    
    mean_reversion_strategies = library.get_strategies_by_tag("mean_reversion")
    print(f"均值回归策略: {[s.name for s in mean_reversion_strategies]}")
    
    # 按置信度搜索
    print("\n📊 按置信度搜索:")
    high_conf_strategies = library.get_strategies_by_confidence(0.8)
    print(f"高置信度策略: {[s.name for s in high_conf_strategies]}")
    
    print("\n" + "=" * 60)
    print("🎉 策略库演示完成！")

if __name__ == "__main__":
    main()
