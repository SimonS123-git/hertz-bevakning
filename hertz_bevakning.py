#!/usr/bin/env python3
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

# ntfy-topic som du prenumererar på i mobilen
NTFY_TOPIC = "Hertzbil_Sthlm-OSD"

# Städer att matcha (byt tillbaka till Visby ↔ Stockholm om du vill)
FROM_CITY = "Visby"
TO_CITY   = "Stockholm"

def skicka_notis(meddelande):
    """Skicka push-notis via ntfy."""
    print(f"📲 Skickar notis: {meddelande}")
    url = f"https://ntfy.sh/{NTFY_TOPIC}"
    requests.post(url, data=meddelande.encode("utf-8"))

def kontrollera_resor():
    """Öppna Hertz Freerider, leta efter FROM_CITY ↔ TO_CITY och eventuellt skicka notis."""
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    # Viktigt: peka på den rätta chromium-binaryn på GitHub Actions
    options.binary_location = "/usr/bin/chromium-browser"

    driver = webdriver.Chrome(options=options)
    driver.get("https://www.hertzfreerider.se/sv-se")

    try:
        # Vänta upp till 30s på att korten ska dyka upp
        WebDriverWait(driver, 30).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.sc-dlfnbm.hLbIrd"))
        )
        cards = driver.find_elements(By.CSS_SELECTOR, "div.sc-dlfnbm.hLbIrd")
        hittade = False

        for card in cards:
            text = card.text
            if FROM_CITY in text and TO_CITY in text:
                skicka_notis(f"🚗 Resa {FROM_CITY} → {TO_CITY}:\n{text}")
                hittade = True
            elif TO_CITY in text and FROM_CITY in text:
                skicka_notis(f"🚗 Resa {TO_CITY} → {FROM_CITY}:\n{text}")
                hittade = True

        if not hittade:
            print(f"❌ Inga resor {FROM_CITY} ↔ {TO_CITY} hittades just nu.")

    except Exception as e:
        print(f"⚠️ Fel vid laddning av kort: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    kontrollera_resor()