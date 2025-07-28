from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def kontrollera_resor():
    """Öppna Hertz Freerider, leta efter Visby ↔ Stockholm och eventuellt skicka notis."""
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    driver.get("https://www.hertzfreerider.se/sv-se")

    # 1) Vänta tills minst ett rutkort finns i DOM:en
    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-test='trip-card']"))
        )
    except:
        print("⚠️ Rutkorten laddades inte inom 15 sek.")
        driver.quit()
        return

    # 2) Hämta alla rutkort
    cards = driver.find_elements(By.CSS_SELECTOR, "div[data-test='trip-card']")
    print(f"🔎 Hittade {len(cards)} kort totalt för debug")  # debug

    hittade_något = False

    # 3) Loopa igenom dem och kolla texten
    for idx, card in enumerate(cards, 1):
        text = card.text.strip()
        print(f"📄 Kort #{idx}: {text.replace(chr(10),' | ')}")  # debug

        # 4) Matcha Visby ↔ Stockholm inuti kortets samlade text
        if FROM_CITY in text and TO_CITY in text:
            skicka_notis(f"🚗 Resa {FROM_CITY} → {TO_CITY}:\n{text}")
            hittade_något = True
        elif TO_CITY in text and FROM_CITY in text:
            skicka_notis(f"🚗 Resa {TO_CITY} → {FROM_CITY}:\n{text}")
            hittade_något = True

    # 5) Ingen match alls?
    if not hittade_något:
        print(f"❌ Inga resor {FROM_CITY} ↔ {TO_CITY} hittades just nu.")

    driver.quit()