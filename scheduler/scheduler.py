"""
Project : Smart_Bourse

File : scheduler.py

Version : 1.0.0

Author :
Mehdi Jalali
ChatGPT

Description :
Smart Scheduler
"""

import time
from datetime import datetime


class Scheduler:

    def __init__(self):

        self.jobs = []

    # --------------------------------------------------

    def add_job(self, name, function, interval):

        self.jobs.append({

            "name": name,

            "function": function,

            "interval": interval,

            "last_run": None

        })

    # --------------------------------------------------

    def run_once(self):

        now = datetime.now()

        for job in self.jobs:

            if job["last_run"] is None:

                job["function"]()

                job["last_run"] = now

                continue

            diff = (now - job["last_run"]).seconds

            if diff >= job["interval"]:

                job["function"]()

                job["last_run"] = now

    # --------------------------------------------------

    def start(self):

        print("=" * 60)

        print("SMART SCHEDULER STARTED")

        print("=" * 60)

        while True:

            self.run_once()

            time.sleep(1)

    # --------------------------------------------------

    def show(self):

        print()

        print("=" * 60)

        print("SCHEDULER JOBS")

        print("=" * 60)

        for job in self.jobs:

            print(job["name"], "-", job["interval"], "sec")

        print("=" * 60)
