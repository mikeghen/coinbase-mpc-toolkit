from typing import Optional, Type, Dict, Any
from web3 import Web3
from langchain.pydantic_v1 import BaseModel, Field
from langchain_core.callbacks import CallbackManagerForToolRun
from langchain_core.tools import BaseTool
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GetWalletBalanceInput(BaseModel):
    wallet_address: str = Field(description="The Ethereum wallet address to check the balance for")

class GetWalletBalanceOutput(BaseModel):
    address: str
    balance_eth: float
    balance_wei: int

class GetWalletBalanceTool(BaseTool):
    name = "GetWalletBalance"
    description = "Retrieve the ETH balance of a specified wallet address using web3.py"
    args_schema: Type[BaseModel] = GetWalletBalanceInput
    return_direct: bool = True
    web3_provider_url: str = Field(..., description="The URL of the Ethereum node to connect to")
    web3: Web3 = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._initialize_web3()

    def _initialize_web3(self):
        self.web3 = Web3(Web3.HTTPProvider(self.web3_provider_url))

    def _ensure_connection(self):
        if not self.web3 or not self.web3.is_connected():
            logger.info("Reconnecting to Ethereum node...")
            self._initialize_web3()
        if not self.web3.is_connected():
            raise ConnectionError("Failed to connect to the Ethereum node.")

    def _run(
        self,
        wallet_address: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
        **kwargs  # Absorbs any unexpected keyword arguments
    ) -> Dict[str, Any]:
        try:
            self._ensure_connection()

            # Normalize the address
            normalized_address = self.web3.to_checksum_address(wallet_address)

            # Get the balance and convert it from Wei to Ether
            balance_wei = self.web3.eth.get_balance(normalized_address)
            balance_eth = self.web3.from_wei(balance_wei, 'ether')
            
            return GetWalletBalanceOutput(
                address=normalized_address,
                balance_eth=float(balance_eth),
                balance_wei=balance_wei
            ).dict()
        except ValueError as ve:
            logger.error(f"Invalid Ethereum address: {wallet_address}")
            raise ValueError(f"Invalid Ethereum address: {wallet_address}") from ve
        except ConnectionError as ce:
            logger.error(f"Connection error: {str(ce)}")
            raise
        except Exception as e:
            logger.error(f"Failed to retrieve ETH balance: {str(e)}")
            raise

# Usage example:
if __name__ == "__main__":
    tool = GetWalletBalanceTool(web3_provider_url="https://mainnet.infura.io/v3/YOUR_INFURA_PROJECT_ID")
    try:
        result = tool._run(wallet_address="your_wallet_address_here")
        print(f"Address: {result['address']}")
        print(f"Balance: {result['balance_eth']} ETH")
        print(f"Balance in Wei: {result['balance_wei']}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")