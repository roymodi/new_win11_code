import sounddevice as sd
import vosk
import queue
import sys
import json
import numpy as np

MODEL_PATH = "vosk-model-small-en-us-0.15"
SAMPLE_RATE = 48000

# Google VoiceHAT is stereo (2 channels)
CHANNELS = 2
BLOCKSIZE = 16000  # bigger block size reduces glitches

model = vosk.Model(MODEL_PATH)
rec = vosk.KaldiRecognizer(model, SAMPLE_RATE)

q = queue.Queue()

def audio_callback(indata, frames, time, status):
    if status:
        print(status, file=sys.stderr)
    # Convert stereo to mono by taking first channel
    mono_data = indata[:, 0].copy()
    q.put(mono_data.tobytes())

# Use the device index from sounddevice - here it is 0 for Google VoiceHAT
device_index = 0

print(f"Using device index: {device_index}")
print("Listening... Press Ctrl+C to stop")

try:
    with sd.InputStream(samplerate=SAMPLE_RATE,
                        blocksize=BLOCKSIZE,
                        dtype='int16',   # standard 16-bit PCM
                        channels=CHANNELS,
                        callback=audio_callback,
                        device=device_index):
        while True:
            data = q.get()
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                text = result.get("text", "")
                if text:
                    print("You said:", text)
except KeyboardInterrupt:
    print("\nStopped by user")
