from telebot import types

def create_account_keyboard():
    """Generates a simple inline keyboard with a '/create' button."""
    keyboard = types.InlineKeyboardMarkup()
    create_button = types.InlineKeyboardButton(text="Create Wallet 🚀", callback_data="create_wallet")
    keyboard.add(create_button)
    return keyboard