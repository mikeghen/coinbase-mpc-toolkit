from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sqlite3
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from tools.fund_wallet import FundWalletTool
from tools.transfer_funds import TransferFundsTool

# Load environment variables from the .env file
load_dotenv()

# Initialize the Flask application
app = Flask(__name__)
CORS(app)  # Enable CORS for cross-origin requests

# Initialize the LLM with the OpenAI API key from the environment
llm = ChatOpenAI(model="gpt-4o-mini", api_key=os.getenv("OPENAI_API_KEY"))

# Initialize the tools from the provided files
fund_wallet_tool = FundWalletTool()
transfer_funds_tool = TransferFundsTool()

# List of tools to be used by the agent
tools = [fund_wallet_tool, transfer_funds_tool]

# Create the ReAct agent using the LangGraph create_react_agent method
agent = create_react_agent(llm, tools)

conn = sqlite3.connect('chat_history.db', check_same_thread=False)

# Save a message to the database
def save_message(user_id, role, message):
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO chat_history (user_id, role, message)
        VALUES (?, ?, ?)
    ''', (user_id, role, message))
    conn.commit()

# Load existing messages for a user
def load_conversation(user_id):
    cursor = conn.cursor()
    cursor.execute('''
        SELECT role, message FROM chat_history
        WHERE user_id = ?
        ORDER BY timestamp ASC
    ''', (user_id,))
    messages = cursor.fetchall()
    return messages

# Function to load the system message
def load_system_message():
    with open('./prompts/agent_prompt.txt', 'r') as file:
        system_message = file.read().strip()
    return system_message

@app.route('/query-agent', methods=['POST'])
def query_agent():
    try:
        data = request.json
        user_id = data.get('user_id')
        user_message = data.get('message')

        # Load existing conversation or start a new one
        conversation = load_conversation(user_id)
        
        if not conversation:
            # If no conversation exists, start with the system message
            system_message = load_system_message()
            save_message(user_id, 'system', system_message)
            messages = [("system", system_message)]
        else:
            # Load existing conversation messages
            messages = [(role, msg) for role, msg in conversation]
        
        # Append the user's new message to the conversation
        save_message(user_id, 'human', user_message)
        messages.append(("human", user_message))
        
        # Pass the conversation history to the agent
        response = agent.invoke({"messages": messages})
        
        # Get the agent's response content
        agent_response = response["messages"][-1].content
        
        # Save the agent's response to the database
        save_message(user_id, 'system', agent_response)

        # Return the response as JSON
        return jsonify(agent_response), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
