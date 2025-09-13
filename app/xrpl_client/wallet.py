from xrpl.clients import JsonRpcClient
from xrpl.wallet import generate_faucet_wallet, Wallet

# Connect to the XRPL Testnet
JSON_RPC_URL = "https://s.altnet.rippletest.net:51234/"
client = JsonRpcClient(JSON_RPC_URL)

def create_xrpl_account() -> Wallet:
    """
    Generates a new wallet from the Testnet faucet.
    Corresponds to: generate_faucet_wallet(tg_id)
    """
    try:
        # The generate_faucet_wallet function handles the creation and funding
        new_wallet = generate_faucet_wallet(client=client)
        # Corresponds to: return Wallet
        return new_wallet
    except Exception as e:
        print(f"Error generating faucet wallet: {e}")
        return None