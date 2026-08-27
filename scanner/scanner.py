"""
Project : Smart_Bourse

File : scanner.py

Version : 1.0.0

Author :
Mehdi Jalali
ChatGPT

Description :
Market Scanner
"""

from database.database import Database
from history.history_database import HistoryDatabase
from indicators.indicator_manager import IndicatorManager
from analyzer.analyzer import Analyzer
from strategy.strategy_engine import StrategyEngine


class Scanner:

    def __init__(self):

        self.db = Database()

        self.history_db = HistoryDatabase()

        self.indicators = IndicatorManager()

        self.analyzer = Analyzer()

        self.strategy = StrategyEngine()

        self.results = []

    # --------------------------------------------------

    def connect(self):

        self.db.connect()

        self.history_db.connect()

    # --------------------------------------------------

    def disconnect(self):

        self.db.close()

        self.history_db.close()

    # --------------------------------------------------

    def scan_symbol(self, symbol):

        print(f"Scanning : {symbol}")

    # --------------------------------------------------

    def scan_all(self):

        print()

        print("=" * 70)
        print("SMART SCANNER")
        print("=" * 70)

    # --------------------------------------------------

    def show(self):

        print()

        print("=" * 70)
        print("SCANNER RESULT")
        print("=" * 70)

        print("Scanned :", len(self.results))

        print("=" * 70)
