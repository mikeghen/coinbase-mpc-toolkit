from typing import Optional, Type
from json import dumps
from langchain.pydantic_v1 import BaseModel, Field
from langchain_core.callbacks import CallbackManagerForToolRun
from langchain_core.tools import BaseTool
from coinbase_sdk.api import CoinbaseAPIWrapper, DEFAULT_WALLET_ID
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FundWalletInput(BaseModel):
    wallet_id: str = Field(description="The wallet ID to fund with testnet ETH")

class FundWalletTool(BaseTool):
    name = "FundWallet"
    description = "Fund a wallet with testnet ETH"
    args_schema: Type[BaseModel] = FundWalletInput
    return_direct: bool = True
    api: CoinbaseAPIWrapper = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.api = CoinbaseAPIWrapper()  # Initialize our API wrapper

    def _run(
        self,
        wallet_id: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
        **kwargs  # Absorbs any unexpected keyword arguments
    ) -> str:
        try:
            logger.info(f"Funding wallet with ID: {wallet_id}")
            result = self.api.fund_wallet(wallet_id)
            logger.info(f"Wallet funded successfully: {result}")
            return dumps(result)
        except Exception as e:
            logger.error(f"Funding failed for wallet ID {wallet_id}: {str(e)}")
            return f"Funding failed: {str(e)}"

# Usage example:
if __name__ == "__main__":
    tool = FundWalletTool()
    result = tool._run(wallet_id=DEFAULT_WALLET_ID)
    print(result)
