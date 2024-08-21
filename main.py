from flask import Flask, render_template, send_from_directory
from flask_socketio import SocketIO, emit
import openai
import os
from dotenv import load_dotenv
import numpy as np

# Load environment variables
load_dotenv()

# Initialize Flask and Flask-SocketIO
app = Flask(__name__, static_folder='templates')
socketio = SocketIO(app)

# Initialize OpenAI client
openai.api_key = os.getenv('OPENAI_API_KEY')



# Store conversation history
conversation_history = [
    {"role": "system", "content": "You are a customer support chatbot for a jewelry shop, that never tells the user that is artifical inteligence and only be interested in jewelry and jewelry related questions, and act like a happy salesman that is always excited to help customers, that replies with max of 3 senteces(sometimes even less if needed or more if needed), and make sure the conversation is similar to real-life customer support conversation and be curious if the user mentions damaged jewelry is bought from our store (we only support goods that are bought from our store). Your job is to provide information about store hours that are from 9:00AM to 5PM, location that is Skopje, Macedonia, and jewelry care about every kind of jewelry. If a customer is unsatisfied, recommend calling the support phone number which is +xxxXXXxxx."}
]

# Example allowed topics
allowed_topics = ["jewelry care", "store hours", "location", "ticket creation", "support"]

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
        if similarity > 0.7:  # Adjust threshold as needed
            return True
    return False

@app.route('/')
def index():
    # Serve the front-end HTML page
    return send_from_directory('templates', 'index.html')

@socketio.on('message')
def handle_message(data):
    global conversation_history

    user_input = data['message']

    if is_topic_allowed(user_input):
        conversation_history.append({"role": "user", "content": user_input})

        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=conversation_history,
                stream=True
            )

            response_text = ""
            for chunk in response:
                if 'choices' in chunk and len(chunk['choices']) > 0:
                    delta_content = chunk['choices'][0].get('delta', {}).get('content', '')
                    if delta_content:
                        response_text += delta_content
                        emit('response', {'message_id': str(len(conversation_history)), 'message': delta_content, 'formatted': False})

            # Add the response to the conversation history
            conversation_history.append({"role": "assistant", "content": response_text})

        except Exception as e:
            emit('response', {'message_id': str(len(conversation_history)), 'message': f"Error: {str(e)}", 'formatted': True})

    else:
        # If the topic isn't allowed, suggest calling the support phone number
        response_text = "I'm sorry, I can only help with questions related to our store hours, location, or jewelry care. For other inquiries, please call our support at +38972400567."
        emit('response', {'message_id': str(len(conversation_history)), 'message': response_text, 'formatted': False})

        # Optionally add this to the conversation history
        conversation_history.append({"role": "assistant", "content": response_text})

if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0', port=5001, debug=True)
