import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Chrome Driver Configuration
options = Options()
options.add_argument('--headless')  # Run browser in headless mode
options.add_argument('--disable-gpu')  # Disable GPU acceleration
options.add_argument('--no-sandbox')  # Bypass OS security model
options.add_argument('--disable-dev-shm-usage')  # Overcome limited resource problems

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

# Define search URL patterns
MARKET_URLS = {
    'bazaar': 'https://cafebazaar.ir/app/{}',
    'myket': 'https://myket.ir/app/{}',
    'google_play': 'https://play.google.com/store/apps/details?id={}&hl=en'
}

def extract_install_count(platform, package_name):
    try:
        url = MARKET_URLS[platform].format(package_name)
        driver.get(url)
        time.sleep(2)  # Let the JS content load

        if platform == 'bazaar':
            try:
                WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".InfoCube__content"))
                )
                el = driver.find_element(By.CSS_SELECTOR, ".InfoCube__content")
                return el.text.strip()
            except:
                return 'موجود نیست'

        elif platform == 'myket':
            try:
                el = driver.find_element(By.XPATH, '/html/body/main/section[1]/div[2]/table/tbody/tr[3]/td[2]')
                return el.text.strip()
            except:
                return 'موجود نیست'

        elif platform == 'google_play':
            try:
                WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, "//div[text()='Downloads' or text()='نصب‌ها']/preceding-sibling::div[1]"))
                )
                el = driver.find_element(By.XPATH, "//div[text()='Downloads' or text()='نصب‌ها']/preceding-sibling::div[1]")
                return el.text.strip()
            except:
                return 'موجود نیست'

    except Exception as e:
        print(f"خطا در بررسی {platform} برای {package_name}: {e}")
        return 'خطا'

# --- MAIN EXECUTION ---
if __name__ == "__main__":
    df = pd.read_csv('apps.csv', header=None, names=['package_name'])
    results = []

    for i, row in df.iterrows():
        pkg = row['package_name']
        bazaar = extract_install_count('bazaar', pkg)
        myket = extract_install_count('myket', pkg)
        google = extract_install_count('google_play', pkg)

        results.append({
            'package_name': pkg,
            'bazaar_installs': bazaar,
            'myket_installs': myket,
            'google_play_installs': google
        })

        print(f"{pkg} → بازار: {bazaar} | مایکت: {myket} | گوگل پلی: {google}")

        # Optional delay to avoid overloading servers
        time.sleep(1)

    pd.DataFrame(results).to_csv('scraped_results.csv', index=False, encoding='utf-8-sig')
    driver.quit()
