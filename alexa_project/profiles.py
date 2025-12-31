import json, os

PROFILE_FILE = "data/users.json"


def load_profiles():
    try:
        if not os.path.exists("data"):
            os.makedirs("data")

        if not os.path.exists(PROFILE_FILE):
            return {}

        with open(PROFILE_FILE, "r") as f:
            return json.load(f)

    except:
        return {}


def save_profiles(data):
    try:
        if not os.path.exists("data"):
            os.makedirs("data")

        with open(PROFILE_FILE, "w") as f:
            json.dump(data, f, indent=2)

    except:
        pass


def identify_user(voice_text):
    """
    Simple heuristic user detection (name based)
    Example: 'I am Rahul', 'Mera naam Amit hai'
    """
    profiles = load_profiles()

    for name in profiles:
        if name.lower() in voice_text.lower():
            return name

    # New user auto-create
    user = "user_" + str(len(profiles) + 1)
    profiles[user] = {
        "language": "hi",
        "history": []
    }
    save_profiles(profiles)
    return user


def update_history(user, text):
    profiles = load_profiles()

    if user not in profiles:
        profiles[user] = {
            "language": "hi",
            "history": []
        }

    profiles[user]["history"].append(text)
    save_profiles(profiles)
