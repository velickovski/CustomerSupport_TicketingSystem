from flask import Flask, render_template, send_from_directory
from flask_socketio import SocketIO, emit
from dotenv import load_dotenv
import openai
import os
import numpy as np
import json
import sqlite3
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pickle

# Load environment variables
load_dotenv()

# Initialize Flask and Flask-SocketIO
app = Flask(__name__, static_folder='templates')
socketio = SocketIO(app)

# Initialize OpenAI client
openai.api_key = os.getenv('OPENAI_API_KEY')

# Define tools for function calling
tools = [
    {
        "name": "create_ticket",
        "description": "Create a ticket for the user's issue. The user should provide their username and a description of the issue.",
        "parameters": {
            "type": "object",
            "properties": {
                "username": {
                    "type": "string",
                    "description": "The user's name.",
                },
                "description": {
                    "type": "string",
                    "description": "Description of the user's issue with a little more .",
                },
                "item": {
                    "type": "string",
                    "description": "Type of jewelry that the user have issue with (with everything that jewelry has attached to it or their material), first letter should be upper case"
                },
            },
            "required": ["username", "description"],
            "additionalProperties": False,
        },
    },
    {
        "name": "get_customer_support",
        "description": "Answer customer support related questions, only be interested in jewelry and pieces that are bought from the store",
        "parameters": {
            "type": "object",
            "properties": {
                "question": {
                    "type": "string",
                    "description": "Question about the store or the jewelry in it",
                },
            },
            "required": ["question"],
            "additionalProperties": False,
        },
    }
]

# Example allowed topics
allowed_topics = ["jewelry care", "store hours", "location", "ticket creation", "support"]

# Store conversation history
conversation_history = [
    {
        "role": "system",
        "content": (
            "You are a customer support chatbot for a jewelry shop. Your primary role is to assist customers "
            "with any inquiries related to jewelry, while always maintaining the demeanor of a cheerful and "
            "enthusiastic salesperson. It's essential that you never reveal you are an artificial intelligence; "
            "your goal is to create a seamless, human-like interaction.\n\n"
            
            "Your responsibilities include providing information about our store's operating hours, which are "
            "from 9:00 AM to 5:00 PM, and our location in Skopje, Macedonia. You should also offer detailed "
            "advice on how to care for various types of jewelry, ensuring customers can maintain their items "
            "in the best possible condition.\n\n"
            
            "If a customer mentions damaged jewelry, be particularly attentive, especially if the item was purchased "
            "from our store, as we only support goods bought from us. Show empathy and offer solutions, but remember, "
            "your responses should be concise, typically no more than three sentences. Sometimes, even shorter responses "
            "are appropriate, especially in fast-paced conversations.\n\n"
            
            "In situations where a customer is unsatisfied with the assistance provided, gently suggest they contact our "
            "support team via phone at +xxxXXXxxx. If a customer asks a question that isn't related to jewelry, kindly inform "
            "them that you are only equipped to handle jewelry-related inquiries."
        )
    }
]

# Function to get embeddings for allowed topics
def get_embeddings(topics):
    embeddings = {}
    for topic in topics:
        response = openai.Embedding.create(input=topic, model="text-embedding-ada-002")
        embeddings[topic] = response['data'][0]['embedding']
    return embeddings

# Store embeddings for allowed topics
allowed_embeddings = get_embeddings(allowed_topics)

# Function to calculate cosine similarity
def cosine_similarity(vec1, vec2):
    dot_product = np.dot(vec1, vec2)
    norm_vec1 = np.linalg.norm(vec1)
    norm_vec2 = np.linalg.norm(vec2)
    return dot_product / (norm_vec1 * norm_vec2)

def is_topic_allowed(user_input):
    user_embedding = openai.Embedding.create(input=user_input, model="text-embedding-ada-002")['data'][0]['embedding']
    for topic, embedding in allowed_embeddings.items():
        similarity = cosine_similarity(user_embedding, embedding)
        if similarity > 0.7:  # Threshold 
            return True
    return False

def is_description_match(input_description, db_path='tickets.db', threshold=0.7):
    # Connect to SQLite
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # Fetch descriptions and vectors from the database
    c.execute('SELECT description, vector FROM products')
    rows = c.fetchall()

    # Separate descriptions and vectors
    descriptions, vectors = zip(*rows)
    vectors = [pickle.loads(vector) for vector in vectors]

    # Initialize the vectorizer
    vectorizer = TfidfVectorizer()
    vectorizer.fit(descriptions)  # Fit on existing descriptions to maintain consistency

    # Vectorize the input description
    input_vector = vectorizer.transform([input_description])

    # Convert input_vector to dense format
    input_vector_dense = input_vector.toarray().flatten()

    # Convert vectors to dense format
    vectors_array_dense = np.array([vec.flatten() if hasattr(vec, 'flatten') else vec for vec in vectors])

    # Compute similarities
    similarities = np.array([cosine_similarity(input_vector_dense, vec) for vec in vectors_array_dense])

    # Find the maximum similarity score
    max_similarity = np.max(similarities)

    # Close the connection
    conn.close()

    # Return True if similarity is higher than the threshold, otherwise False
    return max_similarity > threshold

def check_id_exists(product_id):
    # Connect to the SQLite database
    conn = sqlite3.connect('tickets.db')
    cursor = conn.cursor()

    # SQL query to check if the ID exists
    query = "SELECT 1 FROM products WHERE ID = ?"
    cursor.execute(query, (product_id,))

    # Fetch one result
    result = cursor.fetchone()

    # Close the connection
    conn.close()

    return result is not None

def check_name_exists(name):
    # Connect to the SQLite database
    conn = sqlite3.connect('tickets.db')
    cursor = conn.cursor()

    # SQL query to check if the ID exists
    query = "SELECT 1 FROM users WHERE name = ?"
    cursor.execute(query, (name,))

    # Fetch one result
    result = cursor.fetchone()

    # Close the connection
    conn.close()

    return result is not None
# Function to create a ticket
def create_ticket(username, description):
    try:
        conn = sqlite3.connect('tickets.db')
        cursor = conn.cursor()

        # Create the tickets table if it doesn't already exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tickets (
                ticket_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                message TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        ''')

        # Insert a new ticket into the tickets table
        created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute('''
            INSERT INTO tickets (user_id, message, status, created_at)
            VALUES (?, ?, ?, ?)
        ''', (username, description, "open", created_at))

        conn.commit()
        conn.close()
        return f"Ticket created successfully for {username}. Your issue has been recorded and our support team will contact you shortly."
    except Exception as e:
        return f"Error: Could not create the ticket. Please try again. {e}"

# Function to handle customer support
def get_customer_support(question):
    # Logic to return customer support answers
    # For demonstration, we are returning a fixed response
    return "This is the customer support response."

@app.route('/')
def index():
    return send_from_directory('templates', 'index.html')

ongoing_request = None



@socketio.on('message')
def handle_message(data):
    global conversation_history, ongoing_request

    user_input = data['message']
    if is_topic_allowed(user_input):
        conversation_history.append({"role": "user", "content": user_input})

        try:
            if ongoing_request:
                ongoing_requespyt['stream'].close()

            response = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=conversation_history,
                functions=tools,
                function_call="auto"
            )

            # Check if the model requested to call a function for ticket_creation
            if response['choices'][0].get('finish_reason') == 'function_call':
                function_name = response['choices'][0]['message']['function_call']['name']
                arguments = json.loads(response['choices'][0]['message']['function_call']['arguments'])
                if function_name == "create_ticket":
                    username = arguments['username']
                    description = arguments['description']
                    item = arguments['item']
                    emit('ticket',{'username':username, 'description':description, 'item':item})
            else:
                response_text = response['choices'][0]['message']['content']

                emit('response', {'message_id': str(len(conversation_history)), 'message': response_text, 'formatted': False})

                # Add the response to the conversation history
                conversation_history.append({"role": "assistant", "content": response_text})

            ongoing_request = None

        except Exception as e:
            emit('response', {'message_id': str(len(conversation_history)), 'message': f"Error: {str(e)}", 'formatted': True})

    else:
        # If the topic isn't allowed, suggest calling the support phone number
        response_text = "I'm sorry, I can only help with questions related to our store. For other inquiries, please call our support at +38972400567."
        emit('response', {'message_id': str(len(conversation_history)), 'message': response_text, 'formatted': False})

        # Optionally add this to the conversation history
        conversation_history.append({"role": "assistant", "content": response_text})

@socketio.on('ticket_submission')
def handle_ticket_submission(data):
    username = data.get('username')
    description = data.get('description')
    id = data.get('id')
    product_description = data.get('product_description')
    if username and description and (check_id_exists(id) or is_description_match(product_description)) and check_name_exists(username):
        response_message = create_ticket(username, description)
        emit('response', {'message_id': str(len(conversation_history)), 'message': response_message})
    else:
        emit('response', {'message_id': str(len(conversation_history)), 'message': "That name or product doesn't exist in our sold item list."} )
if __name__ == "__main__":
    
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
