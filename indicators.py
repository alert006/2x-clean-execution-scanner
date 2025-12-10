# file: indicators.py
import pandas as pd
import numpy as np

def ema(df, period, col="Close"):
    """Calculate Exponential Moving Average"""
    return df[col].ewm(span=period, adjust=False).mean()

def supertrend(df, atr_period=10, multiplier=3.0):
    """Calculate Supertrend indicator using ATR"""
    high = df["High"]
    low = df["Low"]
    close = df["Close"]

    # Calculate True Range
    price_diffs = [high - low, (high - close.shift()).abs(), (close.shift() - low).abs()]
    true_range = pd.concat(price_diffs, axis=1).max(axis=1)
    atr = true_range.ewm(alpha=1/atr_period, min_periods=atr_period).mean()

    hl2 = (high + low) / 2
    upperband = hl2 + multiplier * atr
    lowerband = hl2 - multiplier * atr

    final_upperband = upperband.copy()
    final_lowerband = lowerband.copy()
    supertrend_dir = [True] * len(df)

    for i in range(1, len(df)):
        if close.iloc[i] > final_upperband.iloc[i-1]:
            supertrend_dir[i] = True
        elif close.iloc[i] < final_lowerband.iloc[i-1]:
            supertrend_dir[i] = False
        else:
            supertrend_dir[i] = supertrend_dir[i-1]
            if supertrend_dir[i] and final_lowerband.iloc[i] < final_lowerband.iloc[i-1]:
                final_lowerband.iloc[i] = final_lowerband.iloc[i-1]
            if not supertrend_dir[i] and final_upperband.iloc[i] > final_upperband.iloc[i-1]:
                final_upperband.iloc[i] = final_upperband.iloc[i-1]

        if supertrend_dir[i]:
            final_upperband.iloc[i] = np.nan
        else:
            final_lowerband.iloc[i] = np.nan

    out = df.copy()
    out["ST_UpTrend"] = supertrend_dir
    out["ST_Upper"] = final_upperband
    out["ST_Lower"] = final_lowerband
    return out

def generate_signal(df, ema_fast=9, ema_slow=21):
    """Generate trading signals based on EMA + Supertrend"""
    df["EMA_Fast"] = ema(df, ema_fast)
    df["EMA_Slow"] = ema(df, ema_slow)
    df = supertrend(df)

    last = df.iloc[-1]
    prev = df.iloc[-2]

    signal = "NONE"
    sl = np.nan

    # Long signal: Supertrend flips up, price above EMA
    if last["ST_UpTrend"] and last["Close"] > last["EMA_Fast"] and not prev["ST_UpTrend"]:
        signal = "BUY"
        sl = last["ST_Lower"]
    # Short signal: Supertrend flips down, price below EMA
    elif (not last["ST_UpTrend"]) and last["Close"] < last["EMA_Fast"] and prev["ST_UpTrend"]:
        signal = "SELL"
        sl = last["ST_Upper"]

    return signal, sl
