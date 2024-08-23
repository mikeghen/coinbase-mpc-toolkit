import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from tools.fund_wallet import FundWalletTool
from tools.transfer_funds import TransferFundsTool

# Load environment variables from the .env file
load_dotenv()

# Initialize the LLM with the OpenAI API key from the environment
llm = ChatOpenAI(model="gpt-4o-mini", api_key=os.getenv("OPENAI_API_KEY"))

# Initialize the tools from the provided files
fund_wallet_tool = FundWalletTool()
transfer_funds_tool = TransferFundsTool()

# List of tools to be used by the agent
tools = [fund_wallet_tool, transfer_funds_tool]

# Create the ReAct agent using the LangGraph create_react_agent method
agent = create_react_agent(llm, tools)

# Example 1: Fund a wallet
user_message = "I want to fund my wallet with testnet ETH."
response = agent.invoke({"messages": [("human", user_message)]})
print("# Demo 1: The agent funds a previously created wallet, the defualt wallet.")
print("-"*50)
print("## User Message: \n", user_message)
print("## Agent Response: \n", response["messages"][-1].content)
print("-"*50)

# Example 2: Transfer funds
user_message = "I want to transfer 0.0001 ETH to wallet 0xa7979BF6Ce644E4e36da2Ee65Db73c3f5A0dF895."
response = agent.invoke({"messages": [("human", user_message)]})
print("# Demo 2: The agent transfers funds between wallets.")
print("-"*50)
print("## User Message: \n", user_message)
print("## Agent Response: \n", response["messages"][-1].content)
print("-"*50)

