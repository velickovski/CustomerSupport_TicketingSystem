from flask import Flask, render_template, send_from_directory
from flask_socketio import SocketIO, emit
from dotenv import load_dotenv
import openai
import os
import numpy as np

# Load environment variables
load_dotenv()

# Initialize Flask and Flask-SocketIO
app = Flask(__name__, static_folder='templates')
socketio = SocketIO(app)

# Initialize OpenAI client
openai.api_key = os.getenv('OPENAI_API_KEY')

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
                ongoing_request['stream'].close()

            response_stream = openai.ChatCompletion.create(
                model="gpt-4",
                messages=conversation_history,
                stream=True
            )

            ongoing_request = {'stream': response_stream, 'message_id': str(len(conversation_history))}

            response_text = ""
            for chunk in response_stream:
                if 'choices' in chunk and len(chunk['choices']) > 0:
                    delta_content = chunk['choices'][0].get('delta', {}).get('content', '')
                    if delta_content:
                        response_text += delta_content
                        emit('response', {'message_id': ongoing_request['message_id'], 'message': delta_content, 'formatted': False})

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

if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
