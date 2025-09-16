# app/telegram_bot/keyboards.py
from telebot import types

def create_account_keyboard():
    """Generates a simple inline keyboard with a '/create' button."""
    keyboard = types.InlineKeyboardMarkup()
    create_button = types.InlineKeyboardButton(text="Create Wallet 🚀", callback_data="create_wallet")
    keyboard.add(create_button)
    return keyboard

def create_main_menu_keyboard():
    """Generates the main menu keyboard with user options."""
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    
    learn_more_button = types.InlineKeyboardButton(
        text="Learn More About the Bot 📚", 
        callback_data="learn_more"
    )
    check_balance_button = types.InlineKeyboardButton(
        text="Check Balance 💰", 
        callback_data="check_balance"
    )
    send_xrp_button = types.InlineKeyboardButton(
        text="Send XRP 💸", 
        callback_data="send_xrp"
    )
    price_history_button = types.InlineKeyboardButton(
        text="View Price History 📈", 
        callback_data="view_price_history"
    )
    
    keyboard.add(
        learn_more_button, 
        check_balance_button, 
        send_xrp_button, 
        price_history_button
    )
    return keyboard