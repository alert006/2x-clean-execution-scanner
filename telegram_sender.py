# file: telegram_sender.py
import os
import asyncio
from telegram import Bot
from telegram.error import TelegramError

# Load Telegram credentials from environment variables
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

async def send_telegram_signal(chat_id: str, signal_data: dict) -> bool:
    """
    Send trading signals via Telegram using Telegram Bot API
    
    Args:
        chat_id: Telegram chat ID or user ID
        signal_data: Dictionary containing signal information
    
    Returns:
        bool: True if message sent successfully
    """
    try:
        # Check if Telegram credentials are configured
        if not TELEGRAM_BOT_TOKEN:
            print("Error: Telegram bot token not configured.")
            return False
        
        # Initialize Telegram bot
        bot = Bot(token=TELEGRAM_BOT_TOKEN)
        
        # Format the message
        message_text = format_signal_message(signal_data)
        
        # Send the message
        await bot.send_message(chat_id=chat_id, text=message_text)
        print(f"Telegram message sent to {chat_id}")
        return True
    
    except TelegramError as e:
        print(f"Telegram error: {str(e)}")
        return False
    except Exception as e:
        print(f"Error sending Telegram message: {str(e)}")
        return False

def send_telegram_signal_sync(chat_id: str, signal_data: dict) -> bool:
    """
    Synchronous wrapper for sending Telegram messages
    
    Args:
        chat_id: Telegram chat ID or user ID
        signal_data: Dictionary containing signal information
    
    Returns:
        bool: True if message sent successfully
    """
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(send_telegram_signal(chat_id, signal_data))
        loop.close()
        return result
    except Exception as e:
        print(f"Error in sync wrapper: {str(e)}")
        return False

def format_signal_message(signal_data: dict) -> str:
    """
    Format the trading signal into a readable Telegram message
    """
    message = "TRADING SIGNAL\n\n"
    message += f"Symbol: {signal_data.get('symbol', 'N/A')}\n"
    message += f"Signal: {signal_data.get('signal', 'N/A')}\n"
    message += f"Price: {signal_data.get('price', 'N/A')}\n"
    message += f"EMA: {signal_data.get('ema', 'N/A')}\n"
    message += f"SuperTrend: {signal_data.get('supertrend', 'N/A')}\n"
    message += f"ATR: {signal_data.get('atr', 'N/A')}\n\n"
    message += f"Stop Loss: {signal_data.get('sl', 'N/A')}\n"
    message += f"Take Profit: {signal_data.get('tp', 'N/A')}\n"
    message += f"Risk-Reward: {signal_data.get('rrr_ratio', 'N/A')}\n"
    message += f"Time: {signal_data.get('time', 'N/A')}\n\n"
    message += "#2XCleanExecution #Trading #TechnicalAnalysis"
    return message

def send_test_telegram(chat_id: str) -> bool:
    """
    Send a test trading signal via Telegram
    """
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
    
    return send_telegram_signal_sync(chat_id, test_signal)