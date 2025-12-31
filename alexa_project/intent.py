# =====================================
# ALEXALITE - INTENT DETECTION ENGINE
# English + Hindi + Hinglish + ML + JSON
# =====================================

import json
import os
from rapidfuzz import fuzz

from hindi_intent import detect_hindi_intent

# ML intent is optional (PART 4)
try:
    from ml_intent import predict_intent
except:
    predict_intent = None

# -------------------------------------
# FILES
# -------------------------------------
MANUAL_FILE = "data/manual_intents.json"

# -------------------------------------
# ALL INTENTS (ENGLISH + HINDI WORDS)
# -------------------------------------
INTENTS = {
    # 🎶 MUSIC
    "play": [
        "play", "chalao", "bajao", "gana", "gaana"
    ],
    "play_last": [
        "last song", "pichla gana", "last gana"
    ],
    "favorite": [
        "favorite", "like", "pasand"
    ],
    "playlist": [
        "playlist", "suchi"
    ],
    "artist": [
        "songs by", "artist ke gane"
    ],

    # 🔊 VOLUME
    "volume_up": [
        "volume up", "awaz badhao", "avaj tej", "tez karo"
    ],
    "volume_down": [
        "volume down", "awaz kam", "avaj dheemi", "slow karo"
    ],

    # 🌦 WEATHER
    "weather": [
        "weather", "mausam", "mosam"
    ],

    # ❓ QUESTION
    "question": [
        "what", "who", "why", "how",
        "kya", "kaun", "kyon", "kaise"
    ],

    # 🔔 ALARM
    "alarm": [
        "alarm", "reminder", "yaad dilao"
    ],

    # 🎙 MIC
    "mute": [
        "mute", "mic band", "chup"
    ],
    "unmute": [
        "unmute", "mic chalu", "sun"
    ]
}

# -------------------------------------
# LOAD MANUAL INTENTS (JSON SAFE)
# -------------------------------------
def load_manual_intents():
    try:
        if not os.path.exists(os.path.dirname(MANUAL_FILE)):
            os.makedirs(os.path.dirname(MANUAL_FILE))

        if not os.path.exists(MANUAL_FILE):
            with open(MANUAL_FILE, "w") as f:
                json.dump({}, f)

        with open(MANUAL_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

# -------------------------------------
# ADD MANUAL INTENT (SAFE WRITE)
# -------------------------------------
def add_manual_intent(word, intent):
    try:
        data = load_manual_intents()
        data[word.lower()] = intent
        with open(MANUAL_FILE, "w") as f:
            json.dump(data, f, indent=2)
    except:
        pass


# -------------------------------------
# MAIN DETECT FUNCTION
# -------------------------------------
def detect(text):
    if not text:
        return "unknown"

    text = text.lower().strip()

    # 1️⃣ ML INTENT (highest priority)
    if predict_intent:
        ml = predict_intent(text)
        if ml:
            return ml

    # 2️⃣ MANUAL JSON INTENTS
    manual = load_manual_intents()
    for word, intent in manual.items():
        if fuzz.partial_ratio(text, word) > 80:
            return intent

    # 3️⃣ RULE + FUZZY (EN + HI + HINGLISH)
    best_intent = "unknown"
    best_score = 0

    for intent, keywords in INTENTS.items():
        for key in keywords:
            score = fuzz.partial_ratio(text, key)
            if score > best_score:
                best_score = score
                best_intent = intent

    if best_score >= 65:
        return best_intent

    # 4️⃣ FINAL FALLBACK (Hindi fuzzy)
    return detect_hindi_intent(text)
