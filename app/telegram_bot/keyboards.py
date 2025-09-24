from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

def create_main_menu_keyboard():
    """
    Creates the main menu keyboard with a 2x2 grid and a history button below.
    """
    markup = InlineKeyboardMarkup()
    
    # Define all five buttons
    btn_learn_more = InlineKeyboardButton("💡 Learn More", callback_data='learn_more')
    btn_check_balance = InlineKeyboardButton("💰 Check Balance", callback_data='check_balance')
    btn_send_xrp = InlineKeyboardButton("💸 Send XRP", callback_data='send_xrp')
    btn_view_price = InlineKeyboardButton("📈 View Price History", callback_data='view_price_history')
    
    btn_view_tx_history = InlineKeyboardButton("📜 View Transaction History", callback_data='view_tx_history')
    
    # Add buttons in rows 
    markup.row(btn_learn_more, btn_check_balance)
    markup.row(btn_send_xrp, btn_view_price)
    markup.row(btn_view_tx_history) # Add the txhistory button on its own full-width row
    
    return markup

def create_account_keyboard():
    """
    Creates the initial keyboard for new users.
    """
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton("✅ Create Wallet", callback_data='create_wallet'),
        InlineKeyboardButton("💡 Learn More", callback_data='learn_more')
    )
    return markup