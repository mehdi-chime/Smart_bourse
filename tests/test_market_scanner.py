"""
Project : Smart_Bourse

File : test_market_scanner.py

Description :
Test Market Scanner
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from history.history_database import HistoryDatabase
from market.market_scanner import MarketScanner

from history.history_database import HistoryDatabase

from market.market_scanner import MarketScanner


print()
print("=" * 80)
print("SMART BOURSE - MARKET SCANNER TEST")
print("=" * 80)


symbol = "Foolad"

days = 365


history_db = HistoryDatabase()

scanner = MarketScanner()


history_db.connect()

stocks = history_db.get_history(
    symbol,
    days
)

history_db.close()


print()

print("Symbol :", symbol)

print("History Records :", len(stocks))


result = scanner.scan_symbol(stocks)


scanner.show_result(result)


print()

print("=" * 80)

print("SCANNER TEST FINISHED")

print("=" * 80)
