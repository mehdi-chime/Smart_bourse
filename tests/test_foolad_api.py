import sys
sys.path.insert(0, r"F:\python\har roz ba python\smart_bours")

from market.api import MarketAPI

from market.api import MarketAPI

api = MarketAPI()

api.connect()

data = api.get_symbols("فولاد")

print("=" * 80)
print("SEARCH فولاد")
print("=" * 80)

print(data)

api.disconnect()
