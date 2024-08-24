import os
import requests
from dotenv import load_dotenv

load_dotenv()

DEFAULT_WALLET_ID = os.getenv('DEFAULT_WALLET_ID')
COINBASE_API_URL = os.getenv('COINBASE_API_URL')

class CoinbaseAPIWrapper:
    def __init__(self, base_url=COINBASE_API_URL):
        self.base_url = base_url
        self.default_wallet_id = DEFAULT_WALLET_ID

    def create_wallet(self):
        """Create a new wallet."""
        response = requests.post(f"{self.base_url}/create-wallet")
        response.raise_for_status()
        return response.json()
    
    def get_balance(self, wallet_id):
        """Get the balance of an asset in a wallet by its ID."""
        response = requests.get(f"{self.base_url}/get-balance/{wallet_id}")
        response.raise_for_status()
        return response.json()

    def fund_wallet(self, wallet_id):
        """Fund a wallet with testnet ETH."""
        data = {"walletId": wallet_id}
        response = requests.post(f"{self.base_url}/fund-wallet", json=data)
        response.raise_for_status()
        return response.json()

    def transfer_funds(self, source_wallet_id, destination_wallet_address, amount):
        """Transfer funds between wallets."""
        data = {
            "sourceWalletId": source_wallet_id,
            "destinationWalletAddress": destination_wallet_address,
            "amount": amount
        }
        response = requests.post(f"{self.base_url}/transfer-funds", json=data)
        response.raise_for_status()
        return response.json()

    def trade_assets(self, wallet_id, from_asset_id, to_asset_id, amount):
        """Trade assets within a wallet."""
        data = {
            "walletId": wallet_id,
            "fromAssetId": from_asset_id,
            "toAssetId": to_asset_id,
            "amount": amount
        }
        response = requests.post(f"{self.base_url}/trade-assets", json=data)
        response.raise_for_status()
        return response.json()
    
    def get_wallets(self):
        """Get all wallets."""
        response = requests.get(f"{self.base_url}/get-wallets")
        response.raise_for_status()
        return response.json()
    
    def get_wallet(self, wallet_id):
        """Get a wallet by ID."""
        response = requests.get(f"{self.base_url}/get-wallet/{wallet_id}")
        response.raise_for_status()
        return response.json()

# # Usage example:
# if __name__ == "__main__":
#     api = CoinbaseAPIWrapper()
#     try:
#         # Create a wallet
#         wallet = api.create_wallet()
#         print("Created wallet:", wallet)
#
#         # Fund the wallet
#         funding = api.fund_wallet(wallet['wallet']['id'])
#         print("Funded wallet:", funding)
#
#         # Create another wallet for transfer demonstration
#         wallet2 = api.create_wallet()
#         print("Created second wallet:", wallet2)
#
#         # Transfer funds
#         transfer = api.transfer_funds(wallet['wallet']['id'], wallet2['wallet']['id'], "0.1")
#         print("Transferred funds:", transfer)
#
#         # Trade assets
#         trade = api.trade_assets(wallet['wallet']['id'], "ETH", "BTC", "0.05")
#         print("Traded assets:", trade)
#
#     except requests.exceptions.RequestException as e:
#         print("An error occurred:", e)