#!/usr/bin/env python3
"""
真实Stellar数据爬取器 - 获取真实的Stellar DEX数据
"""

import asyncio
import aiohttp
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, timezone
import json
import time
import os
from typing import Dict, List, Optional

# 配置
HORIZON_URL = "https://horizon.stellar.org"
OUT_DIR = "./real_data"
LOOKBACK_DAYS = 30
RESOLUTION_SEC = 15 * 60  # 15分钟

# 真实Stellar资产配置（主网上实际存在的资产）
REAL_STELLAR_ASSETS = {
    "XLM": {"type": "native", "issuer": None},
    "USDC": {"type": "credit_alphanum4", "issuer": "GBBD47IF6I2X6ZJMPRC7JIBMQJSQADPDA3BZX4A5QW4NRS6R6ZQBTNAE"},
    "USDT": {"type": "credit_alphanum4", "issuer": "GCQTGZQQ5G4PTM2GL7CDIFKUBIPEC52BROAQIAPW53XBRJVN6ZJVTG6V"},
    "BTC": {"type": "credit_alphanum4", "issuer": "GAUTUYY2THLF7SGITDFMXJVYH3LHDSMGEAKSBU267M2K7A3W543CKUEF"},
    "ETH": {"type": "credit_alphanum4", "issuer": "GBDEVU63Y6NTHJQQZIKVTC23NWLQVP3WJ2RI2OTSJTNYOIGICST6DUXR"},
}

class RealStellarCrawler:
    """真实Stellar数据爬取器"""
    
    def __init__(self):
        self.out_dir = OUT_DIR
        os.makedirs(self.out_dir, exist_ok=True)
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={"User-Agent": "stellar-real-crawler/1.0"}
        )
        return self
    
    async def __aexit__(self, exc_type, exc, tb):
        if self.session:
            await self.session.close()
    
    async def crawl_real_data(self) -> Dict[str, pd.DataFrame]:
        """爬取真实Stellar数据"""
        print("🔍 爬取真实Stellar DEX数据...")
        
        all_data = {}
        
        # 获取时间范围
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(days=LOOKBACK_DAYS)
        start_ms = int(start_time.timestamp() * 1000)
        end_ms = int(end_time.timestamp() * 1000)
        
        print(f"  📅 时间范围: {start_time} 到 {end_time}")
        print(f"  📊 分辨率: {RESOLUTION_SEC} 秒")
        
        for asset_code, asset_info in REAL_STELLAR_ASSETS.items():
            print(f"\n📈 爬取 {asset_code} 数据...")
            
            try:
                # 获取交易聚合数据
                df = await self._fetch_trade_aggregations(asset_code, asset_info, start_ms, end_ms)
                
                if not df.empty:
                    # 计算技术指标
                    df = self._calculate_technical_indicators(df)
                    
                    # 创建ML特征
                    df = self._create_ml_features(df)
                    
                    all_data[asset_code] = df
                    print(f"    ✅ {asset_code}: {len(df)} 条记录")
                else:
                    print(f"    ⚠️  {asset_code}: 无交易数据")
                
                # 避免API限制
                await asyncio.sleep(0.5)
                
            except Exception as e:
                print(f"    ❌ {asset_code}: 错误 - {e}")
        
        return all_data
    
    async def _fetch_trade_aggregations(self, asset_code: str, asset_info: Dict, 
                                     start_ms: int, end_ms: int) -> pd.DataFrame:
        """获取交易聚合数据"""
        try:
            url = f"{HORIZON_URL}/trade_aggregations"
            
            # 构建参数
            params = {
                "start_time": start_ms,
                "end_time": end_ms,
                "resolution": RESOLUTION_SEC,
                "limit": 200
            }
            
            # 设置base资产参数
            if asset_info["type"] == "native":
                params["base_asset_type"] = "native"
            else:
                params["base_asset_type"] = asset_info["type"]
                params["base_asset_code"] = asset_code
                params["base_asset_issuer"] = asset_info["issuer"]
            
            # 设置counter资产参数（使用XLM作为计价）
            params["counter_asset_type"] = "native"
            
            print(f"    🔍 请求URL: {url}")
            print(f"    📋 参数: {params}")
            
            async with self.session.get(url, params=params) as resp:
                print(f"    📊 响应状态: {resp.status}")
                
                if resp.status == 200:
                    data = await resp.json()
                    records = data.get("_embedded", {}).get("records", [])
                    
                    if records:
                        df = pd.DataFrame(records)
                        df = df.rename(columns={
                            "timestamp": "ts",
                            "base_volume": "volume"
                        })
                        df["ts"] = pd.to_datetime(df["ts"], unit="ms")
                        df = df.set_index("ts")
                        df = df.sort_index()
                        
                        print(f"    📈 获取到 {len(df)} 条交易记录")
                        return df
                    else:
                        print(f"    ⚠️  无交易记录")
                        return pd.DataFrame()
                else:
                    print(f"    ❌ HTTP {resp.status} 错误")
                    return pd.DataFrame()
                    
        except Exception as e:
            print(f"    ❌ 请求失败: {e}")
            return pd.DataFrame()
    
    def _calculate_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
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
        
        # 波动率
        df['Daily_Return'] = close_prices.pct_change()
        df['Volatility_7'] = df['Daily_Return'].rolling(window=7).std() * np.sqrt(252)
        df['Volatility_21'] = df['Daily_Return'].rolling(window=21).std() * np.sqrt(252)
        
        # 动量
        df['Momentum_5'] = close_prices.pct_change(5)
        df['Momentum_10'] = close_prices.pct_change(10)
        df['Momentum_20'] = close_prices.pct_change(20)
        
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
    
    def _create_ml_features(self, df: pd.DataFrame) -> pd.DataFrame:
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
        print(f"    💾 保存真实数据...")
        
        # 保存每个资产的CSV
        for asset, df in all_data.items():
            csv_path = os.path.join(self.out_dir, f"real_stellar_{asset}.csv")
            df.to_csv(csv_path)
            print(f"    ✅ {asset} CSV -> {csv_path}")
        
        # 保存合并的CSV
        if all_data:
            merged = pd.concat(all_data.values(), ignore_index=True)
            csv_path = os.path.join(self.out_dir, "real_stellar_all.csv")
            merged.to_csv(csv_path, index=False)
            print(f"    ✅ 合并CSV -> {csv_path}")
        
        # 保存JSON数据
        json_path = os.path.join(self.out_dir, "real_stellar_data.json")
        self._save_json(all_data, json_path)
        print(f"    ✅ JSON -> {json_path}")
    
    def _save_json(self, all_data: Dict[str, pd.DataFrame], json_path: str):
        """保存JSON数据"""
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
                    'data_type': 'real_stellar_data_with_features'
                }
            }, f, indent=2, default=str)

async def main():
    """主函数"""
    print("🚀 真实Stellar数据爬取器")
    print("=" * 60)
    
    async with RealStellarCrawler() as crawler:
        # 爬取真实数据
        data = await crawler.crawl_real_data()
        
        if data:
            # 保存数据
            crawler.save_data(data)
            
            # 显示数据概览
            print(f"\n📊 真实数据概览:")
            print(f"  资产数: {len(data)}")
            print(f"  资产列表: {list(data.keys())}")
            
            total_records = sum(len(df) for df in data.values())
            print(f"  总记录数: {total_records}")
            
            for asset, df in data.items():
                print(f"\n📈 {asset} 真实数据:")
                print(f"  记录数: {len(df)}")
                if not df.empty:
                    print(f"  时间范围: {df.index.min()} 到 {df.index.max()}")
                    print(f"  特征数: {len(df.columns)}")
                    print(f"  最新价格: ${df['close'].iloc[-1]:.4f}")
                    print(f"  最新RSI: {df['RSI'].iloc[-1]:.2f}")
                    print(f"  最新波动率: {df['Volatility_21'].iloc[-1]:.2f}")
        else:
            print("❌ 未能获取到真实数据")
    
    print("\n" + "=" * 60)
    print("🎉 真实Stellar数据爬取完成！")
    print("💡 真实数据 + 技术指标 + ML特征")

if __name__ == "__main__":
    asyncio.run(main())
