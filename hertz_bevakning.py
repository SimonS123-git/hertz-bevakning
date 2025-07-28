#!/usr/bin/env python3
import time
import requests
import shutil
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# ntfy-topic som du prenumererar på i mobilen
NTFY_TOPIC = "Hertzbil_Sthlm-OSD"

# Städer att matcha (Visby ↔ Stockholm)
FROM_CITY = "Visby"
TO_CITY   = "Stockholm"

def skicka_notis(meddelande):
    print(f"📲 Skickar notis: {meddelande}")
    url = f"https://ntfy.sh/{NTFY_TOPIC}"
    requests.post(url, data=meddelande.encode("utf-8"))

def kontrollera_resor():
    print("▶️ Startar kontrollera_resor()")

    # Debug: var ligger binärerna?
    chromepath = shutil.which("chromium-browser") or shutil.which("chromium")
    driverpath = shutil.which("chromedriver")
    print("🖥️ chromium-browser:", chromepath)
    print("🖥️ chromedriver   :", driverpath)

    options = Options()
    if chromepath:
        options.binary_location = chromepath
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(
        service=Service(driverpath or "/usr/bin/chromedriver"),
        options=options
    )

    print("🔗 Hämtar sidan…")
    driver.get("https://www.hertzfreerider.se/sv-se")

    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-test='trip-card']"))
        )
        print("✅ Rutkorten laddade")
    except Exception as e:
        print("⚠️ Korten laddades inte inom 15s:", e)
        driver.quit()
        return

    cards = driver.find_elements(By.CSS_SELECTOR, "div[data-test='trip-card']")
    print(f"🔎 Hittade {len(cards)} kort totalt")

    hittade_något = False
    for idx, card in enumerate(cards, 1):
        text = card.text.strip()
        print(f"📄 Kort #{idx}: {text.replace(chr(10), ' | ')}")
        if FROM_CITY in text and TO_CITY in text:
            skicka_notis(f"🚗 Resa {FROM_CITY} → {TO_CITY}:\n{text}")
            hittade_något = True
        elif TO_CITY in text and FROM_CITY in text:
            skicka_notis(f"🚗 Resa {TO_CITY} → {FROM_CITY}:\n{text}")
            hittade_något = True

    if not hittade_något:
        print(f"❌ Inga resor {FROM_CITY} ↔ {TO_CITY} hittades just nu.")

    driver.quit()
    print("⏹️ Avslutar kontrollera_resor()")

if __name__ == "__main__":
    kontrollera_resor()