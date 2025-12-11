# file: whatsapp_sender.py
import os
from twilio.rest import Client

# Twilio credentials from environment variables
ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID', '')
AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN', '')
TWILIO_WHATSAPP_NUMBER = os.getenv('TWILIO_WHATSAPP_NUMBER', 'whatsapp:+14155238886')  # Twilio sandbox number

def send_whatsapp_signal(to_number: str, signal_data: dict) -> bool:
    """
    Send a trading signal to WhatsApp using Twilio
    
    Args:
        to_number: Recipient's WhatsApp number (format: +919876543210)
        signal_data: Dictionary containing signal information
                     Expected keys: symbol, signal, price, sl, tp, ema, supertrend, atr, time
    
    Returns:
        bool: True if message sent successfully, False otherwise
    """
    try:
        if not ACCOUNT_SID or not AUTH_TOKEN:
            print("⚠️  Twilio credentials not configured. Set TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN environment variables.")
            return False
        
        client = Client(ACCOUNT_SID, AUTH_TOKEN)
        
        # Format the message
        message_text = format_signal_message(signal_data)
        
        # Ensure the number is in WhatsApp format
        if not to_number.startswith('whatsapp:'):
            to_number = f'whatsapp:{to_number}'
        
        # Send the message
        message = client.messages.create(
            from_=TWILIO_WHATSAPP_NUMBER,
            body=message_text,
            to=to_number
        )
        
        print(f"✅ WhatsApp message sent successfully! Message SID: {message.sid}")
        return True
        
    except Exception as e:
        print(f"❌ Error sending WhatsApp message: {str(e)}")
        return False

def format_signal_message(signal_data: dict) -> str:
    """
    Format the trading signal into a readable WhatsApp message
    
    Args:
        signal_data: Dictionary containing signal information
    
    Returns:
        str: Formatted message for WhatsApp
    """
    symbol = signal_data.get('symbol', 'N/A')
    signal = signal_data.get('signal', 'N/A')
    price = signal_data.get('price', 'N/A')
    sl = signal_data.get('sl', 'N/A')
    tp = signal_data.get('tp', 'N/A')
    ema = signal_data.get('ema', 'N/A')
    supertrend = signal_data.get('supertrend', 'N/A')
    atr = signal_data.get('atr', 'N/A')
    rr_ratio = signal_data.get('rr_ratio', 'N/A')
    time_str = signal_data.get('time', 'N/A')
    
    message = f"""
🎯 2X CLEAN EXECUTION SIGNAL 🎯

📊 {symbol}
🔔 Signal: {signal}
⏰ Time: {time_str}

💰 Entry Price: {price}
📈 EMA(30): {ema}
📉 Supertrend: {supertrend}

🛑 Stop Loss: {sl}
🎁 Take Profit: {tp}
📊 Risk/Reward: {rr_ratio}

💡 ATR: {atr}

#2XCleanExecution #Trading #NIFTY50
    """.strip()
    
    return message

def send_test_signal(to_number: str) -> bool:
    """
    Send a test trading signal to verify WhatsApp integration
    
    Args:
        to_number: Recipient's WhatsApp number
    
    Returns:
        bool: True if test message sent successfully
    """
    test_signal = {
        'symbol': 'MARUTI.NS',
        'signal': 'BUY',
        'price': '₹8,500.00',
        'ema': '₹8,450.00',
        'supertrend': '₹8,400.00',
        'atr': '₹75.50',
        'sl': '₹8,424.50',
        'tp': '₹8,776.50',
        'rr_ratio': '4.71',
        'time': '14:30:00'
    }
    
    return send_whatsapp_signal(to_number, test_signal)
