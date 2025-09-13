import telebot
from sqlalchemy.orm import Session
from app.database import crud
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
    
    # Double-check if user already exists
    if crud.get_user_by_telegram_id(db, tg_id=tg_id):
        bot.send_message(chat_id, "You already have a wallet!")
        return

    # Let the user know we're working on it
    bot.send_message(chat_id, "Generating your new XRPL wallet... 🛠️")
    
    # 1. Generate faucet wallet
    new_wallet = xrpl_wallet.create_xrpl_account()
    if not new_wallet:
        bot.send_message(chat_id, "Sorry, there was an error creating your wallet. Please try again later.")
        return

    # 2. Encrypt the seed
    encrypted_seed = encrypt_seed(new_wallet.seed)

    # 3. Save the new user to the database
    crud.save_new_user(
        db=db,
        tg_id=tg_id,
        address=new_wallet.classic_address,
        encrypted_seed=encrypted_seed
    )

    # 4. Confirm to the user
    # Corresponds to: return success_status & xrp_add
    response_text = (
        "🎉 Welcome! Your new XRPL wallet has been created and funded with test XRP.\n\n"
        f"*Address:* `{new_wallet.classic_address}`\n\n"
        "**IMPORTANT:** We have securely stored your encrypted seed. You are responsible for your account's security."
    )
    # Corresponds to: return update.message()
    bot.send_message(chat_id, response_text, parse_mode="Markdown")