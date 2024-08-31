from typing import Optional, Type
from json import dumps
from langchain.pydantic_v1 import BaseModel, Field
from langchain_core.callbacks import CallbackManagerForToolRun
from langchain_core.tools import BaseTool
from coinbase_sdk.api import CoinbaseAPIWrapper  # Import our API wrapper
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TransferFundsInput(BaseModel):
    source_wallet_id: str = Field(description="The wallet ID from which ETH will be sent")
    destination_wallet_address: str = Field(description="The wallet address to which ETH will be sent")
    amount: str = Field(description="The amount of ETH to send (as a string, e.g., '0.1')")

class TransferFundsTool(BaseTool):
    name = "CreateTransfer"
    description = "Send or transfer an amount of ETH from one wallet to another"
    args_schema: Type[BaseModel] = TransferFundsInput
    return_direct: bool = True
    api: CoinbaseAPIWrapper = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.api = CoinbaseAPIWrapper()  # Initialize our API wrapper

    def _run(
        self, 
        source_wallet_id: str,
        destination_wallet_address: str, 
        amount: str, 
        run_manager: Optional[CallbackManagerForToolRun] = None,
        **kwargs  # Absorbs any unexpected keyword arguments
    ) -> str:
        try:
            logger.info(f"Initiating transfer of {amount} ETH from wallet {source_wallet_id} to address {destination_wallet_address}")
            result = self.api.transfer_funds(source_wallet_id, destination_wallet_address, amount)
            logger.info(f"Transfer result: {result}")
            # Remove some unneeded text from the result before returning it
            del result["transfer"]["model"]["transaction"]["unsigned_payload"]
            del result["transfer"]["model"]["unsigned_payload"]
            return dumps(result)
        except Exception as e:
            logger.error(f"Transfer failed from wallet {source_wallet_id} to {destination_wallet_address}: {str(e)}")
            return f"Transfer failed: {str(e)}"

# Usage example:
if __name__ == "__main__":
    tool = TransferFundsTool()
    result = tool._run(
        source_wallet_id="674069f0-3de9-40bf-a06b-22a9573c7861",
        destination_wallet_address="0xa7979BF6Ce644E4e36da2Ee65Db73c3f5A0dF895",
        amount="0.0001"
    )
    print(result)
