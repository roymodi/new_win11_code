import os, json
from rapidfuzz import fuzz

MANUAL_FILE = "manual_intents.json"

def load_manual_intents():
    if not os.path.exists(MANUAL_FILE):
        try:
            with open(MANUAL_FILE, "w") as f:
                json.dump({}, f)
        except:
            pass
        return {}

    try:
        with open(MANUAL_FILE, "r") as f:
            return json.load(f)
    except:
        return {}
    
def save_unknown_word(word):
    data = load_manual_intents()

    if "unknown" not in data:
        data["unknown"] = []

    if word not in data["unknown"]:
        data["unknown"].append(word)

        try:
            with open(MANUAL_FILE, "w") as f:
                json.dump(data, f, indent=2)
        except:
            pass



INTENT_PATTERNS = {
    "play": [
        "chala", "baja", "play", "song", "gaana"
    ],
    "volume_up": [
        "awaz badha", "volume badha", "tez"
    ],
    "volume_down": [
        "awaz kam", "volume kam", "dhire"
    ],
    "weather": [
        "mausam", "weather", "baarish"
    ],
    "time": [
        "time", "samay", "kitna baja"
    ],
    "mute": [
        "mic band", "chup", "mute"
    ],
    "unmute": [
        "mic chalu", "sun", "unmute"
    ]
}

def detect_hindi_intent(text):
    text = text.lower()

    manual_intents = load_manual_intents()

    best_intent = None
    best_score = 0

    for intent, keywords in INTENT_PATTERNS.items():
        for word in keywords:
            score = fuzz.partial_ratio(text, word)
            if score > best_score:
                best_score = score
                best_intent = intent

    for intent, keywords in manual_intents.items():
        for word in keywords:
            score = fuzz.partial_ratio(text, word)
            if score > best_score:
                best_score = score
                best_intent = intent

    if best_score > 65:
        return best_intent
    # 🔹 ONLY ADDITION (unknown auto-save)
    save_unknown_word(text)
    return "unknown"

