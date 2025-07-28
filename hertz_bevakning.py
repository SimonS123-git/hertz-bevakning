#!/usr/bin/env python3
import re
import json
import requests

# ntfy-topic som du prenumererar på
NTFY_TOPIC = "Hertzbil_Sthlm-OSD"

# Städer att matcha
FROM_CITY = "Visby"
TO_CITY   = "Stockholm"

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
    # 1) Hämta HTML
    resp = requests.get("https://www.hertzfreerider.se/sv-se", headers=HEADERS, timeout=20)
    resp.raise_for_status()
    html = resp.text

    # 2) Extrahera __NEXT_DATA__ JSON
    m = re.search(
        r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>',
        html,
        flags=re.S,
    )
    if not m:
        print("❌ Kunde inte hitta __NEXT_DATA__-script")
        return

    data = json.loads(m.group(1))
    build_id = data.get("buildId")
    if not build_id:
        print("❌ Kunde inte hitta buildId i __NEXT_DATA__")
        return
    print("🔍 Hittat buildId:", build_id)

    # 3) Hämta api-dumpen
    api_url = f"https://www.hertzfreerider.se/_next/data/{build_id}/sv-se.json"
    resp = requests.get(api_url, headers=HEADERS, timeout=20)
    resp.raise_for_status()
    json_data = resp.json()

    # 4) Plocka ut trips-listan
    page_props = json_data.get("pageProps", {})
    trips = None
    # djup-scanna efter första lista i pageProps
    def find_list(obj):
        if isinstance(obj, list):
            return obj
        if isinstance(obj, dict):
            for v in obj.values():
                found = find_list(v)
                if found:
                    return found
        return None

    trips = find_list(page_props)
    if not trips:
        print("❌ Ingen trip-lista funnen i JSON")
        return

    # 5) Filtrera och skicka notis
    hittade = False
    for trip in trips:
        txt = json.dumps(trip, ensure_ascii=False)
        if FROM_CITY in txt and TO_CITY in txt:
            skicka_notis(f"🚗 Resa {FROM_CITY} → {TO_CITY}:\n{txt}")
            hittade = True
        elif TO_CITY in txt and FROM_CITY in txt:
            skicka_notis(f"🚗 Resa {TO_CITY} → {FROM_CITY}:\n{txt}")
            hittade = True

    if not hittade:
        print(f"❌ Inga resor {FROM_CITY} ↔ {TO_CITY} hittades.")

if __name__ == "__main__":
    kontrollera_resor()