"""
core/event_analyzer.py
تحلیل تأثیر رویدادهای خاص بازار (عرضه اولیه، مجامع، و ...)
نسخه ۱.۰
"""

import json
import os
from datetime import datetime, timedelta

class EventAnalyzer:
    def __init__(self, events_file="data/events.json"):
        """
        events_file: مسیر فایل JSON حاوی رویدادها
        """
        self.events_file = events_file
        self.events = self.load_events()
    
    def load_events(self):
        """بارگذاری رویدادها از فایل JSON"""
        if not os.path.exists(self.events_file):
            # اگر فایل نبود، یک نمونه پیش‌فرض ایجاد کن
            default_events = {
                "events": [
                    {
                        "date": "2026-09-01",
                        "type": "عرضه اولیه",
                        "symbol": "تابان",
                        "description": "عرضه اولیه سهام پتروشیمی تابان",
                        "impact": "negative",
                        "severity": 8
                    }
                ]
            }
            os.makedirs(os.path.dirname(self.events_file), exist_ok=True)
            with open(self.events_file, "w", encoding="utf-8") as f:
                json.dump(default_events, f, ensure_ascii=False, indent=2)
            return default_events["events"]
        
        with open(self.events_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("events", [])
    
    def get_today_events(self):
        """رویدادهای امروز و فردا را برمی‌گرداند"""
        today = datetime.now().strftime("%Y-%m-%d")
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        
        today_events = []
        for event in self.events:
            if event["date"] in [today, tomorrow]:
                today_events.append(event)
        return today_events
    
    def calculate_market_impact(self):
        """
        محاسبه تأثیر رویدادها بر سلامت بازار
        خروجی: عددی بین ۰ تا ۱۰۰ (هرچه کمتر، تأثیر منفی بیشتر)
        """
        events = self.get_today_events()
        if not events:
            return {
                "impact_score": 0,
                "impact_level": "بدون رویداد",
                "description": "امروز رویداد خاصی برنامه‌ریزی نشده است.",
                "events": []
            }
        
        total_impact = 0
        for event in events:
            if event["impact"] == "negative":
                total_impact += event["severity"]
            elif event["impact"] == "positive":
                total_impact -= event["severity"]
        
        # تبدیل به نمره (حداکثر تأثیر منفی = ۱۰۰)
        impact_score = min(100, max(0, int(total_impact * 5)))
        
        if impact_score > 70:
            impact_level = "🔴 تأثیر منفی شدید"
            description = "رویدادهای منفی (مانند عرضه اولیه بزرگ) می‌توانند بازار را به شدت تحت تأثیر قرار دهند. احتیاط کنید."
        elif impact_score > 40:
            impact_level = "🟡 تأثیر منفی متوسط"
            description = "رویدادهای منفی در پیش است. بازار ممکن است دچار نوسان شود."
        else:
            impact_level = "🟢 تأثیر مثبت یا خنثی"
            description = "رویدادهای خاص تأثیر قابل توجهی بر بازار ندارند."
        
        return {
            "impact_score": impact_score,
            "impact_level": impact_level,
            "description": description,
            "events": events
        }
    
    def add_event(self, date, event_type, symbol, description, impact, severity):
        """اضافه کردن یک رویداد جدید به فایل"""
        new_event = {
            "date": date,
            "type": event_type,
            "symbol": symbol,
            "description": description,
            "impact": impact,
            "severity": severity
        }
        self.events.append(new_event)
        # ذخیره در فایل
        with open(self.events_file, "w", encoding="utf-8") as f:
            json.dump({"events": self.events}, f, ensure_ascii=False, indent=2)


# ---------- بخش تست ----------
if __name__ == "__main__":
    analyzer = EventAnalyzer()
    impact = analyzer.calculate_market_impact()
    print("📅 تحلیل تأثیر رویدادها:")
    print(f"   {impact['impact_level']}")
    print(f"   {impact['description']}")
    if impact['events']:
        print("   رویدادهای پیش‌رو:")
        for e in impact['events']:
            print(f"     - {e['date']}: {e['symbol']} ({e['type']})")
