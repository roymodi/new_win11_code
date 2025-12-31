import json, os, subprocess, time

SONGS = "data/songs.json"
PLAYLISTS = "data/playlists.json"
FAVORITES = "data/favorites.json"

# -------------------------------
# JSON LOAD / SAVE SAFE
# -------------------------------
def _ensure(path):
    folder = os.path.dirname(path)
    if folder and not os.path.exists(folder):
        os.makedirs(folder)
    if not os.path.exists(path):
        with open(path, "w") as f:
            json.dump({}, f)

def _load(path):
    try:
        _ensure(path)
        with open(path, "r") as f:
            return json.load(f)
    except:
        return {}

def _save(path, data):
    try:
        _ensure(path)
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
    except:
        pass

# -------------------------------
# Search YouTube only once
# -------------------------------
def search_youtube(song):
    cmd = f'yt-dlp "ytsearch1:{song}" --get-url --js-runtime node'
    return subprocess.getoutput(cmd)

# -------------------------------
# Check & refresh broken link
# -------------------------------
def validate_link(url):
    try:
        subprocess.check_output(
            ["yt-dlp", "--skip-download", url, "--js-runtime", "node"],
            stderr=subprocess.DEVNULL
        )
        return True
    except:
        return False

# -------------------------------
# PLAY SONG
# -------------------------------
def play_song(song, artist="unknown"):
    db = _load(SONGS)
    song = song.lower()

    if song in db:
        url = db[song]["url"]
        if not validate_link(url):
            url = search_youtube(song)
            db[song]["url"] = url
    else:
        url = search_youtube(song)
        db[song] = {
            "url": url,
            "artist": artist.lower(),
            "last_played": ""
        }

    db[song]["last_played"] = time.strftime("%Y-%m-%d %H:%M")
    _save(SONGS, db)

    # Non-blocking VLC with JS support
    os.system(f'cvlc "$(yt-dlp -f ba -g --js-runtime node \\"{url}\\")" &')

# -------------------------------
# PLAY LAST SONG
# -------------------------------
def play_last():
    db = _load(SONGS)
    if not db:
        return False

    last = max(db.items(), key=lambda x: x[1]["last_played"])
    url = last[1]["url"]
    os.system(f'cvlc "$(yt-dlp -f ba -g --js-runtime node \\"{url}\\")" &')
    return True

# -------------------------------
# FAVORITES
# -------------------------------
def add_favorite(song):
    fav = _load(FAVORITES)
    fav[song] = True
    _save(FAVORITES, fav)

def play_favorites():
    fav = _load(FAVORITES)
    songs = _load(SONGS)

    for s in fav:
        if s in songs:
            url = songs[s]["url"]
            os.system(f'cvlc "$(yt-dlp -f ba -g --js-runtime node \\"{url}\\")" &')

# -------------------------------
# PLAYLISTS
# -------------------------------
def add_to_playlist(name, song):
    pl = _load(PLAYLISTS)
    pl.setdefault(name, []).append(song)
    _save(PLAYLISTS, pl)

def play_playlist(name):
    pl = _load(PLAYLISTS)
    songs = _load(SONGS)

    if name not in pl:
        return

    for s in pl[name]:
        if s in songs:
            url = songs[s]["url"]
            os.system(f'cvlc "$(yt-dlp -f ba -g --js-runtime node \\"{url}\\")" &')

# -------------------------------
# ARTIST PLAY
# -------------------------------
def play_artist(artist):
    songs = _load(SONGS)
    for s, meta in songs.items():
        if meta["artist"] == artist.lower():
            url = meta["url"]
            os.system(f'cvlc "$(yt-dlp -f ba -g --js-runtime node \\"{url}\\")" &')
