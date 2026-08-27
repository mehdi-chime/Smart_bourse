"""
Project : Smart_Bourse

File : symbol_manager.py

Version : 1.0.0

Author :
Mehdi Jalali
ChatGPT

Description :
Manage Market Symbols
"""


class SymbolManager:

    def __init__(self):

        self.symbols = [

            "Foolad",
            "Femeli",
            "Khodro",
            "Shasta",
            "Shepna"

        ]

    # --------------------------------------------------

    def add(self, symbol):

        symbol = symbol.strip()

        if symbol == "":
            return

        if symbol not in self.symbols:

            self.symbols.append(symbol)

    # --------------------------------------------------

    def remove(self, symbol):

        if symbol in self.symbols:

            self.symbols.remove(symbol)

    # --------------------------------------------------

    def exists(self, symbol):

        return symbol in self.symbols

    # --------------------------------------------------

    def count(self):

        return len(self.symbols)

    # --------------------------------------------------

    def get_all(self):

        return self.symbols.copy()

    # --------------------------------------------------

    def clear(self):

        self.symbols.clear()

    # --------------------------------------------------

    def show(self):

        print()
        print("=" * 60)
        print("MARKET SYMBOLS")
        print("=" * 60)

        for index, symbol in enumerate(self.symbols, start=1):

            print(f"{index}. {symbol}")

        print("=" * 60)
