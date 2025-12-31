import sounddevice as sd
import vosk
import queue
import sys
import json
import numpy as np

MODEL_PATH = "vosk-model-small-en-us-0.15"
SAMPLE_RATE = 48000
CHANNELS = 2
BLOCKSIZE = 16000
AMPLIFY = 3  # Multiply audio by 3 for louder input

model = vosk.Model(MODEL_PATH)
rec = vosk.KaldiRecognizer(model, SAMPLE_RATE)

q = queue.Queue()

def audio_callback(indata, frames, time, status):
    if status:
        print(status, file=sys.stderr)
    # Convert stereo to mono
    mono_data = indata[:, 0].copy()
    # Amplify audio
    mono_data = np.int16(mono_data * AMPLIFY)
    q.put(mono_data.tobytes())

# Set your device index for Google VoiceHAT
device_index = 0

print(f"Using device index: {device_index}")
print("Listening... Press Ctrl+C to stop")

try:
    with sd.InputStream(samplerate=SAMPLE_RATE,
                        blocksize=BLOCKSIZE,
                        dtype='int16',
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
            else:
                # Show partial results for real-time feedback
                partial = json.loads(rec.PartialResult())
                ptext = partial.get("partial", "")
                if ptext:
                    print("Partial:", ptext, end='\r')
except KeyboardInterrupt:
    print("\nStopped by user")
