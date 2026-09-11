import os
import requests
import re
from urllib.parse import urlparse

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
INITIAL_URL = "https://www.1tamilmv.meme/"
CACHE_FILE = "last_url.txt"

def send_telegram_alert(new_url: str):
    endpoint = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": f"🚨 *TamilMV New URL Detected!*\n\n{new_url}",
        "parse_mode": "Markdown"
    }
    try:
        res = requests.post(endpoint, json=payload, timeout=15)
        res.raise_for_status()
        print("Telegram alert sent successfully.")
    except Exception as e:
        print(f"Failed to send Telegram message: {e}")

def resolve_domain():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    }
    
    response = requests.get(INITIAL_URL, headers=headers, allow_redirects=True, timeout=25)
    final_url = response.url

    # Check for meta-refresh redirects
    text = response.text
    meta_match = re.search(r'content=["\']\d+;\s*url=([^"\']+)["\']', text, re.IGNORECASE)
    if meta_match:
        final_url = meta_match.group(1).strip()

    parsed = urlparse(final_url)
    return f"{parsed.scheme}://{parsed.netloc}/"

def main():
    if not BOT_TOKEN or not CHAT_ID:
        print("Missing credentials.")
        return

    try:
        current_url = resolve_domain()
        print(f"Resolved URL: {current_url}")
    except Exception as e:
        print(f"Failed to resolve URL: {e}")
        return

    old_url = ""
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            old_url = f.read().strip()

    if current_url != old_url:
        print(f"URL changed: '{old_url}' -> '{current_url}'")
        send_telegram_alert(current_url)
        with open(CACHE_FILE, "w") as f:
            f.write(current_url)
    else:
        print("No change detected.")

if __name__ == "__main__":
    main()
