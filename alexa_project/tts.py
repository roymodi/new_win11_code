# Text to Speech (Hindi + English)

import os

def speak(text, lang="en", female=True):
    print("Alexa: ", text)
    try:
        if not text:
            return

        text = str(text).replace('"', '')

        # Female voices
        if lang == "hi":
            voice = "hi+f3" if female else "hi"
            os.system(f'espeak-ng -v {voice} "{text}"')
        else:
            voice = "en+f3" if female else "en"
            os.system(f'espeak-ng -v {voice} "{text}"')

    except:
        pass
