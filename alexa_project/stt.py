# Offline Speech Recognition using Vosk API

import vosk
import sounddevice as sd
import json
import os

sd.default.device = (0, 0)  # (input, output)



# Safe model loading
try:
    model_en = vosk.Model("models/vosk-en") if os.path.exists("models/vosk-en") else None
except:
    model_en = None

try:
    model_hi = vosk.Model("models/vosk-hi") if os.path.exists("models/vosk-hi") else None
except:
    model_hi = None

def listen(lang="en"):
    try:
        model = model_hi if lang == "hi" else model_en
        if model is None:
            return ""

        rec = vosk.KaldiRecognizer(model, 16000)

        with sd.RawInputStream(
            samplerate=16000,
            blocksize=8000,
            dtype='int16',
            channels=2,     # MUST stay 2
            device=0
        ) as stream:

            data, overflowed = stream.read(8000)
            if overflowed:
                print("Audio buffer overflowed")
            if data is None:
                return ""

            # ✅ stereo → mono conversion
            data = data[::2]

            rec.AcceptWaveform(data.tobytes())
            result = json.loads(rec.Result())

            print("User:", result.get("text", ""))
            return result.get("text", "")

    except Exception as e:
        print("STT error:", e)
        return ""

