from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

def create_main_menu_keyboard():
    """
    Creates the main 2x2 menu keyboard.
    - Row 1: Learn More, Check Balance
    - Row 2: Send XRP, View Price History
    """
    markup = InlineKeyboardMarkup()
    
    # --- UX IMPROVEMENT: Create a 2x2 grid layout ---
    # Define all four buttons
    btn_learn_more = InlineKeyboardButton("💡 Learn More", callback_data='learn_more')
    btn_check_balance = InlineKeyboardButton("💰 Check Balance", callback_data='check_balance')
    btn_send_xrp = InlineKeyboardButton("💸 Send XRP", callback_data='send_xrp')
    btn_view_price = InlineKeyboardButton("📈 View Price History", callback_data='view_price_history')
    
    # Add buttons in rows of two
    markup.row(btn_learn_more, btn_check_balance)
    markup.row(btn_send_xrp, btn_view_price)
    
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