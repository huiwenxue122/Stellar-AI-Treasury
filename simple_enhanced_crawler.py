#!/usr/bin/env python3
"""
简化版增强Stellar数据爬取器 - 使用模拟数据演示系统功能
结合真实数据结构和完整的技术指标计算
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta, timezone
import json
import time
import os
from typing import Dict, List, Optional

# 配置
OUT_DIR = "./data"
LOOKBACK_DAYS = 30
RESOLUTION_SEC = 15 * 60  # 15分钟

# 支持的资产和基础价格
ASSETS_CONFIG = {
    "BTC": {"base_price": 43000.0, "volatility": 0.08},
    "ETH": {"base_price": 2300.0, "volatility": 0.07},
    "SOL": {"base_price": 95.0, "volatility": 0.09},
    "ARB": {"base_price": 1.2, "volatility": 0.12},
    "LINK": {"base_price": 12.5, "volatility": 0.10},
    "AAVE": {"base_price": 85.0, "volatility": 0.11},
    "LDO": {"base_price": 2.1, "volatility": 0.13},
    "FET": {"base_price": 0.45, "volatility": 0.15},
    "XLM": {"base_price": 0.12, "volatility": 0.05},
}

class SimpleEnhancedCrawler:
    """简化版增强Stellar数据爬取器"""
    
    def __init__(self):
        self.out_dir = OUT_DIR
        os.makedirs(self.out_dir, exist_ok=True)
    
    def generate_mock_data(self, asset_code: str, days: int = 30) -> pd.DataFrame:
        """生成模拟的Stellar数据"""
        print(f"  📊 生成 {asset_code} 数据...")
        
        config = ASSETS_CONFIG[asset_code]
        base_price = config["base_price"]
        volatility = config["volatility"]
        
        # 生成时间序列
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(days=days)
        
        # 15分钟间隔
        time_range = pd.date_range(start=start_time, end=end_time, freq='15T')
        
        # 生成价格数据
        np.random.seed(42 + hash(asset_code) % 1000)
        prices = []
        current_price = base_price
        
        for i in range(len(time_range)):
            # 随机游走
            daily_return = np.random.normal(0, volatility / np.sqrt(96))  # 15分钟波动率
            current_price *= (1 + daily_return)
            prices.append(current_price)
        
        # 创建OHLCV数据
        data = []
        for i, (timestamp, price) in enumerate(zip(time_range, prices)):
            # 生成OHLC
            high = price * (1 + abs(np.random.normal(0, 0.01)))
            low = price * (1 - abs(np.random.normal(0, 0.01)))
            open_price = prices[i-1] if i > 0 else price
            close = price
            
            # 生成成交量
            volume = np.random.uniform(1000, 10000)
            
            data.append({
                'ts': timestamp,
                'open': open_price,
                'high': high,
                'low': low,
                'close': close,
                'base_volume': volume,
                'counter_volume': volume * price,
                'num_trades': np.random.randint(1, 10),
                'base_code': asset_code,
                'base_issuer': 'MOCK_ISSUER',
                'counter_code': 'USDC',
                'counter_issuer': 'MOCK_USDC_ISSUER',
                'source': 'mock_stellar_dex'
            })
        
        df = pd.DataFrame(data)
        df['ts'] = pd.to_datetime(df['ts'])
        df = df.set_index('ts')
        
        print(f"    ✅ {asset_code}: {len(df)} 条记录")
        return df
    
    def calculate_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """计算技术指标"""
        if df.empty or 'close' not in df.columns:
            return df
        
        print(f"    🔧 计算技术指标...")
        
        close_prices = df['close']
        
        # 移动平均线
        df['SMA_5'] = close_prices.rolling(window=5).mean()
        df['SMA_10'] = close_prices.rolling(window=10).mean()
        df['SMA_20'] = close_prices.rolling(window=20).mean()
        
        df['EMA_12'] = close_prices.ewm(span=12, adjust=False).mean()
        df['EMA_26'] = close_prices.ewm(span=26, adjust=False).mean()
        
        # RSI
        df['RSI'] = self._calculate_rsi(close_prices, 14)
        
        # MACD
        df['MACD'] = df['EMA_12'] - df['EMA_26']
        df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
        df['MACD_Histogram'] = df['MACD'] - df['MACD_Signal']
        
        # 布林带
        df['BB_Middle'] = close_prices.rolling(window=20).mean()
        bb_std = close_prices.rolling(window=20).std()
        df['BB_Upper'] = df['BB_Middle'] + (bb_std * 2)
        df['BB_Lower'] = df['BB_Middle'] - (bb_std * 2)
        df['BB_Width'] = (df['BB_Upper'] - df['BB_Lower']) / df['BB_Middle']
        df['BB_Position'] = (close_prices - df['BB_Lower']) / (df['BB_Upper'] - df['BB_Lower'])
        
        # 波动率
        df['Daily_Return'] = close_prices.pct_change()
        df['Volatility_7'] = df['Daily_Return'].rolling(window=7).std() * np.sqrt(252)
        df['Volatility_21'] = df['Daily_Return'].rolling(window=21).std() * np.sqrt(252)
        
        # 动量
        df['Momentum_5'] = close_prices.pct_change(5)
        df['Momentum_10'] = close_prices.pct_change(10)
        df['Momentum_20'] = close_prices.pct_change(20)
        
        # 成交量指标
        if 'base_volume' in df.columns:
            df['Volume_SMA_10'] = df['base_volume'].rolling(window=10).mean()
            df['Volume_Ratio'] = df['base_volume'] / df['Volume_SMA_10']
        
        # 趋势指标
        df['Trend_5'] = (close_prices - close_prices.shift(5)) / close_prices.shift(5)
        df['Trend_10'] = (close_prices - close_prices.shift(10)) / close_prices.shift(10)
        df['Trend_20'] = (close_prices - close_prices.shift(20)) / close_prices.shift(20)
        
        # 强化学习特征
        df['Action_Signal'] = self._calculate_action_signals(df)
        df['Reward_Proxy'] = df['Daily_Return'] * 100
        
        print(f"    ✅ 技术指标计算完成")
        return df.dropna()
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """计算RSI"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def _calculate_action_signals(self, df: pd.DataFrame) -> pd.Series:
        """计算动作信号"""
        signals = []
        
        for i in range(len(df)):
            if i < 20:
                signals.append(0)  # HOLD
                continue
            
            current_price = df['close'].iloc[i]
            sma_20 = df['SMA_20'].iloc[i]
            rsi = df['RSI'].iloc[i]
            macd = df['MACD'].iloc[i]
            macd_signal = df['MACD_Signal'].iloc[i]
            
            signal = 0  # HOLD
            
            # 买入信号
            if (current_price > sma_20 and 
                rsi < 70 and 
                macd > macd_signal and 
                df['Daily_Return'].iloc[i] > 0):
                signal = 1  # BUY
            
            # 卖出信号
            elif (current_price < sma_20 and 
                  rsi > 30 and 
                  macd < macd_signal and 
                  df['Daily_Return'].iloc[i] < 0):
                signal = -1  # SELL
            
            signals.append(signal)
        
        return pd.Series(signals, index=df.index)
    
    def create_ml_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """创建ML特征"""
        print(f"    🤖 创建ML特征...")
        
        features_df = df.copy()
        
        # 价格特征
        features_df['price_change_1d'] = df['close'].pct_change(1)
        features_df['price_change_3d'] = df['close'].pct_change(3)
        features_df['price_change_7d'] = df['close'].pct_change(7)
        
        # 技术指标特征
        features_df['rsi_overbought'] = (df['RSI'] > 70).astype(int)
        features_df['rsi_oversold'] = (df['RSI'] < 30).astype(int)
        features_df['macd_bullish'] = (df['MACD'] > df['MACD_Signal']).astype(int)
        features_df['macd_bearish'] = (df['MACD'] < df['MACD_Signal']).astype(int)
        
        # 波动率特征
        features_df['volatility_regime'] = pd.cut(df['Volatility_21'], 
                                                bins=[0, 0.2, 0.5, 1.0, float('inf')], 
                                                labels=['low', 'medium', 'high', 'extreme'])
        
        # 趋势特征
        features_df['trend_strength'] = abs(df['Trend_20'])
        features_df['trend_direction'] = np.sign(df['Trend_20'])
        
        # 成交量特征
        if 'base_volume' in df.columns:
            features_df['volume_spike'] = (df['Volume_Ratio'] > 2).astype(int)
            features_df['volume_trend'] = df['base_volume'].pct_change(5)
        
        # 标签数据
        features_df['future_return_1d'] = df['close'].shift(-1) / df['close'] - 1
        features_df['future_return_3d'] = df['close'].shift(-3) / df['close'] - 1
        features_df['future_return_7d'] = df['close'].shift(-7) / df['close'] - 1
        
        # 分类标签
        features_df['label_1d'] = 0
        features_df['label_3d'] = 0
        features_df['label_7d'] = 0
        
        valid_1d = features_df['future_return_1d'].notna()
        valid_3d = features_df['future_return_3d'].notna()
        valid_7d = features_df['future_return_7d'].notna()
        
        features_df.loc[valid_1d, 'label_1d'] = (features_df.loc[valid_1d, 'future_return_1d'] > 0.01).astype(int)
        features_df.loc[valid_3d, 'label_3d'] = (features_df.loc[valid_3d, 'future_return_3d'] > 0.03).astype(int)
        features_df.loc[valid_7d, 'label_7d'] = (features_df.loc[valid_7d, 'future_return_7d'] > 0.05).astype(int)
        
        print(f"    ✅ ML特征创建完成")
        return features_df
    
    def save_data(self, all_data: Dict[str, pd.DataFrame]):
        """保存数据"""
        print(f"    💾 保存数据...")
        
        # 保存每个资产的CSV
        for asset, df in all_data.items():
            csv_path = os.path.join(self.out_dir, f"stellar_ohlc_15m_{asset}.csv")
            df.to_csv(csv_path)
            print(f"    ✅ {asset} CSV -> {csv_path}")
        
        # 保存合并的CSV
        if all_data:
            merged = pd.concat(all_data.values(), ignore_index=True)
            csv_path = os.path.join(self.out_dir, "stellar_ohlc_15m_all.csv")
            merged.to_csv(csv_path, index=False)
            print(f"    ✅ 合并CSV -> {csv_path}")
        
        # 保存增强JSON数据
        json_path = os.path.join(self.out_dir, "stellar_enhanced_data.json")
        self._save_enhanced_json(all_data, json_path)
        print(f"    ✅ JSON -> {json_path}")
    
    def _save_enhanced_json(self, all_data: Dict[str, pd.DataFrame], json_path: str):
        """保存增强JSON数据"""
        enhanced_data = {}
        
        for asset, df in all_data.items():
            enhanced_data[asset] = {
                'data': df.to_dict('records'),
                'index': df.index.strftime('%Y-%m-%d %H:%M:%S').tolist(),
                'columns': df.columns.tolist()
            }
        
        with open(json_path, 'w') as f:
            json.dump({
                'timestamp': time.time(),
                'data': enhanced_data,
                'metadata': {
                    'total_assets': len(all_data),
                    'assets': list(all_data.keys()),
                    'total_records': sum(len(df) for df in all_data.values()),
                    'date_range': {
                        'start': min(df.index.min() for df in all_data.values()).isoformat(),
                        'end': max(df.index.max() for df in all_data.values()).isoformat()
                    },
                    'features': list(all_data[list(all_data.keys())[0]].columns) if all_data else [],
                    'data_type': 'mock_stellar_data_with_features'
                }
            }, f, indent=2, default=str)

def main():
    """主函数"""
    print("🚀 简化版增强Stellar数据爬取器")
    print("=" * 60)
    
    crawler = SimpleEnhancedCrawler()
    
    # 生成所有资产的数据
    all_data = {}
    
    for asset_code in ASSETS_CONFIG.keys():
        print(f"\n📊 处理资产: {asset_code}")
        
        # 生成模拟数据
        df = crawler.generate_mock_data(asset_code, LOOKBACK_DAYS)
        
        if not df.empty:
            # 计算技术指标
            df = crawler.calculate_technical_indicators(df)
            
            # 创建ML特征
            df = crawler.create_ml_features(df)
            
            all_data[asset_code] = df
            print(f"    ✅ {asset_code}: {len(df)} 条记录，{len(df.columns)} 个特征")
        else:
            print(f"    ⚠️  {asset_code}: 无数据")
    
    # 保存数据
    if all_data:
        crawler.save_data(all_data)
        
        # 显示数据概览
        print(f"\n📊 数据概览:")
        print(f"  资产数: {len(all_data)}")
        print(f"  资产列表: {list(all_data.keys())}")
        
        total_records = sum(len(df) for df in all_data.values())
        print(f"  总记录数: {total_records}")
        
        for asset, df in all_data.items():
            print(f"\n📈 {asset} 数据:")
            print(f"  记录数: {len(df)}")
            if not df.empty:
                print(f"  时间范围: {df.index.min()} 到 {df.index.max()}")
                print(f"  特征数: {len(df.columns)}")
                print(f"  最新价格: ${df['close'].iloc[-1]:.4f}")
                print(f"  最新RSI: {df['RSI'].iloc[-1]:.2f}")
                print(f"  最新波动率: {df['Volatility_21'].iloc[-1]:.2f}")
                print(f"  最新动作信号: {df['Action_Signal'].iloc[-1]}")
    else:
        print("❌ 未能生成任何数据")
    
    print("\n" + "=" * 60)
    print("🎉 简化版增强Stellar数据生成完成！")
    print("💡 模拟数据 + 技术指标 + ML特征")
    print("📁 数据文件保存在 ./data/ 目录")

if __name__ == "__main__":
    main()
