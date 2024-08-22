from typing import Optional, Type
from langchain.pydantic_v1 import BaseModel, Field
from langchain_core.callbacks import CallbackManagerForToolRun
from langchain_core.tools import BaseTool
from tools.coinbase_api import CoinbaseAPIWrapper, DEFAULT_WALLET_ID  


class FundWalletTool(BaseTool):
    name = "FundWallet"
    description = "Fund a wallet with testnet ETH"
    return_direct: bool = True
    api: CoinbaseAPIWrapper = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.api = CoinbaseAPIWrapper()  # Initialize our API wrapper

    def _run(
        self,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        try:
            result = self.api.fund_wallet(DEFAULT_WALLET_ID)
            return f"Wallet funded successfully: {result}"
        except Exception as e:
            return f"Funding failed: {str(e)}"

# Usage example:
if __name__ == "__main__":
    tool = FundWalletTool()
    result = tool._run()
    print(result)