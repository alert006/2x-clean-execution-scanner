import pandas as pd
import numpy as np

def ema(df, period, col="Close"):
    return df[col].ewm(span=period, adjust=False).mean()

def generate_signal(df, ema_fast=9, ema_slow=21):
    df["EMA_Fast"] = ema(df, ema_fast)
    df["EMA_Slow"] = ema(df, ema_slow)
    signal = "NONE"
    sl = np.nan
    return signal, sl
