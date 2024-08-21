const express = require('express');
const { Coinbase } = require('@coinbase/coinbase-sdk');

const app = express();
app.use(express.json());

// Initialize Coinbase SDK
let coinbase;
(async () => {
    try {
        coinbase = await Coinbase.configureFromJson({ 
            filePath: '~/Downloads/cdp_api_key.json' // Update with your API key file path
        });
        console.log('Coinbase SDK initialized successfully');
    } catch (error) {
        console.error('Failed to initialize Coinbase SDK:', error);
    }
})();

// Create a Wallet
app.post('/create-wallet', async (req, res) => {
    try {
        const user = await coinbase.getDefaultUser();
        const wallet = await user.createWallet();
        res.json({ message: 'Wallet created successfully', wallet });
    } catch (error) {
        console.error('Error creating wallet:', error);
        res.status(500).json({ error: error.message });
    }
});

// Fund a Wallet with testnet ETH
app.post('/fund-wallet', async (req, res) => {
    try {
        const { walletId } = req.body;
        console.log('walletId:', walletId);
        let user = await coinbase.getDefaultUser();
        console.log('user:', user);
        const wallet = await user.getWallet(walletId);
        console.log('wallet:', wallet);
        const faucetTransaction = await wallet.faucet();
        console.log('faucetTransaction:', faucetTransaction);
        res.json({ message: 'Faucet transaction completed', transaction: faucetTransaction });
    } catch (error) {
        console.error('Error funding wallet:', error);
        res.status(500).json({ error: error.message });
    }
});

// Transfer Funds
app.post('/transfer-funds', async (req, res) => {
    try {
        const { sourceWalletId, destinationWalletAddress, amount } = req.body;
        let user = await coinbase.getDefaultUser();
        const sourceWallet = await user.getWallet(sourceWalletId);
        console.log(`wallet is hydrated: ${sourceWallet.canSign()}`);
        const transfer = await sourceWallet.createTransfer({
            amount,
            assetId: Coinbase.assets.Eth,
            destination: destinationWalletAddress,
        });
        res.json({ message: 'Transfer completed successfully', transfer });
    } catch (error) {
        console.error('Error transferring funds:', error);
        res.status(500).json({ error: error.message });
    }
});

// Trade Assets
app.post('/trade-assets', async (req, res) => {
    try {
        const { walletId, fromAssetId, toAssetId, amount } = req.body;
        const user = await coinbase.getDefaultUser();
        const wallet = await user.getWallet(walletId);
        const trade = await wallet.createTrade({ 
            amount, 
            fromAssetId, 
            toAssetId 
        });
        res.json({ message: 'Trade completed successfully', trade });
    } catch (error) {
        console.error('Error trading assets:', error);
        res.status(500).json({ error: error.message });
    }
});

// Function to start the server
const startServer = () => {
    const PORT = process.env.PORT || 3000;
    return app.listen(PORT, () => {
        console.log(`Server is running on port ${PORT}`);
    });
};

// Start the server if this file is run directly
if (require.main === module) {
    startServer();
}

module.exports = { app, startServer };