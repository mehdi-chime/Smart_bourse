"""
Project : Smart_Bourse

File : main_dashboard.py

Version : 1.0.0

Author :
Mehdi Jalali
ChatGPT

Description :
Main Dashboard
"""


class MainDashboard:

    def __init__(self):

        self.modules = []

    # --------------------------------------------------

    def add_module(self, name):

        if name not in self.modules:

            self.modules.append(name)

    # --------------------------------------------------

    def remove_module(self, name):

        if name in self.modules:

            self.modules.remove(name)

    # --------------------------------------------------

    def clear(self):

        self.modules.clear()

    # --------------------------------------------------

    def show(self):

        print()

        print("=" * 70)

        print("SMART_BOURSE DASHBOARD")

        print("=" * 70)

        for module in self.modules:

            print("✔", module)

        print("=" * 70)
