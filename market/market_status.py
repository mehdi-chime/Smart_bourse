"""
Project : Smart_Bourse

File : market_status.py

Version : 2.0.0

Author :
Mehdi Jalali
ChatGPT

Description :
Smart Market Status Manager
"""

from datetime import datetime, timedelta


class MarketStatus:

    def __init__(self):

        # ساعت بازار
        self.open_hour = 8
        self.open_minute = 45

        self.close_hour = 12
        self.close_minute = 30

    # ==================================================

    def now(self):
        return datetime.now()

    # ==================================================

    def current_date(self):
        return self.now().strftime("%Y-%m-%d")

    # ==================================================

    def current_time(self):
        return self.now().strftime("%H:%M:%S")

    # ==================================================

    def weekday(self):
        return self.now().weekday()

    # ==================================================

    def weekday_name(self):

        names = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday"
        ]

        return names[self.weekday()]

    # ==================================================

    def is_weekend(self):

        # ایران
        return self.weekday() in [3, 4]

    # ==================================================

    def market_open_datetime(self):

        now = self.now()

        return now.replace(
            hour=self.open_hour,
            minute=self.open_minute,
            second=0,
            microsecond=0
        )

    # ==================================================

    def market_close_datetime(self):

        now = self.now()

        return now.replace(
            hour=self.close_hour,
            minute=self.close_minute,
            second=0,
            microsecond=0
        )

    # ==================================================

    def is_market_open(self):

        if self.is_weekend():
            return False

        return self.market_open_datetime() <= self.now() <= self.market_close_datetime()

    # ==================================================

    def status(self):

        return "OPEN" if self.is_market_open() else "CLOSED"

    # ==================================================

    def next_open(self):

        now = self.now()

        if self.is_market_open():
            return "Market Is Open"

        dt = self.market_open_datetime()

        if now < dt and not self.is_weekend():
            return dt.strftime("%Y-%m-%d %H:%M")

        # روز بعد
        next_day = now + timedelta(days=1)

        while next_day.weekday() in [3, 4]:
            next_day += timedelta(days=1)

        dt = next_day.replace(
            hour=self.open_hour,
            minute=self.open_minute,
            second=0,
            microsecond=0
        )

        return dt.strftime("%Y-%m-%d %H:%M")

    # ==================================================

    def remaining_time(self):

        if not self.is_market_open():
            return "-"

        diff = self.market_close_datetime() - self.now()

        hours = diff.seconds // 3600
        minutes = (diff.seconds % 3600) // 60

        return f"{hours}h {minutes}m"

    # ==================================================

    def show(self):

        print()

        print("=" * 70)
        print("MARKET STATUS")
        print("=" * 70)

        print("Date            :", self.current_date())
        print("Time            :", self.current_time())
        print("Week Day        :", self.weekday_name())
        print("Weekend         :", self.is_weekend())
        print("Market Status   :", self.status())
        print("Next Open       :", self.next_open())
        print("Remaining Time  :", self.remaining_time())

        print("=" * 70)
