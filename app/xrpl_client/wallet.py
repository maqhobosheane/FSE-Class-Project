from xrpl.clients import JsonRpcClient
from xrpl.wallet import generate_faucet_wallet, Wallet
from xrpl.models.requests.account_info import AccountInfo
from xrpl.utils import drops_to_xrp

# Connect to the XRPL Testnet
JSON_RPC_URL = "https://s.altnet.rippletest.net:51234/"
client = JsonRpcClient(JSON_RPC_URL)

def create_xrpl_account() -> Wallet:
    """Generates a new wallet from the Testnet faucet."""
    try:
        new_wallet = generate_faucet_wallet(client=client)
        return new_wallet
    except Exception as e:
        print(f"Error generating faucet wallet: {e}")
        return None

def get_account_balance(address: str) -> str:
    """Queries the XRPL for the balance of a given address."""
    try:
        acc_info = AccountInfo(account=address, ledger_index="validated")
        response = client.request(acc_info)
        
        # The balance is in the result, under 'account_data', in 'Balance'
        return response.result.get("account_data", {}).get("Balance")
    except Exception as e:
        print(f"Error fetching account balance for {address}: {e}")
        return None