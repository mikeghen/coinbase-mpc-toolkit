import json
import time
import requests
import os
import logging
from typing import Dict, Any
from jose import jws, jwk 
import secrets  
from requests.models import PreparedRequest
import urllib.parse  # Add this import at the top of the file

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CoinbaseClient:
    def __init__(self, api_key_file: str = None, base_url: str = "https://api.cdp.coinbase.com", debugging: bool = False):
        logger.info(f"Initializing CoinbaseClient with base_url: {base_url}")
        self.base_url = base_url
        self.api_key_data = self._load_api_key(api_key_file)
        self.session = requests.Session()
        self.debugging = debugging
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
        
        # Extract PEM key
        pem_private_key = self._extract_pem_key(api_secret)

        # Create JWK from PEM
        private_key = jwk.construct(pem_private_key.encode('utf-8'), 'ES256')

        # Prepare JWT header
        header = {
            "alg": "ES256",
            "kid": api_key,
            "typ": "JWT",
            "nonce": self._generate_nonce(),
        }

        # Prepare claims
        claims = {
            "sub": api_key,
            "iss": "cdp",
            "aud": ["cdp_service"],
            "nbf": int(time.time()),
            "exp": int(time.time()) + 60,  # +1 minute
            "uris": [f"{method} {uri}"],
        }

        # Create JWT
        jwt_token = jws.sign(claims, private_key, algorithm='ES256', headers=header)
        
        logger.info("JWT token generated successfully")
        return jwt_token

    def _extract_pem_key(self, private_key_string: str) -> str:
        pem_header = "-----BEGIN EC PRIVATE KEY-----"
        pem_footer = "-----END EC PRIVATE KEY-----"
        private_key_string = private_key_string.replace("\n", "")
        
        if private_key_string.startswith(pem_header) and private_key_string.endswith(pem_footer):
            return private_key_string
        
        raise ValueError("Invalid private key format")

    def _generate_nonce(self) -> str:
        return ''.join(secrets.choice('0123456789') for _ in range(16))  # Generate a random nonce

    def _get_correlation_data(self) -> str:
        return "sdk_version=1.0.0,sdk_language=python"

    async def authenticate_request(self, request: PreparedRequest) -> PreparedRequest:
        method = request.method.upper()
        url = request.url.replace(self.base_url, '')  # Remove base URL to get the endpoint
        token = self._generate_jwt(method, url)

        if self.debugging:
            logger.info(f"API REQUEST: {method} {url}")

        request.headers["Authorization"] = f"Bearer {token}"
        request.headers["Content-Type"] = "application/json"
        request.headers["Correlation-Context"] = self._get_correlation_data()
        return request

    async def _cdp_request(self, method: str, endpoint: str, payload: Dict[str, Any] = None) -> Dict[str, Any]:
        url = f"{self.base_url}{endpoint}"
        request = requests.Request(method, url, json=payload)
        prepared_request = self.session.prepare_request(request)
        authenticated_request = await self.authenticate_request(prepared_request)

        response = self.session.send(authenticated_request)
        response.raise_for_status()
        return response.json()

    async def create_wallet(self) -> Dict[str, Any]:
        logger.info("Creating new wallet")
        payload = {
            "wallet": {
                "network_id": "1",
                "use_server_signer": False
            }
        }
        response = await self._cdp_request("POST", "/platform/v1/wallets", payload)
        logger.info(f"Wallet creation response: {response}")
        logger.info("Wallet created successfully")
        return response    

    async def get_wallet(self, wallet_id: str) -> Dict[str, Any]:
        logger.info(f"Getting wallet with ID: {wallet_id}")
        response = await self._cdp_request("GET", f"/platform/v1/wallets/{wallet_id}")
        logger.info(f"Get wallet response: {response}")
        return response
    
    async def fund_wallet(self, wallet_id: str, address_id: str) -> Dict[str, Any]:
        logger.info(f"Funding wallet with ID: {wallet_id}, address ID: {address_id}")
        response = await self._cdp_request("POST", f"/platform/v1/wallets/{wallet_id}/addresses/{address_id}/faucet")
        logger.info(f"Fund wallet response: {response}")
        return response

    async def transfer_funds(self, source_wallet_id: str, destination_address: str, amount: str, currency: str) -> Dict[str, Any]:
        logger.info(f"Transferring {amount} {currency} from wallet {source_wallet_id} to {destination_address}")
        payload = {
            "to": destination_address,
            "amount": amount,
            "currency": currency
        }
        response = await self._cdp_request("POST", f"/platform/v1/wallets/{source_wallet_id}/addresses/{destination_address}/transfers", payload)
        logger.info(f"Transfer funds response: {response}")
        return response
