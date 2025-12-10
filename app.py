# file: app.py
import streamlit as st
import yfinance as yf
import pandas as pd
from indicators import generate_signal, supertrend, ema

st.set_page_config(page_title="2X Clean Execution Scanner", layout="wide")

st.title("2X Clean Execution (EMA + Supertrend, ATR Exit) Scanner")
st.markdown("Real-time trading signals for NIFTY, BANKNIFTY, and stock indices")

# Sidebar configuration
with st.sidebar:
    st.header("Configuration")
    
    symbols_input = st.text_area(
        "Symbols (comma separated)",
        value="^NSEBANK,^NSEI,HDFCBANK.NS,ICICIBANK.NS,INFY.NS,RELIANCE.NS",
        height=100
    )
    
    timeframe = st.selectbox("Timeframe", ["5m", "15m", "30m", "60m", "1d"], index=1)
    
    col1, col2 = st.columns(2)
    with col1:
        ema_fast = st.number_input("Fast EMA", 1, 100, 9)
    with col2:
        ema_slow = st.number_input("Slow EMA", 1, 200, 21)
    
    col3, col4 = st.columns(2)
    with col3:
        atr_period = st.number_input("ATR Period", 1, 100, 10)
    with col4:
        atr_mult = st.number_input("ST Multiplier", 1.0, 10.0, 3.0, step=0.5)
    
    scan_button = st.button("🔍 Scan for Signals", use_container_width=True)

# Main scanning logic
if scan_button:
    st.info("Scanning symbols for trading signals...")
    
    rows = []
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    symbols = [s.strip() for s in symbols_input.split(",") if s.strip()]
    
    for idx, sym in enumerate(symbols):
        try:
            status_text.text(f"Processing {sym}...")
            
            # Download data
            df = yf.download(sym, period="30d", interval=timeframe, progress=False)            
            if df.empty or len(dprogress=False)
            df = df.dropna()
            
            # Calculate indicators
            df_ind = supertrend(df, atr_period=int(atr_period), multiplier=float(atr_mult))
            signal, sl = generate_signal(df_ind, ema_fast=int(ema_fast), ema_slow=int(ema_slow))
            
            last_close = df_ind["Close"].iloc[-1]
            risk_pts = abs(last_close - sl) if sl == sl else None  # NaN check
            
            rows.append({
                "Symbol": sym,
                "Last Close": round(float(last_close), 2),
                "Signal": signal,
                "SL": round(float(sl), 2) if sl == sl else "N/A",
                "Risk (pts)": round(float(risk_pts), 2) if risk_pts is not None else "N/A",
                "Risk %": round((risk_pts / last_close * 100), 2) if risk_pts is not None else "N/A"
            })
        
        except Exception as e:
            st.warning(f"⚠️ Error processing {sym}: {str(e)[:50]}")
            continue
        
        progress_bar.progress((idx + 1) / len(symbols))
    
    status_text.empty()
    progress_bar.empty()
    
    # Display results
    if rows:
        df_results = pd.DataFrame(rows)
        
        # Color code signals
        st.subheader(f"📊 Scan Results ({len(rows)} symbols processed)")
        
        # Separate by signal type
        buy_signals = df_results[df_results["Signal"] == "BUY"]
        sell_signals = df_results[df_results["Signal"] == "SELL"]
        no_signals = df_results[df_results["Signal"] == "NONE"]
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("BUY Signals", len(buy_signals), delta=None)
        with col2:
            st.metric("SELL Signals", len(sell_signals), delta=None)
        with col3:
            st.metric("No Signal", len(no_signals), delta=None)
        
        # Display Buy signals
        if not buy_signals.empty:
            st.success("🟢 BUY Signals")
            st.dataframe(buy_signals, use_container_width=True, hide_index=True)
        
        # Display Sell signals
        if not sell_signals.empty:
            st.error("🔴 SELL Signals")
            st.dataframe(sell_signals, use_container_width=True, hide_index=True)
        
        # Display No signals
        if not no_signals.empty:
            with st.expander("⚪ No Signals (click to expand)"):
                st.dataframe(no_signals, use_container_width=True, hide_index=True)
    
    else:
        st.warning("No data / signals for given symbols and timeframe.")

# Footer
st.markdown("---")
st.markdown("""
**Disclaimer:** This scanner is for educational purposes. Always perform your own analysis before trading.

**Strategy:** 2X Clean Execution (EMA + Supertrend, ATR Exit)
- **EMA Fast:** Confirms trend direction
- **EMA Slow:** Identifies overall trend
- **Supertrend:** Entry/Exit signals with ATR-based stops
- **Risk Management:** ATR-based stop loss for each trade
""")
