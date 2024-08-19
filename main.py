from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import openai
import os
from dotenv import load_dotenv
import markdown
# Load environment variables
load_dotenv()

# Initialize Flask and Flask-SocketIO
app = Flask(__name__)
socketio = SocketIO(app)

# Initialize OpenAI client
openai.api_key = os.getenv('OPENAI_API_KEY')

# Store conversation history
conversation_history = []

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('message')
def handle_message(data):
    global conversation_history

    user_input = data['message']
    conversation_history.append({"role": "user", "content": user_input})

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=conversation_history,
            stream=True
        )

        response_text = ""
        markdown_needed = False  # Determine if markdown is needed

        for chunk in response:
            if 'choices' in chunk and len(chunk['choices']) > 0:
                delta_content = chunk['choices'][0].get('delta', {}).get('content', '')
                if delta_content:
                    response_text += delta_content
                    markdown_needed = markdown_needed or detect_markdown(delta_content)  # Detect markdown

                    emit('response', {'message_id': str(len(conversation_history)), 'message': delta_content, 'formatted': False})

        if markdown_needed:
            formatted_text = markdown.markdown(response_text)
            emit('response', {'message_id': str(len(conversation_history)), 'message': formatted_text, 'formatted': True})

    except Exception as e:
        emit('response', {'message_id': str(len(conversation_history)), 'message': f"Error: {str(e)}", 'formatted': True})

def detect_markdown(text):
    # Implement logic to detect if the text contains markdown syntax
    return any(char in text for char in ['*', '_', '#', '-'])

if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
