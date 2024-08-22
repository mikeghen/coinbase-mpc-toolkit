# End to End test of the API endpoints
# - create a wallet
# - fund a wallet
# - transfer funds
# - (Mainnet only) trade funds

# Create a Wallet
# - it should create a new wallet and save the seed locally
# - it should return the walletId and a success message
curl -X POST http://localhost:3000/create-wallet \
     -H "Content-Type: application/json"

# Fund the Wallet
# - Get the walletId from the response of the create-wallet request
curl -X POST http://localhost:3000/fund-wallet \
     -H "Content-Type: application/json" \
     -d '{"walletId": "674069f0-3de9-40bf-a06b-22a9573c7861"}'

# Transfer Funds
curl -X POST http://localhost:3000/transfer-funds \
     -H "Content-Type: application/json" \
     -d '{
         "sourceWalletId": "674069f0-3de9-40bf-a06b-22a9573c7861",
         "destinationWalletAddress": "0xa7979BF6Ce644E4e36da2Ee65Db73c3f5A0dF895",
         "amount": "0.0001"
     }'