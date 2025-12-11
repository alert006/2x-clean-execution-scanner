# file: indicators.py
import pandas as pd
import numpy as np
import pandas_ta as ta

def calculate_supertrend(df, atr_length=10, multiplier=2.0):
    """
    Calculate Supertrend indicator
    Returns: supertrend values and direction (1 for uptrend, -1 for downtrend)
    """
    high = df['High']
    low = df['Low']
    close = df['Close']
    
    # Calculate ATR
    atr_val = ta.atr(high, low, close, length=atr_length)
    
    # Calculate basic bands
    hl_avg = (high + low) / 2
    matr = multiplier * atr_val
    
    # Upper and lower bands
    upper_band = hl_avg + matr
    lower_band = hl_avg - matr
    
    # Initialize supertrend
    supertrend = pd.Series(index=df.index, dtype='float64')
    direction = pd.Series(index=df.index, dtype='int64')
    
    supertrend.iloc[0] = close.iloc[0]
    direction.iloc[0] = 1
    
    for i in range(1, len(df)):
        if close.iloc[i] <= upper_band.iloc[i]:
            supertrend.iloc[i] = upper_band.iloc[i]
            direction.iloc[i] = 1  # Uptrend
        else:
            supertrend.iloc[i] = lower_band.iloc[i]
            direction.iloc[i] = -1  # Downtrend
    
    return supertrend, direction, atr_val

def generate_signal(df, ema_length=30, supertrend_atr_length=10, supertrend_multiplier=2.0, atr_length=14, sl_multiplier=1.5, tp_multiplier=3.0):
    """
    Generate trading signals based on:
    - EMA(30) price position
    - Supertrend direction (ATR=10, Multiplier=2.0)
    - ATR(14) for exit levels
    
    Entry Rules (from TradingView strategy):
    - LONG: Close > EMA(30) AND Supertrend is BULLISH (uptrend)
    - SHORT: Close < EMA(30) AND Supertrend is BEARISH (downtrend)
    
    Exit Rules:
    - SL: Entry Price ± (ATR(14) × 1.5)
    - TP: Entry Price ± (ATR(14) × 3.0)
    """
    
    if len(df) < max(ema_length, supertrend_atr_length, atr_length) + 5:
        return "NONE", 0, 0, 0, 0
    
    # Calculate EMA(30)
    ema = ta.ema(df['Close'], length=ema_length)
    
    # Calculate Supertrend (ATR=10, Multiplier=2.0)
    supertrend, st_direction, st_atr = calculate_supertrend(df, atr_length=supertrend_atr_length, multiplier=supertrend_multiplier)
    
    # Calculate ATR(14) for exit levels
    atr = ta.atr(df['High'], df['Low'], df['Close'], length=atr_length)
    
    # Get latest values
    latest_close = df['Close'].iloc[-1]
    latest_ema = ema.iloc[-1]
    latest_supertrend = supertrend.iloc[-1]
    latest_st_direction = st_direction.iloc[-1]
    latest_atr = atr.iloc[-1]
    
    # Determine signal based on entry conditions
    signal = "NONE"
    
    # LONG condition: Close > EMA(30) AND Supertrend is BULLISH
    if latest_close > latest_ema and latest_st_direction == 1:
        signal = "BUY"
    
    # SHORT condition: Close < EMA(30) AND Supertrend is BEARISH
    elif latest_close < latest_ema and latest_st_direction == -1:
        signal = "SELL"
    
    return signal, latest_atr, latest_ema, latest_supertrend, latest_st_direction
