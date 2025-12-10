# file: app.py
import streamlit as st
import yfinance as yf
import pandas as pd
from indicators import generate_signal
from datetime import datetime
from pytz import timezone

st.set_page_config(page_title="2X Clean Execution Scanner", layout="wide")
st.title("2X Clean Execution (EMA + Supertrend, ATR Exit) Scanner")
st.markdown("Real-time trading signals for NIFTY, BANKNIFTY, and stock indices")

# Sidebar configuration
with st.sidebar:
    st.header("Configuration")
    symbols_input = st.text_area(
        "Symbols (comma separated)",
        value="^NSEBANK.NS,^NSEI.NS,HDFCBANK.NS,ICICIBANK.NS",
    )
    timeframe = st.selectbox("Timeframe", ["5m", "15m", "30m", "60m", "1d"], index=1)
    ema_fast = st.number_input("Fast EMA", 1, 100, 9)
    ema_slow = st.number_input("Slow EMA", 1, 200, 21)
    atr_period = st.number_input("ATR Period", 1, 100, 10)
    atr_mult = st.number_input("Supertrend Multiplier", 1.0, 10.0, 3.0)

# Check market hours
ist = timezone('Asia/Kolkata')
now = datetime.now(ist)
market_open_time = ist.localize(datetime(now.year, now.month, now.day, 9, 15))
market_close_time = ist.localize(datetime(now.year, now.month, now.day, 15, 30))

if market_open_time <= now <= market_close_time:
    market_status = "🟢 **MARKET OPEN** (9:15 AM - 3:30 PM IST)"
    is_market_open = True
else:
    market_status = "🔴 **MARKET CLOSED** (Next opening: 9:15 AM IST)"
    is_market_open = False

st.info(market_status)

if st.button("Scan for Signals", disabled=not is_market_open):
    if not is_market_open:
        st.warning("⏰ Scanner only runs during market hours (9:15 AM - 3:30 PM IST)")
    else:
        rows = []
        for sym in [s.strip() for s in symbols_input.split(",") if s.strip()]:
            try:
                with st.spinner(f"Scanning {sym}..."):
                    df = yf.download(sym, period="30d", interval=timeframe, progress=False)
                    if df.empty or len(df) < 2:
                        continue
                    
                    df = df.dropna()
                    signal, sl = generate_signal(df, ema_fast=int(ema_fast), ema_slow=int(ema_slow))
                    
                    if signal != "NONE":
                        last_close = df["Close"].iloc[-1]
                        risk_pts = abs(last_close - sl) if not pd.isna(sl) else 0
                        
                        rows.append({
                            "Symbol": sym,
                            "Signal": signal,
                            "Entry": round(float(last_close), 2),
                            "SL": round(float(sl), 2) if not pd.isna(sl) else "N/A",
                            "Risk (pts)": round(float(risk_pts), 2),
                            "Time": datetime.now(ist).strftime("%H:%M:%S IST")
                        })
            except Exception as e:
                st.warning(f"Error scanning {sym}: {str(e)}")
        
        if rows:
            df_results = pd.DataFrame(rows)
            st.success(f"✅ Found {len(rows)} signal(s)!")
            st.dataframe(df_results, use_container_width=True)
            
            # Display trade details
            st.subheader("Trade Details")
            for idx, row in enumerate(rows, 1):
                with st.expander(f"{idx}. {row['Signal']} - {row['Symbol']}"):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Entry", f"{row['Entry']:.2f}")
                    with col2:
                        st.metric("SL", f"{row['SL']}") 
                    with col3:
                        st.metric("Risk", f"{row['Risk (pts)']} pts")
        else:
            st.info("📊 No signals found in the current market scan.")

st.markdown("---")
st.markdown("**📌 How It Works:**")
st.markdown("""
- **EMA Cross**: Fast EMA (9) crosses Slow EMA (21)
- **Supertrend**: Confirms trend direction with ATR-based bands
- **Entry**: When both EMA and Supertrend align
- **SL**: ATR-based stop loss level
- **Market Hours**: 9:15 AM - 3:30 PM IST (India Stock Exchange)
""")

st.markdown("**🔧 Setup Required:**")
st.markdown("""
1. Copy `.env.example` to `.env`
2. Add Twilio WhatsApp credentials
3. Add Google Sheets API credentials
4. Run `python scheduler.py` for 5-min auto-scanning
5. Get WhatsApp alerts for every signal
""")
