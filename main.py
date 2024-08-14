from openai import OpenAI
from gtts import gTTS
import os
from fuzzywuzzy import fuzz
from dotenv import load_dotenv
import time

# Load environment variables from .env file
load_dotenv()

# Access environment variables
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
HUGGINGFACE_API_KEY = os.getenv('HUGGINGFACE_API_KEY')
HUGGINGFACE_BASE_URL = os.getenv('HUGGINGFACE_BASE_URL')

# Initialize OpenAI client
client = OpenAI(
    base_url=HUGGINGFACE_BASE_URL,
    api_key=HUGGINGFACE_API_KEY
)

def guard_check(content):
    chat_completion = client.chat.completions.create(
        model="tgi",
        messages=[
            {
                "role": "user",
                "content": content
            }
        ],
        stream=True,
        max_tokens=20
    )
    flag = True
    for message in chat_completion:
        if message.choices[0].delta.content == "unsafe":
            flag = False
    return flag

# Allowed topics for the chatbot
ALLOWED_TOPICS = ["airplanes", "cars"]

def is_question_within_topic_fuzzy(question: str, allowed_topics: list):
    for topic in allowed_topics:
        if fuzz.partial_ratio(topic.lower(), question.lower()) > 70:
            return True
    return False
#SIMULIRAJ SS OPENAI NE SS DELAY
def type_out_text(text, delay=0.05):
    for char in text:
        print(char, end='', flush=True)
        time.sleep(delay)
    print()  # Move to the next line after typing the text

def chatbot(prompt):
    try:
        clients = OpenAI(api_key=OPENAI_API_KEY)
        response = clients.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        response_text = response.choices[0].message.content.strip()
        return response_text
    except Exception as e:
        return f"Error: {str(e)}"

def speak_text(text):
    tts = gTTS(text, lang='en', tld='com', slow=False)
    tts.save("response.mp3")
    os.system("mpg123 response.mp3 > /dev/null 2>&1")

def greeting():
    greeting_message = "Hi! How can I help you today?"
    print("Chatbot: ", end='')
    type_out_text(greeting_message)
    speak_text(greeting_message)


if __name__ == "__main__":
    greeting()
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            print("Chatbot: ", end='')
            type_out_text("Goodbye!")
            speak_text("Goodbye!")
            break

        if guard_check(user_input):
            if is_question_within_topic_fuzzy(user_input, ALLOWED_TOPICS):
                response = chatbot(user_input)
                print("Chatbot: ", end='')
                type_out_text(response)
                speak_text(response)
            else:
                print("Chatbot: Not in the topic for the day")
                speak_text("Not in the topic for the day")
        else:
            print("Chatbot: Not safe for our ChatBot!")
            speak_text("Not safe for our ChatBot")