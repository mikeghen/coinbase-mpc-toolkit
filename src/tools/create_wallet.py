from typing import Optional, Type, Dict, Any
from json import dumps
from langchain_core.callbacks import CallbackManagerForToolRun
from langchain_core.tools import BaseTool
from coinbase_sdk.api import CoinbaseAPIWrapper
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CreateWalletTool(BaseTool):
    name = "CreateWallet"
    description = "Generate a new Ethereum wallet and return the address and wallet ID"
    return_direct: bool = True
    api: CoinbaseAPIWrapper = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.api = CoinbaseAPIWrapper()

    def _run(
        self,
        run_manager: Optional[CallbackManagerForToolRun] = None,
        **kwargs  # Absorbs any unexpected keyword arguments
    ) -> dict:
        try:
            logger.info("Creating a new Ethereum wallet...")
            # API Saves the wallet's sensitive information, so we don't need to return it here.
            result = self.api.create_wallet()
            wallet = self.api.get_wallet(result["walletId"])
            logger.info(f"Wallet created successfully: {result}") 
            ret = {
                "message": result["message"],
                "address": wallet["wallet"]["addresses"][0]["id"],
                "wallet_id": result["walletId"]
            }
            logger.info(f"Returning wallet information: {ret}")
            return dumps(ret)
        except Exception as e:
            logger.error(f"Failed to create wallet: {str(e)}")
            return {"error": f"Failed to create wallet: {str(e)}"}

# Usage example:
if __name__ == "__main__":
    tool = CreateWalletTool()
    result = tool._run()
    print(result)
