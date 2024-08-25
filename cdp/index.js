const express = require('express');
const { Coinbase } = require('@coinbase/coinbase-sdk');
const path = require('path');
const fs = require('fs');
const winston = require('winston');

const app = express();
app.use(express.json());

// Configure winston logger
const logger = winston.createLogger({
    level: 'debug', // Set the default log level
    format: winston.format.combine(
        winston.format.timestamp({ format: 'YYYY-MM-DD HH:mm:ss' }),
        winston.format.printf(({ timestamp, level, message }) => {
            return `${timestamp} [${level.toUpperCase()}]: ${message}`;
        })
    ),
    transports: [
        new winston.transports.Console(),
        new winston.transports.File({ filename: 'logs/application.log' })
    ]
});

// Initialize Coinbase SDK
let coinbase;
(async () => {
    try {
        coinbase = await Coinbase.configureFromJson({ 
            filePath: './secrets/cdp_api_key.json' // Update with your API key file path
        });
        logger.info('Coinbase SDK initialized successfully');
    } catch (error) {
        logger.error('Failed to initialize Coinbase SDK:', error);
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
    logger.debug('POST /create-wallet called');
    try {
        const user = await coinbase.getDefaultUser();
        const wallet = await user.createWallet();

        // Save the wallet seed
        const filePath = getWalletSeedPath(wallet.getId());

        // Create the directory if it doesn't exist
        const directoryPath = path.dirname(filePath);
        if (!fs.existsSync(directoryPath)) {
            fs.mkdirSync(directoryPath, { recursive: true });
            logger.info(`Directory created: ${directoryPath}`);
        }

        await wallet.saveSeed(filePath, true); // true for encryption
        logger.info(`Wallet created and seed saved: ${wallet.getId()}`);

        res.json({ message: 'Wallet created and seed saved successfully', walletId: wallet.getId() });
    } catch (error) {
        logger.error('Error creating wallet:', error);
        res.status(500).json({ error: error.message });
    }
});

// Fund a Wallet with testnet ETH
app.post('/fund-wallet', async (req, res) => {
    logger.debug('POST /fund-wallet called');
    try {
        const { walletId } = req.body;
        logger.debug(`walletId: ${walletId}`);
        let user = await coinbase.getDefaultUser();
        logger.debug('User retrieved');

        // Rehydrate the wallet
        const wallet = await rehydrateWallet(user, walletId);
        logger.debug('Wallet rehydrated');
        logger.debug(`Wallet is hydrated: ${wallet.canSign()}`);

        const faucetTransaction = await wallet.faucet();
        logger.info('Faucet transaction completed', faucetTransaction);
        res.json({ message: 'Faucet transaction completed', transaction: faucetTransaction });
    } catch (error) {
        logger.error('Error funding wallet:', error);
        res.status(500).json({ error: error.message });
    }
});

// Transfer Funds
app.post('/transfer-funds', async (req, res) => {
    logger.debug('POST /transfer-funds called');
    try {
        const { sourceWalletId, destinationWalletAddress, amount } = req.body;
        logger.debug(`sourceWalletId: ${sourceWalletId}, destinationWalletAddress: ${destinationWalletAddress}, amount: ${amount}`);
        let user = await coinbase.getDefaultUser();
        logger.debug('User retrieved');

        // Rehydrate the wallet
        const sourceWallet = await rehydrateWallet(user, sourceWalletId);
        logger.debug('Wallet rehydrated');
        logger.debug(`Wallet is hydrated: ${sourceWallet.canSign()}`);

        const transfer = await sourceWallet.createTransfer({
            amount,
            assetId: Coinbase.assets.Eth,
            destination: destinationWalletAddress,
        });
        logger.info('Transfer completed successfully', transfer);
        res.json({ message: 'Transfer completed successfully', transfer });
    } catch (error) {
        logger.error('Error transferring funds:', error);
        res.status(500).json({ error: error.message });
    }
});

// Trade Assets
app.post('/trade-assets', async (req, res) => {
    logger.debug('POST /trade-assets called');
    try {
        const { walletId, fromAssetId, toAssetId, amount } = req.body;
        logger.debug(`walletId: ${walletId}, fromAssetId: ${fromAssetId}, toAssetId: ${toAssetId}, amount: ${amount}`);
        const user = await coinbase.getDefaultUser();
        logger.debug('User retrieved');

        // Rehydrate the wallet
        const wallet = await rehydrateWallet(user, walletId);
        logger.debug('Wallet rehydrated');
        logger.debug(`Wallet is hydrated: ${wallet.canSign()}`);

        const trade = await wallet.createTrade({ 
            amount, 
            fromAssetId, 
            toAssetId 
        });
        logger.info('Trade completed successfully', trade);
        res.json({ message: 'Trade completed successfully', trade });
    } catch (error) {
        logger.error('Error trading assets:', error);
        res.status(500).json({ error: error.message });
    }
});

// Get ETH Balance
app.get('/wallet-balance/:walletId', async (req, res) => {
    logger.debug('GET /wallet-balance/:walletId called');
    try {
        const { walletId } = req.params;
        logger.debug(`walletId: ${walletId}`);
        let user = await coinbase.getDefaultUser();
        logger.debug('User retrieved');

        // Rehydrate the wallet
        const wallet = await rehydrateWallet(user, walletId);
        logger.debug('Wallet rehydrated');

        // Get the balance of ETH
        const balance = await wallet.getBalance(Coinbase.assets.Eth);
        logger.info('ETH balance retrieved successfully', balance);
        res.json({ message: 'ETH balance retrieved successfully', balance });
    } catch (error) {
        logger.error('Error retrieving wallet balance:', error);
        res.status(500).json({ error: error.message });
    }
});

// Get a Wallet
app.get('/get-wallet/:walletId', async (req, res) => {
    logger.debug('GET /get-wallet/:walletId called');
    try {
        const { walletId } = req.params;
        logger.debug(`walletId: ${walletId}`);
        let user = await coinbase.getDefaultUser();
        logger.debug('User retrieved');

        const wallet = await user.getWallet(walletId);
        logger.info('Wallet retrieved successfully', wallet);
        res.json({ message: 'Wallet retrieved successfully', wallet });
    } catch (error) {
        logger.error('Error retrieving wallet:', error);
        res.status(500).json({ error: error.message });
    }
});

// Function to start the server
const startServer = () => {
    const PORT = process.env.PORT || 3000;
    return app.listen(PORT, () => {
        logger.info(`Server is running on port ${PORT}`);
    });
};

// Start the server if this file is run directly
if (require.main === module) {
    startServer();
}

module.exports = { app, startServer };
