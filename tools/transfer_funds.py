from typing import Optional, Type
from langchain.pydantic_v1 import BaseModel, Field
from langchain_core.callbacks import CallbackManagerForToolRun
from langchain_core.tools import BaseTool
from coinbase_api import CoinbaseAPIWrapper  # Import our API wrapper

class TransferFundsInput(BaseModel):
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
        destination_wallet_address: str, 
        amount: str, 
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        try:
            amount = int(float(amount) * 1e18)
            result = self.api.transfer_funds(self.api.default_wallet_id, destination_wallet_address, amount)
            return f"Transfer successful: {result}"
        except Exception as e:
            return f"Transfer failed: {str(e)}"

# Usage example:
if __name__ == "__main__":
    tool = TransferFundsTool()
    result = tool._run(
        destination_wallet_address="0xa7979BF6Ce644E4e36da2Ee65Db73c3f5A0dF895",
        amount="0.0001"
    )
    print(result)