import os
import urllib.request
import json
import time
from rapidfuzz import fuzz
import pymicro_wakeword as wakeword

# -------------------------------------
# CONFIG
# -------------------------------------
WAKE_JSON = "data/wake_words.json"
MIC_DEVICE = "hw:1,0"  # Replace with your I2S mic device
MODEL_DIR = "models"
MODEL_FILE = "alexa.tflite"
MODEL_PATH = os.path.join(MODEL_DIR, MODEL_FILE)
FUZZY_THRESHOLD = 80  # 0-100

# Alexa model download URL (from micro-wake-word-models repo)
ALEXA_MODEL_URL = "https://github.com/esphome/micro-wake-word-models/raw/main/alexa/alexa.tflite"

# -------------------------------------
# DEFAULT WAKE WORDS
# -------------------------------------
DEFAULT_WAKE_WORDS = [
    "alexa", "hey alexa", "hi alexa", "aa alexa", "alexaa",
    "a lexa", "a-lexa", "aleksa", "elaxa", "elaksa",
    "alex", "alexi", "alexa ji", "alexa suno", "alexa bolo"
]

# -------------------------------------
# SAFE JSON LOAD / CREATE
# -------------------------------------
def load_wake_words():
    try:
        os.makedirs(os.path.dirname(WAKE_JSON), exist_ok=True)
        if not os.path.exists(WAKE_JSON):
            with open(WAKE_JSON, "w") as f:
                json.dump(DEFAULT_WAKE_WORDS, f, indent=2)
            return DEFAULT_WAKE_WORDS
        with open(WAKE_JSON, "r") as f:
            data = json.load(f)
            return data if isinstance(data, list) else DEFAULT_WAKE_WORDS
    except Exception:
        return DEFAULT_WAKE_WORDS

# -------------------------------------
# ADD NEW WAKE WORD
# -------------------------------------
def add_wake_word(word):
    try:
        words = load_wake_words()
        word = word.lower().strip()
        if word not in words:
            words.append(word)
            with open(WAKE_JSON, "w") as f:
                json.dump(words, f, indent=2)
    except Exception:
        pass

# -------------------------------------
# DOWNLOAD MODEL IF MISSING
# -------------------------------------
def download_model():
    os.makedirs(MODEL_DIR, exist_ok=True)
    if not os.path.exists(MODEL_PATH):
        print(f"Downloading Alexa model to {MODEL_PATH}...")
        urllib.request.urlretrieve(ALEXA_MODEL_URL, MODEL_PATH)
        print("Download complete.")
    else:
        print("Alexa model already exists.")

# -------------------------------------
# INIT PYMICRO-WAKEWORD
# -------------------------------------
def init_wakeword():
    download_model()
    ww = wakeword.WakeWord(
        mic_device=MIC_DEVICE,
        model_path=MODEL_PATH,
        sensitivity=0.5
    )
    return ww

# -------------------------------------
# MAIN WAKE LISTENER WITH FUZZY CHECK
# -------------------------------------
def listen_wake():
    wake_words = load_wake_words()
    print("Listening for wake words:", wake_words)
    ww = init_wakeword()

    while True:
        try:
            detected_word = ww.listen()  # Blocks until wakeword detected

            if detected_word:
                # Fuzzy matching against JSON list
                for w in wake_words:
                    similarity = fuzz.partial_ratio(detected_word.lower(), w.lower())
                    if similarity >= FUZZY_THRESHOLD:
                        print("\nUser (wake):", detected_word)
                        print(f"Matched JSON word: {w} (Similarity: {similarity}%)")
                        print("Alexa: Yes?")
                        return True

            time.sleep(0.05)

        except Exception as e:
            print("Wake word error:", e)
            time.sleep(0.2)

# -------------------------------------
# RUN
# -------------------------------------
if __name__ == "__main__":
    listen_wake()
