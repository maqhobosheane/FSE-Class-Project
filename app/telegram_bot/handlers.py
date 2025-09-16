import telebot
from sqlalchemy.orm import Session
from app.database import crud
from app.services import price_service
from app.xrpl_client import wallet as xrpl_wallet
from xrpl.utils import drops_to_xrp
from app.utils.crypto import decrypt_seed, encrypt_seed
from . import keyboards

def handle_start_command(bot: telebot.TeleBot, message: telebot.types.Message, db: Session):
    """
    Handles the /start command.
    """
    tg_id = message.from_user.id
    user = crud.get_user_by_telegram_id(db, tg_id=tg_id)

    if user:
        response_text = f"Welcome back! Your XRPL address is: `{user.wallet_address}`"
        bot.send_message(
            message.chat.id, 
            response_text, 
            parse_mode="Markdown",
            reply_markup=keyboards.create_main_menu_keyboard()
        )
    else:
        response_text = "Hello! 👋 It looks like you don't have an XRPL wallet with us yet. Click the button below to create one!"
        bot.send_message(
            message.chat.id,
            response_text,
            reply_markup=keyboards.create_account_keyboard()
        )

def handle_create_command(bot: telebot.TeleBot, chat_id: int, tg_id: int, db: Session):
    """
    Handles the /create command or callback query.
    """
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
        db=db, tg_id=tg_id, address=new_wallet.classic_address, encrypted_seed=encrypted_seed
    )

    response_text = (
        "🎉 Welcome! Your new XRPL wallet has been created and funded with test XRP.\n\n"
        f"*Address:* `{new_wallet.classic_address}`\n\n"
        "**IMPORTANT:** We have securely stored your encrypted seed. You are responsible for your account's security."
    )
    bot.send_message(
        chat_id, response_text, parse_mode="Markdown", reply_markup=keyboards.create_main_menu_keyboard()
    )
    
def handle_view_price_history(bot: telebot.TeleBot, chat_id: int, tg_id: int, db: Session):
    """
    Handles the 'View Price History' button click.
    Verifies the user and sends the price history.
    """
    # 1. Verify user exists in the database using the ACTUAL user's Telegram ID
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
    
def handle_check_balance(bot: telebot.TeleBot, chat_id: int, tg_id: int, db: Session):
    """
    Handles the 'Check Balance' button click.
    """
    user = crud.get_user_by_telegram_id(db, tg_id=tg_id)
    if not user:
        bot.send_message(chat_id, "Please use /start and create a wallet first.")
        return

    balance_in_drops = xrpl_wallet.get_account_balance(user.wallet_address)
    
    if balance_in_drops is not None:
        balance_in_xrp = drops_to_xrp(balance_in_drops)
        response_text = f"💰 Your current balance is: *{balance_in_xrp:,.6f} XRP*"
    else:
        response_text = "Sorry, there was an error fetching your account balance."
        
    bot.send_message(chat_id, response_text, parse_mode="Markdown")
    
def handle_send_xrp(bot: telebot.TeleBot, chat_id: int, tg_id: int, db: Session):
    """
    Starts the send XRP process.
    """
    user = crud.get_user_by_telegram_id(db, tg_id=tg_id)
    if not user:
        bot.send_message(chat_id, "Please use /start and create a wallet first.")
        return
    
    msg = bot.send_message(chat_id, "Please reply with the destination XRPL address (r...).")
    bot.register_next_step_handler(msg, lambda m: get_recipient_address(bot, m, db))

def get_recipient_address(bot: telebot.TeleBot, message: telebot.types.Message, db: Session):
    """
    Receives the recipient address, validates it, and asks for the amount.
    """
    chat_id = message.chat.id
    recipient_address = message.text.strip()

    if xrpl_wallet.get_account_balance(recipient_address) is None:
        bot.send_message(chat_id, "❌ That recipient address doesn't seem to be valid or activated on the testnet. Please start over by clicking the 'Send XRP' button again.")
        return
        
    msg = bot.send_message(chat_id, f"✅ Address confirmed. Now, please reply with the amount of XRP you wish to send.")
    bot.register_next_step_handler(msg, lambda m: get_amount_and_send(bot, m, db, recipient_address))

def get_amount_and_send(bot: telebot.TeleBot, message: telebot.types.Message, db: Session, recipient_address: str):
    """
    Receives the amount, validates balance, and executes the transaction.
    """
    tg_id = message.from_user.id
    chat_id = message.chat.id
    amount_to_send_str = message.text.strip()
    
    try:
        amount_to_send = float(amount_to_send_str)
        if amount_to_send <= 0:
            raise ValueError("Amount must be positive.")
    except (ValueError, TypeError):
        bot.send_message(chat_id, "❌ Invalid amount. Please start over by clicking the 'Send XRP' button again.")
        return
        
    sender = crud.get_user_by_telegram_id(db, tg_id=tg_id)
    if not sender:
        bot.send_message(chat_id, "Could not find your user data. Please /start again.")
        return

    bot.send_message(chat_id, "Verifying your balance...")
    sender_balance_drops = xrpl_wallet.get_account_balance(sender.wallet_address)
    
    if sender_balance_drops is None:
        bot.send_message(chat_id, "❌ Could not verify your balance. Please try again later.")
        return
        
    sender_balance_xrp = float(drops_to_xrp(sender_balance_drops))
    available_balance = sender_balance_xrp - 1
    
    if available_balance < amount_to_send:
        bot.send_message(chat_id, f"❌ Insufficient funds. Your available balance is {available_balance:,.6f} XRP (after the 1 XRP reserve). Please start over.")
        return
        
    bot.send_message(chat_id, "Balance confirmed. Processing your transaction... 🚀")
    
    decrypted_seed = decrypt_seed(sender.encrypted_seed)
    success = xrpl_wallet.send_xrp(decrypted_seed, str(amount_to_send), recipient_address)

    if success:
        bot.send_message(chat_id, f"✅ Transaction successful! You sent {amount_to_send} XRP to `{recipient_address}`.", parse_mode="Markdown")
    else:
        bot.send_message(chat_id, "❌ Transaction failed. The payment could not be processed by the ledger.")