# file: app.py
import streamlit as st
import yfinance as yf
import pandas as pd
from indicators import generate_signal
from datetime import datetime
from pytz import timezone

st.set_page_config(page_title="2X Clean Execution Scanner", layout="wide")
st.title("2X Clean Execution (EMA + Supertrend, ATR Exit) Scanner")
st.markdown("Real-time trading signals for NIFTY 50 stocks")

# Sidebar configuration
with st.sidebar:
    st.header("Configuration")
    
    # Stock lists dictionary with all Nifty 50 stocks
    stock_lists = {
        "Nifty 50 All": "ADANIENT.NS,ADANIPORTS.NS,APOLLOHOSP.NS,ASIANPAINT.NS,AXISBANK.NS,BAJAJ-AUTO.NS,BAJFINANCE.NS,BAJAJFINSV.NS,BEL.NS,BHARTIARTL.NS,CIPLA.NS,COALINDIA.NS,DRREDDY.NS,EICHERMOT.NS,ETERNAL.NS,GRASIM.NS,HCLTECH.NS,HDFCBANK.NS,HDFCLIFE.NS,HEROMOTOCO.NS,HINDALCO.NS,HINDUNILVR.NS,ICICIBANK.NS,INDUSINDBK.NS,INFY.NS,ITC.NS,JSWSTEEL.NS,JIOFIN.NS,KOTAKBANK.NS,LT.NS,M&MFARM.NS,MARUTI.NS,NTPC.NS,NESTLEIND.NS,ONGC.NS,POWERGRID.NS,RELIANCE.NS,SBILIFE.NS,SHRIRAMFIN.NS,SBIN.NS,SUNPHARMA.NS,TCS.NS,TATACONSUM.NS,TATAMOTORS.NS,TATASTEEL.NS,TECHM.NS,TITAN.NS,TRENT.NS,ULTRACEMCO.NS,WIPRO.NS",
        "Nifty 50 Banks": "AXISBANK.NS,HDFCBANK.NS,ICICIBANK.NS,INDUSINDBK.NS,KOTAKBANK.NS,SBILIFE.NS,SBIN.NS",
        "Nifty 50 IT": "HCLTECH.NS,INFY.NS,TECHM.NS,TCS.NS,WIPRO.NS",
        "Nifty 50 Pharma": "CIPLA.NS,DRREDDY.NS,SUNPHARMA.NS",
        "Nifty 50 Auto": "BAJAJ-AUTO.NS,EICHERMOT.NS,HEROMOTOCO.NS,M&MFARM.NS,MARUTI.NS,TATAMOTORS.NS",
        "Nifty 50 Metals": "HINDALCO.NS,JSWSTEEL.NS,TATASTEEL.NS",
        "Nifty 50 Energy": "COALINDIA.NS,NTPC.NS,ONGC.NS,POWERGRID.NS,RELIANCE.NS",
        "Nifty 50 Finance": "BAJFINANCE.NS,BAJAJFINSV.NS,SHRIRAMFIN.NS",
        "Custom": "HDFCBANK.NS,ICICIBANK.NS,INFY.NS,TCS.NS"
    }
    
    selected_list = st.selectbox(
        "📊 Select Stock List",
        list(stock_lists.keys()),
        index=0
    )
    
    if selected_list == "Custom":
        symbols_input = st.text_area(
            "Custom Symbols (comma separated)",
            value=stock_lists["Custom"],
            height=100
        )
    else:
        symbols_input = st.text_area(
            f"{selected_list} - Click to edit",
            value=stock_lists[selected_list],
            height=100
        )
    
    num_symbols = len([s.strip() for s in symbols_input.split(',') if s.strip()])
    st.success(f"✅ {num_symbols} symbols selected")
    
    st.divider()
    st.subheader("Trading Parameters")
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

if st.button("🔍 Scan for Signals", use_container_width=True, disabled=not is_market_open):
    if not is_market_open:
        st.warning("⏰ Scanner only runs during market hours (9:15 AM - 3:30 PM IST)")
    else:
        rows = []
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        symbols = [s.strip() for s in symbols_input.split(",") if s.strip()]
        total = len(symbols)
        
        for idx, sym in enumerate(symbols):
            try:
                status_text.info(f"🔄 Scanning {idx+1}/{total}: {sym}...")
                df = yf.download(sym, period="30d", interval=timeframe, progress=False)
                
                if df.empty or len(df) < 2:
                    progress_bar.progress((idx + 1) / total)
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
                
                progress_bar.progress((idx + 1) / total)
            except Exception as e:
                progress_bar.progress((idx + 1) / total)
                continue
        
        status_text.empty()
        progress_bar.empty()
        
        if rows:
            df_results = pd.DataFrame(rows)
            st.success(f"✅ Found {len(rows)} signal(s)!")
            st.dataframe(df_results, use_container_width=True)
            
            # Display trade details
            st.subheader("📈 Trade Details")
            for idx, row in enumerate(rows, 1):
                with st.expander(f"{idx}. {row['Signal']} - {row['Symbol']}"):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Entry", f"₹{row['Entry']:.2f}")
                    with col2:
                        st.metric("SL", f"₹{row['SL']}") 
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
5. Get WhatsApp alerts + Google Sheets logging
""")
