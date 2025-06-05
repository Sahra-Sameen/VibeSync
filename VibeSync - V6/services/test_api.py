# test_groq.py
from groqapi import fetch_motivational_quote

fake_state = {
    "emotion": "sad",
    "activity": {
        "typing_speed": 0.4,
        "mouse_speed": 15.7,
        "active_window": "Visual Studio Code"
    }
}

quote = fetch_motivational_quote(fake_state)
print(f"Response: {quote}")
