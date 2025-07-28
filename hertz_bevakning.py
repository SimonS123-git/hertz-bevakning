#!/usr/bin/env python3
import json
import requests
from bs4 import BeautifulSoup

# ntfy-topic som du prenumererar på i mobilen
NTFY_TOPIC = "Hertzbil_Sthlm-OSD"

# Städer att matcha (Visby ↔ Stockholm)
FROM_CITY = "Visby"
TO_CITY   = "Stockholm"

def skicka_notis(meddelande):
    """Skicka push-notis via ntfy."""
    print(f"📲 Skickar notis: {meddelande}")
    requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", data=meddelande.encode("utf-8"))

def kontrollera_resor():
    print("▶️ Börjar kontrollera_resor()")
    resp = requests.get("https://www.hertzfreerider.se/sv-se", timeout=20)
    if resp.status_code != 200:
        print(f"⚠️ Fel vid HTTP-anrop: {resp.status_code}")
        return

    soup = BeautifulSoup(resp.text, "html.parser")

    # Hitta script‐taggen oavsett typ-attribut
    tag = soup.find("script", id="__NEXT_DATA__")
    if not tag:
        print("⚠️ Kunde inte hitta <script id=\"__NEXT_DATA__\">")
        return

    raw = tag.string or tag.text
    print("🔍 Hittade __NEXT_DATA__, första 200 tecken:")
    print(raw[:200].replace("\n", ""))  # debug: visa början av JSON

    try:
        data = json.loads(raw)
    except Exception as e:
        print("⚠️ Kunde inte tolka JSON:", e)
        return

    payload = json.dumps(data)  # gör hela JSON till text
    if FROM_CITY in payload and TO_CITY in payload:
        skicka_notis(f"🚗 Möjlig resa {FROM_CITY} ↔ {TO_CITY} finns! Kolla Hertz Freerider.")
    else:
        print(f"❌ Inga resor {FROM_CITY} ↔ {TO_CITY} funna i JSON-datan.")

if __name__ == "__main__":
    kontrollera_resor()