const { BaseModel, Field } = require('langchain/pydantic_v1');
const { BaseTool } = require('langchain_core/tools');
const { Coinbase } = require('@coinbase/coinbase-sdk');
require('dotenv').config();

class TradeAssetsInput extends BaseModel {
  constructor(data) {
    super(data);
    this.walletId = Field(data.walletId, { description: "The ID of the wallet to trade from" });
    this.amount = Field(data.amount, { description: "The amount of the asset/token to trade (as a string, e.g., '0.1')" });
    this.fromAssetId = Field(data.fromAssetId, { description: "The asset/token ID to trade from" });
    this.toAssetId = Field(data.toAssetId, { description: "The asset/token ID to trade to" });
  }
}

class TradeAssetsTool extends BaseTool {
  constructor() {
    super();
    this.name = "TradeAssets";
    this.description = "Trade one asset/token for another asset/token within a specified wallet";
    this.argsSchema = TradeAssetsInput;
    this.returnDirect = true;
    this.coinbase = null;
  }

  async initialize() {
    try {
      this.coinbase = await Coinbase.configureFromJson({ 
        filePath: process.env.COINBASE_API_KEY_PATH
      });
      console.log('Coinbase SDK initialized successfully for TradeAssetsTool');
    } catch (error) {
      console.error('Failed to initialize Coinbase SDK for TradeAssetsTool:', error);
      throw error;
    }
  }

  async _run(walletId, amount, fromAssetId, toAssetId, runManager = null) {
    if (!this.coinbase) {
      await this.initialize();
    }

    try {
      const user = await this.coinbase.getDefaultUser();
      const wallet = await user.getWallet(walletId);
      const trade = await wallet.createTrade({ 
        amount, 
        fromAssetId, 
        toAssetId 
      });
      return `Trade completed successfully: ${JSON.stringify(trade)}`;
    } catch (error) {
      console.error('Error trading assets:', error);
      return `Trade failed: ${error.message}`;
    }
  }
}

module.exports = { TradeAssetsTool };