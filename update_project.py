"""
Project : Smart_Bourse

File : update_project.py

Version : 0.0.6

Description :
Project Updater
"""

import os
import json

from utils.file_manager import FileManager


print("=" * 50)
print("Smart_Bourse Updater V0.0.6")
print("=" * 50)

# --------------------------------------------------

DATA_FOLDER = "data"

if not os.path.exists(DATA_FOLDER):
    os.makedirs(DATA_FOLDER)
    print("[OK] data folder created")
else:
    print("[OK] data folder exists")

# --------------------------------------------------

symbols_path = os.path.join(DATA_FOLDER, "symbols.txt")

if not os.path.exists(symbols_path):

    symbols = [
        "Foolad",
        "Femeli",
        "Khodro",
        "Shasta",
        "Shepna"
    ]

    FileManager.save_txt(symbols_path, symbols)

    print("[OK] symbols.txt created")

else:

    print("[OK] symbols.txt exists")

# --------------------------------------------------

config_path = os.path.join(DATA_FOLDER, "config.json")

if not os.path.exists(config_path):

    config = {

        "project": "Smart_Bourse",

        "version": "0.0.6",

        "market": "TSE",

        "language": "fa",

        "debug": True

    }

    FileManager.save_json(config_path, config)

    print("[OK] config.json created")

else:

    print("[OK] config.json exists")

# --------------------------------------------------

watchlist_path = os.path.join(DATA_FOLDER, "watchlist.json")

if not os.path.exists(watchlist_path):

    watchlist = {

        "watchlist": [

            {

                "symbol": "Foolad",

                "buy_price": 0,

                "current_price": 0,

                "target_price": 0,

                "stop_loss": 0,

                "volume": 0,

                "rsi": 0,

                "macd": 0,

                "signal": "WAIT",

                "last_update": ""

            }

        ]

    }

    FileManager.save_json(
        watchlist_path,
        watchlist
    )

    print("[OK] watchlist.json created")

else:

    print("[OK] watchlist.json exists")

# --------------------------------------------------

print("=" * 50)
print("Update Finished Successfully")
print("=" * 50)
