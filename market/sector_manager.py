"""
Project : Smart_Bourse

File : sector_manager.py

Description :
Manage market sectors and industries
"""


class SectorManager:

    def __init__(self):

        self.sectors = {

            "فلزات اساسی": [
                "فولاد",
                "فملی",
            ],

            "خودرویی": [
                "خودرو",
            ],

            "سیمانی": [],

            "شیمیایی": [],

            "پالایشی": [],

            "بانکی": [],

            "سرمایه گذاری": [],

            "دارویی": [],

            "غذایی": [],

            "ساختمانی": [],

            "نیروگاهی": [],

            "بیمه": [],

            "ارتباطات": [],

        }

    # -------------------------------------

    def get_sectors(self):

        return list(self.sectors.keys())

    # -------------------------------------

    def get_symbols(self, sector):

        return self.sectors.get(sector, [])

    # -------------------------------------

    def add_symbol(self, sector, symbol):

        if sector not in self.sectors:

            self.sectors[sector] = []

        if symbol not in self.sectors[sector]:

            self.sectors[sector].append(symbol)

    # -------------------------------------

    def find_sector(self, symbol):

        for sector, symbols in self.sectors.items():

            if symbol in symbols:

                return sector

        return None

    # -------------------------------------

    def show(self):

        print()
        print("=" * 60)
        print("MARKET SECTORS")
        print("=" * 60)

        for sector, symbols in self.sectors.items():

            print()
            print(sector)

            if symbols:

                for symbol in symbols:

                    print("   -", symbol)

            else:

                print("   -")

        print("=" * 60)
