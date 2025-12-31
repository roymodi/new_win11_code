import requests
import pandas as pd
import time
import os

# ----------------------------
# CONFIGURATION
# ----------------------------
API_KEY = "a01ee93b-a808-41ce-a298-c66b5e6c34b6"           # Replace with your Upstox API key
TOKEN_FILE = "token.txt"           # Access token saved here
INSTRUMENTS_FILE = "instruments.csv"
INSTRUMENTS_URL = "https://api-v2.upstox.com/instruments/download"  # hypothetical URL
LOG_FILE = "upstox_v2_log.txt"
BASE_URL = "https://api-v2.upstox.com"

FETCH_INTERVAL = 5  # seconds between fetches

# ----------------------------
# HELPER FUNCTIONS
# ----------------------------
def get_access_token():
    if not os.path.exists(TOKEN_FILE):
        print("Token file not found! Generate it first.")
        return None
    with open(TOKEN_FILE, "r") as f:
        return f.read().strip()

def download_instruments():
    """Download instruments CSV if missing"""
    try:
        log("Instruments file not found. Downloading...")
        response = requests.get(INSTRUMENTS_URL, timeout=15)
        if response.status_code == 200:
            with open(INSTRUMENTS_FILE, "wb") as f:
                f.write(response.content)
            log("Instruments CSV downloaded successfully.")
        else:
            log(f"Failed to download instruments: {response.status_code}")
            return False
    except Exception as e:
        log(f"Exception downloading instruments: {e}")
        return False
    return True

def load_instruments():
    if not os.path.exists(INSTRUMENTS_FILE):
        if not download_instruments():
            return []
    df = pd.read_csv(INSTRUMENTS_FILE)
    instruments = []
    for _, row in df.iterrows():
        instruments.append({
            "exchange": row["exchange"],
            "instrument_token": int(row["instrument_token"])
        })
    return instruments

def log(message):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] {message}\n")
    print(f"[{timestamp}] {message}")

def get_live_quotes(access_token, instruments):
    url = f"{BASE_URL}/market/live/feed"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "x-api-key": API_KEY
    }
    payload = {
        "feed_type": "ltp",  # last traded price
        "instruments": instruments
    }
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            log(f"Error {response.status_code}: {response.text}")
            return None
    except Exception as e:
        log(f"Exception fetching quotes: {e}")
        return None

# ----------------------------
# MAIN BOT
# ----------------------------
def main():
    access_token = get_access_token()
    if not access_token:
        return

    instruments = load_instruments()
    if not instruments:
        log("No instruments loaded. Exiting.")
        return

    log("Bot started. Fetching live quotes using API v2...")

    try:
        while True:
            data = get_live_quotes(access_token, instruments)
            if data and "data" in data:
                for item in data["data"]:
                    token = item.get("instrument_token")
                    ltp = item.get("last_price", "N/A")
                    # Find symbol from token
                    df = pd.read_csv(INSTRUMENTS_FILE)
                    symbol_row = df[df["instrument_token"] == token]
                    symbol = symbol_row["symbol"].values[0] if not symbol_row.empty else "Unknown"
                    log(f"{symbol} ({token}) LTP = {ltp}")
            time.sleep(FETCH_INTERVAL)
    except KeyboardInterrupt:
        log("Bot stopped by user.")

if __name__ == "__main__":
    main()
