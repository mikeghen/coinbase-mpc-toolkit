const { BaseModel } = require('langchain/pydantic_v1');
const { BaseTool } = require('langchain_core/tools');
const { Coinbase } = require('@coinbase/coinbase-sdk');
require('dotenv').config();

class CreateWalletInput extends BaseModel {
  constructor(data) {
    super(data);
    // No input parameters needed for wallet creation
  }
}

class CreateWalletTool extends BaseTool {
  constructor() {
    super();
    this.name = "CreateWallet";
    this.description = "Create a new wallet in the Coinbase account";
    this.argsSchema = CreateWalletInput;
    this.returnDirect = true;
    this.coinbase = null;
  }

  async initialize() {
    try {
      this.coinbase = await Coinbase.configureFromJson({ 
        filePath: process.env.COINBASE_API_KEY_PATH
      });
      console.log('Coinbase SDK initialized successfully for CreateWalletTool');
    } catch (error) {
      console.error('Failed to initialize Coinbase SDK for CreateWalletTool:', error);
      throw error;
    }
  }

  async _run(runManager = null) {
    if (!this.coinbase) {
      await this.initialize();
    }

    try {
      const user = await this.coinbase.getDefaultUser();
      const wallet = await user.createWallet();
      return `Wallet created successfully: ${JSON.stringify(wallet)}`;
    } catch (error) {
      console.error('Error creating wallet:', error);
      return `Wallet creation failed: ${error.message}`;
    }
  }
}

module.exports = { CreateWalletTool };