# file: sms_sender.py
import os
from twilio.rest import Client

# Load Twilio credentials from environment variables
ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')

def send_sms_signal(to_number: str, signal_data: dict) -> bool:
    """
    Send trading signals via SMS using Twilio
    
    Args:
        to_number: Recipient's phone number
        signal_data: Dictionary containing signal information
    
    Returns:
        bool: True if SMS sent successfully, False otherwise
    """
    try:
        # Check if Twilio credentials are configured
        if not ACCOUNT_SID or not AUTH_TOKEN or not TWILIO_PHONE_NUMBER:
            print("Error: Twilio credentials not configured.")
            return False
        
        # Initialize Twilio client
        client = Client(ACCOUNT_SID, AUTH_TOKEN)
        
        # Format the message
        message_text = format_signal_message(signal_data)
        
        # Ensure the number is in proper format
        if not to_number.startswith('+'):
            to_number = f'+{to_number}'
        
        # Send the SMS
        message = client.messages.create(
            from_=TWILIO_PHONE_NUMBER,
            body=message_text,
            to=to_number
        )
        
        print(f"SMS sent successfully! Message SID: {message.sid}")
        return True
    
    except Exception as e:
        print(f"Error sending SMS: {str(e)}")
        return False

def format_signal_message(signal_data: dict) -> str:
    """
    Format the trading signal into a readable SMS message
    
    Args:
        signal_data: Dictionary containing signal information
    
    Returns:
        str: Formatted message string
    """
    message = "TRADING SIGNAL\n"
    message += f"Symbol: {signal_data.get('symbol', 'N/A')}\n"
    message += f"Signal: {signal_data.get('signal', 'N/A')}\n"
    message += f"Price: {signal_data.get('price', 'N/A')}\n"
    message += f"EMA: {signal_data.get('ema', 'N/A')}\n"
    message += f"SuperTrend: {signal_data.get('supertrend', 'N/A')}\n"
    message += f"ATR: {signal_data.get('atr', 'N/A')}\n"
    message += f"Stop Loss: {signal_data.get('sl', 'N/A')}\n"
    message += f"Take Profit: {signal_data.get('tp', 'N/A')}\n"
    message += f"RRR: {signal_data.get('rrr_ratio', 'N/A')}\n"
    message += f"Time: {signal_data.get('time', 'N/A')}\n"
    message += "#2XCleanExecution #Trading"
    return message

def send_test_sms(to_number: str) -> bool:
    """
    Send a test trading signal via SMS
    
    Args:
        to_number: Recipient's phone number
    
    Returns:
        bool: True if test message sent successfully
    """
    # Create test signal with sample values
    test_signal = {
        'symbol': 'MARUTI.NS',
        'signal': 'BUY',
        'price': '8500',
        'ema': '8450',
        'supertrend': '8400',
        'atr': '75.50',
        'sl': '8424',
        'tp': '8776',
        'rrr_ratio': '4.71',
        'time': '14:30'
    }
    
    return send_sms_signal(to_number, test_signal)