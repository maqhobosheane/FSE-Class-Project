from xrpl.clients import JsonRpcClient
from xrpl.wallet import Wallet, generate_faucet_wallet
from xrpl.models.requests.account_info import AccountInfo
from xrpl.models.transactions import Payment
from xrpl.transaction import submit_and_wait
from xrpl.utils import xrp_to_drops, drops_to_xrp
from xrpl.models.requests import AccountTx
from datetime import datetime, timedelta

# Use the synchronous client, which is simpler for a Flask app
JSON_RPC_URL = "https://s.altnet.rippletest.net:51234/"
client = JsonRpcClient(JSON_RPC_URL)

def create_xrpl_account() -> Wallet:
    """
    Generates a new wallet from the Testnet faucet.
    """
    try:
        # The synchronous generate_faucet_wallet works directly
        new_wallet = generate_faucet_wallet(client=client)
        return new_wallet
    except Exception as e:
        print(f"Error generating faucet wallet: {e}")
        return None

def get_account_balance(address: str) -> str:
    """
    Queries the XRPL for the balance of a given address in drops.
    """
    try:
        acc_info = AccountInfo(account=address, ledger_index="validated")
        response = client.request(acc_info)
        return response.result.get("account_data", {}).get("Balance")
    except Exception as e:
        print(f"Error fetching account balance for {address}: {e}")
        return None

def send_xrp(sender_seed: str, amount_xrp: str, destination_address: str) -> bool:
    """
    Constructs, signs, and submits a payment transaction to the XRPL.
    Returns True on success, False on failure.
    """
    try:
        sender_wallet = Wallet.from_seed(sender_seed)
        
        acc_info = AccountInfo(account=sender_wallet.classic_address, ledger_index="validated")
        response = client.request(acc_info)
        
        if not response.is_successful():
            print(f"Failed to get account info for {sender_wallet.classic_address}")
            return False
        
        current_sequence = response.result.get("account_data", {}).get("Sequence", 0)
        
        payment = Payment(
            account=sender_wallet.classic_address,
            amount=xrp_to_drops(float(amount_xrp)),
            destination=destination_address,
            sequence=current_sequence
        )

        response = submit_and_wait(transaction=payment, client=client, wallet=sender_wallet)
        result = response.result
        
        if result.get("meta", {}).get("TransactionResult") == "tesSUCCESS":
            print(f"Transaction successful: {result.get('hash')}")
            return True
        else:
            print("--- TRANSACTION FAILED ---")
            print(f"  Result Code: {result.get('meta', {}).get('TransactionResult')}")
            print(f"  Engine Result: {result.get('engine_result')}")
            print(f"  Engine Message: {result.get('engine_result_message')}")
            print("--------------------------")
            return False

    except Exception as e:
        print(f"Error during XRP payment: {e}")
        return False


def get_transaction_history(address: str, limit: int = 5) -> list:
    """
    Fetches the transaction history for a given XRPL address.
    """
    try:
        
        request = AccountTx(account=address, limit=limit)
        response = client.request(request)
        
        transactions = []
        for tx in response.result.get('transactions', []):
            tx_data = tx.get('tx', {})
            # Ensure the transaction is a payment and has a standard XRP amount
            if tx_data.get('TransactionType') == 'Payment' and isinstance(tx_data.get('Amount'), str):
                amount = drops_to_xrp(tx_data['Amount'])
                
                if tx_data['Account'] == address:
                    # We sent this payment
                    tx_type = 'sent'
                    counterparty = tx_data['Destination']
                else:
                    # We received this payment
                    tx_type = 'received'
                    counterparty = tx_data['Account']
                
                transactions.append({
                    'type': tx_type,
                    'amount': f"{float(amount):,.6f}",
                    'counterparty': counterparty
                })
        return transactions
    except Exception as e:
        print(f"--- FAILED to get tx history for {address}: {e} ---")
        return []