# Coinbase MPC Wallets Toolkit for Agentic Frameworks

This project contains code for a [Langchain Toolkit](https://js.langchain.com/v0.2/docs/concepts/#toolkits) that integrates with [Coinbase's Developer Platform API MPC Wallets](https://docs.cdp.coinbase.com/mpc-wallet/docs/wallets) to allow agents to interact onchain as part of their workflow. 

## Overview

* **Tools** ([`./src/tools`](./src/tools)) - This directory contains the tools that can be used to interact with the Coinbase MPC Wallets. Tools are extensions of the Langchain [`BaseTool`](https://js.langchain.com/docs/modules/agents/tools/custom_tools).
    * [`CreateWallet`](./src/tools/createWallet.js): This tool is used to create a new wallet.
    * [`FundWallet`](./src/tools/fundWallet.js): This tool is used to fund a wallet with testnet ETH.
    * [`TransferFunds`](./src/tools/transferFunds.js): This tool is used to transfer funds from one wallet to another.
    * [`TradeAssets`](./src/tools/tradeAssets.js): This tool is used to trade assets on the wallet.

* **Agent** ([`./src/agents`](./src/agents)) - This directory contains the Langchain agent that uses the tools to interact with Coinbase MPC Wallets.
    * [`CoinbaseAgent`](./src/agents/coinbaseAgent.js): This agent can understand and process natural language queries related to Coinbase operations.

## Setup

1. Install dependencies:
   ```
   npm install
   ```

2. Set up environment variables:
   - Copy `.env.example` to `.env`
   - Fill in your OpenAI API key and the path to your Coinbase API key JSON file

3. Run the project:
   ```
   npm start
   ```

## Usage

The agent can handle queries like:
- "Create a new wallet for me"
- "Transfer 0.01 ETH from wallet ABC to address 0x123..."
- "Trade 0.1 ETH for BTC in wallet XYZ"
- "Fund wallet DEF with testnet ETH"

Modify the queries in `src/index.js` to test different operations.

## Testing Tools Individually

You can test each tool individually by running their respective files. For example:

```bash
node src/tools/createWallet.js
node src/tools/fundWallet.js
node src/tools/transferFunds.js
node src/tools/tradeAssets.js
```

Example response for funding a wallet:

```json
{
    "message": "Wallet funded successfully",
    "faucetTransaction": {
        "transaction_hash": "0xe9429a2d01249457bc226a881defe7350a7ac77c32ea34851fd9a13196e6bc1e",
        "transaction_link": "https://sepolia.basescan.org/tx/0xe9429a2d01249457bc226a881defe7350a7ac77c32ea34851fd9a13196e6bc1e"
    }
}
```

## Notice: Non-Production Use Only
This is a demonstration project. In a production environment, ensure proper security measures are in place, especially when handling sensitive information like wallet IDs and addresses.

The project now directly uses the `@coinbase/coinbase-sdk` instead of a separate API, simplifying the setup and usage.