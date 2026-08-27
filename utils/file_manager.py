"""
Project : Smart_Bourse

File : file_manager.py

Version : 0.0.6

Description :
Manage TXT and JSON Files
"""

import json
import os


class FileManager:

    @staticmethod
    def load_json(file_path):

        if not os.path.exists(file_path):
            return {}

        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def save_json(file_path, data):

        with open(file_path, "w", encoding="utf-8") as f:

            json.dump(
                data,
                f,
                ensure_ascii=False,
                indent=4
            )

    @staticmethod
    def load_txt(file_path):

        if not os.path.exists(file_path):
            return []

        with open(file_path, "r", encoding="utf-8") as f:

            return [
                line.strip()
                for line in f.readlines()
                if line.strip()
            ]

    @staticmethod
    def save_txt(file_path, data):

        with open(file_path, "w", encoding="utf-8") as f:

            for item in data:
                f.write(f"{item}\n")
