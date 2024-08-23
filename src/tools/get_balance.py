from typing import Optional, Type
from langchain.pydantic_v1 import BaseModel, Field
from langchain_core.callbacks import CallbackManagerForToolRun
from langchain_core.tools import BaseTool
from tools.coinbase_api import CoinbaseAPIWrapper  # Import our API wrapper

class GetEthBalanceInput(BaseModel):
    wallet_id: str = Field(description="The ID of the wallet to retrieve the ETH balance from")

class GetEthBalanceTool(BaseTool):
    name = "GetEthBalance"
    description = "Retrieve the ETH balance of a specified wallet"
    args_schema: Type[BaseModel] = GetEthBalanceInput
    return_direct: bool = True
    api: CoinbaseAPIWrapper = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.api = CoinbaseAPIWrapper()  # Initialize our API wrapper

    def _run(
        self, 
        wallet_id: str, 
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        try:
            balance = self.api.get_balance(wallet_id, "ETH")  # Assuming `get_balance` is a method in CoinbaseAPIWrapper
            return f"ETH Balance for wallet {wallet_id}: {balance}"
        except Exception as e:
            return f"Failed to retrieve ETH balance: {str(e)}"

# Usage example:
if __name__ == "__main__":
    tool = GetEthBalanceTool()
    result = tool._run(
        wallet_id="your_wallet_id_here"
    )
    print(result)
