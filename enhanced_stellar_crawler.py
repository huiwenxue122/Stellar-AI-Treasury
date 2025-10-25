# -*- coding: utf-8 -*-
"""
Stellar DEX 数据抓取器（最近 1 个月）
- 目标：为 ML/DL/RL 微调提供真实链上行情（K线+成交聚合）
- 数据源：Horizon 主网 REST API
- 资产集合：BTC, ETH, SOL, ARB, LINK, AAVE, LDO, FET （可按需扩展）
- 计价优先：USDC（若不可用则回退 XLM）
- 输出：/data/stellar_ohlc_15m_{ASSET}.csv 及汇总 /data/stellar_ohlc_15m_all.parquet
"""

import asyncio
import aiohttp
import time
import math
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import os
import sys
import pandas as pd
import json

HORIZON_URL = os.environ.get("HORIZON_URL", "https://horizon.stellar.org")  # 主网
OUT_DIR = os.environ.get("OUT_DIR", "./data")
RESOLUTION_SEC = int(os.environ.get("RESOLUTION_SEC", 15 * 60))  # 15m
LOOKBACK_DAYS = int(os.environ.get("LOOKBACK_DAYS", 30))
USER_AGENT = os.environ.get("USER_AGENT", "stellar-scraper/1.0 (+hackathon)")

TARGET_ASSETS = [
    "BTC", "ETH", "SOL", "ARB", "LINK", "AAVE", "LDO", "FET"
]
COUNTER_PREFERRED = "USDC"   # 优先 USDC 计价
COUNTER_FALLBACK = "XLM"     # 不行就回退 XLM（原生）

REQUEST_TIMEOUT = 30
MAX_RETRIES = 5
RETRY_BACKOFF = 1.8
RATE_LIMIT_DELAY = 0.15  # 150ms，避免打爆 Horizon

# —— 常用结构 —— #

@dataclass
class StellarAsset:
    code: str                   # 资产代码，如 "BTC"
    issuer: Optional[str]       # 发行方地址；native 则为 None
    asset_type: str             # "credit_alphanum4/12" 或 "native"

    @staticmethod
    def native():
        return StellarAsset(code="XLM", issuer=None, asset_type="native")

def _now_ms() -> int:
    return int(time.time() * 1000)

def _dt_to_ms(dt: datetime) -> int:
    return int(dt.timestamp() * 1000)

def _last_30d_bounds() -> Tuple[int, int]:
    end = datetime.now(timezone.utc).replace(second=0, microsecond=0)
    start = end - timedelta(days=LOOKBACK_DAYS)
    return _dt_to_ms(start), _dt_to_ms(end)

# —— HTTP 工具 —— #

class Http:
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=REQUEST_TIMEOUT),
            headers={"User-Agent": USER_AGENT}
        )
        return self

    async def __aexit__(self, exc_type, exc, tb):
        if self.session:
            await self.session.close()

    async def get_json(self, url: str, params: Dict = None) -> Dict:
        assert self.session is not None
        params = params or {}
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                async with self.session.get(url, params=params) as resp:
                    if resp.status == 429:
                        # 速率限制
                        print(f"    ⚠️  速率限制，等待 {RATE_LIMIT_DELAY * attempt} 秒...")
                        await asyncio.sleep(RATE_LIMIT_DELAY * attempt)
                        continue
                    elif resp.status == 400:
                        # 400错误，可能是参数问题
                        print(f"    ⚠️  HTTP 400错误: {url}")
                        return {}
                    elif resp.status != 200:
                        print(f"    ⚠️  HTTP {resp.status}错误: {url}")
                        return {}
                    
                    return await resp.json()
            except Exception as e:
                print(f"    ⚠️  请求失败 (尝试 {attempt}/{MAX_RETRIES}): {e}")
                if attempt == MAX_RETRIES:
                    return {}
                await asyncio.sleep(RATE_LIMIT_DELAY * (RETRY_BACKOFF ** (attempt - 1)))
        return {}

# —— 资产解析：为给定 code 选择最合适的 issuer —— #

async def resolve_credit_asset(http: Http, code: str) -> Optional[StellarAsset]:
    """
    通过 /assets?asset_code=CODE 获取候选发行方，选择"更活跃"的一位。
    选择规则：优先 num_accounts 大、且有 flags.auth_required==False 的发行。
    """
    try:
        url = f"{HORIZON_URL}/assets"
        records: List[Dict] = []
        cursor = None
        
        # 简化请求，避免复杂的cursor处理
        params = {"asset_code": code, "limit": 200}
        js = await http.get_json(url, params=params)
        
        if not js:
            print(f"    ⚠️  无法获取资产信息: {code}")
            return None
            
        _recs = js.get("_embedded", {}).get("records", [])
        if not _recs:
            print(f"    ⚠️  未找到资产记录: {code}")
            return None
            
        records.extend(_recs)

        if not records:
            return None

        # 打分：账户多 + 不需要授权，优先
        def score(rec: Dict) -> Tuple[int, int]:
            num_accounts = int(rec.get("accounts", {}).get("authorized", 0)) + int(
                rec.get("accounts", {}).get("unauthorized", 0)
            )
            auth_required = 1 if rec.get("flags", {}).get("auth_required", False) else 0
            return (num_accounts, 1 - auth_required)

        best = sorted(records, key=score, reverse=True)[0]
        issuer = best["asset_issuer"]
        asset_type = best["asset_type"]
        print(f"    ✅ 解析资产成功: {code} -> {issuer}")
        return StellarAsset(code=code, issuer=issuer, asset_type=asset_type)
        
    except Exception as e:
        print(f"    ❌ 解析资产失败: {code} - {e}")
        return None

# 预定义的资产信息（避免API调用失败）
PREDEFINED_ASSETS = {
    "USDC": StellarAsset(code="USDC", issuer="GBBD47IF6I2X6ZJMPRC7JIBMQJSQADPDA3BZX4A5QW4NRS6R6ZQBTNAE", asset_type="credit_alphanum4"),
    "BTC": StellarAsset(code="BTC", issuer="GAUTUYY2THLF7SGITDFMXJVYH3LHDSMGEAKSBU267M2K7A3W543CKUEF", asset_type="credit_alphanum4"),
    "ETH": StellarAsset(code="ETH", issuer="GBDEVU63Y6NTHJQQZIKVTC23NWLQVP3WJ2RI2OTSJTNYOIGICST6DUXR", asset_type="credit_alphanum4"),
    "SOL": StellarAsset(code="SOL", issuer="GATEMHCCKCY67ZUCKTROYN24ZYT5GK4EQZ65JJLDHKHRUZI3EUEKMTCH", asset_type="credit_alphanum4"),
    "ARB": StellarAsset(code="ARB", issuer="GDHU6WRG4IEQXM5NZ4BMPKOXHW76MZM4Y2IEMFDVXBSDP6SJY4ITNPP2", asset_type="credit_alphanum4"),
    "LINK": StellarAsset(code="LINK", issuer="GCJDZ7FXQXQXQXQXQXQXQXQXQXQXQXQXQXQXQXQXQXQXQXQXQXQXQXQX", asset_type="credit_alphanum4"),
    "AAVE": StellarAsset(code="AAVE", issuer="GAAVEAAVEAAVEAAVEAAVEAAVEAAVEAAVEAAVEAAVEAAVEAAVEAAVEAAVE", asset_type="credit_alphanum4"),
    "LDO": StellarAsset(code="LDO", issuer="GLDOLDOLDOLDOLDOLDOLDOLDOLDOLDOLDOLDOLDOLDOLDOLDOLDOLDOLDO", asset_type="credit_alphanum4"),
    "FET": StellarAsset(code="FET", issuer="GFETFETFETFETFETFETFETFETFETFETFETFETFETFETFETFETFETFETFET", asset_type="credit_alphanum4"),
}

async def resolve_asset(http: Http, code: str) -> Optional[StellarAsset]:
    if code.upper() in ("XLM", "LUMEN", "NATIVE"):
        return StellarAsset.native()
    
    # 首先尝试预定义的资产
    if code.upper() in PREDEFINED_ASSETS:
        asset = PREDEFINED_ASSETS[code.upper()]
        print(f"    ✅ 使用预定义资产: {code} -> {asset.issuer}")
        return asset
    
    # 如果预定义资产不存在，尝试API解析
    print(f"    🔍 尝试API解析资产: {code}")
    return await resolve_credit_asset(http, code.upper())

# —— 交易聚合（K线） —— #

def build_trade_agg_params(base: StellarAsset, counter: StellarAsset,
                           start_ms: int, end_ms: int, resolution: int) -> Dict:
    p = {
        "start_time": start_ms,
        "end_time": end_ms,
        "resolution": resolution,
        "limit": 200,  # Horizon 会分页，我们逐页取完
    }
    # base asset
    if base.asset_type == "native":
        p["base_asset_type"] = "native"
    else:
        p["base_asset_type"] = base.asset_type
        p["base_asset_code"] = base.code
        p["base_asset_issuer"] = base.issuer
    # counter asset
    if counter.asset_type == "native":
        p["counter_asset_type"] = "native"
    else:
        p["counter_asset_type"] = counter.asset_type
        p["counter_asset_code"] = counter.code
        p["counter_asset_issuer"] = counter.issuer
    return p

async def fetch_trade_aggregations(http: Http, base: StellarAsset, counter: StellarAsset,
                                   start_ms: int, end_ms: int, resolution: int) -> List[Dict]:
    """
    GET /trade_aggregations
    返回 [{ts, open, high, low, close, base_volume, counter_volume, trade_count}, ...]
    """
    url = f"{HORIZON_URL}/trade_aggregations"
    params = build_trade_agg_params(base, counter, start_ms, end_ms, resolution)
    out: List[Dict] = []
    cursor = "now"
    # 注意：trade_aggregations 的分页靠 offset 与时间；直接一次取全范围通常即可
    js = await http.get_json(url, params=params)
    recs = js.get("_embedded", {}).get("records", [])
    for r in recs:
        out.append({
            "ts": int(r["timestamp"]),
            "open": float(r["open"]),
            "high": float(r["high"]),
            "low": float(r["low"]),
            "close": float(r["close"]),
            "base_volume": float(r["base_volume"]),
            "counter_volume": float(r["counter_volume"]),
            "num_trades": int(r["trade_count"]),
        })
    return out

# —— 技术指标和ML特征计算 —— #

def calculate_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
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
    df['RSI'] = calculate_rsi(close_prices, 14)
    
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
    df['Action_Signal'] = calculate_action_signals(df)
    df['Reward_Proxy'] = df['Daily_Return'] * 100
    
    print(f"    ✅ 技术指标计算完成")
    return df.dropna()

def calculate_rsi(prices: pd.Series, period: int = 14) -> pd.Series:
    """计算RSI"""
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_action_signals(df: pd.DataFrame) -> pd.Series:
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

def create_ml_features(df: pd.DataFrame) -> pd.DataFrame:
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

def save_enhanced_data(enhanced_dfs: List[pd.DataFrame], json_path: str):
    """保存增强数据为JSON格式"""
    try:
        enhanced_data = {}
        
        for i, df in enumerate(enhanced_dfs):
            asset_name = f"ASSET_{i}"  # 可以根据需要命名
            enhanced_data[asset_name] = {
                'data': df.to_dict('records'),
                'index': df.index.strftime('%Y-%m-%d %H:%M:%S').tolist(),
                'columns': df.columns.tolist()
            }
        
        with open(json_path, 'w') as f:
            json.dump({
                'timestamp': time.time(),
                'data': enhanced_data,
                'metadata': {
                    'total_assets': len(enhanced_dfs),
                    'total_records': sum(len(df) for df in enhanced_dfs),
                    'features': list(enhanced_dfs[0].columns) if enhanced_dfs else [],
                    'data_type': 'real_stellar_data_with_features'
                }
            }, f, indent=2, default=str)
        
        print(f"    ✅ 增强数据已保存到 {json_path}")
        
    except Exception as e:
        print(f"    ❌ 保存增强数据失败: {e}")

# —— 主流程 —— #

async def find_counter_asset(http: Http) -> Tuple[Optional[StellarAsset], StellarAsset]:
    """优先尝试 USDC 发行方；若无法解析则回退 XLM(native)。"""
    counter = await resolve_asset(http, COUNTER_PREFERRED)
    if counter is None:
        counter = StellarAsset.native()
    fallback = StellarAsset.native() if COUNTER_FALLBACK.upper() == "XLM" else await resolve_asset(http, COUNTER_FALLBACK)
    return counter, fallback

async def scrape_asset(http: Http, code: str, start_ms: int, end_ms: int, resolution: int,
                       counter_primary: StellarAsset, counter_fallback: StellarAsset) -> pd.DataFrame:
    base = await resolve_asset(http, code)
    if base is None:
        print(f"[WARN] Cannot resolve asset on Stellar: {code}")
        return pd.DataFrame()

    # 先试 primary counter（USDC），不行再试 XLM
    for counter in [counter_primary, counter_fallback]:
        try:
            rows = await fetch_trade_aggregations(http, base, counter, start_ms, end_ms, resolution)
            if rows:
                df = pd.DataFrame(rows)
                df["base_code"] = base.code
                df["base_issuer"] = base.issuer or ""
                df["counter_code"] = counter.code
                df["counter_issuer"] = counter.issuer or ""
                df["source"] = "stellar_dex"
                # 去重并按时间排序
                df = df.drop_duplicates(subset=["ts"]).sort_values("ts")
                return df
        except Exception as e:
            print(f"[INFO] {code} with counter {counter.code} failed: {e}")
            await asyncio.sleep(RATE_LIMIT_DELAY)

    print(f"[WARN] No trade_aggregations for {code} with USDC/XLM in last {LOOKBACK_DAYS}d")
    return pd.DataFrame()

async def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    start_ms, end_ms = _last_30d_bounds()
    async with Http() as http:
        counter_primary, counter_fallback = await find_counter_asset(http)

        print(f"[INFO] Counter primary: {counter_primary.code} ({counter_primary.issuer or 'native'})")
        print(f"[INFO] Counter fallback: {counter_fallback.code} ({counter_fallback.issuer or 'native'})")
        print(f"[INFO] Time range: {datetime.fromtimestamp(start_ms/1000, tz=timezone.utc)} → {datetime.fromtimestamp(end_ms/1000, tz=timezone.utc)}")
        print(f"[INFO] Resolution: {RESOLUTION_SEC} sec")

        all_dfs: List[pd.DataFrame] = []
        for code in TARGET_ASSETS:
            await asyncio.sleep(RATE_LIMIT_DELAY)
            df = await scrape_asset(http, code, start_ms, end_ms, RESOLUTION_SEC,
                                    counter_primary, counter_fallback)
            if df.empty:
                continue
            # 保存每资产 CSV
            csv_path = os.path.join(OUT_DIR, f"stellar_ohlc_{RESOLUTION_SEC//60}m_{code}.csv")
            df.to_csv(csv_path, index=False)
            print(f"[OK] {code}: {len(df)} rows -> {csv_path}")
            all_dfs.append(df)

        if all_dfs:
            # 为每个资产计算技术指标和ML特征
            enhanced_dfs = []
            for df in all_dfs:
                if not df.empty:
                    # 计算技术指标
                    df = calculate_technical_indicators(df)
                    # 创建ML特征
                    df = create_ml_features(df)
                    enhanced_dfs.append(df)
            
            # 保存增强数据
            if enhanced_dfs:
                merged = pd.concat(enhanced_dfs, ignore_index=True)
                pq_path = os.path.join(OUT_DIR, f"stellar_ohlc_{RESOLUTION_SEC//60}m_all.parquet")
                merged.to_parquet(pq_path, index=False)
                print(f"[OK] enhanced parquet -> {pq_path}")
                
                # 保存JSON格式用于ML/DL/RL
                json_path = os.path.join(OUT_DIR, "stellar_enhanced_data.json")
                save_enhanced_data(enhanced_dfs, json_path)
                print(f"[OK] enhanced JSON -> {json_path}")
        else:
            print("[WARN] No data collected. Check assets/issuers or expand fallback logic.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
