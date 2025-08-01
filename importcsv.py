import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# تنظیمات Chrome Driver
options = Options()
options.add_argument('--headless')  # بدون UI
options.add_argument('--disable-gpu')
from webdriver_manager.chrome import ChromeDriverManager
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

# خواندن CSV
df = pd.read_csv('apps.csv')

def detect_platform_and_extract_url(package_url):
    if 'cafebazaar.ir' in package_url:
        return 'bazaar', package_url
    elif 'myket.ir' in package_url:
        return 'myket', package_url
    elif 'play.google.com' in package_url:
        return 'google_play', package_url
    else:
        return 'unknown', package_url

def extract_install_count(platform, url):
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC

    try:
        if not url.startswith("http"):
            url = "https://" + url
        driver.get(url)
        time.sleep(2)  # کمی صبر برای لود JS

        if "cafebazaar.ir" in url:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".InfoCube__content"))
            )
            installs = driver.find_element(By.CSS_SELECTOR, ".InfoCube__content").text
            print("BAZAAR →", installs)
            return installs

        elif platform == 'myket':
            el = driver.find_element(By.XPATH, '/html/body/main/section[1]/div[2]/table/tbody/tr[3]/td[2]')
            return el.text

        elif platform == 'google_play':
            el = driver.find_element(By.CLASS_NAME, 'ClM7O')
            return el.get_attribute('aria-label')  # یا .text

    except Exception as e:
        print(f"❌ خطا در {url}: {e}")
        return 'خطا'

# لیست خروجی
results = []

for _, row in df.iterrows():
    package_url = row['package_name']
    platform, full_url = detect_platform_and_extract_url(package_url)
    install_count = extract_install_count(platform, full_url)

    print(f"{platform.upper()} | {package_url} → {install_count}")

    results.append({
        'platform': platform,
        'url': package_url,
        'install_count': install_count
    })

# ذخیره نتیجه
pd.DataFrame(results).to_csv('scraped_results.csv', index=False)

driver.quit()
