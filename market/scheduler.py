"""
Project : Smart_Bourse

File : scheduler.py

Version : 1.0.0

Author :
Mehdi Jalali
ChatGPT

Description :
Market Scheduler
"""

from datetime import datetime
import time


class Scheduler:

    def __init__(self):

        self.running = False

    # --------------------------------------------------

    def now(self):

        return datetime.now()

    # --------------------------------------------------

    def current_time(self):

        return self.now().strftime("%H:%M:%S")

    # --------------------------------------------------

    def wait(self, seconds):

        time.sleep(seconds)

    # --------------------------------------------------

    def every(self, seconds, function):

        self.running = True

        while self.running:

            function()

            time.sleep(seconds)

    # --------------------------------------------------

    def stop(self):

        self.running = False

    # --------------------------------------------------

    def show(self):

        print()

        print("=" * 60)
        print("SCHEDULER")
        print("=" * 60)
        print("Current Time :", self.current_time())
        print("Running      :", self.running)
        print("=" * 60)
