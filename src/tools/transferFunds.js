const { BaseModel, Field } = require('langchain/pydantic_v1');
const { BaseTool } = require('langchain_core/tools');
const { Coinbase } = require('@coinbase/coinbase-sdk');
require('dotenv').config();

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
        filePath: process.env.COINBASE_API_KEY_PATH
      });
      console.log('Coinbase SDK initialized successfully for FundWalletTool');
    } catch (error) {
      console.error('Failed to initialize Coinbase SDK for FundWalletTool:', error);
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

module.exports = { FundWalletTool };