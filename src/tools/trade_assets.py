from typing import Optional, Type
from langchain.pydantic_v1 import BaseModel, Field
from langchain_core.callbacks import CallbackManagerForToolRun
from langchain_core.tools import BaseTool
from tools.coinbase_api import CoinbaseAPIWrapper  

class TradeAssetsInput(BaseModel):
    amount: str = Field(description="The amount of the asset/token to trade (as a string, e.g., '0.1')")
    asset_from: str = Field(description="The asset/token symbol to trade from (e.g. USDC, ETH)")
    asset_to: str = Field(description="The asset/token symbol to trade to (e.g. USDC, ETH)")

class TradeAssetsTool(BaseTool):
    name = "TradeAssets"
    description = "Trade one asset/token for another asset/token within a specified wallet"
    args_schema: Type[BaseModel] = TradeAssetsInput
    return_direct: bool = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.api = CoinbaseAPIWrapper()  # Initialize our API wrapper

    def _run(
        self,
        amount: str,
        asset_from: str,
        asset_to: str,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        try:
            amount = int(float(amount) * 1e18)
            result = self.api.trade_assets(self.api.default_wallet_id, asset_from, asset_to, amount)
            return f"Trade successful: {result}"
        except Exception as e:
            return f"Trade failed: {str(e)}"

# Only works on mainnet
## Usage example:
# if __name__ == "__main__":
#     tool = TradeAssetsTool()
#     result = tool._run(
#         wallet_id="wallet_123",
#         amount="0.1",
#         asset_from="ETH",
#         asset_to="BTC"
#     )
#     print(result)