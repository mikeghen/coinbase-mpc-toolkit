const { CoinbaseAgent } = require('./agents/coinbaseAgent');

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

main().catch(console.error);