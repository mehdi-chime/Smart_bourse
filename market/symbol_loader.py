"""
Project : Smart_Bourse

File : symbol_loader.py

Version : 1.0.0
"""

from database.symbol_repository import SymbolRepository


class SymbolLoader:

    def __init__(self):

        self.repo = SymbolRepository()

    # ----------------------------------

    def save_symbol(self,
                    symbol,
                    symbol_fa,
                    inscode,
                    isin="",
                    market="",
                    industry=""):

        self.repo.save(

            symbol,

            symbol_fa,

            inscode,

            isin,

            market,

            industry

        )
