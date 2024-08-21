const request = require('supertest');
const { Coinbase } = require('@coinbase/coinbase-sdk');

// Mock the Coinbase SDK
jest.mock('@coinbase/coinbase-sdk', () => ({
  Coinbase: {
    configureFromJson: jest.fn().mockResolvedValue({
      getDefaultUser: jest.fn().mockResolvedValue({
        createWallet: jest.fn().mockResolvedValue({ id: 'wallet123' })
      }),
      getWallet: jest.fn().mockResolvedValue({
        faucet: jest.fn().mockResolvedValue({ id: 'tx123' }),
        createTransfer: jest.fn().mockResolvedValue({ id: 'transfer123' }),
        createTrade: jest.fn().mockResolvedValue({ id: 'trade123' })
      }),
      assets: {
        Eth: 'ETH'
      }
    })
  }
}));

// Import your app
const { app, startServer } = require('../index'); // Update this path if necessary

let server;

describe('Coinbase Express Server', () => {
  beforeAll(async () => {
    server = startServer();
    await new Promise(resolve => setTimeout(resolve, 1000)); // Give some time for the server to start
  });

  afterAll(done => {
    server.close(done);
  });

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('POST /create-wallet', () => {
    it('should create a wallet successfully', async () => {
      const response = await request(app)
        .post('/create-wallet')
        .expect(200);

      expect(response.body).toEqual({
        message: 'Wallet created successfully',
        wallet: { id: 'wallet123' }
      });
    });

    xit('should handle errors when creating a wallet', async () => {
      Coinbase.configureFromJson.mockRejectedValueOnce(new Error('Failed to create wallet'));

      const response = await request(app)
        .post('/create-wallet')
        .expect(500);

      expect(response.body).toEqual({
        error: 'Failed to create wallet'
      });
    });
  });

  describe('POST /fund-wallet', () => {
    it('should fund a wallet successfully', async () => {
      const response = await request(app)
        .post('/fund-wallet')
        .send({ walletId: 'wallet123' })
        .expect(200);

      expect(response.body).toEqual({
        message: 'Faucet transaction completed',
        transaction: { id: 'tx123' }
      });
    });

    xit('should handle errors when funding a wallet', async () => {
      Coinbase.configureFromJson.mockResolvedValueOnce({
        getWallet: jest.fn().mockRejectedValue(new Error('Failed to fund wallet'))
      });

      const response = await request(app)
        .post('/fund-wallet')
        .send({ walletId: 'wallet123' })
        .expect(500);

      expect(response.body).toEqual({
        error: 'Failed to fund wallet'
      });
    });
  });

  describe('POST /transfer-funds', () => {
    it('should transfer funds successfully', async () => {
      const response = await request(app)
        .post('/transfer-funds')
        .send({
          sourceWalletId: 'sourceWallet123',
          destinationWalletId: 'destWallet123',
          amount: '1.0'
        })
        .expect(200);

      expect(response.body).toEqual({
        message: 'Transfer completed successfully',
        transfer: { id: 'transfer123' }
      });
    });

    xit('should handle errors when transferring funds', async () => {
      Coinbase.configureFromJson.mockResolvedValueOnce({
        getWallet: jest.fn().mockRejectedValue(new Error('Failed to transfer funds'))
      });

      const response = await request(app)
        .post('/transfer-funds')
        .send({
          sourceWalletId: 'sourceWallet123',
          destinationWalletId: 'destWallet123',
          amount: '1.0'
        })
        .expect(500);

      expect(response.body).toEqual({
        error: 'Failed to transfer funds'
      });
    });
  });

  describe('POST /trade-assets', () => {
    it('should trade assets successfully', async () => {
      const response = await request(app)
        .post('/trade-assets')
        .send({
          walletId: 'wallet123',
          fromAssetId: 'ETH',
          toAssetId: 'BTC',
          amount: '1.0'
        })
        .expect(200);

      expect(response.body).toEqual({
        message: 'Trade completed successfully',
        trade: { id: 'trade123' }
      });
    });

    it('should handle errors when trading assets', async () => {
      Coinbase.configureFromJson.mockResolvedValueOnce({
        getWallet: jest.fn().mockRejectedValue(new Error('Failed to trade assets'))
      });

      const response = await request(app)
        .post('/trade-assets')
        .send({
          walletId: 'wallet123',
          fromAssetId: 'ETH',
          toAssetId: 'BTC',
          amount: '1.0'
        })
        .expect(500);

      expect(response.body).toEqual({
        error: 'Failed to trade assets'
      });
    });
  });
});