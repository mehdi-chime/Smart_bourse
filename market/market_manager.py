"""
Project : Smart_Bourse

File : market_manager.py

Version : 1.0.0

Author :
Mehdi Jalali
ChatGPT

Description :
Main Market Engine
"""

from market.market_status import MarketStatus
from market.symbol_manager import SymbolManager
from market.data_loader import DataLoader
from market.data_validator import DataValidator
from market.updater import Updater


class MarketManager:

    def __init__(self):

        self.status = MarketStatus()

        self.symbols = SymbolManager()

        self.loader = DataLoader()

        self.validator = DataValidator()

        self.updater = Updater()
        
    # --------------------------------------------------

    def load(self, json_file):

        data = self.loader.load_json(json_file)

        return data

    # --------------------------------------------------

    def validate(self, market_data):

        valid_data, invalid_data = self.validator.validate_list(market_data)

        return valid_data, invalid_data

    # --------------------------------------------------

    def update_database(self, valid_data):

        self.updater.update(valid_data)

    # --------------------------------------------------

    def get_symbols(self):

        return self.symbols.get_all()

    # --------------------------------------------------

    def market_is_open(self):

        return self.status.is_market_open()

    # --------------------------------------------------

    def market_is_closed(self):

        return self.status.is_market_closed()
        # --------------------------------------------------

    def run(self, json_file):

        print()
        print("=" * 70)
        print("SMART MARKET MANAGER")
        print("=" * 70)

        if not self.market_is_open():

            print("Market Is Closed")
            return

        print("Loading Data...")

        market_data = self.load(json_file)

        print("Records :", len(market_data))

        print("Validating Data...")

        valid_data, invalid_data = self.validate(market_data)

        print("Valid :", len(valid_data))
        print("Invalid :", len(invalid_data))

        if invalid_data:

            print()
            print("Invalid Records:")

            for item in invalid_data:

                print(item)

        print()

        print("Updating Database...")

        self.update_database(valid_data)

        print()

        print("Database Updated Successfully")

        print("=" * 70)

    # --------------------------------------------------

    def show(self):

        print()

        print("=" * 70)
        print("MARKET MANAGER")
        print("=" * 70)

        print("Market Open :", self.market_is_open())

        print("Symbols :", len(self.get_symbols()))

        print("=" * 70)
