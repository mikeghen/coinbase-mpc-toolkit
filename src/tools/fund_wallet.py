from typing import Optional, Type
from langchain.pydantic_v1 import BaseModel, Field
from langchain_core.callbacks import CallbackManagerForToolRun
from langchain_core.tools import BaseTool
from tools.coinbase_api import CoinbaseAPIWrapper, DEFAULT_WALLET_ID  


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
            result = self.api.fund_wallet(wallet_id)
            return f"Wallet funded successfully: {result}"
        except Exception as e:
            return f"Funding failed: {str(e)}"

# Usage example:
if __name__ == "__main__":
    tool = FundWalletTool()
    result = tool._run()
    print(result)