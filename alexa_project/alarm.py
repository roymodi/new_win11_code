# 🔔 alarm.py — Alarm & Reminder System

# Voice:

# “Alexa set alarm 6:30”

# “Alexa reminder 8:00”


import time, json, os
from tts import speak

ALARM_FILE = "data/alarms.json"

def load_alarms():
    if not os.path.exists(ALARM_FILE):
        return []
    return json.load(open(ALARM_FILE))

def save_alarms(data):
    json.dump(data, open(ALARM_FILE, "w"), indent=2)

def set_alarm(time_str):
    alarms = load_alarms()
    alarms.append(time_str)
    save_alarms(alarms)
    return f"Alarm set for {time_str}"

def check_alarm():
    current = time.strftime("%H:%M")
    alarms = load_alarms()

    if current in alarms:
        speak("Alarm ringing", "en")
        alarms.remove(current)
        save_alarms(alarms)
