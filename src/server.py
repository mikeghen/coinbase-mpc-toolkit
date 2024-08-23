from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import AIMessage
from tools.fund_wallet import FundWalletTool
from tools.transfer_funds import TransferFundsTool
from tools.get_balance import GetEthBalanceTool

# Load environment variables from the .env file
load_dotenv()

# Initialize the Flask application
app = Flask(__name__)
CORS(app)  # Enable CORS for cross-origin requests

# Configure the SQLAlchemy part of the application
app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Configure logging
logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]',
                    handlers=[logging.StreamHandler()])

# Example model definition
class ChatHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(255), nullable=False)
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, server_default=db.func.now())

# Initialize the LLM with the OpenAI API key from the environment
llm = ChatOpenAI(model="gpt-4o-mini", api_key=os.getenv("OPENAI_API_KEY"))

# Initialize the tools from the provided files
fund_wallet_tool = FundWalletTool()
transfer_funds_tool = TransferFundsTool()
get_balance_tool = GetEthBalanceTool()

# List of tools to be used by the agent
tools = [fund_wallet_tool, transfer_funds_tool, get_balance_tool]

# Create the ReAct agent using the LangGraph create_react_agent method
agent = create_react_agent(llm, tools)

# Save a message to the database
def save_message(user_id, role, message):
    try:
        new_message = ChatHistory(user_id=user_id, role=role, message=message)
        db.session.add(new_message)
        db.session.commit()
        logging.debug(f"Saved message to database: user_id={user_id}, role={role}, message={message}")
    except Exception as e:
        logging.error(f"Failed to save message: {str(e)}")
        db.session.rollback()

# Load existing messages for a user
def load_conversation(user_id):
    try:
        messages = ChatHistory.query.filter_by(user_id=user_id).order_by(ChatHistory.timestamp.asc()).all()
        logging.debug(f"Loaded conversation for user_id={user_id}")
        return [(message.role, message.message) for message in messages]
    except Exception as e:
        logging.error(f"Failed to load conversation for user_id={user_id}: {str(e)}")
        return []

# Function to load the system message
def load_system_message():
    try:
        with open('./prompts/agent_prompt.txt', 'r') as file:
            system_message = file.read().strip()
            logging.debug("Loaded system message.")
            return system_message
    except Exception as e:
        logging.error(f"Failed to load system message: {str(e)}")
        return ""

@app.route('/query-agent', methods=['POST'])
def query_agent():
    try:
        data = request.json
        user_id = data.get('user_id')
        user_message = data.get('message')
        logging.info(f"Received request: user_id={user_id}, message={user_message}")

        # Load existing conversation or start a new one
        conversation = load_conversation(user_id)
        
        if not conversation:
            # If no conversation exists, start with the system message
            system_message = load_system_message()
            save_message(user_id, 'system', system_message)
            messages = [("system", system_message)]
        else:
            # Load existing conversation messages
            messages = conversation
        
        # Append the user's new message to the conversation
        save_message(user_id, 'human', user_message)
        messages.append(("human", user_message))
        
        # Pass the conversation history to the agent and log the intermediate steps
        for step in agent.stream({"messages": messages}, stream_mode="updates"):
            if "agent" in step:
                logging.info(f"Agent message: {step['agent']['messages']}")
            elif "tools" in step:
                logging.info(f"Tool message: {step['tools']['messages']}")

        # Get the agent's final response content
        agent_response = step["agent"]["messages"][-1].content
        
        # Save the agent's response to the database
        save_message(user_id, 'system', agent_response)
        logging.info(f"Agent response for user_id={user_id}: {agent_response}")

        # Return the response as JSON
        return jsonify(agent_response), 200

    except Exception as e:
        logging.error(f"Error processing request: {str(e)}")
        return jsonify({"error": str(e)}), 500

    except Exception as e:
        logging.error(f"Error processing request: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    logging.info("Starting Flask application...")
    app.run(host='0.0.0.0', port=5000, debug=True)
