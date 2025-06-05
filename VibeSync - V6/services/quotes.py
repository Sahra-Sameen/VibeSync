import random, os, json
from services.groqapi import fetch_motivational_quote

fallback_quotes = {
    "happy": [
        "Keep shining, your smile is contagious!",
        "Enjoy the good vibes, and spread them around!",
        "Your happiness is your superpower."
    ],
    "sad": [
        "Tough times don't last, but tough people do.",
        "You're stronger than you think.",
        "Every storm runs out of rain."
    ],
    "angry": [
        "Pause. Breathe. Proceed with calm.",
        "Even fire needs air — give yourself space.",
        "Channel that energy into something powerful."
    ],
    "surprise": [
        "Life is full of surprises — make the most of them!",
        "Unexpected moments often lead to great things.",
        "Embrace the twist, it's part of your story."
    ],
    "fear": [
        "Courage is feeling fear and doing it anyway.",
        "You’ve made it through every challenge so far.",
        "Don’t let fear write your story."
    ],
    "disgust": [
        "Sometimes the mess leads to clarity.",
        "Let it pass. You’ve got better things to focus on.",
        "Not everything deserves your energy."
    ],
    "neutral": [
        "Today is a blank canvas — make it beautiful.",
        "You’re doing fine. Keep going.",
        "Consistency is powerful, even when things feel still."
    ]
}

def load_custom_quotes():
    quotes_file = "quotes.json"
    if os.path.exists(quotes_file):
        try:
            with open(quotes_file, "r") as file:
                quotes_data = json.load(file)
                for item in quotes_data:
                    quote = item.get("quote")
                    category = item.get("category", "neutral").lower()
                    if quote:
                        fallback_quotes.setdefault(category, []).append(quote)
        except Exception as e:
            print(f"[Quotes JSON load error] {e}")

# Load custom quotes into fallback_quotes on import
load_custom_quotes()

def fallback_quote(emotion):
    """
    Try to fetch an AI-generated quote using Groq based on emotion context.
    If that fails, fallback to static predefined quote.
    """
    try:
        user_state = {
            "emotion": emotion,
            "activity": {"typing_speed": 0, "mouse_speed": 0, "active_window": "VibeSync"}
        }
        quote = fetch_motivational_quote(user_state)
        if quote:
            return quote
    except Exception as e:
        print(f"[Quotes AI fallback error] {e}")

    quotes = fallback_quotes.get(emotion, fallback_quotes["neutral"])
    return random.choice(quotes)
