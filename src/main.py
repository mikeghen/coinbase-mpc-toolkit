import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from tools.create_wallet import CreateWalletTool
from tools.fund_wallet import FundWalletTool
from tools.transfer_funds import TransferFundsTool
from tools.get_balance import GetWalletBalanceTool

# Load environment variables from the .env file
load_dotenv()

# Initialize the LLM with the OpenAI API key from the environment
llm = ChatOpenAI(model="gpt-4o-mini", api_key=os.getenv("OPENAI_API_KEY"))

# Initialize the tools from the provided files
create_wallet_tool = CreateWalletTool()
fund_wallet_tool = FundWalletTool()
transfer_funds_tool = TransferFundsTool()
get_balance_tool = GetWalletBalanceTool(web3_provider_url=os.getenv("WEB3_PROVIDER_URL"))

# List of tools to be used by the agent
tools = [fund_wallet_tool, transfer_funds_tool, get_balance_tool, create_wallet_tool]

# Create the ReAct agent using the LangGraph create_react_agent method
agent = create_react_agent(llm, tools)

# # Example 1: Fund a wallet
# user_message = "I want to fund my wallet with testnet ETH."
# response = agent.invoke(
#     {
#         "messages": [
#             ("system", "Create wallet with ID: 674069f0-3de9-40bf-a06b-22a9573c7861"), 
#             ("human", user_message)
#         ]
#     }
# )
# print("# Demo 1: The agent funds a wallet by its")
# print("-"*50)
# print("## User Message: \n", user_message)
# print("## Agent Response: \n", response["messages"][-1].content)
# print("-"*50)

# # Example 2: Transfer funds
# user_message = "I want to transfer 0.0001 ETH to wallet 0xa7979BF6Ce644E4e36da2Ee65Db73c3f5A0dF895."
# response = agent.invoke(
#     {
#         "messages": [
#             ("system", "{\"message\": \"Wallet retrieved successfully\", \"address\": \"0xE9B0f8a530736313fdD388B0660163e93b298c77\",\"wallet_id\": \"674069f0-3de9-40bf-a06b-22a9573c7861\"}"),
#             ("human", user_message)
#         ]
#     }
# )
# print("# Demo 2: The agent transfers funds between wallets.")
# print("-"*50)
# print("## User Message: \n", user_message)
# print("## Agent Response: \n", response["messages"][-1].content)
# print("-"*50) 


# # Example 3: Get wallet balance
# user_message = "What is the balance of my wallet with address 0xa7979BF6Ce644E4e36da2Ee65Db73c3f5A0dF895?"
# response = agent.invoke({"messages": [("human", user_message)]})
# print("# Demo 3: The agent retrieves the balance of a wallet.")
# print("-"*50)
# print("## User Message: \n", user_message)
# print("## Agent Response: \n", response["messages"][-1].content)
# print("-"*50)

# # Example 4: Create a wallet
# user_message = "I want to create a new wallet."
# response = agent.invoke({"messages": [("human", user_message)]})
# print("# Demo 4: The agent creates a new wallet.")
# print("-"*50)
# print("## User Message: \n", user_message)
# print("## Agent Response: \n", response["messages"][-1].content)
# print("-"*50)




# Start a new conversation with the agent, set the system messages to be the response from the last tool calls
# Load the file in prompts/malice_prompt.txt
with open("prompts/malice_prompt.txt", "r") as file:
    system_prompt = file.read()
response = agent.invoke(
    {
        "messages": [
            ("system", system_prompt),
            ("system", wallet_creation_response),
            ("system", fund_wallet_response),
            ("human", "Hi")
        ]
    }
)
print("Agent response:", response["messages"][-1].content)
