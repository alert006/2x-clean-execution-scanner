# file: app.py
import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import time
import pytz
from indicators import generate_signal

# Page configuration
st.set_page_config(page_title="2X Clean Execution Scanner", layout="wide")

st.title("2X Clean Execution (EMA + Supertrend, ATR Exit) Scanner")
st.markdown("**Real-time trading signals for NIFTY 50 stocks**")

# Stock lists dictionary with all Nifty 50 stocks
stock_lists = {
    "Nifty 50 All": "ADANIENT.NS,ADANIPORTS.NS,APOLLOHOSP.NS,ASIANPAINT.NS,AXISBANK.NS,BAJAJ-AUTO.NS,BAJAJISTAND.NS,BAJAJFINSV.NS,BAJFINANCE.NS,BEL.NS,BPCL.NS,BRITANNIA.NS,CIPLA.NS,COALINDIA.NS,DRREDDY.NS,EICHERMOT.NS,GAIL.NS,GRASIM.NS,HCLTECH.NS,HDFC.NS,HDFCBANK.NS,HDFCLIFE.NS,HEROMOTOCO.NS,HINDALCO.NS,HINDUNILVR.NS,HKPPOLYFILN.NS,ICICIBANK.NS,IGSTN.NS,INDIGO.NS,INFY.NS,ITC.NS,JSWSTEEL.NS,KOTAKBANK.NS,LT.NS,LTIM.NS,MARUTI.NS,NTPC.NS,ONGC.NS,POWERGRID.NS,RELIANCE.NS,SBIN.NS,SBILIFE.NS,SUNPHARMA.NS,TATACONSUM.NS,TATAMOTORS.NS,TATAPOWER.NS,TATASTEEL.NS,TCS.NS,TECHM.NS,TITAN.NS,TORNTPHARM.NS,ULTRACEMCO.NS,UPL.NS,WIPRO.NS",
}

# Sidebar configuration
with st.sidebar:
    st.header("Configuration")
    
    stock_list_name = st.selectbox("Select Stock List", list(stock_lists.keys()), key="stock_list")
    
    st.markdown("---")
    st.subheader("Trading Parameters")
    
    # Timeframe selection
    timeframe = st.selectbox("Timeframe", ["5m", "15m", "1h", "1d"], key="timeframe", index=1)
    
    # EMA parameter (single EMA, not two)
    ema_length = st.number_input("EMA Length", value=30, min_value=1, key="ema_length")
    
    # Supertrend parameters
    supertrend_atr_length = st.number_input("Supertrend ATR Length", value=10, min_value=1, key="st_atr")
    supertrend_multiplier = st.number_input("Supertrend Multiplier", value=2.0, min_value=0.1, step=0.1, key="st_mult")
    
    # ATR Exit parameters
    atr_length = st.number_input("ATR Length (Exit)", value=14, min_value=1, key="atr_length")
    sl_multiplier = st.number_input("SL Multiplier (Risk)", value=1.5, min_value=0.1, step=0.1, key="sl_mult")
    tp_multiplier = st.number_input("TP Multiplier (Reward)", value=3.0, min_value=0.1, step=0.1, key="tp_mult")
    
    st.markdown("---")
    st.markdown("**Market Hours:** 9:15 AM - 3:30 PM IST (India Stock Exchange)")

# Display market status
# Get current time in IST
ist_tz = pytz.timezone('Asia/Kolkata')
current_time_ist = datetime.now(ist_tz).time()
market_open_time = datetime.strptime("09:15", "%H:%M").time()
market_close_time = datetime.strptime("15:30", "%H:%M").time()
is_market_open = market_open_time <= current_time_ist <= market_close_time

if is_market_open:
    st.success("✓ MARKET OPEN (9:15 AM - 3:30 PM IST)")
else:
    st.warning("✗ MARKET CLOSED - Last data may be outdated")

# Scan button
col1, col2 = st.columns([1, 3])
with col1:
    scan_button = st.button("🔍 Scan for Signals", key="scan_btn")

# Auto-refresh every 5 minutes
st.markdown("<div style='color: #888; font-size: 12px;'>Auto-refreshing every 5 minutes...</div>", unsafe_allow_html=True)

if scan_button or st.session_state.get('auto_scan', False):
    st.session_state.auto_scan = True
    
    # Get stocks to scan
    symbols = stock_lists[stock_list_name].split(",")
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    results_data = []
    
    for idx, symbol in enumerate(symbols):
        progress_bar.progress((idx + 1) / len(symbols))
        status_text.text(f"Scanning {idx + 1}/{len(symbols)}: {symbol}")
        
        try:
            # Download data based on timeframe
            if timeframe == "5m":
                data = yf.download(symbol, period="10d", interval="5m", progress=False)
            elif timeframe == "15m":
                data = yf.download(symbol, period="10d", interval="15m", progress=False)
            elif timeframe == "1h":
                data = yf.download(symbol, period="30d", interval="1h", progress=False)
            else:  # 1d
                data = yf.download(symbol, period="1y", progress=False)
            
            if len(data) > max(ema_length, supertrend_atr_length, atr_length):
                # Generate signal using the new logic with your exact parameters
                signal, atr, ema, supertrend_val, st_direction = generate_signal(
                    data,
                    ema_length=ema_length,
                    supertrend_atr_length=supertrend_atr_length,
                    supertrend_multiplier=supertrend_multiplier,
                    atr_length=atr_length,
                    sl_multiplier=sl_multiplier,
                    tp_multiplier=tp_multiplier
                )
                
                if signal != "NONE":
                    current_price = data['Close'].iloc[-1]
                    
                    # Calculate SL and TP
                    if signal == "BUY":
                        sl_price = current_price - (atr * sl_multiplier)
                        tp_price = current_price + (atr * tp_multiplier)
                        rr_ratio = (tp_price - current_price) / (current_price - sl_price) if current_price != sl_price else 0
                    else:  # SELL
                        sl_price = current_price + (atr * sl_multiplier)
                        tp_price = current_price - (atr * tp_multiplier)
                        rr_ratio = (current_price - tp_price) / (sl_price - current_price) if sl_price != current_price else 0
                    
                    results_data.append({
                        "Symbol": symbol,
                        "Signal": signal,
                        "Price": f"₹{current_price:.2f}",
                        "EMA(30)": f"₹{ema:.2f}",
                        "Supertrend": f"₹{supertrend_val:.2f}",
                        "ATR": f"₹{atr:.2f}",
                        "SL": f"₹{sl_price:.2f}",
                        "TP": f"₹{tp_price:.2f}",
                        "R:R": f"{rr_ratio:.2f}",
                        "Time": datetime.now().strftime("%H:%M:%S")
                    })
        
        except Exception as e:
            status_text.text(f"Error scanning {symbol}: {str(e)}")
            pass
    
    progress_bar.empty()
    status_text.empty()
    
    # Display results
    st.markdown("---")
    if results_data:
        df_results = pd.DataFrame(results_data)
        
        # Color code by signal
        def color_signal(val):
            if val == "BUY":
                return "background-color: #0d7d0d; color: white;"
            elif val == "SELL":
                return "background-color: #8b0000; color: white;"
            return ""
        
        styled_df = df_results.style.applymap(color_signal, subset=['Signal'])
        st.dataframe(styled_df, use_container_width=True)
        
        st.success(f"✓ Found {len(results_data)} signals")
    else:
        st.info("No signals found. Try scanning again.")

# Auto-refresh timer
if is_market_open:
    st.markdown("---")
    st.markdown(f"<div style='text-align: center; color: #888;'>Last scanned: {datetime.now().strftime('%H:%M:%S')} IST</div>", unsafe_allow_html=True)
    
    # Use streamlit's reruns for auto-refresh
    time.sleep(300)  # 5 minutes
    st.rerun()
