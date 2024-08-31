import os
from dotenv import load_dotenv
from coinbase_sdk.client import CoinbaseClient

load_dotenv()

DEFAULT_WALLET_ID = os.getenv('DEFAULT_WALLET_ID')

class CoinbaseAPIWrapper:
    def __init__(self):
        api_key_file = os.environ.get('CDP_API_KEY_FILE')
        if not api_key_file:
            raise ValueError("CDP_API_KEY_FILE environment variable is not set")
        self.client = CoinbaseClient(api_key_file)
        self.default_wallet_id = DEFAULT_WALLET_ID

    def create_wallet(self):
        """Create a new wallet."""
        response = self.client.create_wallet()
        return response

    def get_balance(self, wallet_id):
        """Get the balance of an asset in a wallet by its ID."""
        response = self.client.get_balance(wallet_id)
        return response

    def fund_wallet(self, wallet_id):
        """Fund a wallet with testnet ETH."""
        response = self.client.fund_wallet(wallet_id, "0.1", "ETH")
        return response

    def transfer_funds(self, source_wallet_id, destination_wallet_address, amount):
        """Transfer funds between wallets."""
        response = self.client.transfer_funds(source_wallet_id, destination_wallet_address, amount, "ETH")
        return response

    def get_wallets(self):
        """Get all wallets."""
        # This endpoint is not available in the basic API, you might need to implement it differently
        raise NotImplementedError("Get all wallets is not implemented in this version of the SDK")

    def get_wallet(self, wallet_id):
        """Get a wallet by ID."""
        response = self.client.get_wallet(wallet_id)
        return response