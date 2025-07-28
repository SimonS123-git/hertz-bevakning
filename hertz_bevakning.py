#!/usr/bin/env python3
import re
import json
import requests

# ntfy-topic som du prenumererar på i mobilen
NTFY_TOPIC = "Hertzbil_Sthlm-OSD"

# Städer att matcha
FROM_CITY = "Visby"
TO_CITY   = "Stockholm"

# En vanlig desktop-UA för att inte bli blockad
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/116.0.0.0 Safari/537.36"
    )
}

def skicka_notis(meddelande: str):
    print(f"📲 Skickar notis: {meddelande}")
    requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", data=meddelande.encode("utf-8"))

def kontrollera_resor():
    # 1) Hämta startsidan och extrahera build-ID
    resp = requests.get("https://www.hertzfreerider.se/sv-se", headers=HEADERS, timeout=20)
    resp.raise_for_status()
    html = resp.text

    m = re.search(r'/_next/static/([^/]+)/', html)
    if not m:
        print("❌ Kunde inte hitta build-ID i HTML")
        return
    build_id = m.group(1)
    print("🔍 Hittat build-ID:", build_id)

    # 2) Hämta JSON-dumpen för sidan
    json_url = f"https://www.hertzfreerider.se/_next/data/{build_id}/sv-se.json"
    resp = requests.get(json_url, headers=HEADERS, timeout=20)
    resp.raise_for_status()
    data = resp.json()

    # 3) Plocka ut trips-listan någonstans i pageProps
    page_props = data.get("pageProps", {})
    trips = None
    for key, val in page_props.items():
        if isinstance(val, list):
            trips = val
            break
        if isinstance(val, dict):
            for subval in val.values():
                if isinstance(subval, list):
                    trips = subval
                    break
        if trips is not None:
            break

    if not trips:
        print("❌ Hittade ingen lista med turer i JSON:en")
        return

    # 4) Filtrera och skicka notis
    hittade = False
    for trip in trips:
        text = json.dumps(trip, ensure_ascii=False)
        if FROM_CITY in text and TO_CITY in text:
            skicka_notis(f"🚗 Resa {FROM_CITY} → {TO_CITY}:\n{text}")
            hittade = True
        elif TO_CITY in text and FROM_CITY in text:
            skicka_notis(f"🚗 Resa {TO_CITY} → {FROM_CITY}:\n{text}")
            hittade = True

    if not hittade:
        print(f"❌ Inga resor {FROM_CITY} ↔ {TO_CITY} hittades.")

if __name__ == "__main__":
    kontrollera_resor()