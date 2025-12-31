#🌙 night.py — Night Silent Hours


import time

SILENT_START = 23   # 11 PM
SILENT_END = 4      # 4 AM

def silent_now():
    h = int(time.strftime("%H"))
    return h >= SILENT_START or h < SILENT_END
