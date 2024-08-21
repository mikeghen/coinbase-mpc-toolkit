# Coinbase Developer Platform API 
This is a wrapper around the `@coinbase/coinbase-sdk` and provides a simple HTTP interface that's consumed by the MPC Agent application in the root of this repository. There is no Python SDK for Coinbase so this is a simple way to interact with the Coinbase API from a Python application.

## Config
You will need to make a Coinbase account and download a key. The key is assumed to be at `~/Downloads/cdp_api_key.json`

## Install
To install the dependencies, run the following command:
```bash
npm install
```

## Run
The application is an Express.js server that listens on port 3000. To start the server, run the following command:
```bash
node index.js
```

## Test
The tests are written using Jest and Supertest. To run the tests, run the following command:
```bash
npx jest
```
