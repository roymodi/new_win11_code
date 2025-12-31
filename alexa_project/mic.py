#🎙 mic.py — Mic Mute / Unmute


MIC_MUTED = False

def mute():
    global MIC_MUTED
    MIC_MUTED = True
    return "Microphone muted"

def unmute():
    global MIC_MUTED
    MIC_MUTED = False
    return "Microphone unmuted"

def is_muted():
    return MIC_MUTED
