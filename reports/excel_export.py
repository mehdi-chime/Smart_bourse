"""
Project : Smart_Bourse

File : excel_export.py

Version : 1.0.0

Author :
Mehdi Jalali
ChatGPT

Description :
Export Reports To Excel
"""

import os

from openpyxl import Workbook


class ExcelExport:

    def __init__(self):

        self.folder = "reports"

        os.makedirs(self.folder, exist_ok=True)

    # --------------------------------------------------

    def export(self, analysis, filename="market_report.xlsx"):

        workbook = Workbook()

        sheet = workbook.active

        sheet.title = "Market"

        sheet.append([

            "Symbol",

            "Trend",

            "Signal",

            "Risk",

            "Score"

        ])

        for item in analysis:

            sheet.append([

                item.get("symbol"),

                item.get("trend"),

                item.get("signal"),

                item.get("risk"),

                item.get("score")

            ])

        path = os.path.join(

            self.folder,

            filename

        )

        workbook.save(path)

        print("Excel Saved :", path)
