#!/usr/bin/env python3
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# ntfy-topic som du prenumererar på i mobilen
NTFY_TOPIC = "Hertzbil_Sthlm-OSD"

# Städer att matcha
STHLM = "Stockholm"
OSTERSUND = "Östersund"

def skicka_notis(meddelande):
    """Skicka push‑notis via ntfy."""
    print(f"📲 Skickar notis: {meddelande}")
    url = f"https://ntfy.sh/{NTFY_TOPIC}"
    requests.post(url, data=meddelande.encode("utf-8"))

def kontrollera_resor():
    """Öppna Hertz Freerider, leta efter Stockholm ↔ Östersund och eventuellt skicka notis."""
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    driver.get("https://www.hertzfreerider.se/sv-se")

    # Vänta på att innehållet laddas
    time.sleep(5)

    cards = driver.find_elements("css selector", "div.sc-dlfnbm.hLbIrd")
    hittade_något = False

    for card in cards:
        text = card.text
        if STHLM in text and OSTERSUND in text:
            skicka_notis(f"🚗 Resa Stockholm → Östersund:\n{text}")
            hittade_något = True
        elif OSTERSUND in text and STHLM in text:
            skicka_notis(f"🚗 Resa Östersund → Stockholm:\n{text}")
            hittade_något = True

    if not hittade_något:
        print("❌ Inga resor hittades just nu.")

    driver.quit()

if __name__ == "__main__":
    kontrollera_resor()