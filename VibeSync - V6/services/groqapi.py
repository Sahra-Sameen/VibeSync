import os
import requests
import json
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
QUOTE_LOG_FILE = "data/last_quote.json"

HEADERS = {
    "Authorization": f"Bearer {GROQ_API_KEY}",
    "Content-Type": "application/json"
}

SYSTEM_PROMPT = {
    "role": "system",
    "content": (
        "You're a kind, motivational assistant who helps people stay mentally strong and productive. "
        "Given the user's emotional and activity state, respond with a short, uplifting message that speaks directly to them. "
        "Format your message as 3 clear lines like a poem or affirmation, no preface or formatting, just the 3-line quote."
        "You're a kind, motivational assistant who helps people stay mentally strong and productive. "
        "Given the user's emotional and activity state, respond with a short, uplifting message that speaks directly to them. "
        "No preface, no quotes or formatting, just a message like you're encouraging a friend. 1-2 sentences max."
    )
}

def is_quote_recent(quote):
    if not os.path.exists(QUOTE_LOG_FILE):
        return False
    try:
        with open(QUOTE_LOG_FILE, 'r') as f:
            data = json.load(f)
            last_quote = data.get("quote")
            timestamp = datetime.fromisoformat(data.get("timestamp"))
            if quote == last_quote and datetime.now() - timestamp < timedelta(hours=24):
                return True
    except:
        pass
    return False

def save_quote_log(quote):
    data = {
        "quote": quote,
        "timestamp": datetime.now().isoformat()
    }
    with open(QUOTE_LOG_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def fetch_motivational_quote(user_state):
    if not GROQ_API_KEY:
        print("[GroqAPI] Missing GROQ_API_KEY in .env")
        return None

    user_prompt = {
        "role": "user",
        "content": (
            f"The user is feeling {user_state['emotion']}. "
            f"They are currently using {user_state['activity']['active_window']} with a typing speed of "
            f"{user_state['activity']['typing_speed']} keys/sec and a mouse speed of "
            f"{user_state['activity']['mouse_speed']} px/sec. Please provide an encouraging, personal motivational message."
        )
    }

    data = {
        "model": "llama3-8b-8192",
        "messages": [SYSTEM_PROMPT, user_prompt],
        "temperature": 0.9
    }

    try:
        print("[GroqAPI] Sending request with state:", json.dumps(user_state, indent=2))
        response = requests.post(GROQ_URL, headers=HEADERS, json=data)
        if response.status_code == 200:
            content = response.json()['choices'][0]['message']['content'].strip()
            if is_quote_recent(content):
                print("[GroqAPI] Skipped repeated quote.")
                return None
            print(f"[GroqAPI] Quote: {content}")
            save_quote_log(content)
            return content
        else:
            print(f"[GroqAPI Error] {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"[GroqAPI Exception] {e}")
        return None
