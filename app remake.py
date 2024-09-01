from flask import Flask, request, jsonify
from flask_cors import CORS
import webbrowser
from datetime import datetime
from pytz import timezone

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

def handle_user_input(user_input):
    user_input = user_input.lower().strip()

    if "calculate" in user_input:
        try:
            # Extract the expression and evaluate it
            expression = user_input.split("calculate", 1)[1].strip()
            result = eval(expression)
            return f"The result of {expression} is {result}."
        except Exception as e:
            return f"Error in calculation: {str(e)}"
    
    elif "open" in user_input:
        url = user_input.split("open", 1)[1].strip()
        if not url.startswith("http://") and not url.startswith("https://"):
            url = "http://" + url
        webbrowser.open(url)
        return f"Opening {url}"

    elif "time" in user_input or "current time" in user_input:
        ist = timezone('Asia/Kolkata')
        current_time = datetime.now(ist).strftime('%Y-%m-%d %H:%M:%S %Z %z')
        return f"Current time: {current_time}"
    
    elif "hello" in user_input or "hi" in user_input:
        return "Hello! How can I assist you today?"
    
    elif "what is your name" in user_input or "name" in user_input:
        return "Hey! My name is LUNA, your everyday AI Assistant."
    
    elif "bye" in user_input:
        return "Goodbye! Have a great day!"

    else:
        return "I'm sorry, I didn't understand that. You can ask me to calculate something, check the current time, or open a link."

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message', '')
    response_message = handle_user_input(user_message)
    return jsonify({'response': response_message})

if __name__ == '__main__':
    app.run(debug=True)
