import os
import sys
import webbrowser
import json

from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime  # <-- Ensure this is imported
from pytz import timezone
import pytz  # <-- Ensure this is imported

import mysql.connector
import google.generativeai as genai

API_KEY = os.environ.get("GEMINI_API_KEY", "AIzaSyBNytWCdBJa_NgQzIU7N975Nn5SuXt98aw")
genai.configure(api_key=API_KEY)

DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = "Sam@SQL"
DB_NAME = "chatbot_db"

def get_db_connection():
    try:
        return mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
    except mysql.connector.Error as err:
        print(f"MySQL Connection Error: {err}", file=sys.stderr)
        return None

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
        print(f"Error initializing database: {err}", file=sys.stderr)

def log_chat_to_db(user_message, response_message):
    conn = get_db_connection()
    if not conn:
        return
    try:
        cursor = conn.cursor()
        
        # --- MODIFIED SECTION ---
        # Get the current time in UTC to ensure consistent timezone storage.
        # This overrides the 'DEFAULT CURRENT_TIMESTAMP' from the table definition.
        utc_now = datetime.now(pytz.utc)
        
        cursor.execute(
            # Explicitly insert the 'timestamp' column
            "INSERT INTO chat_history (user_message, bot_response, timestamp) VALUES (%s, %s, %s)",
            (user_message, response_message, utc_now)
        )
        # --- END OF MODIFIED SECTION ---
        
        conn.commit()
        print("Chat logged successfully (in UTC).")
    except mysql.connector.Error as err:
        print(f"MySQL Logging Error: {err}", file=sys.stderr)
    finally:
        if conn and conn.is_connected():
            conn.close()

def fetch_chat_history():
    conn = get_db_connection()
    if not conn:
        return []
    try:
        cursor = conn.cursor(dictionary=True)
        # We will now retrieve the UTC time we stored.
        cursor.execute("SELECT user_message, bot_response, timestamp FROM chat_history ORDER BY id DESC LIMIT 50")
        history = cursor.fetchall()
        
        # --- IST Timezone Conversion (This section is now correct) ---
        target_tz = timezone('Asia/Kolkata')
        
        processed_history = []
        for item in history:
            # Step 1: Get the naive datetime object from MySQL (which we know is UTC)
            naive_dt = item['timestamp']
            
            # Step 2: Localize the naive UTC time
            utc_dt = pytz.utc.localize(naive_dt)

            # Step 3: Convert the UTC-aware time to Indian Standard Time (IST).
            ist_time = utc_dt.astimezone(target_tz)
            
            # Step 4: Create a clean, formatted time string
            item['display_time'] = ist_time.strftime("%I:%M %p (%Z)") 

            processed_history.append(item)
        # ----------------------------------------------------------------------------
            
        return processed_history
    except mysql.connector.Error as err:
        print(f"MySQL Fetch Error: {err}", file=sys.stderr)
        return []
    finally:
        if conn and conn.is_connected():
            conn.close()

app = Flask(__name__)
CORS(app)

try:
    model = genai.GenerativeModel("gemini-2.5-flash")
except Exception as e:
    print(f"Error initializing Gemini model: {e}", file=sys.stderr)
    model = None

def handle_user_input(user_input):
    user_input_lower = user_input.lower().strip()
    
    if "calculate" in user_input_lower:
        try:
            expr = user_input_lower.split("calculate",1)[1].strip()
            result = eval(expr, {"__builtins__": None}, {})
            return f"The result of {expr} is {result}."
        except Exception:
            return "Sorry, I couldn't perform that calculation."
    
    elif user_input_lower in ["hello", "hi", "hey"]:
        return "Hello! How can I assist you today?"
        
    if not model:
        return "Sorry, Gemini model is not configured."
    try:
        response = model.generate_content(user_input)
        return response.text
    except Exception as e:
        print(f"Gemini API Error: {e}", file=sys.stderr)
        return "Sorry, I'm having some trouble connecting to Gemini right now."

@app.route("/chat", methods=["POST"])
def chat_endpoint():
    user_message = request.json.get("message", "")
    if not user_message:
        return jsonify({"response": "Please enter a message."})
        
    response_message = handle_user_input(user_message)
    
    log_chat_to_db(user_message, response_message)
    
    return jsonify({"response": response_message})

@app.route("/history", methods=["GET"])
def history_endpoint():
    history_data = fetch_chat_history()
    return jsonify(history_data)

if __name__ == "__main__":
    init_db()
    app.run(debug=True, host="127.0.0.1", port=5000)
