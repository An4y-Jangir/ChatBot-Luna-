import os
import sys
import webbrowser

from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
from pytz import timezone

import mysql.connector
import google.generativeai as genai

# --- Configuration ---
API_KEY = os.environ.get("GEMINI_API_KEY", "AIzaSyBNytWCdBJa_NgQzIU7N975Nn5SuXt98aw")
genai.configure(api_key=API_KEY)

DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = "Sam@SQL"
DB_NAME = "chatbot_db"

# --- Initialize Database Function ---
def init_db():
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
        conn.database = DB_NAME
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_history (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_message TEXT NOT NULL,
                bot_response TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        cursor.close()
        conn.close()
        print("Database initialized successfully.")
    except mysql.connector.Error as err:
        print(f"Error initializing database: {err}")
        sys.exit(1)

def log_chat_to_db(user_message, response_message):
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO chat_history (user_message, bot_response) VALUES (%s, %s)",
            (user_message, response_message)
        )
        conn.commit()
        cursor.close()
        conn.close()
        print("Chat logged successfully.")
    except mysql.connector.Error as err:
        print(f"MySQL Error: {err}")
    except Exception as ex:
        print(f"Unexpected error: {ex}")

# --- Flask App ---
app = Flask(__name__)
CORS(app)

# --- Gemini Model Configuration ---
try:
    model = genai.GenerativeModel("gemini-2.5-flash")
except Exception as e:
    print(f"Error initializing Gemini model: {e}")
    model = None

# --- Core Chat Logic ---
def handle_user_input(user_input):
    user_input = user_input.lower().strip()

    if "calculate" in user_input:
        try:
            expr = user_input.split("calculate",1)[1].strip()
            result = eval(expr, {"__builtins__": None}, {})
            return f"The result of {expr} is {result}."
        except Exception:
            return "Sorry, I couldn't perform that calculation."
    elif "open" in user_input:
        url = user_input.split("open", 1)[1].strip()
        if not url.startswith("http"):
            url = f"https://{url.split(' ')[0]}"
        webbrowser.open(url)
        return f"Opening {url} for you."
    elif "time" in user_input or "current time" in user_input:
        ist = timezone("Asia/Kolkata")
        current_time = datetime.now(ist).strftime("%H:%M %p (%Z)")
        return f"The current time in India is {current_time}."
    elif user_input in ["hello", "hi", "hey"]:
        return "Hello! How can I assist you today?"
    elif "your name" in user_input or "who are you" in user_input:
        return "I'm LUNA, your everyday AI Assistant powered by Google Gemini."
    elif user_input in ["bye", "goodbye"]:
        return "Goodbye! Have a great day!"

    # Gemini fallback
    if not model:
        return "Sorry, Gemini model is not configured."
    try:
        response = model.generate_content(user_input)
        return response.text
    except Exception as e:
        print(f"Gemini API Error: {e}")
        return "Sorry, I'm having some trouble connecting to Gemini right now."

@app.route("/chat", methods=["POST"])
def chat_endpoint():
    user_message = request.json.get("message", "")
    if not user_message:
        return jsonify({"response": "Please enter a message."})
    response_message = handle_user_input(user_message)
    log_chat_to_db(user_message, response_message)
    return jsonify({"response": response_message})

if __name__ == "__main__":
    init_db()
    app.run(debug=True, host="127.0.0.1", port=5000)
