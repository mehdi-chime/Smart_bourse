"""
Project : Smart_Bourse

File : report_generator.py

Version : 1.0.0

Author :
Mehdi Jalali
ChatGPT

Description :
Generate Smart Reports
"""

import json
import os
from datetime import datetime


class ReportGenerator:

    def __init__(self):

        self.report_folder = "reports"

        os.makedirs(self.report_folder, exist_ok=True)

    # --------------------------------------------------

    def create(self, analysis):

        report = {

            "date": str(datetime.now()),

            "total_symbols": len(analysis),

            "analysis": analysis

        }

        return report

    # --------------------------------------------------

    def save_json(self, report, filename=None):

        if filename is None:

            filename = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")

            filename = f"{self.report_folder}/{filename}.json"

        with open(

            filename,

            "w",

            encoding="utf-8"

        ) as file:

            json.dump(

                report,

                file,

                indent=4,

                ensure_ascii=False

            )

        print("Report Saved :", filename)

    # --------------------------------------------------

    def show(self, report):

        print()

        print("=" * 80)

        print("SMART REPORT")

        print("=" * 80)

        print("Date :", report["date"])

        print("Symbols :", report["total_symbols"])

        print("=" * 80)

        for item in report["analysis"]:

            print(item)

        print("=" * 80)
