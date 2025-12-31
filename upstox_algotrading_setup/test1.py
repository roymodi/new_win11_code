import time
import os
from upstox_api.api import Upstox

# ----------------------------
# CONFIGURATION
# ----------------------------
API_KEY =   "a01ee93b-a808-41ce-a298-c66b5e6c34b6"                    #"YOUR_API_KEY"
API_SECRET = "fsl8m4awcd"                     #"YOUR_API_SECRET"
TOKEN_FILE = "token.txt"      # file containing your access token
LOG_FILE = "upstox_log.txt"   # log trades / quotes

# List of symbols you want to track
SYMBOLS = [
    ("NSE_EQ", "RELIANCE"),
    ("NSE_EQ", "TCS")
]

# ----------------------------
# HELPER FUNCTIONS
# ----------------------------
def get_access_token():
    """
    Read access token from file
    """
    if not os.path.exists(TOKEN_FILE):
        print("Access token file not found! Generate token first.")
        return None
    with open(TOKEN_FILE, "r") as f:
        token = f.read().strip()
    return token

def log(message):
    """
    Append message to log file
    """
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] {message}\n")
    print(f"[{timestamp}] {message}")

# ----------------------------
# MAIN
# ----------------------------
def main():
    access_token = get_access_token()
    if not access_token:
        return

    # Initialize Upstox
    u = Upstox(API_KEY, access_token)

    log("Bot started. Fetching live quotes...")

    try:
        while True:
            for exchange, symbol in SYMBOLS:
                try:
                    data = u.get_live_feed(exchange, symbol)
                    price = data['last_price']
                    log(f"{exchange}:{symbol} LTP = {price}")
                except Exception as e:
                    log(f"Error fetching {symbol}: {e}")

            time.sleep(5)  # wait 5 seconds before next fetch

    except KeyboardInterrupt:
        log("Bot stopped by user.")

if __name__ == "__main__":
    main()
