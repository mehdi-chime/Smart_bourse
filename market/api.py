"""
Project : Smart_Bourse

File : api.py

Version : 3.0.0

Description :
Real Market API
"""
from database.symbol_repository import SymbolRepository
from datetime import datetime, timedelta
import requests
import json

# ===============================
# SYMBOL MAP
# ===============================

SYMBOL_MAP = {
    "Foolad": {
        "fa": "فولاد",
        "inscode": 46348559193224090
    },

    "Femeli": {
        "fa": "فملی",
        "inscode": None
    },

    "Khodro": {
        "fa": "خودرو",
        "inscode": None
    }
}

# ==============================

class MarketAPI:

    def __init__(self):

        self.connected = False

        self.session = requests.Session()

        self.symbol_repo = SymbolRepository()

        self.base_url = "https://cdn.tsetmc.com/api"
    # --------------------------------------------------

    def connect(self):

        print()

        print("=" * 60)

        print("Market API")

        print("=" * 60)

        print("Connecting To TSETMC...")

        self.connected = True

        print("Connected")

        return True
    # --------------------------------------------------

    def disconnect(self):

        self.session.close()

        self.connected = False

        print("Disconnected")    
    # --------------------------------------------------

    def request(self, endpoint):

        url = f"{self.base_url}/{endpoint}"

        response = self.session.get(url, timeout=20)

        response.raise_for_status()

        return response.json()
    # --------------------------------------------------

    def get_all_symbols(self):

        endpoint = "Instrument/GetInstrument"

        return self.request(endpoint)
    # --------------------------------------------------    
    def search_symbol(self, symbol):

        endpoint = f"Instrument/GetInstrumentSearch/{symbol}"

        data = self.request(endpoint)

        print(symbol)
        print(data)
        print("=" * 80)
        print("SEARCH RESULT")
        print(type(data))
        print(data)
        print("=" * 80)

        return data
    
    # --------------------------------------------------

    def closing_price(self, inscode):

        endpoint = f"ClosingPrice/GetClosingPriceInfo/{inscode}"

        return self.request(endpoint)
    # --------------------------------------------------

    def best_limits(self, inscode):

        endpoint = f"BestLimits/{inscode}"

        return self.request(endpoint)
    # --------------------------------------------------

    def client_type(self, inscode):

        endpoint = f"ClientType/GetClientType/{inscode}"

        return self.request(endpoint)
    # --------------------------------------------------

    def shareholders(self, inscode):

        endpoint = f"Shareholder/GetInstrumentShareHolderLast/{inscode}"

        return self.request(endpoint)
    # --------------------------------------------------

    def instrument(self, inscode):

        endpoint = f"Instrument/GetInstrumentInfo/{inscode}"

        return self.request(endpoint)
    # --------------------------------------------------

    def history(self, inscode):

        endpoint = f"ClosingPrice/GetClosingPriceDailyList/{inscode}/0"

        return self.request(endpoint)
        # --------------------------------------------------
    def download_history(self, symbol, days=365):

        symbol_map = {
            "Foolad": "فولاد",
            "Femeli": "فملی",
            "Khodro": "خودرو",
            "Shasta": "شستا",
            "Shepna": "شپنا"
        }

        search_symbol = symbol_map.get(symbol, symbol)

        print()
        print("-" * 60)
        print("Downloading History :", symbol)
        print("Persian Symbol      :", search_symbol)

        # -------------------------------
        # Get InsCode from Database
        # -------------------------------

        inscode = self.symbol_repo.get_inscode(search_symbol)

        # اگر در Database نبود، از SYMBOL_MAP استفاده کن
        if not inscode:

            inscode = SYMBOL_MAP.get(symbol, {}).get("inscode")

        # -------------------------------
        # InsCode Not Found
        # -------------------------------

        if not inscode:

            print("InsCode Not Found :", search_symbol)

            return []

        print("INSCODE :", inscode)

        # -------------------------------
        # Get History
        # -------------------------------

        data = self.history(inscode)

        if not data:

            print("History Download Failed")

            return []

        # -------------------------------
        # Convert History
        # -------------------------------

        history = []

        history_list = data.get(
            "closingPriceDaily",
            []
        )

        for item in history_list[:days]:

            history.append({

                "symbol": symbol,

                "trade_date": item.get("dEven"),

                "open_price": item.get("priceFirst"),

                "high_price": item.get("priceMax"),

                "low_price": item.get("priceMin"),

                "close_price": item.get("pClosing"),

                "volume": item.get("qTotTran5J")

            })

        print(
            f"{len(history)} History Records Downloaded"
        )

        return history   
    # --------------------------------------------------

    def get_symbols(self, text=""):

        endpoint = f"Instrument/GetInstrumentSearch/{text}"

        return self.request(endpoint)
    # --------------------------------------------------
    def test_symbols(self):

        data = self.get_symbols("ف")

        print()
        print("=" * 60)
        print("TEST SYMBOL API")
        print("=" * 60)

        print("TYPE:", type(data))

        print("KEYS:", data.keys())

        print("=" * 60)


