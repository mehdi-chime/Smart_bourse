"""
Project : Smart_Bourse

File : data_loader.py

Version : 1.0.0

Author :
Mehdi Jalali
ChatGPT

Description :
Load Market Data
"""

import json
import os


class DataLoader:

    def __init__(self):

        self.data = []

    # --------------------------------------------------

    def load_json(self, file_path):

        if not os.path.exists(file_path):

            print("File Not Found")
            return []

        with open(file_path, "r", encoding="utf-8") as file:

            self.data = json.load(file)

        return self.data

    # --------------------------------------------------

    def get_data(self):

        return self.data

    # --------------------------------------------------

    def count(self):

        return len(self.data)

    # --------------------------------------------------

    def clear(self):

        self.data.clear()

    # --------------------------------------------------

    def show(self):

        print()

        print("=" * 70)
        print("LOADED MARKET DATA")
        print("=" * 70)

        for item in self.data:

            print(item)

        print("=" * 70)
