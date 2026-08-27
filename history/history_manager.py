"""
Project : Smart_Bourse

File : history_manager.py

Version : 0.1.1

Author :
Mehdi Jalali
ChatGPT

Description :
Save Daily Market History
"""

from pathlib import Path
import shutil
from datetime import datetime


class HistoryManager:

    def __init__(self):

        self.history_folder = Path("data") / "history"

        self.history_folder.mkdir(parents=True, exist_ok=True)

    # ----------------------------------

    def save_daily_history(self, json_file):

        today = datetime.now().strftime("%Y_%m_%d")

        destination = self.history_folder / f"market_{today}.json"

        shutil.copy(json_file, destination)

        print()

        print("=" * 60)
        print("History Saved")
        print(destination)
        print("=" * 60)

    # ----------------------------------

    def show_history_files(self):

        print()

        print("=" * 60)
        print("History Files")
        print("=" * 60)

        files = sorted(self.history_folder.glob("*.json"))

        if not files:

            print("No History Found")

        else:

            for file in files:

                print(file.name)

        print("=" * 60)
