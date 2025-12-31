import requests

def ask_question(question):
    try:
        url = "https://api.duckduckgo.com/"
        params = {
            "q": question,
            "format": "json",
            "no_redirect": 1,
            "no_html": 1
        }

        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        r = requests.get(url, params=params, headers=headers, timeout=5)

        if r.status_code != 200:
            return "Internet not available"

        data = r.json()

        if data.get("AbstractText"):
            return data["AbstractText"]
        else:
            return "I found something, but cannot summarize"

    except:
        return "Internet not available"
