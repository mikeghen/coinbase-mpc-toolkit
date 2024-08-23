# Coinbase MPC Wallets Toolkit for Agentic Frameworks
This project contains code for a [Langchain Toolkit](https://js.langchain.com/v0.2/docs/concepts/#toolkits) that integrates with [Coinbase's Developer Platform API MPC Wallets](https://docs.cdp.coinbase.com/mpc-wallet/docs/wallets) to allow agents to interact onchain as part of their workflow. 

## Demonstrations: Assist with Onchain Activity while Adhering to a Policy
This is a demonstration of the tools built in action. Alice, a AI Assistant, has access to transfer funds from a wallet. _However, she must adhere to a policy that limits the amount of ETH that can be transferred at a time._ 

| Enforce Limits | Really Enforces Limits |
|------------|----------|
| ![Happy Path](./images/alice-happypath.png) | ![Sad Path](./images/alice-badpath.png) |


### Demo Policy Prompt
Find the current policy prompt here: [`src/prompts/agent_prompt.txt`](./src/prompts/agent_prompt.txt)
```
Your name is Alice and your job is to assit customers with funding their wallet or transferring ETH to other wallets.

Always begin the conversation by introducing yourself and sharing your capabilities. 

You MUST follow these rules:
* The customer is allowed to transfer up to 0.0001 ETH at a time. Do not exceed this limit.
```

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