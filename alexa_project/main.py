# ================================
# ALEXALITE - MAIN BRAIN
# ================================

import time

from wakeword import listen_wake
from stt import listen
from tts import speak
from intent import detect
from mic import is_muted, mute, unmute
from night import silent_now

from profiles import identify_user, update_history
from learner import learn

import music
import volume
import weather
import qa
import alarm

# ================================
# MAIN LOOP
# ================================

print("AlexaLite started...")

while True:
    # 🔔 Check alarm every loop (non-blocking)
    try:
        alarm.check_alarm()
    except Exception as e:
        print("Alarm error:", e)
    time.sleep(0.2)

    # 🎙 If mic muted, do nothing
    if is_muted():
        continue

    # 👂 Wait for wake word
    try:
        listen_wake()
    except Exception as e:
        print("Wake word error:", e)
        continue

    # 🌙 Night mode handling
    if not silent_now():
        speak("Yes?", "en")

    # 🎧 Listen command (Hindi preferred)
    try:
        text = listen("hi")
    except Exception as e:
        print("STT error:", e)
        text = ""

    if not text:
        continue

    print("Heard:", text)

    # 👤 Identify user
    try:
        user = identify_user(text)
        update_history(user, text)
    except Exception as e:
        print("User profile error:", e)
        user = "user_1"

    # 🧠 Detect intent
    try:
        intent = detect(text)
    except Exception as e:
        print("Intent detection error:", e)
        intent = "unknown"
    print("Intent:", intent)

    # 🧠 Learn successful intent
    if intent != "unknown":
        try:
            learn(text, intent)
        except Exception as e:
            print("Learning error:", e)

    # ============================
    # 🎶 MUSIC INTENTS
    # ============================

    try:
        if intent == "play":
            song = (
                text.replace("play", "")
                    .replace("chalao", "")
                    .replace("bajao", "")
                    .strip()
            )
            music.play_song(song)

        elif intent == "play_last":
            if not music.play_last():
                speak("No previous song found", "en")

        elif intent == "favorite":
            music.add_favorite(text)
            speak("Added to favorites", "en")

        elif intent == "playlist":
            music.play_playlist("default")

        elif intent == "artist":
            artist = text.replace("songs by", "").strip()
            music.play_artist(artist)
    except Exception as e:
        print("Music error:", e)

    # ============================
    # 🌦 WEATHER
    # ============================

    if intent == "weather":
        try:
            # Auto-detect city from speech
            weather_text = weather.get_weather(text)
            speak(weather_text, "en")
        except Exception as e:
            print("Weather error:", e)
            speak("Weather service unavailable", "en")

    # ============================
    # 🌐 QUESTION / ANSWER
    # ============================

    elif intent == "question":
        try:
            answer = qa.ask_question(text)
            speak(answer, "en")
        except Exception as e:
            print("QA error:", e)
            speak("Cannot answer now", "en")

    # ============================
    # 🔔 ALARM
    # ============================

    elif intent == "alarm":
        try:
            t = text.split()[-1]
            speak(alarm.set_alarm(t), "en")
        except Exception as e:
            print("Alarm set error:", e)

    # ============================
    # 🔊 VOLUME
    # ============================

    elif intent == "volume_up":
        try:
            volume.volume_up()
            speak("Volume increased", "en")
        except Exception as e:
            print("Volume up error:", e)

    elif intent == "volume_down":
        try:
            volume.volume_down()
            speak("Volume decreased", "en")
        except Exception as e:
            print("Volume down error:", e)

    # ============================
    # 🎙 MIC CONTROL
    # ============================

    elif intent == "mute":
        try:
            speak(mute(), "en")
        except Exception as e:
            print("Mute error:", e)

    elif intent == "unmute":
        try:
            speak(unmute(), "en")
        except Exception as e:
            print("Unmute error:", e)

    # ============================
    # ❓ UNKNOWN
    # ============================

    else:
        speak("I did not understand", "en")
