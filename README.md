# Coinbase MPC Wallets Toolkit for Agentic Frameworks
This project contains code for a [Langchain Toolkit](https://js.langchain.com/v0.2/docs/concepts/#toolkits) that integrates with [Coinbase's Developer Platform API MPC Wallets](https://docs.cdp.coinbase.com/mpc-wallet/docs/wallets) to allow agents to interact onchain as part of their workflow. 

## Overview
* **Tools** ([`./tools`](./tools)) - This directory contains the tools that can be used to interact with the Coinbase MPC Wallets. Tools are extensions of the Langchain `BaseTool`.
    * `FundWallet`: This tool is used to fund a wallet with a specified amount of ETH.
    * `TradeAssets`: This tool is used to trade assets on the wallet.
* **Coinbase Developer Platform API** ([`./cdp`](./cdp)) - This is a simple API I made that exposes the `@coinbase/mpc-wallet-sdk` as API endpoints since there is no Python SDK yet. 

## Testing Tools
1. You need to run the `cdp` API locally.
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
2. You can now run the tools in the `tools` directory. For example, to fund a wallet:
```bash
cd tools
python3 fund_wallet.py
```
An example response if configured correctly is:
```
Wallet funded successfully: 
{
    "message": "Faucet transaction completed",
    "transaction": {
        "model": {
            "transaction_hash": "0xe9429a2d01249457bc226a881defe7350a7ac77c32ea34851fd9a13196e6bc1e",
            "transaction_link": "https://sepolia.basescan.org/tx/0xe9429a2d01249457bc226a881defe7350a7ac77c32ea34851fd9a13196e6bc1e"
        }
    }
}
```