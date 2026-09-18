from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import json
import time

class TsetmcScraper:
    def __init__(self, ins_code="48990026850202503"):
        self.ins_code = ins_code
        self.url = f"https://tsetmc.ir/instInfo/{ins_code}"
        self.driver = None
        self.data = {}
    
    def start_driver(self):
        """راه‌اندازی مرورگر Chrome"""
        options = webdriver.ChromeOptions()
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
    def fetch_data(self):
        """دریافت داده‌های قیمت و صفوف"""
        self.driver.get(self.url)
        wait = WebDriverWait(self.driver, 20)
        
        # ========== داده‌های قیمت ==========
        try:
            price_element = wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "price-value"))
            )
            # اینجا باید بر اساس ساختار واقعی سایت، انتخابگرها را تنظیم کنید
            # فعلاً یک نمونه خروجی برای تست
            self.data["price"] = {
                "last": 4020,
                "open": 4040,
                "high": 4170,
                "low": 4010,
                "volume": 547500532
            }
        except:
            print("⚠️ داده‌های قیمت پیدا نشد.")
        
        # ========== داده‌های صفوف ==========
        try:
            # این بخش باید با توجه به ساختار واقعی سایت تنظیم شود
            self.data["order_book"] = {
                "buy_volume": 53927,
                "sell_volume": 40297115
            }
        except:
            print("⚠️ داده‌های صفوف پیدا نشد.")
        
        return self.data
    
    def save_data(self):
        """ذخیره داده‌ها در فایل JSON"""
        with open("data/tsetmc_scraped.json", "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
        print("✅ داده‌ها در data/tsetmc_scraped.json ذخیره شد.")
    
    def close(self):
        """بستن مرورگر"""
        if self.driver:
            self.driver.quit()

if __name__ == "__main__":
    scraper = TsetmcScraper()
    scraper.start_driver()
    scraper.fetch_data()
    scraper.save_data()
    scraper.close()
