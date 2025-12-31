import requests
import gzip
import shutil

url = "https://assets.upstox.com/market-quote/instruments/exchange.csv.gz"

headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive"
}

r = requests.get(url, headers=headers, timeout=30)
r.raise_for_status()

with open("exchange.csv.gz", "wb") as f:
    f.write(r.content)

with gzip.open("exchange.csv.gz", "rb") as f_in:
    with open("exchange.csv", "wb") as f_out:
        shutil.copyfileobj(f_in, f_out)

print("Downloaded and extracted exchange.csv")
