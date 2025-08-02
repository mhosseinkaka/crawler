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
options.add_argument('--headless')  # Run browser in headless mode (no GUI)
options.add_argument('--disable-gpu')  # Disable GPU acceleration

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

def detect_platform_and_extract_url(package_url):
    """
    Detect the app store platform from URL and return platform name with full URL
    
    شناسایی پلتفرم فروشگاه برنامه از روی URL و برگرداندن نام پلتفرم با URL کامل
    
    Args:
        package_url (str): The URL of the application
        package_url (str): آدرس برنامه در فروشگاه
        
    Returns:
        tuple: (platform_name, full_url) where platform_name is one of:
        tuple: (نام پلتفرم, آدرس کامل) که نام پلتفرم می‌تواند یکی از موارد زیر باشد:
            - 'bazaar' (کافه بازار)
            - 'myket' (مایکت)
            - 'google_play' (گوگل پلی)
            - 'unknown' (ناشناخته)
    """
    if 'cafebazaar.ir' in package_url:
        return 'bazaar', package_url
    elif 'myket.ir' in package_url:
        return 'myket', package_url
    elif 'play.google.com' in package_url:
        return 'google_play', package_url
    else:
        return 'unknown', package_url

def extract_install_count(platform, url):
    """
    Extract installation count from the specified app store platform
    
    استخراج تعداد نصب‌ها از پلتفرم فروشگاه برنامه مشخص شده
    
    Args:
        platform (str): The platform name ('bazaar', 'myket', 'google_play')
        platform (str): نام پلتفرم
        url (str): The full URL of the application page
        url (str): آدرس کامل صفحه برنامه
        
    Returns:
        str: The installation count text or error message
        str: متن تعداد نصب یا پیغام خطا
    """
    try:
        if not url.startswith("http"):
            url = "https://" + url
        driver.get(url)
        time.sleep(2)  # Wait for page to load

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

# Main execution
if __name__ == "__main__":
    """
    Main script to extract installation counts from app store URLs
    
    اسکریپت اصلی برای استخراج تعداد نصب‌ها از آدرس‌های فروشگاه برنامه
    
    Input:
        Requires 'apps.csv' file with 'package_name' column containing app URLs
        نیاز به فایل 'apps.csv' با ستون 'package_name' حاوی آدرس برنامه‌ها
        
    Output:
        Generates 'scraped_results.csv' with columns:
        تولید فایل 'scraped_results.csv' با ستون‌های:
            - package_url: آدرس برنامه
            - platform: پلتفرم
            - install_count: تعداد نصب
    """
    # Read input CSV
    df = pd.read_csv('apps.csv')
    
    results = []
    
    # Process each app URL
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

    # Save results
    pd.DataFrame(results).to_csv('scraped_results.csv', index=False, encoding='utf-8-sig')
    
    # Clean up
    driver.quit()
