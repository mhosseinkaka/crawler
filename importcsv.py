import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# تنظیمات Chrome Driver
options = Options()
options.add_argument('--headless')
options.add_argument('--disable-gpu')

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

# بارگذاری CSV
df = pd.read_csv('apps.csv')

# تشخیص پلتفرم از URL
def detect_platform_and_extract_url(package_url):
    if 'cafebazaar.ir' in package_url:
        return 'bazaar', package_url
    elif 'myket.ir' in package_url:
        return 'myket', package_url
    elif 'play.google.com' in package_url:
        return 'google_play', package_url
    else:
        return 'unknown', package_url

# استخراج تعداد نصب با توجه به پلتفرم
def extract_install_count(platform, url):
    try:
        if not url.startswith("http"):
            url = "https://" + url
        driver.get(url)
        time.sleep(2)

        if platform == "bazaar":
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".InfoCube__content"))
            )
            el = driver.find_element(By.CSS_SELECTOR, ".InfoCube__content")
            return el.text.strip()

        elif platform == "myket":
            el = driver.find_element(By.XPATH, '/html/body/main/section[1]/div[2]/table/tbody/tr[3]/td[2]')
            return el.text.strip()

        elif platform == "google_play":
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[.='Downloads' or .='نصب‌ها']/preceding-sibling::div[1]"))
            )
            el = driver.find_element(By.XPATH, "//div[.='Downloads' or .='نصب‌ها']/preceding-sibling::div[1]")
            return el.text.strip()

        else:
            return 'پلتفرم ناشناس'

    except Exception as e:
        print(f"❌ خطا در {url}: {e}")
        return 'خطا'

results = []

for _, row in df.iterrows():
    package_url = row['package_name']
    platform, full_url = detect_platform_and_extract_url(package_url)
    install_count = extract_install_count(platform, full_url)

    print(f"{platform.upper()} | {package_url} → {install_count}")

    results.append({
        'package_url': package_url,
        'platform': platform,
        'install_count': install_count
    })

# ذخیره خروجی
pd.DataFrame(results).to_csv('scraped_results.csv', index=False, encoding='utf-8-sig')

driver.quit()
