const express = require('express');
const { Coinbase } = require('@coinbase/coinbase-sdk');
const path = require('path');
const fs = require('fs');

const app = express();
app.use(express.json());

// Initialize Coinbase SDK
let coinbase;
(async () => {
    try {
        coinbase = await Coinbase.configureFromJson({ 
            filePath: './secrets/cdp_api_key.json' // Update with your API key file path
        });
        console.log('Coinbase SDK initialized successfully');
    } catch (error) {
        console.error('Failed to initialize Coinbase SDK:', error);
    }
})();

// Utility function to get the file path for a wallet seed
const getWalletSeedPath = (walletId) => {
    return path.join(__dirname, 'wallet_seeds', `${walletId}.json`);
};

// Utility function to rehydrate a wallet
const rehydrateWallet = async (user, walletId) => {
    const wallet = await user.getWallet(walletId);
    const filePath = getWalletSeedPath(walletId);
    await wallet.loadSeed(filePath);
    return wallet;
};

// Create a Wallet
app.post('/create-wallet', async (req, res) => {
    try {
        const user = await coinbase.getDefaultUser();
        const wallet = await user.createWallet();

        // Save the wallet seed
        const filePath = getWalletSeedPath(wallet.getId());

        // Create the directory if it doesn't exist
        const directoryPath = path.dirname(filePath);
        if (!fs.existsSync(directoryPath)) {
            fs.mkdirSync(directoryPath, { recursive: true });
        }

        await wallet.saveSeed(filePath, true); // true for encryption

        res.json({ message: 'Wallet created and seed saved successfully', walletId: wallet.getId() });
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
        
        // Rehydrate the wallet
        const wallet = await rehydrateWallet(user, walletId);
        console.log('wallet:', wallet);
        console.log(`wallet is hydrated: ${wallet.canSign()}`);

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
        
        // Rehydrate the wallet
        const sourceWallet = await rehydrateWallet(user, sourceWalletId);
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
        
        // Rehydrate the wallet
        const wallet = await rehydrateWallet(user, walletId);
        console.log(`wallet is hydrated: ${wallet.canSign()}`);

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

// Get ETH Balance
app.get('/wallet-balance/:walletId', async (req, res) => {
    try {
        const { walletId } = req.params;
        let user = await coinbase.getDefaultUser();

        // Rehydrate the wallet
        const wallet = await rehydrateWallet(user, walletId);

        // Get the balance of ETH
        const balance = await wallet.getBalance(Coinbase.assets.Eth);

        res.json({ message: 'ETH balance retrieved successfully', balance });
    } catch (error) {
        console.error('Error retrieving wallet balance:', error);
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