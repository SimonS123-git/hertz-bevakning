#!/usr/bin/env python3
import json
import requests
from bs4 import BeautifulSoup

NTFY_TOPIC = "Hertzbil_Sthlm-OSD"
FROM_CITY = "Visby"
TO_CITY   = "Stockholm"

def skicka_notis(meddelande):
    print(f"📲 Skickar notis: {meddelande}")
    requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", data=meddelande.encode("utf-8"))

def kontrollera_resor():
    print("▶️ Börjar kontrollera_resor()")
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/116.0.0.0 Safari/537.36"
        )
    }
    resp = requests.get("https://www.hertzfreerider.se/sv-se", headers=headers, timeout=20)
    print("🔗 HTTP-status:", resp.status_code)
    html = resp.text

    # Debug: visa de första 500 tecknen av HTML:en
    snippet = html.replace("\n", " ")[:500]
    print("🔍 HTML-snippet:", snippet, "...")

    soup = BeautifulSoup(html, "html.parser")
    tag = soup.find("script", id="__NEXT_DATA__")
    if not tag:
        print('⚠️ Kunde inte hitta <script id="__NEXT_DATA__">')
        return

    raw = tag.string or tag.text
    data = json.loads(raw)
    payload = json.dumps(data)

    if FROM_CITY in payload and TO_CITY in payload:
        skicka_notis(f"🚗 Möjlig resa {FROM_CITY} ↔ {TO_CITY} finns!")
    else:
        print(f"❌ Inga resor {FROM_CITY} ↔ {TO_CITY} funna i JSON-datan.")

if __name__ == "__main__":
    kontrollera_resor()