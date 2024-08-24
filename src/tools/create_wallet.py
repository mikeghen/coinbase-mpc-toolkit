from typing import Optional, Type
from web3 import Web3, Account
from langchain.pydantic_v1 import BaseModel, Field
from langchain_core.callbacks import CallbackManagerForToolRun
from langchain_core.tools import BaseTool
from tools.coinbase_api import CoinbaseAPIWrapper


class CreateWalletTool(BaseTool):
    name = "CreateWallet"
    description = "Generate a new Ethereum wallet and return the address and private key"
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
            result = self.api.create_wallet()
            wallet = self.api.get_wallet(result["walletId"])
            return f"Wallet: {wallet}"
        except Exception as e:
            return {"error": f"Failed to create wallet: {str(e)}"}

# Usage example:
if __name__ == "__main__":
    tool = CreateWalletTool()
    result = tool._run()
    print(result)
