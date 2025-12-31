



import json, os
from ml_intent import train_model

DATA_FILE = "data/intent_train.json"


def load_data():
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except:
        return []


def save_data(data):
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    try:
        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=2)
    except:
        pass


def learn(text, intent):
    data = load_data()

    # Avoid duplicates
    for d in data:
        if d.get("text") == text:
            return

    data.append({
        "text": text,
        "intent": intent
    })

    save_data(data)

    # retrain when data grows
    if len(data) % 5 == 0:
        train_model()
