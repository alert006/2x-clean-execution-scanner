# file: app.py
import streamlit as st
import yfinance as yf
import pandas as pd
from indicators import generate_signal
st.set_page_config(page_title="2X Clean Execution Scanner", layout="wide")

st.title("2X Clean Execution (EMA + Supertrend, ATR Exit) Scanner")
st.markdown("Real-time trading signals for NIFTY, BANKNIFTY, and stock indices")

# Sidebar configuration
with st.sidebar:
    st.header("Configuration")
    
    symbols_input = st.text_area(
        "Symbols (comma separated)",
value="AARTIIND.NS,ABB.NS,ABCAPITAL.NS,ABFRL.NS,ACC.NS,ADANIENSOL.NS,ADANIENT.NS,ADANIGREEN.NS,ADANIPORTS.NS,ALKEM.NS,AMBUJACEM.NS,ANGELONE.NS,APLAPOLLO.NS,APOLLOHOSP.NS,APOLLOTYRE.NS,ASHOKLEY.NS,ASIANPAINT.NS,ASTRAL.NS,ATGL.NS,AUBANK.NS,AUROPHARMA.NS,AXISBANK.NS,BAJAJ-AUTO.NS,BAJAJFINSV.NS,BAJFINANCE.NS,BALKRISIND.NS,BANDHANBNK.NS,BANKBARODA.NS,BANKINDIA.NS,BEL.NS,BERGEPAINT.NS,BHARATFORG.NS,BHARTIARTL.NS,BHEL.NS,BIOCON.NS,BOSCHLTD.NS,BPCL.NS,BRITANNIA.NS,BSE.NS,BSOFT.NS,CAMS.NS,CANBK.NS,CDSL.NS,CESC.NS,CGPOWER.NS,CHAMBLFERT.NS,CHOLAFIN.NS,CIPLA.NS,COALINDIA.NS,COFORGE.NS,COLPAL.NS,CONCOR.NS,CROMPTON.NS,CUMMINSIND.NS,CYIENT.NS,DABUR.NS,DALBHARAT.NS,DEEPAKNTR.NS,DELHIVERY.NS,DIVISLAB.NS,DIXON.NS,DLF.NS,DMART.NS,DRREDDY.NS,EICHERMOT.NS,ESCORTS.NS,EXIDEIND.NS,FEDERALBNK.NS,GAIL.NS,GLENMARK.NS,GMRAIRPORT.NS,GODREJCP.NS,GODREJPROP.NS,GRANULES.NS,GRASIM.NS,HAL.NS,HAVELLS.NS,HCLTECH.NS,HDFCAMC.NS,HDFCBANK.NS,HDFCLIFE.NS,HEROMOTOCO.NS,HFCL.NS,HINDALCO.NS,HINDCOPPER.NS,HINDPETRO.NS,HINDUNILVR.NS,HINDZINC.NS,HUDCO.NS,ICICIBANK.NS,ICICIGI.NS,ICICIPRULI.NS,IDEA.NS,IDFCFIRSTB.NS,IEX.NS,IGL.NS,IIFL.NS,INDHOTEL.NS,INDIANB.NS,INDIGO.NS,INDUSINDBK.NS,INDUSTOWER.NS,INFY.NS,INOXWIND.NS,IOC.NS,IRB.NS,IRCTC.NS,IREDA.NS,IRFC.NS,ITC.NS,JINDALSTEL.NS,JIOFIN.NS,JSL.NS,JSWENERGY.NS,JSWSTEEL.NS,JUBLFOOD.NS,KALYANKJIL.NS,KEI.NS,KOTAKBANK.NS,KPITTECH.NS,LAURUSLABS.NS,LICHSGFIN.NS,LICI.NS,LODHA.NS,LT.NS,LTF.NS,LTIM.NS,LUPIN.NS,M&M.NS,M&MFIN.NS,MANAPPURAM.NS,MARICO.NS,MARUTI.NS,MAXHEALTH.NS,MCX.NS,MFSL.NS,MGL.NS,MOTHERSON.NS,MPHASIS.NS,MRF.NS,MUTHOOTFIN.NS,NATIONALUM.NS,NAUKRI.NS,NBCC.NS,NCC.NS,NESTLEIND.NS,NHPC.NS,NMDC.NS,NTPC.NS,NYKAA.NS,OBEROIRLTY.NS,OFSS.NS,OIL.NS,ONGC.NS,PAGEIND.NS,PATANJALI.NS,PAYTM.NS,PEL.NS,PERSISTENT.NS,PETRONET.NS,PFC.NS,PHOENIXLTD.NS,PIDILITIND.NS,PIIND.NS,PNB.NS,PNBHOUSING.NS,POLICYBZR.NS,POLYCAB.NS,POONAWALLA.NS,POWERGRID.NS,PRESTIGE.NS,RAMCOCEM.NS,RBLBANK.NS,RECLTD.NS,RELIANCE.NS,SAIL.NS,SBICARD.NS,SBILIFE.NS,SBIN.NS,SHREECEM.NS,SHRIRAMFIN.NS,SJVN.NS,SOLARINDS.NS,SONACOMS.NS,SRF.NS,SUNPHARMA.NS,SUPREMEIND.NS,SYNGENE.NS,TATACHEM.NS,TATACOMM.NS,TATACONSUM.NS,TATAELXSI.NS,TATAMOTORS.NS,TATAPOWER.NS,TATASTEEL.NS,TATATECH.NS,TCS.NS,TECHM.NS,TIINDIA.NS,TITAGARH.NS,TITAN.NS,TORNTPHARM.NS,TORNTPOWER.NS,TRENT.NS,TVSMOTOR.NS,ULTRACEMCO.NS,UNIONBANK.NS,UNITDSPR.NS,UPL.NS,VBL.NS,VEDL.NS,VOLTAS.NS,WIPRO.NS,YESBANK.NS,ZYDUSLIFE.NS"        height=100
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
            if df.empty or len(df) < 2:
                df = df.dropna()
            
            # Calculate indicators
            df_ind = df
            signal, sl = generate_signal(df_ind, ema_fast=int(ema_fast), ema_slow=int(ema_slow))            last_close = df_ind["Close"].iloc[-1]
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
