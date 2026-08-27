
"""
Project : Smart_Bourse

File : symbol_downloader.py

Version : 3.2.0

Description :
Download and save market symbols
"""

from database.symbol_repository import SymbolRepository


class SymbolDownloader:

    def __init__(self, api):

        self.api = api

        self.repo = SymbolRepository()

    # --------------------------------------------------

    def download(self):

        letters = [

            "ا", "ب", "پ", "ت", "ث", "ج", "چ", "ح", "خ",
            "د", "ذ", "ر", "ز", "ژ", "س", "ش", "ص", "ض",
            "ط", "ظ", "ع", "غ", "ف", "ق", "ک", "گ",
            "ل", "م", "ن", "و", "ه", "ی"

        ]

        total = 0

        for letter in letters:

            print(f"Searching : {letter}")

            try:

                data = self.api.get_symbols(letter)

                if letter == "ف":

                    print("=" * 80)
                    print("DEBUG LETTER F")
                    print("TYPE:", type(data))
                    print("DATA:", data)
                    print("=" * 80)

            except Exception as e:

                print("Search Error :", e)

                continue

            if not data:

                continue

            items = data.get("instrumentSearch", [])

            for item in items:
                print("SYMBOL:", item.get("lVal18AFC"))
                print("INSCODE:", item.get("insCode"))
                print("ISIN:", item.get("cIsin"))
                print("-" * 50)
                

                # ------------------------------------------
                # Basic information
                # ------------------------------------------

                symbol = item.get("lVal18AFC")
                company = item.get("lVal30")

                isin = item.get("cIsin")
                
                inscode = item.get("insCode")

                market = item.get("flowTitle")
                board = item.get("cgrValCotTitle")

                print(
                    "CHECK:",
                    repr(symbol),
                    repr(inscode),
                    repr(company)
                )
                

                # ------------------------------------------
                # Ignore invalid records
                # ------------------------------------------

                if not symbol:
                    continue               

                if not inscode:
                    continue

                # ------------------------------------------
                # Debug important symbols
                # ------------------------------------------
                if "فولاد" in self.repo.normalize_symbol(symbol):

                    print()
                    print("=" * 80)
                    print("FOOLAD FOUND")
                    print("SYMBOL  :", repr(symbol))
                    print("COMPANY :", repr(company))
                    print("ISIN    :", repr(isin))
                    print("INSCODE :", repr(inscode))
                    print("MARKET  :", repr(market))
                    print("BOARD   :", repr(board))
                    print("=" * 80)
                
                # ------------------------------------------
                # Save symbol
                # ------------------------------------------

                saved = self.repo.save(

                    symbol=symbol,
                    company=company,
                    isin=isin,
                    company_isin=None,
                    inscode=inscode,
                    market=market,
                    board=board,
                    instrument_type=None,
                    sector_code=None,
                    sector_name=None,
                    sub_sector=None

                )

                if saved:

                    total += 1

        # --------------------------------------------------
        # Result
        # --------------------------------------------------

        print()

        print("=" * 60)
        print("SYMBOL DOWNLOAD FINISHED")
        print("=" * 60)

        print("Downloaded :", total)

        print("=" * 60)

