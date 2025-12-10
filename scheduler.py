# file: scheduler.py
import os
import json
from datetime import datetime
from pytz import timezone
import yfinance as yf
import gspread
from google.oauth2.service_account import Credentials
from apscheduler.schedulers.background import BackgroundScheduler
from twilio.rest import Client
from indicators import generate_signal

# Initialize scheduler
scheduler = BackgroundScheduler()

# Twilio WhatsApp Setup
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER")  # e.g., "whatsapp:+1234567890"
USER_WHATSAPP_NUMBER = os.getenv("USER_WHATSAPP_NUMBER")  # e.g., "whatsapp:+1234567890"

twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Google Sheets Setup
GOOGLE_SHEETS_CREDENTIALS = os.getenv("GOOGLE_SHEETS_CREDENTIALS_JSON")
GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID")

def init_google_sheets():
    """Initialize Google Sheets API"""
    try:
        creds_dict = json.loads(GOOGLE_SHEETS_CREDENTIALS)
        creds = Credentials.from_service_account_info(
            creds_dict,
            scopes=["https://www.googleapis.com/auth/spreadsheets"]
        )
        gc = gspread.authorize(creds)
        sheet = gc.open_by_key(GOOGLE_SHEET_ID).sheet1
        return sheet
    except Exception as e:
        print(f"Google Sheets Error: {e}")
        return None

def send_whatsapp_alert(symbol, signal, entry_price, sl, target=None):
    """Send WhatsApp alert via Twilio"""
    try:
        if signal == "BUY":
            msg = f"\ud83d\udcec *2X CLEAN EXECUTION - BUY SIGNAL*\n\n" \
                  f"Symbol: {symbol}\n" \
                  f"Entry: {entry_price:.2f}\n" \
                  f"SL: {sl:.2f}\n" \
                  f"Risk: {abs(entry_price - sl):.2f} pts\n" \
                  f"Time: {datetime.now().strftime('%H:%M:%S')}"
        elif signal == "SELL":
            msg = f"\ud83d\udcec *2X CLEAN EXECUTION - SELL SIGNAL*\n\n" \
                  f"Symbol: {symbol}\n" \
                  f"Entry: {entry_price:.2f}\n" \
                  f"SL: {sl:.2f}\n" \
                  f"Risk: {abs(entry_price - sl):.2f} pts\n" \
                  f"Time: {datetime.now().strftime('%H:%M:%S')}"
        else:
            return

        twilio_client.messages.create(
            from_=TWILIO_WHATSAPP_NUMBER,
            to=USER_WHATSAPP_NUMBER,
            body=msg
        )
        print(f"WhatsApp alert sent for {symbol}: {signal}")
    except Exception as e:
        print(f"WhatsApp Error: {e}")

def log_to_google_sheets(sheet, symbol, signal, entry, sl, risk, timestamp):
    """Log signal to Google Sheets"""
    try:
        if sheet is None:
            return
        sheet.append_row([
            timestamp,
            symbol,
            signal,
            entry,
            sl,
            risk,
            "PENDING",  # Status: PENDING, FILLED, EXITED
            "",  # Exit Price
            "",  # Exit Time
            ""  # PnL
        ])
        print(f"Logged {symbol} {signal} to Google Sheets")
    except Exception as e:
        print(f"Google Sheets Logging Error: {e}")

def scan_symbols():
    """Scan all symbols for signals every 5 minutes"""
    symbols_to_scan = [
        "^NSEBANK",
        "^NSEI",
            # Check if current time is within market hours (IST: 9:15 AM - 3:30 PM)
    ist = timezone('Asia/Kolkata')
    now = datetime.now(ist)
    market_open = ist.localize(datetime(now.year, now.month, now.day, 9, 15))
    market_close = ist.localize(datetime(now.year, now.month, now.day, 15, 30))
    
    # Only scan during market hours
    if not (market_open <= now <= market_close):
        print(f"Market closed. Current time: {now.strftime('%H:%M:%S IST')}. Scanning resumes at 9:15 AM IST")
        return
        "HDFCBANK.NS",
        "ICICIBANK.NS",
        "BAJAJFINSV.NS",
    ]

    sheet = init_google_sheets()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for symbol in symbols_to_scan:
        try:
            # Fetch 5-min data
            df = yf.download(symbol, period="7d", interval="5m", progress=False)
            if df.empty:
                continue

            df = df.dropna()
            signal, sl = generate_signal(df)

            if signal != "NONE":
                last_close = df["Close"].iloc[-1]
                risk = abs(last_close - sl)

                # Send WhatsApp alert
                send_whatsapp_alert(symbol, signal, last_close, sl)

                # Log to Google Sheets
                log_to_google_sheets(sheet, symbol, signal, last_close, sl, risk, timestamp)

        except Exception as e:
            print(f"Error scanning {symbol}: {e}")

def start_scheduler():
    """Start the background scheduler"""
    scheduler.add_job(scan_symbols, "interval", minutes=5, id="scan_job")
    if not scheduler.running:
        scheduler.start()
    print("Scheduler started: Scanning every 5 minutes")

def stop_scheduler():
    """Stop the background scheduler"""
    if scheduler.running:
        scheduler.shutdown()
    print("Scheduler stopped")
