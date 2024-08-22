const { BaseModel, Field } = require('langchain/pydantic_v1');
const { BaseTool } = require('langchain_core/tools');
const { Coinbase } = require('@coinbase/coinbase-sdk');

class FundWalletInput extends BaseModel {
  constructor(data) {
    super(data);
    this.walletId = Field(data.walletId, { description: "The ID of the wallet to fund with testnet ETH" });
  }
}

class FundWalletTool extends BaseTool {
  constructor() {
    super();
    this.name = "FundWallet";
    this.description = "Fund a wallet with testnet ETH";
    this.argsSchema = FundWalletInput;
    this.returnDirect = true;
    this.coinbase = null;
  }

  async initialize() {
    try {
      this.coinbase = await Coinbase.configureFromJson({ 
        filePath: '~/Downloads/cdp_api_key.json' // Update with your API key file path
      });
      console.log('Coinbase SDK initialized successfully');
    } catch (error) {
      console.error('Failed to initialize Coinbase SDK:', error);
      throw error;
    }
  }

  async _run(walletId, runManager = null) {
    if (!this.coinbase) {
      await this.initialize();
    }

    try {
      const user = await this.coinbase.getDefaultUser();
      const wallet = await user.getWallet(walletId);
      const faucetTransaction = await wallet.faucet();
      return `Wallet funded successfully: ${JSON.stringify(faucetTransaction)}`;
    } catch (error) {
      console.error('Error funding wallet:', error);
      return `Funding failed: ${error.message}`;
    }
  }
}

// Usage example:
async function main() {
  const tool = new FundWalletTool();
  await tool.initialize();
  const result = await tool._run("wallet_id_here");
  console.log(result);
}

if (require.main === module) {
  main().catch(console.error);
}

module.exports = { FundWalletTool };