# app remake.py

from flask import Flask, request, jsonify
from flask_cors import CORS
import webbrowser
from datetime import datetime
from pytz import timezone
import google.generativeai as genai

# --- Gemini API Configuration ---
# IMPORTANT: Replace "YOUR_API_KEY_HERE" with your actual API key
try:
    genai.configure(api_key="AIzaSyBNytWCdBJa_NgQzIU7N975Nn5SuXt98aw")
    model = genai.GenerativeModel('gemini-2.5-flash')
    # Start a chat session to maintain conversation history (memory)
    chat = model.start_chat(history=[])
    print("Gemini Chat Session Initialized.")
except Exception as e:
    print(f"Error initializing Gemini API: {e}")
    chat = None
# --------------------------------

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

def handle_user_input(user_input):
    """
    Handles the user's input by checking for local commands first,
    then falling back to the Gemini chat session for general queries.
    """
    processed_input = user_input.lower().strip()

    # --- Local command checks (no memory needed) ---
    if "calculate" in processed_input:
        try:
            expression = processed_input.split("calculate", 1)[1].strip()
            # A safer way to evaluate mathematical expressions
            result = eval(expression, {"__builtins__": None}, {})
            return f"The result of {expression} is {result}."
        except Exception as e:
            return f"Sorry, I couldn't calculate that. Error: {str(e)}"
    
    elif "open" in processed_input:
        url = processed_input.split("open", 1)[1].strip()
        if not url.startswith("http://") and not url.startswith("https://"):
            url = "https://" + url
        webbrowser.open(url)
        return f"Opening {url} for you."

    elif "time" in processed_input or "current time" in processed_input:
        ist = timezone('Asia/Kolkata')
        current_time = datetime.now(ist).strftime('%H:%M %p (%Z)')
        return f"The current time in India is {current_time}."
    
    elif processed_input in ["hello", "hi", "hey"]:
        return "Hello! How can I assist you today?"
    
    elif "what is your name" in processed_input or "who are you" in processed_input:
        return "I'm LUNA, your everyday AI Assistant, powered by Google Gemini."
    
    elif processed_input in ["bye", "goodbye"]:
        return "Goodbye! Have a great day!"

    # --- Fallback to Gemini API with memory ---
    else:
        if not chat:
            return "Sorry, the connection to the AI model isn't configured correctly."
        try:
            # Send the user message to the ongoing chat session
            response = chat.send_message(user_input)
            return response.text
        except Exception as e:
            print(f"Gemini API Error: {e}")
            return "Sorry, I'm having a little trouble connecting to my brain right now. Please try again in a moment."

@app.route('/chat', methods=['POST'])
def chat_endpoint():
    user_message = request.json.get('message', '')
    if not user_message:
        return jsonify({'response': 'Please enter a message.'})
    
    response_message = handle_user_input(user_message)
    return jsonify({'response': response_message})

if __name__ == '__main__':
    app.run(debug=True)
