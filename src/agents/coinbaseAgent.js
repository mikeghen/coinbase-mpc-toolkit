const { ChatOpenAI } = require("langchain/chat_models/openai");
const { initializeAgentExecutorWithOptions } = require("langchain/agents");
const { TransferFundsTool } = require("../tools/transferFunds");
const { TradeAssetsTool } = require("../tools/tradeAssets");
const { FundWalletTool } = require("../tools/fundWallet");
const { CreateWalletTool } = require("../tools/createWallet");
require('dotenv').config();

class CoinbaseAgent {
  constructor() {
    this.model = new ChatOpenAI({
      temperature: 0,
      openAIApiKey: process.env.OPENAI_API_KEY, // Make sure to set this environment variable
    });
    this.tools = [];
    this.agent = null;
  }

  async initialize() {
    // Initialize all tools
    const transferFundsTool = new TransferFundsTool();
    const tradeAssetsTool = new TradeAssetsTool();
    const fundWalletTool = new FundWalletTool();
    const createWalletTool = new CreateWalletTool();

    await Promise.all([
      transferFundsTool.initialize(),
      tradeAssetsTool.initialize(),
      fundWalletTool.initialize(),
      createWalletTool.initialize(),
    ]);

    this.tools = [transferFundsTool, tradeAssetsTool, fundWalletTool, createWalletTool];

    // Initialize the agent
    this.agent = await initializeAgentExecutorWithOptions(
      this.tools,
      this.model,
      {
        agentType: "chat-zero-shot-react-description",
        verbose: true,
      }
    );

    console.log("Coinbase Agent initialized successfully");
  }

  async processQuery(query) {
    if (!this.agent) {
      throw new Error("Agent not initialized. Call initialize() first.");
    }

    try {
      const result = await this.agent.call({ input: query });
      return result.output;
    } catch (error) {
      console.error("Error processing query:", error);
      return `Error: ${error.message}`;
    }
  }
}

// Usage example:
async function main() {
  const agent = new CoinbaseAgent();
  await agent.initialize();

  const queries = [
    "Create a new wallet for me",
    "Transfer 0.01 ETH from wallet ABC to address 0x123...",
    "Trade 0.1 ETH for BTC in wallet XYZ",
    "Fund wallet DEF with testnet ETH",
  ];

  for (const query of queries) {
    console.log(`Query: ${query}`);
    const result = await agent.processQuery(query);
    console.log(`Result: ${result}\n`);
  }
}

if (require.main === module) {
  main().catch(console.error);
}

module.exports = { CoinbaseAgent };