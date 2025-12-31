#Voice Volume Control

import os

def set_volume(level):
    level = max(0, min(100, level))
    os.system(f"amixer set PCM {level}%")

def volume_up():
    os.system("amixer set PCM 5%+")

def volume_down():
    os.system("amixer set PCM 5%-")
