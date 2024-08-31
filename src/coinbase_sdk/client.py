import json
import time
import requests
import os
import logging
from typing import Dict, Any
from coinbase import jwt_generator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CoinbaseClient:
    def __init__(self, api_key_file: str = None, base_url: str = "https://api.cdp.coinbase.com"):
        logger.info(f"Initializing CoinbaseClient with base_url: {base_url}")
        self.base_url = base_url
        self.api_key_data = self._load_api_key(api_key_file)
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
        })
        logger.info("CoinbaseClient initialized successfully")

    def _load_api_key(self, api_key_file: str = None) -> Dict[str, str]:
        logger.info("Loading API key")
        if api_key_file is None:
            api_key_file = os.environ.get('CDP_API_KEY_FILE')
            logger.info(f"Using CDP_API_KEY_FILE from environment: {api_key_file}")
        
        if not api_key_file:
            logger.error("API key file path not provided and CDP_API_KEY_FILE environment variable is not set")
            raise ValueError("API key file path not provided and CDP_API_KEY_FILE environment variable is not set")
        
        try:
            with open(api_key_file, 'r') as f:
                api_key_data = json.load(f)
                if 'name' not in api_key_data or 'privateKey' not in api_key_data:
                    logger.error("API key file must contain 'name' and 'privateKey'")
                    raise ValueError("API key file must contain 'name' and 'privateKey'")
                logger.info("API key loaded successfully")
                return api_key_data
        except FileNotFoundError:
            logger.error(f"API key file not found: {api_key_file}")
            raise FileNotFoundError(f"API key file not found: {api_key_file}")
        except json.JSONDecodeError:
            logger.error("API key file is not valid JSON")
            raise ValueError("API key file is not valid JSON")

    def _generate_jwt(self, method: str, uri: str) -> str:
        logger.info("Generating JWT token")
        api_key = self.api_key_data["name"]
        api_secret = self.api_key_data["privateKey"]
        logger.info(f"API key: {api_key}")
        logger.info(f"API secret: {api_secret}")
        
        jwt_uri = jwt_generator.format_jwt_uri(method, uri)
        jwt_token = jwt_generator.build_rest_jwt(jwt_uri, api_key, api_secret)
        
        logger.info("JWT token generated successfully")
        return jwt_token

    def _request(self, method: str, endpoint: str, params: Dict[str, Any] = None, data: Dict[str, Any] = None) -> Dict[str, Any]:
        url = f"{self.base_url}{endpoint}"
        logger.info(f"Making {method} request to {url}")
        jwt_token = self._generate_jwt(method, endpoint)
        headers = {
            "Authorization": f"Bearer {jwt_token}",
            "Accept": "application/json"
        }
        logger.info(f"Headers: {headers}")
        logger.info(f"Params: {params}")
        logger.info(f"Data: {data}")
        logger.info(f"Method: {method}")
        logger.info(f"URL: {url}")
        response = self.session.request(method, url, headers=headers, params=params, json=data)
        logger.info(f"Response status code: {response.status_code}")
        response.raise_for_status()
        logger.info("Request successful")
        return response.json()

    def _cdp_request(self, method: str, endpoint: str, payload: str = '') -> Dict[str, Any]:
        import http.client

        logger.info(f"Making CDP {method} request to {endpoint}")
        conn = http.client.HTTPSConnection(self.base_url.replace("https://", ""))
        jwt_token = self._generate_jwt(method, endpoint)
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f"Bearer {jwt_token}"
        }
        conn.request(method, endpoint, payload, headers)
        res = conn.getresponse()
        logger.info(f"CDP Response status: {res.status}")
        data = res.read()
        logger.info(f"CDP Response data: {data}")
        response_data = json.loads(data.decode("utf-8"))
        logger.info("CDP Request successful")
        return response_data

    def create_wallet(self) -> Dict[str, Any]:
        logger.info("Creating new wallet")
        payload = json.dumps({
            "wallet": {
                "network_id": "1",
                "use_server_signer": False
            }
        })
        response = self._cdp_request("POST", "/platform/v1/wallets", payload)
        logger.info(f"Wallet creation response: {response}")
        if not isinstance(response, dict):
            logger.error("Invalid response format; expected a dictionary.")
            raise ValueError("Invalid response format; expected a dictionary.")
        logger.info("Wallet created successfully")
        return response    

    def get_wallet(self, wallet_id: str) -> Dict[str, Any]:
        logger.info(f"Getting wallet with ID: {wallet_id}")
        response = self._cdp_request("GET", f"/platform/v1/wallets/{wallet_id}")
        logger.info(f"Get wallet response: {response}")
        return response
    
    def fund_wallet(self, wallet_id: str, address_id: str) -> Dict[str, Any]:
        logger.info(f"Funding wallet with ID: {wallet_id}, address ID: {address_id}")
        response = self._cdp_request("POST", f"/platform/v1/wallets/{wallet_id}/addresses/{address_id}/faucet")
        logger.info(f"Fund wallet response: {response}")
        return response

    def transfer_funds(self, source_wallet_id: str, destination_address: str, amount: str, currency: str) -> Dict[str, Any]:
        logger.info(f"Transferring {amount} {currency} from wallet {source_wallet_id} to {destination_address}")
        payload = json.dumps({
            "to": destination_address,
            "amount": amount,
            "currency": currency
        })
        response = self._cdp_request("POST", f"/platform/v1/wallets/{source_wallet_id}/addresses/{destination_address}/transfers", payload)
        logger.info(f"Transfer funds response: {response}")
        return response

    def get_balance(self, wallet_id: str) -> Dict[str, Any]:
        logger.info(f"Getting balance for wallet ID: {wallet_id}")
        response = self._request("GET", f"/v2/accounts/{wallet_id}/balance")
        logger.info(f"Get balance response: {response}")
        return response
