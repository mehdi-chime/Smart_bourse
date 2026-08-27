"""
Project : Smart_Bourse

File : market.py

Version : 0.0.5
"""

from pathlib import Path


def load_market():
    print("[Market] Module Loaded")


def data_folder():
    return Path(__file__).parent / "data"


def load_symbols():

    file = data_folder() / "symbols.txt"

    with open(file, "r", encoding="utf-8") as f:
        symbols = f.readlines()

    return [symbol.strip() for symbol in symbols]


def show_symbols():

    print("\n========== Symbols ==========")

    for number, symbol in enumerate(load_symbols(), start=1):
        print(f"{number}. {symbol}")

    print("=============================\n")
