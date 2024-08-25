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
from langgraph.checkpoint.postgres import PostgresSaver
from tools.create_wallet import CreateWalletTool
from tools.fund_wallet import FundWalletTool
from tools.transfer_funds import TransferFundsTool
from tools.get_balance import GetWalletBalanceTool
import json
from sqlalchemy import text

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

# Model definition for user wallet information
class UserWallet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(255), nullable=False, unique=True)
    wallet_id = db.Column(db.String(255), nullable=False)
    wallet_address = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, server_default=db.func.now())

# Initialize the LLM with the OpenAI API key from the environment
llm = ChatOpenAI(model="gpt-4o-mini", temperature=1, api_key=os.getenv("OPENAI_API_KEY"))

# Initialize the tools from the provided files
create_wallet_tool = CreateWalletTool()
fund_wallet_tool = FundWalletTool()
transfer_funds_tool = TransferFundsTool()
get_balance_tool = GetWalletBalanceTool(web3_provider_url=os.getenv("WEB3_PROVIDER_URL"))

# List of tools to be used by the agent
tools = [
    fund_wallet_tool, 
    transfer_funds_tool, 
    get_balance_tool, 
    create_wallet_tool
]

# Save wallet information to the database
def save_wallet_info(user_id, wallet_id, wallet_address):
    try:
        new_wallet = UserWallet(user_id=user_id, wallet_id=wallet_id, wallet_address=wallet_address)
        db.session.add(new_wallet)
        db.session.commit()
        logging.debug(f"Saved wallet info to database: user_id={user_id}, wallet_id={wallet_id}, wallet_address={wallet_address}")
    except Exception as e:
        logging.error(f"Failed to save wallet info: {str(e)}")
        db.session.rollback()

# Function to load the system message
def load_system_message():
    try:
        with open('./prompts/malice_prompt.txt', 'r') as file:
            system_message = file.read().strip()
            logging.debug("Loaded system message.")
            return system_message
    except Exception as e:
        logging.error(f"Failed to load system message: {str(e)}")
        return ""

def get_existing_wallet(user_id):
    wallet = UserWallet.query.filter_by(user_id=user_id).first()
    return wallet

def setup_wallet(user_id):
    try:
        existing_wallet = get_existing_wallet(user_id)
        if existing_wallet:
            return json.dumps({"wallet_id": existing_wallet.wallet_id, "address": existing_wallet.wallet_address}), False

        # Create a new wallet if no existing wallet
        create_wallet_response = create_wallet_tool._run()
        wallet_info = json.loads(create_wallet_response)
        wallet_id = wallet_info['wallet_id']
        wallet_address = wallet_info['address']
        
        # Save wallet information to the database
        save_wallet_info(user_id, wallet_id, wallet_address)
        
        logging.info(f"Created and saved new wallet for user_id: {user_id}, wallet_id: {wallet_id}, address: {wallet_address}")
        return create_wallet_response, True
    except Exception as e:
        logging.error(f"Failed to create and save wallet: {str(e)}")
        return None

@app.route('/query-agent', methods=['POST'])
def query_agent():
    try:
        data = request.json
        logging.info(f"Received request data: {data}")
        user_id = data.get('user_id')
        user_message = data.get('message')
        logging.info(f"Received request: user_id={user_id}, message={user_message}")
        config = {"configurable": {"thread_id": user_id}}

        # Create the ReAct agent using the LangGraph create_react_agent method
        with PostgresSaver.from_conn_string(app.config['SQLALCHEMY_DATABASE_URI']) as checkpointer:
            checkpointer.setup()
            agent = create_react_agent(llm, tools, checkpointer=checkpointer)

            # Always begin/continue a conversation with system message and wallet informations
            wallet_message, is_new_wallet = setup_wallet(user_id)
            system_message = load_system_message()
            logging.info(f"Loaded system message: {system_message}")
            if is_new_wallet:
                messages = [
                    ("system", system_message),
                    ("system", str(wallet_message)),
                    ("human", user_message)
                ]
            else:
                messages = [
                    ("system",str(wallet_message)),
                    ("human", user_message)
                ]
            logging.info(f"Starting new conversation for user_id={user_id}")
        
            # Pass the conversation history to the agent and log the intermediate steps
            for step in agent.stream({"messages": messages}, stream_mode="updates", config=config):
                if "agent" in step:
                    logging.info(f"Agent message: {step['agent']['messages']}")
                elif "tools" in step:
                    logging.info(f"Tool message: {step['tools']['messages']}")

            # Get the agent's final response content
            agent_response = step["agent"]["messages"][-1].content
            
            logging.info(f"Agent response for user_id={user_id}: {agent_response}")

            # Return the response as JSON
            return jsonify(agent_response), 200

    except Exception as e:
        logging.error(f"Error processing request: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    logging.info("Starting Flask application...")
    app.run(host='0.0.0.0', port=5000, debug=True)