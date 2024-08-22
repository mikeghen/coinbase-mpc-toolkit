# Coinbase MPC Wallets Toolkit for Agentic Frameworks
This project contains code for a [Langchain Toolkit](https://js.langchain.com/v0.2/docs/concepts/#toolkits) that integrates with [Coinbase's Developer Platform API MPC Wallets](https://docs.cdp.coinbase.com/mpc-wallet/docs/wallets) to allow agents to interact onchain as part of their workflow. 

## Demonstrations
The following is the demonstration you will get if you configure the project correctly. Main thing is you need to manually do the create wallet call and the replace the `DEFAULT_WALLET_ID` where appropriate in the tools.
```bash
% python main.py
# Demo 1: The agent funds a previously created wallet, the defualt wallet.
--------------------------------------------------
## User Message: 
 I want to fund my wallet with testnet ETH.
## Agent Response: 
 Your wallet has been successfully funded with testnet ETH. You can view the transaction details [here](https://sepolia.basescan.org/tx/0x41e4b9d33b347599ea2a9e7908424823c8a64fdc45768024676299a93c0d0c00).
--------------------------------------------------
# Demo 2: The agent transfers funds between wallets.
--------------------------------------------------
## User Message: 
 I want to transfer 0.0001 ETH to wallet 0xa7979BF6Ce644E4e36da2Ee65Db73c3f5A0dF895.
## Agent Response: 
 The transfer of 0.0001 ETH to the wallet address 0xa7979BF6Ce644E4e36da2Ee65Db73c3f5A0dF895 has been completed successfully. You can view the transaction [here](https://sepolia.basescan.org/tx/0xeb3ae642d1efb18725841b1bd847cccabb07b507d794e58b0994ff4ac04ac71a).
--------------------------------------------------
```
### Onchain Transactions from the above Demo
* **Funding Wallet**: [Transaction](https://sepolia.basescan.org/tx/0x41e4b9d33b347599ea2a9e7908424823c8a64fdc45768024676299a93c0d0c00)
* **Transfer Funds**: [Transaction](https://sepolia.basescan.org/tx/0xeb3ae642d1efb18725841b1bd847cccabb07b507d794e58b0994ff4ac04ac71a)

## Overview
* **Tools** ([`./tools`](./tools)) - This directory contains the tools that can be used to interact with the Coinbase MPC Wallets. Tools are extensions of the Langchain [`BaseTool`](https://python.langchain.com/v0.2/docs/how_to/custom_tools/#subclass-basetool).
    * [`FundWallet`](./tools/fund_wallet.py): This tool is used to fund a wallet with a specified amount of ETH.
    * [`TransferFunds`](./tools/transfer_funds.py): This tool is used to transfer funds from one wallet to another.
    * [`TradeAssets`](./tools/trade_assets.py): This tool is used to trade assets on the wallet.
* **Coinbase Developer Platform API** ([`./cdp`](./cdp)) - This is a simple API I made that exposes the `@coinbase/mpc-wallet-sdk` as API endpoints since there is no Python SDK yet. 

## Integrations
* **Coinbase MPC Wallets API** - This toolkit integrates with the Coinbase MPC Wallets API to allow agents to interact with the blockchain. The API is exposed through the `cdp` API.
* **Langchain** - This toolkit and the demo is built using the Langchain SDK. The tools are extensions of the `BaseTool` class.
* **OpenAI** - The demo uses OpenAI's GPT-4o-mini to generate responses for the agent.

## Running the Demo Locally
The Coinbase MPC SDK is not available for Python. So, I created a simple API that exposes the SDK as API endpoints. You can run the demo locally by following these steps:
1. Start the `cdp` API:
```bash
cd cdp
npm install
node index.js
```
This will start the server and you'll see:
```
Server is running on port 3000
Coinbase SDK initialized successfully
```
2. In another terminal, enter the `src` directory and run commands to install and run the application
```bash
cd src
pip install -r requirements.txt
python main.py
```
An example response can be found above

# Future Work
* **Integration with Slack**: Integrate the toolkit with Slack to allow users to interact with the agent through Slack. Avoid having to make/maintain a frontend.
1. **Save and Reference Chat History**: Save the chat history and reference it in the demo conversations.
1. **Add more tools**: Add more tools to interact with the blockchain for read purposes (e.g. balance, balanceOf, etc).