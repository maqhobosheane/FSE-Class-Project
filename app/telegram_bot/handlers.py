import telebot
from sqlalchemy.orm import Session
from app.database import crud
from app.services import price_service
from app.xrpl_client import wallet as xrpl_wallet
from app.utils.crypto import encrypt_seed
from . import keyboards

def handle_start_command(bot: telebot.TeleBot, message: telebot.types.Message, db: Session):
    """
    Handles the /start command.
    Checks if user exists and sends the appropriate welcome message.
    """
    tg_id = message.from_user.id
    user = crud.get_user_by_telegram_id(db, tg_id=tg_id)

    if user:
        # User exists
        response_text = f"Welcome back! Your XRPL address is: `{user.wallet_address}`"
        bot.send_message(message.chat.id, response_text, parse_mode="Markdown")
    else:
        # Corresponds to: return user_not_exist
        response_text = "Hello! 👋 It looks like you don't have an XRPL wallet with us yet. Click the button below to create one!"
        # Corresponds to: return update.message() (buttons shown)
        bot.send_message(
            message.chat.id,
            response_text,
            reply_markup=keyboards.create_account_keyboard()
        )

def handle_create_command(bot: telebot.TeleBot, message: telebot.types.Message, db: Session):
    """
    Handles the /create command or callback query.
    Generates a new wallet, encrypts the seed, and saves the user.
    """
    tg_id = message.from_user.id
    chat_id = message.chat.id
    
    if crud.get_user_by_telegram_id(db, tg_id=tg_id):
        bot.send_message(chat_id, "You already have a wallet! Here are your options:", reply_markup=keyboards.create_main_menu_keyboard())
        return

    bot.send_message(chat_id, "Generating your new XRPL wallet... 🛠️")
    
    new_wallet = xrpl_wallet.create_xrpl_account()
    if not new_wallet:
        bot.send_message(chat_id, "Sorry, there was an error creating your wallet. Please try again later.")
        return

    encrypted_seed = encrypt_seed(new_wallet.seed)

    crud.save_new_user(
        db=db,
        tg_id=tg_id,
        address=new_wallet.classic_address,
        encrypted_seed=encrypted_seed
    )

    response_text = (
        "🎉 Welcome! Your new XRPL wallet has been created and funded with test XRP.\n\n"
        f"*Address:* `{new_wallet.classic_address}`\n\n"
        "**IMPORTANT:** We have securely stored your encrypted seed. You are responsible for your account's security."
    )
    
    # Send the success message and attach the new main menu keyboard <- MM
    bot.send_message(
        chat_id, 
        response_text, 
        parse_mode="Markdown",
        reply_markup=keyboards.create_main_menu_keyboard() 
    )
    
def handle_view_price_history(bot: telebot.TeleBot, message: telebot.types.Message, db: Session):
    """
    Handles the 'View Price History' button click.
    Verifies the user and sends the price history.
    """
    tg_id = message.from_user.id
    chat_id = message.chat.id
    
    # 1. Verify user exists in the database
    user = crud.get_user_by_telegram_id(db, tg_id=tg_id)
    if not user:
        bot.send_message(chat_id, "Please use /start and create a wallet first.")
        return

    # Let the user know we're working on it
    bot.send_message(chat_id, "Fetching price history... 📈")

    # 2. Call the price service to get the data
    price_message = price_service.get_price_history()
    
    # 3. Send the formatted message to the user
    bot.send_message(chat_id, price_message, parse_mode="Markdown")