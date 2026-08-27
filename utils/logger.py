"""
Project : Smart_Bourse

File : logger.py

Version : 0.0.1

Author :
Mehdi Jalali
ChatGPT

Description :
Write logs to console and log file.
"""

from datetime import datetime
from pathlib import Path

from project_config import PROJECT_PATH


class Logger:

    def __init__(self):

        self.logs = Path(PROJECT_PATH) / "logs"

        self.logs.mkdir(exist_ok=True)

        self.file = self.logs / "smart_bourse.log"

    def write(self, message):

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        text = f"[{now}] {message}"

        print(text)

        with open(self.file, "a", encoding="utf8") as f:

            f.write(text + "\n")
